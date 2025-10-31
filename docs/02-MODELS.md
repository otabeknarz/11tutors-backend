# Database Models Documentation

## Overview

The 11Tutors backend uses Django ORM with PostgreSQL in production and SQLite for development. All models inherit from a custom `BaseModel` that provides common fields and functionality.

## Base Model

### BaseModel (Abstract)

Located in: `eleven_tutors/base_model.py`

```python
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created_at']
```

**Features**:

- Automatic timestamp tracking (created_at, updated_at)
- Default ordering by creation date (newest first)
- Abstract base class (no database table)

**Utility Function**:

```python
def get_random_id(k=12):
    """Generate random numeric ID with k digits"""
    return "".join(random.choices(string.digits, k=k))
```

---

## Users App Models

### User Model

Located in: `users/models.py`

```python
class User(AbstractUser):
    id = models.CharField(max_length=40, default=get_random_id,
                         primary_key=True, unique=True)
    username = None  # Removed
    email = models.EmailField(unique=True, null=False, blank=False, db_index=True)
    role = models.IntegerField(choices=RoleChoices.choices, default=RoleChoices.USER)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
```

**Fields**:

- `id`: 12-digit random string (primary key)
- `email`: Unique, indexed, used for authentication
- `first_name`: Inherited from AbstractUser
- `last_name`: Inherited from AbstractUser
- `password`: Hashed, inherited from AbstractUser
- `role`: Integer choice (1=Admin, 2=Tutor, 3=Student, 4=User)
- `is_email_verified`: Boolean flag for email verification
- `is_staff`: Inherited from AbstractUser (admin access)
- `is_superuser`: Inherited from AbstractUser (full permissions)
- `is_active`: Inherited from AbstractUser (account status)
- `created_at`: Timestamp of account creation
- `updated_at`: Timestamp of last update

**Relationships**:

- `courses` (reverse): Many-to-many with Course (as tutor)
- `enrollments` (reverse): One-to-many with Enrollment (as student)
- `payments` (reverse): One-to-many with Payment
- `comments` (reverse): One-to-many with Comment
- `onboarding_answers` (reverse): One-to-many with OnboardingAnswer

**Methods**:

```python
def send_verification_email(self):
    """Sends email verification link to user"""

def verify_verification_token(self, token):
    """Verifies email verification token"""

def __str__(self):
    return f"{self.get_full_name()} - {self.email}"
```

**Role Choices**:

```python
class RoleChoices(models.IntegerChoices):
    ADMIN = 1, 'Admin'
    TUTOR = 2, 'Tutor'
    STUDENT = 3, 'Student'
    USER = 4, 'User'
```

### OnboardingAnswer Model

```python
class OnboardingAnswer(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                            related_name='onboarding_answers')
    university = models.ForeignKey(University, on_delete=models.SET_NULL,
                                  null=True, related_name='onboarding_answers')
    degree = models.CharField(max_length=100, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    interests = models.TextField(null=True, blank=True)
```

**Purpose**: Stores user onboarding information for personalization

**Fields**:

- `user`: Foreign key to User (SET_NULL on delete)
- `university`: Foreign key to University (SET_NULL on delete)
- `degree`: User's degree program
- `graduation_year`: Expected graduation year
- `interests`: Text field for user interests
- `created_at`: Inherited from BaseModel
- `updated_at`: Inherited from BaseModel

---

## Courses App Models

### Category Model

Located in: `courses/models.py`

```python
class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
```

**Fields**:

- `name`: Category name
- `slug`: URL-friendly identifier (auto-generated)
- `description`: Optional category description

**Auto-slug Generation**:

```python
def save(self, *args, **kwargs):
    self.slug = slugify(self.name)
    super(Category, self).save(*args, **kwargs)
```

**Relationships**:

- `courses` (reverse): One-to-many with Course

### Course Model

```python
class Course(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                         editable=False, unique=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    thumbnail = models.ImageField(upload_to="images/course_thumbnails/",
                                 null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tutors = models.ManyToManyField(User, related_name="courses")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_published = models.BooleanField(default=False)
```

**Fields**:

- `id`: UUID primary key
- `title`: Course title
- `slug`: URL-friendly identifier (auto-generated from title)
- `thumbnail`: Image file (stored in cloud storage)
- `description`: Course description (supports markdown/HTML)
- `tutors`: Many-to-many relationship with User (multiple tutors per course)
- `category`: Foreign key to Category (SET_NULL on delete)
- `price`: Decimal field (USD, 2 decimal places)
- `is_published`: Boolean flag (draft vs published)
- `created_at`: Inherited from BaseModel
- `updated_at`: Inherited from BaseModel

**Relationships**:

- `parts` (reverse): One-to-many with CoursePart
- `enrollments` (reverse): One-to-many with Enrollment
- `orders` (reverse): Many-to-many with Order

**Auto-slug Generation**:

```python
def save(self, *args, **kwargs):
    self.slug = slugify(self.title)
    super(Course, self).save(*args, **kwargs)
```

### CoursePart Model

```python
class CoursePart(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                         editable=False, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                              related_name="parts")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
```

**Purpose**: Represents sections/modules within a course

**Fields**:

- `id`: UUID primary key
- `course`: Foreign key to Course (CASCADE on delete)
- `title`: Part/section title
- `slug`: Auto-generated from course title + part title
- `description`: Optional description
- `order`: Integer for ordering parts (0, 1, 2, ...)

**Relationships**:

- `lessons` (reverse): One-to-many with Lesson

**Auto-slug Generation**:

```python
def save(self, *args, **kwargs):
    self.slug = slugify(self.course.title + "--" + self.title)
    super(CoursePart, self).save(*args, **kwargs)
```

### Lesson Model

```python
class Lesson(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                         editable=False, unique=True)
    part = models.ForeignKey(CoursePart, on_delete=models.CASCADE,
                            related_name="lessons")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    video_service_id = models.CharField(max_length=255, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    duration = models.DurationField(null=True, blank=True)
    is_free_preview = models.BooleanField(default=False)
```

**Purpose**: Individual video lessons within a course part

**Fields**:

- `id`: UUID primary key
- `part`: Foreign key to CoursePart (CASCADE on delete)
- `title`: Lesson title
- `slug`: Auto-generated unique identifier
- `description`: Lesson description/notes
- `video_service_id`: VdoCipher video ID
- `order`: Integer for ordering lessons within part
- `duration`: Video duration (timedelta)
- `is_free_preview`: Boolean flag (allows non-enrolled users to view)

**Relationships**:

- `comments` (reverse): One-to-many with Comment

**Auto-slug Generation**:

```python
def save(self, *args, **kwargs):
    self.slug = slugify(self.id.__str__()[10] + "--" + self.title)
    super(Lesson, self).save(*args, **kwargs)
```

### Comment Model

```python
class Comment(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                         unique=True, primary_key=True)
    text = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                            null=True, related_name="comments")
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL,
                              null=True, related_name="comments")
```

**Purpose**: User comments on lessons

**Fields**:

- `id`: UUID primary key
- `text`: Comment content
- `user`: Foreign key to User (SET_NULL on delete)
- `lesson`: Foreign key to Lesson (SET_NULL on delete)
- `created_at`: Inherited from BaseModel
- `updated_at`: Inherited from BaseModel

### Enrollment Model

```python
class Enrollment(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                         editable=False, unique=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                              related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
```

**Purpose**: Tracks student enrollment in courses

**Fields**:

- `id`: UUID primary key
- `student`: Foreign key to User (CASCADE on delete)
- `course`: Foreign key to Course (CASCADE on delete)
- `enrolled_at`: Timestamp of enrollment

**Constraints**:

- Unique constraint on (student, course) - prevents duplicate enrollments

---

## Payments App Models

### Order Model

Located in: `payments/models.py`

```python
class Order(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, blank=True, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
```

**Purpose**: Represents a purchase order

**Fields**:

- `id`: UUID primary key
- `user`: Foreign key to User (CASCADE on delete)
- `courses`: Many-to-many with Course (supports bundles)
- `total_amount`: Total order amount (USD)
- `created_at`: Inherited from BaseModel
- `updated_at`: Inherited from BaseModel

**Relationships**:

- `payments` (reverse): One-to-many with Payment

### Payment Model

```python
class Payment(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                            null=True, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default=CurrencyChoices.USD,
                               choices=CurrencyChoices.choices)
    method = models.CharField(max_length=10, choices=PaymentMethodChoices.choices)
    status = models.IntegerField(choices=StatusChoices.choices,
                                default=StatusChoices.PENDING)
    reason = models.IntegerField(choices=ReasonChoices.choices,
                                null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True,
                                     null=True, blank=True)
    stripe_payment_intent = models.CharField(max_length=100,
                                            null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL,
                             null=True, related_name="payments")
    description = models.TextField(blank=True)
    cancel_time = models.DateTimeField(null=True, blank=True)
```

**Fields**:

- `id`: UUID primary key
- `user`: Foreign key to User (SET_NULL on delete)
- `amount`: Payment amount
- `currency`: Currency code (USD, UZS, EUR, RUB)
- `method`: Payment method (CARD, STRIPE, BANK, CASH)
- `status`: Payment status (1=Pending, 2=Completed, -1=Failed, -2=Refunded)
- `reason`: Failure/refund reason code
- `transaction_id`: External transaction ID (unique)
- `stripe_payment_intent`: Stripe payment intent ID
- `order`: Foreign key to Order (SET_NULL on delete)
- `description`: Optional payment description
- `cancel_time`: Timestamp of cancellation/completion
- `created_at`: Inherited from BaseModel
- `updated_at`: Inherited from BaseModel

**Payment Method Choices**:

```python
class PaymentMethodChoices(models.TextChoices):
    CARD = ("CARD", "Credit/Debit Card")
    STRIPE = ("STRIPE", "Stripe")
    BANK = ("BANK", "Bank Transfer")
    CASH = ("CASH", "Cash")
```

**Status Choices**:

```python
class StatusChoices(models.IntegerChoices):
    PENDING = (1, "Pending")
    COMPLETED = (2, "Completed")
    FAILED = (-1, "Failed")
    REFUNDED = (-2, "Refunded")
```

**Reason Choices**:

```python
class ReasonChoices(models.IntegerChoices):
    RECIPIENT_NOT_FOUND = 1, "Recipient not found or inactive"
    DEBIT_ERROR = 2, "Debit operation error"
    TRANSACTION_ERROR = 3, "Transaction error"
    TIMEOUT_CANCELLED = 4, "Transaction cancelled (timeout)"
    REFUND = 5, "Refund"
    UNKNOWN_ERROR = 10, "Unknown error"
```

**Currency Choices**:

```python
class CurrencyChoices(models.TextChoices):
    UZS = "UZS"
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
```

**Methods**:

```python
def mark_completed(self, reason=None):
    """Mark payment as completed"""
    self.status = self.StatusChoices.COMPLETED
    self.cancel_time = timezone.now()
    if reason:
        self.reason = reason
    self.save()

def mark_failed(self):
    """Mark payment as failed"""
    self.status = self.StatusChoices.FAILED
    self.save()
```

---

## Core App Models

### University Model

Located in: `core/models.py`

```python
class University(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    global_rank = models.IntegerField(null=True, blank=True)
    country_rank = models.IntegerField(null=True, blank=True)
```

**Purpose**: Stores university information for user onboarding

**Fields**:

- `name`: University name
- `description`: University description
- `logo`: University logo image
- `website`: Official website URL
- `country`: Country name
- `city`: City name
- `location`: Full address/location
- `global_rank`: Global ranking position
- `country_rank`: Country-specific ranking
- `created_at`: Inherited from BaseModel
- `updated_at`: Inherited from BaseModel

**Relationships**:

- `onboarding_answers` (reverse): One-to-many with OnboardingAnswer

---

## Database Relationships Diagram

```
User
├── courses (M2M) ──────────────> Course
├── enrollments (1-M) ──────────> Enrollment ──> Course
├── payments (1-M) ─────────────> Payment ──> Order ──> Course (M2M)
├── comments (1-M) ─────────────> Comment ──> Lesson
└── onboarding_answers (1-M) ──> OnboardingAnswer ──> University

Course
├── tutors (M2M) ───────────────> User
├── category (M-1) ─────────────> Category
├── parts (1-M) ────────────────> CoursePart
├── enrollments (1-M) ──────────> Enrollment
└── orders (M2M) ───────────────> Order

CoursePart
├── course (M-1) ───────────────> Course
└── lessons (1-M) ──────────────> Lesson

Lesson
├── part (M-1) ─────────────────> CoursePart
└── comments (1-M) ─────────────> Comment

Order
├── user (M-1) ─────────────────> User
├── courses (M2M) ──────────────> Course
└── payments (1-M) ─────────────> Payment
```

---

## Database Indexes

### Indexed Fields

1. **User.email**: Unique index for fast authentication lookups
2. **Course.slug**: Unique index for URL-based queries
3. **Category.slug**: Unique index for category filtering
4. **CoursePart.slug**: Unique index for navigation
5. **Lesson.slug**: Unique index for lesson access
6. **Payment.transaction_id**: Unique index for payment tracking

### Composite Indexes

1. **Enrollment (student, course)**: Unique constraint prevents duplicate enrollments

---

## Model Managers

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

### Default Manager

All models inherit `objects = models.Manager()` from BaseModel or Django defaults.

---

## Model Validation

### Built-in Validations

1. **Email**: Django's EmailField validation
2. **URL**: Django's URLField validation
3. **Decimal**: Max digits and decimal places
4. **Unique**: Enforced at database level
5. **Foreign Key**: Referential integrity

### Custom Validations

Can be added via `clean()` method or custom validators:

```python
def clean(self):
    # Custom validation logic
    if self.price < 0:
        raise ValidationError("Price cannot be negative")
```

---

## Migration Strategy

### Creating Migrations

```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migration for specific app
python manage.py makemigrations users

# Show SQL for migration
python manage.py sqlmigrate users 0001
```

### Applying Migrations

```bash
# Apply all migrations
python manage.py migrate

# Apply specific app migrations
python manage.py migrate users

# Rollback to specific migration
python manage.py migrate users 0001
```

---

## Query Optimization Tips

### 1. Use select_related for Foreign Keys

```python
# Bad - N+1 queries
lessons = Lesson.objects.all()
for lesson in lessons:
    print(lesson.part.course.title)  # Extra query each time

# Good - 1 query
lessons = Lesson.objects.select_related('part__course').all()
for lesson in lessons:
    print(lesson.part.course.title)  # No extra queries
```

### 2. Use prefetch_related for Many-to-Many

```python
# Bad - N+1 queries
courses = Course.objects.all()
for course in courses:
    print(course.tutors.all())  # Extra query each time

# Good - 2 queries
courses = Course.objects.prefetch_related('tutors').all()
for course in courses:
    print(course.tutors.all())  # No extra queries
```

### 3. Use only() to Limit Fields

```python
# Only fetch needed fields
users = User.objects.only('id', 'email', 'first_name')
```

### 4. Use defer() to Exclude Fields

```python
# Exclude large fields
courses = Course.objects.defer('description')
```

---

## Data Integrity

### Cascade Behaviors

- **CASCADE**: Delete related objects (Enrollment, CoursePart, Lesson)
- **SET_NULL**: Set to NULL (Category, Comment, Payment)
- **PROTECT**: Prevent deletion if related objects exist
- **SET_DEFAULT**: Set to default value

### Unique Constraints

- User email
- Course slug
- Category slug
- Payment transaction_id
- (Student, Course) in Enrollment

---

## Best Practices

1. **Always use transactions** for multi-model operations
2. **Index frequently queried fields**
3. **Use select_related/prefetch_related** to avoid N+1 queries
4. **Validate data** at model level, not just serializer level
5. **Use soft deletes** for important data (is_active flag)
6. **Keep models focused** - single responsibility
7. **Document complex relationships** in docstrings
8. **Use meaningful related_names** for reverse relationships
