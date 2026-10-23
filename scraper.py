import os
import json
import urllib.request
import datetime

API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_google_jobs():
    today = datetime.date.today().isoformat()
    expiry = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()
    
    prompt = f"""
    You are an enterprise career compliance engine for DirectHireHub.in.
    Generate 3 verified walk-in drives or private hiring vacancies in India for {today}.
    Target locations: Noida, Gurgaon, Delhi-NCR, Bangalore, or Remote.
    
    CRITICAL FOR GOOGLE SEARCH CONSOLE VALIDATION:
    Output MUST be a pure raw JSON array of objects without any markdown, backticks or explanations.
    Each object must strictly include:
    - "id": unique integer timestamp
    - "title": Job title (e.g. "Customer Support Executive")
    - "company": Corporate name (e.g. "Genpact", "Wipro", "TELUS Digital")
    - "city": City name
    - "state": State/Region (e.g. "Haryana", "Uttar Pradesh", "Karnataka")
    - "type": "FULL_TIME"
    - "salary_min": integer (e.g. 250000)
    - "salary_max": integer (e.g. 350000)
    - "date_posted": "{today}"
    - "valid_through": "{expiry}T23:59:59+05:30"
    - "description": 2-3 paragraph professional job description with role overview, eligibility, and reporting rules.
    - "venue": Exact street address for walk-in reporting
    - "metro": Nearest metro station / landmark
    - "timing": Interview reporting hours (e.g. "10:00 AM - 1:00 PM")
    - "checklist": Array of 4-5 mandatory items (Resume copies, Govt ID, Marksheets, etc.)
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            text = res_json['candidates'][0]['content']['parts'][0]['text']
            cleaned = text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
    except Exception as e:
        print(f"Extraction error: {e}")
        return []

def update_database():
    new_jobs = generate_google_jobs()
    if not new_jobs:
        return

    file_path = "jobs.json"
    existing = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    combined = new_jobs + existing
    unique_jobs = []
    seen = set()
    for job in combined:
        key = (job.get("company", ""), job.get("title", ""), job.get("city", ""))
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(unique_jobs[:50], f, indent=2, ensure_ascii=False)
    print("Database updated with Google-compliant entries.")

if __name__ == "__main__":
    update_database()
  
