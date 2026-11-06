from fastapi import APIRouter, HTTPException, status
from typing import List
from models.products import Product, StockReserve

product_router = APIRouter(tags=["Контекст 1: Каталог и склад"])

products_db: List[Product] = []


# 1. Просмотр каталога товаров
@product_router.get("/", response_model=List[Product])
async def get_catalog() -> List[Product]:
    return products_db


# 2. Просмотр одного товара по ID
@product_router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int) -> Product:
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Товар с указанным артикулом не найден"
    )


# 3. Добавление нового товара
@product_router.post("/new", status_code=status.HTTP_201_CREATED)
async def add_product(new_product: Product) -> dict:
    for product in products_db:
        if product.id == new_product.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Товар с таким ID уже существует в каталоге"
            )
    products_db.append(new_product)
    return {"message": "Товар успешно добавлен в каталог (Буриков А.С.)"}


# 4. Резервирование остатков со склада
@product_router.post("/reserve")
async def reserve_stock(reserve: StockReserve) -> dict:
    for product in products_db:
        if product.id == reserve.product_id:
            if product.stock_quantity < reserve.quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Недостаточно товара на складе. Доступно: {product.stock_quantity}"
                )
            product.stock_quantity -= reserve.quantity
            return {
                "message": "Остаток успешно зарезервирован",
                "remaining_stock": product.stock_quantity
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Товар для резервирования не найден"
    )


# 5. ✏️ Редактирование товара менеджером (ИСПРАВЛЕНИЕ / UPDATE)
@product_router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, updated_data: Product) -> Product:
    for index, product in enumerate(products_db):
        if product.id == product_id:
            products_db[index] = updated_data
            return updated_data
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Товар для обновления не найден"
    )