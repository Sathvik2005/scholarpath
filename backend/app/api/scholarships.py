from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Scholarship
from app.schemas.schemas import ScholarshipOut

router = APIRouter(prefix="/scholarships", tags=["scholarships"])


@router.get("", response_model=list[ScholarshipOut])
def list_scholarships(db: Session = Depends(get_db)):
    return db.query(Scholarship).order_by(Scholarship.deadline).all()


@router.get("/{scholarship_id}", response_model=ScholarshipOut)
def get_scholarship(scholarship_id: str, db: Session = Depends(get_db)):
    scholarship = db.get(Scholarship, scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return scholarship
