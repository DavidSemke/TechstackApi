from rest_framework import serializers as serials

from . import models as app_models


class TagSerializer(serials.HyperlinkedModelSerializer):
    class Meta:
        model = app_models.Tag
        fields = "__all__"


class PostSerializer(serials.HyperlinkedModelSerializer):
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
    type = serials.SerializerMethodField()
    target = serials.SerializerMethodField()
    target_type = serials.SerializerMethodField()

    class Meta:
        model = app_models.Reaction
        fields = ["url", "owner", "type", "post", "comment", "target", "target_type"]

    def get_type(self, obj):
        return obj.get_type_display()

    def get_target(self, obj):
        if obj.post is not None:
            return self.fields["post"].to_representation(obj.post)

        if obj.comment is not None:
            return self.fields["comment"].to_representation(obj.comment)

    def get_target_type(self, obj):
        if obj.post is not None:
            return "post"

        if obj.comment is not None:
            return "comment"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop("post")
        rep.pop("comment")

        return rep
