from typing import List

from pydantic import BaseModel, Field


class SkillsResponse(BaseModel):
    """
    Response model for the CV skills extraction endpoint.
    """

    name: str = Field(
        ...,
        description="Candidate full name extracted from the CV.",
        example="John Doe",
    )
    skills: List[str] = Field(
        ...,
        description="List of skills extracted from the CV.",
        example=["Python", "Machine Learning", "SQL"],
    )

