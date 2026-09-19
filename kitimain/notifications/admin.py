"""notifications/admin.py"""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['recipient', 'type', 'title', 'is_read', 'created_at']
    list_filter   = ['type', 'is_read']
    search_fields = ['recipient__full_name', 'title']
    actions       = ['mark_read']

    @admin.action(description='Mark selected as read')
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
