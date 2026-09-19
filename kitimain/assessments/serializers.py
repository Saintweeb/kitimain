"""assessments/serializers.py"""
from rest_framework import serializers
from .models import CAT, Question, CATAttempt, CATAnswer


class QuestionSerializer(serializers.ModelSerializer):
    """Full question – shown to lecturers only (includes correct_ans)."""
    class Meta:
        model  = Question
        fields = ['id', 'cat', 'text', 'option_a', 'option_b', 'option_c', 'option_d',
                  'correct_ans', 'order']
        read_only_fields = ['id']


class QuestionStudentSerializer(serializers.ModelSerializer):
    """Question shown to students – correct answer hidden."""
    options = serializers.SerializerMethodField()

    class Meta:
        model  = Question
        fields = ['id', 'text', 'options', 'order']

    def get_options(self, obj):
        return {
            'A': obj.option_a,
            'B': obj.option_b,
            'C': obj.option_c,
            'D': obj.option_d,
        }


class CATSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    question_count  = serializers.ReadOnlyField()

    class Meta:
        model  = CAT
        fields = ['id', 'title', 'subject', 'instructions', 'duration_mins',
                  'scheduled_date', 'status', 'created_by_name', 'question_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class CATDetailSerializer(CATSerializer):
    """Includes questions – lecturer view."""
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta(CATSerializer.Meta):
        fields = CATSerializer.Meta.fields + ['questions']


class CATStudentDetailSerializer(CATSerializer):
    """Includes questions without answers – student view."""
    questions = QuestionStudentSerializer(many=True, read_only=True)

    class Meta(CATSerializer.Meta):
        fields = CATSerializer.Meta.fields + ['questions']


class CATAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CATAnswer
        fields = ['question', 'chosen_ans']


class SubmitCATSerializer(serializers.Serializer):
    """Payload: list of answers."""
    answers = CATAnswerSerializer(many=True)


class CATAttemptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    cat_title    = serializers.CharField(source='cat.title', read_only=True)
    percentage   = serializers.ReadOnlyField()
    time_taken   = serializers.ReadOnlyField(source='time_taken_seconds')

    class Meta:
        model  = CATAttempt
        fields = ['id', 'cat', 'cat_title', 'student', 'student_name',
                  'started_at', 'submitted_at', 'score', 'percentage',
                  'time_taken', 'is_complete']
        read_only_fields = ['id', 'started_at']
