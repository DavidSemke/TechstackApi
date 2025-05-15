from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models.functions import Lower

from ..core.validators import validate_image_url


class Tag(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(title=Lower("title")), name="lowercase_title"
            )
        ]

    title = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            MinLengthValidator(2),
            # Titles can only contain alphanumeric characters and '-'
            RegexValidator(r"^[-\dA-Za-z]*$"),
        ],
    )


class Post(models.Model):
    title = models.CharField(max_length=100, validators=[MinLengthValidator(20)])
    thumbnail = models.URLField(blank=True, validators=[validate_image_url])
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts_created",
    )
    publish_date = models.DateField(null=True, blank=True)
    last_modified_date = models.DateField(auto_now=True)
    content = models.CharField(
        max_length=3000, blank=True, validators=[MinLengthValidator(500)]
    )
    tags = models.ManyToManyField(Tag, related_name="posts")

    def clean(self):
        super().clean()

        tag_count = self.tags.count()
        max_tag_count = 5

        if self.publish_date:
            if not self.thumbnail or not self.content or not self.tags:
                raise ValidationError(
                    "A published post must have a thumbnail, content, and tags."
                )

            min_tag_count = 1

            if tag_count < min_tag_count:
                raise ValidationError(
                    f"A published post must have at least {min_tag_count} tag(s)."
                )

        if tag_count > max_tag_count:
            raise ValidationError(
                f"A post must not have more than {max_tag_count} tag(s)."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="comments_created",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    create_date = models.DateField(auto_now_add=True)
    content = models.CharField(max_length=300, validators=[MinLengthValidator(1)])
    reply_to = models.ForeignKey(
        "self", null=True, on_delete=models.CASCADE, related_name="replies"
    )


class Reaction(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(post__isnull=True) | models.Q(comment__isnull=True)
                ),
                name="at_most_one_reaction_target",
            )
        ]

    class ReactionType(models.TextChoices):
        LIKE = "L", "Like"
        DISLIKE = "D", "Dislike"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reactions_created",
    )
    type = models.CharField(max_length=1, choices=ReactionType)

    # Either a post or a comment is the reaction target
    # Constraint prevents both from being non-null simultaneously
    post = models.ForeignKey(
        Post, null=True, on_delete=models.CASCADE, related_name="reactions"
    )
    comment = models.ForeignKey(
        Comment, null=True, on_delete=models.CASCADE, related_name="reactions"
    )
