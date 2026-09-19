"""
accounts/views.py
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer,
    RegisterSerializer, ChangePasswordSerializer,
)
from .models import StudentProfile
from .permissions import IsLecturer, IsAdmin

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """Blacklist the refresh token on logout."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    """Get or update the currently authenticated user."""
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Password changed successfully.'})


class RegisterView(generics.CreateAPIView):
    """Only lecturers/admins can register new users."""
    serializer_class   = RegisterSerializer
    permission_classes = [IsLecturer | IsAdmin]


class StudentListView(generics.ListAPIView):
    """Lecturers: list all students with profiles."""
    serializer_class   = UserSerializer
    permission_classes = [IsLecturer | IsAdmin]
    search_fields      = ['full_name', 'email', 'student_profile__reg_number']
    ordering_fields    = ['full_name', 'date_joined']
    filterset_fields   = ['student_profile__year', 'student_profile__course']

    def get_queryset(self):
        return (
            User.objects
            .filter(role=User.STUDENT, is_active=True)
            .select_related('student_profile')
            .prefetch_related('grade_set', 'attendancerecord_set')
        )


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = UserSerializer
    permission_classes = [IsLecturer | IsAdmin]

    def get_queryset(self):
        return User.objects.filter(role=User.STUDENT).select_related('student_profile')


class StudentStatsView(APIView):
    """Return aggregated stats for a single student (for lecturer view)."""
    permission_classes = [IsLecturer | IsAdmin]

    def get(self, request, pk):
        try:
            student = User.objects.get(pk=pk, role=User.STUDENT)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        from assignments.models import Submission
        from attendance.models import AttendanceRecord

        submissions  = Submission.objects.filter(student=student)
        att_records  = AttendanceRecord.objects.filter(student=student)
        present      = att_records.filter(status__in=['present', 'late']).count()
        att_rate     = round(present / att_records.count() * 100) if att_records.count() else 0

        grades = [s.marks_obtained for s in submissions if s.marks_obtained is not None]
        avg    = round(sum(grades) / len(grades)) if grades else 0

        return Response({
            'student_id':      student.id,
            'full_name':       student.full_name,
            'submissions':     submissions.count(),
            'avg_grade':       avg,
            'attendance_rate': att_rate,
            'total_classes':   att_records.count(),
        })
