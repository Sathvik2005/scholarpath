from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel


class ProfileIn(BaseModel):
    full_name: Optional[str] = None
    course: str
    year_level: int
    marks_band: str
    income_bracket: Literal["under_2.5L", "2.5L_5L", "above_5L"]
    category: Optional[str] = None
    gender: Optional[str] = None
    disability_status: Optional[bool] = None
    minority_status: Optional[bool] = None
    state: str
    area_type: Literal["rural", "urban"]
    institution_type: Literal["government", "private", "aided"]
    documents_available: List[str] = []


class ProfileOut(ProfileIn):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScholarshipOut(BaseModel):
    id: str
    name: str
    provider: str
    provider_type: str
    eligibility_criteria_text: str
    required_documents: List[str]
    deadline: datetime
    amount: str
    source_url: Optional[str] = None

    class Config:
        from_attributes = True


class DimensionResult(BaseModel):
    dimension: Literal[
        "ACADEMIC", "FINANCIAL", "DEMOGRAPHIC", "GEOGRAPHIC", "DOCUMENTATION", "DEADLINE"
    ]
    verdict: Literal["ELIGIBLE", "PARTIAL", "NOT_ELIGIBLE", "UNSURE"]
    evidence: str
    reason: str
    missing_requirement: Optional[str] = None


class MatchOut(BaseModel):
    id: str
    scholarship: ScholarshipOut
    dimension_results: List[DimensionResult]
    overall_verdict: str
    days_until_deadline: int

    class Config:
        from_attributes = True
