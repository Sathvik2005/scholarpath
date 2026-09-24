import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import StudentProfile
from app.schemas.schemas import ProfileIn, ProfileOut

router = APIRouter(prefix="/profile", tags=["profile"])

# Demo mode: single-profile-per-session simplification (no auth wired up yet).
DEMO_PROFILE_ID = "demo_student_1"


@router.put("/me", response_model=ProfileOut)
def upsert_profile(payload: ProfileIn, db: Session = Depends(get_db)):
    profile = db.get(StudentProfile, DEMO_PROFILE_ID)
    if profile is None:
        profile = StudentProfile(id=DEMO_PROFILE_ID)
        db.add(profile)

    for field, value in payload.model_dump().items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/me", response_model=ProfileOut | None)
def get_profile(db: Session = Depends(get_db)):
    return db.get(StudentProfile, DEMO_PROFILE_ID)
