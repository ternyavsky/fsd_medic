from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffUser(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.has_perm

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or
                request.user.is_authenticated and
                request.user.has_perm)
