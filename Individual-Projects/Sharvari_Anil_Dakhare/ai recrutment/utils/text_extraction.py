"""
Text extraction for uploaded resumes.

Streamlit's file_uploader gives us an in-memory file object - these
functions turn that into plain text so it can be sent to the AI service.
"""

import io


def extract_text(uploaded_file) -> str:
    """
    Takes a Streamlit UploadedFile (pdf or docx) and returns its plain text.
    Raises ValueError with a friendly message if the file type isn't supported
    or the file can't be read.
    """
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return _extract_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return _extract_docx(uploaded_file)
    else:
        raise ValueError("Only .pdf and .docx resumes are supported right now.")


def _extract_pdf(uploaded_file) -> str:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    text = "\n".join(text_parts).strip()
    if not text:
        raise ValueError(
            "Couldn't extract any text from this PDF - it may be a scanned "
            "image rather than a text PDF."
        )
    return text


def _extract_docx(uploaded_file) -> str:
    import docx
    document = docx.Document(io.BytesIO(uploaded_file.getvalue()))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs).strip()
    if not text:
        raise ValueError("Couldn't extract any text from this Word document.")
    return text
