from django.conf import settings
from django.core import signing


def get_verification_token(email):
    """
    Generate a verification token for the given email.
    """
    return signing.dumps(email, salt=settings.SECRET_KEY)


def verify_token(token, max_age: int = 3600):
    """
    Verify the token and return the email if valid.
    Raises a BadSignature exception if the token is invalid or expired.
    """
    try:
        email = signing.loads(token, max_age=max_age, salt=settings.SECRET_KEY)
        return email
    except signing.BadSignature:
        return None
