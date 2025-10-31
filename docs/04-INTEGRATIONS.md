# Third-Party Integrations Documentation

## Overview

The 11Tutors backend integrates with several third-party services for video hosting, payment processing, file storage, and email delivery.

---

## VdoCipher Integration

### Purpose

VdoCipher provides secure video hosting and streaming with DRM protection, preventing unauthorized downloads and screen recording.

### Configuration

Located in: `eleven_tutors/settings.py`

```python
VIDEO_SERVICE_SECRET_KEY = os.getenv("VIDEO_SERVICE_SECRET_KEY")

VDOCIPHER_HEADERS = {
    'Authorization': f"Apisecret {VIDEO_SERVICE_SECRET_KEY}",
    'Content-Type': "application/json",
    'Accept': "application/json"
}
```

### Environment Variables

```bash
VIDEO_SERVICE_SECRET_KEY=your_vdocipher_api_secret
```

### Video Upload Flow

1. **Frontend requests upload credentials** (not yet implemented in backend)
2. **Frontend uploads video directly to VdoCipher**
3. **Frontend receives video_id from VdoCipher**
4. **Frontend sends video_id to backend** when creating/updating lesson
5. **Backend stores video_id** in `Lesson.video_service_id`

### Video Playback Flow

Located in: `courses/api/views.py` - `LessonViewSet.retrieve()`

```python
def retrieve(self, request, slug=None, *args, **kwargs):
    lesson = Lesson.objects.filter(slug=slug).first()

    # Check enrollment or free preview
    enrollment = Enrollment.objects.filter(
        course=lesson.part.course,
        student=request.user
    ).first()

    not_allowed = not enrollment and not lesson.is_free_preview

    if not_allowed:
        return Response(status=404)

    # Generate OTP for video playback
    payload_str = json.dumps({"ttl": 300})  # 5 minutes

    response = requests.post(
        url=f"https://dev.vdocipher.com/api/videos/{lesson.video_service_id}/otp",
        headers=settings.VDOCIPHER_HEADERS,
        data=payload_str
    )

    json_response = response.json()
    data.update(json_response)

    return Response(data)
```

### OTP Response Format

```json
{
	"otp": "20160313versASE323gfas2eQws",
	"playbackInfo": "eyJ2aWRlb0lkIjoiM2Y0YjY0ZjU3ZjZjNGY2YTk1ZTZhMmI4ZjE5ZjQwZmEifQ=="
}
```

### Frontend Integration

```javascript
// Use VdoCipher player with OTP
const player = new VdoPlayer({
	otp: response.otp,
	playbackInfo: response.playbackInfo,
	theme: "9ae8bbe8dd964ddc9bdb932cca1cb59a",
	container: document.querySelector("#embedBox"),
});
```

### VdoCipher API Endpoints Used

1. **Generate OTP**: `POST https://dev.vdocipher.com/api/videos/{video_id}/otp`
   - Headers: Authorization with API secret
   - Body: `{"ttl": 300}` (time to live in seconds)
   - Returns: OTP and playbackInfo

### Security Features

- **OTP-based access**: Each playback requires a new OTP
- **Time-limited**: OTP expires after 5 minutes (300 seconds)
- **Enrollment check**: Only enrolled students or free preview access
- **DRM protection**: VdoCipher provides built-in DRM
- **No direct video URLs**: Videos cannot be accessed without OTP

### Best Practices

1. **Keep API secret secure**: Never expose in frontend code
2. **Short TTL**: Use 300 seconds (5 minutes) for OTP
3. **Verify enrollment**: Always check before generating OTP
4. **Handle errors**: VdoCipher API may fail, implement fallbacks
5. **Log video access**: Track which users access which videos

---

## Stripe Integration

### Purpose

Stripe handles payment processing, including credit card payments, checkout sessions, and webhook notifications.

### Configuration

Located in: `eleven_tutors/settings.py`

```python
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")
```

### Environment Variables

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
```

### Payment Flow

Located in: `payments/api/views.py` - `PaymentViewSet.create()`

#### 1. Create Checkout Session

```python
def create(self, request, *args, **kwargs):
    # Validate course
    course_id = request.data["course_id"]
    course = Course.objects.filter(id=course_id).first()

    # Create order
    order = Order.objects.create(
        user=request.user,
        total_amount=course.price,
    )
    order.courses.add(course)

    # Create payment record
    payment = Payment.objects.create(
        user=request.user,
        amount=course.price,
        method=Payment.PaymentMethodChoices.STRIPE,
        status=Payment.StatusChoices.PENDING,
    )

    # Create Stripe checkout session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(course.price * 100),  # Convert to cents
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
        success_url=f"{FRONTEND_URL}/dashboard/payment-success?course-slug={course.slug}",
        cancel_url=f"{FRONTEND_URL}/dashboard/payment-cancel",
    )

    return Response({'checkout_session_id': checkout_session.id})
```

#### 2. Frontend Redirects to Stripe

```javascript
const stripe = Stripe("pk_test_...");

const response = await fetch("/api/payments/payments/", {
	method: "POST",
	headers: {
		Authorization: `Bearer ${accessToken}`,
		"Content-Type": "application/json",
	},
	body: JSON.stringify({ course_id: courseId }),
});

const { checkout_session_id } = await response.json();

// Redirect to Stripe Checkout
await stripe.redirectToCheckout({
	sessionId: checkout_session_id,
});
```

#### 3. Webhook Handles Payment Completion

Located in: `payments/api/views.py` - `stripe_webhook()`

```python
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception:
        return HttpResponse(status=400)

    # Handle checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        order_id = session['metadata']['order_id']
        payment_id = session['metadata']['payment_id']

        # Update payment
        payment = Payment.objects.get(id=payment_id)
        payment.status = Payment.StatusChoices.COMPLETED
        payment.order = order
        payment.transaction_id = session['id']
        payment.stripe_payment_intent = session['payment_intent']
        payment.save()

        # Create enrollments
        order = Order.objects.get(id=order_id)
        for course in order.courses.all():
            Enrollment.objects.get_or_create(
                student=user,
                course=course,
            )

    return HttpResponse(status=200)
```

### Webhook Setup

1. **Configure webhook in Stripe Dashboard**:

   - URL: `https://yourdomain.com/api/payments/stripe/webhook/`
   - Events: `checkout.session.completed`

2. **Test webhook locally** (using Stripe CLI):

```bash
stripe listen --forward-to localhost:8000/api/payments/stripe/webhook/
```

### Payment States

```python
class StatusChoices(models.IntegerChoices):
    PENDING = (1, "Pending")      # Checkout session created
    COMPLETED = (2, "Completed")  # Payment successful
    FAILED = (-1, "Failed")       # Payment failed
    REFUNDED = (-2, "Refunded")   # Payment refunded
```

### Error Handling

```python
# User not found
if user is None:
    payment.status = Payment.StatusChoices.FAILED
    payment.reason = Payment.ReasonChoices.RECIPIENT_NOT_FOUND
    payment.save()
    return HttpResponse(content="User not found", status=404)

# Order not found
if order is None:
    payment.status = Payment.StatusChoices.FAILED
    payment.reason = Payment.ReasonChoices.RECIPIENT_NOT_FOUND
    payment.save()
    return HttpResponse(content="Order not found", status=404)
```

### Testing

#### Test Cards

```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
Insufficient funds: 4000 0000 0000 9995
```

#### Test Webhook

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/payments/stripe/webhook/

# Trigger test event
stripe trigger checkout.session.completed
```

### Security Features

1. **Webhook signature verification**: Prevents fake webhooks
2. **Metadata validation**: Ensures payment belongs to correct user
3. **Idempotency**: `get_or_create` prevents duplicate enrollments
4. **CSRF exemption**: Webhook endpoint exempt from CSRF (verified by signature)

---

## Cloudflare R2 / AWS S3 Integration

### Purpose

Cloudflare R2 (S3-compatible) stores user-uploaded files like course thumbnails and university logos.

### Configuration

Located in: `eleven_tutors/settings.py`

```python
AWS_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
AWS_S3_SIGNATURE_VERSION = "s3v4"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "location": "media",
            "default_acl": "private",
            "querystring_auth": True,
            "querystring_expire": 3600,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
        "OPTIONS": {
            "location": "static",
            "default_acl": "private",
            "querystring_auth": True,
            "querystring_expire": 3600,
        },
    },
}

STATIC_URL = f"{AWS_S3_ENDPOINT_URL}/static/"
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/media/"
```

### Environment Variables

```bash
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
```

### File Upload

Django automatically handles file uploads to R2/S3:

```python
# Model with file field
class Course(BaseModel):
    thumbnail = models.ImageField(upload_to="images/course_thumbnails/")

# Upload via API
# Frontend sends multipart/form-data
# Django saves to: media/images/course_thumbnails/filename.jpg
```

### File Access

```python
# Get presigned URL (valid for 1 hour)
course = Course.objects.get(id=course_id)
thumbnail_url = course.thumbnail.url  # Returns presigned URL

# URL format:
# https://account-id.r2.cloudflarestorage.com/media/images/course_thumbnails/file.jpg?X-Amz-Algorithm=...
```

### Storage Structure

```
bucket-name/
├── media/
│   ├── images/
│   │   └── course_thumbnails/
│   │       ├── course1.jpg
│   │       └── course2.png
│   └── logos/
│       └── university1.png
└── static/
    ├── admin/
    └── rest_framework/
```

### Security Features

1. **Private ACL**: Files not publicly accessible
2. **Presigned URLs**: Time-limited access (1 hour)
3. **Signature v4**: Secure URL signing
4. **Access control**: Only authenticated users can upload

### Best Practices

1. **Optimize images**: Compress before upload
2. **Use CDN**: Configure Cloudflare CDN for R2
3. **Set expiration**: Clean up old files periodically
4. **Validate uploads**: Check file type and size
5. **Use UUIDs**: Prevent filename collisions

---

## Email Integration

### Purpose

Send transactional emails for email verification, password reset, and notifications.

### Configuration

Located in: `eleven_tutors/settings.py`

```python
EMAIL_BACKEND = (
    'django.core.mail.backends.smtp.EmailBackend'
    if DEBUG
    else 'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### Environment Variables

```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Gmail Setup

1. **Enable 2-Factor Authentication** on Gmail
2. **Generate App Password**:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate password for "Mail" on "Other device"
3. **Use app password** in EMAIL_HOST_PASSWORD

### Sending Emails

Located in: `users/models.py` - `User.send_verification_email()`

```python
def send_verification_email(self):
    token = get_verification_token(self.email)
    subject = "Email Verification for 11-tutors.com"
    message = f"""
    Hi {self.username},
    Please verify your email address by clicking the link below:
    http://localhost:8000/verify-email?token={token}
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=None,  # Uses DEFAULT_FROM_EMAIL
        recipient_list=[self.email],
        fail_silently=False,
    )
```

### Email Types

1. **Email Verification**: After registration
2. **Password Reset**: Forgot password flow (not yet implemented)
3. **Order Confirmation**: After successful payment (not yet implemented)
4. **Course Updates**: Notify enrolled students (not yet implemented)

### Testing Emails

#### Development (Console Backend)

```python
# In DEBUG mode, emails printed to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

#### Production (SMTP Backend)

```python
# In production, emails sent via SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

### Email Templates

Currently using plain text. Future enhancement: HTML templates with Django templates.

```python
# Future: HTML email template
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

html_content = render_to_string('emails/verification.html', {
    'user': user,
    'token': token
})

msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
msg.attach_alternative(html_content, "text/html")
msg.send()
```

---

## Database Integration

### PostgreSQL (Production)

Configuration via `DATABASE_URL` environment variable:

```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
```

Parsed by `dj-database-url`:

```python
DATABASES = {
    "default": dj_database_url.config(default=os.getenv("DATABASE_URL"))
}
```

### SQLite (Development)

Default fallback if DATABASE_URL not set:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

### Connection Pooling

For production, consider adding connection pooling:

```bash
pip install psycopg2-pool
```

```python
DATABASES = {
    "default": {
        ...
        "CONN_MAX_AGE": 600,  # 10 minutes
    }
}
```

---

## CORS Configuration

### Purpose

Allow frontend (different domain) to access API.

### Configuration

```python
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
```

### Environment Variables

```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://11tutors.com
CSRF_TRUSTED_ORIGINS=http://localhost:3000,https://11tutors.com
```

### Middleware

```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be first
    "django.middleware.security.SecurityMiddleware",
    ...
]
```

---

## Future Integrations

### Planned

1. **Sentry**: Error tracking and monitoring
2. **Redis**: Caching and session storage
3. **Celery**: Background task processing
4. **Elasticsearch**: Full-text search
5. **SendGrid/Mailgun**: Professional email service
6. **Twilio**: SMS notifications
7. **Google Analytics**: Usage tracking
8. **Intercom**: Customer support chat

### Integration Checklist

- [ ] Sentry for error tracking
- [ ] Redis for caching
- [ ] Celery for async tasks
- [ ] Elasticsearch for search
- [ ] Professional email service
- [ ] SMS notifications
- [ ] Analytics integration
- [ ] Customer support chat
- [ ] CDN for static files
- [ ] Monitoring and alerting
