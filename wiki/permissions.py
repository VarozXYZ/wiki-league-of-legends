from rest_framework.permissions import BasePermission


def HasRole(*required_roles):
    class RolePermission(BasePermission):
        def has_permission(self, request, view):
            if not request.auth:
                return False
            roles = request.auth.get('roles', [])
            return any(role in roles for role in required_roles)

    return RolePermission
