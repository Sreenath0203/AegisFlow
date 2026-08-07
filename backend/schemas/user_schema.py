from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Sreenath",
                "email": "sreenath@example.com",
                "password": "Sreenath@123"
            }
        }
    }


class UserLogin(BaseModel):
    email: EmailStr

    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "sreenath@example.com",
                "password": "Sreenath@123"
            }
        }
    }


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    access_token: str
    token_type: str