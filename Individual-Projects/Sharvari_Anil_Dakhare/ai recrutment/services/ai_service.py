"""
Central AI service layer.

Every AI-powered feature in the app (resume matching, ranking, interview
questions, chat, etc.) calls through THIS file instead of hitting an AI
provider directly. That means:

  - one place to swap providers - this file supports BOTH Gemini (cloud)
    and Ollama (runs locally on your machine, free, no daily quota)
  - one place to handle missing keys/servers, quota errors, and bad JSON
  - every page gets the same graceful "AI not configured" fallback UI

Setup - choose ONE provider in your .env file:

  Option A: Gemini (cloud, free tier has a daily request limit)
    1. Get a free API key from https://aistudio.google.com/apikey
    2. In .env:  GEMINI_API_KEY=your_key_here

  Option B: Ollama (runs locally, no quota limits, needs Ollama installed)
    1. Install Ollama from https://ollama.com and pull a model (see README)
    2. In .env:  AI_PROVIDER=ollama
                 OLLAMA_MODEL=llama3.2

Never commit .env or share it - it's already in .gitignore.
"""

import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower().strip()

# --- Gemini settings ---
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-flash-latest"

# --- Ollama settings ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

_client = None


class AIServiceError(Exception):
    """Raised for any AI call failure - missing key, quota, bad response, etc."""
    pass


def is_configured() -> bool:
    """Pages call this to decide whether to show the AI feature or a setup notice."""
    if AI_PROVIDER == "ollama":
        return True  # no key needed; connection is checked at call time
    return bool(API_KEY)


def _get_client():
    global _client
    if not API_KEY:
        raise AIServiceError(
            "No Gemini API key found. Add GEMINI_API_KEY=your_key to a .env "
            "file in the project root, then restart the app."
        )
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=API_KEY)
    return _client


def _call_gemini(prompt: str, temperature: float) -> str:
    """Calls Google's Gemini API. Retries transient server errors before giving up."""
    import time
    last_error = None
    for attempt in range(3):
        try:
            from google.genai import types
            client = _get_client()
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature),
            )
            if not response.text:
                raise AIServiceError("The AI returned an empty response. Try again.")
            return response.text
        except AIServiceError as e:
            last_error = e
            break  # missing key / empty response - retrying won't help
        except Exception as e:
            msg = str(e)
            last_error = e

            if "PerDay" in msg or "RESOURCE_EXHAUSTED" in msg:
                raise AIServiceError(
                    "You've hit the Gemini free tier's daily limit (20 requests/day "
                    "for this model). This resets ~24 hours after your first request "
                    "today - it is NOT a bug. To keep testing today, either wait for "
                    "the reset, enable billing on your Google AI Studio project, or "
                    "switch to Ollama (set AI_PROVIDER=ollama in .env)."
                )

            transient = any(code in msg for code in ["503", "UNAVAILABLE"])
            if transient and attempt < 2:
                time.sleep(1.5 * (attempt + 1))  # brief backoff, then retry
                continue
            break
    raise AIServiceError(f"AI request failed: {last_error}")


def _call_ollama(prompt: str, temperature: float, json_mode: bool = False) -> str:
    """Calls a locally running Ollama server."""
    import requests
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if json_mode:
        payload["format"] = "json"

    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=120)
    except requests.exceptions.ConnectionError:
        raise AIServiceError(
            f"Can't reach Ollama at {OLLAMA_BASE_URL}. Make sure Ollama is installed "
            f"and running - open a terminal and run 'ollama serve', or just open the "
            f"Ollama desktop app."
        )
    except requests.exceptions.Timeout:
        raise AIServiceError("Ollama took too long to respond. Try again, or use a smaller model.")

    if resp.status_code == 404:
        raise AIServiceError(
            f"Model '{OLLAMA_MODEL}' isn't installed. Run: ollama pull {OLLAMA_MODEL}"
        )
    if resp.status_code != 200:
        raise AIServiceError(f"Ollama request failed ({resp.status_code}): {resp.text[:200]}")

    text = resp.json().get("response", "")
    if not text:
        raise AIServiceError("Ollama returned an empty response. Try again.")
    return text


def _call(prompt: str, temperature: float = 0.4, json_mode: bool = False) -> str:
    """Routes to whichever provider is configured in .env (AI_PROVIDER)."""
    if AI_PROVIDER == "ollama":
        return _call_ollama(prompt, temperature, json_mode=json_mode)
    return _call_gemini(prompt, temperature)


def _extract_json(raw: str) -> dict:
    """Some models wrap JSON in ```json fences - strip those before parsing."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned.strip())
    cleaned = re.sub(r"```$", "", cleaned.strip())
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise AIServiceError(f"AI returned malformed JSON: {e}")


def _call_json(prompt: str, temperature: float = 0.3) -> dict:
    full_prompt = (
        prompt.strip()
        + "\n\nRespond with ONLY a valid JSON object. No markdown code fences, "
          "no preamble, no explanation - just the raw JSON."
    )
    raw = _call(full_prompt, temperature=temperature, json_mode=True)
    return _extract_json(raw)


# ---------------------------------------------------------------------------
# Batch 1 features: Job Description tools + Resume Matching
# ---------------------------------------------------------------------------

def extract_jd_requirements(jd_text: str) -> dict:
    """
    Given a raw job description, pull out structured requirements.
    Used by the Job Description Manager's "Extract with AI" button.
    """
    prompt = f"""
You are a recruitment analyst. Read this job description and extract structured data.

Job Description:
\"\"\"{jd_text}\"\"\"

Return a JSON object with exactly these keys:
- "required_skills": list of strings, the must-have technical/functional skills
- "nice_to_have_skills": list of strings, bonus skills mentioned or implied
- "experience_level": one of "Entry", "Mid", "Senior", "Lead" (best guess if not explicit)
- "key_responsibilities": list of 3-5 short strings summarizing core responsibilities
"""
    return _call_json(prompt)


def match_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    """
    Core Resume Matching AI. Compares a candidate resume against a job
    description and returns a structured scoring breakdown.
    """
    prompt = f"""
You are an ATS (Applicant Tracking System) resume screening assistant for a
recruitment platform. Be honest and specific, not generic.

Job Description:
\"\"\"{jd_text}\"\"\"

Candidate Resume:
\"\"\"{resume_text}\"\"\"

Analyze how well this resume matches the job description. Return a JSON
object with exactly these keys:
- "match_score": integer from 0 to 100
- "matched_skills": list of strings - skills/requirements from the JD that ARE present in the resume
- "missing_skills": list of strings - important JD requirements NOT found in the resume
- "strengths": list of 2-4 short strings, specific candidate strengths for this exact role
- "concerns": list of 1-3 short strings, specific gaps or concerns a recruiter should probe in interview
- "summary": a 2-3 sentence recruiter-style summary of overall fit
"""
    return _call_json(prompt)


def parse_resume_profile(resume_text: str) -> dict:
    """
    Extracts structured candidate info (name, contact, experience, education)
    from raw resume text, so the Resume Analyzer page can display real data
    instead of the old hardcoded sample candidate.
    """
    prompt = f"""
Extract structured profile information from this resume text. If a field
isn't present in the resume, use an empty string or empty list - do not
invent information.

Resume:
\"\"\"{resume_text}\"\"\"

Return a JSON object with exactly these keys:
- "name": string
- "email": string
- "phone": string
- "location": string
- "skills": list of strings (all technical/professional skills found)
- "education": list of objects with keys "degree", "school", "year"
- "experience": list of objects with keys "title", "company", "duration", "desc" (desc is one sentence)
- "certifications": list of strings
- "projects": list of strings
"""
    return _call_json(prompt)


# ---------------------------------------------------------------------------
# Batch 2 features: Candidate Ranking, Skill Gap Analysis, Candidate Comparison
# ---------------------------------------------------------------------------

def rank_candidates(candidates: list, jd_text: str) -> dict:
    """
    Ranks a pool of candidates against a job description.
    `candidates` is a list of dicts with at least: name, role, skills (str).
    Returns {"rankings": [{"name": ..., "ai_score": int, "reasoning": str}, ...]}
    ordered best-fit first.
    """
    candidate_lines = "\n".join(
        f"- {c['name']}: applying for {c['role']}, skills: {c['skills']}"
        for c in candidates
    )
    prompt = f"""
You are a recruitment AI ranking candidates for a role.

Job Description:
\"\"\"{jd_text}\"\"\"

Candidates:
{candidate_lines}

Rank ALL of these candidates from best fit to worst fit for this job description.
Return a JSON object with exactly this key:
- "rankings": a list of objects, one per candidate, each with:
    - "name": the candidate's name (must match exactly)
    - "ai_score": integer 0-100, this candidate's fit for the JD
    - "reasoning": one short sentence explaining the score

The list must be sorted best-to-worst by ai_score, and must include every candidate given.
"""
    return _call_json(prompt)


def analyze_skill_gap(candidate: dict, jd_text: str) -> dict:
    """
    Compares a single candidate's skills against a JD and returns what's
    missing plus concrete upskilling suggestions.
    """
    prompt = f"""
You are a talent development advisor. Compare this candidate's current
skills against what the target role requires.

Job Description:
\"\"\"{jd_text}\"\"\"

Candidate: {candidate['name']}, current role applied for: {candidate['role']}
Current skills: {candidate['skills']}

Return a JSON object with exactly these keys:
- "readiness_level": one of "Ready", "Needs Development", "Not Ready"
- "gap_skills": list of strings - skills required by the JD that the candidate is missing
- "existing_strengths": list of 2-4 strings - skills the candidate already has that matter for this role
- "recommendations": list of objects, one per gap skill, each with:
    - "skill": string
    - "suggestion": one short sentence on how to close this gap (course type, project idea, certification, etc.)
- "summary": 2-3 sentence overall readiness summary
"""
    return _call_json(prompt)


def compare_candidates(candidates: list, jd_text: str) -> dict:
    """
    Head-to-head comparison of 2-3 candidates for the same role.
    """
    candidate_lines = "\n".join(
        f"- {c['name']}: role {c['role']}, skills: {c['skills']}, current match score: {c['match']}%"
        for c in candidates
    )
    prompt = f"""
You are a recruitment AI helping a hiring manager choose between finalist
candidates for the same role.

Job Description:
\"\"\"{jd_text}\"\"\"

Candidates being compared:
{candidate_lines}

Return a JSON object with exactly these keys:
- "comparisons": list of objects, one per candidate, each with:
    - "name": string (must match exactly)
    - "pros": list of 2-3 short strings
    - "cons": list of 1-2 short strings
- "recommended": the name of the single best candidate for this role
- "recommendation_reason": 2-3 sentence explanation of why that candidate is the best choice
"""
    return _call_json(prompt)



# ---------------------------------------------------------------------------
# Batch 3 features: Interview Questions, Resume Chat, AI Email Generator
# ---------------------------------------------------------------------------

def generate_interview_questions(candidate_name: str, role: str, question_type: str, jd_text: str = "") -> dict:
    """
    Generates tailored interview questions for a candidate/role/round type.
    question_type is one of "Technical", "HR Questions", "Coding".
    """
    jd_context = f"\n\nRelevant job description for context:\n\"\"\"{jd_text}\"\"\"" if jd_text else ""
    prompt = f"""
You are an experienced technical recruiter preparing interview questions.

Candidate: {candidate_name}
Role: {role}
Round type: {question_type}{jd_context}

Generate 5 strong, specific interview questions appropriate for a "{question_type}"
round for this role. Avoid generic questions - make them relevant to the role.

Return a JSON object with exactly this key:
- "questions": list of 5 strings
"""
    return _call_json(prompt)


def resume_chat(resume_text: str, jd_text: str, history: list, question: str) -> str:
    """
    Conversational Q&A about a specific candidate's resume.
    `history` is a list of {"role": "user"|"assistant", "content": str} from
    earlier turns in this session, used to keep the conversation coherent.
    Returns a plain-text answer (not JSON).
    """
    history_text = "\n".join(
        f"{'Recruiter' if h['role'] == 'user' else 'Assistant'}: {h['content']}"
        for h in history[-6:]  # keep last few turns to bound prompt size
    )
    prompt = f"""
You are a recruiting assistant answering a recruiter's questions about ONE
specific candidate's resume. Only use information present in the resume
below - if something isn't in the resume, say so honestly instead of
guessing.

Job Description (for context):
\"\"\"{jd_text}\"\"\"

Candidate Resume:
\"\"\"{resume_text}\"\"\"

Conversation so far:
{history_text}

Recruiter's new question: {question}

Answer concisely and directly, in 2-4 sentences, as the recruiting assistant.
"""
    return _call(prompt, temperature=0.3).strip()


def generate_email(candidate_name: str, role: str, email_type: str, tone: str = "Professional", extra_context: str = "") -> str:
    """
    Drafts a recruiter email. email_type is one of:
    "Interview Invitation", "Rejection", "Offer Letter".
    Returns plain text (with a Subject: line), not JSON.
    """
    context_line = f"\nAdditional context: {extra_context}" if extra_context else ""
    prompt = f"""
You are a recruiter writing a {email_type} email to a candidate.

Candidate: {candidate_name}
Role: {role}
Tone: {tone}{context_line}

Write a complete, ready-to-send email. Start with a line "Subject: ..." then
a blank line, then the email body. Keep it warm but professional, concise
(under 150 words for the body), and appropriate for a {email_type.lower()} email.
Do not use placeholder brackets like [Your Name] - sign off as "The Recruitment Team".
"""
    return _call(prompt, temperature=0.5).strip()


# ---------------------------------------------------------------------------
# Batch 4 features: Talent Insight, Talent Analyzer, Hiring Recommendation,
# Recruitment Analysis, Report Generator
# ---------------------------------------------------------------------------

def talent_insight_summary(candidate_summary: str, kpi_summary: str) -> dict:
    """
    High-level narrative insights about the current talent pool and hiring
    funnel. Powers the "AI Hiring Summary" section on Hiring Analytics.
    """
    prompt = f"""
You are a talent intelligence AI for a recruitment platform's analytics dashboard.

Current candidate pool:
{candidate_summary}

Hiring KPIs:
{kpi_summary}

Return a JSON object with exactly these keys:
- "insights": list of 4-6 short strings, specific and data-grounded observations
  about the talent pool and hiring performance (not generic advice)
- "summary": one 2-sentence executive summary
"""
    return _call_json(prompt)


def analyze_talent_pool(candidate_summary: str) -> dict:
    """
    Structured breakdown of the current candidate pool: skill coverage,
    department distribution, and where the pool is strong/weak.
    """
    prompt = f"""
You are a talent analytics AI. Analyze this candidate pool structurally.

Candidate pool:
{candidate_summary}

Return a JSON object with exactly these keys:
- "top_skills": list of the 5 most common skills across the pool, each an object with "skill" and "count"
- "department_breakdown": list of objects with "department" and "count"
- "strongest_area": one short string - what this pool is strongest in
- "weakest_area": one short string - the clearest gap in this pool
- "summary": 2-3 sentence overall assessment of pool health
"""
    return _call_json(prompt)


def hiring_recommendation(jd_text: str, candidate_summary: str) -> dict:
    """
    For a specific open role, recommends which current-pool candidates to
    prioritize and whether more sourcing is needed.
    """
    prompt = f"""
You are a hiring strategy AI advising a recruiter on how to fill an open role.

Job Description:
\"\"\"{jd_text}\"\"\"

Current candidates in the pipeline (may or may not be relevant to this role):
{candidate_summary}

Return a JSON object with exactly these keys:
- "recommended_candidates": list of objects (0-5 items, only include genuinely relevant candidates) with:
    - "name": string
    - "reason": one short sentence on why to prioritize them
- "should_source_more": boolean - true if the current pool is insufficient for this role
- "sourcing_suggestion": one short sentence on where/how to find more candidates if needed (empty string if should_source_more is false)
- "overall_recommendation": 2-3 sentence overall hiring strategy for this role
"""
    return _call_json(prompt)


def recruitment_process_analysis(funnel_summary: str, kpi_summary: str) -> dict:
    """
    Analyzes the recruitment funnel/process itself for bottlenecks and
    strengths - not about individual candidates.
    """
    prompt = f"""
You are a recruitment operations AI analyzing hiring process efficiency.

Funnel data:
{funnel_summary}

KPIs:
{kpi_summary}

Return a JSON object with exactly these keys:
- "bottlenecks": list of 2-3 short strings identifying specific stages or metrics that are underperforming
- "strengths": list of 2-3 short strings identifying what's working well
- "recommendations": list of 3-4 short, actionable strings to improve the process
- "summary": 2-3 sentence overall process health assessment
"""
    return _call_json(prompt)


def generate_hiring_report(context: str) -> str:
    """
    Synthesizes everything into one downloadable markdown report.
    Returns plain markdown text, not JSON.
    """
    prompt = f"""
You are a recruitment analytics AI writing an executive hiring report for a
Talent Acquisition leader.

Context and data to synthesize:
{context}

Write a complete, well-structured report in Markdown with these sections:
# Hiring Report
## Executive Summary
## Talent Pool Overview
## Recruitment Process Health
## Key Recommendations

Keep it concise, data-grounded, and free of filler. Do not invent numbers
that weren't given to you - only reason over what's in the context above.
"""
    return _call(prompt, temperature=0.4).strip()


# ---------------------------------------------------------------------------
# Performance Review AI Assistant (Talent Management / Candidate Screening)
# ---------------------------------------------------------------------------

def generate_performance_review(employee: dict) -> dict:
    """
    Powers the Performance Review AI Assistant in Talent Management
    (Candidate Screening page). Generates a structured performance review
    for one employee: summary, strengths, improvement areas, training/
    career recommendations, and a ready-to-use manager comment.

    `employee` needs: name, role, department, experience (years),
    performance_rating (0-5), skills, stage.
    """
    prompt = f"""
You are an HR performance management AI helping a manager prepare a
performance review for an employee.

Employee: {employee['name']}
Designation: {employee['role']}
Department: {employee['department']}
Experience: {employee['experience']} years
Current performance rating: {employee['performance_rating']} / 5
Current stage/status: {employee['stage']}
Skills: {employee['skills']}

Return a JSON object with exactly these keys:
- "summary": 2-4 sentence overall performance summary, grounded in the
  rating and experience given above (don't invent specific incidents or
  numbers not implied by the data above)
- "strengths": list of 3-5 short strings - concrete strengths based on
  their skills, role, and rating
- "improvement_areas": list of 2-4 short strings - realistic areas to
  develop, phrased constructively (not harsh)
- "training_recommendations": list of objects, each with:
    - "area": string (a skill or competency area)
    - "recommendation": one short sentence (course type, certification,
      project, or mentorship idea)
- "career_growth": 2-3 sentences suggesting a plausible next step or
  growth path for someone at this level and department
- "manager_comment": a polished, professional paragraph (4-6 sentences)
  written in a manager's voice, suitable to paste directly into a formal
  performance review document
"""
    return _call_json(prompt)


# ---------------------------------------------------------------------------
# Global AI Assistant - floating chat available on every page
# ---------------------------------------------------------------------------

def global_assistant_chat(history: list, question: str) -> str:
    """
    Powers the floating Global AI Assistant available on every page (see
    components/global_chat.py). Acts as a direct-answer HR/recruitment
    copilot - interview questions, performance review frameworks, resume
    screening criteria, hiring-funnel/analytics interpretation, job
    description feedback, HR policy guidance, etc. Not tied to one specific
    candidate/JD like resume_chat() is - this is the app-wide helper.

    `history` is a list of {"role": "user"|"assistant", "content": str}
    from earlier turns in this session. Returns a plain-text answer.
    """
    history_text = "\n".join(
        f"{'User' if h['role'] == 'user' else 'Assistant'}: {h['content']}"
        for h in history[-8:]  # keep last few turns to bound prompt size
    )
    prompt = f"""
You are the built-in AI HR Assistant for YourTalentPilot, an AI
recruitment/talent-management platform. You act as an expert HR and
recruiting copilot, not a help desk - always answer the question directly
and completely yourself in this response.

You can be asked to:
- Write or suggest interview questions (behavioral, technical, situational)
  for a given role, seniority, or skill
- Draft or structure performance reviews and feedback
- Give resume/candidate screening criteria, red flags, or scoring rubrics
- Explain or interpret hiring-funnel and recruiting-analytics metrics
  (time-to-hire, offer-acceptance rate, source quality, drop-off stages,
  etc.) and recommend improvements
- Give job description feedback or suggest improved wording
- Answer general HR, recruiting, and people-management best-practice
  questions
- Explain how a feature of this app works conceptually

Always give the real, usable answer in the response itself - actual
interview questions, an actual rubric, an actual summary or
recommendation, etc. Never reply with only an instruction to "go to this
page" / "use this feature" / "check the X page" as if that were the whole
answer. It is fine to mention a relevant page in passing (e.g. "you can
save this list from the Interview Copilot page") only AFTER you've already
given the full, useful answer - never instead of it.

You do NOT have live access to this session's actual candidate, job, or
analytics data. When asked about specific numbers or records you can't
see, don't invent them - instead give the best general-purpose answer you
can (a template, framework, typical benchmark range, or worked example
with placeholder data clearly marked as illustrative), so the user still
gets something immediately usable.

SCOPE: You only answer questions about recruitment, hiring, talent
management, HR practices, and this app. If the user's message is unrelated
to those topics (e.g. general trivia, coding help, politics, entertainment,
personal advice unrelated to work), politely decline in 1-2 sentences and
steer them back to what you can help with. Do not answer the off-topic
question itself.

Conversation so far:
{history_text}

User's new message: {question}

Reply directly and completely. Use short paragraphs or lists/numbered
steps for anything structured (like interview questions or a rubric).
Don't pad with filler, don't repeat the user's question back to them, and
don't end with a generic "let me know if you need more help" unless it
adds something specific.
"""
    return _call(prompt, temperature=0.4).strip()


# ---------------------------------------------------------------------------
# Interview Management (Module 7): AI Candidate Summary + AI Feedback
# Generator. Same _call_json() pattern as every function above.
# ---------------------------------------------------------------------------

def generate_candidate_summary(candidate_name: str, resume_text: str, role: str) -> dict:
    """
    Powers the Interview Management "AI Candidate Summary" panel: skills,
    projects, experience, and a short resume summary, in one call - so
    the interviewer sees everything before walking into the room.
    """
    prompt = f"""
You are a recruitment AI preparing a quick candidate briefing for an
interviewer, right before an interview.

Candidate: {candidate_name}
Role: {role}

Resume:
\"\"\"{resume_text[:6000]}\"\"\"

Return a JSON object with exactly these keys:
- "skills": list of strings - key technical/professional skills found in the resume
- "projects": list of 2-4 strings - notable projects or achievements found (or reasonably inferred)
- "experience_summary": one sentence describing their overall experience level and background
- "resume_summary": 2-3 sentence plain-English summary of this candidate, written for an interviewer
  who has 30 seconds to read it before the interview starts
"""
    return _call_json(prompt)


def generate_interview_feedback(candidate_name: str, role: str, round_name: str, hr_notes: str) -> dict:
    """
    AI Feedback Generator: turns the interviewer's live notes into a
    structured scorecard. Powers the "Conduct & Feedback" step of
    Interview Management.
    """
    prompt = f"""
You are a recruitment AI turning an interviewer's raw notes into a
structured interview scorecard.

Candidate: {candidate_name}
Role: {role}
Interview Round: {round_name}

Interviewer's raw notes:
\"\"\"{hr_notes}\"\"\"

Return a JSON object with exactly these keys:
- "technical_score": integer 0-100 - technical competence shown, based on the notes
- "communication_score": integer 0-100 - communication/clarity shown, based on the notes
- "strengths": list of 2-4 short strings
- "weaknesses": list of 1-3 short strings
- "recommendation": one of "Proceed to Next Round", "Select", "Hold", "Reject"
- "summary": 2-3 sentence overall assessment of this round
"""
    return _call_json(prompt)


def generate_document_verification_summary(doc_type: str, extracted_text: str) -> dict:
    """
    AI Document Verification (Section I): given OCR/extracted text from an
    uploaded document and its claimed type (Aadhaar, PAN, Degree,
    Experience Certificate, Payslip), checks whether the content is
    plausibly consistent with that document type.

    This is a plausibility check on the extracted text, not a legal or
    biometric identity verification - always surfaced to HR as a
    recommendation to double-check, not an automatic pass/fail.
    """
    prompt = f"""
You are a document verification assistant for an HR onboarding system.
You are checking whether extracted text plausibly matches the claimed
document type - you cannot verify authenticity, only content consistency.

Claimed document type: {doc_type}

Extracted text from the document:
\"\"\"{extracted_text[:4000]}\"\"\"

Return a JSON object with exactly these keys:
- "status": one of "Verified", "Needs Review", "Mismatch" - "Verified" only
  if the text clearly contains content consistent with a {doc_type}
  (e.g. relevant ID numbers, institution names, employer names, amounts -
  whatever is typical for this document type); "Mismatch" if the content
  clearly looks like a different document type; "Needs Review" otherwise
- "findings": list of 2-4 short strings - specific things found (or
  missing) that inform the status
- "summary": 1-2 sentence plain-English verification summary for HR
"""
    return _call_json(prompt)