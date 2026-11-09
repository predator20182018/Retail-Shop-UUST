from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
from sqlmodel import Session, select
import uvicorn

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from database.connection import init_db, engine
from models.products import Product
from models.orders import Order
from models.users import CustomerInDB
from routes.products import product_router
from routes.orders import order_router
from routes.users import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="REST API Розничной торговой фирмы (Вариант 2.2 — SQLite DB)",
    description="Индивидуальный проект с подключением СУБД SQLite. Выполнил: ст. гр. ИВТ-ИВСС-401Б Буриков А.С.",
    lifespan=lifespan
)

templates = Jinja2Templates(directory="templates")


@app.get("/shop", tags=["Веб-интерфейс (Jinja2)"])
async def shop_ui(request: Request):
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        orders = session.exec(select(Order)).all()
        customers = session.exec(select(CustomerInDB)).all()
    return templates.TemplateResponse(
        request=request,
        name="shop.html",
        context={
            "products": products,
            "orders": orders,
            "customers": customers
        }
    )

app.include_router(product_router, prefix="/products")
app.include_router(order_router, prefix="/orders")
app.include_router(user_router, prefix="/users")


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


# 🛠 Красивая панель администратора базы данных SQLite
@app.get("/admin", response_class=HTMLResponse, tags=["Администрирование"])
async def admin_dashboard():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        orders = session.exec(select(Order)).all()
        customers = session.exec(select(CustomerInDB)).all()

    # 1. Генерация строк таблицы товаров
    product_rows = "".join([
        f"""<tr>
            <td><span class="badge bg-dark fs-6">{p.id}</span></td>
            <td><b>{p.title}</b></td>
            <td><span class="badge bg-info text-dark">{p.category}</span></td>
            <td><span class="text-success fw-bold">{p.price:,.2f} ₽</span></td>
            <td><span class="badge bg-primary fs-6">{p.stock_quantity} шт.</span></td>
        </tr>"""
        for p in products
    ]) or "<tr><td colspan='5' class='text-center text-muted p-4'>В таблице product пока нет записей</td></tr>"

    # 2. Генерация строк таблицы заказов с цветными статусами
    order_rows = ""
    for o in orders:
        status_badge = "bg-success" if o.status == "PAID" else "bg-warning text-dark"
        order_rows += f"""<tr>
            <td><b>#{o.id}</b></td>
            <td>{o.customer_email}</td>
            <td>{o.product_title} <small class="text-muted">(ID: {o.product_id})</small></td>
            <td><b>{o.quantity} шт.</b></td>
            <td><span class="text-success fw-bold">{o.total_amount:,.2f} ₽</span></td>
            <td><span class="badge {status_badge}">{o.status}</span></td>
            <td><small class="text-secondary">{o.delivery_address}</small></td>
        </tr>"""
    if not order_rows:
        order_rows = "<tr><td colspan='7' class='text-center text-muted p-4'>В таблице order пока нет записей</td></tr>"

    # 3. Генерация строк таблицы клиентов
    customer_rows = "".join([
        f"""<tr>
            <td><span class="badge bg-dark fs-6">{c.id}</span></td>
            <td><b>{c.email}</b></td>
            <td>{c.full_name}</td>
            <td>{c.phone}</td>
            <td><code class="text-danger fw-bold">{c.password_hash[:20]}...</code></td>
        </tr>"""
        for c in customers
    ]) or "<tr><td colspan='5' class='text-center text-muted p-4'>В таблице customerindb пока нет записей</td></tr>"

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Панель управления СУБД SQLite — Буриков А.С.</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="bg-light p-4">
        <div class="container">
            <!-- Шапка панели -->
            <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
                <div>
                    <h2 class="mb-0">🗄 Панель управления СУБД SQLite</h2>
                    <small class="text-muted">
                        Файл базы: <b>retail_shop.db</b> | 
                        Разработчик: <b>ст. гр. ИВТ-ИВСС-401Б Буриков А.С.</b>
                    </small>
                </div>
                <div>
                    <button onclick="location.reload()" class="btn btn-outline-secondary me-2">🔄 Обновить данные</button>
                    <a href="/docs" class="btn btn-primary">📖 Swagger UI</a>
                </div>
            </div>

            <!-- Блок 1: Товары -->
            <div class="card shadow-sm mb-4 border-0">
                <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center py-2">
                    <span class="fs-6">📦 Таблица: <code>product</code> (Каталог и склад)</span>
                    <span class="badge bg-info text-dark">Записей: {len(products)}</span>
                </div>
                <div class="table-responsive">
                    <table class="table table-striped table-hover mb-0 align-middle">
                        <thead class="table-secondary">
                            <tr><th>ID</th><th>Наименование товара</th><th>Категория</th><th>Цена</th><th>Остаток на складе</th></tr>
                        </thead>
                        <tbody>{product_rows}</tbody>
                    </table>
                </div>
            </div>

            <!-- Блок 2: Заказы -->
            <div class="card shadow-sm mb-4 border-0">
                <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center py-2">
                    <span class="fs-6">🛒 Таблица: <code>order</code> (Оформленные заказы)</span>
                    <span class="badge bg-warning text-dark">Заказов: {len(orders)}</span>
                </div>
                <div class="table-responsive">
                    <table class="table table-striped table-hover mb-0 align-middle">
                        <thead class="table-secondary">
                            <tr><th>ID</th><th>Email клиента</th><th>Товар</th><th>Кол-во</th><th>Итоговая сумма</th><th>Статус</th><th>Адрес доставки</th></tr>
                        </thead>
                        <tbody>{order_rows}</tbody>
                    </table>
                </div>
            </div>

            <!-- Блок 3: Клиенты -->
            <div class="card shadow-sm border-0">
                <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center py-2">
                    <span class="fs-6">👤 Таблица: <code>customerindb</code> (Учетные записи)</span>
                    <span class="badge bg-success">Клиентов: {len(customers)}</span>
                </div>
                <div class="table-responsive">
                    <table class="table table-striped table-hover mb-0 align-middle">
                        <thead class="table-secondary">
                            <tr><th>ID</th><th>Email</th><th>ФИО покупателя</th><th>Телефон</th><th>Криптографический хэш (SHA-256)</th></tr>
                        </thead>
                        <tbody>{customer_rows}</tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)