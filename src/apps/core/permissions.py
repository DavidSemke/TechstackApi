from rest_framework import permissions as p


class ReadOnly(p.BasePermission):
    def has_permission(self, request, view):
        return request.method in p.SAFE_METHODS


class CreateOnly(p.BasePermission):
    def has_permission(self, request, view):
        return request.method == "POST"


class UpdateOnly(p.BasePermission):
    def has_permission(self, request, view):
        return request.method in ("PUT", "PATCH")


class DeleteOnly(p.BasePermission):
    def has_permission(self, request, view):
        return request.method == "DELETE"


class IsOwner(p.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
