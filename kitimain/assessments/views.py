"""assessments/views.py"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import CAT, Question, CATAttempt, CATAnswer
from .serializers import (
    CATSerializer, CATDetailSerializer, CATStudentDetailSerializer,
    QuestionSerializer, SubmitCATSerializer, CATAttemptSerializer,
)
from accounts.permissions import IsLecturerOrAdmin


class CATListView(generics.ListCreateAPIView):
    serializer_class = CATSerializer
    filterset_fields = ['status', 'subject']
    search_fields    = ['title', 'subject']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        qs = CAT.objects.select_related('created_by')
        # Students only see non-draft CATs
        if user.role == User.STUDENT:
            qs = qs.exclude(status=CAT.STATUS_DRAFT)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CATDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Lecturer sees full detail with answers; student sees questions without answers."""

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsLecturerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return CAT.objects.prefetch_related('questions')

    def get_serializer_class(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if self.request.user.role in (User.LECTURER, User.ADMIN):
            return CATDetailSerializer
        return CATStudentDetailSerializer


class QuestionCreateView(generics.CreateAPIView):
    """Lecturer adds a question to a CAT."""
    serializer_class   = QuestionSerializer
    permission_classes = [IsLecturerOrAdmin]

    def perform_create(self, serializer):
        cat = get_object_or_404(CAT, pk=self.kwargs['cat_id'])
        serializer.save(cat=cat)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Question.objects.all()
    serializer_class   = QuestionSerializer
    permission_classes = [IsLecturerOrAdmin]


class StartCATView(APIView):
    """Student starts a CAT – creates (or returns existing) attempt."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, cat_id):
        cat = get_object_or_404(CAT, pk=cat_id)
        if cat.status != CAT.STATUS_OPEN:
            return Response(
                {'detail': 'This CAT is not currently open.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        attempt, created = CATAttempt.objects.get_or_create(
            cat=cat,
            student=request.user,
            defaults={'is_complete': False}
        )
        if attempt.is_complete:
            return Response(
                {'detail': 'You have already completed this CAT.',
                 'attempt': CATAttemptSerializer(attempt).data},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CATAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SubmitCATView(APIView):
    """Student submits answers and receives score."""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, cat_id):
        cat     = get_object_or_404(CAT, pk=cat_id)
        attempt = get_object_or_404(CATAttempt, cat=cat, student=request.user, is_complete=False)

        serializer = SubmitCATSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers_data = serializer.validated_data['answers']
        score = 0

        for ans_data in answers_data:
            question   = get_object_or_404(Question, pk=ans_data['question'].id, cat=cat)
            cat_answer, _ = CATAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={'chosen_ans': ans_data['chosen_ans']}
            )
            if cat_answer.is_correct:
                score += 1

        attempt.score       = score
        attempt.is_complete = True
        attempt.submitted_at = timezone.now()
        attempt.save()

        return Response({
            'score':      score,
            'total':      cat.question_count,
            'percentage': attempt.percentage,
            'time_taken': attempt.time_taken_seconds,
            'message':    _grade_message(attempt.percentage),
        })


def _grade_message(pct):
    if pct is None:
        return ''
    if pct >= 80:
        return 'Excellent! Outstanding performance.'
    if pct >= 65:
        return 'Good job! Keep it up.'
    if pct >= 50:
        return 'Pass. Review the topics you missed.'
    return 'Below pass mark. Please revise and speak to your lecturer.'


class MyCATAttemptsView(generics.ListAPIView):
    """Student: all my CAT attempts."""
    serializer_class   = CATAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CATAttempt.objects.filter(
            student=self.request.user
        ).select_related('cat').order_by('-started_at')


class CATAttemptsView(generics.ListAPIView):
    """Lecturer: all attempts for a specific CAT."""
    serializer_class   = CATAttemptSerializer
    permission_classes = [IsLecturerOrAdmin]

    def get_queryset(self):
        return CATAttempt.objects.filter(
            cat_id=self.kwargs['cat_id'],
            is_complete=True
        ).select_related('student', 'cat').order_by('-score')


class ToggleCATStatusView(APIView):
    """Lecturer: open or close a CAT."""
    permission_classes = [IsLecturerOrAdmin]

    def patch(self, request, cat_id):
        cat    = get_object_or_404(CAT, pk=cat_id)
        action = request.data.get('status')
        if action not in dict(CAT.STATUS_CHOICES):
            return Response({'detail': 'Invalid status.'}, status=400)
        cat.status = action
        cat.save()
        return Response(CATSerializer(cat).data)
