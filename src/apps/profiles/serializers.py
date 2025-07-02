from rest_framework import serializers

from ..core.serializers import base as base_serials
from .models import Profile


class ProfileSerializer(base_serials.HyperlinkedReprnModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Profile
        fields = ["url", "owner", "pic", "bio", "followers"]
