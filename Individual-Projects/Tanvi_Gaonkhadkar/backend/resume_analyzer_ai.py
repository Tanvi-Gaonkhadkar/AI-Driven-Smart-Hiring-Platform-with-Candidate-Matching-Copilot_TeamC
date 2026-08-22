from backend.ollama_client import ask_llama


def analyze_candidate(resume_data, jd_data, matching_result):
    """
    Generate AI explanation based on resume, job description
    and ATS matching results.
    """

    # ---------------------------------
    # ATS SCORE BASED RECOMMENDATION
    # ---------------------------------

    score = matching_result["skill_score"]

    if score >= 90:
        recommendation = "Highly Recommended"

    elif score >= 75:
        recommendation = "Recommended"

    elif score >= 60:
        recommendation = "Needs Improvement"

    else:
        recommendation = "Reject"

    # ---------------------------------
    # AI PROMPT
    # ---------------------------------

    prompt = f"""
You are an experienced HR Recruiter.

Candidate Information:
{resume_data}

Job Requirements:
{jd_data}

Matching Result:
Matched Skills: {matching_result["matched"]}
Missing Skills: {matching_result["missing"]}
Extra Skills: {matching_result["extra"]}
ATS Score: {score}%

The ATS score is authoritative.

The hiring recommendation has already been determined by the ATS system:

{recommendation}

You MUST use exactly this recommendation.
Do NOT change it.

Generate a concise hiring assessment.

Return Markdown with ONLY:

## Candidate Summary
2 short lines.

## Technical Strengths
Top 3 relevant strengths.

## Soft Skills
Top 2 relevant strengths.

## Missing Skills
Important missing skills.

## Suitable Roles
Up to 2 suitable roles.

## Hiring Recommendation
{recommendation}

## Reason
2 short lines explaining why this recommendation is appropriate based on the ATS score, matched skills and missing skills.

Do not add any other sections.
"""

    return ask_llama(prompt)