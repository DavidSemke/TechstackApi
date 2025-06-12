from rest_framework import exceptions, viewsets
from rest_framework import permissions as perms

from ..core import permissions as core_perms
from .models import Profile
from .serializers import ProfileSerializer


# View/edit profiles
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.order_by("owner__username")
    serializer_class = ProfileSerializer
    # Anyone can view a profile.
    # Only a profile's owner can edit the profile.
    # Profile creation/deletion is disabled.
    permission_classes = [
        perms.IsAuthenticatedOrReadOnly,
        core_perms.IsOwner | core_perms.ReadOnly,
    ]

    def create(self, request, *args, **kwargs):
        raise exceptions.PermissionDenied()

    def destroy(self, request, *args, **kwargs):
        raise exceptions.PermissionDenied()
