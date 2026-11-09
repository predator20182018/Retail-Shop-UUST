from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Optional


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    category: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Смартфон iPhone 16 Pro 256GB",
                "category": "Смартфоны",
                "description": "Флагманский смартфон в титановом корпусе",
                "price": 119990.0,
                "stock_quantity": 10,
                "is_active": True
            }
        }


class StockReserve(BaseModel):
    product_id: int
    quantity: int