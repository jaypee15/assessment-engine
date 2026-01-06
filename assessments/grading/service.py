from .strategies import GradingStrategy, MockGradingStrategy
from assessments.models import Submission

class GradingService:
    def __init__(self, strategy: GradingStrategy = None):
        # Default to MockGradingStrategy, but allow injection
        self.strategy = strategy or MockGradingStrategy()

    def grade(self, submission_id: int) -> float:
        try:
            submission = Submission.objects.get(id=submission_id)
            return self.strategy.grade_submission(submission)
        except Submission.DoesNotExist:
            raise ValueError(f"Submission {submission_id} does not exist")
