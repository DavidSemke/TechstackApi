from rest_framework import permissions as perms
from rest_framework import viewsets

from ..core import permissions as core_perms
from . import models as app_models
from . import permissions as app_perms
from . import serializers as app_serials


# View/edit tags
class TagViewSet(viewsets.ModelViewSet):
    queryset = app_models.Tag.objects.all().order_by("title")
    serializer_class = app_serials.TagSerializer

    # An author can create.
    # A moderator can update/delete.
    permission_classes = [
        perms.IsAuthenticatedOrReadOnly,
        (
            (app_perms.IsAuthor & core_perms.CreateOnly)
            | (app_perms.IsModerator & (core_perms.UpdateOnly | core_perms.DeleteOnly))
            | core_perms.ReadOnly
        ),
    ]


# View/edit posts
class PostViewSet(viewsets.ModelViewSet):
    queryset = app_models.Post.objects.all().order_by("title", "-publish_date")
    serializer_class = app_serials.PostSerializer

    # An author can create.
    # An author that owns the post can update/delete.
    # A moderator can update/delete.
    permission_classes = [
        perms.IsAuthenticatedOrReadOnly,
        (
            (app_perms.IsAuthor & core_perms.IsOwner)
            | (app_perms.IsModerator & (core_perms.UpdateOnly | core_perms.DeleteOnly))
            | core_perms.ReadOnly
        ),
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        return super().perform_create(serializer)


# View/edit comments
class CommentViewSet(viewsets.ModelViewSet):
    queryset = app_models.Comment.objects.all().order_by("post", "-create_date")
    serializer_class = app_serials.CommentSerializer

    # A commenter can create.
    # A commenter that owns the comment can update/delete.
    # A moderator can update/delete.
    permission_classes = [
        perms.IsAuthenticatedOrReadOnly,
        (
            (app_perms.IsCommenter & core_perms.IsOwner)
            | (app_perms.IsModerator & (core_perms.UpdateOnly | core_perms.DeleteOnly))
            | core_perms.ReadOnly
        ),
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        return super().perform_create(serializer)


# View/edit reactions
class ReactionViewSet(viewsets.ModelViewSet):
    queryset = app_models.Reaction.objects.all().order_by(
        "owner__username", "-create_date"
    )
    serializer_class = app_serials.ReactionSerializer

    permission_classes = [
        perms.IsAuthenticatedOrReadOnly,
        core_perms.IsOwner | core_perms.ReadOnly,
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        return super().perform_create(serializer)
