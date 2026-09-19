"""collaboration/admin.py"""
from django.contrib import admin
from .models import Room, Message, CodeSnapshot


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display   = ['name', 'type', 'member_count', 'created_by', 'is_active']
    list_filter    = ['type', 'is_active']
    search_fields  = ['name']
    filter_horizontal = ['members']

    def member_count(self, obj):
        return obj.members.count()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ['sender', 'room', 'text_preview', 'created_at']
    list_filter   = ['room']
    search_fields = ['sender__full_name', 'text']

    def text_preview(self, obj):
        return obj.text[:60]


@admin.register(CodeSnapshot)
class CodeSnapshotAdmin(admin.ModelAdmin):
    list_display  = ['title', 'room', 'language', 'saved_by', 'created_at']
    list_filter   = ['language', 'room']
    search_fields = ['title', 'saved_by__full_name']
