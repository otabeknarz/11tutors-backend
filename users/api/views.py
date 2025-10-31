from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Sum, Avg, Q
from datetime import datetime, timedelta
from django.utils import timezone

from courses.api.serializers import Course, CourseSerializer
from courses.models import Enrollment, Comment
from payments.models import Payment, Order
from .serializers import UserSerializer, TutorSerializer, OnboardingAnswerSerializer
from users.models import User, OnboardingAnswer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_email_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'id']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TutorViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role=User.RoleChoices.TUTOR)
    serializer_class = TutorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_email_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'id']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['get'], url_path='me/quick_statistics')
    def quick_statistics(self, request):
        """Get quick statistics for tutor dashboard"""
        tutor = request.user
        
        # Get tutor's courses
        tutor_courses = Course.objects.filter(tutors=tutor).distinct()
        
        # Calculate total earnings from completed payments
        total_earnings = Payment.objects.filter(
            order__courses__tutors=tutor,
            status=Payment.StatusChoices.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Count active students (unique enrollments)
        active_students = Enrollment.objects.filter(
            course__tutors=tutor
        ).values('student').distinct().count()
        
        # Count published and draft courses
        published_courses = tutor_courses.filter(is_published=True).count()
        draft_courses = tutor_courses.filter(is_published=False).count()
        
        # Calculate average rating and reviews (placeholder - implement when rating system is added)
        average_rating = 4.5  # Default rating
        total_reviews = Comment.objects.filter(
            lesson__part__course__tutors=tutor
        ).count()
        
        # Get recent enrollments (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_enrollments = Enrollment.objects.filter(
            course__tutors=tutor,
            created_at__gte=week_ago
        ).count()
        
        # Get monthly earnings for the last 6 months
        monthly_earnings = []
        for i in range(5, -1, -1):
            month_start = timezone.now() - timedelta(days=30 * i)
            month_end = timezone.now() - timedelta(days=30 * (i - 1)) if i > 0 else timezone.now()
            
            month_data = Payment.objects.filter(
                order__courses__tutors=tutor,
                status=Payment.StatusChoices.COMPLETED,
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(
                earnings=Sum('amount'),
                students=Count('order__user', distinct=True)
            )
            
            monthly_earnings.append({
                'month': month_start.strftime('%b'),
                'earnings': float(month_data['earnings'] or 0),
                'students': month_data['students'] or 0
            })
        
        # Get course performance
        course_performance = []
        for course in tutor_courses.filter(is_published=True)[:6]:  # Top 6 courses
            students_count = Enrollment.objects.filter(course=course).count()
            
            course_earnings = Payment.objects.filter(
                order__courses=course,
                status=Payment.StatusChoices.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            course_performance.append({
                'id': str(course.id),
                'title': course.title,
                'students': students_count,
                'rating': 4.5,  # Default rating until rating system is implemented
                'earnings': float(course_earnings)
            })
        
        return Response({
            'total_earnings': float(total_earnings),
            'active_students': active_students,
            'published_courses': published_courses,
            'draft_courses': draft_courses,
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'recent_enrollments': recent_enrollments,
            'monthly_earnings': monthly_earnings,
            'course_performance': course_performance
        })

    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        pass

    @action(detail=False, methods=['get'], url_path='courses-statistics')
    def courses_statistics(self, request):
        pass

    @action(detail=False, methods=['get'], url_path='earnings-statistics')
    def earnings_statistics(self, request):
        pass

    @action(detail=False, methods=['get'], url_path='payment-statistics')
    def payment_statistics(self, request):
        pass

    @action(detail=False, methods=['get', 'post'], url_path='me/courses')
    def get_courses(self, request):
        """Get tutor's courses with statistics"""
        tutor = request.user

        if request.method == 'GET':
            courses = tutor.courses.all().order_by('-created_at')
            
            # Add statistics to each course
            courses_data = []
            for course in courses:
                # Get students count
                students_count = Enrollment.objects.filter(course=course).count()
                
                # Get reviews count
                reviews_count = Comment.objects.filter(
                    lesson__part__course=course
                ).count()
                
                # Get earnings
                earnings = Payment.objects.filter(
                    order__courses=course,
                    status=Payment.StatusChoices.COMPLETED
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                # Get lessons count
                lessons_count = course.parts.aggregate(
                    total=Count('lessons')
                )['total'] or 0
                
                course_data = CourseSerializer(course, context={'request': request}).data
                course_data.update({
                    'students_count': students_count,
                    'rating': 4.5,  # Default rating
                    'reviews_count': reviews_count,
                    'earnings': float(earnings),
                    'lessons_count': lessons_count
                })
                courses_data.append(course_data)
            
            return Response({
                'results': courses_data,
                'count': len(courses_data)
            })

        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class OnboardingAnswerViewSet(viewsets.ModelViewSet):
    queryset = OnboardingAnswer.objects.all()
    serializer_class = OnboardingAnswerSerializer

    def get_queryset(self):
        return OnboardingAnswer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
