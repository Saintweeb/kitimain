"""attendance/serializers.py"""
from rest_framework import serializers
from .models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.full_name', read_only=True)

    class Meta:
        model  = AttendanceRecord
        fields = ['id', 'student', 'student_name', 'date', 'status',
                  'online_class', 'marked_by_name', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at', 'marked_by_name']


class BulkAttendanceSerializer(serializers.Serializer):
    """POST body: { date, records: [{student_id, status, notes}] }"""
    date    = serializers.DateField()
    records = serializers.ListField(
        child=serializers.DictField()
    )
