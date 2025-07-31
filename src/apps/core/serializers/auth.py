from django.contrib.auth.models import Group, User
from djoser.serializers import UserSerializer
from rest_framework import serializers as serials

from .mixins import DynamicFieldsMixin


class UserSerializer(DynamicFieldsMixin, UserSerializer):
    groups = serials.SlugRelatedField(
        many=True, queryset=Group.objects.all(), slug_field="name"
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "groups"]


class GroupSerializer(serials.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]
