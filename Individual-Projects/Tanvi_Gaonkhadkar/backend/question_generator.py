from backend.ollama_client import ask_llama
from backend.ai_parser import parse_json


def generate_questions(resume_data, jd_data):
    """
    Generate interview questions based on parsed resume and job description.

    Parameters
    ----------
    resume_data : dict
        Output from extract_resume_info()

    jd_data : dict
        Output from extract_jd_info()

    Returns
    -------
    dict
        {
            "technical": [...],
            "hr": [...],
            "behavioral": [...]
        }
    """

    prompt = f"""
You are an experienced Technical Interviewer.

Your task is to generate interview questions for the candidate.

Candidate Resume Information

Skills:
{resume_data.get("skills", [])}

Projects:
{resume_data.get("projects", [])}

Experience:
{resume_data.get("experience", [])}

Education:
{resume_data.get("education", [])}


Job Description

Required Skills:
{jd_data.get("required_skills", [])}

Required Experience:
{jd_data.get("experience", "")}

Required Education:
{jd_data.get("education", "")}


Instructions

Generate interview questions in exactly three categories.

1. Technical Questions
- Focus on candidate skills.
- Focus on candidate projects.
- Include role-specific technical questions.

Generate exactly 5 questions.

2. HR Questions
- Motivation
- Career goals
- Communication
- Company fit

Generate exactly 5 questions.

3. Behavioral Questions
- Leadership
- Teamwork
- Conflict resolution
- Problem solving
- Decision making

Generate exactly 5 questions.

Return ONLY valid JSON.

Example

{{
    "technical": [
        "...",
        "...",
        "...",
        "...",
        "..."
    ],

    "hr": [
        "...",
        "...",
        "...",
        "...",
        "..."
    ],

    "behavioral": [
        "...",
        "...",
        "...",
        "...",
        "..."
    ]
}}

IMPORTANT

Return ONLY JSON.

Do NOT write explanations.

Do NOT use markdown.

Do NOT use ```json.
"""

    response = ask_llama(prompt)

    try:
        return parse_json(response)

    except Exception as e:

        print("\n========== QUESTION GENERATION FAILED ==========")
        print(e)
        print("\nRAW RESPONSE:")
        print(response)
        print("===============================================\n")

        # Safe fallback questions
        return {
            "technical": [
                "Explain one of the technical skills mentioned in your resume.",
                "Describe a challenging technical problem you have solved.",
                "How would you approach debugging a complex application?"
            ],
            "hr": [
                "Why are you interested in this role?",
                "What motivates you in your career?",
                "Where do you see yourself in the next few years?"
            ],
            "behavioral": [
                "Tell me about a difficult situation you handled.",
                "Describe a time when you worked effectively in a team.",
                "How do you handle feedback or criticism?"
            ]
        }