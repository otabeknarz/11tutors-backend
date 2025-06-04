from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"courses", views.CourseViewSet, basename="course")
router.register(r"course-parts", views.CoursePartViewSet, basename="course-part")
router.register(r"lessons", views.LessonViewSet, basename="lesson")
router.register(r"comments", views.CommentViewSet, basename="comment")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")

urlpatterns = router.urls
