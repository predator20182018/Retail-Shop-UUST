from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr
from typing import Optional


class OrderCreate(BaseModel):
    id: int
    customer_email: EmailStr
    product_id: int
    quantity: int
    delivery_address: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 101,
                "customer_email": "burikov@uust.ru",
                "product_id": 1,
                "quantity": 2,
                "delivery_address": "г. Уфа, ул. Карла Маркса, д. 12"
            }
        }


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_email: str
    product_id: int
    product_title: str
    price_at_purchase: float
    quantity: int
    total_amount: float
    status: str = "CREATED"
    delivery_address: str