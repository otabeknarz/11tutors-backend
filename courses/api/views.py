from rest_framework import viewsets

from courses.models import Category, Course, CoursePart, Lesson, Comment, Enrollment
from .serializers import CourseSerializer, LessonSerializer, CategorySerializer, CommentSerializer, EnrollmentSerializer, CoursePartSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CoursePartViewSet(viewsets.ModelViewSet):
    queryset = CoursePart.objects.all()
    serializer_class = CoursePartSerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("part__order", "order")


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("-created_at")


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("-enrolled_at")


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("-created_at")
