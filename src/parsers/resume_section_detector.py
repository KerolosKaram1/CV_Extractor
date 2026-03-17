from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Section:
    """
    Represents a logical section in the resume text.
    """

    title: str
    content: str


SECTION_TITLE_PATTERNS: Dict[str, List[str]] = {
    # Professional summary / profile block
    "professional_summary": [
        r"professional summary",
        r"summary",
        r"profile",
        r"professional profile",
        r"about me",
        r"career summary",
        r"career profile",
        r"objective",
        r"career objective",
    ],
    # Education / academic background
    "education": [
        r"education",
        r"education & training",
        r"academic background",
        r"academic qualifications",
        r"qualifications",
        r"studies",
    ],
    # Work / professional experience
    "professional_experience": [
        r"experience",
        r"work experience",
        r"work history",
        r"professional experience",
        r"professional history",
        r"employment history",
        r"career history",
    ],
    # Projects
    "projects": [
        r"projects",
        r"key projects",
        r"notable projects",
        r"selected projects",
        r"personal projects",
        r"academic projects",
    ],
    # Organizations / memberships / volunteering
    "organizations": [
        r"organizations",
        r"memberships",
        r"professional memberships",
        r"affiliations",
        r"professional affiliations",
        r"volunteering",
        r"volunteer experience",
        r"community involvement",
    ],
    # Certificates and licenses
    "certificates": [
        r"certifications",
        r"certificates",
        r"licenses",
        r"licenses & certifications",
        r"professional certifications",
    ],
    # Technical / hard skills
    "technical_skills": [
        r"technical skills",
        r"technical competencies",
        r"technical expertise",
        r"hard skills",
        r"it skills",
        r"computer skills",
    ],
    # Soft / interpersonal skills
    "soft_skills": [
        r"soft skills",
        r"interpersonal skills",
        r"communication skills",
        r"people skills",
        r"leadership skills",
    ],
}


def detect_sections(text: str) -> Dict[str, Section]:
    """
    Detect high-level resume sections in the raw text.

    This function uses simple heading heuristics:
    - A line that matches one of the known section title patterns is treated as a header.
    - Content from that line until the next header becomes the section body.
    """
    lines = [line.rstrip() for line in text.splitlines()]

    # Precompile mapping from lowercase line to canonical section key
    compiled_patterns: List[tuple[str, re.Pattern[str]]] = []
    for section_key, patterns in SECTION_TITLE_PATTERNS.items():
        for pattern in patterns:
            compiled_patterns.append((section_key, re.compile(rf"^{pattern}\s*:?\s*$", re.IGNORECASE)))

    sections: Dict[str, Section] = {}
    current_key: str | None = None
    buffer: List[str] = []

    def flush_current() -> None:
        nonlocal current_key, buffer
        if current_key and buffer:
            content = "\n".join(line for line in buffer).strip()
            if content:
                sections[current_key] = Section(title=current_key, content=content)
        buffer = []

    for raw_line in lines:
        stripped = raw_line.strip()
        # Check if this line is a section title
        matched_key: str | None = None
        for section_key, pattern in compiled_patterns:
            if pattern.match(stripped):
                matched_key = section_key
                break

        if matched_key:
            flush_current()
            current_key = matched_key
            continue

        if current_key:
            buffer.append(raw_line)

    flush_current()

    return sections

