import datetime

import streamlit as st
from styles.theme import inject_global_styles, COLORS
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from utils.auth import require_login
from utils.ocr import extract_text_from_document, is_ocr_available
from services import database, email_service, ai_service

st.set_page_config(page_title="Interview Management | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header(
    "Interview Management",
    "The complete recruitment pipeline — from Applied to Onboarded, in one place",
)

database.init_db()

# ---------------------------------------------------------------------------
# Page-scoped styling: avatar circles, stage badges, stat pills, and a
# sticky progress rail. Uses the same marker + :has() sibling technique as
# the floating AI Assistant (this project's pinned streamlit==1.38.0 has
# no st.container(key=...) support), so the rail's own st.container() can
# be pinned to the top of the viewport while scrolling through sections.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        div[data-testid="stElementContainer"]:has(.im-rail-marker),
        div[data-testid="stElementContainer"]:has(.im-rail-marker) + div[data-testid="stElementContainer"] {
            position: sticky !important;
            top: 48px;
            z-index: 999;
        }
        .im-avatar {
            width: 52px; height: 52px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 800; font-size: 18px; flex-shrink: 0;
        }
        .im-badge {
            display: inline-block; padding: 3px 11px; border-radius: 12px;
            font-size: 12px; font-weight: 700;
        }
        .im-chip {
            display: inline-block; padding: 2px 9px; border-radius: 8px;
            font-size: 11px; font-weight: 600; margin: 2px 3px 2px 0;
        }
        .im-stat { text-align: center; }
        .im-stat-value { font-size: 22px; font-weight: 800; font-family: monospace; }
        .im-stat-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.6; }
    </style>
    """,
    unsafe_allow_html=True,
)

STAGE_COLOR_KEY = {
    "Applied": "text_secondary", "AI Reviewed": "text_secondary", "Shortlisted": "info",
    "Interview Round 1": "primary", "Interview Round 2": "primary", "Interview Round 3": "primary",
    "Selected": "success", "Offer Sent": "success", "Onboarded": "success",
    "Rejected": "danger", "Hold": "warning",
}


def stage_color(stage: str) -> str:
    return COLORS.get(STAGE_COLOR_KEY.get(stage, "text_secondary"))


def stage_badge_html(stage: str) -> str:
    c = stage_color(stage)
    return f"<span class='im-badge' style='background:{c}22; color:{c};'>{stage}</span>"


def chip_html(text: str) -> str:
    return f"<span class='im-chip' style='background:{COLORS['surface_muted']}; color:{COLORS['text_secondary']};'>{text}</span>"


class workflow_section:
    """Thin wrapper around st.expander adding a numbered 'stop' badge and a
    lock state — mirrors the WorkflowSection pattern from the design
    reference (numbered stop, title, subtitle, lock message)."""

    def __init__(self, stop, title, subtitle, locked=False, force_open_key=None, badge=None):
        self.stop, self.title, self.subtitle, self.locked = stop, title, subtitle, locked
        self.badge = badge
        forced = st.session_state.get("im_focus_section") == stop
        self._expander = st.expander(
            f"**{stop}**   {title}", expanded=(forced or not locked and stop in ("A", "B")),
        )

    def __enter__(self):
        self._expander.__enter__()
        st.caption(self.subtitle)
        if self.badge:
            st.markdown(self.badge, unsafe_allow_html=True)
        if self.locked:
            st.info("🔒 Unlocks once the previous stop is complete.")
        return self._expander

    def __exit__(self, *a):
        return self._expander.__exit__(*a)


# ---------------------------------------------------------------------------
# Candidate picker + compact pipeline overview
# ---------------------------------------------------------------------------
all_candidates = database.get_all_job_candidates()

if not all_candidates:
    st.info("No candidates yet. Screen resumes on the **ATS Scoring** page first.")
    st.page_link("pages/9_ATS_Screening.py", label="Go to ATS Scoring →")
    render_global_chat()
    st.stop()

st.markdown("**Pipeline Overview**")
for c in all_candidates:
    with st.container(border=True):
        cols = st.columns([2.2, 1.6, 2, 1.2])
        cols[0].markdown(f"**{c['name']}**  \n{c['job_title']} (`{c['job_code']}`)")
        cols[1].markdown(f"ATS: **{c['ats_score']}**")
        cols[2].markdown(stage_badge_html(c["stage"]), unsafe_allow_html=True)
        if cols[3].button("Open Workflow →", key=f"open_{c['id']}", use_container_width=True):
            st.session_state["im_active_candidate"] = c["id"]
            st.session_state.pop("im_focus_section", None)
            st.rerun()

active_id = st.session_state.get("im_active_candidate")
if not active_id or not any(c["id"] == active_id for c in all_candidates):
    st.info("Select a candidate above and click **Open Workflow** to start their recruitment pipeline.")
    render_global_chat()
    st.stop()

candidate = database.get_job_candidate(active_id)
job = database.get_job_opening(candidate["job_id"])
interviews = database.get_interviews_for_candidate(candidate["id"])
employee = database.get_employee_by_candidate(candidate["id"])
matched = [s for s in (candidate["matched_skills"] or "").split(",") if s.strip()]
missing = [s for s in (candidate["missing_skills"] or "").split(",") if s.strip()]
total_skills = len(matched) + len(missing)
skill_match_pct = round((len(matched) / total_skills) * 100) if total_skills else candidate["ats_score"]

st.divider()

# ---------------------------------------------------------------------------
# Section A: Recruitment Progress Rail (sticky, clickable)
# ---------------------------------------------------------------------------
st.markdown('<span class="im-rail-marker"></span>', unsafe_allow_html=True)
with st.container(border=True):
    is_terminal = candidate["stage"] in ("Rejected", "Hold")
    if is_terminal:
        c = stage_color(candidate["stage"])
        st.markdown(
            f"<span class='im-badge' style='background:{c}22; color:{c};'>"
            f"{'⏸ On Hold' if candidate['stage'] == 'Hold' else '✕ Rejected'} — rail paused at last active stop</span>",
            unsafe_allow_html=True,
        )
    active_idx = database.STAGE_ORDER.index(candidate["stage"]) if candidate["stage"] in database.STAGE_ORDER else -1
    SECTION_FOR_STAGE = {
        "Applied": "B", "AI Reviewed": "B", "Shortlisted": "B",
        "Interview Round 1": "C", "Interview Round 2": "C", "Interview Round 3": "C",
        "Selected": "G", "Offer Sent": "H", "Onboarded": "J",
    }
    rail_cols = st.columns(len(database.STAGE_ORDER))
    for i, (col, stage) in enumerate(zip(rail_cols, database.STAGE_ORDER)):
        completed = not is_terminal and i < active_idx
        current = not is_terminal and i == active_idx
        c = COLORS["success"] if completed else (COLORS["primary"] if current else COLORS["text_secondary"])
        icon = "✅" if completed else ("🔵" if current else "⚪")
        with col:
            st.markdown(
                f"<div style='text-align:center;'><div style='font-size:18px;'>{icon}</div>"
                f"<div style='font-size:10px; font-weight:700; color:{c}; line-height:1.2; margin-top:2px;'>{stage}</div></div>",
                unsafe_allow_html=True,
            )
            if st.button("↦", key=f"rail_{i}", help=f"Review {stage}", use_container_width=True):
                st.session_state["im_focus_section"] = SECTION_FOR_STAGE.get(stage, "B")
                st.rerun()

# ---------------------------------------------------------------------------
# Section B: Candidate Summary Card
# ---------------------------------------------------------------------------
with workflow_section("B", "Candidate Summary", "Everything HR needs to know about this candidate at a glance"):
    initials = "".join(w[0] for w in candidate["name"].split()[:2]).upper()
    top1, top2 = st.columns([3, 2])
    with top1:
        st.markdown(
            f"<div style='display:flex; gap:14px; align-items:center;'>"
            f"<div class='im-avatar' style='background:{COLORS['primary']}22; color:{COLORS['primary']};'>{initials}</div>"
            f"<div><div style='font-weight:800; font-size:17px;'>{candidate['name']} "
            f"{stage_badge_html(candidate['stage'])}</div>"
            f"<div style='opacity:0.7; font-size:13px;'>{job['title']} · {job['department']}</div>"
            f"<div style='opacity:0.6; font-size:12px; margin-top:4px;'>"
            f"✉️ {candidate['email'] or '—'} &nbsp; 📞 {candidate['phone'] or '—'} &nbsp; "
            f"📅 Applied {candidate['created_at']}</div></div></div>",
            unsafe_allow_html=True,
        )
    with top2:
        s1, s2, s3 = st.columns(3)
        for col, label, value in [
            (s1, "ATS Score", candidate["ats_score"]),
            (s2, "Skill Match", f"{skill_match_pct}%"),
            (s3, "Experience", "—" if not job else job.get("department", "—")),
        ]:
            col.markdown(
                f"<div class='im-stat'><div class='im-stat-value' style='color:{COLORS['success']};'>{value}</div>"
                f"<div class='im-stat-label'>{label}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("**Resume Summary**")
    resume_preview = (candidate["resume_text"] or "")[:400]
    st.write(resume_preview + ("..." if len(candidate["resume_text"] or "") > 400 else ""))
    st.markdown(
        "".join(chip_html(s) for s in matched) or "_No matched skills recorded._",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Section C: Interview Scheduling
# ---------------------------------------------------------------------------
c_locked = candidate["stage"] not in (
    "Shortlisted", "Interview Round 1", "Interview Round 2", "Interview Round 3"
)
with workflow_section("C", "Interview Scheduling", "Assign an interviewer, pick a slot, and send the invite", locked=c_locked):
    if not c_locked:
        round_tab = st.radio(
            "Round", ["Interview Round 1", "Interview Round 2", "Interview Round 3"],
            horizontal=True, key="im_round_tab",
        )
        existing_iv = next((iv for iv in interviews if iv["round_name"] == round_tab), None)

        with st.form(f"schedule_form_{round_tab}"):
            fcol1, fcol2, fcol3 = st.columns(3)
            with fcol1:
                interviewer = st.text_input(
                    "Interviewer", value=existing_iv["interviewer"] if existing_iv else "",
                )
            with fcol2:
                meeting_mode = st.selectbox(
                    "Meeting Mode", ["Video Call", "Phone Call", "On-site"],
                    index=["Video Call", "Phone Call", "On-site"].index(existing_iv["meeting_mode"]) if existing_iv and existing_iv["meeting_mode"] in ["Video Call", "Phone Call", "On-site"] else 0,
                )
            with fcol3:
                pass
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                interview_date = st.date_input(
                    "Date",
                    value=datetime.date.fromisoformat(existing_iv["interview_date"]) if existing_iv else datetime.date.today(),
                )
            with dcol2:
                interview_time = st.time_input(
                    "Time",
                    value=datetime.datetime.strptime(existing_iv["interview_time"], "%H:%M:%S").time()
                    if existing_iv and len(existing_iv["interview_time"].split(":")) == 3
                    else datetime.time(10, 0),
                )
            save_schedule = st.form_submit_button(
                "Update Schedule" if existing_iv else "Schedule Interview", use_container_width=True,
            )

        if save_schedule:
            if not interviewer.strip():
                st.error("Interviewer is required.")
            elif existing_iv:
                database.update_interview_status(existing_iv["id"], existing_iv["status"], existing_iv["feedback"] or "")
                st.success("Schedule updated.")
                st.rerun()
            else:
                database.schedule_interview(
                    candidate["id"], round_tab, interview_date, interview_time,
                    interviewer, meeting_mode=meeting_mode,
                )
                while (candidate["stage"] in database.STAGE_ORDER and candidate["stage"] != round_tab
                       and database.STAGE_ORDER.index(candidate["stage"]) < database.STAGE_ORDER.index(round_tab)):
                    candidate = database.move_candidate_to_next_stage(candidate["id"])
                st.rerun()

        if existing_iv:
            lcol1, lcol2 = st.columns(2)
            with lcol1:
                if st.button(
                    "🔗 Regenerate Meeting Link" if existing_iv["meeting_link"] else "🔗 Generate Meeting Link",
                    use_container_width=True,
                ):
                    link = f"https://meet.yourtalentpilot.dev/{candidate['id']}-{round_tab.replace(' ', '-').lower()}"
                    database.set_interview_meeting_link(existing_iv["id"], link)
                    st.rerun()
            with lcol2:
                already_sent = bool(existing_iv["invitation_sent"])
                if st.button(
                    "✅ Invitation Sent" if already_sent else "✉️ Send AI Interview Invitation",
                    disabled=already_sent, use_container_width=True, type="primary",
                ):
                    sent, subject, body = email_service.send_interview_invitation(
                        candidate["email"], candidate["name"], job["title"], round_tab,
                        existing_iv["interview_date"], existing_iv["interview_time"], existing_iv["interviewer"],
                    )
                    database.mark_invitation_sent(existing_iv["id"])
                    if sent:
                        st.success(f"Invitation emailed to {candidate['email']}.")
                    else:
                        st.success("Invitation generated.")
                        with st.expander("Preview"):
                            st.markdown(f"**Subject:** {subject}")
                            st.text(body)
                    st.rerun()
            if existing_iv["meeting_link"]:
                st.caption(f"🔗 {existing_iv['meeting_link']}")

# ---------------------------------------------------------------------------
# Section D: AI Interview Preparation
# ---------------------------------------------------------------------------
with workflow_section("D", "AI Interview Preparation", "Candidate summary and suggested questions before you walk in", locked=c_locked):
    if not c_locked:
        if not ai_service.is_configured():
            st.warning("Add a Gemini API key (or set AI_PROVIDER=ollama) in `.env` to enable AI prep.")
        else:
            if st.button("🧠 Generate AI Candidate Summary", key="ai_prep_summary"):
                with st.spinner("Reading resume..."):
                    st.session_state["im_ai_summary"] = ai_service.generate_candidate_summary(
                        candidate["name"], candidate["resume_text"] or "", job["title"],
                    )
            summ = st.session_state.get("im_ai_summary")
            if summ:
                st.markdown("**Experience:** " + summ.get("experience_summary", ""))
                st.markdown("**Resume Summary:** " + summ.get("resume_summary", ""))
                st.markdown("**Projects**")
                for p in summ.get("projects", []):
                    st.markdown(f"- {p}")

            st.write("")
            qcol1, qcol2 = st.columns([1, 3])
            with qcol1:
                q_type = st.selectbox("Question Type", ["Technical", "HR Questions", "Behavioural"], key="im_q_type")
                gen_q = st.button("Generate Questions", use_container_width=True)
            if gen_q:
                with st.spinner("Generating questions..."):
                    st.session_state["im_questions"] = ai_service.generate_interview_questions(
                        candidate["name"], job["title"], q_type,
                    )
            questions = st.session_state.get("im_questions")
            if questions:
                for q in questions.get("questions", []):
                    st.markdown(f"- {q}")

# ---------------------------------------------------------------------------
# Section E: Conduct Interview
# ---------------------------------------------------------------------------
active_round_iv = next((iv for iv in interviews if iv["round_name"] == candidate["stage"]), None)
e_locked = c_locked or active_round_iv is None
with workflow_section("E", "Conduct Interview", "Capture notes during or right after the interview", locked=e_locked):
    if not e_locked:
        technical_notes = st.text_area("Technical Notes", value=active_round_iv["technical_notes"] or "")
        communication_notes = st.text_area("Communication Notes", value=active_round_iv["communication_notes"] or "")
        overall_notes = st.text_area("Overall Observations", value=active_round_iv["overall_notes"] or "")
        if st.button("Save Notes", use_container_width=True):
            database.save_interview_notes(active_round_iv["id"], technical_notes, communication_notes, overall_notes)
            st.success("Notes saved.")
            st.rerun()

# ---------------------------------------------------------------------------
# Section F: AI Interview Feedback
# ---------------------------------------------------------------------------
with workflow_section("F", "AI Interview Feedback", "Turns your notes into a structured scorecard", locked=e_locked):
    if not e_locked:
        combined_notes = "\n".join(filter(None, [
            f"Technical: {active_round_iv['technical_notes']}" if active_round_iv["technical_notes"] else "",
            f"Communication: {active_round_iv['communication_notes']}" if active_round_iv["communication_notes"] else "",
            f"Overall: {active_round_iv['overall_notes']}" if active_round_iv["overall_notes"] else "",
        ]))
        gen_disabled = not ai_service.is_configured() or not combined_notes.strip()
        if st.button("✨ Generate AI Feedback", disabled=gen_disabled, use_container_width=True, type="primary"):
            with st.spinner("Scoring interview..."):
                feedback = ai_service.generate_interview_feedback(
                    candidate["name"], job["title"], candidate["stage"], combined_notes,
                )
            database.save_interview_ai_feedback(active_round_iv["id"], feedback)
            database.update_interview_status(active_round_iv["id"], "Completed", active_round_iv["overall_notes"] or "")
            st.rerun()

        ai_feedback = database.get_interview_ai_feedback(active_round_iv["id"])
        if ai_feedback:
            sc1, sc2 = st.columns(2)
            sc1.metric("Technical Score", f"{ai_feedback.get('technical_score', '—')}/100")
            sc2.metric("Communication Score", f"{ai_feedback.get('communication_score', '—')}/100")
            st.write(ai_feedback.get("summary", ""))
            st.markdown("**Strengths**")
            for s in ai_feedback.get("strengths", []):
                st.markdown(f"- {s}")
            st.markdown("**Weaknesses**")
            for w in ai_feedback.get("weaknesses", []):
                st.markdown(f"- {w}")
            rec = ai_feedback.get("recommendation", "")
            st.markdown(f"**AI Recommendation:** {stage_badge_html(rec) if rec in STAGE_COLOR_KEY else rec}", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Section G: Decision
# ---------------------------------------------------------------------------
g_locked = candidate["stage"] in ("Rejected", "Onboarded")
with workflow_section("G", "Decision", "Move this candidate forward, on hold, or out of the pipeline", locked=g_locked):
    if not g_locked:
        d1, d2, d3, d4 = st.columns(4)
        if d1.button("▶ Proceed to Next Round", use_container_width=True):
            database.move_candidate_to_next_stage(candidate["id"])
            if active_round_iv:
                database.update_interview_status(active_round_iv["id"], "Qualified for Next Round", active_round_iv["overall_notes"] or "")
            st.rerun()
        if d2.button("✅ Select", use_container_width=True, type="primary"):
            database.set_candidate_selected(candidate["id"])
            if active_round_iv:
                database.update_interview_status(active_round_iv["id"], "Selected", active_round_iv["overall_notes"] or "")
            st.rerun()
        if d3.button("⏸ Hold", use_container_width=True):
            database.set_candidate_hold(candidate["id"])
            st.rerun()
        if d4.button("✕ Reject", use_container_width=True):
            database.set_candidate_rejected(candidate["id"])
            if active_round_iv:
                database.update_interview_status(active_round_iv["id"], "Rejected", active_round_iv["overall_notes"] or "")
            st.rerun()
        if candidate["stage"] == "Hold":
            if st.button("▶ Resume from Hold", use_container_width=True):
                database.resume_candidate_from_hold(candidate["id"])
                st.rerun()

# ---------------------------------------------------------------------------
# Section H: Offer & Onboarding
# ---------------------------------------------------------------------------
h_locked = candidate["stage"] not in ("Selected", "Offer Sent", "Onboarded")
with workflow_section("H", "Offer & Onboarding", "Generate the offer, confirm acceptance, and set up the new hire", locked=h_locked):
    if not h_locked:
        if ai_service.is_configured():
            if st.button("📄 Generate AI Offer Letter", use_container_width=True):
                with st.spinner("Drafting offer letter..."):
                    offer_text = ai_service.generate_email(candidate["name"], job["title"], "Offer Letter")
                database.save_offer_letter(candidate["id"], offer_text)
                st.rerun()

        if candidate["offer_letter_text"]:
            with st.expander("Offer Letter Draft", expanded=True):
                st.text(candidate["offer_letter_text"])
            ocol1, ocol2 = st.columns(2)
            with ocol1:
                if st.button(
                    "✅ Offer Sent" if candidate["offer_sent"] else "✉️ Send Offer Email",
                    disabled=bool(candidate["offer_sent"]), use_container_width=True, type="primary",
                ):
                    sent, subject, body = email_service.send_offer_email(
                        candidate["email"], candidate["name"], job["title"], candidate["offer_letter_text"],
                    )
                    database.mark_offer_sent(candidate["id"])
                    st.success("Offer emailed." if sent else "Offer marked as sent (SMTP not configured — share manually).")
                    st.rerun()
            with ocol2:
                if candidate["offer_sent"] and not candidate["offer_accepted"]:
                    if st.button("🎉 Record Offer Acceptance", use_container_width=True):
                        database.mark_offer_accepted(candidate["id"])
                        st.rerun()
                elif candidate["offer_accepted"]:
                    st.success("Offer accepted by candidate.")

        if candidate["offer_accepted"] and not employee:
            st.markdown("**Onboarding Details**")
            with st.form("onboarding_details_form"):
                ocol1, ocol2, ocol3 = st.columns(3)
                with ocol1:
                    department = st.text_input("Department", value=candidate["onboard_department"] or job["department"])
                with ocol2:
                    manager = st.text_input("Manager", value=candidate["onboard_manager"] or "")
                with ocol3:
                    joining_date = st.date_input("Joining Date", value=datetime.date.today())
                create_emp = st.form_submit_button("🆔 Generate Employee ID & Create Employee", use_container_width=True, type="primary")
            if create_emp:
                if not department.strip() or not manager.strip():
                    st.error("Department and Manager are required.")
                else:
                    database.set_onboarding_details(candidate["id"], department, manager, joining_date)
                    new_employee = database.create_employee(
                        candidate_id=candidate["id"], name=candidate["name"], email=candidate["email"],
                        department=department, designation=job["title"], joining_date=joining_date,
                        manager=manager,
                    )
                    st.success(f"🎉 {candidate['name']} onboarded as **{new_employee['employee_code']}**.")
                    st.rerun()

# ---------------------------------------------------------------------------
# Section I: Document Verification
# ---------------------------------------------------------------------------
i_locked = not candidate["offer_sent"]
with workflow_section("I", "Document Verification", "Upload and AI-verify onboarding documents", locked=i_locked):
    if not i_locked:
        if not is_ocr_available():
            st.caption("ℹ️ OCR isn't installed for image uploads — PDF documents still verify normally.")

        DOC_TYPES = ["Aadhaar", "PAN", "Degree Certificate", "Experience Certificate", "Payslip"]
        candidate_docs = {d["doc_type"]: d for d in database.get_candidate_documents(candidate["id"])}

        for doc_type in DOC_TYPES:
            existing = candidate_docs.get(doc_type)
            with st.container(border=True):
                dcol1, dcol2, dcol3 = st.columns([1.4, 2, 1.4])
                dcol1.markdown(f"**{doc_type}**")
                if existing:
                    status_color = {
                        "Verified": COLORS["success"], "Needs Review": COLORS["warning"], "Mismatch": COLORS["danger"],
                    }.get(existing["verification_status"], COLORS["text_secondary"])
                    dcol2.markdown(
                        f"<span style='color:{status_color}; font-weight:700;'>{existing['verification_status']}</span>"
                        f"<br><span style='font-size:12px; opacity:0.7;'>{existing['verification_summary'] or ''}</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    upload = dcol2.file_uploader(
                        f"Upload {doc_type}", type=["pdf", "jpg", "jpeg", "png"],
                        key=f"doc_upload_{doc_type}", label_visibility="collapsed",
                    )
                    if dcol3.button("Upload & Verify", key=f"verify_{doc_type}", use_container_width=True):
                        if not upload:
                            st.error("Choose a file first.")
                        else:
                            import os
                            candidate_dir = os.path.join(database.APP_DATA_DIR, "candidate_documents", str(candidate["id"]))
                            os.makedirs(candidate_dir, exist_ok=True)
                            filepath = os.path.join(candidate_dir, f"{doc_type.replace(' ', '_')}__{upload.name}")
                            with open(filepath, "wb") as f:
                                f.write(upload.getvalue())
                            doc_id = database.add_candidate_document(candidate["id"], doc_type, upload.name, filepath)

                            if ai_service.is_configured():
                                try:
                                    extracted = extract_text_from_document(upload)
                                    with st.spinner("Verifying with AI..."):
                                        result = ai_service.generate_document_verification_summary(doc_type, extracted)
                                    database.update_candidate_document_verification(
                                        doc_id, result.get("status", "Needs Review"), result.get("summary", ""),
                                    )
                                except ValueError as e:
                                    database.update_candidate_document_verification(doc_id, "Needs Review", str(e))
                            st.rerun()

# ---------------------------------------------------------------------------
# Section J: Talent Management
# ---------------------------------------------------------------------------
j_locked = employee is None
with workflow_section("J", "Talent Management", "Auto-created employee profile after onboarding", locked=j_locked):
    if not j_locked:
        emp_docs = database.get_documents_for_employee(employee["id"])
        cand_docs = database.get_candidate_documents(candidate["id"])
        tcol1, tcol2, tcol3 = st.columns(3)
        tcol1.markdown(f"**Employee ID**  \n{employee['employee_code']}")
        tcol1.markdown(f"**Department**  \n{employee['department']}")
        tcol2.markdown(f"**Manager**  \n{employee['manager']}")
        tcol2.markdown(f"**Joining Date**  \n{employee['joining_date']}")
        tcol3.markdown(f"**Performance Rating**  \n{employee['performance_rating']} / 5")
        tcol3.markdown("**Employment Status**  \nActive")
        st.markdown("**Skills**  \n" + "".join(chip_html(s) for s in matched))
        st.markdown(f"**Documents on File:** {len(emp_docs)} (Document Management) · {len(cand_docs)} (verified during onboarding)")
        st.page_link("pages/12_Talent_Management.py", label="Open full Talent Management profile →")

render_global_chat()
