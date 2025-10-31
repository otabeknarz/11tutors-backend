# 11Tutors Backend Documentation

## Welcome

This is the comprehensive documentation for the **11Tutors** backend system - an online learning platform built with Django and Django REST Framework.

---

## Documentation Structure

### [00 - System Overview](./00-OVERVIEW.md)

Complete overview of the backend architecture, technology stack, project structure, and key features.

**Topics Covered**:

- Technology stack and dependencies
- Project structure and organization
- Key features and capabilities
- API architecture
- Database schema overview
- Environment configuration
- Security features
- Development workflow

---

### [01 - Authentication System](./01-AUTHENTICATION.md)

In-depth guide to the JWT-based authentication system.

**Topics Covered**:

- Authentication flow (registration, login, token refresh)
- Custom User model with email-based authentication
- User roles (Admin, Tutor, Student, User)
- Email verification system
- JWT configuration and token management
- Permission classes and access control
- API endpoints for authentication
- Security best practices
- Frontend integration examples

---

### [02 - Database Models](./02-MODELS.md)

Complete documentation of all database models and relationships.

**Topics Covered**:

- BaseModel abstract class
- User and OnboardingAnswer models
- Course, CoursePart, Lesson models
- Category and Comment models
- Enrollment model
- Payment and Order models
- University model
- Model relationships and foreign keys
- Database indexes and constraints
- Query optimization techniques
- Migration strategies

---

### [03 - API Endpoints](./03-API-ENDPOINTS.md)

Comprehensive API reference with request/response examples.

**Topics Covered**:

- Authentication endpoints (token, user management)
- Tutor-specific endpoints
- Course management endpoints
- Lesson and video access endpoints
- Payment and checkout endpoints
- Stripe webhook handling
- Core endpoints (universities)
- Error responses and status codes
- Pagination and filtering
- CORS configuration

---

### [04 - Third-Party Integrations](./04-INTEGRATIONS.md)

Documentation for all external service integrations.

**Topics Covered**:

- **VdoCipher**: Secure video hosting and streaming
- **Stripe**: Payment processing and webhooks
- **Cloudflare R2 / AWS S3**: File storage
- **Email**: SMTP configuration and email sending
- **PostgreSQL**: Database configuration
- **CORS**: Cross-origin resource sharing
- Future integrations (Sentry, Redis, Celery, etc.)

---

### [05 - Deployment Guide](./05-DEPLOYMENT.md)

Step-by-step deployment instructions for production.

**Topics Covered**:

- Pre-deployment checklist
- Environment variables configuration
- Production settings and security
- VPS deployment (DigitalOcean, AWS EC2)
- PaaS deployment (Heroku, Railway, Render)
- Docker deployment
- Nginx and Gunicorn configuration
- SSL certificate setup
- Database migrations in production
- Monitoring and logging
- Backup strategies
- Performance optimization
- Scaling strategies
- Troubleshooting guide

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (production) or SQLite (development)
- pip and virtualenv

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/11tutors-backend.git
cd 11tutors-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Access Points

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: See [03-API-ENDPOINTS.md](./03-API-ENDPOINTS.md)

---

## Project Overview

### What is 11Tutors?

11Tutors is an online learning platform that connects tutors with students through video-based courses. The platform provides:

- **Course Management**: Create and organize courses with parts and lessons
- **Video Delivery**: Secure video streaming via VdoCipher
- **Payment Processing**: Stripe integration for course purchases
- **User Management**: Role-based access control (Admin, Tutor, Student)
- **Enrollment System**: Track student progress and course access
- **Comments**: Student interaction on lessons

### Technology Stack

- **Backend Framework**: Django 5.2.1
- **API Framework**: Django REST Framework 3.16.0
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL (production), SQLite (development)
- **File Storage**: Cloudflare R2 / AWS S3
- **Video Hosting**: VdoCipher
- **Payment Gateway**: Stripe
- **Server**: Gunicorn + Nginx

---

## API Structure

```
/api/
├── auth/                    # Authentication & user management
│   ├── token/              # JWT token obtain
│   ├── token/refresh/      # JWT token refresh
│   ├── users/              # User CRUD operations
│   ├── users/me/           # Current user profile
│   ├── tutors/             # Tutor management
│   └── onboarding-answers/ # User onboarding
│
├── courses/                 # Course management
│   ├── categories/         # Course categories
│   ├── courses/            # Course CRUD
│   ├── course-parts/       # Course sections
│   ├── lessons/            # Video lessons
│   ├── comments/           # Lesson comments
│   └── enrollments/        # Student enrollments
│
├── payments/                # Payment processing
│   ├── payments/           # Payment records
│   └── stripe/webhook/     # Stripe webhook handler
│
└── core/                    # Core utilities
    └── universities/        # University data

/admin/                      # Django admin panel
/webhook/                    # Alternative webhook endpoint
```

---

## Key Features

### 1. Secure Authentication

- JWT-based token authentication
- Email-based user accounts (no username)
- Role-based access control
- Email verification system
- Password hashing and validation

### 2. Course Management

- Hierarchical structure: Course → CoursePart → Lesson
- Category-based organization
- Multiple tutors per course
- Draft and published states
- Thumbnail images with cloud storage

### 3. Video Content Delivery

- VdoCipher integration for secure streaming
- OTP-based video access (5-minute validity)
- Free preview lessons
- Enrollment-based access control
- DRM protection

### 4. Payment Processing

- Stripe Checkout integration
- Automatic enrollment after payment
- Payment status tracking
- Webhook handling for payment events
- Multi-currency support

### 5. RESTful API

- Consistent JSON responses
- Pagination support (100 items per page)
- Filtering and search capabilities
- CORS enabled for frontend integration
- Comprehensive error handling

---

## Database Schema

### Core Entities

```
User (Custom email-based authentication)
├── Role: Admin, Tutor, Student, User
├── Email verification status
└── Timestamps

Course
├── Title, slug, description
├── Thumbnail image
├── Price
├── Category
├── Multiple tutors (M2M)
├── Published status
└── Parts (1-M)

CoursePart
├── Title, order
├── Course (M-1)
└── Lessons (1-M)

Lesson
├── Title, slug, description
├── VdoCipher video ID
├── Duration
├── Order
├── Free preview flag
└── Part (M-1)

Enrollment
├── Student (M-1)
├── Course (M-1)
└── Enrolled timestamp

Payment
├── User (M-1)
├── Amount, currency
├── Status (Pending, Completed, Failed, Refunded)
├── Stripe payment intent
└── Order (M-1)

Order
├── User (M-1)
├── Courses (M2M)
└── Total amount
```

---

## Development Workflow

### Common Commands

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

### Code Organization

```
backend/
├── eleven_tutors/      # Main project settings
├── users/              # User management app
├── courses/            # Course management app
├── payments/           # Payment processing app
├── core/               # Core utilities app
├── docs/               # Documentation (this folder)
├── media/              # User uploads (development)
├── static/             # Static files
└── manage.py           # Django management script
```

---

## Environment Configuration

### Required Environment Variables

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# VdoCipher
VIDEO_SERVICE_SECRET_KEY=your-vdocipher-api-key

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000

# Cloudflare R2 / AWS S3
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=your-bucket
R2_ENDPOINT_URL=https://your-endpoint.r2.cloudflarestorage.com
```

---

## Testing

### API Testing with cURL

```bash
# Register user
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Get profile (authenticated)
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test courses

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Write tests for new features

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request on GitHub
```

---

## Support & Resources

### Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [VdoCipher API](https://www.vdocipher.com/docs/)
- [Stripe API](https://stripe.com/docs/api)

### Community

- GitHub Issues: Report bugs and request features
- Email: support@11tutors.com

---

## License

[Add your license information here]

---

## Changelog

### Version 1.0.0 (Current)

- Initial release
- User authentication with JWT
- Course management system
- VdoCipher video integration
- Stripe payment processing
- Admin panel
- RESTful API

### Planned Features

- [ ] Course reviews and ratings
- [ ] Student progress tracking
- [ ] Certificate generation
- [ ] Live sessions integration
- [ ] Advanced analytics for tutors
- [ ] Mobile app API support
- [ ] Multi-language support
- [ ] Advanced search with Elasticsearch
- [ ] Real-time notifications
- [ ] Discussion forums

---

## Credits

Developed by the 11Tutors team.

**Technologies Used**:

- Django & Django REST Framework
- PostgreSQL
- VdoCipher
- Stripe
- Cloudflare R2
- Gunicorn & Nginx

---

For detailed information on specific topics, please refer to the individual documentation files listed at the top of this README.
