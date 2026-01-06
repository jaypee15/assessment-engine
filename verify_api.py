import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def run_test():
    # 1. Login to get Token
    print("1. Authenticating...")
    auth_resp = requests.post(f"{BASE_URL}/token-auth/", data={
        'username': 'student1',
        'password': 'pass1234'
    })
    if auth_resp.status_code != 200:
        print(f"Login failed: {auth_resp.text}")
        sys.exit(1)
    
    token = auth_resp.json()['token']
    headers = {'Authorization': f'Token {token}'}
    print(f"   Success! Token: {token[:10]}...")

    # 2. List Exams
    print("\n2. Listing Exams...")
    exams_resp = requests.get(f"{BASE_URL}/exams/", headers=headers)
    exams = exams_resp.json()
    print(f"   Found {len(exams)} exams.")
    if not exams:
        print("   No exams found to take.")
        sys.exit(1)
    
    exam_id = exams[0]['id']
    print(f"   Selected Exam ID: {exam_id}")

    # 3. Get Exam Details (Questions)
    print("\n3. Fetching Exam Details...")
    exam_detail_resp = requests.get(f"{BASE_URL}/exams/{exam_id}/", headers=headers)
    questions = exam_detail_resp.json()['questions']
    for q in questions:
        print(f"   Q{q['order']}: {q['text']} (ID: {q['id']})")

    # 4. Submit Answers
    print("\n4. Submitting Answers...")
    # Prepare answers
    # Q1: "Artificial Intelligence" (Correct)
    # Q2: "Machine learning is where computers learn from data." (Partial/Similar)
    
    payload = {
        "answers": [
            {
                "question_id": questions[0]['id'],
                "student_response": "Artificial Intelligence" 
            },
            {
                "question_id": questions[1]['id'],
                "student_response": "Machine learning is where computers learn from data."
            }
        ]
    }
    
    submit_resp = requests.post(f"{BASE_URL}/exams/{exam_id}/submit/", json=payload, headers=headers)
    
    if submit_resp.status_code != 201:
        print(f"   Submission Failed: {submit_resp.status_code} {submit_resp.text}")
        # Could be duplicate submission, which is also a valid test
        if "already submitted" in submit_resp.text:
            print("   (Previously submitted)")
    else:
        submission = submit_resp.json()
        print(f"   Success! Score: {submission['score']}")
        print(f"   Answers: {len(submission['answers'])}")

    # 5. List Submissions (Verify Optimization & History)
    print("\n5. Listing My Submissions...")
    subs_resp = requests.get(f"{BASE_URL}/submissions/", headers=headers)
    subs = subs_resp.json()
    for s in subs:
        print(f"   - {s['exam_title']}: Score {s['score']} (ID: {s['id']})")

if __name__ == "__main__":
    try:
        run_test()
    except requests.exceptions.ConnectionError:
        print("Error: application is not running on port 8000. Start it first.")
