from rest_framework import viewsets, permissions

from core.models import University
from .serializers import UniversitySerializer


class UniversityViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    http_method_names = ["get"]
