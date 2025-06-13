from django.db import models
from django.contrib.auth.models import AbstractUser

from core.models import University
from eleven_tutors.base_model import BaseModel, get_random_id
from django.core.mail import send_mail
from users.api.email_tools import get_verification_token, verify_token


class User(AbstractUser):
    class RoleChoices(models.IntegerChoices):
        ADMIN = 1, 'Admin'
        TUTOR = 2, 'Tutor'
        STUDENT = 3, 'Student'
        USER = 4, 'User'

    id = models.CharField(max_length=40, default=get_random_id, primary_key=True, unique=True)
    username = None
    email = models.EmailField(unique=True, null=False, blank=False, db_index=True)
    role = models.IntegerField(choices=RoleChoices.choices, default=RoleChoices.USER)
    is_email_verified = models.BooleanField(default=False, help_text="Indicates whether the user's email is verified.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.get_full_name()} - {self.email}"

    def send_verification_email(self):
        """
        Sends a verification email to the user.
        """
        token = get_verification_token(self.email)
        subject = "Email Verification for 11-tutors.com"
        message = f"""
        Hi {self.username},
        Please verify your email address by clicking the link below:
        http://localhost:8000/verify-email?token={token}
        """
        return send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[self.email],
            fail_silently=False,
        )

    def verify_verification_token(self, token):
        """
        Verifies the provided token and returns the email if valid.
        """
        email = verify_token(token)
        if email == self.email:
            self.is_email_verified = True
            self.save()
            return True
        return False


class OnboardingAnswer(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='onboarding_answers')
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, related_name='onboarding_answers')
