from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
import stripe

from payments.models import Payment, Order
from courses.models import Course, Enrollment
from users.models import User
from .serializers import PaymentSerializer, CreatePaymentSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


class PaymentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing payment instances.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned payments to a given user,
        by filtering against a `user` query parameter in the URL.
        """
        queryset = super().get_queryset()
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user=user)
        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data["course_id"]
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return Response({"detail": "No course found with given slug"}, status=404)

        order = Order.objects.create(
            user=request.user,
            total_amount=course.price,
        )

        order.courses.add(course)
        order.save()

        payment = Payment.objects.create(
            user=request.user,
            amount=course.price,
            method=Payment.PaymentMethodChoices.STRIPE,
            status=Payment.StatusChoices.PENDING,
        )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(course.price * 100),
                    'product_data': {
                        'name': course.title,
                        'images': [request.build_absolute_uri(course.thumbnail.url)],
                    },
                },
                'quantity': 1,
            }],
            metadata={
                "user_id": request.user.id,
                "user_email": request.user.email,
                "order_id": order.id,
                "payment_id": payment.id,
            },
            mode='payment',
            success_url=settings.FRONTEND_URL + f"/dashboard/payment-success?course-slug={course.slug}",
            cancel_url=settings.FRONTEND_URL + "/dashboard/payment-cancel",
        )

        return Response({'checkout_session_id': checkout_session.id})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        order_id = session['metadata']['order_id']
        payment_id = session['metadata']['payment_id']

        payment = Payment.objects.get(id=payment_id)

        user = User.objects.filter(id=user_id).first()
        if user is None:
            payment.status = Payment.StatusChoices.FAILED
            payment.reason = Payment.ReasonChoices.RECIPIENT_NOT_FOUND
            payment.save()
            return HttpResponse(content="User not found", status=404)

        order = Order.objects.filter(id=order_id).first()

        if order is None:
            payment.status = Payment.StatusChoices.FAILED
            payment.reason = Payment.ReasonChoices.RECIPIENT_NOT_FOUND
            payment.save()
            return HttpResponse(content="Order not found", status=404)

        payment.status = Payment.StatusChoices.COMPLETED
        payment.order = order
        payment.transaction_id = session['id']
        payment.stripe_payment_intent = session['payment_intent']
        payment.save()

        for course in order.courses.all():
            Enrollment.objects.get_or_create(
                student=user,
                course=course,
            )

    return HttpResponse(status=200)
