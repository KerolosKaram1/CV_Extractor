from typing import List, Optional

from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    degree: Optional[str] = Field(default=None, description="Degree title, e.g. BSc Computer Science.")
    university: Optional[str] = Field(default=None, description="Institution name.")
    year: Optional[str] = Field(default=None, description="Graduation or attendance year.")


class ProjectItem(BaseModel):
    name: Optional[str] = Field(default=None, description="Project name or title.")
    description: Optional[str] = Field(default=None, description="Short description of the project.")


class ExperienceItem(BaseModel):
    title: Optional[str] = Field(default=None, description="Job title.")
    company: Optional[str] = Field(default=None, description="Company or organization name.")
    period: Optional[str] = Field(default=None, description="Employment period.")
    description: Optional[str] = Field(default=None, description="Summary of responsibilities and achievements.")


class CertificateItem(BaseModel):
    name: Optional[str] = Field(default=None, description="Certificate name.")
    issuer: Optional[str] = Field(default=None, description="Issuing organization.")
    year: Optional[str] = Field(default=None, description="Year obtained.")


class OrganizationItem(BaseModel):
    name: Optional[str] = Field(default=None, description="Organization or association name.")
    role: Optional[str] = Field(default=None, description="Role or position.")
    period: Optional[str] = Field(default=None, description="Involvement period.")


class ResumeResponse(BaseModel):
    """
    Top-level response model for the resume parser.

    Only non-null fields will be serialized to JSON so that
    missing sections are simply omitted from the API response.
    """

    name: Optional[str] = Field(default=None, description="Candidate full name.")
    email: Optional[str] = Field(default=None, description="Primary contact email.")
    phone: Optional[str] = Field(default=None, description="Primary phone number.")
    location: Optional[str] = Field(default=None, description="Candidate location.")
    professional_summary: Optional[str] = Field(default=None, description="Professional summary / profile section.")

    education: Optional[List[EducationItem]] = Field(default=None, description="List of education entries.")
    professional_experience: Optional[List[ExperienceItem]] = Field(
        default=None,
        description="List of professional experience entries.",
    )
    organizations: Optional[List[OrganizationItem]] = Field(
        default=None,
        description="List of organizations / memberships.",
    )
    certificates: Optional[List[CertificateItem]] = Field(
        default=None,
        description="List of certificates.",
    )
    projects: Optional[List[ProjectItem]] = Field(default=None, description="List of highlighted projects.")
    technical_skills: Optional[List[str]] = Field(default=None, description="List of technical skills.")
    soft_skills: Optional[List[str]] = Field(default=None, description="List of soft skills.")

    class Config:
        # Ensure fields with value None are excluded from serialized JSON.
        json_encoders = {}
        orm_mode = True

