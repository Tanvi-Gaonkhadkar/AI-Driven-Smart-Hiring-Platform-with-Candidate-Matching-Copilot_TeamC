import streamlit as st

from utils.ai import ask_ai_jd_analysis
from utils.resume_parser import extract_resume_text


def display_section(title, content):

    st.markdown(
        f"""
        <h4 style="
        font-size:18px;
        margin-top:18px;
        margin-bottom:8px;">
        {title}
        </h4>
        """,
        unsafe_allow_html=True
    )

    if isinstance(content, list):

        if content:
            for item in content:
                st.write(f"• {item}")
        else:
            st.write("Not specified.")

    else:
        st.write(content if content else "Not specified.")


def job_description_analyzer_page():

    st.title(
        "Job Description Analyzer AI"
    )

    st.caption(
        "Analyze Job Descriptions using Llama 3.2 — "
        "paste a full JD, type just a role (e.g. \"AI Engineer\", "
        "\"SDE\"), or upload a file."
    )

    st.markdown("---")


    job_description = st.text_area(

        "Paste Job Description or type a Job Title",

        height=220,

        placeholder=
        "Paste a complete Job Description, or just type a role "
        "like \"AI Engineer\" or \"SDE\"..."

    )


    uploaded_file = st.file_uploader(

        "Upload Job Description",

        type=[
            "pdf",
            "docx",
            "txt"
        ],

        key="jd_upload"

    )


    st.markdown("---")


    if st.button(

        "Analyze Job Description",

        use_container_width=True

    ):


        if uploaded_file:


            try:

                job_description = extract_resume_text(
                    uploaded_file
                )


            except Exception:

                try:

                    job_description = (
                        uploaded_file
                        .read()
                        .decode(
                            "utf-8",
                            errors="ignore"
                        )
                    )

                except Exception:

                    st.error(
                        "Unable to read file."
                    )

                    return



        if not job_description.strip():

            st.warning(
                "Please provide a Job Description."
            )

            return


        with st.spinner(
            "Analyzing with Llama 3.2..."
        ):

            result = ask_ai_jd_analysis(job_description)


        if result.get("ai_error"):

            st.error(
                "The AI analysis failed or returned a response that "
                "couldn't be read. Check that Ollama is running "
                "(`ollama serve`) and that the `llama3.2` model is "
                "pulled. See the terminal running Streamlit for the "
                "exact error."
            )

            return


        # ==================================================
        # DISPLAY RESULT
        # ==================================================

        st.markdown("---")

        st.subheader(
            "AI Analysis"
        )


        with st.container(
            border=True
        ):

            display_section(
                "Job Title",
                result["job_title"]
            )


            display_section(
                "Required Skills",
                result["required_skills"]
            )


            display_section(
                "Experience Required",
                result["experience_required"]
            )


            display_section(
                "Education",
                result["education"]
            )


            display_section(
                "Key Responsibilities",
                result["key_responsibilities"]
            )


            display_section(
                "Preferred Qualifications",
                result["preferred_qualifications"]
            )


            display_section(
                "Important Keywords",
                result["important_keywords"]
            )


            display_section(
                "Summary",
                result["summary"]
            )


        st.success(
            "Job Description analyzed successfully."
        )


    else:

        st.info(
            "Paste or upload a Job Description and click Analyze Job Description."
        )


    st.markdown("---")


    st.caption(
        "AI Recruitment & Talent Management Copilot • Job Description Analyzer"
    )