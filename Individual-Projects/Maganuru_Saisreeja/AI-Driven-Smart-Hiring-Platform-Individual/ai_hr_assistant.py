import streamlit as st
from utils.resume_parser import extract_resume_text
from utils.ai import ask_ai, validate_prompt


def ai_hr_assistant():

    st.title("AI HR Assistant")
    st.caption(
        "Your AI-powered recruitment and HR assistant for resume analysis, hiring decisions, interview preparation, and general HR guidance."
    )

    st.markdown("---")

    if "ai_hr_chat_history" not in st.session_state:
        st.session_state.ai_hr_chat_history = []

    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    left, right = st.columns([1, 2])

    # =====================================================
    # LEFT PANEL
    # =====================================================

    with left:

        st.subheader("Candidate Resume")

        uploaded = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx"]
        )

        if uploaded is not None:

            with st.spinner("Reading resume..."):
                st.session_state.resume_text = extract_resume_text(uploaded)

            st.success("Resume loaded successfully.")

        st.markdown("---")

        if st.button("Clear Chat", use_container_width=True):
            st.session_state.ai_hr_chat_history = []
            st.rerun()

    # =====================================================
    # RIGHT PANEL
    # =====================================================

    with right:

        st.subheader("AI HR Conversation")

        for role, msg in st.session_state.ai_hr_chat_history:

            with st.chat_message(role):
                st.markdown(msg)

        question = st.chat_input(
            "Ask any recruitment or HR-related question..."
        )

        if question:

            st.session_state.ai_hr_chat_history.append(
                ("user", question)
            )

            with st.chat_message("user"):
                st.markdown(question)

            # =====================================================
            # TOPIC GATE
            # =====================================================
            #
            # ask_ai()'s own validation is skipped whenever the full
            # prompt contains the word "Resume" — which it always
            # does here, since the prompt template itself includes a
            # "Resume" heading even when the recruiter's actual
            # question is off-topic. That let ANY question through
            # once a resume was uploaded. Validate the raw question
            # text directly, before it ever gets wrapped in a prompt,
            # so the restriction actually applies regardless of
            # whether a resume is loaded.

            if not validate_prompt(question):

                refusal = (
                    "This assistant only answers recruitment, hiring, "
                    "and HR-related questions (including questions "
                    "about an uploaded resume). Please ask something "
                    "related to HR or recruitment."
                )

                with st.chat_message("assistant"):
                    st.markdown(refusal)

                st.session_state.ai_hr_chat_history.append(
                    ("assistant", refusal)
                )

            else:

                # =====================================================
                # RESUME UPLOADED
                # =====================================================

                if st.session_state.resume_text:

                    prompt = f"""
You are an experienced AI HR Assistant helping recruiters.

Answer professionally using Markdown.

You can help with:
- Resume analysis
- Candidate evaluation
- Skill assessment
- Job-role matching
- Hiring recommendations
- Interview preparation
- Recruitment best practices
- General HR guidance

If the recruiter asks about the uploaded candidate,
use ONLY the information present in the resume.

Do NOT invent experience, skills, education, certifications,
or projects.

If the requested information is not available in the resume,
reply exactly:

"This information is not available in the uploaded resume."

If the recruiter asks a general HR or recruitment question,
answer it normally.

Resume
-------
{st.session_state.resume_text}

Recruiter Question
------------------
{question}
"""

                # =====================================================
                # NO RESUME
                # =====================================================

                else:

                    prompt = f"""
You are an experienced AI HR Assistant.

Answer ONLY HR and recruitment related questions.

Topics include:
- Recruitment
- Resume screening
- Candidate evaluation
- Interview preparation
- Hiring decisions
- Talent management
- HR policies
- Employee engagement
- Performance management
- HR analytics
- Recruitment best practices

If the recruiter asks about a specific candidate,
politely ask them to upload a resume first.

Return your response in well-formatted Markdown
using headings and bullet points whenever appropriate.

Recruiter Question
------------------
{question}
"""

                with st.chat_message("assistant"):

                    with st.spinner("Thinking..."):
                        # strict_scope=False: this is a free-form chat
                        # assistant, not a candidate-data extraction
                        # call. General questions (e.g. "skills
                        # required for an AI engineer") should be
                        # answered from the model's own knowledge even
                        # when a resume happens to be loaded — only
                        # candidate-specific questions should be
                        # restricted to the resume text itself, which
                        # the prompt template above already handles.
                        answer = ask_ai(prompt, strict_scope=False)

                    st.markdown(answer)

                st.session_state.ai_hr_chat_history.append(
                    ("assistant", answer)
                )