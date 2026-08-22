from email.mime import text
import json
from urllib import response
from backend.ollama_client import ask_llama

def parse_json(response):

    print("\n========== BEFORE JSON PARSE ==========")
    print(response)
    print("=======================================\n")

    response = response.replace("```json", "")
    response = response.replace("```", "")
    response = response.strip()

    start = response.find("{")

    if start == -1:
        raise ValueError("No JSON found.")

    response = response[start:]

    # Balance braces
    open_braces = response.count("{")
    close_braces = response.count("}")

    if close_braces < open_braces:
        response += "}" * (open_braces - close_braces)

    return json.loads(response)

def extract_resume_info(text):

    prompt = f"""
You are an ATS resume parser.

Your ONLY task is to extract information that is explicitly present
in the resume text below.

CRITICAL RULES:

1. Use ONLY information found in the resume.
2. NEVER use information from examples or previous responses.
3. NEVER invent, assume, or hallucinate information.
4. If a field is not present, return [].
5. Every value must come directly from the resume.
6. Do NOT add common skills just because they are related to the candidate.
7. Do NOT infer experience from projects.
8. Do NOT infer education.
9. Do NOT infer programming languages from frameworks.
10. Return ONLY valid JSON.

Required JSON structure:

{{
    "programmingLanguages": [],
    "frameworks": [],
    "libraries": [],
    "databases": [],
    "cloudTechnologies": [],
    "tools": [],
    "experience": [],
    "education": [],
    "projects": [],
    "certifications": []
}}

FIELD RULES:

programmingLanguages:
Only programming languages explicitly mentioned.

frameworks:
Only frameworks explicitly mentioned.

libraries:
Only libraries explicitly mentioned.

databases:
Only databases explicitly mentioned.

cloudTechnologies:
Only cloud technologies explicitly mentioned.

tools:
Only tools explicitly mentioned.

experience:
Extract actual job titles, internships, and explicitly stated work experience.

education:
Extract the actual education qualification exactly as written.

projects:
Extract actual project names/descriptions explicitly present.

certifications:
Extract certifications explicitly mentioned.

IMPORTANT:
Do NOT copy information from these instructions.
Only extract information from the RESUME TEXT.

RESUME TEXT:
-------------------------
{text}
-------------------------

Return ONLY the JSON object.
"""

    # -----------------------------
    # JSON SCHEMA
    # -----------------------------

    resume_schema = {
        "type": "object",
        "properties": {
            "programmingLanguages": {
                "type": "array",
                "items": {"type": "string"}
            },
            "frameworks": {
                "type": "array",
                "items": {"type": "string"}
            },
            "libraries": {
                "type": "array",
                "items": {"type": "string"}
            },
            "databases": {
                "type": "array",
                "items": {"type": "string"}
            },
            "cloudTechnologies": {
                "type": "array",
                "items": {"type": "string"}
            },
            "tools": {
                "type": "array",
                "items": {"type": "string"}
            },
            "experience": {
                "type": "array",
                "items": {"type": "string"}
            },
            "education": {
                "type": "array",
                "items": {"type": "string"}
            },
            "projects": {
                "type": "array",
                "items": {"type": "string"}
            },
            "certifications": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": [
            "programmingLanguages",
            "frameworks",
            "libraries",
            "databases",
            "cloudTechnologies",
            "tools",
            "experience",
            "education",
            "projects",
            "certifications"
        ]
    }

    # -----------------------------
    # CALL LLAMA
    # -----------------------------

    response = ask_llama(
        prompt,
        json_schema=resume_schema
    )

    print("\n========== RAW RESUME RESPONSE ==========")
    print(repr(response))
    print("=========================================\n")

    return parse_json(response)

def extract_jd_info(text):

    prompt = f"""
Extract the required information from this job description.

Return ONLY valid JSON using exactly these keys:
required_skills, experience, education.

Use [] or "" when information is not present.

Job Description:
{text}
"""

#     prompt = f"""
# You are an ATS Job Description Parser.

# Extract ONLY the required information.

# Do NOT explain anything.

# Return ONLY valid JSON.

# Example

# {{
#     "required_skills":[
#         "Python",
#         "FastAPI",
#         "Docker",
#         "AWS",
#         "SQL"
#     ],

#     "experience":"3-5 Years",

#     "education":"B.E./B.Tech"
# }}
# IMPORTANT:

# Return ONLY valid JSON.

# Do not write:

# - Here is the JSON
# - Explanation
# - Notes
# - Markdown
# - ```json

# Return ONLY the JSON object.

# Job Description

# {text}
# """

    response = ask_llama(prompt, json_mode=True)

    try:
        return parse_json(response)

    except Exception:

        response = ask_llama(prompt, json_mode=True)
        return parse_json(response)