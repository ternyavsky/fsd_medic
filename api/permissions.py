from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.exceptions import APIException


class IsClinicAuthenticated(BasePermission):
    def has_permission(self, request, view):
        print(request.clinic, 8)
        return request.clinic


class IsDoctorAuthenticated(BasePermission):
    def has_permission(self, request, view):
        print(request.doctor, 13)
        return request.doctor


class IsUsermanAuthenticated(BasePermission):
    def has_permission(self, request, view):
        print(request.userman, request.clinic, request.doctor, 21)
        return request.userman


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.has_perm

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.has_perm
        )


class OnlyCreate(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return bool(request.user.is_staff)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
