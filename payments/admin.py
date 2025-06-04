from django.contrib import admin
from .models import Payment, Order


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount", "currency", "method", "status")
    search_fields = (
        "user__username",
        "user__id",
        "user__name",
    )
    list_filter = ("status",)
    ordering = ("status",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount")
    search_fields = ("user__username",)
    list_filter = ()
    ordering = ("created_at",)
