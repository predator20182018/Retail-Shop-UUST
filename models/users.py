from pydantic import BaseModel, EmailStr


# Модель для входящего запроса регистрации
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


# Модель, которая хранится в БД
class CustomerInDB(BaseModel):
    email: EmailStr
    password_hash: str
    full_name: str
    phone: str


# Модель для входа
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