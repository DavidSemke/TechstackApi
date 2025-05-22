from rest_framework import permissions as p


class IsOwnerOrReadOnly(p.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in p.SAFE_METHODS:
            return True

        return obj.owner == request.user


class IsNotCreating(p.BasePermission):
    def has_permission(self, request, view):
        if request.method in p.SAFE_METHODS:
            return True

        return request.method != "POST"


class IsNotDeleting(p.BasePermission):
    def has_permission(self, request, view):
        if request.method in p.SAFE_METHODS:
            return True

        return request.method != "DELETE"
