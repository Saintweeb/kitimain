"""reports/views.py"""
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from accounts.permissions import IsLecturerOrAdmin
from assignments.models import Submission
from attendance.models import AttendanceRecord
from assessments.models import CATAttempt
from assignments.models import LecturerNote

User = get_user_model()


class StudentProgressReportView(APIView):
    """
    GET /api/reports/student/<id>/
    Query param: ?format=pdf  → download PDF
                 ?format=json → return JSON data (default)

    Accessible by the student themselves OR any lecturer/admin.
    """
    permission_classes = [permissions.IsAuthenticated]

    def _check_access(self, request, student):
        if request.user == student:
            return True
        if request.user.role in (User.LECTURER, User.ADMIN):
            return True
        return False

    def get(self, request, student_id):
        try:
            student = User.objects.get(pk=student_id, role=User.STUDENT)
        except User.DoesNotExist:
            return Response({'detail': 'Student not found.'}, status=404)

        if not self._check_access(request, student):
            return Response({'detail': 'Permission denied.'}, status=403)

        # Gather data
        submissions       = list(Submission.objects.filter(student=student, submitted=True).select_related('assignment'))
        attendance_records = list(AttendanceRecord.objects.filter(student=student).order_by('-date'))
        cat_attempts      = list(CATAttempt.objects.filter(student=student).select_related('cat'))
        notes             = list(LecturerNote.objects.filter(student=student).select_related('author'))

        fmt = request.query_params.get('format', 'json')

        if fmt == 'pdf':
            return self._pdf_response(student, submissions, attendance_records, notes, cat_attempts)
        return self._json_response(student, submissions, attendance_records, notes, cat_attempts)

    def _pdf_response(self, student, grades, attendance, notes, cats):
        from .pdf_generator import generate_student_report
        buffer = generate_student_report(student, grades, attendance, notes, cats)

        if buffer is None:
            # ReportLab not installed – return helpful message
            return HttpResponse(
                "ReportLab is not installed. Run: pip install reportlab",
                status=501,
                content_type='text/plain'
            )

        filename = f"KITI_Report_{student.full_name.replace(' ', '_')}.pdf"
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _json_response(self, student, grades, attendance, notes, cats):
        profile  = getattr(student, 'student_profile', None)
        valid_g  = [g for g in grades if g.marks_obtained is not None]
        avg_pct  = 0
        if valid_g:
            avg_pct = round(sum(g.marks_obtained / g.assignment.max_marks * 100 for g in valid_g) / len(valid_g))

        att_total   = len(attendance)
        att_present = sum(1 for a in attendance if a.status in ('present', 'late'))
        att_rate    = round(att_present / att_total * 100) if att_total else 0

        def grade_letter(p):
            if p >= 80: return 'A'
            if p >= 65: return 'B'
            if p >= 50: return 'C'
            if p >= 40: return 'D'
            return 'F'

        return Response({
            'student': {
                'id':        student.id,
                'full_name': student.full_name,
                'email':     student.email,
                'reg_number': profile.reg_number if profile else '',
                'course':     profile.course     if profile else '',
                'year':       profile.year        if profile else '',
            },
            'summary': {
                'avg_percentage':  avg_pct,
                'grade_letter':    grade_letter(avg_pct),
                'attendance_rate': att_rate,
                'submissions':     len(valid_g),
                'cats_completed':  sum(1 for a in cats if a.is_complete),
            },
            'grades': [{
                'assignment': g.assignment.title,
                'subject':    g.assignment.subject,
                'score':      g.marks_obtained,
                'max_marks':  g.assignment.max_marks,
                'percentage': round(g.marks_obtained / g.assignment.max_marks * 100),
                'feedback':   g.feedback,
            } for g in valid_g],
            'attendance': [{
                'date':   a.date.isoformat(),
                'status': a.status,
            } for a in attendance[:30]],
            'cat_results': [{
                'title':      a.cat.title,
                'subject':    a.cat.subject,
                'score':      a.score,
                'total':      a.cat.question_count,
                'percentage': a.percentage,
            } for a in cats if a.is_complete],
            'notes': [{
                'type':    n.type,
                'content': n.content,
                'author':  n.author.full_name,
                'date':    n.created_at.date().isoformat(),
            } for n in notes],
        })


class ClassReportView(APIView):
    """
    GET /api/reports/class/
    Lecturer: overview of all students' performance.
    """
    permission_classes = [IsLecturerOrAdmin]

    def get(self, request):
        students = User.objects.filter(role=User.STUDENT, is_active=True).select_related('student_profile')
        data = []
        for student in students:
            subs  = Submission.objects.filter(student=student, submitted=True)
            valid = [s for s in subs if s.marks_obtained is not None]
            att   = AttendanceRecord.objects.filter(student=student)
            present = att.filter(status__in=['present', 'late']).count()
            att_rate = round(present / att.count() * 100) if att.count() else 0
            avg = round(sum(s.marks_obtained / s.assignment.max_marks * 100 for s in valid) / len(valid)) if valid else 0

            profile = getattr(student, 'student_profile', None)
            data.append({
                'id':          student.id,
                'full_name':   student.full_name,
                'reg_number':  profile.reg_number if profile else '',
                'year':        profile.year if profile else '',
                'avg_grade':   avg,
                'att_rate':    att_rate,
                'submissions': len(valid),
                'at_risk':     avg < 50 or att_rate < 75,
            })

        # Sort: at-risk first, then by name
        data.sort(key=lambda x: (not x['at_risk'], x['full_name']))
        return Response({'students': data, 'total': len(data)})
