"""Pydantic schema definitions and validation for profile.yml."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from scripts.errors import ProfileValidationError, format_validation_error
from scripts.sanitize import is_safe_url


class ProjectStatus(str, Enum):
    SHIPPED = "shipped"
    BUILDING = "building"
    PLANNED = "planned"


class RoadmapStatus(str, Enum):
    DONE = "done"
    DOING = "doing"
    NEXT = "next"


class CertificationKind(str, Enum):
    CERTIFICATION = "certification"
    COURSE = "course"


class SkillLevel(str, Enum):
    DAILY = "daily"
    COMFORTABLE = "comfortable"
    LEARNING = "learning"


class AvailabilityStatus(str, Enum):
    OPEN_TO_WORK = "open_to_work"
    OPEN_TO_INTERNSHIPS = "open_to_internships"
    FREELANCE = "freelance"
    NOT_LOOKING = "not_looking"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)


class Availability(StrictModel):
    status: AvailabilityStatus = AvailabilityStatus.OPEN_TO_WORK
    text: str | None = None
    work_mode: str | None = None


class EducationItem(StrictModel):
    school: str
    degree: str
    start: str | None = None
    end: str | None = None
    score: str | None = None


class Identity(StrictModel):
    name: str
    handle: str
    headline: str | None = None
    tagline: str | None = None
    location: str | None = None
    languages_spoken: list[str] = Field(default_factory=list)
    availability: Availability = Field(default_factory=Availability)
    roles_targeted: list[str] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    focus_areas: list[str] = Field(default_factory=list)


class Links(StrictModel):
    github: str | None = None
    linkedin: str | None = None
    leetcode: str | None = None
    portfolio: str | None = None
    resume_pdf: str | None = None
    email: str | None = None
    kaggle: str | None = None
    huggingface: str | None = None
    scholar: str | None = None
    x_twitter: str | None = None
    blog: str | None = None
    wakatime: str | None = None

    @field_validator("*", mode="before")
    @classmethod
    def validate_url(cls, v: Any, info: Any) -> Any:
        if not v:
            return None
        val = str(v).strip()
        if info.field_name == "email":
            if not val.startswith("mailto:") and "@" in val:
                val = f"mailto:{val}"
            if not is_safe_url(val):
                raise ValueError(f"Invalid email '{v}'. Must be a valid email or mailto link.")
            return val
        if not is_safe_url(val):
            raise ValueError(f"Unsafe or invalid URL '{v}'. Must start with http://, https://, or mailto:.")
        return val


class NowBlock(StrictModel):
    updated: str | None = None
    building: list[str] = Field(default_factory=list)
    learning: list[str] = Field(default_factory=list)
    reading: list[str] = Field(default_factory=list)
    exploring: list[str] = Field(default_factory=list)


class RoadmapItem(StrictModel):
    item: str
    status: RoadmapStatus
    target: str | None = None


class Goals(StrictModel):
    short_term: list[str] = Field(default_factory=list)
    mid_term: list[str] = Field(default_factory=list)
    long_term: list[str] = Field(default_factory=list)
    roadmap: list[RoadmapItem] = Field(default_factory=list)


class PrincipleItem(StrictModel):
    title: str
    detail: str


class SkillItem(StrictModel):
    name: str
    level: SkillLevel | None = None


class SkillGroup(StrictModel):
    name: str
    items: list[SkillItem] = Field(default_factory=list)


class Skills(StrictModel):
    groups: list[SkillGroup] = Field(default_factory=list)


class ProjectLinks(StrictModel):
    live: str | None = None
    demo: str | None = None
    paper: str | None = None
    video: str | None = None


class ProjectItem(StrictModel):
    slug: str
    title: str
    tagline: str | None = None
    status: ProjectStatus = ProjectStatus.BUILDING
    repo: str | None = None
    featured: bool = False
    categories: list[str] = Field(default_factory=list)
    stack: list[str] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)
    results: list[str] = Field(default_factory=list)
    links: ProjectLinks = Field(default_factory=ProjectLinks)
    diagram: str | None = None


class ExperienceItem(StrictModel):
    org: str
    role: str
    start: str | None = None
    end: str | None = None
    bullets: list[str] = Field(default_factory=list)
    stack: list[str] = Field(default_factory=list)


class PublicationItem(StrictModel):
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    venue: str | None = None
    year: int | str | None = None
    status: str | None = None
    doi: str | None = None
    pdf: str | None = None
    bibtex: str | None = None


class Patent(StrictModel):
    mention: bool = False
    text: str | None = None


class CertificationItem(StrictModel):
    title: str
    issuer: str
    kind: CertificationKind
    url: str | None = None


class OpenSource(StrictModel):
    interests: list[str] = Field(default_factory=list)
    want_to_contribute_to: list[str] = Field(default_factory=list)
    open_to_collaborate_on: list[str] = Field(default_factory=list)


class Leetcode(StrictModel):
    solved: int | None = None
    rating: float | int | None = None
    as_of: str | None = None


class Features(StrictModel):
    terminal_header: bool = True
    mermaid_skill_map: bool = True
    languages_chart: bool = True
    recent_activity: bool = True
    projects_last_updated: bool = True
    snake: bool = False
    stats_card: bool = False
    leetcode_block: bool = False
    blog_rss: bool = False
    wakatime: bool = False


class Profile(StrictModel):
    identity: Identity
    links: Links = Field(default_factory=Links)
    now: NowBlock = Field(default_factory=NowBlock)
    goals: Goals = Field(default_factory=Goals)
    principles: list[PrincipleItem] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    projects: list[ProjectItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    publications: list[PublicationItem] = Field(default_factory=list)
    patent: Patent = Field(default_factory=Patent)
    certifications: list[CertificationItem] = Field(default_factory=list)
    open_source: OpenSource = Field(default_factory=OpenSource)
    leetcode: Leetcode = Field(default_factory=Leetcode)
    wakatime: str | None = None
    features: Features = Field(default_factory=Features)


def validate_profile_dict(data: dict[str, Any]) -> Profile:
    """Validate raw profile dictionary and return a validated Profile instance."""
    try:
        return Profile.model_validate(data)
    except ValidationError as e:
        raise ProfileValidationError(format_validation_error(e)) from e
