"""
OCR text extraction for AI Document Verification (Section I).

Uses pytesseract + Pillow for image documents (JPG/PNG), and the existing
utils/text_extraction.py for PDF/DOCX (those already have real text, no
OCR needed). Tesseract is a separate system binary pytesseract calls out
to - it is NOT bundled with the pip package, so this degrades gracefully
if it isn't installed rather than crashing the page:

    Windows: https://github.com/UB-Mannheim/tesseract/wiki
    macOS:   brew install tesseract
    Linux:   sudo apt install tesseract-ocr

If Tesseract isn't found, is_ocr_available() returns False and the page
shows a "manual review needed" notice for image uploads instead of
failing. PDF/DOCX documents work either way.
"""

import io


def is_ocr_available() -> bool:
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text_from_document(uploaded_file) -> str:
    """
    Takes a Streamlit UploadedFile of any supported document type (PDF,
    DOCX, or an image) and returns its plain text - via the existing
    text_extraction helpers for PDF/DOCX, or OCR for images.
    Raises ValueError with a friendly message if extraction isn't possible.
    """
    name = uploaded_file.name.lower()

    if name.endswith(".pdf") or name.endswith(".docx"):
        from utils.text_extraction import extract_text
        return extract_text(uploaded_file)

    if name.endswith((".jpg", ".jpeg", ".png")):
        if not is_ocr_available():
            raise ValueError(
                "OCR isn't available - Tesseract OCR isn't installed on this machine. "
                "Install it (see utils/ocr.py for links) or upload a PDF instead."
            )
        import pytesseract
        from PIL import Image
        image = Image.open(io.BytesIO(uploaded_file.getvalue()))
        text = pytesseract.image_to_string(image).strip()
        if not text:
            raise ValueError("OCR couldn't read any text from this image - try a clearer scan.")
        return text

    raise ValueError("Only PDF, JPG, and PNG documents are supported for verification.")
