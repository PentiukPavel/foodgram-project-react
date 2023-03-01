from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """Доступ к редактированию только автору, остальным для чтоения."""

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
            )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ReadOnly(permissions.BasePermission):
    """Доступ только для чтения."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
