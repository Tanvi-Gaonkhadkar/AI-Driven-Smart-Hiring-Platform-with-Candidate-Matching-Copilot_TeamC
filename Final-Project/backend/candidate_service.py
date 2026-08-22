"""
Candidate Screening Service

This service combines all AI modules:

1. Candidate Ranking
2. Hiring Recommendation
3. Resume Comparison
4. Email Generator
"""

import os

from backend.candidate_ranking import rank_candidates
from backend.hiring_recommend import hiring_recommendation
from backend.resume_comparison import compare_candidates
from backend.email_generator import generate_email

def candidate_service(
    resume_paths,
    job_id,
    job_title="AI Engineer",
    company="ABC Technologies"
):

    resume_paths = [
        path
        for path in resume_paths
        if isinstance(path, str) and os.path.exists(path)
    ]

    ranking = rank_candidates(
        resume_paths,
        job_id
    )

    return {
        "ranking": ranking
    }

