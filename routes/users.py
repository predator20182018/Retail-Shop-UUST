import hashlib
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database.connection import get_session
from models.users import CustomerRegister, CustomerInDB, CustomerSignIn

user_router = APIRouter(tags=["Контекст 3: Клиенты и авторизация"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# 0. Получение списка всех клиентов (GET /users/)
@user_router.get("/", response_model=List[CustomerInDB])
async def get_all_customers(session: Session = Depends(get_session)) -> List[CustomerInDB]:
    return session.exec(select(CustomerInDB)).all()


# 1. Регистрация покупателя в SQLite
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_customer(
    data: CustomerRegister,
    session: Session = Depends(get_session)
) -> dict:
    existing = session.exec(select(CustomerInDB).where(CustomerInDB.email == data.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Покупатель с данным email уже зарегистрирован в БД (Буриков А.С.)"
        )

    customer_record = CustomerInDB(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone
    )
    session.add(customer_record)
    session.commit()
    return {"message": f"Покупатель {data.full_name} успешно сохранен в БД!"}


# 2. Авторизация покупателя по данным из SQLite
@user_router.post("/signin")
async def login_customer(
    data: CustomerSignIn,
    session: Session = Depends(get_session)
) -> dict:
    customer = session.exec(select(CustomerInDB).where(CustomerInDB.email == data.email)).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учетная запись с таким email не найдена"
        )
    if customer.password_hash != hash_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный пароль"
        )
    return {"message": "Авторизация прошла успешно (Буриков А.С.)"}