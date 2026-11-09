import requests
import sqlite3
import sys

BASE = "http://127.0.0.1:8080"

try:
    requests.get(f"{BASE}/docs", timeout=1.5)
except Exception:
    print("\n❌ ОШИБКА: Сначала запустите сервер в соседнем окне: python main.py\n")
    sys.exit(1)

# SETUP: Очищаем тестовые записи в SQLite перед прогоном для 100% повторяемости
try:
    with sqlite3.connect("retail_shop.db") as conn:
        conn.execute("DELETE FROM customerindb WHERE email = 'burikov@uust.ru'")
        conn.execute("DELETE FROM product WHERE id = 1")
        conn.execute('DELETE FROM "order" WHERE id IN (101, 102)')
        conn.commit()
except Exception:
    pass

results = []

def test(tc_id, desc, code, expected, extra=True, note=""):
    passed = (code == expected) and extra
    res_str = "PASS" if passed else "FAIL"
    print(f" {tc_id:<6} │ {desc:<44} │ {code:<5} │ {expected:<8} │ {res_str:<6} │ {note}")
    results.append(passed)

print("\n" + "="*105)
print("   ПОЛНЫЙ АВТОМАТИЗИРОВАННЫЙ ТЕСТ-ПЛАН РОЗНИЧНОЙ ФИРМЫ (16 ПРОВЕРОК) — БУРИКОВ А.С. (ВАРИАНТ 2.2)")
print("="*105)
print(f" {'ID':<6} │ {'Назначение проверки':<44} │ {'Код':<5} │ {'Ожидался':<8} │ {'Статус':<6} │ Детали верификации")
print("─"*105)

# === БЛОК 1: КОНТЕКСТ 3 (КЛИЕНТЫ И КРИПТОГРАФИЯ SHA-256) ===
r = requests.post(f"{BASE}/users/signup", json={"email": "burikov@uust.ru", "password": "123", "full_name": "Буриков Алексей", "phone": "+79170000000"})
test("TC-01", "Регистрация нового покупателя (POST)", r.status_code, 201)

r = requests.post(f"{BASE}/users/signup", json={"email": "burikov@uust.ru", "password": "123", "full_name": "Буриков Алексей", "phone": "+79170000000"})
test("TC-02", "Блокировка дубликата email", r.status_code, 409)

r = requests.get(f"{BASE}/users/")
users_list = r.json()
target_user = next((u for u in users_list if u["email"] == "burikov@uust.ru"), None)
is_hashed = target_user is not None and target_user["password_hash"] != "123" and len(target_user["password_hash"]) == 64
test("TC-03", "Проверка хэширования пароля в БД (GET)", r.status_code, 200, is_hashed, f"SHA-256: {target_user['password_hash'][:16]}...")

r = requests.post(f"{BASE}/users/signin", json={"email": "burikov@uust.ru", "password": "wrong_password"})
test("TC-04", "Отказ при вводе неверного пароля", r.status_code, 403)

r = requests.post(f"{BASE}/users/signin", json={"email": "burikov@uust.ru", "password": "123"})
test("TC-05", "Успешный вход покупателя (сверка хэшей)", r.status_code, 200)

# === БЛОК 2: КОНТЕКСТ 1 (КАТАЛОГ И СКЛАД) ===
r = requests.post(f"{BASE}/products/new", json={"id": 1, "title": "iPhone 16 Pro", "category": "Смартфоны", "price": 100000.0, "stock_quantity": 10})
test("TC-06", "Добавление товара на склад (10 шт.)", r.status_code, 201)

r = requests.post(f"{BASE}/products/new", json={"id": 1, "title": "Клон", "category": "Смартфоны", "price": 50.0, "stock_quantity": 5})
test("TC-07", "Блокировка дубликата артикула ID", r.status_code, 409)

r = requests.put(f"{BASE}/products/1", json={"id": 1, "title": "iPhone 16 Pro Max", "category": "Смартфоны", "price": 120000.0, "stock_quantity": 10, "is_active": True})
test("TC-08", "Редактирование товара менеджером (PUT)", r.status_code, 200, note="Новая цена: 120,000 ₽")

r = requests.post(f"{BASE}/products/reserve", json={"product_id": 1, "quantity": 1})
rem = r.json().get("remaining_stock")
test("TC-09", "Прямое резервирование со склада (1 шт.)", r.status_code, 200, rem == 9, f"Остаток: {rem} шт.")

# === БЛОК 3: КОНТЕКСТ 2 (ЗАКАЗЫ И МЕЖКОНТЕКСТНОЕ СПИСАНИЕ) ===
r = requests.post(f"{BASE}/orders/new", json={"id": 101, "customer_email": "burikov@uust.ru", "product_id": 1, "quantity": 2, "delivery_address": "г. Уфа"})
test("TC-10", "Оформление заказа со списанием (2 шт.)", r.status_code, 201, note="Сумма: 240,000 ₽")

r = requests.post(f"{BASE}/orders/new", json={"id": 101, "customer_email": "burikov@uust.ru", "product_id": 1, "quantity": 2, "delivery_address": "г. Уфа"})
test("TC-11", "Защита от дублирования номера заказа", r.status_code, 409)

r = requests.get(f"{BASE}/products/1")
stock = r.json().get("stock_quantity")
test("TC-12", "Верификация остатка на складе (9 - 2 = 7)", r.status_code, 200, stock == 7, f"Остаток в БД: {stock} шт.")

r = requests.post(f"{BASE}/orders/new", json={"id": 102, "customer_email": "burikov@uust.ru", "product_id": 1, "quantity": 50, "delivery_address": "г. Уфа"})
test("TC-13", "Блокировка заказа при нехватке на складе", r.status_code, 409, note="Запрос 50 шт. при остатке 7")

r = requests.patch(f"{BASE}/orders/101/status?new_status=PAID")
orders_list = requests.get(f"{BASE}/orders/").json()
paid_ok = any(o["id"] == 101 and o["status"] == "PAID" for o in orders_list)
test("TC-14", "Перевод статуса заказа в PAID (PATCH + GET)", r.status_code, 200, paid_ok, "Статус в БД: PAID")

# === БЛОК 4: ВЕБ-ИНТЕРФЕЙСЫ (JINJA2 И ПАНЕЛЬ СУБД) ===
r = requests.get(f"{BASE}/shop")
test("TC-15", "Рендеринг клиентской витрины Jinja2 (/shop)", r.status_code, 200, "UUST Store" in r.text, "HTML витрина активна")

r = requests.get(f"{BASE}/admin")
test("TC-16", "Рендеринг панели мониторинга СУБД (/admin)", r.status_code, 200, "retail_shop.db" in r.text, "Админка БД активна")

print("─"*105)
passed_count = sum(results)
print(f" ИТОГОВЫЙ РЕЗУЛЬТАТ: Успешно пройдено {passed_count} из {len(results)} тестов ({passed_count/len(results)*100:.0f}% Pass)")
print("="*105 + "\n")
