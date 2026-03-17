import json
from typing import Any, Dict

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from src.core.config import get_settings


# Strict schema description for full resume extraction (used in prompt)
RESUME_EXTRACTION_SCHEMA = """
{
  "name": string or null,
  "email": string or null,
  "phone": string or null,
  "location": string or null,
  "professional_summary": string or null,
  "education": [ { "degree": string, "university": string, "year": string } ] or null,
  "professional_experience": [ { "title": string, "company": string, "period": string, "description": string } ] or null,
  "projects": [ { "name": string, "description": string } ] or null,
  "technical_skills": [ string ] or null,
  "soft_skills": [ string ] or null
}
"""

RESUME_EXTRACTION_SYSTEM = (
    "You are an expert resume parser. Extract structured data from the CV text below. "
    "Return ONLY valid JSON. Do not include any explanations or markdown. "
    "Do not invent information. If a field or section is missing, use null. "
    "Do not merge different fields (e.g. do not put email in the name field). "
    "Keep each education, experience, and project as separate objects with correct degree/university/year and title/company/period/description."
)

RESUME_EXTRACTION_USER_PREFIX = (
    "Extract the following fields from the CV. Return ONLY valid JSON matching this schema. "
    "Use null for missing fields. Do not invent data.\n\n"
    f"Schema:\n{RESUME_EXTRACTION_SCHEMA}\n\n"
    "CV TEXT:\n\n"
)


class LLMExtractionResult(BaseModel):
    """
    Structured result returned from the LLM.
    """

    name: str
    skills: list[str]


class LLMClient:
    """
    Client responsible for communicating with the Qwen model via OpenRouter.
    """

    def __init__(self) -> None:

        settings = get_settings()

        self._model = settings.llm_model

        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "cv-skill-extractor",
            },
        )

    def extract_name_and_skills(self, cv_text: str) -> LLMExtractionResult:
        """
        Send CV text to the LLM and return structured extraction.
        """

        prompt = (
            "You are a resume information extraction system.\n"
            "Extract the candidate FULL NAME and ALL SKILLS from the CV.\n"
            "Focus especially on the SKILLS section.\n\n"
            "Return ONLY valid JSON.\n\n"
            "Schema:\n"
            '{ "name": "John Doe", "skills": ["Python","Machine Learning","SQL"] }\n\n'
            f"CV TEXT:\n{cv_text}"
        )

        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict JSON extraction API.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0,
            )
        except Exception as exc:
            # Surface the real API error (auth, rate limit, model not found, etc.)
            raise ValueError(f"LLM API error: {exc!s}") from exc

        content = completion.choices[0].message.content or "{}"

        try:

            raw: Dict[str, Any] = json.loads(content)

        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid JSON.") from exc

        try:

            return LLMExtractionResult.model_validate(raw)

        except ValidationError as exc:
            raise ValueError("LLM JSON does not match expected schema.") from exc

    def extract_full_resume(self, cv_text: str) -> Dict[str, Any]:
        """
        Extract full resume structure from CV text using the LLM.

        Uses a strict prompt and response_format=json_object.
        Returns a dict that may contain nulls and must be post-processed
        and validated against ResumeResponse.
        """
        if not cv_text or not cv_text.strip():
            raise ValueError("CV text is empty; cannot extract resume.")

        user_content = RESUME_EXTRACTION_USER_PREFIX + cv_text.strip()

        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": RESUME_EXTRACTION_SYSTEM},
                    {"role": "user", "content": user_content},
                ],
                temperature=0,
            )
        except Exception as exc:
            raise ValueError(f"LLM API error: {exc!s}") from exc

        content = completion.choices[0].message.content or "{}"
        try:
            raw = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid JSON.") from exc

        if not isinstance(raw, dict):
            raise ValueError("LLM response is not a JSON object.")

        return raw