"""
Central mock data store.

Every page pulls its sample data from here instead of hardcoding values
inline. When a real database/API is wired in later, only this file
(or its call sites) needs to change - page code stays untouched.
"""

import pandas as pd

# ---- Dashboard KPIs ----
KPIS = [
    {"label": "Open Positions", "value": "24", "delta": "+3", "icon": "💼"},
    {"label": "Active Candidates", "value": "312", "delta": "+18", "icon": "👥"},
    {"label": "Interviews Scheduled", "value": "17", "delta": "+5", "icon": "🗓️"},
    {"label": "Avg. Time to Hire", "value": "16 days", "delta": "-2", "icon": "⏱️"},
]

# ---- Hiring trend (line chart) ----
TREND_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
TREND_APPLICATIONS = [120, 145, 160, 190, 210, 240]
TREND_HIRES = [8, 10, 9, 14, 15, 18]

# ---- Recruitment funnel ----
FUNNEL_STAGES = ["Applied", "Screened", "Interviewed", "Offer", "Hired"]
FUNNEL_VALUES = [312, 180, 95, 40, 18]

# ---- Department hiring ----
DEPARTMENTS = ["Engineering", "AI/ML", "Sales", "Design", "Operations"]
DEPARTMENT_COUNTS = [42, 27, 33, 15, 19]

# ---- Recent candidates ----
RECENT_CANDIDATES = pd.DataFrame([
    {"Candidate": "Ananya Rao", "Role": "AI Engineer", "Match": "92%", "Stage": "Interview", "Applied": "2 days ago"},
    {"Candidate": "Karan Mehta", "Role": "Backend Developer", "Match": "87%", "Stage": "Screened", "Applied": "3 days ago"},
    {"Candidate": "Priya Nair", "Role": "Product Designer", "Match": "84%", "Stage": "Applied", "Applied": "4 days ago"},
    {"Candidate": "Rohan Gupta", "Role": "Data Analyst", "Match": "79%", "Stage": "Offer", "Applied": "5 days ago"},
    {"Candidate": "Sneha Iyer", "Role": "AI Engineer", "Match": "90%", "Stage": "Interview", "Applied": "1 week ago"},
])

# ---- Recent activity feed ----
RECENT_ACTIVITY = [
    {"icon": "✅", "text": "Rahul shortlisted Ananya Rao for AI Engineer", "time": "10 min ago"},
    {"icon": "📩", "text": "New application received for Backend Developer", "time": "45 min ago"},
    {"icon": "🗓️", "text": "Interview scheduled with Priya Nair", "time": "2 hours ago"},
    {"icon": "🏆", "text": "Offer accepted by Rohan Gupta", "time": "1 day ago"},
]

# ---- Upcoming interviews ----
UPCOMING_INTERVIEWS = pd.DataFrame([
    {"Candidate": "Ananya Rao", "Role": "AI Engineer", "Interviewer": "Rahul", "Time": "Today, 3:00 PM"},
    {"Candidate": "Sneha Iyer", "Role": "AI Engineer", "Interviewer": "Aditi", "Time": "Tomorrow, 11:00 AM"},
    {"Candidate": "Karan Mehta", "Role": "Backend Developer", "Interviewer": "Sneha", "Time": "Jul 6, 2:30 PM"},
])

# ---- Recruiter performance (Hiring Analytics) ----
RECRUITER_PERFORMANCE = pd.DataFrame([
    {"Recruiter": "Rahul", "Candidates Hired": 18, "Avg Time to Hire": "16 Days", "Offer Acceptance": "92%"},
    {"Recruiter": "Sneha", "Candidates Hired": 15, "Avg Time to Hire": "19 Days", "Offer Acceptance": "87%"},
    {"Recruiter": "Aditi", "Candidates Hired": 13, "Avg Time to Hire": "18 Days", "Offer Acceptance": "85%"},
    {"Recruiter": "Rohan", "Candidates Hired": 11, "Avg Time to Hire": "22 Days", "Offer Acceptance": "81%"},
])

# ---- Monthly hiring report (Hiring Analytics) ----
MONTHLY_REPORT = pd.DataFrame([
    {"Month": "Jan", "Applications": 120, "Interviews": 45, "Offers": 12, "Hires": 8},
    {"Month": "Feb", "Applications": 145, "Interviews": 52, "Offers": 14, "Hires": 10},
    {"Month": "Mar", "Applications": 160, "Interviews": 58, "Offers": 13, "Hires": 9},
    {"Month": "Apr", "Applications": 190, "Interviews": 70, "Offers": 18, "Hires": 14},
    {"Month": "May", "Applications": 210, "Interviews": 76, "Offers": 20, "Hires": 15},
    {"Month": "Jun", "Applications": 240, "Interviews": 88, "Offers": 24, "Hires": 18},
])

TIME_TO_HIRE_DAYS = 16
OFFER_ACCEPTANCE_RATE = "87%"

# ---- Full candidate pool (Candidate Screening) ----
# EmployeeID / Experience / PerformanceRating / Location are additive
# fields for the Talent Management view - nothing below depends on them,
# so existing AI ranking/comparison/skill-gap/email features are unaffected.
ALL_CANDIDATES = pd.DataFrame([
    {"Candidate": "Ananya Rao", "Role": "AI Engineer", "Department": "AI/ML", "Match": 92, "Stage": "Interview", "Skills": "Python, TensorFlow, NLP", "Applied": "2 days ago", "EmployeeID": "EMP-1001", "Experience": 4, "PerformanceRating": 4.6, "Location": "Bengaluru"},
    {"Candidate": "Karan Mehta", "Role": "Backend Developer", "Department": "Engineering", "Match": 87, "Stage": "Screened", "Skills": "Python, Django, PostgreSQL", "Applied": "3 days ago", "EmployeeID": "EMP-1002", "Experience": 5, "PerformanceRating": 4.1, "Location": "Pune"},
    {"Candidate": "Priya Nair", "Role": "Product Designer", "Department": "Design", "Match": 84, "Stage": "Applied", "Skills": "Figma, UX Research", "Applied": "4 days ago", "EmployeeID": "EMP-1003", "Experience": 3, "PerformanceRating": 3.8, "Location": "Mumbai"},
    {"Candidate": "Rohan Gupta", "Role": "Data Analyst", "Department": "Engineering", "Match": 79, "Stage": "Offer", "Skills": "SQL, Excel, Power BI", "Applied": "5 days ago", "EmployeeID": "EMP-1004", "Experience": 2, "PerformanceRating": 4.3, "Location": "Hyderabad"},
    {"Candidate": "Sneha Iyer", "Role": "AI Engineer", "Department": "AI/ML", "Match": 90, "Stage": "Interview", "Skills": "Python, PyTorch, LLMs", "Applied": "1 week ago", "EmployeeID": "EMP-1005", "Experience": 6, "PerformanceRating": 4.8, "Location": "Bengaluru"},
    {"Candidate": "Aditi Shah", "Role": "Sales Executive", "Department": "Sales", "Match": 74, "Stage": "Applied", "Skills": "CRM, Negotiation", "Applied": "1 week ago", "EmployeeID": "EMP-1006", "Experience": 1, "PerformanceRating": 3.2, "Location": "Delhi"},
    {"Candidate": "Vikram Singh", "Role": "DevOps Engineer", "Department": "Engineering", "Match": 81, "Stage": "Screened", "Skills": "AWS, Docker, Kubernetes", "Applied": "8 days ago", "EmployeeID": "EMP-1007", "Experience": 7, "PerformanceRating": 4.4, "Location": "Remote"},
    {"Candidate": "Meera Joshi", "Role": "HR Coordinator", "Department": "Operations", "Match": 70, "Stage": "Rejected", "Skills": "Recruitment, Onboarding", "Applied": "9 days ago", "EmployeeID": "EMP-1008", "Experience": 2, "PerformanceRating": 3.0, "Location": "Pune"},
])

CANDIDATE_TIMELINE = {
    "Ananya Rao": [
        {"stage": "Applied", "date": "Jun 27, 2026", "note": "Application received via careers page."},
        {"stage": "Screened", "date": "Jun 28, 2026", "note": "Resume matched 92% against job description."},
        {"stage": "Interview Scheduled", "date": "Jul 2, 2026", "note": "Technical round set with Rahul."},
    ],
}

# ---- Resume Analyzer sample parsed resume ----
SAMPLE_RESUME = {
    "name": "Ananya Rao",
    "role_applied": "AI Engineer",
    "email": "ananya.rao@email.com",
    "phone": "+91 98765 43210",
    "location": "Bengaluru, India",
    "ats_score": 92,
    "strength": "Strong",
    "skills_matched": ["Python", "TensorFlow", "NLP", "SQL", "Git"],
    "skills_missing": ["Kubernetes", "MLOps"],
    "education": [
        {"degree": "M.Tech, Computer Science", "school": "IIT Bombay", "year": "2022"},
    ],
    "experience": [
        {"title": "ML Engineer", "company": "DataSphere Analytics", "duration": "2022 - Present",
         "desc": "Built and deployed NLP models for document classification at scale."},
        {"title": "Research Intern", "company": "AI4Bharat", "duration": "2021 - 2022",
         "desc": "Worked on multilingual language model fine-tuning."},
    ],
    "certifications": ["TensorFlow Developer Certificate", "AWS Machine Learning Specialty"],
    "projects": ["Resume Screening NLP Pipeline", "Real-time Fraud Detection Model"],
    "ai_summary": (
        "Ananya is a strong AI Engineering candidate with hands-on experience "
        "deploying NLP models in production. Her background aligns closely with "
        "the role's core requirements, with minor gaps in MLOps tooling."
    ),
}

# ---- Interview Copilot ----
INTERVIEW_SCHEDULE = pd.DataFrame([
    {"Candidate": "Ananya Rao", "Role": "AI Engineer", "Type": "Technical", "Interviewer": "Rahul", "Time": "Today, 3:00 PM"},
    {"Candidate": "Sneha Iyer", "Role": "AI Engineer", "Type": "HR Round", "Interviewer": "Aditi", "Time": "Tomorrow, 11:00 AM"},
    {"Candidate": "Karan Mehta", "Role": "Backend Developer", "Type": "Technical", "Interviewer": "Sneha", "Time": "Jul 6, 2:30 PM"},
])

# ---- Job Descriptions (Job Description Manager) ----
JOB_DESCRIPTIONS_SEED = [
    {
        "id": "jd-001",
        "title": "AI Engineer",
        "department": "AI/ML",
        "level": "Mid",
        "employment_type": "Full-time",
        "description": (
            "We're looking for an AI Engineer to design, build, and deploy "
            "machine learning models in production. You'll work closely with "
            "the data team on NLP pipelines, model evaluation, and MLOps. "
            "Strong Python skills and hands-on experience with TensorFlow or "
            "PyTorch required. Experience with LLMs, vector databases, and "
            "cloud deployment (AWS/GCP) is a strong plus."
        ),
        "required_skills": ["Python", "TensorFlow", "PyTorch", "NLP", "SQL"],
        "nice_to_have_skills": ["Kubernetes", "MLOps", "LLMs", "AWS"],
        "created": "Jun 20, 2026",
    },
    {
        "id": "jd-002",
        "title": "Backend Developer",
        "department": "Engineering",
        "level": "Mid",
        "employment_type": "Full-time",
        "description": (
            "Backend Developer to own core services powering our platform. "
            "You'll design REST APIs, optimize database queries, and ship "
            "reliable, well-tested code. Strong Python and Django experience "
            "required, PostgreSQL and Docker experience preferred."
        ),
        "required_skills": ["Python", "Django", "PostgreSQL", "REST APIs"],
        "nice_to_have_skills": ["Docker", "Redis", "AWS"],
        "created": "Jun 18, 2026",
    },
]

INTERVIEW_QUESTIONS = {
    "Technical": [
        "Walk me through a project where you used Python at scale.",
        "How would you design a system to deduplicate incoming resumes?",
        "Explain the tradeoffs between precision and recall in a screening model.",
        "How would you debug a model that performs well offline but poorly in production?",
    ],
    "HR Questions": [
        "Tell me about a time you disagreed with a teammate's approach.",
        "How do you prioritize when handling multiple deadlines?",
        "What kind of team environment helps you do your best work?",
    ],
    "Coding": [
        "Given a list of resumes and a job description, outline an approach to rank them.",
        "Write a function to find the top-k matching skills between two sets.",
    ],
}
