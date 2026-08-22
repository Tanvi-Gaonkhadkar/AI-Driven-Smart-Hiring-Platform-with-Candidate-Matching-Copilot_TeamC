import os
import time
from backend.pdf_parser import extract_resume_text

from backend.ai_parser import extract_resume_info

from backend.matching_engine import compare
from backend.resume_analyzer_ai import analyze_candidate

from database.database import get_job_by_id

import time


# def analyze_resume(resume_pdf, jd_pdf):
#     """
#     Complete Resume Analysis Pipeline
#     """

#     # Step 1 - Extract text
#     print("Step 1: Extract Resume")
#     resume_text = extract_resume_text(resume_pdf)
#     print("Resume extracted")

#     print("Step 2: Extract JD")
#     jd_text = extract_jd_text(jd_pdf)
#     print("JD extracted")

#     print("Step 3: Resume JSON")
#     resume_json = extract_resume_info(resume_text)
#     print("Resume JSON done")

#     print("Step 4: JD JSON START")
#     jd_json = extract_jd_info(jd_text)
#     print("Step 4: JD JSON END")
    
#     print("Step 5 START")
#     matching = compare(resume_json, jd_json)
#     print("Step 5 END")

#     print("Step 6: AI Summary")
#     ai_summary = analyze_candidate(
#         resume_text,
#         jd_text,
#         matching
#     )
#     print("AI Summary done")

#     return {
#         "resume_text": resume_text,
#         "jd_text": jd_text,
#         "resume_json": resume_json,
#         "jd_json": jd_json,
#         "matching": matching,
#         "analysis": ai_summary
#     }
def analyze_resume(resume_pdf, job_id):

    start = time.time()

    # ==========================
    # Step 1: Extract Resume
    # ==========================

    print("Step 1: Extract Resume")

    resume_text = extract_resume_text(resume_pdf)
    print("\n========== RESUME DEBUG ==========")
    print("FILE:", resume_pdf)
    print("TEXT:")
    print(resume_text[:1000])
    print("==================================\n")

    print(
        f"Resume extracted: "
        f"{time.time() - start:.2f}s"
    )

    # ==========================
    # Step 2: Resume JSON
    # ==========================

    step = time.time()

    print("Step 2: Resume JSON")

    resume_json = extract_resume_info(
        resume_text
    )

    print(
        f"Resume JSON done: "
        f"{time.time() - step:.2f}s"
    )

    # ==========================
    # Step 3: Get Job
    # ==========================

    step = time.time()

    print("Step 3: Get Job")

    job = get_job_by_id(job_id)

    if job is None:
        raise ValueError(
            f"Job with ID {job_id} not found."
        )

    print(
        f"Job fetched: "
        f"{time.time() - step:.2f}s"
    )

    # ==========================
    # Build JD JSON
    # ==========================

    jd_json = {
        "required_skills": [],
        "experience": job["experience"] or "",
        "education": ""
    }

    # required_skills is stored in DB
    required_skills = job["required_skills"]

    if required_skills:

        if isinstance(required_skills, str):

            jd_json["required_skills"] = [
                skill.strip()
                for skill in required_skills.split(",")
                if skill.strip()
            ]

        elif isinstance(required_skills, list):

            jd_json["required_skills"] = required_skills

    # ==========================
    # Job Description
    # ==========================

    jd_text = job["job_description"] or ""

    print(
        f"Job data prepared: "
        f"{time.time() - step:.2f}s"
    )

    # ==========================
    # Step 4: Matching
    # ==========================

    step = time.time()

    print("Step 4: Matching")

    matching = compare(
        resume_json,
        jd_json,
        resume_text
    )
    print("\n========== ATS DEBUG ==========")

    print("JOB:", job["job_title"])

    print("REQUIRED SKILLS:")
    print(jd_json["required_skills"])

    print("RESUME TEXT:")
    print(resume_text)

    print("MATCHED:")
    print(matching["matched"])

    print("MISSING:")
    print(matching["missing"])

    print("ATS SCORE:")
    print(matching["skill_score"])

    print("===============================\n")

    print(
        f"Matching done: "
        f"{time.time() - step:.2f}s"
    )

    # ==========================
    # Step 5: AI Summary
    # ==========================

    step = time.time()

    print("Step 5: AI Summary")

    ai_summary = analyze_candidate(
        resume_json,
        jd_json,
        matching
    )

    print(
        f"AI Summary done: "
        f"{time.time() - step:.2f}s"
    )

    # ==========================
    # Total
    # ==========================

    print(
        f"TOTAL TIME: "
        f"{time.time() - start:.2f}s"
    )

    return {
        "resume_text": resume_text,
        "jd_text": jd_text,
        "resume_json": resume_json,
        "jd_json": jd_json,
        "matching": matching,
        "analysis": ai_summary,
        "job_id": job_id,
        "job_title": job["job_title"]
    }