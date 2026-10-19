from rest_framework.permissions import BasePermission

from .models import UserRole


class PinIsCurrent(BasePermission):
    message = "You must change your PIN before continuing."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return not user.must_change_pin

class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role in (UserRole.MANAGER, UserRole.ADMIN)