from django.db import models
import random
import string


def get_random_id(k=12):
    return "".join(random.choices(string.digits, k=k))


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created_at']
