from abc import ABC, abstractmethod
import math
from collections import Counter
from django.conf import settings
from assessments.models import Submission, Answer, Question

class GradingStrategy(ABC):
    """
    Abstract Base Class for Grading Strategies.
    Allows swapping between Rule-Based, Mock-AI, or Real LLM strategies.
    """
    @abstractmethod
    def grade_submission(self, submission: Submission) -> float:
        pass

class MockGradingStrategy(GradingStrategy):
    """
    Implements a simple grading algorithm.
    Uses basic keyword matching / cosine similarity simulation for text answers.
    """
    def grade_submission(self, submission: Submission) -> float:
        total_score = 0
        total_weight = 0

        # Prefetch answers and related questions to minimize queries during grading loop
        answers = submission.answers.select_related('question').all()

        for answer in answers:
            question = answer.question
            total_weight += question.weight
            
            if question.question_type == Question.QuestionType.MCQ:
                score = self._grade_mcq(answer, question)
            else:
                score = self._grade_text_similarity(answer, question)
            
            answer.is_correct = (score == 1.0)
            answer.save()
            total_score += (score * question.weight)

        final_score = (total_score / total_weight) * 100 if total_weight > 0 else 0
        submission.score = round(final_score, 2)
        submission.save()
        return submission.score

    def _grade_mcq(self, answer: Answer, question: Question) -> float:
        return 1.0 if answer.student_response.strip() == question.expected_answer.strip() else 0.0

    def _grade_text_similarity(self, answer: Answer, question: Question) -> float:
        """
        Calculates Cosine Similarity between student response and expected answer.
        """
        text1 = answer.student_response.lower()
        text2 = question.expected_answer.lower()
        
        # Tokenize (simple whitespace split)
        vec1 = Counter(text1.split())
        vec2 = Counter(text2.split())
        
        # Intersection
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        
        if not denominator:
            return 0.0
        
        similarity = float(numerator) / denominator
        return similarity
