from django.db import models
from rest_framework import permissions as perms
from rest_framework import viewsets

from ..core import permissions as core_perms
from . import filters as app_filters
from . import models as app_models
from . import permissions as app_perms
from . import serializers as app_serials


# View/edit tags
class TagViewSet(viewsets.ModelViewSet):
    queryset = app_models.Tag.objects.all().order_by("title")
    serializer_class = app_serials.TagSerializer
    filterset_class = app_filters.TagFilter

    # An author can create.
    # A moderator can update/delete.
    def get_permissions(self):
        self.permission_classes = [perms.IsAuthenticatedOrReadOnly]

        if self.action == "create":
            self.permission_classes += [app_perms.IsAuthor]
        elif self.action in ("update", "partial_update", "destroy"):
            self.permission_classes += [core_perms.IsModerator]

        return super().get_permissions()


# View/edit posts
class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        app_models.Post.objects.select_related("owner")
        .prefetch_related("tags")
        .prefetch_related("comments")
        .order_by("title", "-publish_date")
    )
    serializer_class = app_serials.PostSerializer
    filterset_class = app_filters.PostFilter

    # An author can create.
    # An author that owns the post can update/delete.
    # A moderator can update/delete.
    def get_permissions(self):
        self.permission_classes = [perms.IsAuthenticatedOrReadOnly]

        if self.action == "create":
            self.permission_classes += [app_perms.IsAuthor]
        elif self.action in ("update", "partial_update", "destroy"):
            self.permission_classes += [
                (app_perms.IsAuthor & core_perms.IsOwner) | core_perms.IsModerator
            ]

        return super().get_permissions()

    def get_queryset(self):
        filter = models.Q(publish_date__isnull=False)

        if self.request.user.is_authenticated:
            filter |= models.Q(owner=self.request.user)

        return (
            super()
            .get_queryset()
            .filter(filter)
            .annotate(
                like_count=models.Count(
                    "reactions",
                    filter=models.Q(
                        reactions__type=app_models.Reaction.ReactionType.LIKE
                    ),
                ),
                dislike_count=models.Count(
                    "reactions",
                    filter=models.Q(
                        reactions__type=app_models.Reaction.ReactionType.DISLIKE
                    ),
                ),
            )
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        return super().perform_create(serializer)


# View/edit comments
class CommentViewSet(viewsets.ModelViewSet):
    queryset = app_models.Comment.objects.select_related("owner").order_by(
        "post", "-create_date"
    )
    serializer_class = app_serials.CommentSerializer
    filterset_class = app_filters.CommentFilter

    # A commenter can create.
    # A commenter that owns the comment can update/delete.
    # A moderator can update/delete.
    def get_permissions(self):
        self.permission_classes = [perms.IsAuthenticatedOrReadOnly]

        if self.action == "create":
            self.permission_classes += [app_perms.IsCommenter]
        elif self.action in ("update", "partial_update", "destroy"):
            self.permission_classes += [
                (app_perms.IsCommenter & core_perms.IsOwner) | core_perms.IsModerator
            ]

        return super().get_permissions()

    def get_queryset(self):
        filter = models.Q(post__publish_date__isnull=False)

        if self.request.user.is_authenticated:
            filter |= models.Q(owner=self.request.user)
            filter |= models.Q(post__owner=self.request.user)

        return (
            super()
            .get_queryset()
            .filter(filter)
            .annotate(
                like_count=models.Count(
                    "reactions",
                    filter=models.Q(
                        reactions__type=app_models.Reaction.ReactionType.LIKE
                    ),
                ),
                dislike_count=models.Count(
                    "reactions",
                    filter=models.Q(
                        reactions__type=app_models.Reaction.ReactionType.DISLIKE
                    ),
                ),
            )
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        return super().perform_create(serializer)


# View/edit reactions
class ReactionViewSet(viewsets.ModelViewSet):
    queryset = app_models.Reaction.objects.all().order_by(
        "owner__username", "-create_date"
    )
    serializer_class = app_serials.ReactionSerializer
    filterset_class = app_filters.ReactionFilter

    def get_permissions(self):
        self.permission_classes = [perms.IsAuthenticatedOrReadOnly]

        if self.action in ("update", "partial_update", "destroy"):
            self.permission_classes += [core_perms.IsOwner]

        return super().get_permissions()

    def get_queryset(self):
        post_filter = models.Q(post__isnull=False)
        comment_filter = models.Q(comment__isnull=False)
        post_defined_query = models.Q(post__publish_date__isnull=False)
        comment_defined_query = models.Q(comment__post__publish_date__isnull=False)
        filter = models.Q()

        if self.request.user.is_authenticated:
            post_defined_query |= models.Q(post__owner=self.request.user)
            comment_defined_query |= models.Q(comment__post__owner=self.request.user)
            filter &= models.Q(owner=self.request.user)

        post_filter &= post_defined_query
        comment_filter &= comment_defined_query
        filter |= post_filter | comment_filter

        return super().get_queryset().filter(filter)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        return super().perform_create(serializer)
