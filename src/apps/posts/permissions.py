from rest_framework import permissions as perms


class IsAuthor(perms.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="author").exists()


class IsCommenter(perms.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="commenter").exists()
