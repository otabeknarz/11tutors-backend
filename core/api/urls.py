from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("universities", views.UniversityViewSet)

urlpatterns = router.urls
