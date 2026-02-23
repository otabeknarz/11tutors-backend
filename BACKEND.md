# 11Tutors Backend

## Overview

Django 5.2 REST API backend for the 11Tutors online education platform. Provides JWT authentication, course management, video hosting (VdoCipher), Stripe payments, and file storage (Cloudflare R2).

**Django Project Name:** `eleven_tutors`
**Custom User Model:** `users.User` (email-based, no username)
**Database:** PostgreSQL (via `dj-database-url`), SQLite fallback for dev
**Static/Media Storage:** Cloudflare R2 via `django-storages` + `boto3`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.2.1 + DRF 3.16 |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL (`psycopg2-binary`) |
| Payments | Stripe (`stripe` 12.2) |
| Video | VdoCipher API |
| Storage | Cloudflare R2 (`django-storages` + `boto3`) |
| CORS | `django-cors-headers` |
| Filtering | `django-filter` |
| Server | Gunicorn |

---

## Project Structure

```
backend/
├── eleven_tutors/          # Django project config
│   ├── settings.py         # Main settings (env-driven)
│   ├── urls.py             # Root URL routing
│   ├── base_model.py       # Abstract BaseModel (created_at, updated_at)
│   ├── wsgi.py / asgi.py
│   └── __init__.py
├── users/                  # User management app
│   ├── models.py           # User, OnboardingAnswer
│   ├── admin.py
│   └── api/
│       ├── views.py        # UserViewSet, TutorViewSet, OnboardingAnswerViewSet
│       ├── serializers.py  # UserSerializer, TutorSerializer, OnboardingAnswerSerializer
│       ├── urls.py
│       ├── auth_views.py   # Custom JWT token views
│       └── email_tools.py  # Email verification token utils
├── courses/                # Course management app
│   ├── models.py           # Category, Course, CoursePart, Lesson, Comment, Enrollment
│   ├── admin.py
│   └── api/
│       ├── views.py        # CRUD ViewSets for all course models
│       ├── serializers.py  # Full serializer suite (list, detail, create)
│       ├── urls.py
│       └── vdocipher_views.py  # VdoCipher upload credentials & OTP
├── payments/               # Payment processing app
│   ├── models.py           # Order, Payment
│   ├── admin.py
│   └── api/
│       ├── views.py        # PaymentViewSet + stripe_webhook
│       ├── serializers.py  # PaymentSerializer, CreatePaymentSerializer
│       └── urls.py
├── core/                   # Shared/reference data app
│   ├── models.py           # University
│   └── api/
│       ├── views.py        # UniversityViewSet (read-only)
│       ├── serializers.py
│       └── urls.py
├── docs/                   # Existing detailed documentation
├── static/                 # Static files
├── media/                  # Media uploads (local dev)
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Data Models

### `users.User` (extends AbstractUser)
- **Primary Key:** `CharField(max_length=40)` — random 12-digit string
- **Auth field:** `email` (USERNAME_FIELD, unique)
- **username:** removed (set to `None`)
- **Roles:** `ADMIN=1`, `TUTOR=2`, `STUDENT=3`, `USER=4`
- **Fields:** `email`, `role`, `is_email_verified`, `created_at`, `updated_at`
- **Methods:** `send_verification_email()`, `verify_verification_token(token)`

### `users.OnboardingAnswer`
- FK to `User`, FK to `University`
- Fields: `degree`, `graduation_year`, `interests`

### `courses.Category`
- `name`, `slug` (auto-generated), `description`

### `courses.Course`
- **PK:** UUID
- `title`, `slug`, `thumbnail` (ImageField), `description`
- `tutors` (M2M → User), `category` (FK → Category)
- `price` (Decimal), `is_published` (Boolean)

### `courses.CoursePart`
- **PK:** UUID, FK to `Course`
- `title`, `slug`, `description`, `order`

### `courses.Lesson`
- **PK:** UUID, FK to `CoursePart`
- `title`, `slug`, `description`, `video_service_id` (VdoCipher)
- `order`, `duration`, `is_free_preview`

### `courses.Comment`
- **PK:** UUID, FK to `User`, FK to `Lesson`
- `text`

### `courses.Enrollment`
- **PK:** UUID, FK to `User` (student), FK to `Course`
- `enrolled_at`, unique_together: `(student, course)`

### `payments.Order`
- **PK:** UUID, FK to `User`
- `courses` (M2M → Course), `total_amount`

### `payments.Payment`
- **PK:** UUID, FK to `User`, FK to `Order`
- `amount`, `currency` (USD/UZS/EUR/RUB), `method` (CARD/STRIPE/BANK/CASH)
- `status` (PENDING=1, COMPLETED=2, FAILED=-1, REFUNDED=-2)
- `reason` (error codes), `transaction_id`, `stripe_payment_intent`
- Methods: `mark_completed()`, `mark_failed()`

### `core.University`
- `name`, `description`, `logo`, `website`
- `country`, `city`, `location`
- `global_rank`, `country_rank`

---

## API Endpoints

### Authentication (`/api/auth/`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/token/` | JWT login (email + password) |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET/POST | `/api/auth/users/` | List / Register user |
| GET/PATCH | `/api/auth/users/me/` | Current user profile |
| GET/POST | `/api/auth/tutors/` | List / Register tutor |
| GET/PATCH | `/api/auth/tutors/me/` | Current tutor profile |
| GET | `/api/auth/tutors/me/quick_statistics/` | Tutor dashboard stats |
| GET | `/api/auth/tutors/me/courses/` | Tutor's courses with stats |
| CRUD | `/api/auth/onboarding-answers/` | Onboarding answers |

### Courses (`/api/courses/`)
| Method | Endpoint | Description |
|---|---|---|
| CRUD | `/api/courses/categories/` | Categories |
| CRUD | `/api/courses/courses/` | Courses (lookup by slug) |
| CRUD | `/api/courses/course-parts/` | Course parts (lookup by slug) |
| CRUD | `/api/courses/lessons/` | Lessons (lookup by slug) |
| CRUD | `/api/courses/comments/` | Comments |
| GET | `/api/courses/enrollments/` | User's enrollments |
| POST | `/api/courses/vdocipher/upload-credentials/` | VdoCipher upload |
| GET | `/api/courses/vdocipher/video/<id>/otp/` | VdoCipher playback OTP |

### Payments (`/api/payments/`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/payments/payments/` | Create Stripe checkout session |
| GET | `/api/payments/payments/` | List payments |
| POST | `/api/payments/stripe/webhook/` | Stripe webhook handler |

### Core (`/api/core/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/core/universities/` | List universities (public) |

---

## Key Integrations

### VdoCipher (Video Hosting)
- Upload: `POST /api/courses/vdocipher/upload-credentials/` → calls VdoCipher PUT API
- Playback: `GET /api/courses/vdocipher/video/<id>/otp/` → returns OTP for secure playback
- Lesson `retrieve()` also fetches OTP inline for enrolled/free-preview lessons

### Stripe (Payments)
- `POST /api/payments/payments/` creates Order + Payment + Stripe Checkout Session
- Webhook at `/api/payments/stripe/webhook/` handles `checkout.session.completed`
- On success: marks Payment completed, creates Enrollment for all courses in Order

### Cloudflare R2 (Storage)
- All static and media files stored in R2 via `django-storages`
- Private ACL with signed URLs (1 hour expiry)

---

## Environment Variables

```env
DJANGO_SECRET_KEY=           # Django secret key
DJANGO_DEBUG=                # "true"/"1" for debug mode
DATABASE_URL=                # PostgreSQL connection string
VIDEO_SERVICE_SECRET_KEY=    # VdoCipher API secret
STRIPE_SECRET_KEY=           # Stripe secret key
STRIPE_PUBLIC_KEY=           # Stripe publishable key
STRIPE_WEBHOOK_SECRET=       # Stripe webhook signing secret
FRONTEND_URL=                # Frontend URL for redirects
CORS_ALLOWED_ORIGINS=        # Comma-separated origins
CSRF_TRUSTED_ORIGINS=        # Comma-separated origins
R2_ACCESS_KEY_ID=            # Cloudflare R2 access key
R2_SECRET_ACCESS_KEY=        # Cloudflare R2 secret key
R2_BUCKET_NAME=              # R2 bucket name
R2_ENDPOINT_URL=             # R2 endpoint URL
EMAIL_HOST_USER=             # Gmail SMTP user
EMAIL_HOST_PASSWORD=         # Gmail app password
```

---

## Running Locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # http://localhost:8000
```

Admin panel: `http://localhost:8000/admin/`

---

## JWT Configuration

- **Access token lifetime:** 1 day
- **Refresh token lifetime:** 7 days
- **Header:** `Authorization: Bearer <token>`
- **DEBUG mode:** AllowAny permissions (dev convenience)
- **Production:** IsAuthenticated by default
