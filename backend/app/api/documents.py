import uuid
import io

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import StudentProfile, Document
from app.api.profile import DEMO_PROFILE_ID
from app.services.document_pipeline_service import run_pipeline, DOCUMENT_SCHEMAS

router = APIRouter(prefix="/documents", tags=["documents"])


def _extract_raw_text(file_bytes: bytes, filename: str, mime_type: str) -> str:
    """Stage 0 (pre-processing): pull whatever text we can out of the file.
    Text files and text-layer PDFs work directly; image files (jpg/png) have
    no OCR wired up here and return empty text -- see the pipeline's explicit
    NEEDS_REVIEW handling for that case, and the module docstring for how to
    plug in real OCR."""
    lower = filename.lower()
    if lower.endswith(".txt") or (mime_type or "").startswith("text/"):
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return ""
    if lower.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception:
            return ""
    return ""  # images / unsupported types -- OCR stub, handled by the pipeline


@router.get("/schemas")
def get_schemas():
    """Lets the frontend know which document types exist and what fields
    each one carries, for building the upload UI."""
    return DOCUMENT_SCHEMAS


@router.post("/upload")
async def upload_document(
    declared_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    student = db.get(StudentProfile, DEMO_PROFILE_ID)
    if student is None:
        raise HTTPException(status_code=400, detail="Complete your profile before uploading documents.")
    if declared_type not in DOCUMENT_SCHEMAS:
        raise HTTPException(status_code=400, detail=f"Unknown document type '{declared_type}'.")

    file_bytes = await file.read()
    raw_text = _extract_raw_text(file_bytes, file.filename, file.content_type)

    result = run_pipeline(student, declared_type, raw_text)

    doc = Document(
        id=str(uuid.uuid4()),
        student_id=student.id,
        declared_type=declared_type,
        file_name=file.filename,
        mime_type=file.content_type,
        raw_text=raw_text[:5000],  # cap stored text
        classification=result["classification"],
        extracted_fields=result["extracted_fields"],
        validation_findings=result["validation_findings"],
        status=result["status"],
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return _serialize(doc)


def _serialize(doc: Document) -> dict:
    return {
        "id": doc.id,
        "declared_type": doc.declared_type,
        "file_name": doc.file_name,
        "classification": doc.classification,
        "extracted_fields": doc.extracted_fields,
        "validation_findings": doc.validation_findings,
        "status": doc.status,
        "created_at": doc.created_at,
    }


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    student = db.get(StudentProfile, DEMO_PROFILE_ID)
    if student is None:
        return []
    docs = db.query(Document).filter(Document.student_id == student.id).order_by(Document.created_at.desc()).all()
    return [_serialize(d) for d in docs]


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.student_id != DEMO_PROFILE_ID:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"deleted": True}
