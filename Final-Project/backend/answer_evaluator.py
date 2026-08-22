from backend.ollama_client import ask_llama
from backend.ai_parser import parse_json


def evaluate_answer(
    resume_data,
    jd_data,
    question,
    answer
):
    """
    Evaluate a single interview answer dynamically.
    """

    prompt = f"""
You are an experienced Technical Interviewer evaluating a candidate's
answer to ONE specific interview question.

Your evaluation MUST be based ONLY on the candidate's actual answer.

==================================================
CANDIDATE RESUME
==================================================
{resume_data}

==================================================
JOB DESCRIPTION
==================================================
{jd_data}

==================================================
INTERVIEW QUESTION
==================================================
{question}

==================================================
CANDIDATE ANSWER
==================================================
{answer}

==================================================
EVALUATION RULES
==================================================

Evaluate the candidate answer carefully.

Consider:

1. Relevance
   - Does the answer actually address the question?

2. Technical correctness
   - Are the concepts accurate?

3. Depth
   - Does the candidate explain the concept sufficiently?

4. Practical experience
   - Does the candidate provide a relevant example when appropriate?

5. Communication
   - Is the answer clear and understandable?

6. Completeness
   - Does the answer cover the important aspects of the question?

IMPORTANT:

A very short, vague, irrelevant, incorrect, or meaningless answer
MUST receive a low score.

Do NOT give a good score simply because the candidate's resume
contains relevant skills.

Evaluate the ANSWER, not the resume.

Examples of weak answers include:
- "I don't know."
- "I will read about it."
- "It is useful."
- Random or meaningless text.
- Answers that do not address the question.

Do NOT use a fixed score.

The score MUST be determined independently for this answer.

==================================================
SCORING
==================================================

9-10 = Excellent answer
7-8  = Strong answer
5-6  = Average answer
3-4  = Weak answer
0-2  = Very poor / irrelevant / no meaningful answer

Confidence should represent how confident you are in your evaluation,
not how confident the candidate sounds.

==================================================
FOLLOW-UP
==================================================

Generate a follow-up question that is directly related to:

- the interview question,
- the candidate's answer,
- or a weakness/gap identified in the answer.

Do NOT always ask about scalability.

==================================================
OUTPUT
==================================================

Return ONLY ONE valid JSON object.

Use exactly this structure:

{{
    "score": <integer from 0 to 10>,
    "confidence": <integer from 0 to 100>,
    "feedback": "<specific feedback about this answer>",
    "strengths": [
        "<strength specific to this answer>"
    ],
    "weaknesses": [
        "<weakness specific to this answer>"
    ],
    "follow_up": "<specific follow-up question>"
}}

Do NOT copy example values.
Do NOT return multiple JSON objects.
Do NOT include markdown.
Do NOT include explanations outside the JSON.

Now evaluate the candidate's actual answer.
"""

    response = ask_llama(prompt, json_mode=True)

    print("\n========== RAW LLM RESPONSE ==========")
    print(response)
    print("=====================================\n")

    return parse_json(response)

def generate_final_report(interview_data):

    prompt = f"""
You are an HR Interview Panel.

Analyze the complete interview conversation below.

Interview Conversation:
{interview_data}

Evaluate the candidate based ONLY on their actual interview answers.

Consider:
- Technical knowledge
- Problem solving
- Communication
- Answer quality
- Consistency
- Overall interview performance

Do not assume skills that the candidate did not demonstrate.

Return ONLY valid JSON.

{{
    "technical_score": 85,
    "communication_score": 80,
    "confidence_score": 88,
    "overall_score": 84,
    "recommendation": "Recommended",
    "summary": "Candidate performed well overall."
}}

IMPORTANT:
- Scores must be based on the actual interview answers.
- Do not always return the example scores.
- The recommendation must depend on the candidate's actual performance.
- Return ONLY the JSON object.
- Do not include markdown.
- Do not include explanations outside the JSON.
"""

    response = ask_llama(prompt)

    print("\n========== RAW FINAL REPORT ==========")
    print(response)
    print("======================================\n")

    return parse_json(response)