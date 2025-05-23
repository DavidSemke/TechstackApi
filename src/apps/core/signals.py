from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_default_groups(sender, instance, created, **kwargs):
    if created:
        commenter_group, _ = Group.objects.get_or_create(name="commenter")
        instance.groups.add(commenter_group)
