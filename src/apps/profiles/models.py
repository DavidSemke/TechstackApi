from django.conf import settings
from django.db import models

from ..core.validators import validate_image_url


class Profile(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    pic = models.URLField(blank=True, validators=[validate_image_url])
    bio = models.TextField(max_length=300, blank=True)
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="following", blank=True
    )
