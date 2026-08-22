import streamlit as st
import re
from utils.ai import ask_ai


def scrub_placeholders(text: str) -> str:
    """
    Remove any bracketed placeholder text (e.g. "[date]", "[Name]")
    that the model inserts despite being told not to. Guarantees none
    reach the final email regardless of what the model actually does.
    """

    # "by [date]" / "before [Date]" etc. read naturally as "at your
    # earliest convenience" once the bracket is gone.
    text = re.sub(
        r"\b(by|before|on)\s*\[[^\]]*\]",
        "at your earliest convenience",
        text,
        flags=re.IGNORECASE,
    )

    # Any other bracketed placeholder is simply dropped.
    text = re.sub(r"\[[^\]]*\]", "", text)

    # Clean up any double spaces left behind.
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text


def ai_email_generator_page():

    st.title("AI Email Generator")
    st.caption("Generate professional recruitment emails using AI.")
    st.markdown("---")

    candidates = st.session_state.get("candidates", [])

    if not candidates:
        st.info(
            "No candidates available.\n\n"
            "Analyze resumes first."
        )
        return

    candidate_names = [
        c.get("name", "Unknown")
        for c in candidates
    ]

    selected_candidate = st.selectbox(
        "Candidate",
        candidate_names
    )

    candidate = next(
        (
            c
            for c in candidates
            if c.get("name") == selected_candidate
        ),
        {}
    )

    # Using `or` instead of dict.get(key, default) so an empty string
    # (key present but blank — e.g. recommended_role: "") also falls
    # back to the default, not just a missing key. This is what was
    # causing the empty "Offer Letter – " subject line.
    email = candidate.get("email") or ""
    role = candidate.get("recommended_role") or "Software Engineer"
    experience = candidate.get("experience") or "Fresher"
    education = candidate.get("education") or "Not Available"
    score = candidate.get("score") or 0

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Candidate")

        st.write(f"**Name:** {selected_candidate}")
        st.write(f"**Email:** {email}")
        st.write(f"**Role:** {role}")
        st.write(f"**Experience:** {experience}")
        st.write(f"**Education:** {education}")
        st.write(f"**Match Score:** {score}%")

    with col2:

        st.subheader("Recruitment")

        recruiter = st.text_input(
            "Recruiter",
            "HR Recruiter"
        )

        company = st.text_input(
            "Company",
            "ABC Technologies"
        )

        email_type = st.selectbox(

            "Email Type",

            [

                "Interview Invitation",

                "Interview Reminder",

                "Offer Letter",

                "Joining Instructions",

                "Follow-up Email",

                "Rejection Email"

            ]

        )

        salary = st.text_input(
            "Annual CTC (₹)",
            "₹12,00,000 per annum"
        )

        employment = st.selectbox(

            "Employment Type",

            [

                "Full-Time",

                "Internship",

                "Contract"

            ]

        )

        location = st.text_input(
            "Location",
            "Hyderabad"
        )

        meeting_date = st.date_input(
            "Interview / Joining Date"
        )

        meeting_time = st.time_input(
            "Time"
        )

    formatted_date = meeting_date.strftime(
        "%d %B %Y"
    )

    formatted_time = meeting_time.strftime(
        "%I:%M %p"
    )

    subject_map = {

        "Interview Invitation":
            f"Interview Invitation – {role}",

        "Interview Reminder":
            f"Interview Reminder – {role}",

        "Offer Letter":
            f"Offer Letter – {role}",

        "Joining Instructions":
            f"Joining Instructions – {role}",

        "Follow-up Email":
            "Follow-up Regarding Your Application",

        "Rejection Email":
            f"Application Update – {role}"

    }

    subject = subject_map[email_type]

    st.markdown("---")

    # =====================================================
    # GENERATE EMAIL
    # =====================================================

    if st.button(
        "Generate Email",
        use_container_width=True
    ):

        content_instructions_by_type = {

            "Interview Invitation": (
                "- Warmly invite the candidate to interview for the role\n"
                "- Mention interview date, time, and location\n"
                "- Include brief preparation instructions (documents to "
                "bring, what to expect)"
            ),

            "Interview Reminder": (
                "- Politely remind the candidate of their upcoming interview\n"
                "- Restate the interview date and time\n"
                "- Offer to help with any questions before the interview"
            ),

            "Offer Letter": (
                "- Congratulate the candidate warmly\n"
                "- Clearly state the job role, employment type, annual CTC, "
                "joining date, and work location\n"
                "- Convey enthusiasm about them joining the team\n"
                "- Ask the candidate to confirm their acceptance"
            ),

            "Joining Instructions": (
                "- Welcome the candidate to the company\n"
                "- Mention reporting date, time, and office location\n"
                "- List documents to bring on the first day"
            ),

            "Follow-up Email": (
                "- Thank the candidate for their time and interest\n"
                "- Ask them to confirm their continued availability/interest"
            ),

            "Rejection Email": (
                "- Thank the candidate sincerely for their time and effort\n"
                "- Deliver the decision respectfully and without being blunt\n"
                "- Wish them genuine success in their future opportunities"
            ),

        }

        content_instructions = content_instructions_by_type[email_type]

        prompt = f"""
You are a senior HR Recruiter at {company}, writing the body content of a
professional recruitment email.

Candidate Information
---------------------
Name: {selected_candidate}
Role: {role}
Experience: {experience}
Education: {education}

Recruiter Information
---------------------
Recruiter: {recruiter}
Company: {company}

Employment Details
------------------
Employment Type: {employment}
Annual CTC: {salary}
Location: {location}

Important Dates
---------------
Date: {formatted_date}
Time: {formatted_time}

Email Type
----------
{email_type}

Write ONLY the informative content of the email, as flowing
professional prose (plain sentences, no bullet points, no headings).

Do NOT include:
- A greeting/salutation (e.g. "Dear ...") — that is added separately
- A sign-off/closing (e.g. "Kind Regards", the recruiter's name, or
  the company name) — that is added separately
- A subject line, HTML, code blocks, or square-bracket placeholders
  such as [Name] or [Date] under ANY circumstance — if you need to
  reference a date you were not given (e.g. a response deadline),
  phrase it naturally instead, such as "at your earliest convenience"
- Phone numbers or company addresses
- Any explanation before or after the content
- Content for any email type OTHER than "{email_type}" — write ONLY
  what applies to this one email type, nothing else

Tone: warm, confident, professional business English. Write complete,
considered sentences — not curt or robotic.

Content to cover for this "{email_type}" email:

{content_instructions}

Return ONLY the content sentences for this one email type — nothing else.
"""

        with st.spinner(
            "Generating Email..."
        ):

            raw_content = ask_ai(prompt).strip()

        if raw_content.startswith("Error:"):

            st.session_state["email_body"] = raw_content

        else:

            # Break the model's flat prose into paragraphs ourselves,
            # rather than depending on the model to self-delimit
            # (a literal marker or a JSON array both proved unreliable
            # with this local model — one got echoed back garbled,
            # the other caused the model to under-fill the schema).
            #
            # Also strip any stray "--" / "---" separator artifacts,
            # in case the model still tries to section its output,
            # and scrub any leftover bracketed placeholders.
            flat_content = scrub_placeholders(raw_content)
            flat_content = re.sub(r"-{2,}", " ", flat_content)
            flat_content = re.sub(r"\s+", " ", flat_content).strip()

            sentences = re.split(r"(?<=[.!?])\s+", flat_content)
            sentences = [s.strip() for s in sentences if s.strip()]

            sentences_per_paragraph = 2

            content_paragraphs = [
                " ".join(sentences[i:i + sentences_per_paragraph])
                for i in range(0, len(sentences), sentences_per_paragraph)
            ]

            # Greeting and sign-off are fixed, known text — Python
            # assembles these directly instead of trusting the model
            # to reproduce them exactly and in the right place.
            all_paragraphs = (
                [f"Dear {selected_candidate},"]
                + content_paragraphs
                + ["Kind Regards,", recruiter, company]
            )

            st.session_state["email_body"] = "\n\n".join(all_paragraphs)

    # =====================================================
    # EMAIL PREVIEW
    # =====================================================

    if "email_body" in st.session_state:

        st.markdown("## Email Preview")

        with st.container(border=True):

            st.write(f"**To:** {email}")

            st.write(f"**Subject:** {subject}")

            st.divider()

            # Real double newlines here, so Markdown renders actual
            # paragraph breaks instead of tightly stacked lines.
            st.markdown(st.session_state["email_body"])

        st.button(
            "Send Email",
            use_container_width=True,
            disabled=not email
        )

    else:

        st.info(
            "Select a candidate and click **Generate Email**."
        )

    st.markdown("---")

    st.caption(
        "AI Recruitment & Talent Management Copilot • AI Email Generator"
    )

# ==========================================================
# Temporary compatibility patch
# ==========================================================

def check_cache_replay_rules(*args, **kwargs):
    """
    Compatibility stub for mismatched Streamlit installations.
    """
    return None