"""courses/admin.py"""
from django.contrib import admin
from .models import Module, ModuleProgress, OnlineClass, Announcement, RevisionPaper


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display  = ['title', 'total_lessons', 'order', 'is_active', 'created_by']
    list_filter   = ['is_active']
    search_fields = ['title']
    ordering      = ['order']


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display  = ['student', 'module', 'lessons_done', 'percentage', 'completed']
    list_filter   = ['completed', 'module']
    search_fields = ['student__full_name', 'module__title']


@admin.register(OnlineClass)
class OnlineClassAdmin(admin.ModelAdmin):
    list_display  = ['name', 'subject', 'teacher', 'status', 'schedule']
    list_filter   = ['status', 'subject']
    search_fields = ['name', 'subject']
    actions       = ['set_live', 'set_upcoming', 'set_completed']

    @admin.action(description='Set selected to LIVE')
    def set_live(self, request, queryset):
        queryset.update(status='live')

    @admin.action(description='Set selected to Upcoming')
    def set_upcoming(self, request, queryset):
        queryset.update(status='upcoming')

    @admin.action(description='Set selected to Completed')
    def set_completed(self, request, queryset):
        queryset.update(status='completed')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display  = ['title', 'type', 'author', 'is_pinned', 'created_at']
    list_filter   = ['type', 'is_pinned']
    search_fields = ['title', 'body']


@admin.register(RevisionPaper)
class RevisionPaperAdmin(admin.ModelAdmin):
    list_display  = ['title', 'subject', 'year', 'type', 'uploaded_by']
    list_filter   = ['type', 'subject', 'year']
    search_fields = ['title', 'subject']
