from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models as app_models

"""
Create a user's profile when the user is created.
"""


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = app_models.Profile(user=instance)
        profile.save()
