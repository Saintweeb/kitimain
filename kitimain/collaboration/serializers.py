"""collaboration/serializers.py"""
from rest_framework import serializers
from .models import Room, Message, CodeSnapshot


class RoomSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    member_names = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model  = Room
        fields = ['id', 'name', 'type', 'icon', 'member_count', 'member_names',
                  'created_by_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_member_names(self, obj):
        return [m.full_name for m in obj.members.all()[:8]]


class MessageSerializer(serializers.ModelSerializer):
    sender_name    = serializers.CharField(source='sender.full_name', read_only=True)
    sender_initials = serializers.CharField(source='sender.initials', read_only=True)
    file_url       = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = ['id', 'room', 'sender', 'sender_name', 'sender_initials',
                  'text', 'file_url', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class CodeSnapshotSerializer(serializers.ModelSerializer):
    saved_by_name = serializers.CharField(source='saved_by.full_name', read_only=True)

    class Meta:
        model  = CodeSnapshot
        fields = ['id', 'room', 'saved_by_name', 'language', 'title', 'code', 'created_at']
        read_only_fields = ['id', 'created_at', 'saved_by_name']
