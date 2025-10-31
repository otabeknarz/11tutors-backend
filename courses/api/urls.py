from rest_framework.routers import DefaultRouter
from django.urls import path

from . import views
from . import vdocipher_views

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"courses", views.CourseViewSet, basename="course")
router.register(r"course-parts", views.CoursePartViewSet, basename="course-part")
router.register(r"lessons", views.LessonViewSet, basename="lesson")
router.register(r"comments", views.CommentViewSet, basename="comment")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")

# VdoCipher endpoints
vdocipher_urls = [
    path('vdocipher/upload-credentials/', vdocipher_views.get_upload_credentials, name='vdocipher-upload-credentials'),
    path('vdocipher/video/<str:video_id>/otp/', vdocipher_views.get_video_otp, name='vdocipher-video-otp'),
]

urlpatterns = router.urls + vdocipher_urls
