from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

from routes.products import product_router, products_db
from routes.orders import order_router, orders_db
from routes.users import user_router, customers_db

app = FastAPI(
    title="REST API Розничной торговой фирмы (Вариант 2.2)",
    description="Лабораторная работа №2: Проектирование структуры на основе микросервисов. Выполнил: ст. гр. ИВТ-ИВСС-401Б Буриков А.С."
)

# Подключение роутеров трех контекстов
app.include_router(product_router, prefix="/products")
app.include_router(order_router, prefix="/orders")
app.include_router(user_router, prefix="/users")


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


# Простая и надежная админка
@app.get("/admin", response_class=HTMLResponse, tags=["Администрирование"])
async def admin_dashboard():
    p_rows = "".join([f"<tr><td>{p.id}</td><td>{p.title}</td><td>{p.price} ₽</td><td>{p.stock_quantity} шт.</td></tr>" for p in products_db]) or "<tr><td colspan='4'>Пусто</td></tr>"
    o_rows = "".join([f"<tr><td>#{o.id}</td><td>{o.customer_email}</td><td>{o.product_title}</td><td>{o.total_amount} ₽</td><td>{o.status}</td></tr>" for o in orders_db]) or "<tr><td colspan='5'>Пусто</td></tr>"
    c_rows = "".join([f"<tr><td>{c.email}</td><td>{c.full_name}</td><td>{c.phone}</td></tr>" for c in customers_db.values()]) or "<tr><td colspan='3'>Пусто</td></tr>"

    return f"""
    <html><head><title>Admin</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"></head>
    <body class="p-4 container">
        <h2>🛠 Панель данных (Буриков А.С.)</h2>
        <a href="/docs" class="btn btn-primary mb-3">В Swagger UI</a>
        <h4>Товары на складе</h4><table class="table table-bordered mb-4"><tr><th>ID</th><th>Товар</th><th>Цена</th><th>Остаток</th></tr>{p_rows}</table>
        <h4>Заказы</h4><table class="table table-bordered mb-4"><tr><th>ID</th><th>Клиент</th><th>Товар</th><th>Сумма</th><th>Статус</th></tr>{o_rows}</table>
        <h4>Клиенты</h4><table class="table table-bordered"><tr><th>Email</th><th>ФИО</th><th>Телефон</th></tr>{c_rows}</table>
    </body></html>
    """


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)