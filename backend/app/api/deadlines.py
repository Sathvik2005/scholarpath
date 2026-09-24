from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import StudentProfile, Match
from app.api.profile import DEMO_PROFILE_ID

router = APIRouter(prefix="/deadlines", tags=["deadlines"])


@router.get("")
def list_deadlines(db: Session = Depends(get_db)):
    student = db.get(StudentProfile, DEMO_PROFILE_ID)
    if student is None:
        return []

    matches = (
        db.query(Match)
        .filter(Match.student_id == student.id, Match.overall_verdict.in_(["ELIGIBLE", "PARTIAL"]))
        .all()
    )

    items = []
    for m in matches:
        s = m.scholarship
        days_left = (s.deadline - datetime.utcnow()).days
        if days_left < 0:
            continue
        items.append(
            {
                "scholarship_id": s.id,
                "name": s.name,
                "deadline": s.deadline,
                "days_until_deadline": days_left,
                "overall_verdict": m.overall_verdict,
                "urgent": days_left <= 14,
            }
        )

    items.sort(key=lambda x: x["days_until_deadline"])
    return items
