"""assignments/admin.py"""
from django.contrib import admin
from .models import Assignment, Submission, LecturerNote


class SubmissionInline(admin.TabularInline):
    model  = Submission
    extra  = 0
    fields = ['student', 'submitted', 'submitted_at', 'marks_obtained', 'feedback']
    readonly_fields = ['submitted_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display   = ['title', 'subject', 'max_marks', 'due_date', 'submission_count', 'created_by', 'is_active']
    list_filter    = ['subject', 'is_active', 'due_date']
    search_fields  = ['title', 'subject']
    inlines        = [SubmissionInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display   = ['student', 'assignment', 'submitted', 'marks_obtained', 'percentage', 'graded_at']
    list_filter    = ['submitted', 'assignment__subject']
    search_fields  = ['student__full_name', 'assignment__title']
    readonly_fields = ['submitted_at', 'graded_at', 'percentage']


@admin.register(LecturerNote)
class LecturerNoteAdmin(admin.ModelAdmin):
    list_display  = ['student', 'author', 'type', 'created_at']
    list_filter   = ['type']
    search_fields = ['student__full_name', 'author__full_name', 'content']
