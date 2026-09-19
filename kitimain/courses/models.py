"""
courses/models.py  –  Modules, Online Classes, Announcements, Revision Papers.
"""
from django.db import models
from django.conf import settings


class Module(models.Model):
    """A learning module / course unit."""
    title       = models.CharField(max_length=200)
    description = models.TextField()
    icon        = models.CharField(max_length=10, default='📚')
    tags        = models.JSONField(default=list)          # ["Python","Pandas"]
    total_lessons = models.PositiveIntegerField(default=10)
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='modules_created'
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class ModuleProgress(models.Model):
    """Track a student's progress through a module."""
    student     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='module_progress')
    module      = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progress')
    lessons_done = models.PositiveIntegerField(default=0)
    completed   = models.BooleanField(default=False)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'module')

    @property
    def percentage(self):
        if self.module.total_lessons == 0:
            return 0
        return round(self.lessons_done / self.module.total_lessons * 100)


class OnlineClass(models.Model):
    STATUS_UPCOMING   = 'upcoming'
    STATUS_LIVE       = 'live'
    STATUS_COMPLETED  = 'completed'
    STATUS_CHOICES    = [
        (STATUS_UPCOMING,  'Upcoming'),
        (STATUS_LIVE,      'Live'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    name        = models.CharField(max_length=200)
    subject     = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    teacher     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='classes_taught'
    )
    schedule    = models.CharField(max_length=100)          # "Mon & Wed 09:00–11:00"
    meeting_link = models.URLField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Online Class'
        verbose_name_plural = 'Online Classes'

    def __str__(self):
        return f'{self.name} ({self.status})'


class Announcement(models.Model):
    TYPE_COURSE = 'course'
    TYPE_EXAM   = 'exam'
    TYPE_ADMIN  = 'admin'
    TYPE_CHOICES = [
        (TYPE_COURSE, 'Course Update'),
        (TYPE_EXAM,   'Exam Notice'),
        (TYPE_ADMIN,  'Administrative'),
    ]

    title       = models.CharField(max_length=300)
    body        = models.TextField()
    type        = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_COURSE)
    author      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='announcements'
    )
    is_pinned   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class RevisionPaper(models.Model):
    TYPE_KNEC    = 'knec'
    TYPE_NOTES   = 'notes'
    TYPE_PRACTICE = 'practice'
    TYPE_CHOICES = [
        (TYPE_KNEC,    'KNEC Paper'),
        (TYPE_NOTES,   'Study Notes'),
        (TYPE_PRACTICE,'Practice'),
    ]

    title       = models.CharField(max_length=300)
    subject     = models.CharField(max_length=100)
    year        = models.PositiveIntegerField()
    paper       = models.CharField(max_length=50, blank=True)  # "Paper 1"
    type        = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_KNEC)
    file        = models.FileField(upload_to='revision_papers/', null=True, blank=True)
    external_url = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='revision_papers'
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', 'title']

    def __str__(self):
        return self.title
