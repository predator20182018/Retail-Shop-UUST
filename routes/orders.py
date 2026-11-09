from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from database.connection import get_session
from models.orders import Order, OrderCreate
from models.products import Product

order_router = APIRouter(tags=["Контекст 2: Заказы и корзина"])


# 1. Оформление заказа с атомарным списанием склада в одной SQL-транзакции
@order_router.post("/new", status_code=status.HTTP_201_CREATED, response_model=Order)
async def create_order(
    order_req: OrderCreate,
    session: Session = Depends(get_session)
) -> Order:
    # Проверка уникальности номера заказа
    if session.get(Order, order_req.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Заказ с номером {order_req.id} уже существует в БД (Буриков А.С.)"
        )

    # Поиск товара в таблице Product
    target_product = session.get(Product, order_req.product_id)
    if not target_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запрашиваемый товар не существует в каталоге"
        )

    # Проверка и списание остатка
    if target_product.stock_quantity < order_req.quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Отказ в резервировании: на складе осталось {target_product.stock_quantity} шт."
        )

    target_product.stock_quantity -= order_req.quantity
    session.add(target_product)

    # Запись заказа в таблицу Order
    new_order = Order(
        id=order_req.id,
        customer_email=order_req.customer_email,
        product_id=target_product.id,
        product_title=target_product.title,
        price_at_purchase=target_product.price,
        quantity=order_req.quantity,
        total_amount=target_product.price * order_req.quantity,
        status="CREATED",
        delivery_address=order_req.delivery_address
    )
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    return new_order


# 2. Получение всех заказов из БД
@order_router.get("/", response_model=List[Order])
async def get_all_orders(session: Session = Depends(get_session)) -> List[Order]:
    return session.exec(select(Order)).all()


# 3. Изменение статуса заказа в БД
@order_router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: str,
    session: Session = Depends(get_session)
) -> dict:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ с указанным номером не найден"
        )
    order.status = new_status
    session.add(order)
    session.commit()
    return {"message": f"Статус заказа №{order_id} в БД изменен на {new_status}"}