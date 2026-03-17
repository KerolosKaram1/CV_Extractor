from fastapi import APIRouter, File, HTTPException, UploadFile, status

from src.models.schemas import SkillsResponse
from src.services.skill_extraction_service import SkillExtractionService


router = APIRouter()


@router.post(
    "/extract",
    response_model=SkillsResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract candidate name and skills from an uploaded CV",
    tags=["skills"],
)
async def extract_skills(
    file: UploadFile = File(..., description="CV file (PDF or DOCX). Use 'Choose File' to select a file; do not paste text."),
) -> SkillsResponse:
    """
    Accept a CV file (PDF or DOCX), send its content to the LLM,
    and return the extracted name and skills.

    **In Swagger UI:** Click "Choose File", select your PDF or DOCX, then "Execute".
    Do not type into the file field.
    """
    if not file.filename or file.filename.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file selected. Use 'Choose File' to select a PDF or DOCX file.",
        ) from None
    if file.content_type not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only PDF and DOCX are allowed.",
        )

    service = SkillExtractionService()

    try:
        result = await service.extract_from_cv(file)
    except ValueError as exc:
        # Domain errors: empty file, invalid JSON, or LLM API errors (auth, rate limit, etc.)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return SkillsResponse(name=result.name, skills=result.skills)

