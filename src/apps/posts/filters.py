import django_filters
from django.contrib.auth import get_user_model

from . import models as posts_models

User = get_user_model()


class TagFilter(django_filters.FilterSet):
    class Meta:
        model = posts_models.Tag
        fields = []

    title = django_filters.CharFilter(lookup_expr="icontains")


class PostFilter(django_filters.FilterSet):
    class Meta:
        model = posts_models.Post
        fields = {
            "publish_date": ["exact", "lt", "gt", "range"],
            "last_modified_date": ["exact", "lt", "gt", "range"],
        }

    title = django_filters.CharFilter(lookup_expr="icontains")
    owner = django_filters.CharFilter(
        field_name="owner__username", lookup_expr="icontains"
    )
    private = django_filters.BooleanFilter(
        field_name="publish_date", lookup_expr="isnull"
    )
    content = django_filters.CharFilter(lookup_expr="icontains")
    tag = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__title",
        to_field_name="title",
        queryset=posts_models.Tag.objects.all(),
    )


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = posts_models.Comment
        fields = {
            "post": ["exact"],
            "create_date": ["exact", "lt", "gt", "range"],
            "reply_to": ["exact"],
        }

    owner = django_filters.CharFilter(
        field_name="owner__username", lookup_expr="icontains"
    )
    content = django_filters.CharFilter(lookup_expr="icontains")


class ReactionFilter(django_filters.FilterSet):
    class Meta:
        model = posts_models.Reaction
        fields = {
            "create_date": ["exact", "lt", "gt", "range"],
            "type": ["exact"],
            "post": ["exact"],
            "comment": ["exact"],
        }

    owner = django_filters.CharFilter(
        field_name="owner__username", lookup_expr="icontains"
    )
