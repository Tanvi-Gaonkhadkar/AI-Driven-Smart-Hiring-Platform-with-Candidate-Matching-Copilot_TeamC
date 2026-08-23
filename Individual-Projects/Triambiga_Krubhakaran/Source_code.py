# -*- coding: utf-8 -*-
"""
AI Recruitment & Talent Management Copilot
Group 1 - Batch-1
"""
import streamlit as st
import requests
import json
import plotly.graph_objects as go

st.set_page_config(
    page_title="AI Recruitment & Talent Management Copilot",
    page_icon="🤖",
    layout="wide"
)

# ---------------- Custom styling ----------------

CUSTOM_CSS = """
<style>
/* ---- Global ---- */
html, body, [class*="css"] {
    font-family: 'Segoe UI', 'Inter', sans-serif;
}

/* ---- Headers: gradient, confident, corporate ---- */
h1 {
    background: linear-gradient(90deg, #5EEAD4 0%, #6366F1 60%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    padding-bottom: 4px;
}
h2, h3 {
    color: #CBD5E1 !important;
    font-weight: 600 !important;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1220 0%, #111827 100%);
    border-right: 1px solid #1F2937;
}
section[data-testid="stSidebar"] h1 {
    -webkit-text-fill-color: #E5E7EB !important;
    background: none !important;
    font-size: 1.3rem !important;
}

/* ---- Buttons ---- */
.stButton > button {
    border-radius: 10px !important;
    border: 1px solid #334155 !important;
    transition: all 0.18s ease-in-out;
    font-weight: 600 !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    border-color: #6366F1 !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #14B8A6, #6366F1) !important;
    border: none !important;
}

/* ---- Metric cards ---- */
div[data-testid="stMetric"] {
    background: linear-gradient(160deg, #111827 0%, #0B1220 100%);
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 14px 16px 10px 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    transition: transform 0.15s ease-in-out;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #6366F1;
}
div[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
}

/* ---- Tabs ---- */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #5EEAD4 !important;
    border-bottom-color: #6366F1 !important;
}

/* ---- Dividers ---- */
hr {
    border-color: #1F2937 !important;
}

/* ---- Chat bubbles ---- */
div[data-testid="stChatMessage"] {
    border-radius: 14px;
    border: 1px solid #1F2937;
}

/* ---- Text areas / inputs ---- */
textarea, input, .stSelectbox div[data-baseweb="select"] {
    border-radius: 8px !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------- Ollama backend ----------------

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"


def call_ollama(prompt: str, system: str = None, max_tokens: int = 220) -> str:
    """Send a prompt to a local Ollama model and return the generated text.

    Uses streaming under the hood: each chunk arriving resets the read timer,
    so slow-but-still-working generations don't get killed by one long
    blocking read the way stream=False can. Defaults are tuned for CPU-only
    inference, where each token can take noticeably longer than on GPU.
    """
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": True,
                "options": {"num_predict": max_tokens},
            },
            timeout=(10, 120),  # (connect timeout, read timeout per chunk)
            stream=True,
        )
        response.raise_for_status()

        full_text = ""
        for line in response.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            full_text += chunk.get("response", "")
            if chunk.get("done"):
                break
        return full_text.strip() or "⚠️ Ollama returned an empty response."

    except requests.exceptions.ConnectionError:
        return "⚠️ Could not reach Ollama. Is it running? Try `ollama serve` in a terminal."
    except requests.exceptions.ReadTimeout:
        return (
            "⚠️ Ollama took too long to respond (no data for 120s). On CPU, this can happen "
            "with long prompts. Try again — the model should be warm after the first "
            "successful call — or shorten the input."
        )
    except Exception as e:
        return f"⚠️ Error calling Ollama: {e}"
    
def is_recruitment_related(question: str) -> bool:
    """Classify whether a question falls within the recruitment/HR/talent-management domain."""
    classifier_prompt = (
        "You are a strict topic classifier for an HR and recruitment assistant. "
        "The assistant is ONLY allowed to discuss: recruitment, hiring, job descriptions, "
        "resumes/CVs, candidates, interviews, talent management, HR policies, onboarding, "
        "offer/rejection emails, or this recruitment application itself.\n\n"
        f"User question: \"{question}\"\n\n"
        "Is this question within that domain? Reply with exactly one word, "
        "either YES or NO, with no punctuation and nothing else."
    )
    reply = call_ollama(classifier_prompt, max_tokens=5).strip().lower()
    return reply.startswith("yes")


def extract_text(uploaded_file) -> str:
    """Extract raw text from an uploaded PDF, DOCX, or TXT file."""
    if uploaded_file is None:
        return ""
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".pdf"):
            import pdfplumber
            text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for pg in pdf.pages:
                    text += (pg.extract_text() or "") + "\n"
            return text.strip()
        elif name.endswith(".docx"):
            import docx
            document = docx.Document(uploaded_file)
            return "\n".join(p.text for p in document.paragraphs).strip()
        elif name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8", errors="ignore").strip()
        return ""
    except Exception as e:
        return f"⚠️ Could not extract text: {e}"


def parse_match_reply(reply: str):
    """Pull Match %, Status, and Reason out of a model reply, tolerant of markdown,
    stray text, and small models not following the exact requested format."""
    import re

    # --- Match percentage: look near the word "match" first, then any %/number as fallback ---
    match_pct = "N/A"
    m = re.search(r"match[^0-9]{0,20}(\d{1,3})", reply, re.IGNORECASE)
    if not m:
        m = re.search(r"(\d{1,3})\s*%", reply)
    if not m:
        m = re.search(r"\b(\d{1,3})\b", reply)
    if m:
        val = max(0, min(100, int(m.group(1))))  # clamp to a sane 0-100 range
        match_pct = f"{val}%"

    # --- Status: keyword search anywhere in the reply, not just a labeled line ---
    low = reply.lower()
    if "shortlist" in low:
        status = "Shortlisted"
    elif "reject" in low:
        status = "Rejected"
    else:
        status = "Review"

    # --- Reason: prefer an explicit "Reason:" label, else fall back to first useful line ---
    reason = ""
    m2 = re.search(r"reason[:\-]?\s*(.+)", reply, re.IGNORECASE)
    if m2:
        reason = m2.group(1).strip().splitlines()[0].strip()
    if not reason:
        for line in reply.splitlines():
            cleaned = line.strip().strip("*#-> ").strip()
            if cleaned and not re.match(r"^(match|status)\b", cleaned, re.IGNORECASE):
                reason = cleaned
                break
    if not reason:
        reason = reply.strip()[:150] or "No reason returned."

    return match_pct, status, reason


def send_email_smtp(to_email: str, subject: str, body: str) -> tuple[bool, str]:
    """Send an email via SMTP using credentials from st.secrets.

    Expects a .streamlit/secrets.toml with:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 465
        SMTP_EMAIL = "your_email@gmail.com"
        SMTP_PASSWORD = "your_app_password"
    """
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        server = st.secrets["SMTP_SERVER"]
        port = int(st.secrets["SMTP_PORT"])
        sender_email = st.secrets["SMTP_EMAIL"]
        sender_password = st.secrets["SMTP_PASSWORD"]
    except (KeyError, FileNotFoundError):
        return False, (
            "SMTP credentials not configured. Add a .streamlit/secrets.toml file with "
            "SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, and SMTP_PASSWORD."
        )

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(server, port, context=context, timeout=20) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.sendmail(sender_email, to_email, msg.as_string())
        return True, "Email sent successfully."
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Check SMTP_EMAIL/SMTP_PASSWORD (Gmail needs an App Password, not your regular password)."
    except Exception as e:
        return False, f"Failed to send: {e}"


def parse_retention_risk(reply: str) -> str:
    """Pull a Low/Medium/High retention-risk label out of a talent strategy reply,
    for a quick badge in the employee list."""
    import re
    m = re.search(r"retention risk[:\-]?\s*(low|medium|high)", reply, re.IGNORECASE)
    if not m:
        m = re.search(r"\b(low|medium|high)\b", reply, re.IGNORECASE)
    return m.group(1).capitalize() if m else "Unknown"


def split_subject_body(text: str) -> tuple[str, str]:
    """Split a 'Subject: ...' first line from the rest of the email body."""
    lines = text.splitlines()
    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[-1].strip()
        body = "\n".join(lines[1:]).strip()
        return subject or "No subject", body
    return "No subject", text.strip()


# ---------------- Session state ----------------

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "resume_texts" not in st.session_state:
    st.session_state.resume_texts = {}          # candidate name -> extracted text
if "screening_results" not in st.session_state:
    st.session_state.screening_results = []      # list of dicts
if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = ""
if "report_text" not in st.session_state:
    st.session_state.report_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "resume_chat_history" not in st.session_state:
    st.session_state.resume_chat_history = []
if "skill_gap_result" not in st.session_state:
    st.session_state.skill_gap_result = ""
if "screening_raw" not in st.session_state:
    st.session_state.screening_raw = {}
if "email_draft" not in st.session_state:
    st.session_state.email_draft = ""
if "employees" not in st.session_state:
    st.session_state.employees = []              # list of {name, role, tenure, target_role}
if "talent_strategies" not in st.session_state:
    st.session_state.talent_strategies = {}       # employee name -> AI strategy text

# ---------------- Sidebar ----------------

st.sidebar.title("🤖 AI Recruitment Copilot")
st.sidebar.caption("Group 1 - Batch-1")

pages = [
    "Dashboard", "Resume Screening", "Candidate Search", "Candidate Comparison",
    "Interview Assistant", "Resume Chat", "Talent Analytics", "Email Generator",
    "Talent Management", "AI Chat",
]
icons = {
    "Dashboard": "🏠", "Resume Screening": "📄", "Candidate Search": "👤",
    "Candidate Comparison": "⚖️", "Interview Assistant": "🎤", "Resume Chat": "💭",
    "Talent Analytics": "📊", "Email Generator": "✉️", "Talent Management": "🚀",
    "AI Chat": "💬",
}

for p in pages:
    btn_type = "primary" if st.session_state.page == p else "secondary"
    if st.sidebar.button(f"{icons[p]} {p}", use_container_width=True, type=btn_type):
        st.session_state.page = p

st.sidebar.divider()
st.sidebar.caption(f"Backend: {OLLAMA_MODEL} (Ollama, local, CPU)")
st.sidebar.caption("⏳ Responses may take 10-60s+ on CPU — this is expected.")

page = st.session_state.page

# ---------------- Dashboard ----------------
if page == "Dashboard":
    st.title("AI Recruitment & Talent Management Copilot")
    st.markdown("### Welcome Recruiter")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Candidates", len(st.session_state.resume_texts) or 245)
    col2.metric("Open Jobs", "18")
    col3.metric("Shortlisted", sum(1 for r in st.session_state.screening_results if r["Status"].lower() == "shortlisted") or 42)
    col4.metric("Interviews", "16")

    st.divider()
    st.subheader("Recent Activities")
    st.write("• Resume uploaded")
    st.write("• AI shortlisted candidates")
    st.write("• Interview scheduled")
    st.write("• Offer generated")

    st.divider()
    st.subheader("AI Modules")
    m1, m2, m3, m4 = st.columns(4)
    m1.info("📄 Job Description AI")
    m2.info("🧩 Resume Matching AI")
    m3.info("🏆 Candidate Ranking AI")
    m4.info("🎤 Interview Question Generator AI")
    m5, m6, m7, m8 = st.columns(4)
    m5.info("💭 Resume Chat AI")
    m6.info("⚖️ Candidate Comparison AI")
    m7.info("✅ Hiring Recommendation AI")
    m8.info("🔎 Talent Insight AI")
    m9, m10, m11, m12 = st.columns(4)
    m9.info("📉 Skill Gap AI")
    m10.info("✉️ AI Email Generator")
    m11.info("📈 Recruitment Analysis AI")
    m12.info("📝 Report Generator AI")

# ---------------- Resume Screening ----------------
elif page == "Resume Screening":
    st.title("Resume Screening")
    st.caption(f"Backend: {OLLAMA_MODEL} (Ollama, local)")

    tab_jd, tab_match, tab_rank = st.tabs(
        ["📄 Job Description AI", "🧩 Resume Matching AI", "🏆 Candidate Ranking AI"]
    )

    # --- Job Description AI ---
    with tab_jd:
        st.subheader("Job Description AI")
        jd_mode = st.radio("Mode", ["Upload JD", "Generate JD with AI"], horizontal=True)

        if jd_mode == "Upload JD":
            jd_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])
            if jd_file is not None:
                st.session_state.jd_text = extract_text(jd_file)
                st.success(f"Extracted {len(st.session_state.jd_text)} characters from {jd_file.name}")
        else:
            company = st.text_input("Company Name", placeholder="e.g. Acme Corp")
            role = st.text_input("Job Title")
            skills = st.text_input("Key Skills (comma separated)")
            exp = st.slider("Required Experience (Years)", 0, 20, 3)
            if st.button("Generate Job Description"):
                if not role:
                    st.warning("Please enter a job title.")
                else:
                    company_line = company if company else "the company"
                    prompt = (
                        f"Fill in this job description template exactly. Do not add extra sections. "
                        f"Do not repeat these instructions in your answer.\n\n"
                        f"Job Title: {role}\n"
                        f"Company: {company_line}\n"
                        f"Experience Required: {exp} years\n"
                        f"Key Skills: {skills if skills else 'not specified'}\n\n"
                        "Now write the job description using exactly these headers, in this order:\n"
                        "About the Role: (2 sentences max)\n"
                        "Responsibilities: (exactly 4 bullet points)\n"
                        "Requirements: (exactly 4 bullet points)\n"
                        "Keep the whole thing under 150 words total."
                    )
                    with st.spinner("Generating job description..."):
                        st.session_state.jd_text = call_ollama(prompt, max_tokens=350)
                    st.success("Job description generated.")

        if st.session_state.jd_text:
            st.text_area("Current Job Description", value=st.session_state.jd_text, height=180)
        else:
            st.info("No job description loaded yet.")

    # --- Resume Matching AI ---
    with tab_match:
        st.subheader("Resume Matching AI")
        resumes = st.file_uploader(
            "Upload Candidate Resumes", accept_multiple_files=True, type=["pdf", "docx"]
        )

        if st.button("Run AI Screening"):
            if not st.session_state.jd_text:
                st.warning("Load a job description in the Job Description AI tab first.")
            elif not resumes:
                st.warning("Please upload at least one resume.")
            else:
                results = []
                raw_replies = {}
                for r in resumes:
                    resume_text = extract_text(r)
                    st.session_state.resume_texts[r.name] = resume_text

                    prompt = (
                        f"Job description:\n{st.session_state.jd_text[:900]}\n\n"
                        f"Candidate resume:\n{resume_text[:900]}\n\n"
                        "Score how well this resume matches the job description. "
                        "Reply with EXACTLY 3 lines, plain text, no markdown, no extra words:\n"
                        "Match: <a single number from 0 to 100>\n"
                        "Status: <one word only: Shortlisted or Review or Rejected>\n"
                        "Reason: <one short sentence, no line breaks>"
                    )
                    with st.spinner(f"Screening {r.name}..."):
                        reply = call_ollama(prompt, max_tokens=120)
                    raw_replies[r.name] = reply
                    match_pct, status, reason = parse_match_reply(reply)
                    results.append({
                        "Candidate": r.name, "Match %": match_pct,
                        "Status": status, "Reason": reason,
                    })
                st.session_state.screening_results = results
                st.session_state.screening_raw = raw_replies
                st.success("Screening complete.")

        st.divider()
        st.subheader("Match Results")
        if st.session_state.screening_results:
            st.table(st.session_state.screening_results)
            with st.expander("🔍 Raw AI replies (debug)"):
                for name, raw in st.session_state.get("screening_raw", {}).items():
                    st.caption(name)
                    st.text(raw)
        else:
            st.info("Run AI Screening to see results here.")

    # --- Candidate Ranking AI ---
    with tab_rank:
        st.subheader("Candidate Ranking AI")
        st.caption("Ranking uses the results from the Resume Matching tab.")
        rank_by = st.selectbox("Rank By", ["Overall Match %", "Experience", "Skill Relevance", "Education"])

        if st.button("Rank Candidates"):
            if not st.session_state.screening_results:
                st.warning("Run Resume Matching first — ranking needs real screening results.")
            else:
                def to_num(v):
                    try:
                        return float(str(v).replace("%", "").strip())
                    except ValueError:
                        return -1
                ranked = sorted(
                    st.session_state.screening_results,
                    key=lambda r: to_num(r["Match %"]),
                    reverse=True,
                )
                if rank_by != "Overall Match %":
                    st.caption(
                        f"Note: only Match % is currently tracked from screening, "
                        f"so '{rank_by}' ranking falls back to Match % for now."
                    )
                st.table([
                    {"Rank": i + 1, "Candidate": r["Candidate"], "Score": r["Match %"]}
                    for i, r in enumerate(ranked)
                ])
        else:
            st.info("Click 'Rank Candidates' to rank using stored screening results.")

# ---------------- Candidate Search ----------------
elif page == "Candidate Search":
    st.title("Candidate Search")

    tab_search, tab_insight = st.tabs(["👤 Search", "🔎 Talent Insight AI"])

    with tab_search:
        st.text_input("Search Skills", key="search_skill")
        st.slider("Experience (Years)", 0, 20, 2, key="search_experience")
        st.selectbox("Location", ["Any", "Chennai", "Bangalore", "Hyderabad", "Remote"], key="search_location")
        st.button("Search Candidates")
        st.divider()
        st.warning(
            "This module needs a real candidate database to search — there isn't one yet, "
            "so it can't be meaningfully connected to Ollama. It just returns text right now. "
            "Once resumes are stored (e.g. after Resume Screening), this can filter/rank against them."
        )

    with tab_insight:
        st.subheader("Talent Insight AI")
        st.caption("AI-generated *estimate* of talent availability — not live market data.")
        if st.button("Generate Talent Insight"):
            skill = st.session_state.get("search_skill", "")
            exp = st.session_state.get("search_experience", 2)
            loc = st.session_state.get("search_location", "Any")
            if not skill:
                st.warning("Enter search skills in the Search tab first.")
            else:
                prompt = (
                    f"A recruiter is looking for candidates with skill(s): {skill}, "
                    f"around {exp} years of experience, in location: {loc}. "
                    "Give a brief, clearly-labeled ESTIMATE (not real data) of talent availability, "
                    "typical demand, and general salary expectations for this profile. "
                    "Keep it to 4-5 short lines."
                )
                with st.spinner("Generating insight..."):
                    insight = call_ollama(prompt)
                st.write(insight)
        else:
            st.info("Market availability, salary range, and demand trends will appear here.")

# ---------------- Candidate Comparison ----------------
elif page == "Candidate Comparison":
    st.title("Candidate Comparison")

    tab_compare, tab_reco = st.tabs(["⚖️ Candidate Comparison AI", "✅ Hiring Recommendation AI"])

    available_candidates = list(st.session_state.resume_texts.keys()) or ["John", "Alice", "David"]

    with tab_compare:
        st.subheader("Candidate Comparison AI")
        if not st.session_state.resume_texts:
            st.caption("No resumes uploaded yet — showing sample names. Upload resumes in Resume Screening for a real comparison.")
        candidates = st.multiselect("Select Candidates to Compare", available_candidates)

        if st.button("Compare Candidates"):
            if len(candidates) < 2:
                st.warning("Select at least two candidates.")
            else:
                profiles = ""
                for name in candidates:
                    text = st.session_state.resume_texts.get(name, f"(No resume text on file for {name} — sample candidate.)")
                    profiles += f"\n--- {name} ---\n{text[:700]}\n"

                prompt = (
                    f"Compare these candidates for a role based on their resumes:\n{profiles}\n\n"
                    "For each candidate, briefly rate: Skills Match, Experience, Communication (infer "
                    "conservatively if not stated), and Culture Fit (infer conservatively). "
                    "Present as a short list per candidate, not a long essay."
                )
                with st.spinner("Comparing candidates..."):
                    st.session_state.comparison_result = call_ollama(prompt)
                st.success("Comparison generated.")

        st.divider()
        if st.session_state.comparison_result:
            st.write(st.session_state.comparison_result)
        else:
            st.info("Comparison output will appear here.")

    with tab_reco:
        st.subheader("Hiring Recommendation AI")
        if st.button("Generate Hiring Recommendation"):
            if not st.session_state.comparison_result:
                st.warning("Run Candidate Comparison first.")
            else:
                prompt = (
                    f"Based on this candidate comparison:\n{st.session_state.comparison_result}\n\n"
                    "Recommend the single best-fit candidate and give 2-3 sentences of reasoning."
                )
                with st.spinner("Generating recommendation..."):
                    reco = call_ollama(prompt)
                st.write(reco)
        else:
            st.info("AI recommendation on the best-fit candidate will appear here.")

# ---------------- Interview Assistant ----------------
elif page == "Interview Assistant":
    st.title("Interview Assistant")
    st.caption(f"Interview Question Generator AI — Backend: {OLLAMA_MODEL}")

    role = st.text_input("Job Role")
    level = st.selectbox("Experience Level", ["Intern", "Junior", "Mid", "Senior"])

    tab_coding, tab_technical = st.tabs(["💻 Coding Questions", "🧠 Technical Questions"])

    with tab_coding:
        difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"])
        if st.button("Generate Coding Questions"):
            if not role:
                st.warning("Enter a job role first.")
            else:
                prompt = (
                    f"Generate 5 {difficulty.lower()}-difficulty coding interview questions "
                    f"for a {level}-level {role} candidate. Number them 1-5."
                )
                with st.spinner("Generating coding questions..."):
                    st.write(call_ollama(prompt))
        else:
            st.info("AI-generated coding questions will appear here.")

    with tab_technical:
        focus_area = st.text_input("Focus Area (e.g. System Design, Databases)")
        if st.button("Generate Technical Questions"):
            if not role:
                st.warning("Enter a job role first.")
            else:
                prompt = (
                    f"Generate 5 technical interview questions for a {level}-level {role} candidate, "
                    f"focused on: {focus_area or 'general technical knowledge for this role'}. Number them 1-5."
                )
                with st.spinner("Generating technical questions..."):
                    st.write(call_ollama(prompt))
        else:
            st.info("AI-generated technical questions will appear here.")

# ---------------- Resume Chat ----------------
elif page == "Resume Chat":
    st.title("Resume Chat AI")
    st.caption("Chat with an AI about a specific candidate's resume.")

    available_candidates = list(st.session_state.resume_texts.keys()) or ["John", "Alice", "David"]
    selected_resume = st.selectbox("Select Candidate Resume", available_candidates)

    if selected_resume not in st.session_state.resume_texts:
        st.warning(
            f"No resume text on file for '{selected_resume}' — upload resumes in Resume Screening "
            "first for the AI to answer accurately. Chat will still run but without real resume context."
        )
    else:
        preview = st.session_state.resume_texts[selected_resume]
        with st.expander("🔍 Resume text being used (debug)"):
            if not preview.strip():
                st.error("Extracted text is EMPTY. The file may be scanned/image-based, or extraction failed silently.")
            elif preview.strip().startswith("⚠️"):
                st.error(f"Extraction failed: {preview}")
            else:
                st.caption(f"{len(preview)} characters extracted")
                st.text(preview[:1000])

    for role_, msg in st.session_state.resume_chat_history:
        with st.chat_message(role_):
            st.write(msg)

    prompt = st.chat_input(f"Ask about {selected_resume}'s resume...")
    if prompt:
        st.session_state.resume_chat_history.append(("user", prompt))
        with st.chat_message("user"):
            st.write(prompt)

        resume_context = st.session_state.resume_texts.get(selected_resume, "")
        system_prompt = (
            f"You are answering questions about a candidate named {selected_resume}. "
            f"Here is their resume text (may be empty if not available):\n{resume_context[:1500]}\n"
            "If the resume text is empty, say you don't have their resume on file yet."
        )
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = call_ollama(prompt, system=system_prompt)
                st.write(reply)
        st.session_state.resume_chat_history.append(("assistant", reply))

# ---------------- Talent Analytics ----------------
elif page == "Talent Analytics":
    st.title("Talent Analytics")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Hiring Success", "89%")
        st.metric("Average Match", "84%")
    with col2:
        st.metric("Average Hiring Time", "12 Days")
        st.metric("Offer Acceptance", "91%")

    st.divider()

    # --- Real chart: match scores from actual screening results, if any exist ---
    st.subheader("Candidate Match Scores")
    if st.session_state.screening_results:
        st.caption("Real data — from your last Resume Screening run.")

        def to_num(v):
            try:
                return float(str(v).replace("%", "").strip())
            except ValueError:
                return 0

        names = [r["Candidate"] for r in st.session_state.screening_results]
        scores = [to_num(r["Match %"]) for r in st.session_state.screening_results]
        colors = [
            "#2ecc71" if s >= 80 else "#f1c40f" if s >= 50 else "#e74c3c"
            for s in scores
        ]

        fig_scores = go.Figure(go.Bar(x=names, y=scores, marker_color=colors, text=scores, textposition="auto"))
        fig_scores.update_layout(
            yaxis_title="Match %", yaxis_range=[0, 100],
            margin=dict(t=20, b=20), height=350,
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    else:
        st.info("No screening results yet — run Resume Screening to see real match-score charts here.")

    st.divider()

    tab_analysis, tab_gap, tab_report = st.tabs(
        ["📈 Recruitment Analysis AI", "📉 Skill Gap AI", "📝 Report Generator AI"]
    )

    with tab_analysis:
        st.subheader("Recruitment Analysis AI")

        # --- Illustrative chart: hiring funnel (mock, no real pipeline tracking yet) ---
        st.caption("⚠️ Illustrative data below — no real end-to-end pipeline is tracked yet.")
        funnel_stages = ["Applied", "Screened", "Shortlisted", "Interviewed", "Offered", "Hired"]
        funnel_values = [245, 120, 42, 16, 8, 6]
        fig_funnel = go.Figure(go.Funnel(y=funnel_stages, x=funnel_values, textinfo="value+percent initial"))
        fig_funnel.update_layout(margin=dict(t=20, b=20), height=380)
        st.plotly_chart(fig_funnel, use_container_width=True)

        months = ["Feb", "Mar", "Apr", "May", "Jun", "Jul"]
        hiring_success = [78, 81, 83, 85, 87, 89]
        avg_match = [74, 76, 79, 80, 82, 84]
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=months, y=hiring_success, mode="lines+markers", name="Hiring Success %"))
        fig_trend.add_trace(go.Scatter(x=months, y=avg_match, mode="lines+markers", name="Average Match %"))
        fig_trend.update_layout(yaxis_title="%", margin=dict(t=20, b=20), height=350)
        st.plotly_chart(fig_trend, use_container_width=True)

        st.subheader("AI Narrative Summary")
        if st.button("Generate Recruitment Analysis"):
            prompt = (
                "Write a short (4-5 sentence) recruitment performance analysis for a hiring dashboard "
                "with these metrics: Hiring Success 89%, Average Match 84%, Average Hiring Time 12 days, "
                "Offer Acceptance 91%. Note strengths and one area to improve."
            )
            with st.spinner("Analyzing..."):
                st.write(call_ollama(prompt))
        else:
            st.info("Click above for an AI-written summary of these trends.")

    with tab_gap:
        st.subheader("Skill Gap AI")
        st.caption("Upload a candidate's resume and the role they're applying for — the AI compares them directly.")

        gap_role = st.text_input("Job Role Applying For", placeholder="e.g. Backend Developer", key="gap_role")
        gap_resume_file = st.file_uploader(
            "Upload Candidate Resume", type=["pdf", "docx", "txt"], key="gap_resume_file"
        )

        if st.button("Analyze Skill Gap"):
            if not gap_role:
                st.warning("Enter the job role first.")
            elif not gap_resume_file:
                st.warning("Upload a resume first.")
            else:
                resume_text = extract_text(gap_resume_file)
                if not resume_text.strip():
                    st.error("Extracted resume text is empty — the file may be scanned/image-based.")
                elif resume_text.strip().startswith("⚠️"):
                    st.error(f"Extraction failed: {resume_text}")
                else:
                    prompt = (
                        f"Job role the candidate is applying for: {gap_role}\n\n"
                        f"Candidate resume:\n{resume_text[:1500]}\n\n"
                        "First, briefly note the key skills typically expected for this role. "
                        "Then compare those against the resume above and reply in exactly this format:\n"
                        "Matching Skills:\n- <skill>\n- <skill>\n\n"
                        "Skill Gaps:\n- <missing skill>\n- <missing skill>\n\n"
                        "Recommendation: <one sentence on what to upskill in first>"
                    )
                    with st.spinner(f"Analyzing {gap_resume_file.name} against {gap_role}..."):
                        st.session_state.skill_gap_result = call_ollama(prompt, max_tokens=300)

        st.divider()
        if st.session_state.skill_gap_result:
            st.write(st.session_state.skill_gap_result)
        else:
            st.info("Skill gap analysis will appear here.")

    with tab_report:
        st.subheader("Report Generator AI")
        report_type = st.selectbox("Report Type", ["Weekly Summary", "Monthly Summary", "Pipeline Report"])
        if st.button("Generate Report"):
            prompt = (
                f"Write a {report_type} for a recruitment team using these metrics: "
                "Hiring Success 89%, Average Match 84%, Average Hiring Time 12 days, "
                "Offer Acceptance 91%, Open Jobs 18, Shortlisted 42, Interviews 16. "
                "Keep it under 200 words, plain text, no markdown headers."
            )
            with st.spinner("Generating report..."):
                st.session_state.report_text = call_ollama(prompt)
            st.success("Report generated.")

        st.download_button(
            "Download Report",
            data=st.session_state.report_text or "No report generated yet.",
            file_name="report.txt",
            disabled=not bool(st.session_state.report_text),
        )
        if st.session_state.report_text:
            st.text_area("Report Preview", value=st.session_state.report_text, height=180)

# ---------------- Email Generator ----------------
elif page == "Email Generator":
    st.title("AI Email Generator")

    email_type = st.selectbox(
        "Email Type", ["Interview Invitation", "Offer Letter", "Rejection Email", "Follow-up Email"]
    )
    candidate_name = st.text_input("Candidate Name")
    job_role = st.text_input("Job Role")
    company_name = st.text_input("Company Name", placeholder="e.g. Acme Corp")
    tone = st.select_slider("Tone", ["Formal", "Friendly", "Concise"])

    extra_hints = {
        "Interview Invitation": "e.g. Date: July 22, Time: 3 PM, Venue: Office - 2nd Floor, or Google Meet link",
        "Offer Letter": "e.g. Salary: ₹8,00,000/year, Joining Date: Aug 1, Reporting Manager: ...",
        "Rejection Email": "e.g. Reason (optional), any encouragement to reapply later",
        "Follow-up Email": "e.g. What to follow up about, any deadline",
    }
    extra_details = st.text_area(
        "Extra Details (optional)",
        placeholder=extra_hints.get(email_type, "Any additional details to include..."),
        height=80,
    )

    if st.button("Generate Email"):
        if not candidate_name or not job_role:
            st.warning("Please enter candidate name and job role.")
        else:
            company_clause = f"from {company_name}" if company_name else "from the company"
            signoff_clause = f"Sign off as the recruitment team at {company_name}." if company_name else ""
            details_clause = (
                f" Include these specific details naturally in the email: {extra_details}."
                if extra_details.strip() else ""
            )
            prompt = (
                f"Write a {tone.lower()} {email_type.lower()} email {company_clause} to a candidate named "
                f"{candidate_name} for the role of {job_role}. {signoff_clause}{details_clause} "
                "Include a subject line at the top starting with 'Subject:'."
            )
            with st.spinner("Generating email..."):
                st.session_state.email_draft = call_ollama(prompt, max_tokens=350)
            st.session_state.email_reviewed = False  # reset review flag on every new generation
            st.success("Email generated. Review it below before sending.")

    st.divider()
    st.text_area(
        "Generated Email (edit as needed before sending)",
        key="email_draft",
        placeholder="Generated email content will appear here...",
        height=220,
    )

    st.divider()
    st.subheader("📧 Send Email")
    st.caption("Requires SMTP credentials in .streamlit/secrets.toml — see notes below.")

    recipient_email = st.text_input("Candidate's Email Address", placeholder="candidate@example.com")

    reviewed = st.checkbox(
        "I (HR) have reviewed this email and confirm it is accurate and ready to send.",
        key="email_reviewed",
    )

    send_disabled = not (reviewed and recipient_email and st.session_state.email_draft.strip())
    if st.button("Send Email", disabled=send_disabled, type="primary"):
        subject, body = split_subject_body(st.session_state.email_draft)
        with st.spinner(f"Sending to {recipient_email}..."):
            ok, message = send_email_smtp(recipient_email, subject, body)
        if ok:
            st.success(message)
        else:
            st.error(message)

    if not reviewed:
        st.caption("⬆️ Check the review box above to enable sending.")

    with st.expander("⚙️ One-time SMTP setup (do this once)"):
        st.markdown(
            "Create a file at `.streamlit/secrets.toml` next to `app.py` with:\n\n"
            "```toml\n"
            'SMTP_SERVER = "smtp.gmail.com"\n'
            "SMTP_PORT = 465\n"
            'SMTP_EMAIL = "your_email@gmail.com"\n'
            'SMTP_PASSWORD = "your_16_char_app_password"\n'
            "```\n\n"
            "**For Gmail:** you cannot use your normal password — generate an "
            "[App Password](https://myaccount.google.com/apppasswords) instead "
            "(requires 2-Step Verification to be enabled on the account).\n\n"
            "**Never commit `secrets.toml` to GitHub** — add it to `.gitignore`."
        )

# ---------------- Talent Management ----------------
elif page == "Talent Management":
    st.title("Talent Management & Retention Strategy")
    st.caption(f"A list view of employees/candidates with AI-generated growth & retention plans — Backend: {OLLAMA_MODEL}")

    RISK_BADGE = {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High", "Unknown": "⚪ Not analyzed"}

    # --- Add / import employees ---
    with st.expander("➕ Add / Import Employees", expanded=not st.session_state.employees):
        if st.session_state.resume_texts:
            if st.button("📥 Import candidates from Resume Screening"):
                existing = {e["name"] for e in st.session_state.employees}
                added = 0
                for name in st.session_state.resume_texts:
                    if name not in existing:
                        st.session_state.employees.append(
                            {"name": name, "role": "", "tenure": 0, "target_role": ""}
                        )
                        added += 1
                st.success(f"Imported {added} candidate(s)." if added else "All candidates already in the list.")
        else:
            st.caption("No resumes uploaded yet in Resume Screening — add employees manually below, or upload resumes first for AI to use real resume context.")

        st.markdown("**Add an employee manually**")
        c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 2, 1])
        new_name = c1.text_input("Name", key="new_emp_name", label_visibility="collapsed", placeholder="Name")
        new_role = c2.text_input("Current Role", key="new_emp_role", label_visibility="collapsed", placeholder="Current role")
        new_tenure = c3.number_input("Tenure", 0, 40, 1, key="new_emp_tenure", label_visibility="collapsed")
        new_target = c4.text_input("Target Role", key="new_emp_target", label_visibility="collapsed", placeholder="Target role")
        if c5.button("Add", use_container_width=True):
            if not new_name.strip():
                st.warning("Enter a name first.")
            elif any(e["name"] == new_name for e in st.session_state.employees):
                st.warning(f"{new_name} is already in the list.")
            else:
                st.session_state.employees.append(
                    {"name": new_name, "role": new_role, "tenure": new_tenure, "target_role": new_target}
                )
                st.success(f"Added {new_name}.")
                st.rerun()

    st.divider()

    if not st.session_state.employees:
        st.info("No employees added yet. Use the section above to add employees manually or import from Resume Screening.")
    else:
        top_col1, top_col2 = st.columns([1, 3])
        generate_all = top_col1.button("⚡ Generate Strategy for All", type="primary", use_container_width=True)
        top_col2.caption(f"{len(st.session_state.employees)} employee(s) in the list")

        # --- Summary table (quick glance at retention risk across everyone) ---
        summary_rows = []
        for emp in st.session_state.employees:
            result = st.session_state.talent_strategies.get(emp["name"])
            risk = parse_retention_risk(result) if result else "Unknown"
            summary_rows.append({
                "Name": emp["name"], "Role": emp["role"] or "—",
                "Tenure (yrs)": emp["tenure"], "Target Role": emp["target_role"] or "—",
                "Retention Risk": RISK_BADGE[risk],
            })
        st.table(summary_rows)

        st.subheader("Employee Details & Strategy")

        remove_idx = None
        for idx, emp in enumerate(st.session_state.employees):
            name = emp["name"]
            with st.container(border=True):
                r1c1, r1c2, r1c3, r1c4, r1c5, r1c6 = st.columns([2, 2, 1, 2, 1, 1])
                r1c1.markdown(f"**{name}**")
                emp["role"] = r1c2.text_input(
                    "Role", value=emp.get("role", ""), key=f"role_{idx}",
                    label_visibility="collapsed", placeholder="Current role",
                )
                emp["tenure"] = r1c3.number_input(
                    "Yrs", 0, 40, value=int(emp.get("tenure", 0)), key=f"tenure_{idx}",
                    label_visibility="collapsed",
                )
                emp["target_role"] = r1c4.text_input(
                    "Target", value=emp.get("target_role", ""), key=f"target_{idx}",
                    label_visibility="collapsed", placeholder="Target role",
                )
                gen_clicked = r1c5.button("Generate", key=f"gen_{idx}", use_container_width=True)
                remove_clicked = r1c6.button("🗑️", key=f"remove_{idx}", use_container_width=True)

                if remove_clicked:
                    remove_idx = idx

                if gen_clicked or generate_all:
                    resume_context = st.session_state.resume_texts.get(name, "")
                    prompt = (
                        f"Employee/Candidate: {name}\n"
                        f"Current Role: {emp['role'] or 'Not specified'}\n"
                        f"Tenure at Company: {emp['tenure']} years\n"
                        f"Target / Growth Role: {emp['target_role'] or 'Not specified'}\n"
                        f"Resume context (may be empty):\n{resume_context[:1000]}\n\n"
                        "As a talent management advisor, write a concise talent growth & retention "
                        "strategy covering exactly these four labeled sections, each with 2-3 short "
                        "bullet points, plain text, no markdown headers:\n"
                        "Retention Risk: (state Low, Medium, or High, plus a one-sentence reason)\n"
                        "Growth Path: (2-3 concrete next steps or roles)\n"
                        "Skill Development: (2-3 specific skills or certifications to invest in)\n"
                        "Retention Actions: (2-3 concrete actions HR or the manager should take)"
                    )
                    with st.spinner(f"Generating strategy for {name}..."):
                        st.session_state.talent_strategies[name] = call_ollama(prompt, max_tokens=350)

                result = st.session_state.talent_strategies.get(name)
                if result:
                    risk = parse_retention_risk(result)
                    st.caption(f"Retention Risk: {RISK_BADGE[risk]}")
                    with st.expander("View full growth & retention strategy"):
                        st.write(result)
                        st.download_button(
                            "Download Strategy", data=result,
                            file_name=f"{name}_talent_strategy.txt", key=f"dl_{idx}",
                        )
                else:
                    st.caption("No strategy generated yet — click Generate.")

        if remove_idx is not None:
            removed_name = st.session_state.employees[remove_idx]["name"]
            st.session_state.employees.pop(remove_idx)
            st.session_state.talent_strategies.pop(removed_name, None)
            st.rerun()

# ---------------- AI Chat ----------------
elif page == "AI Chat":
    st.title("AI Recruitment Copilot Chat")
    st.caption(f"Backend: {OLLAMA_MODEL} (Ollama, local)")

    for role_, msg in st.session_state.chat_history:
        with st.chat_message(role_):
            st.write(msg)

    user_input = st.chat_input("Find Python developers with 3+ years experience...")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Checking topic..."):
                on_topic = is_recruitment_related(user_input)

            if not on_topic:
                reply = (
                    "🚫 I'm scoped to this recruitment project only — I can help with job "
                    "descriptions, resumes, candidate screening/comparison, interview questions, "
                    "hiring recommendations, and recruitment analytics. "
                    "Please ask something related to recruitment or hiring."
                )
                st.write(reply)
            else:
                system_prompt = (
                    "You are an AI recruitment assistant helping a recruiter search candidates, "
                    "summarize resumes, and answer hiring questions. Only answer questions "
                    "within the recruitment/HR/talent-management domain."
                )
                with st.spinner("Thinking..."):
                    reply = call_ollama(user_input, system=system_prompt)
                st.write(reply)

        st.session_state.chat_history.append(("assistant", reply))