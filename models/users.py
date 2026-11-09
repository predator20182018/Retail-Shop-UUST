from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr
from typing import Optional


class CustomerRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "burikov@uust.ru",
                "password": "StrongPassword123!",
                "full_name": "Буриков Алексей Сергеевич",
                "phone": "+79170000000"
            }
        }


class CustomerInDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    full_name: str
    phone: str


class CustomerSignIn(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "burikov@uust.ru",
                "password": "StrongPassword123!"
            }
        }