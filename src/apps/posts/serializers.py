from rest_framework import serializers as serials

from . import models as app_models


class TagSerializer(serials.HyperlinkedModelSerializer):
    class Meta:
        model = app_models.Tag
        fields = "__all__"


class PostSerializer(serials.HyperlinkedModelSerializer):
    owner = serials.ReadOnlyField(source="owner.username")
    publish_date = serials.ReadOnlyField()
    tags = serials.StringRelatedField(many=True)

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
            "tags",
        ]


class CommentSerializer(serials.HyperlinkedModelSerializer):
    owner = serials.ReadOnlyField(source="owner.username")

    class Meta:
        model = app_models.Comment
        fields = ["url", "owner", "post", "create_date", "content", "reply_to"]


class ReactionSerializer(serials.HyperlinkedModelSerializer):
    owner = serials.ReadOnlyField(source="owner.username")

    class Meta:
        model = app_models.Reaction
        fields = ["url", "owner", "type", "post", "comment"]
