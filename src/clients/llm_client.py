# import json
# from typing import Any, Dict
#
# from openai import OpenAI
# from pydantic import BaseModel, ValidationError
#
# from src.core.config import get_settings
#
#
# class LLMExtractionResult(BaseModel):
#     """
#     Structured result returned from the LLM.
#     """
#
#     name: str
#     skills: list[str]
#
#
# class LLMClient:
#     """
#     Client responsible for talking to the Qwen model via the OpenRouter API.
#     """
#
#     def __init__(self) -> None:
#         settings = get_settings()
#         self._model = settings.llm_model
#         self._client = OpenAI(
#             base_url="https://openrouter.ai/api/v1",
#             api_key=settings.openrouter_api_key,
#             default_headers={
#                 "HTTP-Referer": "http://localhost:8000",
#                 "X-Title": "cv-skill-extractor",
#             },
#         )
#
#     def extract_name_and_skills(self, cv_text: str) -> LLMExtractionResult:
#         """
#         Call the LLM with a structured prompt and parse the JSON response.
#         """
#         prompt = (
#             "You are an information extraction system.\n"
#             "Extract the candidate full name and skills from the CV text below.\n"
#             "Focus especially on the SKILLS section if present.\n"
#             "Return ONLY valid JSON with the following shape:\n"
#             '{\n  "name": "John Doe",\n  "skills": ["Python","Machine Learning","SQL"]\n}\n\n'
#             f"CV TEXT:\n{cv_text}"
#         )
#
#         completion = self._client.chat.completions.create(
#             model=self._model,
#             response_format={"type": "json_object"},
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are a strict JSON information extraction API.",
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 },
#             ],
#         )
#
#         content = completion.choices[0].message.content or "{}"
#
#         try:
#             raw: Dict[str, Any] = json.loads(content)
#         except json.JSONDecodeError as exc:
#             raise ValueError("LLM returned invalid JSON.") from exc
#
#         try:
#             return LLMExtractionResult.model_validate(raw)
#         except ValidationError as exc:
#             raise ValueError("LLM JSON did not match expected schema.") from exc
#
import json
from typing import Any, Dict

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from src.core.config import get_settings


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
            raise RuntimeError("Failed to call LLM API.") from exc

        content = completion.choices[0].message.content or "{}"

        try:

            raw: Dict[str, Any] = json.loads(content)

        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid JSON.") from exc

        try:

            return LLMExtractionResult.model_validate(raw)

        except ValidationError as exc:
            raise ValueError("LLM JSON does not match expected schema.") from exc