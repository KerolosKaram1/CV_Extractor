"""
Orchestrates the full resume parsing flow: file → text → clean → LLM → post-process → response.
"""

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

from src.clients.llm_client import LLMClient
from src.models.response_models import ResumeResponse
from src.parsers.file_parser import parse_file_to_text
from src.parsers.resume_post_processor import process_resume_response
from src.utils.text_cleaner import clean_cv_text


class ResumeParsingService:
    """
    Orchestrates resume parsing:
    1. Extract raw text from uploaded file (PDF/DOCX).
    2. Preprocess text (clean bullets, whitespace, separators).
    3. Send cleaned text to LLM for structured extraction.
    4. Post-process and validate LLM output (name/location/skills, consolidation).
    5. Return validated ResumeResponse.
    """

    def __init__(self) -> None:
        self._llm_client = LLMClient()

    async def parse_resume(self, file: UploadFile) -> ResumeResponse:
        """
        Parse uploaded CV into structured JSON. Raises ValueError on empty text or LLM/JSON errors.
        """
        # 1. Extract raw text
        raw_text = await parse_file_to_text(file)
        if not raw_text or not raw_text.strip():
            raise ValueError("The uploaded file produced no text. The file may be empty or unreadable.")

        # 2. Preprocess
        cleaned_text = clean_cv_text(raw_text)
        if not cleaned_text.strip():
            raise ValueError("After cleaning, the CV text is empty. The file may be image-only or corrupted.")

        # 3. LLM extraction (sync client → run in threadpool)
        try:
            raw_resume = await run_in_threadpool(
                self._llm_client.extract_full_resume,
                cleaned_text,
            )
        except ValueError:
            raise

        # 4. Post-process and validate
        processed = process_resume_response(raw_resume)

        # 5. Build response model (only include non-null fields)
        return ResumeResponse.model_validate(processed)
