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
            MinLengthValidator(1),
            # Titles can only contain alphanumeric characters and '-'
            RegexValidator(
                r"^[-\dA-Za-z]*$",
                message="Tag title must only contain letters, numbers, and hyphens.",
            ),
        ],
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100, validators=[MinLengthValidator(20)])
    thumbnail = models.URLField(blank=True, validators=[validate_image_url])
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts_owned",
    )
    publish_date = models.DateField(null=True, blank=True)
    last_modified_date = models.DateField(auto_now=True)
    content = models.TextField(
        max_length=18500, blank=True, validators=[MinLengthValidator(1850)]
    )
    tags = models.ManyToManyField(Tag, related_name="+")

    def clean(self):
        super().clean()

        if self.publish_date:
            if not self.thumbnail:
                raise ValidationError("A published post must have a thumbnail.")

            if not self.content:
                raise ValidationError("A published post must have content.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Comment(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="comments_owned",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    create_date = models.DateField(auto_now_add=True)
    content = models.TextField(max_length=300, validators=[MinLengthValidator(1)])
    reply_to = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    def clean(self):
        super().clean()

        if not self.post.publish_date:
            raise ValidationError("A comment cannot be made on a private post.")

        if self.reply_to:
            if self.reply_to == self:
                raise ValidationError("A comment cannot be a reply to itself.")

            if self.reply_to.reply_to:
                raise ValidationError("A comment cannot be a reply to a reply.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Reaction(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    (models.Q(post__isnull=True) & models.Q(comment__isnull=False))
                    | (models.Q(post__isnull=False) & models.Q(comment__isnull=True))
                ),
                name="exactly_one_reaction_target",
            ),
            models.UniqueConstraint(
                fields=["owner", "post"],
                condition=models.Q(post__isnull=False),
                name="unique_owner_post",
            ),
            models.UniqueConstraint(
                fields=["owner", "comment"],
                condition=models.Q(comment__isnull=False),
                name="unique_owner_comment",
            ),
        ]

    class ReactionType(models.TextChoices):
        LIKE = "L", "Like"
        DISLIKE = "D", "Dislike"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reactions_owned",
    )
    create_date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=ReactionType)

    # Either a post or a comment is the reaction target
    # Constraint prevents both from being non-null or null simultaneously
    post = models.ForeignKey(
        Post, null=True, blank=True, on_delete=models.CASCADE, related_name="reactions"
    )
    comment = models.ForeignKey(
        Comment,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reactions",
    )

    def clean(self):
        super().clean()

        if self.post and not self.post.publish_date:
            raise ValidationError("A reaction cannot target a private post.")

        if self.comment and not self.comment.post.publish_date:
            raise ValidationError(
                "A reaction cannot target a comment of a private post."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
