from django.contrib.auth.models import User
from assessments.models import Exam, Question
from django.utils import timezone

# 1. Create Users
if not User.objects.filter(username='student1').exists():
    User.objects.create_user('student1', 'student1@example.com', 'pass1234')
    print("Created user: student1")

# 2. Create Exam
exam, created = Exam.objects.get_or_create(
    title="Introduction to AI",
    course="CS101",
    duration_minutes=60,
    defaults={'description': "Basic AI knowledge test."}
)
print(f"Exam: {exam.title}")

# 3. Create Questions
# Q1: MCQ (Weight 1.0)
q1, _ = Question.objects.get_or_create(
    exam=exam,
    order=1,
    defaults={
        'question_type': Question.QuestionType.MCQ,
        'text': "What does AI stand for?",
        'expected_answer': "Artificial Intelligence",
        'weight': 1.0
    }
)

# Q2: Text (Weight 2.0)
q2, _ = Question.objects.get_or_create(
    exam=exam,
    order=2,
    defaults={
        'question_type': Question.QuestionType.SHORT_ANSWER,
        'text': "Explain the concept of Machine Learning briefly.",
        'expected_answer': "Machine learning is a subset of artificial intelligence where computers learn from data without being explicitly programmed.",
        'weight': 2.0
    }
)

print("Seed data populated successfully.")
