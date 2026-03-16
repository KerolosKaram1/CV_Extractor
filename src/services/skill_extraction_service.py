from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

from src.clients.llm_client import LLMClient, LLMExtractionResult
from src.utils.file_utils import read_cv_text


class SkillExtractionService:
    """
    Service coordinating CV text extraction and LLM-based name/skills extraction.
    """

    def __init__(self) -> None:
        self._llm_client = LLMClient()

    async def extract_from_cv(self, file: UploadFile) -> LLMExtractionResult:
        """
        High-level use case:

        1. Read and normalize text from the uploaded CV file.
        2. Call the LLM client to extract name and skills.
        """
        cv_text = await read_cv_text(file)

        # The OpenAI client is synchronous; we run it in a threadpool to keep
        # the FastAPI event loop responsive under load.
        result: LLMExtractionResult = await run_in_threadpool(
            self._llm_client.extract_name_and_skills,
            cv_text,
        )

        return result


