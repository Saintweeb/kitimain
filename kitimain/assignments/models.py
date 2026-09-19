"""
assignments/models.py
"""
from django.db import models
from django.conf import settings


class Assignment(models.Model):
    title       = models.CharField(max_length=300)
    subject     = models.CharField(max_length=100)
    description = models.TextField()
    max_marks   = models.PositiveIntegerField(default=100)
    due_date    = models.DateField()
    brief_file  = models.FileField(upload_to='assignment_briefs/', null=True, blank=True)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='assignments_created'
    )
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def submission_count(self):
        return self.submissions.filter(submitted=True).count()


class Submission(models.Model):
    assignment      = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grade_set')
    text_content    = models.TextField(blank=True)
    submitted_file  = models.FileField(upload_to='submissions/', null=True, blank=True)
    submitted       = models.BooleanField(default=False)
    submitted_at    = models.DateTimeField(null=True, blank=True)
    marks_obtained  = models.PositiveIntegerField(null=True, blank=True)
    feedback        = models.TextField(blank=True)
    graded_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='grades_given'
    )
    graded_at       = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student.full_name} → {self.assignment.title}'

    @property
    def percentage(self):
        if self.marks_obtained is None or self.assignment.max_marks == 0:
            return None
        return round(self.marks_obtained / self.assignment.max_marks * 100)


class LecturerNote(models.Model):
    """Notes / instructions / feedback a lecturer posts to a specific student."""
    NOTE    = 'note'
    FEEDBACK = 'feedback'
    COMMEND = 'commendation'
    WARNING = 'warning'
    INSTRUCT = 'instruction'
    TYPE_CHOICES = [
        (NOTE,     'General Note'),
        (FEEDBACK, 'Feedback'),
        (COMMEND,  'Commendation'),
        (WARNING,  'Warning'),
        (INSTRUCT, 'Instructions'),
    ]

    student  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_notes'
    )
    author   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_notes'
    )
    type     = models.CharField(max_length=20, choices=TYPE_CHOICES, default=NOTE)
    content  = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.type} for {self.student.full_name} by {self.author.full_name}'
