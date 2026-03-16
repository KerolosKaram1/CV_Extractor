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
async def extract_skills(file: UploadFile = File(...)) -> SkillsResponse:
    """
    Accept a CV file (PDF or DOCX), send its content to the LLM,
    and return the extracted name and skills.
    """
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
        # Domain errors (empty file, invalid JSON from LLM, etc.)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        import traceback
        traceback.print_exc()   # يظهر الخطأ الحقيقي في التيرمينال
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    return SkillsResponse(name=result.name, skills=result.skills)

