from django.db import models
from django.utils import timezone
import uuid

from eleven_tutors.base_model import BaseModel
from users.models import User
from courses.models import Course


class Order(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, blank=True, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order for @{self.user}"


class Payment(BaseModel):
    class PaymentMethodChoices(models.TextChoices):
        CARD = ("CARD", "Credit/Debit Card")
        STRIPE = ("STRIPE", "Stripe")
        BANK = ("BANK", "Bank Transfer")
        CASH = ("CASH", "Cash")

    class StatusChoices(models.IntegerChoices):
        PENDING = (1, "Pending")
        COMPLETED = (2, "Completed")
        FAILED = (-1, "Failed")
        REFUNDED = (-2, "Refunded")

    class ReasonChoices(models.IntegerChoices):
        RECIPIENT_NOT_FOUND = 1, "Recipient not found or inactive"
        DEBIT_ERROR = 2, "Debit operation error"
        TRANSACTION_ERROR = 3, "Transaction error"
        TIMEOUT_CANCELLED = 4, "Transaction cancelled (timeout)"
        REFUND = 5, "Refund"
        UNKNOWN_ERROR = 10, "Unknown error"

    class CurrencyChoices(models.TextChoices):
        UZS = "UZS"
        USD = "USD"
        EUR = "EUR"
        RUB = "RUB"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(
        max_length=10, default=CurrencyChoices.USD, choices=CurrencyChoices.choices
    )
    method = models.CharField(max_length=10, choices=PaymentMethodChoices.choices)
    status = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.PENDING)
    reason = models.IntegerField(choices=ReasonChoices.choices, null=True, blank=True)
    transaction_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    stripe_payment_intent = models.CharField(max_length=100, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name="payments")
    description = models.TextField(blank=True)

    cancel_time = models.DateTimeField(null=True, blank=True)

    def mark_completed(self, reason=None):
        self.status = self.StatusChoices.COMPLETED
        self.cancel_time = timezone.now()
        if reason:
            self.reason = reason

        self.save()

    def mark_failed(self):
        self.status = self.StatusChoices.FAILED
        self.save()

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} - ({self.status})"
