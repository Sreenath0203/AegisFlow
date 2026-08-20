from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database.db import get_db
from backend.models.models import ComplianceRecord
from backend.schemas.schemas import ComplianceOut

router = APIRouter(prefix="/compliance", tags=["Compliance Management"])

@router.get("", response_model=List[ComplianceOut])
@router.get("/", response_model=List[ComplianceOut])
def list_compliance_records(db: Session = Depends(get_db)):
    return db.query(ComplianceRecord).all()
