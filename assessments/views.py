from rest_framework import viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from assessments.models import Exam, Submission, Answer, Question
from assessments.serializers import (
    ExamListSerializer, ExamDetailSerializer, SubmissionCreateSerializer,
    SubmissionListSerializer, SubmissionDetailSerializer
)
from assessments.grading.service import GradingService

class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to list Exams and handle Submissions.
    """
    queryset = Exam.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExamDetailSerializer
        return ExamListSerializer

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_exam(self, request, pk=None):
        exam = self.get_object()
        serializer = SubmissionCreateSerializer(data=request.data, context={'request': request, 'exam': exam})
        serializer.is_valid(raise_exception=True)

        answers_data = serializer.validated_data['answers']

        try:
            with transaction.atomic():
                submission = Submission.objects.create(
                    student=request.user,
                    exam=exam,
                    submitted_at=timezone.now()
                )

                q_ids = [a['question_id'] for a in answers_data]
                questions = {q.id: q for q in Question.objects.filter(id__in=q_ids, exam=exam)}
                
                new_answers = []
                for ans_input in answers_data:
                    q_id = ans_input['question_id']
                    question = questions.get(q_id)
                    if not question:
                        raise ValueError(f"Question ID {q_id} does not belong to this exam.")
                    
                    new_answers.append(Answer(
                        submission=submission,
                        question=question,
                        student_response=ans_input['student_response']
                    ))
                
                Answer.objects.bulk_create(new_answers)

                grading_service = GradingService()
                grading_service.grade(submission.id)
                
                submission.refresh_from_db()
                
                return Response(
                    SubmissionDetailSerializer(submission).data,
                    status=status.HTTP_201_CREATED
                )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "An error occurred during submission."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmissionViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user)\
            .select_related('exam')\
            .order_by('-submitted_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubmissionDetailSerializer
        return SubmissionListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # Schema generation workaround
            return Submission.objects.none()

        if not self.request.user.is_authenticated:
            return Submission.objects.none()

        qs = Submission.objects.filter(student=self.request.user).select_related('exam')
        if self.action == 'retrieve':
            qs = qs.prefetch_related('answers__question')
        return qs.order_by('-submitted_at')
