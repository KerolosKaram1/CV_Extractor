from io import BytesIO

from fastapi import UploadFile
from PyPDF2 import PdfReader
from docx import Document


def _read_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file.
    """
    buffer = BytesIO(file_bytes)
    reader = PdfReader(buffer)
    pages_text: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)

    return "\n".join(pages_text)


def _read_docx(file_bytes: bytes) -> str:
    """
    Extract text from a DOCX file.
    """
    buffer = BytesIO(file_bytes)
    document = Document(buffer)
    paragraphs = [p.text for p in document.paragraphs]
    return "\n".join(paragraphs)


async def read_cv_text(upload_file: UploadFile) -> str:
    """
    Read the uploaded CV file and return its textual content.

    The function dispatches to the appropriate reader depending on the
    media type / file extension.
    """
    contents = await upload_file.read()

    if not contents.strip():
        raise ValueError("The uploaded file is empty.")

    content_type = (upload_file.content_type or "").lower()
    filename = (upload_file.filename or "").lower()

    if content_type == "application/pdf" or filename.endswith(".pdf"):
        return _read_pdf(contents)

    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or filename.endswith(
        ".docx"
    ):
        return _read_docx(contents)

    raise ValueError("Unsupported file type. Only PDF and DOCX are allowed.")

