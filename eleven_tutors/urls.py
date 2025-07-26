from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import static

from payments.api import views as payments_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.api.urls")),
    path("api/courses/", include("courses.api.urls")),
    path("api/payments/", include("payments.api.urls")),
    path("webhook/", payments_views.stripe_webhook)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
