from rest_framework import permissions as perms


class ReadOnly(perms.BasePermission):
    def has_permission(self, request, view):
        return request.method in perms.SAFE_METHODS


class IsOwner(perms.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
