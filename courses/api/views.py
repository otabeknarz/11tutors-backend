from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.conf import settings
import json
import requests

from courses.models import Category, Course, CoursePart, Lesson, Comment, Enrollment
from .serializers import CourseSerializer, LessonSerializer, CategorySerializer, CommentSerializer, \
    EnrollmentSerializer, CoursePartSerializer, CourseDetailSerializer, LessonDetailSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get"]


class CoursePartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = CoursePart.objects.all()
    serializer_class = CoursePartSerializer
    http_method_names = ["get"]


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    http_method_names = ["get"]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("part__order", "order")

    def get_serializer_class(self):
        if self.action == "list":
            return LessonSerializer
        return LessonDetailSerializer

    def retrieve(self, request, slug=None, *args, **kwargs):
        lesson = Lesson.objects.filter(slug=slug).first()

        self.permission_classes = (
            [permissions.AllowAny
             if lesson.is_free_preview
             else permissions.IsAuthenticated]
        )

        if not lesson:
            return Response(status=404)

        serializer = self.get_serializer(lesson)

        data = serializer.data

        payload_str = json.dumps({"ttl": 300})

        response = requests.post(
            url=f"https://dev.vdocipher.com/api/videos/{lesson.video_service_id}/otp",
            headers=settings.VDOCIPHER_HEADERS,
            data=payload_str
        )
        json_response = response.json()
        data.update(json_response)

        return Response(data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("-created_at")


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("-enrolled_at")


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = "slug"
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return CourseSerializer
        return CourseDetailSerializer
