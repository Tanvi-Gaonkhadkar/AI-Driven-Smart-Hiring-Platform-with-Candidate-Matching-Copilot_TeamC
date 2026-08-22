"""
Email delivery for automatic interview invitations (Interview Scheduling
module). Uses Python's built-in smtplib - no extra dependency.

Configure in .env (all optional - if unset, the app just shows the
invitation text on screen instead of sending it, exactly like the AI
service falls back gracefully when no API key is set):

    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=you@example.com
    SMTP_PASSWORD=your_app_password
    SMTP_FROM_EMAIL=you@example.com
    SMTP_FROM_NAME=YourTalentPilot Recruiting
"""

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "YourTalentPilot Recruiting")


def is_configured() -> bool:
    return bool(SMTP_HOST and SMTP_USERNAME and SMTP_PASSWORD and SMTP_FROM_EMAIL)


def _send_raw(to_email: str, subject: str, body: str) -> bool:
    """Shared low-level sender used by every specific email helper below."""
    if not is_configured() or not to_email:
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        return False


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    General-purpose email generator - the one place every page in the app
    should go through to actually send mail (interview invitations, offer
    letters, or anything else). Returns whether it was actually sent;
    always safe to call even with SMTP unconfigured (just returns False).
    """
    return _send_raw(to_email, subject, body)


def build_interview_invitation(candidate_name, job_title, round_name, interview_date, interview_time, interviewer):
    subject = f"Interview Invitation — {job_title} ({round_name})"
    body = (
        f"Hi {candidate_name},\n\n"
        f"You've been shortlisted to move forward for the {job_title} role. "
        f"We'd like to invite you to the following interview:\n\n"
        f"  Round:       {round_name}\n"
        f"  Date:        {interview_date}\n"
        f"  Time:        {interview_time}\n"
        f"  Interviewer: {interviewer}\n\n"
        f"Please reply to confirm your availability. If this time doesn't work, "
        f"let us know and we'll find an alternative slot.\n\n"
        f"Looking forward to speaking with you.\n\n"
        f"Best regards,\n{SMTP_FROM_NAME}"
    )
    return subject, body


def send_interview_invitation(to_email, candidate_name, job_title, round_name, interview_date, interview_time, interviewer):
    """
    Sends the invitation if SMTP is configured. Returns (sent: bool, subject, body)
    so the caller can always display the invitation text, whether or not it
    was actually emailed.
    """
    subject, body = build_interview_invitation(
        candidate_name, job_title, round_name, interview_date, interview_time, interviewer
    )
    sent = _send_raw(to_email, subject, body)
    return sent, subject, body


def send_offer_email(to_email: str, candidate_name: str, job_title: str, offer_text: str):
    """
    Sends the AI-generated offer letter (Section H). Returns (sent, subject,
    body) - same pattern as send_interview_invitation, so the UI can always
    show what would have been sent even without SMTP configured.
    """
    subject = f"Your Offer Letter — {job_title}"
    sent = _send_raw(to_email, subject, offer_text)
    return sent, subject, offer_text
