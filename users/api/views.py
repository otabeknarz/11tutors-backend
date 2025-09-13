from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from courses.api.serializers import Course, CourseSerializer
from .serializers import UserSerializer, TutorSerializer, OnboardingAnswerSerializer
from users.models import User, OnboardingAnswer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_email_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'id']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TutorViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role=User.RoleChoices.TUTOR)
    serializer_class = TutorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_email_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'id']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['get'], url_path='statistics')
    def get_statistics(self, request):
        user = request.user

    @action(detail=False, methods=['get', 'post'], url_path='courses')
    def get_courses(self, request):
        tutor = request.user

        if request.method == 'GET':
            courses = tutor.courses.all()
            page = self.paginate_queryset(courses)
            serializer = CourseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(tutor, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class OnboardingAnswerViewSet(viewsets.ModelViewSet):
    queryset = OnboardingAnswer.objects.all()
    serializer_class = OnboardingAnswerSerializer

    def get_queryset(self):
        return OnboardingAnswer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
