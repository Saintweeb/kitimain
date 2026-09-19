"""
notifications/utils.py
Helper function – call from signals or views to create notifications.

Usage:
    from notifications.utils import notify
    notify(user, 'assignment', 'New Assignment Posted',
           body='Network Topology Design is due 20 Jul', link='/assignments/')
"""
from .models import Notification


def notify(recipient, notif_type, title, body='', link=''):
    """Create a notification for a user."""
    return Notification.objects.create(
        recipient=recipient,
        type=notif_type,
        title=title,
        body=body,
        link=link,
    )


def notify_all_students(notif_type, title, body='', link=''):
    """Broadcast a notification to every active student."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    students = User.objects.filter(role=User.STUDENT, is_active=True)
    notifications = [
        Notification(recipient=s, type=notif_type, title=title, body=body, link=link)
        for s in students
    ]
    Notification.objects.bulk_create(notifications)
