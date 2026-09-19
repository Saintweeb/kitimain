"""
courses/serializers.py
"""
from rest_framework import serializers
from .models import Module, ModuleProgress, OnlineClass, Announcement, RevisionPaper


class ModuleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model  = Module
        fields = ['id', 'title', 'description', 'icon', 'tags', 'total_lessons',
                  'order', 'is_active', 'created_by_name', 'created_at']


class ModuleProgressSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)
    percentage   = serializers.ReadOnlyField()

    class Meta:
        model  = ModuleProgress
        fields = ['id', 'module', 'module_title', 'lessons_done', 'completed', 'percentage', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class OnlineClassSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)

    class Meta:
        model  = OnlineClass
        fields = ['id', 'name', 'subject', 'description', 'teacher', 'teacher_name',
                  'schedule', 'meeting_link', 'status', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)

    class Meta:
        model  = Announcement
        fields = ['id', 'title', 'body', 'type', 'author', 'author_name', 'is_pinned', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class RevisionPaperSerializer(serializers.ModelSerializer):
    file_url       = serializers.SerializerMethodField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)

    class Meta:
        model  = RevisionPaper
        fields = ['id', 'title', 'subject', 'year', 'paper', 'type', 'file_url',
                  'external_url', 'uploaded_by_name', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.external_url or None
