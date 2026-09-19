"""attendance/models.py"""
from django.db import models
from django.conf import settings


class AttendanceRecord(models.Model):
    PRESENT = 'present'
    LATE    = 'late'
    ABSENT  = 'absent'
    STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (LATE,    'Late'),
        (ABSENT,  'Absent'),
    ]

    student    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendancerecord_set'
    )
    date       = models.DateField()
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT)
    online_class = models.ForeignKey(
        'courses.OnlineClass', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='attendance_records'
    )
    marked_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True,
        related_name='attendance_marked'
    )
    notes      = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.student.full_name} – {self.date} – {self.status}'
