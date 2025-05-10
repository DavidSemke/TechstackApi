from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from ..core.validators import validate_image_url


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    pic = models.URLField(blank=True, validators=[validate_image_url])
    bio = models.CharField(max_length=300, blank=True)
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="following"
    )


# Use signal to create profile when user created
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()


post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL)
