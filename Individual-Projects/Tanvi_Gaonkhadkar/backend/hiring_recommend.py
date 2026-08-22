from backend.ollama_client import ask_llama


def hiring_recommendation(result):
    score = result["matching"]["skill_score"]

    if score >= 85:
        recommendation = "HR Interview"

    elif score >= 70:
        recommendation = "Technical Interview"

    elif score >= 50:
        recommendation = "Hold"

    else:
        recommendation = "Reject"

    prompt = f"""
You are a Senior HR Recruiter.

The ATS system has already evaluated the candidate.

==================================================
ATS RESULT
==================================================

ATS Match Score: {score}%

Final Recommendation: {recommendation}

Matched Skills:
{result["matching"]["matched"]}

Missing Skills:
{result["matching"]["missing"]}

==================================================
RESUME ANALYSIS
==================================================

{result["analysis"]}

==================================================
YOUR TASK
==================================================

The ATS recommendation is FINAL.

DO NOT change the recommendation.

Your job is ONLY to explain why the ATS produced this decision.

Return ONLY the following sections.

## ATS Evaluation Summary

### Candidate Match Score
Write the ATS score exactly as provided: {score}%

### Final Recommendation
Write the recommendation exactly as provided: {recommendation}

### Hiring Confidence
Generate ONE numeric confidence value between 0 and 100 followed by %.
For example: 82%
DO NOT write "(0-100%)".

### Risk Level
Choose EXACTLY ONE:
Low
Medium
High

DO NOT write "(Low / Medium / High)".

### Top Strengths
Give exactly 3 strengths based ONLY on the candidate information.

- Strength 1
- Strength 2
- Strength 3

### Top Weaknesses
Give exactly 3 weaknesses based ONLY on the missing skills or weaknesses.

- Weakness 1
- Weakness 2
- Weakness 3

### Suggested Salary Level
Choose EXACTLY ONE:
Entry
Junior
Mid
Senior

DO NOT write "(Entry / Junior / Mid / Senior)".

### HR Explanation
Explain in 3-5 professional sentences why the ATS recommendation is appropriate.

IMPORTANT RULES:
1. Do NOT change the ATS recommendation.
2. Do NOT invent skills that are not present in the resume.
3. Do NOT invent missing skills.
4. Hiring Confidence must be an actual number from 0 to 100.
5. Risk Level must be exactly Low, Medium, or High.
6. Suggested Salary Level must be exactly Entry, Junior, Mid, or Senior.
7. Never output placeholder text such as "(0-100%)".
8. Never output "(Low / Medium / High)".
9. Never output "(Entry / Junior / Mid / Senior)".
10. Do not add any additional sections.
"""

    return ask_llama(prompt)