from rest_framework import serializers

from courses.models import Course, Lesson, Category, CoursePart, Comment, Enrollment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description")


class CoursePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePart
        fields = ("id", "title", "order", "course")


class LessonSerializer(serializers.ModelSerializer):
    part = CoursePartSerializer()

    class Meta:
        model = Lesson
        fields = ("id", "title", "part", "order", "duration", "created_at")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user", "lesson", "text", "created_at")


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("id", "student", "course", "enrolled_at")


class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    parts = CoursePartSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "thumbnail",
            "category",
            "parts",
            "created_at",
            "updated_at",
        )
