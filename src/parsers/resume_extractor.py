import re
from typing import Dict, List, Optional

from src.models.response_models import (
    CertificateItem,
    EducationItem,
    ExperienceItem,
    OrganizationItem,
    ProjectItem,
    ResumeResponse,
)
from src.parsers.resume_section_detector import Section


def _extract_name(text: str) -> Optional[str]:
    # Heuristic: use the first non-empty line that is not an obvious header/contact line.
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(keyword in stripped.lower() for keyword in ["email", "phone", "linkedin", "github"]):
            continue
        if 1 < len(stripped.split()) <= 5:
            return stripped
    return None


def _extract_email(text: str) -> Optional[str]:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> Optional[str]:
    match = re.search(r"(\+?\d[\d\s\-()]{7,})", text)
    return match.group(0).strip() if match else None


def _extract_location(text: str) -> Optional[str]:
    # Very lightweight heuristic: look for lines containing city/country-like separators.
    for line in text.splitlines():
        stripped = line.strip()
        if "," in stripped and any(ch.isalpha() for ch in stripped):
            return stripped
    return None


def _split_lines(section: Section) -> List[str]:
    return [line.strip() for line in section.content.splitlines() if line.strip()]


def _parse_education(section: Section) -> List[EducationItem]:
    entries: List[EducationItem] = []
    for line in _split_lines(section):
        entries.append(EducationItem(degree=line))
    return entries


def _parse_experience(section: Section) -> List[ExperienceItem]:
    entries: List[ExperienceItem] = []
    for line in _split_lines(section):
        entries.append(ExperienceItem(description=line))
    return entries


def _parse_projects(section: Section) -> List[ProjectItem]:
    entries: List[ProjectItem] = []
    for line in _split_lines(section):
        # Naive parse: split on hyphen or colon to get name/description.
        if " - " in line:
            name, desc = line.split(" - ", 1)
            entries.append(ProjectItem(name=name.strip(), description=desc.strip()))
        elif ":" in line:
            name, desc = line.split(":", 1)
            entries.append(ProjectItem(name=name.strip(), description=desc.strip()))
        else:
            entries.append(ProjectItem(description=line))
    return entries


def _parse_certificates(section: Section) -> List[CertificateItem]:
    return [CertificateItem(name=line) for line in _split_lines(section)]


def _parse_organizations(section: Section) -> List[OrganizationItem]:
    return [OrganizationItem(name=line) for line in _split_lines(section)]


def _parse_skills(section: Section) -> List[str]:
    content = section.content.replace("\n", ",")
    raw_items = [item.strip() for item in re.split(r"[,\n;]", content) if item.strip()]
    # Deduplicate while preserving order
    seen = set()
    skills: List[str] = []
    for item in raw_items:
        lower = item.lower()
        if lower not in seen:
            seen.add(lower)
            skills.append(item)
    return skills


def build_resume_response(
    full_text: str,
    sections: Dict[str, Section],
) -> ResumeResponse:
    """
    Convert raw text and detected sections into a structured ResumeResponse.
    """
    resume = ResumeResponse()

    # Top-level fields inferred from the entire document.
    resume.name = _extract_name(full_text)
    resume.email = _extract_email(full_text)
    resume.phone = _extract_phone(full_text)
    resume.location = _extract_location(full_text)

    # Professional summary
    summary_section = sections.get("professional_summary")
    if summary_section:
        resume.professional_summary = summary_section.content.strip()

    # Education
    education_section = sections.get("education")
    if education_section:
        resume.education = _parse_education(education_section)

    # Experience
    experience_section = sections.get("professional_experience")
    if experience_section:
        resume.professional_experience = _parse_experience(experience_section)

    # Projects
    projects_section = sections.get("projects")
    if projects_section:
        resume.projects = _parse_projects(projects_section)

    # Certificates
    certificates_section = sections.get("certificates")
    if certificates_section:
        resume.certificates = _parse_certificates(certificates_section)

    # Organizations
    organizations_section = sections.get("organizations")
    if organizations_section:
        resume.organizations = _parse_organizations(organizations_section)

    # Skills
    technical_section = sections.get("technical_skills")
    if technical_section:
        resume.technical_skills = _parse_skills(technical_section)

    soft_section = sections.get("soft_skills")
    if soft_section:
        resume.soft_skills = _parse_skills(soft_section)

    return resume

