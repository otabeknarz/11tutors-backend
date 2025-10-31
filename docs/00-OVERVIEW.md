# 11Tutors Backend - System Overview

## Project Description

**11Tutors** is an online learning platform that connects tutors with students through video-based courses. The backend is built with Django and Django REST Framework, providing a robust API for course management, user authentication, payment processing, and video content delivery.

## Technology Stack

### Core Framework

- **Django 5.2.1** - Web framework
- **Django REST Framework 3.16.0** - API development
- **Python 3.x** - Programming language

### Authentication & Security

- **djangorestframework-simplejwt 5.5.0** - JWT token authentication
- **django-cors-headers 4.7.0** - CORS handling
- Custom email verification system

### Database

- **PostgreSQL** (via psycopg2-binary 2.9.10)
- **dj-database-url 3.0.1** - Database configuration
- SQLite3 for development

### File Storage

- **django-storages 1.14.6** - Cloud storage integration
- **boto3 1.40.30** - AWS S3/Cloudflare R2 integration
- **Pillow 11.2.1** - Image processing

### Payment Processing

- **Stripe 12.2.0** - Payment gateway integration
- Webhook handling for payment events

### Video Service

- **VdoCipher** - Video hosting and streaming
- OTP-based video access control

### Additional Tools

- **django-filter 25.1** - Advanced filtering
- **python-slugify 8.0.4** - URL slug generation
- **python-dotenv 1.1.0** - Environment variable management
- **gunicorn 23.0.0** - Production WSGI server

## Project Structure

```
backend/
├── eleven_tutors/          # Main project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py            # Root URL configuration
│   ├── base_model.py      # Abstract base model
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
│
├── users/                  # User management app
│   ├── models.py          # User, OnboardingAnswer models
│   ├── admin.py           # Admin configuration
│   └── api/               # API endpoints
│       ├── views.py       # User ViewSets
│       ├── serializers.py # User serializers
│       ├── auth_views.py  # JWT authentication views
│       ├── email_tools.py # Email verification utilities
│       └── urls.py        # User API routes
│
├── courses/                # Course management app
│   ├── models.py          # Course, CoursePart, Lesson, etc.
│   ├── admin.py           # Admin configuration
│   └── api/               # API endpoints
│       ├── views.py       # Course ViewSets
│       ├── serializers.py # Course serializers
│       └── urls.py        # Course API routes
│
├── payments/               # Payment processing app
│   ├── models.py          # Payment, Order models
│   ├── admin.py           # Admin configuration
│   └── api/               # API endpoints
│       ├── views.py       # Payment ViewSets & webhooks
│       ├── serializers.py # Payment serializers
│       └── urls.py        # Payment API routes
│
├── core/                   # Core utilities app
│   ├── models.py          # University model
│   ├── admin.py           # Admin configuration
│   └── api/               # API endpoints
│       ├── views.py       # Core ViewSets
│       ├── serializers.py # Core serializers
│       └── urls.py        # Core API routes
│
├── media/                  # User-uploaded files
├── static/                 # Static files
├── db.sqlite3             # Development database
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (gitignored)
```

## Key Features

### 1. User Management

- Custom user model with email-based authentication
- Role-based access control (Admin, Tutor, Student, User)
- Email verification system
- JWT token authentication
- User onboarding with university affiliation

### 2. Course Management

- Hierarchical course structure (Course → CoursePart → Lesson)
- Category-based organization
- Tutor assignment (many-to-many)
- Course thumbnails with cloud storage
- Draft and published states
- Slug-based URLs

### 3. Video Content Delivery

- VdoCipher integration for secure video hosting
- OTP-based video access
- Free preview lessons
- Enrollment-based access control
- Video duration tracking

### 4. Payment Processing

- Stripe Checkout integration
- Order management system
- Payment status tracking (Pending, Completed, Failed, Refunded)
- Webhook handling for payment events
- Automatic enrollment after successful payment
- Multi-currency support

### 5. Enrollment System

- Course enrollment tracking
- Student-course relationship management
- Enrollment-based content access

### 6. Comments & Interaction

- Lesson-level comments
- User-generated content

## API Architecture

### Base URL Structure

```
/api/auth/          # Authentication endpoints
/api/users/         # User management
/api/tutors/        # Tutor-specific endpoints
/api/courses/       # Course management
/api/core/          # Core utilities (universities)
/api/payments/      # Payment processing
/admin/             # Django admin panel
```

### Authentication Flow

1. User registers via `/api/auth/users/`
2. User logs in via `/api/auth/token/` (receives JWT tokens)
3. Access token used in Authorization header: `Bearer <token>`
4. Refresh token used via `/api/auth/token/refresh/`

### Permission System

- **AllowAny**: Public endpoints (course listing, registration)
- **IsAuthenticated**: Protected endpoints (user profile, enrollments)
- **Custom permissions**: Role-based access for tutors/admins

## Database Schema

### Core Models

- **User**: Custom user with email authentication
- **Course**: Main course entity
- **CoursePart**: Course sections/modules
- **Lesson**: Individual video lessons
- **Category**: Course categorization
- **Enrollment**: Student-course relationship
- **Payment**: Payment transactions
- **Order**: Purchase orders
- **Comment**: Lesson comments
- **University**: Educational institutions
- **OnboardingAnswer**: User onboarding data

## Environment Configuration

Required environment variables (stored in `.env`):

```bash
# Django
DJANGO_SECRET_KEY=<secret-key>
DJANGO_DEBUG=True/False

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# CORS & CSRF
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000

# Email
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<password>

# VdoCipher
VIDEO_SERVICE_SECRET_KEY=<vdocipher-api-key>

# Stripe
STRIPE_SECRET_KEY=<stripe-secret>
STRIPE_PUBLIC_KEY=<stripe-public>
STRIPE_WEBHOOK_SECRET=<webhook-secret>
FRONTEND_URL=http://localhost:3000

# Cloudflare R2 / AWS S3
R2_ACCESS_KEY_ID=<access-key>
R2_SECRET_ACCESS_KEY=<secret-key>
R2_BUCKET_NAME=<bucket-name>
R2_ENDPOINT_URL=<endpoint-url>
```

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **CORS Protection**: Configured allowed origins
3. **CSRF Protection**: Django CSRF middleware
4. **Password Validation**: Django's built-in validators
5. **Email Verification**: Token-based email verification
6. **Secure Video Access**: OTP-based VdoCipher integration
7. **Payment Security**: Stripe webhook signature verification
8. **Environment Variables**: Sensitive data in .env file

## Development Workflow

### Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Edit with your values

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Common Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Shell access
python manage.py shell
```

## API Response Format

### Success Response

```json
{
	"id": "uuid-or-id",
	"field1": "value1",
	"field2": "value2",
	"created_at": "2024-01-01T00:00:00Z",
	"updated_at": "2024-01-01T00:00:00Z"
}
```

### Error Response

```json
{
	"detail": "Error message",
	"field_name": ["Error for specific field"]
}
```

### Paginated Response

```json
{
  "count": 100,
  "next": "http://api.example.com/api/resource/?page=2",
  "previous": null,
  "results": [...]
}
```

## Integration Points

### Frontend Integration

- RESTful API with JSON responses
- JWT token authentication
- CORS configured for frontend domain
- File upload support for thumbnails

### VdoCipher Integration

- Video upload via VdoCipher API
- OTP generation for secure playback
- Video metadata storage

### Stripe Integration

- Checkout session creation
- Webhook event handling
- Payment status synchronization

### Cloudflare R2 / S3 Integration

- File storage for thumbnails and media
- Presigned URLs for secure access
- Automatic file management

## Performance Considerations

1. **Database Indexing**: Email, slug fields indexed
2. **Query Optimization**: Select_related, prefetch_related used
3. **Pagination**: Default 100 items per page
4. **Caching**: Ready for Redis/Memcached integration
5. **Static Files**: Served via CDN in production

## Monitoring & Logging

- Django logging configured
- Error tracking ready for Sentry integration
- Admin panel for data inspection
- Payment webhook logging

## Next Steps for Development

1. Add comprehensive test coverage
2. Implement caching layer (Redis)
3. Add API rate limiting
4. Implement search functionality (Elasticsearch)
5. Add real-time features (WebSockets)
6. Enhance analytics and reporting
7. Add content moderation tools
8. Implement notification system
