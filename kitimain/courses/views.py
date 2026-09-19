"""
courses/views.py
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Module, ModuleProgress, OnlineClass, Announcement, RevisionPaper
from .serializers import (
    ModuleSerializer, ModuleProgressSerializer, OnlineClassSerializer,
    AnnouncementSerializer, RevisionPaperSerializer,
)
from accounts.permissions import IsLecturer, IsAdmin, IsLecturerOrAdmin


# ── Modules ──────────────────────────────────────────────
class ModuleListView(generics.ListCreateAPIView):
    queryset         = Module.objects.filter(is_active=True)
    serializer_class = ModuleSerializer
    search_fields    = ['title', 'tags']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Module.objects.all()
    serializer_class = ModuleSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]


class ModuleProgressView(APIView):
    """Get or update the current student's progress for a module."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, module_id):
        module = get_object_or_404(Module, pk=module_id)
        prog, _ = ModuleProgress.objects.get_or_create(student=request.user, module=module)
        return Response(ModuleProgressSerializer(prog).data)

    def patch(self, request, module_id):
        module = get_object_or_404(Module, pk=module_id)
        prog, _ = ModuleProgress.objects.get_or_create(student=request.user, module=module)
        serializer = ModuleProgressSerializer(prog, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MyModuleProgressListView(generics.ListAPIView):
    """All module progress for the logged-in student."""
    serializer_class   = ModuleProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ModuleProgress.objects.filter(student=self.request.user).select_related('module')


# ── Online Classes ────────────────────────────────────────
class OnlineClassListView(generics.ListCreateAPIView):
    queryset         = OnlineClass.objects.select_related('teacher')
    serializer_class = OnlineClassSerializer
    filterset_fields = ['status', 'subject']
    search_fields    = ['name', 'subject']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class OnlineClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = OnlineClass.objects.all()
    serializer_class = OnlineClassSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]


# ── Announcements ─────────────────────────────────────────
class AnnouncementListView(generics.ListCreateAPIView):
    queryset         = Announcement.objects.select_related('author')
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsLecturerOrAdmin]


# ── Revision Papers ───────────────────────────────────────
class RevisionPaperListView(generics.ListCreateAPIView):
    queryset         = RevisionPaper.objects.all()
    serializer_class = RevisionPaperSerializer
    filterset_fields = ['type', 'subject', 'year']
    search_fields    = ['title', 'subject']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class RevisionPaperDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = RevisionPaper.objects.all()
    serializer_class = RevisionPaperSerializer
    permission_classes = [IsLecturerOrAdmin]
