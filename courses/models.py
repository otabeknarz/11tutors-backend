from django.db import models
import uuid
from slugify import slugify

from eleven_tutors.base_model import BaseModel
from users.models import User


class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Course(BaseModel):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    thumbnail = models.ImageField(upload_to="images/course_thumbnails/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tutors = models.ManyToManyField(User, related_name="courses")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Course, self).save(*args, **kwargs)


class CoursePart(BaseModel):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="parts")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.course.title + "--" + self.title)
        super(CoursePart, self).save(*args, **kwargs)


class Lesson(BaseModel):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    part = models.ForeignKey(
        CoursePart, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    video_service_id = models.CharField(max_length=255, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    duration = models.DurationField(null=True, blank=True)
    is_free_preview = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.part.course.title} - {self.part.title} - {self.title}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id.__str__()[10] + "--" + self.title)
        super(Lesson, self).save(*args, **kwargs)


class Comment(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    text = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="comments")
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, related_name="comments")

    def __str__(self):
        return f"{self.user} - {self.lesson}"


class Enrollment(BaseModel):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
