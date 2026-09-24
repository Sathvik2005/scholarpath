"""
ScholarPath Document Verification Pipeline.

Adapted from the LogikIntake classify -> extract -> validate -> decide
pattern, applied here to student-uploaded scholarship documents instead of
mortgage packages.

    UPLOAD
       |
    CLASSIFICATION   "What document is this?"
       |
    EXTRACTION       "What information is inside it?"
       |
    VALIDATION       "Is it correct, complete, and consistent with the
       |               student's declared profile?"
       v
    DECISION          VERIFIED / NEEDS_REVIEW / REJECTED

This is a deterministic, keyword/regex-based reference implementation, so
the whole pipeline runs with no external OCR/AI dependency. To upgrade to
real OCR + AI classification (as in LogikIntake, e.g. Tesseract + Gemini):
replace `classify_document()` and `extract_fields()` below with real calls,
keeping the same input/output contract -- `validate_document()` and the
decision logic do not need to change.
"""

import re
from difflib import SequenceMatcher
from typing import Optional

from app.models.models import StudentProfile

# ---------------------------------------------------------------------------
# Document type schemas -- what fields we expect to find in each type,
# and the keywords used for (stub) classification.
# ---------------------------------------------------------------------------

DOCUMENT_SCHEMAS = {
    "income_certificate": {
        "keywords": ["income certificate", "annual income", "income of rs", "tehsildar"],
        "fields": ["name", "annual_income", "issue_date"],
    },
    "OBC_certificate": {
        "keywords": ["obc certificate", "other backward class", "caste certificate"],
        "fields": ["name", "category", "certificate_number"],
    },
    "SC_certificate": {
        "keywords": ["sc certificate", "scheduled caste", "caste certificate"],
        "fields": ["name", "category", "certificate_number"],
    },
    "aadhaar": {
        "keywords": ["aadhaar", "unique identification authority", "uidai"],
        "fields": ["name", "aadhaar_last4"],
    },
    "bonafide_certificate": {
        "keywords": ["bonafide certificate", "bona fide", "is a student of"],
        "fields": ["name", "institution"],
    },
    "bank_passbook": {
        "keywords": ["passbook", "account number", "ifsc"],
        "fields": ["name", "account_last4"],
    },
    "admission_letter": {
        "keywords": ["admission letter", "offer of admission", "admitted to"],
        "fields": ["name", "institution", "course"],
    },
}

INCOME_BRACKET_CEILINGS = {
    "under_2.5L": 250_000,
    "2.5L_5L": 500_000,
    "above_5L": float("inf"),
}


# ---------------------------------------------------------------------------
# Stage 0-1: Pre-processing / text acquisition happens in the API layer
# (reading the uploaded file and extracting text if possible). This module
# picks up from there with `raw_text`, which may be empty for image files
# with no OCR wired up yet -- handled explicitly as a NEEDS_REVIEW case.
# ---------------------------------------------------------------------------


def classify_document(declared_type: str, raw_text: str) -> dict:
    """Stage 1 -- Classification: 'what document is this?'

    Scores every known document type by keyword presence in the extracted
    text and returns the top prediction plus alternatives, mirroring the
    LogikIntake AI-classification + confidence + alternatives contract.
    """
    text_lower = (raw_text or "").lower()

    if not text_lower.strip():
        return {
            "predicted_type": declared_type,
            "confidence": 0.3,
            "alternatives": {},
            "reasoning": "No embedded text could be read from this file (likely a scanned image). "
                         "Classification falls back to the student's declared type with low confidence. "
                         "A production build would run OCR here before classification.",
        }

    scores = {}
    for doc_type, schema in DOCUMENT_SCHEMAS.items():
        hits = sum(1 for kw in schema["keywords"] if kw in text_lower)
        if hits:
            scores[doc_type] = min(0.55 + hits * 0.15, 0.97)

    if not scores:
        return {
            "predicted_type": declared_type,
            "confidence": 0.4,
            "alternatives": {},
            "reasoning": "Text was found but did not match any known document keywords. "
                         "Falling back to the student's declared type.",
        }

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    predicted_type, confidence = ranked[0]
    alternatives = dict(ranked[1:4])

    # Keyword-boost guardrail (from LogikIntake): if the student's declared
    # type scored reasonably and is within a small confidence gap of the
    # top prediction, keep the declared type rather than override it.
    declared_score = scores.get(declared_type)
    if declared_type != predicted_type and declared_score is not None:
        gap = confidence - declared_score
        if gap <= 0.15:
            predicted_type, confidence = declared_type, declared_score
            alternatives = {k: v for k, v in ranked if k != declared_type}

    return {
        "predicted_type": predicted_type,
        "confidence": round(confidence, 2),
        "alternatives": {k: round(v, 2) for k, v in alternatives.items()},
        "reasoning": f"Matched keywords associated with '{predicted_type}' in the document text.",
    }


def _find(pattern: str, text: str) -> Optional[str]:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def extract_fields(predicted_type: str, raw_text: str) -> dict:
    """Stage 2 -- Extraction: 'what information is inside it?'

    Field-level extraction with a confidence per field, matching the
    LogikIntake field record shape (value + confidence). Uses simple
    regexes against common certificate phrasing; a production build would
    replace this with schema-driven AI/OCR extraction.
    """
    text = raw_text or ""
    fields: dict[str, dict] = {}

    def add(name: str, value: Optional[str], high_confidence: bool = True):
        if value:
            fields[name] = {"value": value, "confidence": 0.9 if high_confidence else 0.6}
        else:
            fields[name] = {"value": None, "confidence": 0.0}

    if not text.strip():
        # No text available (unread image) -- every field is unknown.
        for f in DOCUMENT_SCHEMAS.get(predicted_type, {}).get("fields", []):
            add(f, None)
        return fields

    name_val = _find(r"name[:\-]\s*([A-Za-z .]+)", text)

    if predicted_type == "income_certificate":
        add("name", name_val)
        income_val = _find(r"(?:income|rs\.?|rupees)[:\-\s]*([\d,]{4,})", text)
        add("annual_income", income_val.replace(",", "") if income_val else None)
        add("issue_date", _find(r"(?:issued on|date)[:\-\s]*([\d/\-]{6,10})", text), high_confidence=False)

    elif predicted_type in ("OBC_certificate", "SC_certificate"):
        add("name", name_val)
        cat_val = _find(r"category[:\-\s]*([A-Za-z/ ]+)", text)
        add("category", cat_val.strip() if cat_val else ("OBC" if predicted_type == "OBC_certificate" else "SC"))
        add("certificate_number", _find(r"certificate no\.?[:\-\s]*([A-Za-z0-9\-/]+)", text), high_confidence=False)

    elif predicted_type == "aadhaar":
        add("name", name_val)
        aad = _find(r"(\d{4}\s?\d{4}\s?\d{4})", text)
        add("aadhaar_last4", aad[-4:] if aad else None)

    elif predicted_type == "bonafide_certificate":
        add("name", name_val)
        add("institution", _find(r"(?:college|institute|university)[:\-\s]*([A-Za-z0-9 .,]+)", text), high_confidence=False)

    elif predicted_type == "bank_passbook":
        add("name", name_val)
        acct = _find(r"account (?:no\.?|number)[:\-\s]*(\d{6,})", text)
        add("account_last4", acct[-4:] if acct else None)

    elif predicted_type == "admission_letter":
        add("name", name_val)
        add("institution", _find(r"(?:college|institute|university)[:\-\s]*([A-Za-z0-9 .,]+)", text), high_confidence=False)
        add("course", _find(r"course[:\-\s]*([A-Za-z0-9 .]+)", text), high_confidence=False)

    else:
        add("name", name_val)

    return fields


def _names_match(profile_name: Optional[str], extracted_name: Optional[str]) -> bool:
    if not profile_name or not extracted_name:
        return True  # can't compare -- not a mismatch, just unverified (handled via confidence)
    ratio = SequenceMatcher(None, profile_name.lower().strip(), extracted_name.lower().strip()).ratio()
    return ratio >= 0.72


CATEGORY_ALIASES = {
    "OBC": ["obc", "other backward class", "other backward classes"],
    "SC": ["sc", "scheduled caste", "scheduled castes"],
    "ST": ["st", "scheduled tribe", "scheduled tribes"],
}


def _normalize_category(value: str) -> Optional[str]:
    v = re.sub(r"[^a-z ]", " ", value.lower())
    v = " ".join(v.split())
    for canonical, aliases in CATEGORY_ALIASES.items():
        if v in aliases:
            return canonical
    return None


def validate_document(student: StudentProfile, predicted_type: str, fields: dict) -> list[dict]:
    """Stage 3 -- Validation: 'is this correct, complete, and consistent?'

    Returns a list of findings, each tagged HARD_STOP or ADVISORY, following
    the LogikIntake severity model.
    """
    findings = []

    def field_value(name):
        return (fields.get(name) or {}).get("value")

    extracted_name = field_value("name")
    if not student.full_name:
        findings.append({
            "field": "name",
            "severity": "ADVISORY",
            "message": "No name on your profile to compare against -- add your full name so this document can be verified.",
        })
    elif extracted_name and not _names_match(student.full_name, extracted_name):
        findings.append({
            "field": "name",
            "severity": "HARD_STOP",
            "message": f"Name on document ('{extracted_name}') does not match the name on file ('{student.full_name}').",
        })
    elif not extracted_name:
        findings.append({
            "field": "name",
            "severity": "ADVISORY",
            "message": "Could not confirm the name on this document -- please ensure it's legible.",
        })

    if predicted_type == "income_certificate":
        income_str = field_value("annual_income")
        if income_str:
            try:
                income_val = float(income_str)
                ceiling = INCOME_BRACKET_CEILINGS.get(student.income_bracket, float("inf"))
                # allow the bracket *below* too -- a lower income than declared bracket is fine
                if income_val > ceiling:
                    findings.append({
                        "field": "annual_income",
                        "severity": "HARD_STOP",
                        "message": f"Document shows income of ₹{int(income_val):,}, which exceeds the "
                                   f"declared bracket ({student.income_bracket.replace('_', '-')}).",
                    })
            except ValueError:
                findings.append({
                    "field": "annual_income",
                    "severity": "ADVISORY",
                    "message": "Could not read a clear income figure from this document.",
                })
        else:
            findings.append({
                "field": "annual_income",
                "severity": "ADVISORY",
                "message": "Could not locate an income figure on this document.",
            })

    if predicted_type in ("OBC_certificate", "SC_certificate"):
        cat_val = field_value("category")
        expected = "OBC" if predicted_type == "OBC_certificate" else "SC"
        if cat_val and _normalize_category(cat_val) != expected:
            findings.append({
                "field": "category",
                "severity": "HARD_STOP",
                "message": f"Certificate category ('{cat_val}') does not match a {expected} certificate.",
            })
        if not student.category or student.category.strip().upper() != expected:
            findings.append({
                "field": "category",
                "severity": "HARD_STOP",
                "message": f"This is a {expected} certificate, but the student's declared category is '{student.category or 'not declared'}'.",
            })

    low_confidence_fields = [f for f, v in fields.items() if v.get("value") is None]
    if low_confidence_fields:
        findings.append({
            "field": ", ".join(low_confidence_fields),
            "severity": "ADVISORY",
            "message": f"Could not extract: {', '.join(low_confidence_fields)}. Manual review recommended.",
        })

    return findings


def decide_status(classification: dict, findings: list[dict]) -> str:
    """Stage 4 -- Decision: roll classification confidence + findings into a
    single status, following the LogikIntake hard-stop / advisory model."""
    if any(f["severity"] == "HARD_STOP" for f in findings):
        return "REJECTED"
    if classification["confidence"] < 0.5 or any(f["severity"] == "ADVISORY" for f in findings):
        return "NEEDS_REVIEW"
    return "VERIFIED"


def run_pipeline(student: StudentProfile, declared_type: str, raw_text: str) -> dict:
    """Runs the full classify -> extract -> validate -> decide pipeline for
    one uploaded document and returns everything needed to persist it."""
    classification = classify_document(declared_type, raw_text)
    fields = extract_fields(classification["predicted_type"], raw_text)
    findings = validate_document(student, classification["predicted_type"], fields)
    if classification["predicted_type"] != declared_type:
        # Documents are counted by their declared type, so a mismatch must
        # never be allowed to verify (e.g. an income certificate uploaded as aadhaar).
        findings.append({
            "field": "document_type",
            "severity": "HARD_STOP",
            "message": f"This looks like a '{classification['predicted_type']}', not the declared '{declared_type}'.",
        })
    status = decide_status(classification, findings)

    return {
        "classification": classification,
        "extracted_fields": fields,
        "validation_findings": findings,
        "status": status,
    }
