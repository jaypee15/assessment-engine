from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    course = models.CharField(max_length=255, db_index=True)
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course} - {self.title}"

class Question(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = 'MCQ', 'Multiple Choice'
        SHORT_ANSWER = 'SA', 'Short Answer'

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=3, choices=QuestionType.choices)
    text = models.TextField()
    expected_answer = models.TextField(help_text="Correct answer text or option key")
    weight = models.FloatField(default=1.0, validators=[MinValueValidator(0.1)])
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['exam', 'order']),
        ]

    def __str__(self):
        return f"{self.exam.title} - Q{self.order}: {self.text[:50]}"

class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'exam'], name='unique_student_exam_submission')
        ]
        indexes = [
            models.Index(fields=['student', 'submitted_at']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

class Answer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    student_response = models.TextField()
    is_correct = models.BooleanField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"Ans: {self.submission} - Q{self.question.id}"
