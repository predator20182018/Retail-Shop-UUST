from fastapi import APIRouter, HTTPException, status
from typing import List
from models.orders import Order, OrderCreate
from routes.products import products_db

order_router = APIRouter(tags=["Контекст 2: Заказы и корзина"])

orders_db: List[Order] = []


# UC-2.2: Оформление заказа розничным покупателем (с вызовом резерва склада UC-1.5)
@order_router.post("/new", status_code=status.HTTP_201_CREATED, response_model=Order)
async def create_order(order_req: OrderCreate) -> Order:
    # 0. Проверка уникальности ID заказа (защита от дубликатов)
    for existing_order in orders_db:
        if existing_order.id == order_req.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Заказ с номером {order_req.id} уже существует (Буриков А.С.)"
            )

    # 1. Ищем товар в каталоге
    target_product = None
    for product in products_db:
        if product.id == order_req.product_id:
            target_product = product
            break

    if not target_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запрашиваемый товар не существует в каталоге"
        )

    # 2. Проверяем и списываем складской остаток (UC-1.5)
    if target_product.stock_quantity < order_req.quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Отказ в резервировании: на складе осталось {target_product.stock_quantity} шт."
        )

    target_product.stock_quantity -= order_req.quantity

    # 3. Фиксируем цену на момент покупки (price_at_purchase) и создаем заказ
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
    orders_db.append(new_order)
    return new_order


# UC-2.5: Отслеживание списка и статуса заказов
@order_router.get("/", response_model=List[Order])
async def get_all_orders() -> List[Order]:
    return orders_db


# UC-2.6: Изменение статуса заказа менеджером
@order_router.patch("/{order_id}/status")
async def update_order_status(order_id: int, new_status: str) -> dict:
    for order in orders_db:
        if order.id == order_id:
            order.status = new_status
            return {"message": f"Статус заказа №{order_id} изменен на {new_status}"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Заказ с указанным номером не найден"
    )