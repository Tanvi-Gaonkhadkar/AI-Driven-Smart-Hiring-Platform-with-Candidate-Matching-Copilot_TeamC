import os

from backend.resume_service import analyze_resume


def rank_candidates(resume_paths, job_id):

    candidates = []

    for resume in resume_paths:

        print("=" * 50)
        print("Resume:", resume)
        print("Type:", type(resume))
        print("Exists:", os.path.exists(resume) if isinstance(resume, str) else "Not a string")

        result = analyze_resume(resume, job_id)

        candidates.append({
            "name": os.path.splitext(os.path.basename(resume))[0],
            "ATS Score": result["matching"]["skill_score"],
            "recommendation": result["analysis"],
            "result": result
        })

    candidates.sort(
        key=lambda x: x["ATS Score"],
        reverse=True
    )

    for i, c in enumerate(candidates):
        c["rank"] = i + 1

    return candidates

