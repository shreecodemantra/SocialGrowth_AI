from pydantic import BaseModel


class ResearchBrief(BaseModel):
    summary: str
    key_points: list[str]
    suggested_angle: str


class QualityCheckResult(BaseModel):
    passed: bool
    violations: list[str] = []
