"""
assessments/models.py  –  Online CAT / Quiz system.

NOTE: Question is defined BEFORE CAT so Pylance can resolve the
`questions` reverse-FK without a forward-reference warning.
Django's ForeignKey accepts a string label ('assessments.CAT') to
handle the forward reference at the ORM level.
"""
from django.db import models
from django.conf import settings


# ── Question defined first so CAT.question_count can reference it ─────────────

class Question(models.Model):
    """A single MCQ question belonging to a CAT."""
    cat = models.ForeignKey(
        'assessments.CAT',
        on_delete=models.CASCADE,
        related_name='questions',
    )
    text        = models.TextField()
    option_a    = models.CharField(max_length=500)
    option_b    = models.CharField(max_length=500)
    option_c    = models.CharField(max_length=500)
    option_d    = models.CharField(max_length=500)
    correct_ans = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'Q{self.order}: {self.text[:60]}'

    def options_list(self):
        return [self.option_a, self.option_b, self.option_c, self.option_d]


# ── CAT defined after Question so the reverse FK is already resolved ──────────

class CAT(models.Model):
    """Continuous Assessment Test."""
    STATUS_DRAFT    = 'draft'
    STATUS_UPCOMING = 'upcoming'
    STATUS_OPEN     = 'open'
    STATUS_CLOSED   = 'closed'
    STATUS_CHOICES  = [
        (STATUS_DRAFT,    'Draft'),
        (STATUS_UPCOMING, 'Upcoming'),
        (STATUS_OPEN,     'Open'),
        (STATUS_CLOSED,   'Closed'),
    ]

    title          = models.CharField(max_length=300)
    subject        = models.CharField(max_length=100)
    instructions   = models.TextField(blank=True)
    duration_mins  = models.PositiveIntegerField(default=30)
    scheduled_date = models.DateField(null=True, blank=True)
    status         = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cats_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'CAT'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.status})'

    @property
    def question_count(self) -> int:
        """Number of questions attached to this CAT."""
        return self.questions.count()


# ── Attempt & Answer ──────────────────────────────────────────────────────────

class CATAttempt(models.Model):
    """A student's attempt at a CAT."""
    cat     = models.ForeignKey(CAT, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cat_attempts',
    )
    started_at   = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score        = models.PositiveIntegerField(null=True, blank=True)
    is_complete  = models.BooleanField(default=False)

    class Meta:
        unique_together = ('cat', 'student')

    def __str__(self):
        return f'{self.student.full_name} – {self.cat.title}'

    @property
    def percentage(self):
        qc = self.cat.question_count
        if self.score is None or qc == 0:
            return None
        return round(self.score / qc * 100)

    @property
    def time_taken_seconds(self):
        if self.submitted_at and self.started_at:
            return int((self.submitted_at - self.started_at).total_seconds())
        return None


class CATAnswer(models.Model):
    """Individual answer within an attempt."""
    attempt    = models.ForeignKey(CATAttempt, on_delete=models.CASCADE, related_name='answers')
    question   = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_ans = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')

    def save(self, *args, **kwargs):
        self.is_correct = (self.chosen_ans == self.question.correct_ans)
        super().save(*args, **kwargs)
