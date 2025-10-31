# API Endpoints Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://api.11tutors.com
```

## API Structure

All API endpoints are prefixed with `/api/` except for the admin panel and webhooks.

---

## Authentication Endpoints

Base path: `/api/auth/`

### Token Management

#### Obtain JWT Token (Login)

```http
POST /api/auth/token/
```

**Permission**: AllowAny

**Request Body**:

```json
{
	"email": "user@example.com",
	"password": "securepassword"
}
```

**Response** (200 OK):

```json
{
	"access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response** (401 Unauthorized):

```json
{
	"detail": "No active account found with the given credentials"
}
```

---

#### Refresh Access Token

```http
POST /api/auth/token/refresh/
```

**Permission**: AllowAny

**Request Body**:

```json
{
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):

```json
{
	"access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### User Management

#### Register New User

```http
POST /api/auth/users/
```

**Permission**: AllowAny

**Request Body**:

```json
{
	"email": "newuser@example.com",
	"password": "securepassword123",
	"first_name": "John",
	"last_name": "Doe"
}
```

**Response** (201 Created):

```json
{
	"id": "123456789012",
	"email": "newuser@example.com",
	"first_name": "John",
	"last_name": "Doe",
	"role": 4,
	"is_email_verified": false,
	"created_at": "2024-01-01T00:00:00Z",
	"updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### Get Current User Profile

```http
GET /api/auth/users/me/
```

**Permission**: IsAuthenticated

**Headers**:

```
Authorization: Bearer <access_token>
```

**Response** (200 OK):

```json
{
	"id": "123456789012",
	"email": "user@example.com",
	"first_name": "John",
	"last_name": "Doe",
	"role": 4,
	"is_email_verified": true,
	"created_at": "2024-01-01T00:00:00Z",
	"updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### Update Current User Profile

```http
PATCH /api/auth/users/me/
```

**Permission**: IsAuthenticated

**Request Body** (partial update):

```json
{
	"first_name": "Jane",
	"last_name": "Smith"
}
```

**Response** (200 OK):

```json
{
	"id": "123456789012",
	"email": "user@example.com",
	"first_name": "Jane",
	"last_name": "Smith",
	"role": 4,
	"is_email_verified": true,
	"created_at": "2024-01-01T00:00:00Z",
	"updated_at": "2024-01-01T12:30:00Z"
}
```

---

#### List All Users

```http
GET /api/auth/users/
```

**Permission**: IsAuthenticated

**Query Parameters**:

- `role`: Filter by role (1, 2, 3, 4)
- `is_email_verified`: Filter by verification status (true/false)
- `search`: Search by username, email, first_name, last_name, id
- `ordering`: Order by created_at, updated_at (prefix with `-` for descending)
- `page`: Page number for pagination

**Example**:

```
GET /api/auth/users/?role=2&is_email_verified=true&search=john&page=1
```

**Response** (200 OK):

```json
{
	"count": 50,
	"next": "http://localhost:8000/api/auth/users/?page=2",
	"previous": null,
	"results": [
		{
			"id": "123456789012",
			"email": "user@example.com",
			"first_name": "John",
			"last_name": "Doe",
			"role": 2,
			"is_email_verified": true,
			"created_at": "2024-01-01T00:00:00Z",
			"updated_at": "2024-01-01T00:00:00Z"
		}
	]
}
```

---

#### Get Specific User

```http
GET /api/auth/users/{id}/
```

**Permission**: IsAuthenticated

---

#### Update Specific User

```http
PATCH /api/auth/users/{id}/
PUT /api/auth/users/{id}/
```

**Permission**: IsAuthenticated

---

#### Delete User

```http
DELETE /api/auth/users/{id}/
```

**Permission**: IsAuthenticated

**Response** (204 No Content)

---

### Tutor Management

#### Register as Tutor

```http
POST /api/auth/tutors/
```

**Permission**: AllowAny

**Request Body**:

```json
{
	"email": "tutor@example.com",
	"password": "securepassword123",
	"first_name": "Jane",
	"last_name": "Teacher"
}
```

**Response** (201 Created):

```json
{
	"id": "987654321098",
	"email": "tutor@example.com",
	"first_name": "Jane",
	"last_name": "Teacher",
	"role": 2,
	"is_email_verified": false,
	"created_at": "2024-01-01T00:00:00Z",
	"updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### Get Tutor Profile

```http
GET /api/auth/tutors/me/
```

**Permission**: IsAuthenticated (Tutor role)

---

#### Get Tutor's Courses

```http
GET /api/auth/tutors/me/courses/
```

**Permission**: IsAuthenticated (Tutor role)

**Response** (200 OK):

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "title": "Introduction to Python",
      "slug": "introduction-to-python",
      "description": "Learn Python from scratch",
      "price": "99.99",
      "thumbnail": "https://cdn.example.com/thumbnails/python.jpg",
      "tutors": [...],
      "category": {...},
      "parts": [...],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

#### Get Quick Statistics

```http
GET /api/auth/tutors/me/quick_statistics/
```

**Permission**: IsAuthenticated (Tutor role)

**Response** (200 OK):

```json
{
	"total_earnings": "5000.00",
	"active_students": 150,
	"published_courses": 5,
	"average_rating": 4.5
}
```

---

### Onboarding

#### Create Onboarding Answer

```http
POST /api/auth/onboarding-answers/
```

**Permission**: IsAuthenticated

**Request Body**:

```json
{
	"university": 1,
	"degree": "Computer Science",
	"graduation_year": 2025,
	"interests": "Web Development, Machine Learning"
}
```

**Response** (201 Created):

```json
{
	"id": 1,
	"user": "123456789012",
	"university": 1,
	"degree": "Computer Science",
	"graduation_year": 2025,
	"interests": "Web Development, Machine Learning",
	"created_at": "2024-01-01T00:00:00Z",
	"updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### Get User's Onboarding Answers

```http
GET /api/auth/onboarding-answers/
```

**Permission**: IsAuthenticated

---

## Course Endpoints

Base path: `/api/courses/`

### Categories

#### List All Categories

```http
GET /api/courses/categories/
```

**Permission**: IsAuthenticated

**Response** (200 OK):

```json
{
	"count": 10,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"name": "Programming",
			"slug": "programming"
		},
		{
			"id": 2,
			"name": "Data Science",
			"slug": "data-science"
		}
	]
}
```

---

#### Create Category

```http
POST /api/courses/categories/
```

**Permission**: IsAuthenticated

**Request Body**:

```json
{
	"name": "Web Development",
	"description": "Learn to build websites and web applications"
}
```

---

#### Get Category

```http
GET /api/courses/categories/{id}/
```

---

#### Update Category

```http
PATCH /api/courses/categories/{id}/
PUT /api/courses/categories/{id}/
```

---

#### Delete Category

```http
DELETE /api/courses/categories/{id}/
```

---

### Courses

#### List All Courses

```http
GET /api/courses/courses/
```

**Permission**: AllowAny

**Query Parameters**:

- `search`: Search in title, description
- `ordering`: Order by created_at, updated_at, price
- `page`: Page number

**Response** (200 OK):

```json
{
	"count": 25,
	"next": "http://localhost:8000/api/courses/courses/?page=2",
	"previous": null,
	"results": [
		{
			"id": "uuid-here",
			"title": "Python for Beginners",
			"slug": "python-for-beginners",
			"description": "Complete Python course",
			"price": "99.99",
			"thumbnail": "https://cdn.example.com/thumbnails/python.jpg",
			"tutors": [
				{
					"id": "tutor-id",
					"first_name": "Jane",
					"last_name": "Teacher",
					"email": "jane@example.com"
				}
			],
			"category": {
				"id": 1,
				"name": "Programming",
				"slug": "programming"
			},
			"parts": [
				{
					"id": "part-uuid",
					"title": "Introduction",
					"order": 0
				}
			],
			"created_at": "2024-01-01T00:00:00Z",
			"updated_at": "2024-01-01T00:00:00Z"
		}
	]
}
```

---

#### Get Course Details

```http
GET /api/courses/courses/{slug}/
```

**Permission**: AllowAny

**Response** (200 OK):

```json
{
  "id": "uuid-here",
  "title": "Python for Beginners",
  "slug": "python-for-beginners",
  "description": "Complete Python course with hands-on projects",
  "price": "99.99",
  "thumbnail": "https://cdn.example.com/thumbnails/python.jpg",
  "tutors": [...],
  "is_enrolled": false,
  "parts": [
    {
      "id": "part-uuid",
      "title": "Introduction to Python",
      "order": 0,
      "lessons": [
        {
          "id": "lesson-uuid",
          "title": "What is Python?",
          "slug": "what-is-python",
          "order": 0,
          "duration": "00:10:30",
          "created_at": "2024-01-01T00:00:00Z",
          "is_free_preview": true
        }
      ]
    }
  ],
  "categories": [...],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### Create Course

```http
POST /api/courses/courses/
```

**Permission**: IsAuthenticated

**Request Body** (multipart/form-data):

```json
{
  "title": "New Course",
  "description": "Course description",
  "category": 1,
  "price": "149.99",
  "thumbnail": <file>,
  "is_published": false
}
```

**Response** (201 Created)

---

#### Update Course

```http
PATCH /api/courses/courses/{slug}/
PUT /api/courses/courses/{slug}/
```

**Permission**: IsAuthenticated

---

#### Delete Course

```http
DELETE /api/courses/courses/{slug}/
```

**Permission**: IsAuthenticated

---

### Course Parts

#### List Course Parts

```http
GET /api/courses/course-parts/
```

**Permission**: IsAuthenticated

---

#### Create Course Part

```http
POST /api/courses/course-parts/
```

**Permission**: IsAuthenticated

**Request Body**:

```json
{
	"course": "course-uuid",
	"title": "Advanced Topics",
	"description": "Deep dive into advanced concepts",
	"order": 2
}
```

**Response** (201 Created):

```json
{
	"id": "part-uuid",
	"title": "Advanced Topics",
	"order": 2,
	"course": "course-uuid",
	"created_at": "2024-01-01T00:00:00Z",
	"updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### Get Course Part

```http
GET /api/courses/course-parts/{id}/
```

---

#### Update Course Part

```http
PATCH /api/courses/course-parts/{id}/
PUT /api/courses/course-parts/{id}/
```

---

#### Delete Course Part

```http
DELETE /api/courses/course-parts/{id}/
```

---

### Lessons

#### List Lessons

```http
GET /api/courses/lessons/
```

**Permission**: AllowAny (retrieve), IsAuthenticated (other actions)

**Response**: Ordered by part order, then lesson order

---

#### Get Lesson Details

```http
GET /api/courses/lessons/{slug}/
```

**Permission**: AllowAny

**Access Control**:

- Free preview lessons: Anyone can access
- Paid lessons: Only enrolled students can access

**Response** (200 OK):

```json
{
	"id": "lesson-uuid",
	"title": "Introduction to Variables",
	"slug": "introduction-to-variables",
	"description": "Learn about variables in Python",
	"is_free_preview": false,
	"order": 1,
	"duration": "00:15:30",
	"created_at": "2024-01-01T00:00:00Z",
	"otp": "vdocipher-otp-token",
	"playbackInfo": "vdocipher-playback-info"
}
```

**Error Response** (404 Not Found):

```json
{
	"detail": "Not found."
}
```

Note: Returns 404 if user is not enrolled and lesson is not free preview.

---

#### Create Lesson

```http
POST /api/courses/lessons/
```

**Permission**: IsAuthenticated

**Request Body**:

```json
{
	"part": "part-uuid",
	"title": "New Lesson",
	"description": "Lesson description",
	"video_service_id": "vdocipher-video-id",
	"order": 3,
	"duration": "00:20:00",
	"is_free_preview": false
}
```

---

#### Update Lesson

```http
PATCH /api/courses/lessons/{slug}/
PUT /api/courses/lessons/{slug}/
```

---

#### Delete Lesson

```http
DELETE /api/courses/lessons/{slug}/
```

---

### Comments

#### List Comments

```http
GET /api/courses/comments/
```

**Permission**: IsAuthenticated

**Query Parameters**:

- `lesson`: Filter by lesson ID

**Response**: Ordered by creation date (newest first)

---

#### Create Comment

```http
POST /api/courses/comments/
```

**Permission**: IsAuthenticated

**Request Body**:

```json
{
	"lesson": "lesson-uuid",
	"text": "Great explanation! Very helpful."
}
```

---

#### Update Comment

```http
PATCH /api/courses/comments/{id}/
PUT /api/courses/comments/{id}/
```

---

#### Delete Comment

```http
DELETE /api/courses/comments/{id}/
```

---

### Enrollments

#### List User's Enrollments

```http
GET /api/courses/enrollments/
```

**Permission**: IsAuthenticated

**Response** (200 OK):

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "enrollment-uuid",
      "student": {...},
      "course": {...},
      "enrolled_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

#### Get Enrollment Details

```http
GET /api/courses/enrollments/{id}/
```

**Permission**: IsAuthenticated

---

## Payment Endpoints

Base path: `/api/payments/`

### Payments

#### List User's Payments

```http
GET /api/payments/payments/
```

**Permission**: IsAuthenticated

**Query Parameters**:

- `user`: Filter by user ID

**Response** (200 OK):

```json
{
	"count": 10,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": "payment-uuid",
			"amount": "99.99",
			"currency": "USD",
			"status": 2,
			"created_at": "2024-01-01T00:00:00Z"
		}
	]
}
```

---

#### Create Payment (Checkout)

```http
POST /api/payments/payments/
```

**Permission**: IsAuthenticated

**Request Body**:

```json
{
	"course_id": "course-uuid"
}
```

**Response** (200 OK):

```json
{
	"checkout_session_id": "cs_test_stripe_session_id"
}
```

**Process**:

1. Creates Order with course
2. Creates Payment record (status: PENDING)
3. Creates Stripe Checkout Session
4. Returns session ID for frontend redirect

**Error Response** (404 Not Found):

```json
{
	"detail": "No course found with given slug"
}
```

---

#### Get Payment Details

```http
GET /api/payments/payments/{id}/
```

**Permission**: IsAuthenticated

---

### Stripe Webhook

```http
POST /api/payments/stripe/webhook/
POST /webhook/
```

**Permission**: Public (verified by Stripe signature)

**Headers**:

```
Stripe-Signature: <stripe-signature>
```

**Process**:

1. Verifies Stripe signature
2. Handles `checkout.session.completed` event
3. Updates Payment status to COMPLETED
4. Creates Enrollment for user and course
5. Returns 200 OK

**Event Handling**:

```json
{
	"type": "checkout.session.completed",
	"data": {
		"object": {
			"id": "cs_test_...",
			"payment_intent": "pi_test_...",
			"metadata": {
				"user_id": "123456789012",
				"order_id": "order-uuid",
				"payment_id": "payment-uuid"
			}
		}
	}
}
```

---

## Core Endpoints

Base path: `/api/core/`

### Universities

#### List Universities

```http
GET /api/core/universities/
```

**Permission**: AllowAny

**Response** (200 OK):

```json
{
	"count": 50,
	"next": "http://localhost:8000/api/core/universities/?page=2",
	"previous": null,
	"results": [
		{
			"id": 1,
			"name": "Harvard University",
			"description": "Private Ivy League research university",
			"logo": "https://cdn.example.com/logos/harvard.png",
			"website": "https://www.harvard.edu",
			"country": "United States",
			"city": "Cambridge",
			"location": "Cambridge, MA 02138",
			"global_rank": 1,
			"country_rank": 1,
			"created_at": "2024-01-01T00:00:00Z",
			"updated_at": "2024-01-01T00:00:00Z"
		}
	]
}
```

---

#### Get University Details

```http
GET /api/core/universities/{id}/
```

**Permission**: AllowAny

---

## Admin Panel

```http
GET /admin/
```

**Permission**: Staff users only (is_staff=True)

**Features**:

- User management
- Course management
- Payment tracking
- Order management
- Category management
- University management

---

## Error Responses

### 400 Bad Request

```json
{
	"field_name": ["Error message for this field"],
	"another_field": ["Another error message"]
}
```

### 401 Unauthorized

```json
{
	"detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
	"detail": "You do not have permission to perform this action."
}
```

### 404 Not Found

```json
{
	"detail": "Not found."
}
```

### 500 Internal Server Error

```json
{
	"detail": "Internal server error"
}
```

---

## Pagination

All list endpoints support pagination with the following format:

**Query Parameters**:

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 100, max: 100)

**Response Format**:

```json
{
  "count": 250,
  "next": "http://localhost:8000/api/resource/?page=3",
  "previous": "http://localhost:8000/api/resource/?page=1",
  "results": [...]
}
```

---

## Filtering

Supported on specific endpoints:

**User Filtering**:

- `role`: 1, 2, 3, 4
- `is_email_verified`: true, false

**Search**:

- `search`: Full-text search across specified fields

**Ordering**:

- `ordering`: Field name (prefix with `-` for descending)
- Examples: `created_at`, `-created_at`, `price`, `-price`

---

## Rate Limiting

Currently not implemented. Ready for Django REST Framework throttling:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
```

---

## CORS Configuration

Configured in settings.py:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://11tutors.com"
]
```

All API endpoints support CORS for configured origins.
