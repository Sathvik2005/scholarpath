from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(String, primary_key=True)
    full_name = Column(String, nullable=True)
    course = Column(String)
    year_level = Column(Integer)
    marks_band = Column(String)          # e.g. "60-75%"
    income_bracket = Column(String)      # e.g. "under_2.5L", "2.5L_5L", "above_5L"
    category = Column(String, nullable=True)          # General/OBC/SC/ST etc, optional
    gender = Column(String, nullable=True)
    disability_status = Column(Boolean, nullable=True)
    minority_status = Column(Boolean, nullable=True)
    state = Column(String)
    area_type = Column(String)           # rural / urban
    institution_type = Column(String)    # government / private / aided
    documents_available = Column(JSON, default=list)   # list[str]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Scholarship(Base):
    __tablename__ = "scholarships"

    id = Column(String, primary_key=True)
    name = Column(String)
    provider = Column(String)
    provider_type = Column(String)       # government / state / private / institutional
    eligibility_criteria_text = Column(Text)
    structured_criteria = Column(JSON, default=dict)   # hard-filter fields
    required_documents = Column(JSON, default=list)
    deadline = Column(DateTime)
    amount = Column(String)
    source_url = Column(String, nullable=True)


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("student_profiles.id"))
    scholarship_id = Column(String, ForeignKey("scholarships.id"))
    dimension_results = Column(JSON)     # list of dimension result dicts
    overall_verdict = Column(String)     # ELIGIBLE / PARTIAL / NOT_ELIGIBLE / UNSURE
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scholarship = relationship("Scholarship")


class Document(Base):
    """A single uploaded document, run through the classify -> extract ->
    validate pipeline (see services/document_pipeline_service.py)."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("student_profiles.id"))

    declared_type = Column(String)         # what the student says it is
    file_name = Column(String)
    mime_type = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)  # extracted text, if any (OCR stub for images)

    classification = Column(JSON)          # {predicted_type, confidence, alternatives, reasoning}
    extracted_fields = Column(JSON)        # {field: {value, confidence}}
    validation_findings = Column(JSON)     # list of {field, severity, message}
    status = Column(String)                # UPLOADED / VERIFIED / NEEDS_REVIEW / REJECTED

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
