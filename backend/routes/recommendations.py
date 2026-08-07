from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from security import get_current_user
from models.user import User

from schemas.recommendation_schema import (
    RecommendationCreate,
    RecommendationResponse
)

from services import recommendation_service


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get(
    "/",
    response_model=list[RecommendationResponse]
)
def get_all_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return recommendation_service.get_all_recommendations(db)



@router.get(
    "/{recommendation_id}",
    response_model=RecommendationResponse
)
def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    recommendation = recommendation_service.get_recommendation(
        db,
        recommendation_id
    )

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )

    return recommendation



@router.get(
    "/supplier/{supplier_id}",
    response_model=list[RecommendationResponse]
)
def get_supplier_recommendations(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return recommendation_service.get_supplier_recommendations(
        db,
        supplier_id
    )



@router.post(
    "/",
    response_model=RecommendationResponse
)
def create_recommendation(
    recommendation: RecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return recommendation_service.create_recommendation(
        db,
        recommendation
    )



@router.delete("/{recommendation_id}")
def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    deleted = recommendation_service.delete_recommendation(
        db,
        recommendation_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )

    return {
        "success": True,
        "message": "Recommendation deleted successfully"
    }