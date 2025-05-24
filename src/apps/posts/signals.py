from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.forms import ValidationError

from . import models as app_models

"""
Enforce limits on the number of tags a post has.
The instance parameter is always of the Post model because the reverse
M2M relationship from the Tag model is disabled.
"""


@receiver(m2m_changed, sender=app_models.Post.tags.through)
def clean_post_on_tags_change(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        current_tag_count = instance.tags.count()
        new_tag_count = current_tag_count + len(pk_set)
        max_tag_count = 5

        if new_tag_count > max_tag_count:
            raise ValidationError(f"A post must have at most {max_tag_count} tag(s).")

    elif action == "pre_remove":
        # Min limit is not enforced when post is not published
        if instance.publish_date is None:
            return

        current_tag_count = instance.tags.count()
        new_tag_count = current_tag_count - len(pk_set)
        min_tag_count = 1

        if new_tag_count < min_tag_count:
            raise ValidationError(
                f"A published post must have at least {min_tag_count} tag(s)."
            )
