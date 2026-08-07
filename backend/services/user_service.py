from sqlalchemy.orm import Session

from models.user import User
from schemas.user_schema import UserCreate, UserLogin

from security import (
    hash_password,
    verify_password,
    create_access_token
)


def register_user(
    db: Session,
    user: UserCreate
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        return None

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(
    db: Session,
    user: UserLogin
):
    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not db_user:
        return None

    if not verify_password(
        user.password,
        db_user.password
    ):
        return None

    token = create_access_token(
        {
            "sub": db_user.email,
            "user_id": db_user.id
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


def login_user_with_credentials(
    db: Session,
    email: str,
    password: str
):
    db_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not db_user:
        return None

    if not verify_password(
        password,
        db_user.password
    ):
        return None

    token = create_access_token(
        {
            "sub": db_user.email,
            "user_id": db_user.id
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }