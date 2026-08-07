from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db

from schemas.user_schema import (
    UserCreate,
    UserResponse,
    Token
)

from services import user_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    new_user = user_service.register_user(
        db,
        user
    )

    if not new_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return new_user


@router.post(
    "/login",
    response_model=Token
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    token = user_service.login_user_with_credentials(
        db,
        form_data.username,
        form_data.password
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return token