from django.contrib.auth.models import Group
from djoser import views
from djoser.conf import settings
from rest_framework import permissions, viewsets

from . import permissions as core_perms
from .serializers.auth import GroupSerializer


# This viewset is needed to allow moderators to manage author and commenter groups
class UserViewSet(views.UserViewSet):
    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "activation":
            self.permission_classes = settings.PERMISSIONS.activation
        elif self.action == "resend_activation":
            self.permission_classes = settings.PERMISSIONS.password_reset
        elif self.action == "list":
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == "reset_password":
            self.permission_classes = settings.PERMISSIONS.password_reset
        elif self.action == "reset_password_confirm":
            self.permission_classes = settings.PERMISSIONS.password_reset_confirm
        elif self.action == "set_password":
            self.permission_classes = settings.PERMISSIONS.set_password
        elif self.action == "set_username":
            self.permission_classes = settings.PERMISSIONS.set_username
        elif self.action == "reset_username":
            self.permission_classes = settings.PERMISSIONS.username_reset
        elif self.action == "reset_username_confirm":
            self.permission_classes = settings.PERMISSIONS.username_reset_confirm
        elif self.action == "destroy" or (
            self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            self.permission_classes = settings.PERMISSIONS.user_delete
        elif self.action == "retrieve":
            self.permission_classes = [core_perms.IsModerator | permissions.IsAdminUser]
        elif self.action == "partial_update":
            self.permission_classes = [
                core_perms.IsGroupModerator | permissions.IsAdminUser
            ]

        return super(views.UserViewSet, self).get_permissions()


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]
