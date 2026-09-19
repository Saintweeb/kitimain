"""attendance/admin.py"""
from django.contrib import admin
from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display   = ['student', 'date', 'status', 'marked_by', 'online_class']
    list_filter    = ['status', 'date']
    search_fields  = ['student__full_name']
    date_hierarchy = 'date'
    ordering       = ['-date']
