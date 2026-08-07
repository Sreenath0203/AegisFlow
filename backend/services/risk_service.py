from sqlalchemy.orm import Session

from models.risk import Risk
from schemas.risk_schema import RiskCreate, RiskUpdate


def get_all_risks(db: Session):
    return db.query(Risk).all()


def get_risk(db: Session, risk_id: int):
    return db.query(Risk).filter(Risk.risk_id == risk_id).first()


def create_risk(db: Session, risk: RiskCreate):
    new_risk = Risk(**risk.model_dump())

    db.add(new_risk)
    db.commit()
    db.refresh(new_risk)

    return new_risk


def update_risk(db: Session, risk_id: int, risk: RiskUpdate):
    db_risk = db.query(Risk).filter(Risk.risk_id == risk_id).first()

    if not db_risk:
        return None

    for key, value in risk.model_dump().items():
        setattr(db_risk, key, value)

    db.commit()
    db.refresh(db_risk)

    return db_risk


def delete_risk(db: Session, risk_id: int):
    db_risk = db.query(Risk).filter(Risk.risk_id == risk_id).first()

    if not db_risk:
        return None

    db.delete(db_risk)
    db.commit()

    return True