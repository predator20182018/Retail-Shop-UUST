from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from database.connection import get_session
from models.products import Product, StockReserve

product_router = APIRouter(tags=["Контекст 1: Каталог и склад"])


# 1. Просмотр каталога товаров из SQLite
@product_router.get("/", response_model=List[Product])
async def get_catalog(session: Session = Depends(get_session)) -> List[Product]:
    return session.exec(select(Product)).all()


# 2. Просмотр одного товара по ID
@product_router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, session: Session = Depends(get_session)) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар с указанным артикулом не найден"
        )
    return product


# 3. Добавление нового товара в БД
@product_router.post("/new", status_code=status.HTTP_201_CREATED)
async def add_product(new_product: Product, session: Session = Depends(get_session)) -> dict:
    existing = session.get(Product, new_product.id) if new_product.id else None
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Товар с таким ID уже существует в базе данных"
        )
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return {"message": "Товар успешно сохранен в БД (Буриков А.С.)", "id": new_product.id}


# 4. Резервирование остатков со склада в БД
@product_router.post("/reserve")
async def reserve_stock(reserve: StockReserve, session: Session = Depends(get_session)) -> dict:
    product = session.get(Product, reserve.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар для резервирования не найден"
        )
    if product.stock_quantity < reserve.quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Недостаточно товара на складе. Доступно: {product.stock_quantity}"
        )
    product.stock_quantity -= reserve.quantity
    session.add(product)
    session.commit()
    session.refresh(product)
    return {
        "message": "Остаток успешно зарезервирован в БД",
        "remaining_stock": product.stock_quantity
    }


# 5. Редактирование товара менеджером (PUT)
@product_router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    updated_data: Product,
    session: Session = Depends(get_session)
) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар для обновления не найден"
        )
    product.title = updated_data.title
    product.category = updated_data.category
    product.description = updated_data.description
    product.price = updated_data.price
    product.stock_quantity = updated_data.stock_quantity
    product.is_active = updated_data.is_active

    session.add(product)
    session.commit()
    session.refresh(product)
    return product