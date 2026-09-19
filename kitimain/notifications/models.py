"""notifications/models.py"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_ASSIGNMENT = 'assignment'
    TYPE_GRADE      = 'grade'
    TYPE_NOTE       = 'note'
    TYPE_CAT        = 'cat'
    TYPE_CLASS      = 'class'
    TYPE_GENERAL    = 'general'
    TYPE_CHOICES = [
        (TYPE_ASSIGNMENT, 'Assignment'),
        (TYPE_GRADE,      'Grade'),
        (TYPE_NOTE,       'Note'),
        (TYPE_CAT,        'CAT'),
        (TYPE_CLASS,      'Class'),
        (TYPE_GENERAL,    'General'),
    ]

    recipient  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    type       = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_GENERAL)
    title      = models.CharField(max_length=300)
    body       = models.TextField(blank=True)
    is_read    = models.BooleanField(default=False)
    link       = models.CharField(max_length=200, blank=True)  # frontend route
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient.full_name}: {self.title}'
