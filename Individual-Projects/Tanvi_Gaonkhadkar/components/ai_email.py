# ==========================================================
# components/interview/ai_email.py
# ==========================================================

from unittest import result

import streamlit as st
from backend.connect_mail import send_email


# ==========================================================
# Email Templates
# ==========================================================

def generate_email(

    candidate_name,

    role,

    round_name,

    status,

    interview_date,

    interview_time,

    meeting_link

):

    if status in ("Passed", "Next Round"):

        return f"""
Subject: Congratulations! Next Interview Round

Dear {candidate_name},

Congratulations!

You have successfully cleared the {round_name}
for the position of {role}.

Your next interview has been scheduled.

Interview Details

Role:
{role}

Interview Round:
Next Round

Date:
{interview_date}

Time:
{interview_time}

Meeting Link:
{meeting_link}

Please be available 10 minutes before the interview.

Regards,

Talent Acquisition Team
"""

    elif status == "Rejected":

        return f"""
Subject: Application Status

Dear {candidate_name},

Thank you for taking the time to interview with us.

After careful consideration,
we have decided not to move forward with your application.

We sincerely appreciate your interest
and wish you success in your future career.

Regards,

Talent Acquisition Team
"""

    elif status == "Hold":

        return f"""
Subject: Interview Update

Dear {candidate_name},

Thank you for interviewing with us.

Your profile is currently under review.

We will contact you soon regarding the
next steps in the recruitment process.

Regards,

Talent Acquisition Team
"""

    elif status == "Selected":

        return f"""
Subject: Congratulations! You are Selected

Dear {candidate_name},

Congratulations!

We are delighted to inform you that you
have been selected for the role of

{role}

Our HR Team will shortly connect with you
regarding the offer letter and onboarding.

Welcome to the team.

Regards,

Talent Acquisition Team
"""

    elif status == "Offer Sent":

        return f"""
Subject: Offer Letter

Dear {candidate_name},

Congratulations!

Please find your offer details below.

Role:
{role}

Our HR team is looking forward to
welcoming you.

Regards,

Talent Acquisition Team
"""

    else:

        return f"""
Subject: Interview Invitation

Dear {candidate_name},

Congratulations!

You have been shortlisted for the role of

{role}

Interview Details

Interview Round:
{round_name}

Date:
{interview_date}

Time:
{interview_time}

Meeting Link:
{meeting_link}

Please join the meeting 10 minutes early.

Regards,

Talent Acquisition Team
"""


# ==========================================================
# Draw Email Section
# ==========================================================

def draw_ai_email(candidate, interview):

    st.subheader("📧 AI Email Draft")

    email = generate_email(

        candidate["candidate_name"],

        candidate["role"],

        interview["round"],

        interview["status"],

        interview["date"],

        interview["time"],

        interview["link"]

    )

    email = st.text_area(

        "Generated Email",

        value=email,

        height=320

    )

    c1, c2 = st.columns(2)

    with c1:

        st.download_button(

            "📥 Download Email",

            data=email,

            file_name=f"{candidate['candidate_name']}_Email.txt",

            mime="text/plain",

            use_container_width=True

        )

    with c2:

        if st.button(

                "📨 Send Email",

                use_container_width=True

            ):
                lines = [line for line in email.split("\n") if line.strip()]

                subject = lines[0].replace(
                    "Subject:",
                    ""
                ).strip()

                body = "\n".join(lines[1:])

                result = send_email(

                    candidate["email"],

                    subject,

                    body

                )

                if result is True:

                    st.success("✅ Email sent successfully!")

                else:

                    st.error(result)

    st.divider()