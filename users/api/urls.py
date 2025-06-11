from rest_framework.routers import DefaultRouter
from django.urls import path
from .auth_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView
)
from . import views


router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

auth_urls = [
    path('token/', CustomTokenObtainPairView.as_view()),
    path('token/refresh/', CustomTokenRefreshView.as_view()),
]

urlpatterns = router.urls + auth_urls
