from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class Candidate:
    source_file: str
    name: str
    email: str | None
    github_url: str | None
    text: str
    skills: list[str]
    projects: list[str]
    eligible: bool = False
    rejection_reasons: list[str] | None = None
    matched_skills: list[str] | None = None
    score_breakdown: dict[str, int] | None = None
    total_score: int = 0
    project_summary: str = ""
    github_summary: str = ""
    strengths: list[str] | None = None
    concerns: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("text", None)
        return d
