import rest_framework
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_superuser or 
            request.method in SAFE_METHODS
        )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 1


class IsManagerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.user_type == 1 or
            request.method in SAFE_METHODS
        )


class IsManagerOrAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_staff or
            request.user.user_type == 1 or
            request.method in SAFE_METHODS
        )
