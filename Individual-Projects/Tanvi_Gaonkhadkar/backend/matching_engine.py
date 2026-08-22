# def compare(resume, jd):

#     resume_skills = set()

#     # Combine all technical skill categories
#     for key in [
#         "programmingLanguages",
#         "frameworks",
#         "libraries",
#         "databases",
#         "cloudTechnologies",
#         "tools"
#     ]:

#         values = resume.get(key)

#         # Handle null values
#         if values is None:
#             values = []

#         # Handle single string
#         if isinstance(values, str):
#             values = [values]

#         resume_skills.update(values)

#     jd_skills = jd.get("required_skills")

#     if jd_skills is None:
#         jd_skills = []

#     if isinstance(jd_skills, str):
#         jd_skills = [jd_skills]

#     jd_skills = set(jd_skills)

#     matched = sorted(resume_skills & jd_skills)
#     missing = sorted(jd_skills - resume_skills)
#     extra = sorted(resume_skills - jd_skills)

#     if len(jd_skills) == 0:
#         skill_score = 0
#     else:
#         skill_score = round(
#             len(matched) / len(jd_skills) * 100
#         )

#     return {
#         "matched": matched,
#         "missing": missing,
#         "extra": extra,
#         "skill_score": skill_score,
#         "matched_count": len(matched),
#         "required_count": len(jd_skills),
#         "resume_skill_count": len(resume_skills)
#     }
import re


def normalize(text):
    return re.sub(
        r"[^a-z0-9+#.]",
        "",
        str(text).lower()
    )


def skill_present(skill, resume_text):
    """
    Check whether the required skill is actually present
    in the original resume text.
    """

    text = resume_text.lower()
    skill_lower = skill.lower()

    # Direct match
    if skill_lower in text:
        return True

    # Common aliases
    aliases = {
        "machine learning": [
            "machine learning",
            "ml"
        ],

        "deep learning": [
            "deep learning",
            "dl"
        ],

        "sql": [
            "sql",
            "mysql",
            "postgresql",
            "postgres"
        ],

        "aws": [
            "aws",
            "amazon web services"
        ],

        "fastapi": [
            "fastapi",
            "fast api"
        ],

        "docker": [
            "docker",
            "dockerized",
            "containerization"
        ],

        "python": [
            "python"
        ],

        "tensorflow": [
            "tensorflow"
        ],

        "power bi": [
            "power bi",
            "powerbi"
        ],

        "javascript": [
            "javascript",
            "js"
        ],

        "react": [
            "react",
            "reactjs",
            "react.js"
        ],

        "mongodb": [
            "mongodb",
            "mongo db"
        ]
    }

    key = skill_lower.strip()

    if key in aliases:

        for alias in aliases[key]:

            if alias in text:
                return True

    return False


def extract_years(text):
    """
    Extract years of experience from text.

    Examples:
    '4 Years' -> 4
    '2 years experience' -> 2
    """

    if not text:
        return 0

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        str(text).lower()
    )

    if match:
        return float(match.group(1))

    return 0


def experience_score(resume, jd):
    """
    Experience contributes 15 points to ATS.
    """

    required_exp = extract_years(
        jd.get("experience", "")
    )

    resume_experience = resume.get(
        "experience",
        []
    )

    if isinstance(resume_experience, str):
        resume_experience = [resume_experience]

    resume_text = " ".join(
        str(x) for x in resume_experience
    )

    candidate_exp = extract_years(
        resume_text
    )

    # If JD doesn't specify experience,
    # give full points when resume has experience.
    if required_exp == 0:

        if candidate_exp > 0:
            return 15

        return 5

    if candidate_exp == 0:
        return 0

    if candidate_exp >= required_exp:
        return 15

    # Partial experience
    score = (candidate_exp / required_exp) * 15

    return round(score)


def education_score(resume):
    """
    Education contributes 10 points.
    """

    education = resume.get(
        "education",
        []
    )

    if isinstance(education, str):
        education = [education]

    if education:
        return 10

    return 0


def project_score(resume):
    """
    Projects contribute 10 points.
    """

    projects = resume.get(
        "projects",
        []
    )

    if isinstance(projects, str):
        projects = [projects]

    if projects:
        return 10

    return 0


def certification_score(resume):
    """
    Certifications contribute 5 points.
    """

    certifications = resume.get(
        "certifications",
        []
    )

    if isinstance(certifications, str):
        certifications = [certifications]

    if certifications:
        return 5

    return 0


def compare(resume, jd, resume_text=None):

    # ==================================================
    # 1. REQUIRED JOB SKILLS
    # ==================================================

    jd_skills = jd.get(
        "required_skills",
        []
    )

    if jd_skills is None:
        jd_skills = []

    if isinstance(jd_skills, str):
        jd_skills = [jd_skills]

    # Remove duplicates
    jd_skills = list(
        dict.fromkeys(
            skill.strip()
            for skill in jd_skills
            if skill and skill.strip()
        )
    )

    # ==================================================
    # 2. MATCH REQUIRED SKILLS
    # ==================================================

    matched = []
    missing = []

    if resume_text:

        for skill in jd_skills:

            if skill_present(
                skill,
                resume_text
            ):
                matched.append(skill)

            else:
                missing.append(skill)

    else:

        # Fallback
        resume_skills = set()

        for key in [
            "programmingLanguages",
            "frameworks",
            "libraries",
            "databases",
            "cloudTechnologies",
            "tools"
        ]:

            values = resume.get(
                key,
                []
            )

            if values is None:
                values = []

            if isinstance(values, str):
                values = [values]

            resume_skills.update(
                normalize(v)
                for v in values
            )

        for skill in jd_skills:

            if normalize(skill) in resume_skills:
                matched.append(skill)

            else:
                missing.append(skill)

    # ==================================================
    # 3. EXTRA SKILLS
    # ==================================================

    resume_skills_display = set()

    for key in [
        "programmingLanguages",
        "frameworks",
        "libraries",
        "databases",
        "cloudTechnologies",
        "tools"
    ]:

        values = resume.get(
            key,
            []
        )

        if values is None:
            values = []

        if isinstance(values, str):
            values = [values]

        resume_skills_display.update(
            values
        )

    required_normalized = {
        normalize(skill)
        for skill in jd_skills
    }

    extra = sorted(
        skill
        for skill in resume_skills_display
        if normalize(skill)
        not in required_normalized
    )

    # ==================================================
    # 4. SKILL SCORE
    # ==================================================

    if len(jd_skills) == 0:

        skill_score = 0

    else:

        skill_score = round(
            len(matched)
            / len(jd_skills)
            * 60
        )

    # ==================================================
    # 5. OTHER ATS COMPONENTS
    # ==================================================

    exp_score = experience_score(
        resume,
        jd
    )

    edu_score = education_score(
        resume
    )

    proj_score = project_score(
        resume
    )

    cert_score = certification_score(
        resume
    )

    # ==================================================
    # 6. FINAL ATS SCORE
    # ==================================================

    ats_score = (
        skill_score
        + exp_score
        + edu_score
        + proj_score
        + cert_score
    )

    # Keep score between 0 and 100
    ats_score = min(
        100,
        max(0, round(ats_score))
    )

    # ==================================================
    # DEBUG
    # ==================================================

    print("\n========== ATS DEBUG ==========")

    print("JOB:", jd.get("job_title", "AI Engineer"))

    print(
        "REQUIRED SKILLS:",
        jd_skills
    )

    print(
        "MATCHED:",
        sorted(matched)
    )

    print(
        "MISSING:",
        sorted(missing)
    )

    print(
        "Skill Score / 60:",
        skill_score
    )

    print(
        "Experience Score / 15:",
        exp_score
    )

    print(
        "Education Score / 10:",
        edu_score
    )

    print(
        "Project Score / 10:",
        proj_score
    )

    print(
        "Certification Score / 5:",
        cert_score
    )

    print(
        "FINAL ATS SCORE:",
        ats_score
    )

    print("===============================\n")

    return {
        "matched": sorted(matched),

        "missing": sorted(missing),

        "extra": extra,

        "skill_score": ats_score,

        "matched_count": len(matched),

        "required_count": len(jd_skills),

        "resume_skill_count": len(
            resume_skills_display
        ),

        "skill_score_component": skill_score,

        "experience_score": exp_score,

        "education_score": edu_score,

        "project_score": proj_score,

        "certification_score": cert_score
    }