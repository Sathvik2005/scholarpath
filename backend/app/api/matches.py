import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import StudentProfile, Scholarship, Match, Document
from app.schemas.schemas import MatchOut
from app.services.matching_service import run_match, hard_filter_candidates
from app.api.profile import DEMO_PROFILE_ID

router = APIRouter(prefix="/matches", tags=["matches"])


def _verified_types(db: Session, student_id: str) -> set[str]:
    rows = (
        db.query(Document.declared_type)
        .filter(Document.student_id == student_id, Document.status == "VERIFIED")
        .distinct()
        .all()
    )
    return {r[0] for r in rows}


def _serialize(match: Match, scholarship: Scholarship) -> dict:
    days_left = (scholarship.deadline - datetime.utcnow()).days
    return {
        "id": match.id,
        "scholarship": scholarship,
        "dimension_results": match.dimension_results,
        "overall_verdict": match.overall_verdict,
        "days_until_deadline": days_left,
    }


@router.post("/run", response_model=list[MatchOut])
def run_matches(db: Session = Depends(get_db)):
    student = db.get(StudentProfile, DEMO_PROFILE_ID)
    if student is None:
        raise HTTPException(status_code=400, detail="Complete your profile before running matches.")

    all_scholarships = db.query(Scholarship).all()
    candidates = hard_filter_candidates(student, all_scholarships)
    verified_types = _verified_types(db, student.id)

    # Drop stale rows (e.g. scholarships whose deadline has since passed).
    candidate_ids = {s.id for s in candidates}
    for old in db.query(Match).filter(Match.student_id == student.id).all():
        if old.scholarship_id not in candidate_ids:
            db.delete(old)

    results = []
    for scholarship in candidates:
        assessment = run_match(student, scholarship, verified_types)

        existing = (
            db.query(Match)
            .filter(Match.student_id == student.id, Match.scholarship_id == scholarship.id)
            .first()
        )
        if existing:
            existing.dimension_results = assessment["dimension_results"]
            existing.overall_verdict = assessment["overall_verdict"]
            match = existing
        else:
            match = Match(
                id=str(uuid.uuid4()),
                student_id=student.id,
                scholarship_id=scholarship.id,
                dimension_results=assessment["dimension_results"],
                overall_verdict=assessment["overall_verdict"],
            )
            db.add(match)

        results.append((match, scholarship))

    db.commit()

    verdict_order = {"ELIGIBLE": 0, "PARTIAL": 1, "UNSURE": 2, "NOT_ELIGIBLE": 3}
    results.sort(key=lambda pair: (verdict_order[pair[0].overall_verdict], pair[1].deadline))

    return [_serialize(m, s) for m, s in results]


@router.get("", response_model=list[MatchOut])
def list_matches(db: Session = Depends(get_db)):
    student = db.get(StudentProfile, DEMO_PROFILE_ID)
    if student is None:
        return []

    matches = db.query(Match).filter(Match.student_id == student.id).all()
    verdict_order = {"ELIGIBLE": 0, "PARTIAL": 1, "UNSURE": 2, "NOT_ELIGIBLE": 3}
    pairs = [(m, m.scholarship) for m in matches]
    pairs.sort(key=lambda pair: (verdict_order[pair[0].overall_verdict], pair[1].deadline))

    return [_serialize(m, s) for m, s in pairs]


@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id: str, db: Session = Depends(get_db)):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return _serialize(match, match.scholarship)
