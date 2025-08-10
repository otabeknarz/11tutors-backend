from rest_framework import serializers

from courses.models import Course, Lesson, Category, CoursePart, Comment, Enrollment
from users.api.serializers import UserSerializer
from users.models import User


class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class CoursePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePart
        fields = ("id", "title", "order")


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "slug", "order", "duration", "created_at", "is_free_preview")


class LessonDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "slug", "description", "is_free_preview", "order", "duration", "created_at")


class CoursePartDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = CoursePart
        fields = ("id", "title", "order", "lessons")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user", "lesson", "text", "created_at")


class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    parts = CoursePartSerializer(many=True, read_only=True)
    tutors = TutorSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField(read_only=True)

    def get_is_enrolled(self, course):
        user = self.context.get("request").user
        if not user or user.is_anonymous:
            return False
        return Enrollment.objects.filter(course=course, student=user).exists()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "price",
            "thumbnail",
            "tutors",
            "is_enrolled",
            "category",
            "parts",
            "created_at",
            "updated_at",
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    student = UserSerializer()

    class Meta:
        model = Enrollment
        fields = ("id", "student", "course", "enrolled_at")


class CourseDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    tutors = TutorSerializer(many=True, read_only=True)
    parts = CoursePartDetailSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField(read_only=True)

    def get_is_enrolled(self, course):
        user = self.context.get("request").user
        if not user or user.is_anonymous:
            return False
        return Enrollment.objects.filter(course=course, student=user).exists()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "price",
            "thumbnail",
            "tutors",
            "is_enrolled",
            "parts",
            "categories",
            "categories",
            "created_at",
            "updated_at",
        )
