"""
uploads/models.py  –  Central file upload tracking.
"""
from django.db import models
from django.conf import settings
import os


def upload_path(instance, filename):
    """Dynamic upload path: uploads/<category>/<user_id>/<filename>"""
    return f"uploads/{instance.category}/{instance.uploaded_by_id}/{filename}"


class UploadedFile(models.Model):
    CATEGORY_ASSIGNMENT  = 'assignment'
    CATEGORY_SUBMISSION  = 'submission'
    CATEGORY_REVISION    = 'revision'
    CATEGORY_PROFILE     = 'profile'
    CATEGORY_NOTE        = 'note'
    CATEGORY_OTHER       = 'other'

    CATEGORY_CHOICES = [
        (CATEGORY_ASSIGNMENT, 'Assignment Brief'),
        (CATEGORY_SUBMISSION, 'Student Submission'),
        (CATEGORY_REVISION,   'Revision Paper'),
        (CATEGORY_PROFILE,    'Profile Photo'),
        (CATEGORY_NOTE,       'Note Attachment'),
        (CATEGORY_OTHER,      'Other'),
    ]

    file          = models.FileField(upload_to=upload_path)
    original_name = models.CharField(max_length=255)
    category      = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    file_size     = models.PositiveIntegerField(default=0)   # bytes
    mime_type     = models.CharField(max_length=100, blank=True)
    uploaded_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_files'
    )
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.original_name} ({self.category})'

    @property
    def file_size_kb(self):
        return round(self.file_size / 1024, 1)

    @property
    def extension(self):
        _, ext = os.path.splitext(self.original_name)
        return ext.lower()

    def delete(self, *args, **kwargs):
        # Delete physical file when record is deleted
        if self.file and os.path.exists(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)
