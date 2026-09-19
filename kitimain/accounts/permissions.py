"""
accounts/permissions.py  –  Reusable DRF permission classes.
"""
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.STUDENT)


class IsLecturer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.LECTURER)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.ADMIN)


class IsLecturerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in (User.LECTURER, User.ADMIN)
        )


class IsOwnerOrLecturer(BasePermission):
    """Allow object owner (student) or any lecturer/admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.role in (User.LECTURER, User.ADMIN):
            return True
        # obj may be the user directly, or have a .student field
        owner = getattr(obj, 'student', getattr(obj, 'user', obj))
        return owner == request.user
