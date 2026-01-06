from rest_framework import serializers
from django.db import transaction
from assessments.models import Exam, Question, Submission, Answer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_type', 'text', 'weight', 'order']

class ExamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'title', 'description', 'course', 'duration_minutes', 'created_at']

class ExamDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'description', 'course', 'duration_minutes', 'metadata', 'questions']

class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    student_response = serializers.CharField()

class SubmissionCreateSerializer(serializers.Serializer):
    answers = AnswerInputSerializer(many=True)

    def validate(self, attrs):
        request = self.context.get('request')
        exam = self.context.get('exam')
        
        if request and exam:
            if Submission.objects.filter(student=request.user, exam=exam).exists():
                raise serializers.ValidationError("You have already submitted this exam.")
        
        return attrs

class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    expected_answer = serializers.SerializerMethodField()
    
    class Meta:
        model = Answer
        fields = ['id', 'question', 'question_text', 'student_response', 'is_correct', 'feedback', 'expected_answer']

    def get_expected_answer(self, obj):
        return obj.question.expected_answer

class SubmissionDetailSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'exam', 'exam_title', 'score', 'submitted_at', 'answers']

class SubmissionListSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'exam', 'exam_title', 'score', 'submitted_at']
