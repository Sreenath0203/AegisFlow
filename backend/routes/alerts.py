from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.security import get_current_user
from backend.models.user import User

from backend.schemas.alert_schema import (
    AlertCreate,
    AlertUpdate,
    AlertResponse
)

from backend.services import alert_service


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@router.get("/", response_model=list[AlertResponse])
def get_all_alerts(
    db: Session = Depends(get_db)
):
    return alert_service.get_all_alerts(db)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = alert_service.get_alert(
        db,
        alert_id
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return alert


@router.post("/", response_model=AlertResponse)
def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return alert_service.create_alert(
        db,
        alert
    )


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    updated = alert_service.update_alert(
        db,
        alert_id,
        alert
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return updated


@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    deleted = alert_service.delete_alert(
        db,
        alert_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return {
        "success": True,
        "message": "Alert deleted successfully"
    }