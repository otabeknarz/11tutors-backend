from rest_framework import viewsets
from .serializers import UserSerializer
from users.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_email_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'id']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
