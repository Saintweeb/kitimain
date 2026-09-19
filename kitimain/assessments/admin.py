"""assessments/admin.py"""
from django.contrib import admin
from .models import CAT, Question, CATAttempt, CATAnswer


class QuestionInline(admin.TabularInline):
    model  = Question
    extra  = 1
    fields = ['order', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_ans']


class CATAnswerInline(admin.TabularInline):
    model         = CATAnswer
    extra         = 0
    readonly_fields = ['question', 'chosen_ans', 'is_correct']
    can_delete    = False


@admin.register(CAT)
class CATAdmin(admin.ModelAdmin):
    list_display  = ['title', 'subject', 'status', 'duration_mins', 'question_count', 'scheduled_date', 'created_by']
    list_filter   = ['status', 'subject']
    search_fields = ['title', 'subject']
    inlines       = [QuestionInline]
    actions       = ['open_cat', 'close_cat']

    @admin.action(description='Open selected CATs')
    def open_cat(self, request, queryset):
        queryset.update(status=CAT.STATUS_OPEN)

    @admin.action(description='Close selected CATs')
    def close_cat(self, request, queryset):
        queryset.update(status=CAT.STATUS_CLOSED)


@admin.register(CATAttempt)
class CATAttemptAdmin(admin.ModelAdmin):
    list_display    = ['student', 'cat', 'score', 'percentage', 'is_complete', 'submitted_at']
    list_filter     = ['is_complete', 'cat__subject']
    search_fields   = ['student__full_name', 'cat__title']
    readonly_fields = ['started_at', 'submitted_at', 'percentage', 'time_taken_seconds']
    inlines         = [CATAnswerInline]
