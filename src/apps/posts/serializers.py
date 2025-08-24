from rest_framework import serializers as serials

from ..core.serializers import base as base_serials
from ..core.serializers import mixins as serial_mixins
from . import models as app_models


class TagSerializer(base_serials.HyperlinkedReprnModelSerializer):
    class Meta:
        model = app_models.Tag
        fields = ["url", "title"]


class PostSerializer(base_serials.HyperlinkedReprnModelSerializer):
    owner = serials.ReadOnlyField(source="owner.username")
    like_count = serials.IntegerField(read_only=True)
    dislike_count = serials.IntegerField(read_only=True)
    tags = serials.SlugRelatedField(
        many=True, slug_field="title", queryset=app_models.Tag.objects.all()
    )

    class Meta:
        model = app_models.Post
        fields = [
            "url",
            "owner",
            "title",
            "thumbnail",
            "publish_date",
            "last_modified_date",
            "content",
            "like_count",
            "dislike_count",
            "tags",
            "comments",
        ]
        read_only_fields = ["publish_date"]


class CommentSerializer(
    serial_mixins.ImmutableFieldsMixin, base_serials.HyperlinkedReprnModelSerializer
):
    owner = serials.ReadOnlyField(source="owner.username")
    like_count = serials.IntegerField(read_only=True)
    dislike_count = serials.IntegerField(read_only=True)

    class Meta:
        model = app_models.Comment
        fields = [
            "url",
            "owner",
            "post",
            "create_date",
            "content",
            "reply_to",
            "like_count",
            "dislike_count",
        ]
        immutable_fields = ["post", "reply_to"]


class ReactionSerializer(base_serials.HyperlinkedReprnModelSerializer):
    owner = serials.ReadOnlyField(source="owner.username")

    class Meta:
        model = app_models.Reaction
        fields = ["url", "owner", "type", "post", "comment"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["type"] = instance.get_type_display()
        return rep
