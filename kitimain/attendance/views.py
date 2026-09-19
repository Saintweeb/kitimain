"""attendance/views.py"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer, BulkAttendanceSerializer
from accounts.permissions import IsLecturerOrAdmin

User = get_user_model()


class AttendanceListView(generics.ListAPIView):
    """Lecturer: full attendance log, filterable by date/student."""
    serializer_class   = AttendanceRecordSerializer
    permission_classes = [IsLecturerOrAdmin]
    filterset_fields   = ['date', 'status', 'student']
    ordering_fields    = ['date', 'student__full_name']

    def get_queryset(self):
        return AttendanceRecord.objects.select_related('student', 'marked_by').order_by('-date')


class MyAttendanceView(generics.ListAPIView):
    """Student: my own attendance records."""
    serializer_class   = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AttendanceRecord.objects.filter(
            student=self.request.user
        ).order_by('-date')


class BulkMarkAttendanceView(APIView):
    """Lecturer: mark attendance for an entire class in one request."""
    permission_classes = [IsLecturerOrAdmin]

    def post(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        date    = serializer.validated_data['date']
        records = serializer.validated_data['records']
        created_count = 0

        for rec in records:
            student_id = rec.get('student_id')
            att_status = rec.get('status', AttendanceRecord.PRESENT)
            notes      = rec.get('notes', '')

            try:
                student = User.objects.get(pk=student_id, role=User.STUDENT)
            except User.DoesNotExist:
                continue

            obj, created = AttendanceRecord.objects.update_or_create(
                student=student,
                date=date,
                defaults={
                    'status':    att_status,
                    'notes':     notes,
                    'marked_by': request.user,
                }
            )
            if created:
                created_count += 1

        return Response({
            'detail':  f'Attendance recorded for {len(records)} students on {date}.',
            'created': created_count,
            'updated': len(records) - created_count,
        }, status=status.HTTP_200_OK)


class AttendanceSummaryView(APIView):
    """Lecturer: summary stats per student (rate, present/absent/late counts)."""
    permission_classes = [IsLecturerOrAdmin]

    def get(self, request):
        students = User.objects.filter(role=User.STUDENT, is_active=True)
        data = []
        for student in students:
            records = AttendanceRecord.objects.filter(student=student)
            total   = records.count()
            present = records.filter(status=AttendanceRecord.PRESENT).count()
            late    = records.filter(status=AttendanceRecord.LATE).count()
            absent  = records.filter(status=AttendanceRecord.ABSENT).count()
            rate    = round((present + late) / total * 100) if total else 0
            data.append({
                'student_id':   student.id,
                'full_name':    student.full_name,
                'total':        total,
                'present':      present,
                'late':         late,
                'absent':       absent,
                'rate':         rate,
            })
        return Response(data)


class StudentAttendanceSummaryView(APIView):
    """Lecturer: summary for a single student."""
    permission_classes = [IsLecturerOrAdmin]

    def get(self, request, student_id):
        student = User.objects.get(pk=student_id)
        records = AttendanceRecord.objects.filter(student=student).order_by('-date')
        total   = records.count()
        present = records.filter(status=AttendanceRecord.PRESENT).count()
        late    = records.filter(status=AttendanceRecord.LATE).count()
        absent  = records.filter(status=AttendanceRecord.ABSENT).count()
        rate    = round((present + late) / total * 100) if total else 0
        return Response({
            'student_id': student.id,
            'full_name':  student.full_name,
            'total':      total,
            'present':    present,
            'late':       late,
            'absent':     absent,
            'rate':       rate,
            'records':    AttendanceRecordSerializer(records[:30], many=True).data,
        })
