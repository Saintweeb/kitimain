"""assignments/views.py"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Assignment, Submission, LecturerNote
from .serializers import (
    AssignmentSerializer, SubmissionSerializer,
    GradeSubmissionSerializer, LecturerNoteSerializer,
)
from accounts.permissions import IsLecturerOrAdmin, IsOwnerOrLecturer


# ── Assignments ───────────────────────────────────────────
class AssignmentListView(generics.ListCreateAPIView):
    queryset         = Assignment.objects.filter(is_active=True).select_related('created_by')
    serializer_class = AssignmentSerializer
    filterset_fields = ['subject']
    search_fields    = ['title', 'subject']
    ordering_fields  = ['due_date', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]


# ── Submissions ───────────────────────────────────────────
class SubmitAssignmentView(APIView):
    """Student submits or updates their work."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, pk=assignment_id, is_active=True)
        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            student=request.user,
        )
        submission.text_content = request.data.get('text_content', '')
        if 'file' in request.FILES:
            submission.submitted_file = request.FILES['file']
        submission.submitted    = True
        submission.submitted_at = timezone.now()
        submission.save()
        serializer = SubmissionSerializer(submission, context={'request': request})
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)


class MySubmissionsView(generics.ListAPIView):
    """Student: all my submissions."""
    serializer_class   = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Submission.objects
            .filter(student=self.request.user, submitted=True)
            .select_related('assignment')
        )


class AssignmentSubmissionsView(generics.ListAPIView):
    """Lecturer: all submissions for an assignment."""
    serializer_class   = SubmissionSerializer
    permission_classes = [IsLecturerOrAdmin]

    def get_queryset(self):
        assignment_id = self.kwargs['assignment_id']
        return (
            Submission.objects
            .filter(assignment_id=assignment_id, submitted=True)
            .select_related('student', 'assignment')
        )


class GradeSubmissionView(APIView):
    """Lecturer: record marks + feedback for a specific submission."""
    permission_classes = [IsLecturerOrAdmin]

    def patch(self, request, submission_id):
        submission = get_object_or_404(Submission, pk=submission_id)
        serializer = GradeSubmissionSerializer(submission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(graded_by=request.user, graded_at=timezone.now())
        return Response(SubmissionSerializer(submission, context={'request': request}).data)


# ── Lecturer Notes ────────────────────────────────────────
class LecturerNoteListView(generics.ListCreateAPIView):
    serializer_class = LecturerNoteSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if user.role in (User.LECTURER, User.ADMIN):
            qs = LecturerNote.objects.select_related('student', 'author')
            student_id = self.request.query_params.get('student')
            if student_id:
                qs = qs.filter(student_id=student_id)
            return qs
        # Students see only their own notes
        return LecturerNote.objects.filter(student=user).select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LecturerNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = LecturerNote.objects.all()
    serializer_class   = LecturerNoteSerializer
    permission_classes = [IsLecturerOrAdmin]
