from rest_framework import permissions as perms


class ReadOnly(perms.BasePermission):
    def has_permission(self, request, view):
        return request.method in perms.SAFE_METHODS


class IsOwner(perms.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsModerator(perms.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="moderator").exists()


class IsGroupModerator(IsModerator):
    def has_object_permission(self, request, view, obj):
        only_groups = (
            request.data and len(request.data) < 2 and "groups" in request.data
        )

        if not only_groups:
            return False

        groups = obj.groups.values_list("name", flat=True)
        mod_group_name = "moderator"
        mod_in_request_data = mod_group_name in request.data["groups"]
        mod_in_groups = mod_group_name in groups
        mod_making_mod = mod_in_request_data and not mod_in_groups
        mod_removing_mod = not mod_in_request_data and mod_in_groups

        if mod_making_mod or mod_removing_mod:
            return False

        return super().has_object_permission(request, view, obj)
