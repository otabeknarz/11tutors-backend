from django.db import models
from eleven_tutors.base_model import BaseModel


class University(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    country = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)

    global_rank = models.IntegerField(null=True, blank=True)
    country_rank = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name if self.name else f"University ({self.id})"

    class Meta:
        verbose_name = "University"
        verbose_name_plural = "Universities"
