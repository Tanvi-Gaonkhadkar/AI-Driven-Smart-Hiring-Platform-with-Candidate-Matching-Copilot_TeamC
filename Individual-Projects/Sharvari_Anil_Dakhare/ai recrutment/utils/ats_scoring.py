"""
Rule-based ATS (Applicant Tracking System) scoring.

Module 3 (Candidate Screening) needs to work out of the box, without
requiring a Gemini/Ollama key - so this is a deterministic keyword-overlap
scorer, not an AI call: for each required skill, check whether it appears
(case-insensitively, tolerant of punctuation) in the resume text. The
score is simply the percentage of required skills found.

This deliberately mirrors what a real ATS keyword screen does. If the AI
service is configured, pages are free to additionally call
ai_service.match_resume_to_jd() for a richer, AI-written summary - but the
pass/fail ATS number itself stays deterministic and explainable.
"""

import re


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9+#. ]", " ", text.lower())


def parse_skills(skills_text: str) -> list:
    """'Python, Flask, SQL' -> ['Python', 'Flask', 'SQL']"""
    return [s.strip() for s in skills_text.split(",") if s.strip()]


def score_resume(resume_text: str, required_skills_text: str):
    """
    Returns (ats_score: int 0-100, matched_skills: list[str], missing_skills: list[str]).
    """
    required = parse_skills(required_skills_text)
    if not required:
        return 0, [], []

    normalized_resume = _normalize(resume_text)
    matched, missing = [], []

    for skill in required:
        skill_norm = _normalize(skill).strip()
        if not skill_norm:
            continue
        pattern = r"(?<![a-z0-9])" + re.escape(skill_norm) + r"(?![a-z0-9])"
        if re.search(pattern, normalized_resume):
            matched.append(skill)
        else:
            missing.append(skill)

    score = round((len(matched) / len(required)) * 100) if required else 0
    return score, matched, missing
