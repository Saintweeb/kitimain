"""
notifications/signals.py
Django signals that fire notifications automatically.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='assignments.Assignment')
def on_new_assignment(sender, instance, created, **kwargs):
    if created:
        from .utils import notify_all_students
        notify_all_students(
            notif_type='assignment',
            title=f'New Assignment: {instance.title}',
            body=f'{instance.subject} – Due {instance.due_date}',
            link='/assignments/',
        )


@receiver(post_save, sender='assignments.Submission')
def on_submission_graded(sender, instance, **kwargs):
    if instance.marks_obtained is not None and instance.graded_at:
        from .utils import notify
        notify(
            recipient=instance.student,
            notif_type='grade',
            title=f'Assignment Graded: {instance.assignment.title}',
            body=f'You scored {instance.marks_obtained}/{instance.assignment.max_marks}.',
            link='/assignments/',
        )


@receiver(post_save, sender='assignments.LecturerNote')
def on_new_note(sender, instance, created, **kwargs):
    if created:
        from .utils import notify
        notify(
            recipient=instance.student,
            notif_type='note',
            title=f'New note from {instance.author.full_name}',
            body=instance.content[:120],
            link='/profile/',
        )


@receiver(post_save, sender='assessments.CAT')
def on_cat_opened(sender, instance, **kwargs):
    if instance.status == 'open':
        from .utils import notify_all_students
        notify_all_students(
            notif_type='cat',
            title=f'CAT Now Open: {instance.title}',
            body=f'{instance.subject} – {instance.duration_mins} minutes. Start now!',
            link='/cat/',
        )


@receiver(post_save, sender='courses.Announcement')
def on_announcement(sender, instance, created, **kwargs):
    if created:
        from .utils import notify_all_students
        notify_all_students(
            notif_type='general',
            title=instance.title,
            body=instance.body[:120],
            link='/dashboard/',
        )
