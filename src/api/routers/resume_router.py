from fastapi import APIRouter, File, HTTPException, UploadFile, status

from src.models.response_models import ResumeResponse
from src.services.resume_parsing_service import ResumeParsingService


router = APIRouter()


@router.post(
    "/parse-resume",
    response_model=ResumeResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse a resume/CV into structured sections",
    tags=["resume"],
)
async def parse_resume(file: UploadFile = File(...)) -> ResumeResponse:
    """
    Accept a CV/Resume file (PDF or DOCX), extract its text, and return
    structured JSON containing only the sections that were successfully parsed.
    """
    if file.content_type not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only PDF and DOCX are allowed.",
        )

    service = ResumeParsingService()

    try:
        resume = await service.parse_resume(file)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while parsing the resume.",
        ) from exc

    # Exclude any fields that were not populated from the output JSON.
    return ResumeResponse.parse_obj(resume.model_dump(exclude_none=True))

