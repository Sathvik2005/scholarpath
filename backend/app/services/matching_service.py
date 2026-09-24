"""
ScholarPath Matching Engine — reference implementation.

This module implements the exact verdict/evidence/reason contract defined in
03_AI_ENGINE_PROMPT.md as a deterministic rule-based engine, so the product
works end-to-end without requiring an LLM API key.

To upgrade to a real LLM-backed engine: replace `assess_dimension()` calls
below with a call to your LLM using 03_AI_ENGINE_PROMPT.md as the system
prompt, passing the same (student_profile, scholarship) pair, and validate
the response against the DimensionResult schema before storing it. The rest
of the pipeline (hard filter -> per-dimension assessment -> overall verdict ->
missing requirements -> deadline alerts) does not need to change.
"""

from datetime import datetime
from typing import Optional

from app.models.models import StudentProfile, Scholarship

INCOME_ORDER = {"under_2.5L": 0, "2.5L_5L": 1, "above_5L": 2}

VERDICT_RANK = {"NOT_ELIGIBLE": 0, "PARTIAL": 1, "UNSURE": 2, "ELIGIBLE": 3}


def _income_within_limit(student_bracket: str, max_bracket: Optional[str]) -> bool:
    if not max_bracket:
        return True
    return INCOME_ORDER[student_bracket] <= INCOME_ORDER[max_bracket]


def assess_academic(student: StudentProfile, criteria: dict) -> dict:
    allowed_courses = criteria.get("courses")
    min_year = criteria.get("min_year")

    if allowed_courses and student.course not in allowed_courses:
        return {
            "dimension": "ACADEMIC",
            "verdict": "NOT_ELIGIBLE",
            "evidence": criteria.get("academic_text", "Course restriction stated in eligibility criteria."),
            "reason": f"Scholarship is restricted to {', '.join(allowed_courses)}; student is enrolled in {student.course}.",
        }
    if min_year and student.year_level < min_year:
        return {
            "dimension": "ACADEMIC",
            "verdict": "NOT_ELIGIBLE",
            "evidence": criteria.get("academic_text", "Minimum year of study stated in eligibility criteria."),
            "reason": f"Requires year {min_year} or above; student is in year {student.year_level}.",
        }
    return {
        "dimension": "ACADEMIC",
        "verdict": "ELIGIBLE",
        "evidence": criteria.get("academic_text", "No restriction stated for this dimension."),
        "reason": "Student's course and year of study meet the stated academic criteria.",
    }


def assess_financial(student: StudentProfile, criteria: dict) -> dict:
    max_income = criteria.get("max_income_bracket")
    if _income_within_limit(student.income_bracket, max_income):
        return {
            "dimension": "FINANCIAL",
            "verdict": "ELIGIBLE",
            "evidence": criteria.get("financial_text", "No income restriction stated for this dimension."),
            "reason": "Student's declared income bracket falls within the stated limit.",
        }
    return {
        "dimension": "FINANCIAL",
        "verdict": "NOT_ELIGIBLE",
        "evidence": criteria.get("financial_text", "Income restriction stated in eligibility criteria."),
        "reason": "Student's declared income bracket exceeds the stated limit.",
    }


def assess_demographic(student: StudentProfile, criteria: dict) -> dict:
    allowed_categories = criteria.get("categories")
    required_genders = criteria.get("genders")
    evidence_text = criteria.get("demographic_text", "No restriction stated for this dimension.")

    if allowed_categories:
        if not student.category:
            return {
                "dimension": "DEMOGRAPHIC",
                "verdict": "UNSURE",
                "evidence": evidence_text,
                "reason": "Student did not declare a category; cannot confirm against this scholarship's category restriction.",
            }
        if student.category not in allowed_categories:
            return {
                "dimension": "DEMOGRAPHIC",
                "verdict": "NOT_ELIGIBLE",
                "evidence": evidence_text,
                "reason": f"Scholarship is restricted to {', '.join(allowed_categories)}; student's declared category ({student.category}) is not listed.",
            }

    if required_genders:
        if not student.gender:
            return {
                "dimension": "DEMOGRAPHIC",
                "verdict": "UNSURE",
                "evidence": evidence_text,
                "reason": "Student did not declare a gender; cannot confirm against this scholarship's restriction.",
            }
        if student.gender not in required_genders:
            return {
                "dimension": "DEMOGRAPHIC",
                "verdict": "NOT_ELIGIBLE",
                "evidence": evidence_text,
                "reason": f"Scholarship is restricted to {', '.join(required_genders)} students.",
            }

    if not allowed_categories and not required_genders:
        return {
            "dimension": "DEMOGRAPHIC",
            "verdict": "ELIGIBLE",
            "evidence": "No restriction stated for this dimension.",
            "reason": "This scholarship does not restrict eligibility by category or gender.",
        }

    return {
        "dimension": "DEMOGRAPHIC",
        "verdict": "ELIGIBLE",
        "evidence": evidence_text,
        "reason": "Student's declared demographic details meet the stated criteria.",
    }


def assess_geographic(student: StudentProfile, criteria: dict) -> dict:
    allowed_states = criteria.get("states")
    required_area_types = criteria.get("area_types")
    evidence_text = criteria.get("geographic_text", "No restriction stated for this dimension.")

    if allowed_states and student.state not in allowed_states:
        return {
            "dimension": "GEOGRAPHIC",
            "verdict": "NOT_ELIGIBLE",
            "evidence": evidence_text,
            "reason": f"Scholarship is restricted to residents of {', '.join(allowed_states)}; student resides in {student.state}.",
        }

    if required_area_types and student.area_type not in required_area_types:
        return {
            "dimension": "GEOGRAPHIC",
            "verdict": "NOT_ELIGIBLE",
            "evidence": evidence_text,
            "reason": f"Scholarship is restricted to {', '.join(required_area_types)} students; student is from a {student.area_type} area.",
        }

    if not allowed_states and not required_area_types:
        return {
            "dimension": "GEOGRAPHIC",
            "verdict": "ELIGIBLE",
            "evidence": "No restriction stated for this dimension.",
            "reason": "This scholarship has no state or area-type restriction.",
        }

    return {
        "dimension": "GEOGRAPHIC",
        "verdict": "ELIGIBLE",
        "evidence": evidence_text,
        "reason": "Student's location meets the stated geographic criteria.",
    }


def assess_documentation(student: StudentProfile, scholarship: Scholarship, verified_types: set[str]) -> dict:
    """`verified_types` are document types the student has actually uploaded
    and had pass the classify/extract/validate pipeline (status VERIFIED) --
    not just self-declared. See services/document_pipeline_service.py."""
    required = scholarship.required_documents or []
    missing = [doc for doc in required if doc not in verified_types]

    if not required:
        return {
            "dimension": "DOCUMENTATION",
            "verdict": "ELIGIBLE",
            "evidence": "No specific documents stated for this dimension.",
            "reason": "No additional documentation is required beyond standard application details.",
        }
    if not missing:
        return {
            "dimension": "DOCUMENTATION",
            "verdict": "ELIGIBLE",
            "evidence": f"Required documents: {', '.join(required)}.",
            "reason": "All required documents have been uploaded and passed verification.",
        }
    return {
        "dimension": "DOCUMENTATION",
        "verdict": "PARTIAL",
        "evidence": f"Required documents: {', '.join(required)}.",
        "reason": f"{len(missing)} required document(s) are missing or not yet verified.",
        "missing_requirement": ", ".join(missing),
    }


def assess_deadline(scholarship: Scholarship) -> dict:
    days_left = (scholarship.deadline - datetime.utcnow()).days
    if days_left < 0:
        return {
            "dimension": "DEADLINE",
            "verdict": "NOT_ELIGIBLE",
            "evidence": f"Deadline: {scholarship.deadline.date().isoformat()}.",
            "reason": "This scholarship's deadline has already passed.",
        }
    return {
        "dimension": "DEADLINE",
        "verdict": "ELIGIBLE",
        "evidence": f"Deadline: {scholarship.deadline.date().isoformat()}.",
        "reason": f"{days_left} day(s) remain until the deadline.",
    }


def compute_overall_verdict(dimension_results: list[dict]) -> str:
    ranks = [VERDICT_RANK[d["verdict"]] for d in dimension_results]
    worst = min(ranks)
    if worst == VERDICT_RANK["NOT_ELIGIBLE"]:
        return "NOT_ELIGIBLE"
    if worst == VERDICT_RANK["PARTIAL"]:
        return "PARTIAL"
    if worst == VERDICT_RANK["UNSURE"]:
        return "UNSURE"
    return "ELIGIBLE"


def run_match(student: StudentProfile, scholarship: Scholarship, verified_types: set[str]) -> dict:
    """Runs the full explainable eligibility assessment for one student/scholarship pair."""
    criteria = scholarship.structured_criteria or {}

    dimension_results = [
        assess_academic(student, criteria),
        assess_financial(student, criteria),
        assess_demographic(student, criteria),
        assess_geographic(student, criteria),
        assess_documentation(student, scholarship, verified_types),
        assess_deadline(scholarship),
    ]

    return {
        "dimension_results": dimension_results,
        "overall_verdict": compute_overall_verdict(dimension_results),
    }


def hard_filter_candidates(student: StudentProfile, scholarships: list[Scholarship]) -> list[Scholarship]:
    """Cheap pre-filter: at demo scale we only drop scholarships whose deadline has
    already passed. At production scale (hundreds of scholarships), this is also
    where you'd drop scholarships with a clear, unambiguous disqualifier (e.g. wrong
    state, course not offered) before running the more detailed per-dimension
    assessment on the remaining candidates -- see 02_BACKEND_PROMPT.md."""
    return [s for s in scholarships if s.deadline >= datetime.utcnow()]
