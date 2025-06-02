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

    def get_like_count(self, obj):
        return app_models.Reaction.objects.filter(
            type=app_models.Reaction.ReactionType.LIKE, post=obj
        ).count()

    def get_dislike_count(self, obj):
        return app_models.Reaction.objects.filter(
            type=app_models.Reaction.ReactionType.DISLIKE, post=obj
        ).count()


class CommentSerializer(serials.HyperlinkedModelSerializer):
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

    def get_like_count(self, obj):
        return app_models.Reaction.objects.filter(
            type=app_models.Reaction.ReactionType.LIKE, comment=obj
        ).count()

    def get_dislike_count(self, obj):
        return app_models.Reaction.objects.filter(
            type=app_models.Reaction.ReactionType.DISLIKE, comment=obj
        ).count()


class ReactionSerializer(serials.HyperlinkedModelSerializer):
    owner = serials.ReadOnlyField(source="owner.username")

    class Meta:
        model = app_models.Reaction
        fields = ["url", "owner", "type", "post", "comment"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Display 'Like' and 'Dislike' instead of 'L' and 'D'
        rep["type"] = instance.get_type_display()

        if rep["post"] is not None:
            target_value = rep["post"]
            target_type = "post"
        elif rep["comment"] is not None:
            target_value = rep["comment"]
            target_type = "comment"

        # Use 'target' field instead of 'post' or 'comment'
        rep["target"] = target_value
        rep["target_type"] = target_type
        rep.pop("post")
        rep.pop("comment")

        return rep
