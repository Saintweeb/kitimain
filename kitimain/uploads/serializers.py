"""uploads/serializers.py"""
from rest_framework import serializers
from .models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):
    file_url         = serializers.SerializerMethodField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)

    class Meta:
        model  = UploadedFile
        fields = ['id', 'file_url', 'original_name', 'category',
                  'file_size_kb', 'extension', 'mime_type',
                  'uploaded_by_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'uploaded_by_name',
                            'file_size_kb', 'extension']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
