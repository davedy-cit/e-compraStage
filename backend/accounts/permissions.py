from rest_framework import permissions


class IsMarketAdmin(permissions.BasePermission):
    """
    Allows access only to Market Administrators (is_staff=True).
    """
    message = "Market Administrator privileges required."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'is_staff_bool', False)
        )


class IsMarketAdminOrReadOnly(permissions.BasePermission):
    """
    Allows read access to all authenticated users, write access only to Market Admins.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'is_staff_bool', False)
        )