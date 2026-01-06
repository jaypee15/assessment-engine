# Mini Assessment Engine (Acad AI)

A Django-based REST API for creating exams, submitting answers, and automated mock grading.

## Prerequisites

- Python 3.12+
- `uv` (recommended) or `pip`

## Setup

1. **Create Virtual Environment & Install Dependencies**:

   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   # OR just install manually if no requirements.txt yet (I will create it)
   uv pip install django djangorestframework drf-yasg numpy requests
   ```

2. **Database Migration**:

   ```bash
   python manage.py migrate
   ```

3. **Seed Data** (Optional, creates `student1` / `pass1234` and a sample Exam):
   ```bash
   python manage.py shell < seed_data.py
   ```

## Running the Server

```bash
source .venv/bin/activate
python manage.py runserver
```

- API Root: http://127.0.0.1:8000/api/
- Swagger UI: http://127.0.0.1:8000/swagger/

## Testing

Run the verification script to simulate a full exam flow:

```bash
python verify_api.py
```
