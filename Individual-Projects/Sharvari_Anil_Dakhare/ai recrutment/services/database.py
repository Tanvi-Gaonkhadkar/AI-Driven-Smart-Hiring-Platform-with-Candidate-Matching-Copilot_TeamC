"""
SQLite persistence layer for the HR workflow modules added on top of the
existing session-only app: Recruiter Login, Job Openings, ATS Candidate
Screening, Interview Scheduling & Status Tracking, Onboarding, Talent
Management, and Document Management.

This is deliberately separate from data/candidate_store.py and
data/jd_store.py, which power the original session-state-backed pages
(Dashboard, Resume Analyzer, Candidate Screening, Interview Copilot,
Hiring Analytics, Job Description) - those are untouched. Everything in
THIS file is real, on-disk SQLite storage under app_data/, so job
openings, screened candidates, interviews, employees, and uploaded
documents all survive an app restart.

Every table is created here, in one place, via init_db() - called once at
app startup (see app.py). Every other module in the app should go through
the functions in this file rather than opening its own sqlite3 connection.
"""

import os
import sqlite3
import datetime
import json

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DATA_DIR = os.path.join(_BASE_DIR, "app_data")
DOCUMENTS_DIR = os.path.join(APP_DATA_DIR, "documents")
DB_PATH = os.path.join(APP_DATA_DIR, "yourtalentpilot.db")

# The full Interview Management pipeline (Module 7). Every job_candidates
# row moves left-to-right through this list via move_candidate_to_next_stage();
# "Rejected" and "Hold" are side-states reachable from any point, not part
# of the linear order itself.
STAGE_ORDER = [
    "Applied",
    "AI Reviewed",
    "Shortlisted",
    "Interview Round 1",
    "Interview Round 2",
    "Interview Round 3",
    "Selected",
    "Offer Sent",
    "Onboarded",
]
SIDE_STAGES = ["Rejected", "Hold"]


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_connection() -> sqlite3.Connection:
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_column(cur, table, column, coldef):
    """Adds `column` to `table` if it doesn't already exist - safe to call every run."""
    existing = [row[1] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in existing:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coldef}")


def init_db():
    """Creates every table if it doesn't exist yet. Safe to call on every app run."""
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recruiters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            role TEXT NOT NULL DEFAULT 'Recruiter',
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_openings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            department TEXT,
            required_skills TEXT NOT NULL,
            min_ats_score INTEGER NOT NULL DEFAULT 60,
            status TEXT NOT NULL DEFAULT 'Open',
            created_by TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL REFERENCES job_openings(id),
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            resume_filename TEXT,
            resume_text TEXT,
            ats_score INTEGER NOT NULL DEFAULT 0,
            matched_skills TEXT,
            missing_skills TEXT,
            status TEXT NOT NULL DEFAULT 'Screened',
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL REFERENCES job_candidates(id),
            round_name TEXT NOT NULL,
            interview_date TEXT NOT NULL,
            interview_time TEXT NOT NULL,
            interviewer TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Scheduled',
            feedback TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT UNIQUE NOT NULL,
            candidate_id INTEGER REFERENCES job_candidates(id),
            name TEXT NOT NULL,
            email TEXT,
            department TEXT,
            designation TEXT,
            joining_date TEXT,
            performance_rating REAL NOT NULL DEFAULT 3.0,
            manager TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL REFERENCES employees(id),
            doc_type TEXT NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    """)

    # --- Interview Management (Module 7) additions ---
    # `stage` is the granular pipeline position (STAGE_ORDER / SIDE_STAGES);
    # the original `status` column (Screened/Shortlisted/Rejected/Selected)
    # is kept in sync automatically (see _sync_status_from_stage()) so every
    # existing page that already filters on `status` keeps working unchanged.
    _ensure_column(cur, "job_candidates", "stage", "TEXT NOT NULL DEFAULT 'Applied'")
    _ensure_column(cur, "interviews", "meeting_link", "TEXT")
    _ensure_column(cur, "interviews", "ai_feedback_json", "TEXT")

    # --- Interview Management redesign: scheduling detail, split notes,
    # invitation tracking, offer/onboarding, all on the same page now ---
    _ensure_column(cur, "interviews", "meeting_mode", "TEXT DEFAULT 'Video Call'")
    _ensure_column(cur, "interviews", "invitation_sent", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(cur, "interviews", "technical_notes", "TEXT")
    _ensure_column(cur, "interviews", "communication_notes", "TEXT")
    _ensure_column(cur, "interviews", "overall_notes", "TEXT")

    _ensure_column(cur, "job_candidates", "offer_letter_text", "TEXT")
    _ensure_column(cur, "job_candidates", "offer_sent", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(cur, "job_candidates", "offer_accepted", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(cur, "job_candidates", "onboard_department", "TEXT")
    _ensure_column(cur, "job_candidates", "onboard_manager", "TEXT")
    _ensure_column(cur, "job_candidates", "onboard_joining_date", "TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidate_stage_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL REFERENCES job_candidates(id),
            stage TEXT NOT NULL,
            note TEXT,
            changed_at TEXT NOT NULL
        )
    """)

    # --- AI Document Verification (Section I) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidate_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL REFERENCES job_candidates(id),
            doc_type TEXT NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            verification_status TEXT NOT NULL DEFAULT 'Pending',
            verification_summary TEXT,
            uploaded_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Recruiters (auth) - see utils/auth.py for password hashing / login logic
# ---------------------------------------------------------------------------

def create_recruiter(username: str, password_hash: str, full_name: str, email: str = "", role: str = "Recruiter"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO recruiters (username, password_hash, full_name, email, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (username.strip().lower(), password_hash, full_name.strip(), email.strip(), role, _now()),
    )
    conn.commit()
    conn.close()


def get_recruiter_by_username(username: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM recruiters WHERE username = ?", (username.strip().lower(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def any_recruiters_exist() -> bool:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) AS c FROM recruiters").fetchone()["c"]
    conn.close()
    return count > 0


# ---------------------------------------------------------------------------
# Job Openings
# ---------------------------------------------------------------------------

def create_job_opening(title, department, required_skills, min_ats_score, created_by):
    conn = get_connection()
    cur = conn.cursor()
    next_num = cur.execute("SELECT COUNT(*) AS c FROM job_openings").fetchone()["c"] + 1
    job_code = f"JOB-{1000 + next_num}"
    cur.execute(
        "INSERT INTO job_openings (job_code, title, department, required_skills, min_ats_score, status, created_by, created_at) "
        "VALUES (?, ?, ?, ?, ?, 'Open', ?, ?)",
        (job_code, title.strip(), department.strip(), required_skills.strip(), int(min_ats_score), created_by, _now()),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_job_opening(new_id)


def get_all_job_openings():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM job_openings ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_job_opening(job_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM job_openings WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def set_job_status(job_id: int, status: str):
    conn = get_connection()
    conn.execute("UPDATE job_openings SET status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# ATS Candidate Screening
# ---------------------------------------------------------------------------

def add_job_candidate(job_id, name, email, phone, resume_filename, resume_text,
                       ats_score, matched_skills, missing_skills, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO job_candidates (job_id, name, email, phone, resume_filename, resume_text, "
        "ats_score, matched_skills, missing_skills, status, stage, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Applied', ?)",
        (job_id, name.strip(), email.strip(), phone.strip(), resume_filename, resume_text,
         int(ats_score), ",".join(matched_skills), ",".join(missing_skills), status, _now()),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    # ATS screening already ran synchronously (score + decision happened
    # before this row was even inserted), so log the full Applied -> AI
    # Reviewed -> Shortlisted/Rejected progression as one instant sequence -
    # the Candidate Timeline still shows every step, just all at once.
    _log_stage(new_id, "Applied", "Application received.")
    _log_stage(new_id, "AI Reviewed", f"ATS scored {ats_score}.")
    final_stage = "Shortlisted" if status == "Shortlisted" else "Rejected"
    _set_stage(new_id, final_stage, f"Auto-{final_stage.lower()} by ATS threshold.")

    return get_job_candidate(new_id)


def get_job_candidate(candidate_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM job_candidates WHERE id = ?", (candidate_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_candidates_for_job(job_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM job_candidates WHERE job_id = ? ORDER BY ats_score DESC", (job_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_job_candidates():
    conn = get_connection()
    rows = conn.execute(
        "SELECT jc.*, jo.title AS job_title, jo.job_code AS job_code "
        "FROM job_candidates jc JOIN job_openings jo ON jc.job_id = jo.id "
        "ORDER BY jc.id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_job_candidate_status(candidate_id: int, status: str):
    conn = get_connection()
    conn.execute("UPDATE job_candidates SET status = ? WHERE id = ?", (status, candidate_id))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Interview Management: candidate stage pipeline
# (Applied -> AI Reviewed -> Shortlisted -> Interview Round 1/2/3 ->
#  Selected -> Offer Sent -> Onboarded, with Rejected/Hold as side-states)
# ---------------------------------------------------------------------------

def _log_stage(candidate_id: int, stage: str, note: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO candidate_stage_history (candidate_id, stage, note, changed_at) VALUES (?, ?, ?, ?)",
        (candidate_id, stage, note, _now()),
    )
    conn.commit()
    conn.close()


def _sync_status_from_stage(candidate_id: int, stage: str):
    """Keeps the legacy `status` column (used by ATS Screening/Onboarding
    filters) consistent with the new granular `stage`, so nothing that
    already reads `status` needs to change."""
    if stage == "Rejected":
        update_job_candidate_status(candidate_id, "Rejected")
    elif stage in ("Selected", "Offer Sent", "Onboarded"):
        update_job_candidate_status(candidate_id, "Selected")
    elif stage == "Shortlisted":
        update_job_candidate_status(candidate_id, "Shortlisted")
    # "Applied" / "AI Reviewed" / "Interview Round N" / "Hold" don't have a
    # matching legacy status - status is left as whatever it already was.


def _set_stage(candidate_id: int, stage: str, note: str = ""):
    conn = get_connection()
    conn.execute("UPDATE job_candidates SET stage = ? WHERE id = ?", (stage, candidate_id))
    conn.commit()
    conn.close()
    _log_stage(candidate_id, stage, note)
    _sync_status_from_stage(candidate_id, stage)


def get_candidate_stage_history(candidate_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM candidate_stage_history WHERE candidate_id = ? ORDER BY id ASC", (candidate_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def move_candidate_to_next_stage(candidate_id: int, note: str = ""):
    """Advances one step along STAGE_ORDER. No-op if already at the last stage."""
    candidate = get_job_candidate(candidate_id)
    current = candidate["stage"]
    if current in STAGE_ORDER:
        idx = STAGE_ORDER.index(current)
    else:
        idx = -1  # e.g. coming back from Hold/Rejected - restart at the top
    if idx + 1 < len(STAGE_ORDER):
        _set_stage(candidate_id, STAGE_ORDER[idx + 1], note or "Moved to next stage.")
    return get_job_candidate(candidate_id)


def set_candidate_hold(candidate_id: int, note: str = ""):
    _set_stage(candidate_id, "Hold", note or "Put on hold by recruiter.")
    return get_job_candidate(candidate_id)


def resume_candidate_from_hold(candidate_id: int, note: str = ""):
    """Resumes at whatever stage the candidate was in immediately before Hold."""
    history = get_candidate_stage_history(candidate_id)
    pre_hold = next((h["stage"] for h in reversed(history) if h["stage"] != "Hold"), "Shortlisted")
    _set_stage(candidate_id, pre_hold, note or "Resumed from hold.")
    return get_job_candidate(candidate_id)


def set_candidate_rejected(candidate_id: int, note: str = ""):
    _set_stage(candidate_id, "Rejected", note or "Rejected by recruiter.")
    return get_job_candidate(candidate_id)


def set_candidate_selected(candidate_id: int, note: str = ""):
    _set_stage(candidate_id, "Selected", note or "Selected after interviews.")
    return get_job_candidate(candidate_id)


# ---------------------------------------------------------------------------
# Interviews (scheduling + status tracking)
# ---------------------------------------------------------------------------

def schedule_interview(candidate_id, round_name, interview_date, interview_time, interviewer,
                        meeting_link="", meeting_mode="Video Call"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO interviews (candidate_id, round_name, interview_date, interview_time, "
        "interviewer, meeting_link, meeting_mode, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'Scheduled', ?)",
        (candidate_id, round_name, str(interview_date), str(interview_time), interviewer.strip(),
         meeting_link.strip(), meeting_mode, _now()),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_interview(new_id)


def set_interview_meeting_link(interview_id: int, meeting_link: str):
    conn = get_connection()
    conn.execute("UPDATE interviews SET meeting_link = ? WHERE id = ?", (meeting_link, interview_id))
    conn.commit()
    conn.close()


def mark_invitation_sent(interview_id: int):
    conn = get_connection()
    conn.execute("UPDATE interviews SET invitation_sent = 1 WHERE id = ?", (interview_id,))
    conn.commit()
    conn.close()


def save_interview_notes(interview_id: int, technical_notes="", communication_notes="", overall_notes=""):
    conn = get_connection()
    conn.execute(
        "UPDATE interviews SET technical_notes = ?, communication_notes = ?, overall_notes = ?, feedback = ? WHERE id = ?",
        (technical_notes, communication_notes, overall_notes, overall_notes, interview_id),
    )
    conn.commit()
    conn.close()


def get_interview(interview_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_interviews_for_candidate(candidate_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM interviews WHERE candidate_id = ? ORDER BY id ASC", (candidate_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_interviews():
    conn = get_connection()
    rows = conn.execute(
        "SELECT iv.*, jc.name AS candidate_name, jc.job_id AS job_id, jo.title AS job_title "
        "FROM interviews iv "
        "JOIN job_candidates jc ON iv.candidate_id = jc.id "
        "JOIN job_openings jo ON jc.job_id = jo.id "
        "ORDER BY iv.id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_interview_status(interview_id: int, status: str, feedback: str = ""):
    conn = get_connection()
    conn.execute(
        "UPDATE interviews SET status = ?, feedback = ? WHERE id = ?",
        (status, feedback, interview_id),
    )
    conn.commit()
    conn.close()


def save_interview_ai_feedback(interview_id: int, feedback_dict: dict):
    """feedback_dict: {technical_score, communication_score, strengths, weaknesses, recommendation, summary}"""
    conn = get_connection()
    conn.execute(
        "UPDATE interviews SET ai_feedback_json = ? WHERE id = ?",
        (json.dumps(feedback_dict), interview_id),
    )
    conn.commit()
    conn.close()


def get_interview_ai_feedback(interview_id: int):
    conn = get_connection()
    row = conn.execute("SELECT ai_feedback_json FROM interviews WHERE id = ?", (interview_id,)).fetchone()
    conn.close()
    if row and row["ai_feedback_json"]:
        return json.loads(row["ai_feedback_json"])
    return None


# ---------------------------------------------------------------------------
# Offer & Onboarding (Section H) - lives on job_candidates until the
# employee record is actually created, so HR can track offer status even
# before Talent Management has anything to show.
# ---------------------------------------------------------------------------

def save_offer_letter(candidate_id: int, offer_text: str):
    conn = get_connection()
    conn.execute("UPDATE job_candidates SET offer_letter_text = ? WHERE id = ?", (offer_text, candidate_id))
    conn.commit()
    conn.close()


def mark_offer_sent(candidate_id: int):
    conn = get_connection()
    conn.execute("UPDATE job_candidates SET offer_sent = 1 WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    _set_stage(candidate_id, "Offer Sent", "Offer letter sent to candidate.")


def mark_offer_accepted(candidate_id: int):
    conn = get_connection()
    conn.execute("UPDATE job_candidates SET offer_accepted = 1 WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    _log_stage(candidate_id, "Offer Sent", "Candidate accepted the offer.")


def set_onboarding_details(candidate_id: int, department: str, manager: str, joining_date):
    conn = get_connection()
    conn.execute(
        "UPDATE job_candidates SET onboard_department = ?, onboard_manager = ?, onboard_joining_date = ? WHERE id = ?",
        (department.strip(), manager.strip(), str(joining_date), candidate_id),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Employees (onboarding + talent management)
# ---------------------------------------------------------------------------

def create_employee(candidate_id, name, email, department, designation, joining_date, manager, performance_rating=3.0):
    conn = get_connection()
    cur = conn.cursor()
    next_num = cur.execute("SELECT COUNT(*) AS c FROM employees").fetchone()["c"] + 1
    employee_code = f"EMP-{2000 + next_num}"
    cur.execute(
        "INSERT INTO employees (employee_code, candidate_id, name, email, department, designation, "
        "joining_date, performance_rating, manager, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (employee_code, candidate_id, name.strip(), email.strip(), department.strip(), designation.strip(),
         str(joining_date), float(performance_rating), manager.strip(), _now()),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    if candidate_id:
        _set_stage(candidate_id, "Onboarded", f"Employee record created ({employee_code}).")
    return get_employee(new_id)


def get_employee_by_candidate(candidate_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM employees WHERE candidate_id = ?", (candidate_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_employee(employee_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    conn.close()
    return dict(row) if row else None



def get_all_employees():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM employees ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_candidate_onboarded(candidate_id: int) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT id FROM employees WHERE candidate_id = ?", (candidate_id,)).fetchone()
    conn.close()
    return row is not None


def update_employee(employee_id, department=None, designation=None, performance_rating=None, manager=None):
    fields, values = [], []
    if department is not None:
        fields.append("department = ?"); values.append(department)
    if designation is not None:
        fields.append("designation = ?"); values.append(designation)
    if performance_rating is not None:
        fields.append("performance_rating = ?"); values.append(float(performance_rating))
    if manager is not None:
        fields.append("manager = ?"); values.append(manager)
    if not fields:
        return
    values.append(employee_id)
    conn = get_connection()
    conn.execute(f"UPDATE employees SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

def add_document(employee_id, doc_type, filename, filepath):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (employee_id, doc_type, filename, filepath, uploaded_at) VALUES (?, ?, ?, ?, ?)",
        (employee_id, doc_type, filename, filepath, _now()),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_documents_for_employee(employee_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM documents WHERE employee_id = ? ORDER BY id DESC", (employee_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_document(document_id: int):
    conn = get_connection()
    row = conn.execute("SELECT filepath FROM documents WHERE id = ?", (document_id,)).fetchone()
    conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()
    if row and row["filepath"] and os.path.exists(row["filepath"]):
        try:
            os.remove(row["filepath"])
        except OSError:
            pass


# ---------------------------------------------------------------------------
# AI Document Verification (Section I) - documents attached to a CANDIDATE
# during onboarding, separate from the employee-level `documents` table
# above (that one stays untouched, used by the existing Document
# Management page for post-onboarding record-keeping).
# ---------------------------------------------------------------------------

def add_candidate_document(candidate_id, doc_type, filename, filepath):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO candidate_documents (candidate_id, doc_type, filename, filepath, verification_status, uploaded_at) "
        "VALUES (?, ?, ?, ?, 'Pending', ?)",
        (candidate_id, doc_type, filename, filepath, _now()),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_candidate_documents(candidate_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM candidate_documents WHERE candidate_id = ? ORDER BY id DESC", (candidate_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_candidate_document_verification(document_id: int, status: str, summary: str):
    conn = get_connection()
    conn.execute(
        "UPDATE candidate_documents SET verification_status = ?, verification_summary = ? WHERE id = ?",
        (status, summary, document_id),
    )
    conn.commit()
    conn.close()
