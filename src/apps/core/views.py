from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets

from .serializers.auth import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]
