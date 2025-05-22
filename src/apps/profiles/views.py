from rest_framework import permissions as perms
from rest_framework import viewsets

from ..core import permissions as my_perms
from .models import Profile
from .serializers import ProfileSerializer


# View/edit profiles
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # Anyone can view a profile.
    # Only a profile's owner can edit the profile.
    # Profile creation/deletion is disabled.
    permission_classes = [
        perms.IsAuthenticatedOrReadOnly,
        my_perms.IsOwner | my_perms.ReadOnly,
        my_perms.UpdateOnly | my_perms.ReadOnly,
    ]
