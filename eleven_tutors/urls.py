from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import static

from payments.api import views as payments_views

# Customize Django Admin Panel
admin.site.site_header = "11Tutors Admin Panel"
admin.site.site_title = "11Tutors Admin"
admin.site.index_title = "Welcome to 11Tutors Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.api.urls")),
    path("api/courses/", include("courses.api.urls")),
    path("api/core/", include("core.api.urls")),
    path("api/payments/stripe/webhook/", payments_views.stripe_webhook),
    path("webhook/", payments_views.stripe_webhook),
    path("api/payments/", include("payments.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
