import json
import re
import requests

# ==========================================================
# CONFIGURATION
# ==========================================================

MODEL = "llama3.2"

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

REQUEST_TIMEOUT = 300

MAX_RETRIES = 2


# ==========================================================
# RECRUITMENT DOMAIN
# ==========================================================

RECRUITMENT_KEYWORDS = {

    "resume",
    "cv",
    "candidate",
    "job",
    "job description",
    "jd",
    "hiring",
    "hire",
    "recruitment",
    "recruit",
    "recruiter",
    "talent",
    "employee",
    "employment",
    "interview",
    "screening",
    "screen",
    "skill",
    "skills",
    "experience",
    "education",
    "college",
    "degree",
    "certification",
    "project",
    "developer",
    "engineer",
    "python",
    "java",
    "react",
    "node",
    "ai",
    "machine learning",
    "full stack",
    "frontend",
    "backend",
    "salary",
    "offer",
    "notice period",
    "cgpa",
    "internship",

    # Short-form commands/verbs commonly used in resume/HR chat context
    # (e.g. "Summarize", "Skills" typed alone). Without these, a valid
    # follow-up question about the uploaded resume could be wrongly
    # rejected just because it doesn't repeat the word "resume" itself.
    "summarize",
    "summary",
    "strength",
    "strengths",
    "weakness",
    "weaknesses",
    "improve",
    "improvement",
    "suitable",
    "fit",
    "qualified",
    "qualification",
    "qualifications",
    "evaluate",
    "evaluation",
    "assess",
    "assessment",
    "rank",
    "ranking",
    "compare",
    "comparison",
    "shortlist",
    "score",
    "match",
    "matching",
    "role",
    "position",
    "vacancy",
    "onboarding",
    "kpi",
    "kpis",
    "bias",
    "star method",
    "recommend",
    "recommendation"
}


# ==========================================================
# RESPONSE CLEANER
# ==========================================================

def clean_response(text):

    if not text:

        return ""

    text = text.strip()

    # Remove markdown code fences

    text = re.sub(

        r"^```(?:json)?",

        "",

        text,

        flags=re.IGNORECASE

    )

    text = re.sub(

        r"```$",

        "",

        text

    )

    # Remove extra blank lines

    text = re.sub(

        r"\n{2,}",

        "\n",

        text

    )

    return text.strip()


# ==========================================================
# VALIDATE USER PROMPT
# ==========================================================

def validate_prompt(prompt):

    lower = prompt.lower()

    return any(

        keyword in lower

        for keyword in RECRUITMENT_KEYWORDS

    )


# ==========================================================
# GLOBAL SYSTEM PROMPT
# ==========================================================

def build_system_prompt(json_mode: bool = False, strict_scope: bool = True):
    """
    strict_scope controls whether the "never invent / use only the
    provided candidate data" rules are included.

    These rules are correct and necessary for functions that operate
    on a specific candidate/JD (ask_ai_json, ask_ai_jd_analysis,
    ask_ai_questions) — keep strict_scope=True (the default) there.

    They are WRONG for the free-form conversational assistant
    (ai_hr_assistant.py / ask_ai with strict_scope=False), because
    they conflict with legitimate general knowledge questions like
    "what skills are required for an AI engineer" that aren't about
    any uploaded resume at all. With a small local model (llama3.2),
    that conflict between "use only provided info" and "answer
    general questions normally" reliably caused refusals or empty
    output. When strict_scope=False, those rules are dropped and
    replaced with an explicit instruction that draws the line at the
    "is this about the specific candidate?" question instead.
    """

    base = """
You are an expert AI Recruitment and Talent Management Assistant.

Your responsibilities include:

- Resume Screening
- Resume Matching
- Job Description Analysis
- Candidate Ranking
- Hiring Recommendations
- Interview Question Generation
- Talent Management
- General Recruitment, Hiring, and HR Knowledge (e.g. what skills a
  role typically requires, interview best practices, HR policy
  questions) even when no resume or job description has been
  provided

Rules:

1. Answer ONLY recruitment, hiring, and talent management related
   queries (this includes general questions like "what skills does
   an AI engineer need", not just questions about an uploaded
   resume).

2. Never answer unrelated topics like:
   - Movies
   - Sports
   - Politics
   - Cooking
   - Mathematics
   - General Chat
""".strip()

    if strict_scope:

        base += """

3. Never invent information.

4. Never fabricate candidate details.

5. Use only the information provided.

6. Internship is NOT professional experience.

7. Academic projects are NOT work experience.

8. Personal projects are NOT work experience.

9. Certifications are NOT work experience.

10. If candidate_type or experience_years are already provided,
    NEVER recalculate them.

11. Base recommendations on:

- Skills
- Education
- Projects
- Certifications
- Experience
- Resume Quality
- Job Description

12. If information is missing,
return the best recommendation using only available data.
"""

    else:

        base += """

3. The "never invent, use only provided info" rule applies ONLY when
   the recruiter is asking about a specific uploaded candidate or
   job description. In that case, do not invent or assume any
   experience, skills, education, certifications, or projects that
   are not explicitly present in the provided text.

4. If the recruiter asks a general recruitment/HR/technical
   question that is NOT about a specific uploaded candidate (e.g.
   "what skills are required for a backend engineer", "how do I
   structure a panel interview"), answer it fully and normally using
   your own expert knowledge, even if a resume happens to be loaded
   in the conversation. Do not refuse or redirect such questions to
   the resume.
"""

    # The "return ONLY valid JSON, no markdown/prose" instruction must
    # NOT be baked in unconditionally — when it was always present,
    # Llama 3.2 kept pattern-matching to it even for plain conversational
    # chat prompts (e.g. the AI HR Assistant), turning ordinary answers
    # into raw JSON blobs. Only append it when the caller actually wants
    # structured JSON output.
    if json_mode:

        base += """

13. When returning JSON:

Return ONLY valid JSON.

Do not include markdown.

Do not include explanations.

Do not include extra text.
"""

    return base.strip()
# ==========================================================
# BASIC AI FUNCTION
# ==========================================================

def ask_ai(prompt: str, json_mode: bool = False, strict_scope: bool = True) -> str:
    """
    Sends a prompt to Ollama.

    Features:
    - Recruitment-only validation
    - Global system prompt
    - Automatic retries
    - Response cleaning
    - Stable generation settings
    - Optional JSON-constrained decoding (format="json") for callers
      that need structured output (JD analysis, resume matching,
      interview questions). This is OPT-IN via json_mode=True — it
      must NOT be the default, because free-form chat callers (like
      the AI HR Assistant) need normal Markdown prose back, not a
      raw JSON blob.
    - strict_scope (default True): passed through to
      build_system_prompt(). Set False for free-form conversational
      callers (e.g. the AI HR Assistant chat) so general recruitment/
      HR questions ("skills required for an AI engineer") aren't
      blocked by the "use only the provided candidate data" rules
      that are meant for candidate/JD-specific extraction calls.
    """

    if not prompt.strip():

        return "Error: Empty prompt."

    # Skip validation for internal resume/JD prompts
    if not (
        "Candidate Information" in prompt
        or "Resume" in prompt
        or "Job Description" in prompt
        or "JD" in prompt
    ):

        if not validate_prompt(prompt):

            return (
                "Error: This AI Assistant supports only "
                "Recruitment and Talent Management queries."
            )

    full_prompt = f"""

{build_system_prompt(json_mode=json_mode, strict_scope=strict_scope)}

==================================================

{prompt}

"""

    payload = {

        "model": MODEL,

        "prompt": full_prompt,

        "stream": False,

        "options": {

            "temperature": 0.15,

            "top_p": 0.90,

            "top_k": 40,

            "repeat_penalty": 1.20,

            "num_predict": 3072,

            # Ollama defaults to a 2048-token context window if this
            # isn't set. A system prompt + a full resume + a question
            # can easily exceed that, silently truncating content and
            # degrading/emptying the response. Give it real headroom.
            "num_ctx": 8192

        }

    }

    if json_mode:
        payload["format"] = "json"

    last_error = "Unknown Error"

    for _ in range(MAX_RETRIES):

        try:

            response = requests.post(

                OLLAMA_URL,

                json=payload,

                timeout=REQUEST_TIMEOUT

            )

            response.raise_for_status()

            data = response.json()

            answer = clean_response(

                data.get("response", "")

            )

            if answer:

                return answer

            # Log the raw payload so an empty response is debuggable
            # from the terminal instead of just silently disappearing.
            print(f"[ask_ai] Empty response. Raw data was: {data}")

            last_error = "Empty AI response."

        except requests.exceptions.Timeout:

            last_error = "Ollama request timed out."

        except requests.exceptions.ConnectionError:

            last_error = (
                "Cannot connect to Ollama. "
                "Please make sure Ollama is running."
            )

        except requests.exceptions.HTTPError as e:

            last_error = f"HTTP Error: {e}"

        except Exception as e:

            last_error = str(e)

    return f"Error: {last_error}"
# ==========================================================
# RESUME MATCHING / JD ANALYSIS
# ==========================================================

def ask_ai_json(prompt: str):
    """
    Returns structured JSON for Resume Matching,
    Candidate Ranking and JD Analysis.

    IMPORTANT: on failure this now returns a dict that clearly says
    *why* it failed (Ollama unreachable, malformed JSON, etc.) instead
    of generic placeholder text like "No summary generated." — that
    made every failure look identical and impossible to diagnose from
    the UI alone. The raw model output is also printed to the console
    so you can see exactly what Ollama returned.
    """

    system_prompt = f"""
{build_system_prompt(json_mode=True)}

Analyze the candidate carefully.

IMPORTANT RULES:

1. If Candidate Type is already provided,
   NEVER change it.

2. If Experience Years is already provided,
   NEVER calculate it again.

3. Internship is NOT professional experience.

4. Academic projects are NOT work experience.

5. Personal projects are NOT work experience.

6. Certifications are NOT work experience.

7. Match the candidate only against
   the provided Job Description.

8. Evaluate using:

- Skills
- Education
- Projects
- Certifications
- Experience
- Resume Quality
- Job Description

9. Give realistic scores.

Score Guide:

90-100 = Excellent Match

75-89 = Good Match

60-74 = Average Match

40-59 = Weak Match

Below 40 = Poor Match

Return ONLY valid JSON.

Required JSON format:

{{
    "match_score": 0,
    "recommended_role": "",
    "missing_skills": [],
    "strengths": [],
    "weaknesses": [],
    "skill_gap_analysis": "",
    "summary": "",
    "hiring_recommendation": ""
}}

Candidate Information:

{prompt}
"""

    response = ask_ai(system_prompt, json_mode=True)

    response = clean_response(response)

    # ask_ai() itself failed (Ollama unreachable, timeout, empty
    # response, etc). Surface that real reason instead of masking it
    # with generic placeholder text.
    if response.startswith("Error:"):

        print(f"[ask_ai_json] ask_ai() failed: {response}")

        return {

            "match_score": 0,

            "recommended_role": "Not Specified",

            "missing_skills": [],

            "strengths": [],

            "weaknesses": [],

            "skill_gap_analysis": response,

            "summary": response,

            "hiring_recommendation": "Needs Manual Review",

            "ai_error": True

        }

    try:

        start = response.find("{")
        end = response.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON object found in AI response.")

        data = json.loads(response[start:end])

        score = data.get("match_score", 0)

        try:
            score = int(score)
        except (TypeError, ValueError):
            score = 0

        score = max(0, min(score, 100))

        return {

            "match_score": score,

            "recommended_role":

                str(
                    data.get(
                        "recommended_role",
                        "Not Specified"
                    )
                ),

            "missing_skills":

                data.get(
                    "missing_skills",
                    []
                ),

            "strengths":

                data.get(
                    "strengths",
                    []
                ),

            "weaknesses":

                data.get(
                    "weaknesses",
                    []
                ),

            "skill_gap_analysis":

                str(
                    data.get(
                        "skill_gap_analysis",
                        ""
                    )
                ),

            "summary":

                str(
                    data.get(
                        "summary",
                        ""
                    )
                ),

            "hiring_recommendation":

                str(
                    data.get(
                        "hiring_recommendation",
                        "Consider"
                    )
                ),

            "ai_error": False

        }

    except Exception as e:

        # Log the raw, unparsed response so it's visible in the
        # terminal running Streamlit — this is the actual text Ollama
        # sent back, which is essential for figuring out why JSON
        # parsing failed (e.g. model added commentary, truncated
        # output, wrong format entirely).
        print(f"[ask_ai_json] JSON parse failed: {e}")
        print(f"[ask_ai_json] Raw response was:\n{response}")

        return {

            "match_score": 0,

            "recommended_role": "Not Specified",

            "missing_skills": [],

            "strengths": [],

            "weaknesses": [],

            "skill_gap_analysis":

                "AI response could not be parsed as JSON. "
                "Check the terminal running Streamlit for the raw "
                "model output.",

            "summary":

                "AI response could not be parsed as JSON. "
                "Check the terminal running Streamlit for the raw "
                "model output.",

            "hiring_recommendation": "Needs Manual Review",

            "ai_error": True

        }
# ==========================================================
# JOB DESCRIPTION ANALYZER
# ==========================================================

def _looks_like_title_only(text: str) -> bool:
    """
    Heuristic: distinguishes a bare role/title ("AI Engineer", "SDE",
    "Backend Developer - II") typed into the box from an actual pasted
    Job Description.

    A real JD is virtually always multiple sentences/bullets long. A
    title is short and has no sentence punctuation, newlines, or
    bullet markers. This intentionally errs on the side of treating
    ambiguous-but-short input as a title, since the extraction-only
    prompt path produces near-empty results for anything that isn't a
    real JD, while the generation path below still behaves correctly
    even if given a short JD fragment (it just leans a bit more on
    general knowledge to fill gaps).
    """

    stripped = text.strip()

    if not stripped:
        return False

    if len(stripped.split()) > 6:
        return False

    if any(ch in stripped for ch in ".\n•:;"):
        return False

    return True


def ask_ai_jd_analysis(job_description: str):
    """
    Returns structured JSON analysis of a job description.

    Uses strict JSON output instead of a free-text template, because
    free-text templates only parse correctly when the model's output
    happens to match the exact line-by-line format expected — any
    reordering (a heading and its content landing on the same line, a
    bullet appearing where a heading was expected, etc.) silently
    misfiles content into the wrong section instead of failing loudly.
    JSON with named keys doesn't have that failure mode.

    Handles two different kinds of input:

    - A full pasted/uploaded Job Description -> extraction-only mode.
      The model must extract facts strictly from the given text and
      must not invent anything not present in it.

    - Just a role/title typed in (e.g. "AI Engineer", "SDE") -> there
      is no JD text to extract from, so extraction-only rules would
      correctly leave every field empty, which looked to users like
      "analysis doesn't work when I type a role". Instead, generate a
      realistic, typical analysis for that role using general
      recruitment/industry knowledge, while still pinning job_title to
      exactly what was typed.
    """

    title_only = _looks_like_title_only(job_description)

    if title_only:

        role_text = job_description.strip()

        system_prompt = f"""
{build_system_prompt(json_mode=True, strict_scope=False)}

The recruiter has typed only a job TITLE/ROLE ("{role_text}"), not a
full job description. There is no job description text to extract
from.

Using your general recruitment and industry knowledge, generate a
realistic, typical Job Description analysis for this role, as it is
commonly defined in real-world job postings today.

IMPORTANT RULES:

1. The "job_title" field must be exactly "{role_text}" — do not
   rename, expand, or reinterpret it into a different role.
2. Populate every field below with realistic, typical values for this
   role based on common industry job postings. Do not leave a field
   empty just because no JD text was pasted — use your general
   knowledge of what this role typically requires.
3. For "important_keywords": list at least 5 distinct technologies,
   tools, frameworks, languages, platforms, or certifications commonly
   associated with this role.
4. For "key_responsibilities": list the duties/tasks this role
   typically involves.
5. Degree requirements belong in "education", not
   "preferred_qualifications".

Return ONLY valid JSON, in exactly this shape:

{{
    "job_title": "",
    "summary": "",
    "required_skills": [],
    "experience_required": "",
    "education": "",
    "key_responsibilities": [],
    "preferred_qualifications": [],
    "important_keywords": []
}}

Note: "summary" must always be a non-empty 1-2 sentence overview of the
role. Do not leave summary blank.

Job Description / Role:

{job_description}
"""

        response = ask_ai(system_prompt, json_mode=True, strict_scope=False)

    else:

        system_prompt = f"""
{build_system_prompt(json_mode=True)}

You are analyzing a Job Description. Extract information ONLY from
the text provided below.

IMPORTANT RULES:

1. Do not change the job role.
2. Do not invent another role.
3. Do not generate a different Job Description.
4. Extract information only from the input text.
5. If the input names a specific role (e.g. "Backend Engineer"), the
   job_title field must use that exact role, not a different one.
6. Only use an empty string ("") or empty list ([]) if the information
   is genuinely absent from the text after careful reading. Do not
   leave a field empty just because it takes more effort to extract —
   read the ENTIRE job description before deciding a field is empty.
7. For "important_keywords": read the entire text and list ALL
   distinct technologies, tools, frameworks, languages, platforms,
   and certifications mentioned anywhere in the JD — including ones
   you already listed under required_skills or
   preferred_qualifications. Aim for at least 5 keywords if the JD
   mentions that many.
8. For "key_responsibilities": list every duty or task mentioned in
   the JD, even briefly-mentioned ones. Do not summarize multiple
   responsibilities into one bullet.
9. Degree requirements (e.g. "Bachelor's degree in Computer Science",
   "Master's in AI") ALWAYS belong in the "education" field — even if
   the source text lists them under a "Preferred Qualifications"
   heading. Do not duplicate degree text inside
   "preferred_qualifications"; only non-degree items (certifications,
   specific tool/cloud knowledge, prior project experience, etc.)
   belong there.

Return ONLY valid JSON, in exactly this shape:

{{
    "job_title": "",
    "summary": "",
    "required_skills": [],
    "experience_required": "",
    "education": "",
    "key_responsibilities": [],
    "preferred_qualifications": [],
    "important_keywords": []
}}

Note: "summary" must always be a non-empty 1-2 sentence overview of the
role, even if some other fields end up empty due to missing input
detail. Do not leave summary blank.

Job Description:

{job_description}
"""

        response = ask_ai(system_prompt, json_mode=True)
    response = clean_response(response)

    if response.startswith("Error:"):

        print(f"[ask_ai_jd_analysis] ask_ai() failed: {response}")

        return {

            "job_title": "",
            "required_skills": [],
            "experience_required": "",
            "education": "",
            "key_responsibilities": [],
            "preferred_qualifications": [],
            "important_keywords": [],
            "summary": response,
            "ai_error": True

        }

    try:

        start = response.find("{")
        end = response.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON object found in AI response.")

        data = json.loads(response[start:end])

        def _as_list(value):
            if isinstance(value, list):
                return [str(v).strip() for v in value if str(v).strip()]
            return []

        required_skills = _as_list(data.get("required_skills"))
        preferred_qualifications = _as_list(data.get("preferred_qualifications"))
        important_keywords = _as_list(data.get("important_keywords"))
        education = str(data.get("education", "")).strip()

        # Fallback: if the model filed a degree requirement under
        # preferred_qualifications instead of education (common when
        # the source JD itself lists the degree under a "Preferred
        # Qualifications" heading), pull it out and use it as the
        # education value, removing it from preferred_qualifications
        # so it isn't shown twice.
        if not education and preferred_qualifications:

            degree_pattern = re.compile(
                r"\b(bachelor|master|b\.?tech|b\.?e\.?|m\.?tech|"
                r"phd|degree|diploma)\b",
                re.IGNORECASE
            )

            degree_items = [
                item for item in preferred_qualifications
                if degree_pattern.search(item)
            ]

            if degree_items:
                education = "; ".join(degree_items)
                preferred_qualifications = [
                    item for item in preferred_qualifications
                    if item not in degree_items
                ]

        # Fallback: if the model left important_keywords empty despite
        # the prompt rules, derive a reasonable list from the skills
        # fields instead of showing "Not specified." in the UI.
        if not important_keywords:
            important_keywords = list(dict.fromkeys(
                required_skills + preferred_qualifications
            ))

        return {

            "job_title": str(data.get("job_title", "")).strip(),

            "required_skills": required_skills,

            "experience_required": str(data.get("experience_required", "")).strip(),

            "education": education,

            "key_responsibilities": _as_list(data.get("key_responsibilities")),

            "preferred_qualifications": preferred_qualifications,

            "important_keywords": important_keywords,

            "summary": str(data.get("summary", "")).strip(),

            "ai_error": False

        }

    except Exception as e:

        print(f"[ask_ai_jd_analysis] JSON parse failed: {e}")
        print(f"[ask_ai_jd_analysis] Raw response was:\n{response}")

        return {

            "job_title": "",
            "required_skills": [],
            "experience_required": "",
            "education": "",
            "key_responsibilities": [],
            "preferred_qualifications": [],
            "important_keywords": [],
            "summary":
                "AI response could not be parsed as JSON. "
                "Check the terminal running Streamlit for the raw "
                "model output.",
            "ai_error": True

        }
# ==========================================================
# INTERVIEW QUESTION GENERATOR
# ==========================================================

def ask_ai_questions(role, level, qtype):
    """
    Generate exactly 5 interview questions.

    Returns:
        List[str]
    """

    system_prompt = f"""
{build_system_prompt(json_mode=True)}

Generate interview questions only.

Role:
{role}

Experience Level:
{level}

Question Type:
{qtype}

Rules:

1. Generate EXACTLY 5 questions.

2. Questions should match the candidate's experience level.

3. Do NOT provide:

- Answers
- Hints
- Explanations
- Evaluation Criteria
- Difficulty Labels
- Notes

4. Questions should be realistic and commonly asked by recruiters.

5. Return ONLY valid JSON.

Format:

{{
    "questions":[
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5"
    ]
}}
"""

    response = ask_ai(system_prompt, json_mode=True)

    response = clean_response(response)

    try:

        start = response.find("{")
        end = response.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("Invalid JSON")

        data = json.loads(response[start:end])

        questions = data.get("questions", [])

        clean_questions = []

        for q in questions:

            if isinstance(q, str):

                q = q.strip()

                if q:

                    clean_questions.append(q)

            elif isinstance(q, dict):

                question = q.get("question", "").strip()

                if question:

                    clean_questions.append(question)

        # Remove duplicates

        unique = []

        seen = set()

        for question in clean_questions:

            key = question.lower()

            if key not in seen:

                seen.add(key)

                unique.append(question)

        # Ensure exactly 5 questions

        return unique[:5]

    except Exception:

        questions = []

        for line in response.splitlines():

            line = line.strip()

            line = re.sub(r"^\d+[\).\-\s]*", "", line)

            if len(line) > 10:

                questions.append(line)

        # Remove duplicates

        unique = []

        seen = set()

        for question in questions:

            key = question.lower()

            if key not in seen:

                seen.add(key)

                unique.append(question)

        return unique[:5]