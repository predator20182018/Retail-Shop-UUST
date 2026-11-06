import hashlib
from fastapi import APIRouter, HTTPException, status
from typing import Dict
from models.users import CustomerRegister, CustomerInDB, CustomerSignIn

user_router = APIRouter(tags=["Контекст 3: Клиенты и авторизация"])

# Хранилище пользователей (содержит только объекты CustomerInDB с хэшами)
customers_db: Dict[str, CustomerInDB] = {}


def hash_password(password: str) -> str:
    """Преобразует открытый пароль в криптографический хэш SHA-256"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# UC-3.1: Регистрация нового розничного покупателя
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_customer(data: CustomerRegister) -> dict:
    if data.email in customers_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Покупатель с данным email уже зарегистрирован (Буриков А.С.)"
        )

    # Хэшируем пароль перед сохранением в базу
    hashed_pwd = hash_password(data.password)

    customer_record = CustomerInDB(
        email=data.email,
        password_hash=hashed_pwd,
        full_name=data.full_name,
        phone=data.phone
    )
    customers_db[data.email] = customer_record
    return {
        "message": f"Покупатель {data.full_name} успешно зарегистрирован!",
        "password_hash_preview": hashed_pwd[:16] + "..."
    }


# UC-3.2: Авторизация в системе (сверка хэшей)
@user_router.post("/signin")
async def login_customer(data: CustomerSignIn) -> dict:
    if data.email not in customers_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учетная запись с таким email не найдена"
        )

    # Хэшируем введенный пароль и сравниваем с хэшем в БД
    if customers_db[data.email].password_hash != hash_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный пароль"
        )
    return {"message": "Авторизация прошла успешно (Буриков А.С.)"}