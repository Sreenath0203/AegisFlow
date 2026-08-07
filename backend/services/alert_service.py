from sqlalchemy.orm import Session

from models.alert import Alert
from schemas.alert_schema import AlertCreate, AlertUpdate



def get_all_alerts(db: Session):
    return db.query(Alert).all()



def get_alert(db: Session, alert_id: int):

    return (
        db.query(Alert)
        .filter(Alert.alert_id == alert_id)
        .first()
    )



def create_alert(
    db: Session,
    alert: AlertCreate
):

    new_alert = Alert(
        **alert.model_dump()
    )

    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return new_alert



def update_alert(
    db: Session,
    alert_id: int,
    alert: AlertUpdate
):

    db_alert = (
        db.query(Alert)
        .filter(Alert.alert_id == alert_id)
        .first()
    )

    if not db_alert:
        return None


    for key, value in alert.model_dump(exclude_unset=True).items():
        setattr(db_alert, key, value)


    db.commit()
    db.refresh(db_alert)

    return db_alert



def delete_alert(
    db: Session,
    alert_id: int
):

    db_alert = (
        db.query(Alert)
        .filter(Alert.alert_id == alert_id)
        .first()
    )

    if not db_alert:
        return None


    db.delete(db_alert)
    db.commit()

    return True