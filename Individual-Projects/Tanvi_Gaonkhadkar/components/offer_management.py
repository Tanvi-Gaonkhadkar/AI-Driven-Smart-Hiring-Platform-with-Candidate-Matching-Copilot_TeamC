# ==========================================================
# components/interview/offer_management.py
# ==========================================================

import sqlite3
import streamlit as st

DB_PATH = "database/recruitment.db"


# ==========================================================
# Database
# ==========================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# Offer Letter Generator
# ==========================================================

def generate_offer_letter(candidate):

    return f"""
======================================================
                 OFFER LETTER
======================================================

Candidate Name
{candidate['candidate_name']}

Role
{candidate['role']}

Congratulations!

We are delighted to offer you the position of

{candidate['role']}

Employment Type
Full Time

Work Mode
Hybrid

Reporting Manager
Talent Acquisition Team

Joining Date
To Be Decided

------------------------------------------------------

Please acknowledge your acceptance of this offer
within 7 days.

We look forward to working with you.

Regards,

Talent Acquisition Team

======================================================
"""


# ==========================================================
# Update Offer Status
# ==========================================================

def mark_offer_sent(candidate):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE interviews

        SET status='Offer Sent'

        WHERE id=?
        """,
        (
            candidate["interview_id"],
        )
    )

    cursor.execute(
        """
        UPDATE candidates

        SET status='Offer Sent'

        WHERE id=?
        """,
        (
            candidate["candidate_id"],
        )
    )

    conn.commit()
    conn.close()


# ==========================================================
# Draw Offer Management
# ==========================================================

def draw_offer_management(candidate):

    st.subheader("📄 Offer Management")

    if candidate["status"] not in (

        "Selected",

        "Offer Sent"

    ):

        st.info(
            """
Offer Management becomes available
only after candidate selection.
"""
        )

        st.divider()

        return

    offer = generate_offer_letter(candidate)

    st.text_area(

        "Generated Offer Letter",

        value=offer,

        height=350

    )

    c1, c2 = st.columns(2)

    with c1:

        st.download_button(

            "📥 Download Offer Letter",

            data=offer,

            file_name=f"{candidate['candidate_name']}_Offer_Letter.txt",

            mime="text/plain",

            use_container_width=True

        )

    with c2:

        if candidate["status"] == "Offer Sent":

            st.success("✅ Offer Already Sent")

        else:

            if st.button(

                "📨 Mark Offer Sent",

                type="primary",

                use_container_width=True

            ):

                mark_offer_sent(candidate)

                st.success(

                    "Offer marked as sent successfully."

                )

                st.rerun()

    st.divider()