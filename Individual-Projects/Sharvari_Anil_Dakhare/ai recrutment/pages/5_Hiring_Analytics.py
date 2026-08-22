import streamlit as st
from styles.theme import inject_global_styles
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from components.kpi_card import kpi_card
from components.charts import (
    recruitment_funnel_chart,
    hiring_trend_chart,
    department_hiring_chart,
    monthly_report_chart,
)
from components.tables import styled_table
from data import mock_data as data
from data import candidate_store
from services import ai_service

from utils.auth import require_login

st.set_page_config(page_title="Hiring Analytics | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Hiring Analytics", "Recruitment performance and trends")

if not ai_service.is_configured():
    st.warning(
        "AI insights, talent analysis, recommendations, and report generation "
        "need a Gemini API key. Add one to your `.env` file and restart the app.",
    )

# ---- Build reusable summaries for AI prompts ----
live_df = candidate_store.get_all_df()

def _candidate_summary() -> str:
    if not len(live_df):
        return "No candidates currently in the pipeline."
    lines = [
        f"- {r['Candidate']}: {r['Role']} ({r['Department']}), skills: {r['Skills']}, "
        f"match: {r['Match']}%, stage: {r['Stage']}"
        for _, r in live_df.iterrows()
    ]
    return "\n".join(lines)

def _kpi_summary() -> str:
    return (
        f"Time to hire: {data.TIME_TO_HIRE_DAYS} days. "
        f"Offer acceptance rate: {data.OFFER_ACCEPTANCE_RATE}. "
        f"Total hires YTD: {data.MONTHLY_REPORT['Hires'].sum()}. "
        f"Total candidates in pipeline: {len(live_df)}."
    )

def _funnel_summary() -> str:
    return ", ".join(f"{stage}: {val}" for stage, val in zip(data.FUNNEL_STAGES, data.FUNNEL_VALUES))

# ---- KPIs ----
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Time to Hire", f"{data.TIME_TO_HIRE_DAYS} days", "-2")
with k2:
    kpi_card("Offer Acceptance", data.OFFER_ACCEPTANCE_RATE, "+3%")
with k3:
    kpi_card("Total Hires (YTD)", str(data.MONTHLY_REPORT["Hires"].sum()), "+18")
with k4:
    kpi_card("Open Requisitions", "24", "+3")

st.write("")

# ---- Funnel + Trend ----
left, right = st.columns([1, 2])
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Hiring Funnel**")
    fig = recruitment_funnel_chart(data.FUNNEL_STAGES, data.FUNNEL_VALUES)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Hiring Trends**")
    fig = hiring_trend_chart(data.TREND_MONTHS, data.TREND_APPLICATIONS, data.TREND_HIRES)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Department + Monthly report ----
left, right = st.columns(2)
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Hiring by Department**")
    fig = department_hiring_chart(data.DEPARTMENTS, data.DEPARTMENT_COUNTS)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Monthly Report**")
    fig = monthly_report_chart(
        data.MONTHLY_REPORT["Month"],
        data.MONTHLY_REPORT["Applications"],
        data.MONTHLY_REPORT["Offers"],
        data.MONTHLY_REPORT["Hires"],
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Recruiter performance ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("**Recruiter Performance**")
styled_table(data.RECRUITER_PERFORMANCE)
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Talent Insight AI ----
st.markdown('<div class="card">', unsafe_allow_html=True)
insight_col1, insight_col2 = st.columns([4, 1])
with insight_col1:
    st.markdown("**Talent Insight AI**")
    st.caption("AI-generated insights grounded in your live candidate pool and KPIs.")
with insight_col2:
    insight_clicked = st.button("Generate Insights", use_container_width=True, disabled=not ai_service.is_configured())

if insight_clicked:
    with st.spinner("Analyzing hiring data..."):
        try:
            result = ai_service.talent_insight_summary(_candidate_summary(), _kpi_summary())
            st.session_state["talent_insight"] = result
        except ai_service.AIServiceError as e:
            st.error(f"AI insight generation failed: {e}")

insight = st.session_state.get("talent_insight")
if insight:
    st.write(insight.get("summary", ""))
    for point in insight.get("insights", []):
        st.markdown(f"- {point}")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Talent Analyzer ----
st.markdown('<div class="card">', unsafe_allow_html=True)
ta_col1, ta_col2 = st.columns([4, 1])
with ta_col1:
    st.markdown("**Talent Analyzer**")
    st.caption("Structural breakdown of your current candidate pool - skills, departments, strengths, gaps.")
with ta_col2:
    ta_clicked = st.button("Analyze Pool", use_container_width=True, disabled=not (ai_service.is_configured() and len(live_df)))

if ta_clicked:
    with st.spinner("Analyzing talent pool..."):
        try:
            result = ai_service.analyze_talent_pool(_candidate_summary())
            st.session_state["talent_analysis"] = result
        except ai_service.AIServiceError as e:
            st.error(f"Talent pool analysis failed: {e}")

analysis = st.session_state.get("talent_analysis")
if analysis:
    st.write(analysis.get("summary", ""))
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        st.markdown("**Top skills in pool**")
        for s in analysis.get("top_skills", []):
            st.markdown(f"- {s.get('skill','')} ({s.get('count','')})")
    with tcol2:
        st.markdown("**By department**")
        for d in analysis.get("department_breakdown", []):
            st.markdown(f"- {d.get('department','')}: {d.get('count','')}")
    st.markdown(f"**Strongest area:** {analysis.get('strongest_area','')}")
    st.markdown(f"**Weakest area:** {analysis.get('weakest_area','')}")
elif not len(live_df):
    st.caption("No candidates in the pipeline yet - analyze or shortlist a resume first.")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Recruitment Analysis AI ----
st.markdown('<div class="card">', unsafe_allow_html=True)
ra_col1, ra_col2 = st.columns([4, 1])
with ra_col1:
    st.markdown("**Recruitment Analysis AI**")
    st.caption("Analyzes your hiring funnel and process for bottlenecks and strengths.")
with ra_col2:
    ra_clicked = st.button("Analyze Process", use_container_width=True, disabled=not ai_service.is_configured())

if ra_clicked:
    with st.spinner("Analyzing recruitment process..."):
        try:
            result = ai_service.recruitment_process_analysis(_funnel_summary(), _kpi_summary())
            st.session_state["process_analysis"] = result
        except ai_service.AIServiceError as e:
            st.error(f"Process analysis failed: {e}")

process = st.session_state.get("process_analysis")
if process:
    st.write(process.get("summary", ""))
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.markdown("**Bottlenecks**")
        for b in process.get("bottlenecks", []):
            st.markdown(f"- {b}")
        st.markdown("**Strengths**")
        for s in process.get("strengths", []):
            st.markdown(f"- {s}")
    with pcol2:
        st.markdown("**Recommendations**")
        for r in process.get("recommendations", []):
            st.markdown(f"- {r}")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Report Generator AI ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("**Report Generator AI**")
st.caption("Synthesizes everything above into one downloadable hiring report.")
report_clicked = st.button("Generate Full Report", disabled=not ai_service.is_configured())

if report_clicked:
    with st.spinner("Writing report..."):
        try:
            context = (
                f"CANDIDATE POOL:\n{_candidate_summary()}\n\n"
                f"KPIs:\n{_kpi_summary()}\n\n"
                f"FUNNEL:\n{_funnel_summary()}\n\n"
                f"PRIOR TALENT INSIGHTS: {insight.get('summary','') if insight else 'Not yet generated.'}\n"
                f"PRIOR PROCESS ANALYSIS: {process.get('summary','') if process else 'Not yet generated.'}"
            )
            report_text = ai_service.generate_hiring_report(context)
            st.session_state["hiring_report"] = report_text
        except ai_service.AIServiceError as e:
            st.error(f"Report generation failed: {e}")

report = st.session_state.get("hiring_report")
if report:
    st.markdown('<div class="subsection">', unsafe_allow_html=True)
    st.markdown('<div class="subsection-label">Generated Report</div>', unsafe_allow_html=True)
    st.markdown(report)
    st.download_button(
        "Download Report (Markdown)", data=report,
        file_name="hiring_report.md", mime="text/markdown",
    )
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

render_global_chat()
