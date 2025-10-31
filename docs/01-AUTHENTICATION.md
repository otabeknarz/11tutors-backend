# Authentication System Documentation

## Overview

The 11Tutors backend uses **JWT (JSON Web Token)** authentication via `djangorestframework-simplejwt`. This provides stateless, secure authentication for API endpoints.

## Authentication Flow

### 1. User Registration

**Endpoint**: `POST /api/auth/users/`

**Request Body**:

```json
{
	"email": "user@example.com",
	"password": "securepassword123",
	"first_name": "John",
	"last_name": "Doe"
}
```

**Response** (201 Created):

```json
{
	"id": "123456789012",
	"email": "user@example.com",
	"first_name": "John",
	"last_name": "Doe",
	"role": 4,
	"is_email_verified": false,
	"created_at": "2024-01-01T00:00:00Z",
	"updated_at": "2024-01-01T00:00:00Z"
}
```

**Implementation Details**:

- Password is automatically hashed using Django's `set_password()` method
- Default role is `USER (4)`
- Email verification is initially `false`
- Custom ID generated using 12-digit random string
- No username required (email-based authentication)

### 2. User Login (Token Obtain)

**Endpoint**: `POST /api/auth/token/`

**Request Body**:

```json
{
	"email": "user@example.com",
	"password": "securepassword123"
}
```

**Response** (200 OK):

```json
{
	"access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Token Details**:

- **Access Token**: Valid for 1 day (24 hours)
- **Refresh Token**: Valid for 7 days
- Tokens are signed with `SECRET_KEY` from settings

### 3. Token Refresh

**Endpoint**: `POST /api/auth/token/refresh/`

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

**Use Case**: When access token expires, use refresh token to get a new access token without re-login.

### 4. Using Authenticated Endpoints

**Authorization Header**:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Example Request**:

```bash
curl -H "Authorization: Bearer <access_token>" \
     http://localhost:8000/api/auth/users/me/
```

## User Model

### Custom User Model

Located in: `users/models.py`

```python
class User(AbstractUser):
    id = models.CharField(max_length=40, default=get_random_id, primary_key=True)
    username = None  # Removed username field
    email = models.EmailField(unique=True, db_index=True)
    role = models.IntegerField(choices=RoleChoices.choices, default=RoleChoices.USER)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  # Use email for authentication
    REQUIRED_FIELDS = []
```

### User Roles

```python
class RoleChoices(models.IntegerChoices):
    ADMIN = 1, 'Admin'
    TUTOR = 2, 'Tutor'
    STUDENT = 3, 'Student'
    USER = 4, 'User'
```

**Role Descriptions**:

- **ADMIN (1)**: Full system access, can manage all resources
- **TUTOR (2)**: Can create and manage courses, view analytics
- **STUDENT (3)**: Can enroll in courses, access content
- **USER (4)**: Default role, basic access

### Custom User Manager

```python
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
```

## Email Verification System

### Email Verification Token Generation

Located in: `users/api/email_tools.py`

```python
def get_verification_token(email):
    """Generate a verification token for the given email."""
    return signing.dumps(email, salt=settings.SECRET_KEY)

def verify_token(token, max_age: int = 3600):
    """Verify the token and return the email if valid."""
    try:
        email = signing.loads(token, max_age=max_age, salt=settings.SECRET_KEY)
        return email
    except signing.BadSignature:
        return None
```

**Token Details**:

- Uses Django's cryptographic signing
- Default expiration: 1 hour (3600 seconds)
- Salt: Django SECRET_KEY
- Tamper-proof and time-limited

### Sending Verification Email

```python
def send_verification_email(self):
    """Sends a verification email to the user."""
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
        from_email=None,
        recipient_list=[self.email],
        fail_silently=False,
    )
```

### Verifying Email

```python
def verify_verification_token(self, token):
    """Verifies the provided token and returns the email if valid."""
    email = verify_token(token)
    if email == self.email:
        self.is_email_verified = True
        self.save()
        return True
    return False
```

## JWT Configuration

Located in: `eleven_tutors/settings.py`

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated' if not DEBUG
        else 'rest_framework.permissions.AllowAny',
    ],
}
```

**Key Settings**:

- **Access Token Lifetime**: 1 day
- **Refresh Token Lifetime**: 7 days
- **Auth Header Type**: Bearer
- **Default Permission**: IsAuthenticated (AllowAny in DEBUG mode)

## Permission Classes

### Built-in Permissions

1. **AllowAny**: No authentication required

   ```python
   permission_classes = [permissions.AllowAny]
   ```

2. **IsAuthenticated**: Requires valid JWT token
   ```python
   permission_classes = [permissions.IsAuthenticated]
   ```

### Custom Permission Logic

Example from `UserViewSet`:

```python
def get_permissions(self):
    if self.action == 'create':
        return [permissions.AllowAny()]  # Registration is public
    return [permissions.IsAuthenticated()]  # All other actions require auth
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint                   | Permission      | Description                 |
| ------ | -------------------------- | --------------- | --------------------------- |
| POST   | `/api/auth/token/`         | AllowAny        | Obtain JWT tokens (login)   |
| POST   | `/api/auth/token/refresh/` | AllowAny        | Refresh access token        |
| POST   | `/api/auth/users/`         | AllowAny        | Register new user           |
| GET    | `/api/auth/users/me/`      | IsAuthenticated | Get current user profile    |
| PATCH  | `/api/auth/users/me/`      | IsAuthenticated | Update current user profile |
| GET    | `/api/auth/users/`         | IsAuthenticated | List all users              |
| GET    | `/api/auth/users/{id}/`    | IsAuthenticated | Get specific user           |
| PATCH  | `/api/auth/users/{id}/`    | IsAuthenticated | Update specific user        |
| DELETE | `/api/auth/users/{id}/`    | IsAuthenticated | Delete user                 |

### Tutor-Specific Endpoints

| Method | Endpoint                                | Permission      | Description         |
| ------ | --------------------------------------- | --------------- | ------------------- |
| POST   | `/api/auth/tutors/`                     | AllowAny        | Register as tutor   |
| GET    | `/api/auth/tutors/me/`                  | IsAuthenticated | Get tutor profile   |
| GET    | `/api/auth/tutors/me/courses/`          | IsAuthenticated | Get tutor's courses |
| GET    | `/api/auth/tutors/me/quick_statistics/` | IsAuthenticated | Get quick stats     |
| GET    | `/api/auth/tutors/me/analytics/`        | IsAuthenticated | Get analytics       |

## User Serializers

### UserSerializer

```python
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'password',
            'role', 'is_email_verified', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at',
                           'is_email_verified', 'role')

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user
```

### TutorSerializer

```python
class TutorSerializer(UserSerializer):
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.role = User.RoleChoices.TUTOR  # Automatically set role to TUTOR
        user.save()
        return user
```

## Security Best Practices

### 1. Password Security

- Passwords hashed using Django's PBKDF2 algorithm
- Minimum password validators configured
- Password never returned in API responses (write_only=True)

### 2. Token Security

- JWT tokens signed with SECRET_KEY
- Short-lived access tokens (1 day)
- Refresh tokens for extended sessions (7 days)
- Tokens transmitted via HTTPS in production

### 3. Email Verification

- Time-limited verification tokens (1 hour)
- Cryptographically signed tokens
- Cannot be tampered with or forged

### 4. CORS Protection

```python
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
```

### 5. Rate Limiting

- Ready for Django REST Framework throttling
- Can be configured per-endpoint

## Common Authentication Patterns

### 1. Frontend Login Flow

```javascript
// Login
const response = await fetch("http://localhost:8000/api/auth/token/", {
	method: "POST",
	headers: { "Content-Type": "application/json" },
	body: JSON.stringify({ email, password }),
});

const { access, refresh } = await response.json();

// Store tokens
localStorage.setItem("accessToken", access);
localStorage.setItem("refreshToken", refresh);

// Use access token for authenticated requests
const userResponse = await fetch("http://localhost:8000/api/auth/users/me/", {
	headers: { Authorization: `Bearer ${access}` },
});
```

### 2. Token Refresh Flow

```javascript
// Check if token is expired
const isTokenExpired = (token) => {
	const payload = JSON.parse(atob(token.split(".")[1]));
	return payload.exp * 1000 < Date.now();
};

// Refresh token if expired
if (isTokenExpired(accessToken)) {
	const response = await fetch(
		"http://localhost:8000/api/auth/token/refresh/",
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ refresh: refreshToken }),
		}
	);

	const { access } = await response.json();
	localStorage.setItem("accessToken", access);
}
```

### 3. Logout Flow

```javascript
// Simply remove tokens from storage
localStorage.removeItem("accessToken");
localStorage.removeItem("refreshToken");

// Optional: Blacklist token on backend (requires additional setup)
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**

   - Token expired: Use refresh token
   - Invalid token: Re-login
   - Missing Authorization header

2. **403 Forbidden**

   - User lacks required permissions
   - Check user role and endpoint permissions

3. **Email Verification Token Expired**

   - Request new verification email
   - Tokens expire after 1 hour

4. **CORS Errors**
   - Ensure frontend domain in CORS_ALLOWED_ORIGINS
   - Check CSRF_TRUSTED_ORIGINS for POST requests

## Testing Authentication

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Get profile
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Using Python Requests

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/token/', json={
    'email': 'test@example.com',
    'password': 'testpass123'
})
tokens = response.json()

# Authenticated request
headers = {'Authorization': f'Bearer {tokens["access"]}'}
user_response = requests.get('http://localhost:8000/api/auth/users/me/', headers=headers)
print(user_response.json())
```

## Future Enhancements

1. **OAuth Integration**: Google, Facebook, GitHub login
2. **Two-Factor Authentication**: SMS or TOTP-based 2FA
3. **Password Reset**: Email-based password reset flow
4. **Session Management**: Track active sessions
5. **Token Blacklisting**: Revoke tokens on logout
6. **Rate Limiting**: Prevent brute force attacks
7. **Account Lockout**: After multiple failed login attempts
8. **Audit Logging**: Track authentication events
