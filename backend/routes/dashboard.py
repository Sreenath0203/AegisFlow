from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services import dashboard_service
from schemas.dashboard_schema import DashboardStats

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard_stats(db)