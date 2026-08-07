from sqlalchemy.orm import Session

from backend.models.recommendation import Recommendation
from backend.schemas.recommendation_schema import RecommendationCreate


def get_all_recommendations(db: Session):
    return db.query(Recommendation).all()


def get_recommendation(
    db: Session,
    recommendation_id: int
):
    return (
        db.query(Recommendation)
        .filter(
            Recommendation.recommendation_id == recommendation_id
        )
        .first()
    )


def get_supplier_recommendations(
    db: Session,
    supplier_id: int
):
    return (
        db.query(Recommendation)
        .filter(
            Recommendation.supplier_id == supplier_id
        )
        .all()
    )


def create_recommendation(
    db: Session,
    recommendation: RecommendationCreate
):
    new_recommendation = Recommendation(
        supplier_id=recommendation.supplier_id,
        recommendation=recommendation.recommendation,
        reason=recommendation.reason,
        priority=recommendation.priority
    )

    db.add(new_recommendation)
    db.commit()
    db.refresh(new_recommendation)

    return new_recommendation


def delete_recommendation(
    db: Session,
    recommendation_id: int
):
    recommendation = (
        db.query(Recommendation)
        .filter(
            Recommendation.recommendation_id == recommendation_id
        )
        .first()
    )

    if not recommendation:
        return False

    db.delete(recommendation)
    db.commit()

    return True