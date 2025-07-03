from rest_framework import serializers as serials

from ..core.serializers import base as base_serials
from ..core.serializers import mixins as serial_mixins
from . import models as app_models


class TagSerializer(base_serials.HyperlinkedReprnModelSerializer):
    class Meta:
        model = app_models.Tag
        fields = "__all__"


class PostSerializer(base_serials.HyperlinkedReprnModelSerializer):
    owner = serials.ReadOnlyField(source="owner.username")
    publish_date = serials.ReadOnlyField()
    tags = serials.SlugRelatedField(
        many=True, slug_field="title", queryset=app_models.Tag.objects.all()
    )
    like_count = serials.SerializerMethodField()
    dislike_count = serials.SerializerMethodField()

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

    def get_like_count(self, obj):
        return app_models.Reaction.objects.filter(
            type=app_models.Reaction.ReactionType.LIKE, post=obj
        ).count()

    def get_dislike_count(self, obj):
        return app_models.Reaction.objects.filter(
            type=app_models.Reaction.ReactionType.DISLIKE, post=obj
        ).count()


class CommentSerializer(
    serial_mixins.ImmutableFieldsMixin, base_serials.HyperlinkedReprnModelSerializer
):
    owner = serials.ReadOnlyField(source="owner.username")
    like_count = serials.SerializerMethodField()
    dislike_count = serials.SerializerMethodField()

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

    def get_like_count(self, obj):
        return app_models.Reaction.objects.filter(
            type=app_models.Reaction.ReactionType.LIKE, comment=obj
        ).count()

    def get_dislike_count(self, obj):
        return app_models.Reaction.objects.filter(
            type=app_models.Reaction.ReactionType.DISLIKE, comment=obj
        ).count()


class ReactionSerializer(base_serials.HyperlinkedReprnModelSerializer):
    owner = serials.ReadOnlyField(source="owner.username")

    class Meta:
        model = app_models.Reaction
        fields = ["url", "owner", "type", "post", "comment"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["type"] = instance.get_type_display()
        return rep
