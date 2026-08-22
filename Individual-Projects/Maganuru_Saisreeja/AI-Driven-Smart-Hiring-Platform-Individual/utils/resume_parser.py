import re
from io import BytesIO
from typing import Dict, List

import pdfplumber
from docx import Document


# ---------------------------------------------------------
# SKILL DATABASE
# ---------------------------------------------------------
#
# Canonical skill names. Matching against this list alone misses a lot
# of real-world resume spellings (NodeJS vs Node.js, Postgres vs
# PostgreSQL, etc). See SKILL_ALIASES below — every alias maps back to
# one of these canonical names so the candidate's skill list always
# uses consistent terminology.

SKILL_DB = {

    # Programming
    "python", "java", "c", "c++", "c#",
    "javascript", "typescript", "php", "r",

    # Web
    "html", "css", "bootstrap", "tailwind",
    "react", "angular", "vue", "node.js",
    "express", "next.js",

    # Databases
    "mysql", "postgresql", "mongodb",
    "sqlite", "oracle", "sql",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "nlp",
    "computer vision",
    "opencv",
    "tensorflow",
    "keras",
    "pytorch",
    "scikit-learn",
    "numpy",
    "pandas",

    # Cloud
    "aws",
    "azure",
    "gcp",

    # Tools
    "git",
    "github",
    "docker",
    "kubernetes",
    "streamlit",
    "fastapi",
    "flask",
    "django",
    "ollama",
    "terraform",
    "ansible",
    "jenkins",
    "github actions",
    "ci/cd",
    "bash",
    "shell scripting",
    "prometheus",
    "grafana",

    # Others
    "data structures",
    "algorithms",
    "problem solving",
    "rest api",
    "linux",
    "windows",

    # Design / UX
    "figma",
    "adobe xd",
    "sketch",
    "invision",
    "wireframing",
    "prototyping",
    "user research",
    "usability testing",
    "design systems",
    "adobe photoshop",
    "adobe illustrator",
    "ui design",
    "ux design",
    "interaction design",
    "visual design",
    "adobe premiere pro",
    "after effects",
    "canva",
    "material design",
    "responsive design",
    "accessibility",

    # Data / BI
    "power bi",
    "tableau",
    "excel",
    "google analytics",
    "google data studio",
    "looker",
    "a/b testing",
    "data visualization",
    "statistics",
    "data warehousing",
    "etl",
    "spss",

    # Marketing
    "seo",
    "sem",
    "google ads",
    "content marketing",
    "social media marketing",
    "email marketing",
    "hubspot",
    "digital marketing",
    "marketing automation",
    "brand management",
    "copywriting",

    # Sales / CRM
    "salesforce",
    "crm",
    "lead generation",
    "negotiation",
    "cold calling",
    "account management",
    "business development",

    # HR
    "recruitment",
    "onboarding",
    "hris",
    "payroll",
    "performance management",
    "applicant tracking system",
    "talent acquisition",
    "employee engagement",

    # Finance / Accounting
    "quickbooks",
    "sap",
    "financial modeling",
    "bookkeeping",
    "taxation",
    "budgeting",
    "financial analysis",
    "auditing",
    "tally",

    # Project Management
    "agile",
    "scrum",
    "kanban",
    "jira",
    "trello",
    "pmp",
    "stakeholder management",
    "risk management",
    "project planning",

    # QA / Testing
    "manual testing",
    "automation testing",
    "selenium",
    "test cases",
    "bug tracking",
    "postman",
    "junit",
    "cypress",

    # Mobile
    "android",
    "ios",
    "kotlin",
    "swift",
    "flutter",
    "react native",
    "xcode"
}


# ---------------------------------------------------------
# SKILL ALIASES
# ---------------------------------------------------------
#
# Maps alternate real-world spellings to the canonical SKILL_DB name.
# Extend this list as you find more variants in real resumes — it's
# far higher leverage than adding one-off regex tweaks per skill.

SKILL_ALIASES = {
    "node.js": ["nodejs", "node js"],
    "next.js": ["nextjs", "next js"],
    "scikit-learn": ["scikit learn", "sklearn"],
    "postgresql": ["postgres"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud platform", "google cloud"],
    "ai": ["a.i."],
    "c++": ["c plus plus"],
    "c#": ["c sharp"],
    "rest api": ["rest apis", "restful api", "restful apis"],
    "machine learning": ["ml"],
    "deep learning": ["dl"],
    "nlp": ["natural language processing"],
    "adobe xd": ["adobe experience design", "xd"],
    "ui design": ["ui/ux design", "ui/ux"],
    "ux design": ["user experience design", "ux"],
    "user research": ["user research methods"],
    "wireframing": ["wireframes", "wire-framing"],
    "prototyping": ["prototypes", "high-fidelity prototypes", "low-fidelity prototypes"],
    "adobe photoshop": ["photoshop"],
    "adobe illustrator": ["illustrator"],
    "after effects": ["adobe after effects"],
    "design systems": ["design system"],
    "power bi": ["powerbi", "power-bi"],
    "google analytics": ["ga4", "google analytics 4"],
    "a/b testing": ["ab testing", "a b testing", "split testing"],
    "seo": ["search engine optimization"],
    "sem": ["search engine marketing"],
    "google ads": ["adwords", "google adwords"],
    "crm": ["customer relationship management"],
    "hris": ["human resource information system"],
    "applicant tracking system": ["ats"],
    "financial modeling": ["financial modelling"],
    "sap": ["sap erp"],
    "pmp": ["project management professional"],
    "react native": ["reactnative"],
    "automation testing": ["test automation"],
    "manual testing": ["functional testing"],
    "ci/cd": ["ci cd", "continuous integration", "continuous deployment"],
    "github actions": ["github action"],
    "bash": ["bash scripting"],
}


# ---------------------------------------------------------
# PDF / DOCX TEXT EXTRACTION
# ---------------------------------------------------------

def extract_resume_text(uploaded_file):

    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):

        text = ""

        with pdfplumber.open(
            BytesIO(uploaded_file.read())
        ) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=2
                )

                if page_text:
                    text += "\n" + page_text

        return clean_text(text)

    elif filename.endswith(".docx"):

        document = Document(uploaded_file)

        text = "\n".join(
            p.text
            for p in document.paragraphs
        )

        return clean_text(text)

    return ""


# ---------------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------------

def clean_text(text):

    text = text.replace("\xa0", " ")

    text = re.sub(
        r"\n{2,}",
        "\n",
        text
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


# ---------------------------------------------------------
# BASIC DETAILS
# ---------------------------------------------------------

def extract_email(text):

    match = re.search(

        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}",

        text

    )

    return match.group() if match else ""


def extract_phone(text):

    match = re.search(

        r"(\+91[\-\s]?)?"
        r"(\d{10})",

        text

    )

    if match:
        return match.group().replace(" ", "")

    return ""


def extract_name(text):

    lines = [

        line.strip()

        for line in text.splitlines()

        if line.strip()

    ]

    if lines:

        first = lines[0]

        if len(first.split()) <= 5:
            return first.title()

    return "Unknown"


# ---------------------------------------------------------
# SECTION HEADERS
# ---------------------------------------------------------

SECTION_HEADERS = {

    "education": [
        "education",
        "academic background",
        "academic qualification",
        "academic qualifications",
        "qualification",
        "qualifications"
    ],

    "skills": [
        "technical skills",
        "skills",
        "technologies",
        "core competencies",
        "key skills"
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "key projects"
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses",
        "licenses & certifications"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "internships"
    ]
}

_ALL_HEADERS = {
    h for group in SECTION_HEADERS.values() for h in group
}


# ---------------------------------------------------------
# FIND SECTION
# ---------------------------------------------------------
#
# Resume section headers almost always sit alone on their own line
# ("SKILLS", "Work Experience:", etc). Matching on a substring found
# anywhere in the text (the old approach) means a phrase like
# "received a certificate of appreciation" inside a Projects bullet
# would be misread as the start of a Certifications section and
# silently truncate the real section. Instead, only treat a line as a
# header if the line itself (after stripping punctuation) IS one of
# the known header phrases.

def _line_matches_header(line, headers):

    cleaned = line.strip().lower().strip(":").strip()

    if not cleaned or len(cleaned) > 40:
        return False

    return cleaned in headers


def get_section(text, section_name):

    lines = text.split("\n")
    headers = set(SECTION_HEADERS.get(section_name, []))

    start_idx = None

    for i, line in enumerate(lines):

        if _line_matches_header(line, headers):
            start_idx = i
            break

    if start_idx is None:
        return ""

    end_idx = len(lines)

    for i in range(start_idx + 1, len(lines)):

        if _line_matches_header(lines[i], _ALL_HEADERS):
            end_idx = i
            break

    return "\n".join(lines[start_idx + 1:end_idx]).strip()


# ---------------------------------------------------------
# EDUCATION
# ---------------------------------------------------------

def extract_education(text):

    section = get_section(text, "education")

    if not section:
        section = text

    degree_patterns = [

        r"B\.?\s*Tech.*",

        r"Bachelor.*",

        r"B\.?E.*",

        r"M\.?\s*Tech.*",

        r"Master.*",

        r"MCA.*",

        r"BCA.*",

        r"BSc.*",

        r"B\.Sc.*",

        r"Intermediate.*"

    ]

    for pattern in degree_patterns:

        match = re.search(
            pattern,
            section,
            re.IGNORECASE
        )

        if match:

            degree = match.group().strip()

            cgpa = re.search(

                r"(\d+\.\d+\s*CGPA)",

                section,

                re.IGNORECASE

            )

            # The degree pattern above is greedy (".*") and often already
            # swallows a trailing "(X.X CGPA)" on the same line. Only
            # append it separately if it isn't already part of the match.
            if cgpa and cgpa.group(1).lower() not in degree.lower():

                degree += f" ({cgpa.group(1)})"

            return degree

    return "Not Mentioned"


# ---------------------------------------------------------
# EXPERIENCE
# ---------------------------------------------------------
#
# The old version collapsed everything to a binary "Fresher" /
# "Experienced" label, and returned "Fresher" the instant the word
# "internship" appeared anywhere in the resume — even for candidates
# who also have real full-time roles listed. That threw away real
# signal and gave the LLM almost nothing to reason from, which is
# part of why it started inventing plausible-sounding detail.
#
# Instead, hand over the actual Experience section text (or a clear
# "Not Mentioned" if there isn't one) and let the AI's system prompt
# — which already states internships/projects/certifications are not
# professional experience — do the actual reasoning against real text.
#
# One gap this left: when the "Experience" section contains ONLY an
# internship (no real full-time role), the raw section text still
# gets displayed as-is in the UI — which for internship-only
# candidates can end up showing a wall of internship/achievement
# text where a simple "Fresher" label would be clearer and more
# accurate. _is_internship_only() below detects that specific case
# and returns a "Fresher" label instead, while genuine work history
# (a role alongside or instead of an internship) still returns the
# real section text as before.

INTERNSHIP_INDICATORS = [
    "intern",
    "internship",
    "trainee",
    "virtual internship",
]

EMPLOYMENT_INDICATORS = [
    "full-time",
    "full time",
    "permanent",
    "employed as",
    "years of experience",
    "software engineer at",
    "developer at",
    "engineer at",
    "analyst at",
    "consultant at",
    "senior ",
    "associate ",
    "lead ",
    "manager",
]


def _is_internship_only(section):
    """
    True only when the section mentions an internship/trainee role
    and shows no sign of a genuine full-time/paid employment role.
    A candidate with both a real job AND an internship listed should
    NOT be classified as internship-only.
    """

    lower = section.lower()

    has_internship = any(
        keyword in lower for keyword in INTERNSHIP_INDICATORS
    )

    has_employment = any(
        keyword in lower for keyword in EMPLOYMENT_INDICATORS
    )

    return has_internship and not has_employment


def extract_experience(text):

    section = get_section(text, "experience")

    if section:

        if _is_internship_only(section):
            return "Fresher (Internship Experience Only)"

        return section.strip()

    # No dedicated experience/employment section was found at all —
    # this almost always means an entry-level candidate with no work
    # history yet, so "Fresher" is a more useful label here than a
    # vague "Not Mentioned". This is different from the old bug: the
    # old code returned "Fresher" the instant it saw the word
    # "internship" ANYWHERE in the resume, even when a full work
    # history existed elsewhere. Now that only happens when there is
    # genuinely no experience section to read from.
    return "Fresher"


# ---------------------------------------------------------
# ROLE TITLE -> TYPICAL SKILLS (fallback for bare-title JDs)
# ---------------------------------------------------------
#
# When a job description is just a role name ("SDE-1", "AI Engineer")
# there's no prose for extract_skills() to match against, and asking
# a small local LLM to invent a plausible skill list is unreliable —
# it may fail outright, or phrase skills in ways that don't match
# SKILL_DB's canonical terms. This lookup gives a deterministic floor
# of typical skills for common titles, independent of the LLM. It is
# only ever used to ADD candidate skills for the matcher to check for
# — it never claims the candidate has them.
#
# Keys are checked as substrings of the (normalized) JD text, longest
# key first, so "SDE-1" and "SDE 1" both resolve under "sde".

ROLE_SKILL_MAP = {
    "sde": [
        "data structures", "algorithms", "problem solving",
        "python", "java", "c++", "sql", "git", "rest api",
    ],
    "software engineer": [
        "data structures", "algorithms", "problem solving",
        "python", "java", "c++", "sql", "git", "rest api",
    ],
    "software developer": [
        "data structures", "algorithms", "problem solving",
        "python", "java", "sql", "git", "rest api",
    ],
    "backend developer": [
        "python", "java", "node.js", "sql", "rest api", "docker", "git",
    ],
    "backend engineer": [
        "python", "java", "node.js", "sql", "rest api", "docker", "git",
    ],
    "frontend developer": [
        "javascript", "typescript", "react", "html", "css", "git",
    ],
    "frontend engineer": [
        "javascript", "typescript", "react", "html", "css", "git",
    ],
    "full stack developer": [
        "javascript", "react", "node.js", "html", "css",
        "sql", "rest api", "git",
    ],
    "full stack engineer": [
        "javascript", "react", "node.js", "html", "css",
        "sql", "rest api", "git",
    ],
    "ai engineer": [
        "python", "machine learning", "deep learning",
        "tensorflow", "pytorch", "nlp", "numpy", "pandas",
    ],
    "ml engineer": [
        "python", "machine learning", "deep learning",
        "tensorflow", "pytorch", "numpy", "pandas",
    ],
    "machine learning engineer": [
        "python", "machine learning", "deep learning",
        "tensorflow", "pytorch", "numpy", "pandas",
    ],
    "data scientist": [
        "python", "machine learning", "statistics",
        "pandas", "numpy", "sql", "data visualization",
    ],
    "data analyst": [
        "sql", "excel", "power bi", "tableau",
        "python", "statistics", "data visualization",
    ],
    "devops engineer": [
        "docker", "kubernetes", "aws", "ci/cd",
        "jenkins", "terraform", "linux", "git",
    ],
    "qa engineer": [
        "manual testing", "automation testing",
        "selenium", "test cases", "postman", "junit",
    ],
    "android developer": ["android", "kotlin", "java", "git"],
    "ios developer": ["ios", "swift", "xcode", "git"],
    "product manager": [
        "stakeholder management", "agile", "scrum",
        "jira", "project planning",
    ],
}


def infer_skills_from_role_title(text):
    """
    Deterministic fallback: if the given text contains a known role
    title, return that role's typical skill list (canonical, title
    case). Longest/most-specific key wins when multiple match.
    Returns [] if no known role title is found.
    """

    lower = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    lower = re.sub(r"\s+", " ", lower).strip()

    best_key = None

    for key in ROLE_SKILL_MAP:
        if key in lower:
            if best_key is None or len(key) > len(best_key):
                best_key = key

    if best_key is None:
        return []

    return sorted(s.title() for s in ROLE_SKILL_MAP[best_key])


# ---------------------------------------------------------
# SKILLS
# ---------------------------------------------------------

_LIST_BOUNDARY_START = r"(?:^|[\n,|/;:])[ \t]*"
_LIST_BOUNDARY_END = r"[ \t]*(?:$|[\n,|/;.])"

# Single-letter skill names are unusually ambiguous — a stray "R" or "C"
# in ordinary prose (initials, abbreviations, etc.) will satisfy a plain
# \b...\b match even though it has nothing to do with the language.
# These are only trusted when they appear as a standalone entry in an
# actual list (comma/pipe/slash/newline separated), the way skills are
# normally written on a resume.
_AMBIGUOUS_SINGLE_TOKEN_SKILLS = {"c", "r"}


def _skill_pattern(skill):
    """
    Symbol-heavy skills like 'c++' and 'c#' break under \\b word
    boundaries, because '+' and '#' aren't word characters — there's
    no boundary between the symbol and the whitespace/punctuation that
    typically follows it, so the old regex silently never matched.
    Those skills get matched as a plain literal substring instead.

    Single-letter skills (C, R) require list context to avoid matching
    stray initials/abbreviations in prose.

    Everything else keeps \\b boundaries to avoid partial-word matches
    (e.g. "java" inside "javascript").
    """

    if skill in {"c++", "c#"}:
        return re.escape(skill)

    if skill in _AMBIGUOUS_SINGLE_TOKEN_SKILLS:
        return (
            _LIST_BOUNDARY_START
            + re.escape(skill)
            + _LIST_BOUNDARY_END
        )

    return r"\b" + re.escape(skill) + r"\b"


def extract_skills(text):

    lower = text.lower()

    found = set()

    for skill in SKILL_DB:

        pattern = _skill_pattern(skill)
        flags = re.MULTILINE if skill in _AMBIGUOUS_SINGLE_TOKEN_SKILLS else 0

        if re.search(pattern, lower, flags):
            found.add(skill)

    for canonical, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            pattern = _skill_pattern(alias)
            flags = re.MULTILINE if alias in _AMBIGUOUS_SINGLE_TOKEN_SKILLS else 0

            if re.search(pattern, lower, flags):
                found.add(canonical)
                break

    return sorted(s.title() for s in found)


# ---------------------------------------------------------
# PROJECTS
# ---------------------------------------------------------
#
# The old version hardcoded specific project names ("Health Mitra",
# "FixTrack", etc) from what looks like one test resume — for any
# other candidate those would never match and projects would come
# back empty. Use the generic section-based extraction only.

def extract_projects(text):

    section = get_section(text, "projects")

    if not section:
        return []

    project_names = []

    for line in section.split("\n"):

        line = line.strip().lstrip("•-*").strip()

        if not (5 < len(line) < 80):
            continue

        if "|" in line:
            project_names.append(line.split("|")[0].strip())
        else:
            project_names.append(line)

    return list(dict.fromkeys(project_names))


# ---------------------------------------------------------
# CERTIFICATIONS
# ---------------------------------------------------------

CERTIFICATION_KEYWORDS = [
    "certificate",
    "certification",
    "certified",
    "academy",
    "coursera",
    "udemy",
    "udacity",
    "infosys",
    "salesforce",
    "google",
    "microsoft",
    "aws certified",
    "nptel",
    "hackerrank",
    "linkedin learning"
]


def extract_certifications(text):

    certs = []

    section = get_section(text, "certifications")

    if not section:
        section = text

    lines = section.split("\n")

    for line in lines:

        line = line.strip()

        if len(line) < 3:
            continue

        if any(word in line.lower() for word in CERTIFICATION_KEYWORDS):
            certs.append(line.replace("•", "").strip())

    return list(dict.fromkeys(certs))


# ---------------------------------------------------------
# COLLEGE
# ---------------------------------------------------------
#
# The old hardcoded college list only worked for one test resume.
# Pull it from the Education section generically instead: look for a
# line containing a common institution keyword.

COLLEGE_KEYWORDS = [
    "college", "university", "institute", "school of"
]


def extract_college(text):

    section = get_section(text, "education")

    if not section:
        section = text

    for line in section.split("\n"):

        line = line.strip()

        if not line:
            continue

        if any(word in line.lower() for word in COLLEGE_KEYWORDS):
            return line.replace("•", "").strip()

    return ""


# ---------------------------------------------------------
# CGPA
# ---------------------------------------------------------

def extract_cgpa(text):

    match = re.search(

        r"(\d+\.\d+)\s*CGPA",

        text,

        re.IGNORECASE

    )

    if match:

        return match.group(1)

    return ""


# ---------------------------------------------------------
# MAIN PARSER
# ---------------------------------------------------------

def extract_candidate_info(text):

    candidate = {}

    candidate["name"] = extract_name(text)

    candidate["email"] = extract_email(text)

    candidate["phone"] = extract_phone(text)

    candidate["education"] = extract_education(text)

    candidate["college"] = extract_college(text)

    candidate["cgpa"] = extract_cgpa(text)

    candidate["experience"] = extract_experience(text)

    candidate["skills"] = extract_skills(text)

    candidate["projects"] = extract_projects(text)

    candidate["certifications"] = extract_certifications(text)

    # Fields populated later by AI
    candidate["score"] = 0

    candidate["recommended_role"] = ""

    candidate["missing_skills"] = []

    candidate["skill_gap_analysis"] = ""

    candidate["hiring_recommendation"] = ""

    return candidate