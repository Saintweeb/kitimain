"""assignments/serializers.py"""
from rest_framework import serializers
from .models import Assignment, Submission, LecturerNote


class AssignmentSerializer(serializers.ModelSerializer):
    created_by_name  = serializers.CharField(source='created_by.full_name', read_only=True)
    submission_count = serializers.ReadOnlyField()
    brief_file_url   = serializers.SerializerMethodField()

    class Meta:
        model  = Assignment
        fields = ['id', 'title', 'subject', 'description', 'max_marks', 'due_date',
                  'brief_file_url', 'created_by_name', 'is_active', 'submission_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_brief_file_url(self, obj):
        request = self.context.get('request')
        if obj.brief_file and request:
            return request.build_absolute_uri(obj.brief_file.url)
        return None


class SubmissionSerializer(serializers.ModelSerializer):
    student_name      = serializers.CharField(source='student.full_name', read_only=True)
    assignment_title  = serializers.CharField(source='assignment.title', read_only=True)
    max_marks         = serializers.IntegerField(source='assignment.max_marks', read_only=True)
    percentage        = serializers.ReadOnlyField()
    file_url          = serializers.SerializerMethodField()

    class Meta:
        model  = Submission
        fields = ['id', 'assignment', 'assignment_title', 'student', 'student_name',
                  'text_content', 'file_url', 'submitted', 'submitted_at',
                  'marks_obtained', 'max_marks', 'percentage', 'feedback', 'graded_at']
        read_only_fields = ['id', 'student', 'graded_at', 'graded_by']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.submitted_file and request:
            return request.build_absolute_uri(obj.submitted_file.url)
        return None


class GradeSubmissionSerializer(serializers.ModelSerializer):
    """Used by lecturers to record marks and feedback."""
    class Meta:
        model  = Submission
        fields = ['marks_obtained', 'feedback']


class LecturerNoteSerializer(serializers.ModelSerializer):
    author_name  = serializers.CharField(source='author.full_name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model  = LecturerNote
        fields = ['id', 'student', 'student_name', 'author', 'author_name',
                  'type', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
