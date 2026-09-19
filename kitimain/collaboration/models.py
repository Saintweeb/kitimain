"""
collaboration/models.py  –  Chat Rooms, Messages, CodeSpace snapshots.
"""
from django.db import models
from django.conf import settings


class Room(models.Model):
    TYPE_CLASS     = 'class'
    TYPE_STUDY     = 'study'
    TYPE_CODESPACE = 'codespace'
    TYPE_CHOICES   = [
        (TYPE_CLASS,     'Class Room'),
        (TYPE_STUDY,     'Study Group'),
        (TYPE_CODESPACE, 'CodeSpace'),
    ]

    name       = models.CharField(max_length=200)
    type       = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_STUDY)
    icon       = models.CharField(max_length=10, default='💬')
    members    = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='rooms',
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='rooms_created'
    )
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.type})'


class Message(models.Model):
    room       = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages_sent'
    )
    text       = models.TextField()
    file       = models.FileField(upload_to='room_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.full_name} in {self.room.name}: {self.text[:50]}'


class CodeSnapshot(models.Model):
    """Saved code snapshot in a codespace room."""
    LANG_PYTHON = 'python'
    LANG_HTML   = 'html'
    LANG_JS     = 'javascript'
    LANG_SQL    = 'sql'
    LANG_CHOICES = [
        (LANG_PYTHON, 'Python'),
        (LANG_HTML,   'HTML'),
        (LANG_JS,     'JavaScript'),
        (LANG_SQL,    'SQL'),
    ]

    room       = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='snapshots')
    saved_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='code_snapshots'
    )
    language   = models.CharField(max_length=20, choices=LANG_CHOICES, default=LANG_PYTHON)
    title      = models.CharField(max_length=200, default='Untitled')
    code       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} – {self.room.name}'
