from rest_framework import permissions as p
from rest_framework import viewsets

from ..core import permissions as my_p
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
        p.IsAuthenticatedOrReadOnly,
        my_p.IsOwner | my_p.ReadOnly,
        my_p.UpdateOnly | my_p.ReadOnly,
    ]
