import streamlit as st
from styles.theme import inject_global_styles, COLORS
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from components.kpi_card import kpi_card
from components.clipboard import copy_to_clipboard_button
from data import candidate_store
from data import jd_store
from services import ai_service

from utils.auth import require_login

st.set_page_config(page_title="Candidate Screening | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Candidate Screening", "Search, filter, and evaluate every candidate")

if not ai_service.is_configured():
    st.warning(
        "AI ranking, comparison, and skill-gap features need a Gemini API key. "
        "Add one to your `.env` file and restart the app to enable them.",
    )

# Same pastel-bg/dark-text badge convention used for the Resume Analyzer
# match badge and the Skill Gap readiness badge - shared here (instead of
# being defined twice) so the employee table and Candidate Detail panel
# always agree on what each stage looks like.
STAGE_STYLES = {
    "Applied": ("#E4E9EC", "#4E6672"),
    "Screened": ("#F3E9D4", "#755729"),
    "Shortlisted": ("#ECE1E3", "#7A4F56"),
    "Interview": ("#F3E4DA", "#824A31"),
    "Offer": ("#E4EDE1", "#4C6B49"),
    "Rejected": ("#F5E1DA", "#A54A34"),
}
TOP_PERFORMER_THRESHOLD = 4.5


@st.dialog("Employee Profile", width="large")
def show_profile_dialog(emp: dict):
    """Full-detail read-only profile, opened from the 'View Full Profile'
    button in the employee table. Session-only (no state changes here) -
    the actual AI actions (ranking, email, stage changes) stay in the
    Candidate Detail panel below the table."""
    star = " (Top Performer)" if emp["PerformanceRating"] >= TOP_PERFORMER_THRESHOLD else ""
    st.markdown(f"### {emp['Candidate']}{star}")
    st.caption(f"{emp['Role']} · {emp['Department']} · {emp['EmployeeID']}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Experience", f"{emp['Experience']} yrs")
    c2.metric("Location", emp["Location"])
    c3.metric("Applied", emp["Applied"])

    # Fill color follows the same theme-derived success/warning/danger
    # tones used everywhere else in the app (sage/ochre/terracotta), not a
    # generic red-yellow-green traffic-light palette - so it stays
    # consistent with the rest of the redesign while still giving an
    # at-a-glance signal.
    rating = emp["PerformanceRating"]
    rating_color = COLORS["success"] if rating >= 4.2 else COLORS["warning"] if rating >= 3.0 else COLORS["danger"]
    st.caption("Performance Rating")
    # Built as one unindented block - see kpi_card.py for why (indented
    # multi-line HTML risks Markdown treating it as a literal code block).
    bar_html = (
        f'<div style="background:{COLORS["border"]}; border-radius:8px; height:10px; width:100%; overflow:hidden;">'
        f'<div style="background:{rating_color}; width:{rating/5*100}%; height:100%;"></div>'
        f'</div>'
        f'<div style="margin-top:6px; font-size:14px; font-weight:700; color:{rating_color};">{rating} / 5</div>'
    )
    st.markdown(bar_html, unsafe_allow_html=True)

    st.write("")
    stage_bg, stage_text = STAGE_STYLES.get(emp["Stage"], ("#EFE7D8", "#635B51"))
    st.markdown(
        f"<span style='background:{stage_bg}; color:{stage_text}; padding:5px 14px; "
        f"border-radius:20px; font-size:13px; font-weight:600;'>{emp['Stage']}</span>",
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown(f"**Match Score:** {emp['Match']}%")
    st.markdown(f"**Skills:** {emp['Skills']}")


df_all = candidate_store.get_all_df()
all_jds = jd_store.get_all()

# ---- Stats cards ----
total_employees = len(df_all)
active_employees = int((df_all["Stage"] != "Rejected").sum()) if total_employees else 0
avg_rating = round(float(df_all["PerformanceRating"].mean()), 1) if total_employees else 0.0
total_departments = int(df_all["Department"].nunique()) if total_employees else 0

s1, s2, s3, s4 = st.columns(4)
with s1:
    kpi_card("Total Employees", str(total_employees))
with s2:
    kpi_card("Active Employees", str(active_employees))
with s3:
    kpi_card("Avg. Performance", f"{avg_rating} / 5")
with s4:
    kpi_card("Departments", str(total_departments))

st.write("")

prefill = st.session_state.pop("screening_query", "")

# ---- Search + sort + advanced filters (wrapped in a card so they read as
# one toolbar, instead of widgets floating above the page) ----
st.markdown('<div class="card">', unsafe_allow_html=True)
search_col, sort_col, dir_col = st.columns([2.4, 1.3, 0.9])
with search_col:
    st.caption("Search")
    query = st.text_input(
        "Search", value=prefill,
        placeholder="Search by Employee ID, name, department, or designation",
        label_visibility="collapsed",
    )
with sort_col:
    st.caption("Sort by")
    sort_field = st.selectbox(
        "Sort by", ["Name", "Department", "Experience", "Performance Rating"],
        label_visibility="collapsed",
    )
with dir_col:
    st.caption("Order")
    sort_dir = st.selectbox("Order", ["↑ Ascending", "↓ Descending"], label_visibility="collapsed")

with st.expander("Advanced Filters (Department, Designation, Stage, Location, Experience, Performance)"):
    af1, af2, af3 = st.columns(3)
    with af1:
        dept_filter = st.selectbox("Department", ["All Departments"] + sorted(df_all["Department"].unique().tolist()))
        stage_filter = st.selectbox("Stage", ["All Stages"] + sorted(df_all["Stage"].unique().tolist()))
    with af2:
        designation_filter = st.selectbox("Designation", ["All Designations"] + sorted(df_all["Role"].unique().tolist()))
        location_filter = st.selectbox("Location", ["All Locations"] + sorted(df_all["Location"].unique().tolist()))
    with af3:
        max_exp = int(df_all["Experience"].max()) if total_employees else 10
        exp_range = st.slider("Experience (years)", min_value=0, max_value=max(max_exp, 1), value=(0, max(max_exp, 1)))
        rating_range = st.slider("Performance Rating", min_value=0.0, max_value=5.0, value=(0.0, 5.0), step=0.1)
st.markdown('</div>', unsafe_allow_html=True)

# ---- Apply search + filters -> this `df` feeds everything below
# (AI ranking, comparison, candidate detail) exactly like before ----
df = df_all.copy()
if query:
    q = query.lower()
    df = df[
        df["Candidate"].str.lower().str.contains(q)
        | df["Role"].str.lower().str.contains(q)
        | df["Department"].str.lower().str.contains(q)
        | df["EmployeeID"].str.lower().str.contains(q)
        | df["Skills"].str.lower().str.contains(q)
    ]
if stage_filter != "All Stages":
    df = df[df["Stage"] == stage_filter]
if dept_filter != "All Departments":
    df = df[df["Department"] == dept_filter]
if designation_filter != "All Designations":
    df = df[df["Role"] == designation_filter]
if location_filter != "All Locations":
    df = df[df["Location"] == location_filter]
df = df[(df["Experience"] >= exp_range[0]) & (df["Experience"] <= exp_range[1])]
df = df[(df["PerformanceRating"] >= rating_range[0]) & (df["PerformanceRating"] <= rating_range[1])]

# ---- Sort ----
SORT_FIELD_MAP = {"Name": "Candidate", "Department": "Department", "Experience": "Experience", "Performance Rating": "PerformanceRating"}
df = df.sort_values(by=SORT_FIELD_MAP[sort_field], ascending=sort_dir.startswith("↑"), kind="stable").reset_index(drop=True)

st.write("")
count_col, export_col = st.columns([3, 1])
with count_col:
    st.caption(f"{len(df)} of {total_employees} employee(s)")
with export_col:
    if len(df):
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Export CSV", data=csv_bytes, file_name="talent_management.csv",
            mime="text/csv", use_container_width=True,
        )

# ---- Employee table (paginated, one row per employee, with a real
# per-row "View Full Profile" button - not possible with a plain
# st.dataframe, so this is a lightweight custom grid instead) ----
PAGE_SIZE = 8
total_pages = max(1, -(-len(df) // PAGE_SIZE)) if len(df) else 1
st.session_state.setdefault("screening_page", 1)
if st.session_state["screening_page"] > total_pages:
    st.session_state["screening_page"] = 1

st.markdown('<div class="card">', unsafe_allow_html=True)
if len(df) == 0:
    st.info("No employees match your filters.")
else:
    col_widths = [1.3, 1.8, 1.5, 1.3, 0.8, 1.7, 1.2, 1.3]
    header_cols = st.columns(col_widths)
    for c, h in zip(header_cols, ["Emp ID", "Name", "Designation", "Department", "Exp.", "Performance", "Stage", ""]):
        c.markdown(
            f"<div style='font-size:12px; font-weight:700; color:{COLORS['text_secondary']}; "
            f"text-transform:uppercase; letter-spacing:0.04em;'>{h}</div>",
            unsafe_allow_html=True,
        )

    start = (st.session_state["screening_page"] - 1) * PAGE_SIZE
    for _, r in df.iloc[start:start + PAGE_SIZE].iterrows():
        row_cols = st.columns(col_widths)
        row_cols[0].markdown(r["EmployeeID"])
        star = " (Top)" if r["PerformanceRating"] >= TOP_PERFORMER_THRESHOLD else ""
        row_cols[1].markdown(f"**{r['Candidate']}**{star}")
        row_cols[2].markdown(r["Role"])
        row_cols[3].markdown(r["Department"])
        row_cols[4].markdown(f"{r['Experience']} yrs")

        rating = r["PerformanceRating"]
        rating_color = COLORS["success"] if rating >= 4.2 else COLORS["warning"] if rating >= 3.0 else COLORS["danger"]
        row_cols[5].markdown(
            f"<div style='background:{COLORS['border']}; border-radius:8px; height:8px; width:100%; overflow:hidden;'>"
            f"<div style='background:{rating_color}; width:{rating/5*100}%; height:100%;'></div></div>"
            f"<div style='font-size:12px; color:{rating_color}; font-weight:700; margin-top:2px;'>{rating}/5</div>",
            unsafe_allow_html=True,
        )

        stage_bg, stage_text = STAGE_STYLES.get(r["Stage"], ("#EFE7D8", "#635B51"))
        row_cols[6].markdown(
            f"<span style='background:{stage_bg}; color:{stage_text}; padding:3px 10px; "
            f"border-radius:14px; font-size:12px; font-weight:600;'>{r['Stage']}</span>",
            unsafe_allow_html=True,
        )

        if row_cols[7].button("Profile", key=f"profile_btn_{r['EmployeeID']}", use_container_width=True):
            show_profile_dialog(r.to_dict())

    if total_pages > 1:
        st.write("")
        p1, p2, p3 = st.columns([1, 2, 1])
        with p1:
            if st.button("◀ Previous", disabled=st.session_state["screening_page"] <= 1, use_container_width=True, key="prev_page"):
                st.session_state["screening_page"] -= 1
                st.rerun()
        with p2:
            st.markdown(
                f"<div style='text-align:center; padding-top:8px; color:{COLORS['text_secondary']};'>"
                f"Page {st.session_state['screening_page']} of {total_pages}</div>",
                unsafe_allow_html=True,
            )
        with p3:
            if st.button("Next ▶", disabled=st.session_state["screening_page"] >= total_pages, use_container_width=True, key="next_page"):
                st.session_state["screening_page"] += 1
                st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.markdown('<div class="card">', unsafe_allow_html=True)
rank_col1, rank_col2 = st.columns([2, 1])
with rank_col1:
    if all_jds:
        jd_labels = [f"{jd['title']} · {jd['department']}" for jd in all_jds]
        rank_jd_index = st.selectbox("Rank current results against Job Description",
                                      range(len(jd_labels)), format_func=lambda i: jd_labels[i])
        rank_jd = all_jds[rank_jd_index]
    else:
        st.info("Create a Job Description first to enable AI ranking.")
        rank_jd = None
with rank_col2:
    st.write("")
    rank_clicked = st.button(
        "Rank with AI", use_container_width=True,
        disabled=not (rank_jd and len(df) and ai_service.is_configured()),
    )

if rank_clicked and rank_jd is not None:
    with st.spinner("AI is ranking candidates..."):
        try:
            candidate_payload = [
                {"name": r["Candidate"], "role": r["Role"], "skills": r["Skills"]}
                for _, r in df.iterrows()
            ]
            result = ai_service.rank_candidates(candidate_payload, rank_jd["description"])
            st.session_state["ranking_result"] = {"jd_title": rank_jd["title"], "rankings": result.get("rankings", [])}
        except ai_service.AIServiceError as e:
            st.error(f"AI ranking failed: {e}")

ranking = st.session_state.get("ranking_result")
if ranking:
    st.markdown(f"**AI Ranking against '{ranking['jd_title']}'**")
    for i, r in enumerate(ranking["rankings"], start=1):
        st.markdown(
            f"{i}. **{r.get('name','')}** — AI Score: **{r.get('ai_score','—')}%**  \n"
            f"　　_{r.get('reasoning','')}_"
        )
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- AI Candidate Comparison ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("**🆚 Compare Candidates with AI**")
compare_names = st.multiselect(
    "Select 2-3 candidates to compare", df["Candidate"].tolist(),
    max_selections=3,
)
compare_col1, compare_col2 = st.columns([2, 1])
with compare_col1:
    if all_jds:
        cmp_jd_index = st.selectbox("Compare against Job Description", range(len(jd_labels)),
                                     format_func=lambda i: jd_labels[i], key="cmp_jd")
        cmp_jd = all_jds[cmp_jd_index]
    else:
        cmp_jd = None
with compare_col2:
    st.write("")
    compare_clicked = st.button(
        "Compare Selected", use_container_width=True,
        disabled=not (len(compare_names) >= 2 and cmp_jd and ai_service.is_configured()),
    )

if compare_clicked and cmp_jd is not None:
    with st.spinner("AI is comparing candidates..."):
        try:
            payload = []
            for n in compare_names:
                c = candidate_store.get_by_name(n)
                payload.append({"name": c["Candidate"], "role": c["Role"], "skills": c["Skills"], "match": c["Match"]})
            result = ai_service.compare_candidates(payload, cmp_jd["description"])
            st.session_state["comparison_result"] = result
        except ai_service.AIServiceError as e:
            st.error(f"AI comparison failed: {e}")

comparison = st.session_state.get("comparison_result")
if comparison:
    cols = st.columns(len(comparison.get("comparisons", [])) or 1)
    for col, c in zip(cols, comparison.get("comparisons", [])):
        with col:
            is_best = c.get("name") == comparison.get("recommended")
            badge = " (Best Fit)" if is_best else ""
            st.markdown(f"**{c.get('name','')}{badge}**")
            st.markdown("Pros:")
            for p in c.get("pros", []):
                st.markdown(f"- {p}")
            st.markdown("Cons:")
            for con in c.get("cons", []):
                st.markdown(f"- {con}")
    st.write("")
    st.info(f"**AI Recommendation: {comparison.get('recommended','')}** — {comparison.get('recommendation_reason','')}")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Candidate detail ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("**Candidate Detail**")
selected = st.selectbox("Select a candidate", df["Candidate"].tolist() if len(df) else ["No candidates match your filters"])

row = candidate_store.get_by_name(selected)
if row:
    match_score = row["Match"]
    match_label = "Strong" if match_score >= 80 else "Moderate" if match_score >= 60 else "Weak"
    match_color = COLORS["success"] if match_score >= 80 else COLORS["warning"] if match_score >= 60 else COLORS["danger"]

    # STAGE_STYLES is defined once near the top of this file and shared
    # with the employee table and profile dialog above.
    stage_bg, stage_text = STAGE_STYLES.get(row["Stage"], ("#EFE7D8", "#635B51"))

    d1, d2, d3 = st.columns(3)
    with d1:
        st.caption("Match Score")
        match_bar_html = (
            f'<div style="background:{COLORS["border"]}; border-radius:8px; height:10px; width:100%; overflow:hidden; margin-top:4px;">'
            f'<div style="background:{match_color}; width:{match_score}%; height:100%;"></div>'
            f'</div>'
            f'<div style="margin-top:6px; font-size:14px; font-weight:700; color:{match_color};">{match_score}% · {match_label}</div>'
        )
        st.markdown(match_bar_html, unsafe_allow_html=True)
    with d2:
        st.caption("Current Stage")
        stage_badge_html = (
            '<div style="margin-top:8px;">'
            f'<span style="background:{stage_bg}; color:{stage_text}; padding:5px 14px; '
            f'border-radius:20px; font-size:13px; font-weight:600;">{row["Stage"]}</span>'
            '</div>'
        )
        st.markdown(stage_badge_html, unsafe_allow_html=True)
    with d3:
        st.metric("Applied", row["Applied"])

    st.write("")
    st.markdown(f"**Skills:** {row['Skills']}")

    # ---- Skill Gap Analyzer AI ----
    st.write("")
    sg_col1, sg_col2 = st.columns([2, 1])
    with sg_col1:
        if all_jds:
            sg_jd_index = st.selectbox("Analyze skill gap against", range(len(jd_labels)),
                                        format_func=lambda i: jd_labels[i], key="sg_jd")
            sg_jd = all_jds[sg_jd_index]
        else:
            sg_jd = None
    with sg_col2:
        st.write("")
        sg_clicked = st.button(
            "Analyze Skill Gap", use_container_width=True,
            disabled=not (sg_jd and ai_service.is_configured()),
        )

    if sg_clicked and sg_jd is not None:
        with st.spinner("AI is analyzing skill gaps..."):
            try:
                candidate_payload = {"name": row["Candidate"], "role": row["Role"], "skills": row["Skills"]}
                gap = ai_service.analyze_skill_gap(candidate_payload, sg_jd["description"])
                st.session_state["skill_gap_result"] = {"candidate": selected, "data": gap}
            except ai_service.AIServiceError as e:
                st.error(f"Skill gap analysis failed: {e}")

    gap_result = st.session_state.get("skill_gap_result")
    if gap_result and gap_result["candidate"] == selected:
        g = gap_result["data"]
        readiness_colors = {"Ready": "#4C6B49", "Needs Development": "#755729", "Not Ready": "#A54A34"}
        readiness_bg = {"Ready": "#E4EDE1", "Needs Development": "#F3E9D4", "Not Ready": "#F5E1DA"}
        level = g.get("readiness_level", "Needs Development")
        st.markdown(
            f"<span style='background:{readiness_bg.get(level,'#EFE7D8')}; color:{readiness_colors.get(level,'#635B51')}; "
            f"padding:4px 12px; border-radius:20px; font-size:13px; font-weight:600;'>{level}</span>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.write(g.get("summary", ""))
        if g.get("gap_skills"):
            st.markdown("**Missing skills:** " + " · ".join(g["gap_skills"]))
        if g.get("existing_strengths"):
            st.markdown("**Existing strengths:** " + " · ".join(g["existing_strengths"]))
        if g.get("recommendations"):
            st.markdown("**How to close the gap:**")
            for rec in g["recommendations"]:
                st.markdown(f"- **{rec.get('skill','')}**: {rec.get('suggestion','')}")

    # ---- AI Email Generator ----
    st.write("")
    st.markdown("**AI Email Generator**")
    st.markdown('<div class="subsection">', unsafe_allow_html=True)
    st.markdown('<div class="subsection-label">Prompt</div>', unsafe_allow_html=True)
    em_col1, em_col2, em_col3 = st.columns([1, 1, 1])
    with em_col1:
        email_type = st.selectbox("Email Type", ["Interview Invitation", "Rejection", "Offer Letter"], key="email_type")
    with em_col2:
        email_tone = st.selectbox("Tone", ["Professional", "Warm", "Formal"], key="email_tone")
    with em_col3:
        st.write("")
        email_clicked = st.button("Generate Email", use_container_width=True, disabled=not ai_service.is_configured())
    st.markdown('</div>', unsafe_allow_html=True)

    if email_clicked:
        with st.spinner("Drafting email..."):
            try:
                email_text = ai_service.generate_email(row["Candidate"], row["Role"], email_type, email_tone)
                st.session_state["generated_email"] = {"candidate": selected, "text": email_text}
            except ai_service.AIServiceError as e:
                st.error(f"Email generation failed: {e}")

    generated = st.session_state.get("generated_email")
    if generated and generated["candidate"] == selected:
        st.markdown('<div class="subsection">', unsafe_allow_html=True)
        label_col, copy_col = st.columns([3, 1])
        with label_col:
            st.markdown('<div class="subsection-label">Generated Email</div>', unsafe_allow_html=True)
        with copy_col:
            copy_to_clipboard_button(generated["text"], key=f"screening_email_{selected}")
        st.text_area("Generated Email (copy from here)", value=generated["text"], height=220, key="generated_email_box", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- Performance Review AI Assistant ----
    st.write("")
    st.markdown("**Performance Review AI Assistant**")
    pr_clicked = st.button(
        "Generate Performance Review", use_container_width=True,
        disabled=not ai_service.is_configured(), key="pr_generate",
    )

    if pr_clicked:
        with st.spinner("AI is drafting the performance review..."):
            try:
                employee_payload = {
                    "name": row["Candidate"], "role": row["Role"], "department": row["Department"],
                    "experience": row["Experience"], "performance_rating": row["PerformanceRating"],
                    "stage": row["Stage"], "skills": row["Skills"],
                }
                review = ai_service.generate_performance_review(employee_payload)
                st.session_state["performance_review"] = {"candidate": selected, "data": review}
            except ai_service.AIServiceError as e:
                st.error(f"Performance review generation failed: {e}")

    pr_result = st.session_state.get("performance_review")
    if pr_result and pr_result["candidate"] == selected:
        pr = pr_result["data"]

        st.markdown('<div class="subsection">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-label">Performance Summary</div>', unsafe_allow_html=True)
        st.write(pr.get("summary", ""))
        st.markdown('</div>', unsafe_allow_html=True)

        pr_col1, pr_col2 = st.columns(2)
        with pr_col1:
            st.markdown('<div class="subsection">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-label">Strengths</div>', unsafe_allow_html=True)
            for s in pr.get("strengths", []):
                st.markdown(f"- {s}")
            st.markdown('</div>', unsafe_allow_html=True)
        with pr_col2:
            st.markdown('<div class="subsection">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-label">Areas to Improve</div>', unsafe_allow_html=True)
            for a in pr.get("improvement_areas", []):
                st.markdown(f"- {a}")
            st.markdown('</div>', unsafe_allow_html=True)

        if pr.get("training_recommendations"):
            st.markdown('<div class="subsection">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-label">Training &amp; Skill Development</div>', unsafe_allow_html=True)
            for t in pr["training_recommendations"]:
                st.markdown(f"- **{t.get('area','')}**: {t.get('recommendation','')}")
            st.markdown('</div>', unsafe_allow_html=True)

        if pr.get("career_growth"):
            st.markdown('<div class="subsection">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-label">Career Growth</div>', unsafe_allow_html=True)
            st.write(pr["career_growth"])
            st.markdown('</div>', unsafe_allow_html=True)

        if pr.get("manager_comment"):
            st.markdown('<div class="subsection">', unsafe_allow_html=True)
            mc_label_col, mc_copy_col = st.columns([3, 1])
            with mc_label_col:
                st.markdown('<div class="subsection-label">Manager Review Comment</div>', unsafe_allow_html=True)
            with mc_copy_col:
                copy_to_clipboard_button(pr["manager_comment"], key=f"perf_review_{selected}", label="Copy Comment")
            st.text_area("Manager Comment", value=pr["manager_comment"], height=140, key="perf_review_box", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("**Recruiter Notes**")
    st.text_area("Notes", placeholder="Add notes about this candidate...", label_visibility="collapsed", key="screening_notes")

    st.write("")
    b1, b2, b3 = st.columns(3)
    if b1.button("Shortlist", use_container_width=True, key="shortlist_btn"):
        candidate_store.update_stage(selected, "Shortlisted", note="Shortlisted by recruiter.")
        st.success(f"{selected} moved to Shortlisted.")
        st.rerun()
    if b2.button("Move to Interview", use_container_width=True, key="interview_btn"):
        candidate_store.update_stage(selected, "Interview", note="Moved to interview stage.")
        st.success(f"{selected} moved to Interview.")
        st.rerun()
    if b3.button("Reject", use_container_width=True, key="reject_btn"):
        candidate_store.update_stage(selected, "Rejected", note="Rejected by recruiter.")
        st.success(f"{selected} marked as Rejected.")
        st.rerun()

    timeline = candidate_store.get_timeline(selected)
    if timeline:
        st.write("")
        st.markdown("**Timeline**")
        for step in timeline:
            st.markdown(f"- **{step['stage']}** · {step['date']} — {step['note']}")

st.markdown('</div>', unsafe_allow_html=True)

render_global_chat()
