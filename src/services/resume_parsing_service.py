from fastapi import UploadFile

from src.models.response_models import ResumeResponse
from src.parsers.file_parser import parse_file_to_text
from src.parsers.resume_extractor import build_resume_response
from src.parsers.resume_section_detector import detect_sections


class ResumeParsingService:
    """
    Orchestrates the full resume parsing flow:
    - Read file contents and normalize to text.
    - Detect logical sections.
    - Extract structured resume data.
    """

    async def parse_resume(self, file: UploadFile) -> ResumeResponse:
        text = await parse_file_to_text(file)
        sections = detect_sections(text)
        resume = build_resume_response(text, sections)
        return resume

