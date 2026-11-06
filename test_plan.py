import requests
import sys

BASE = "http://127.0.0.1:8080"

# Проверка доступности сервера перед стартом
try:
    requests.get(f"{BASE}/docs", timeout=1.5)
except Exception:
    print("\n" + "="*80)
    print("❌ ОШИБКА: Сервер не отвечает на http://127.0.0.1:8080!")
    print("👉 Сначала запустите сервер в соседнем окне терминала: python main.py")
    print("="*80 + "\n")
    sys.exit(1)

results = []

def test(tc_id, desc, code, expected, extra=True, note=""):
    passed = (code == expected) and extra
    res_str = "PASS" if passed else "FAIL"
    print(f" {tc_id:<6} │ {desc:<42} │ {code:<5} │ {expected:<8} │ {res_str:<6} │ {note}")
    results.append(passed)

print("\n" + "="*95)
print("   АВТОМАТИЗИРОВАННЫЙ ТЕСТ-ПЛАН API РОЗНИЧНОЙ ФИРМЫ — БУРИКОВ А.С. (ВАРИАНТ 2.2)")
print("="*95)
print(f" {'ID':<6} │ {'Назначение проверки':<42} │ {'Код':<5} │ {'Ожидался':<8} │ {'Статус':<6} │ Детали")
print("─"*95)

# --- КОНТЕКСТ 3: КЛИЕНТЫ ---
r = requests.post(f"{BASE}/users/signup", json={"email": "burikov@uust.ru", "password": "123", "full_name": "Буриков Алексей", "phone": "+79170000000"})
test("TC-01", "Регистрация нового покупателя", r.status_code, 201)

r = requests.post(f"{BASE}/users/signup", json={"email": "burikov@uust.ru", "password": "123", "full_name": "Буриков Алексей", "phone": "+79170000000"})
test("TC-02", "Блокировка дубликата email", r.status_code, 409)

r = requests.post(f"{BASE}/users/signin", json={"email": "burikov@uust.ru", "password": "wrong"})
test("TC-03", "Отказ при неверном пароле", r.status_code, 403)

r = requests.post(f"{BASE}/users/signin", json={"email": "burikov@uust.ru", "password": "123"})
test("TC-04", "Успешная авторизация (сверка SHA-256)", r.status_code, 200)

# --- КОНТЕКСТ 1: КАТАЛОГ И СКЛАД ---
r = requests.post(f"{BASE}/products/new", json={"id": 1, "title": "iPhone 16 Pro", "category": "Смартфоны", "price": 100000.0, "stock_quantity": 10})
test("TC-05", "Добавление товара на склад (10 шт.)", r.status_code, 201)

r = requests.post(f"{BASE}/products/new", json={"id": 1, "title": "Клон", "category": "Смартфоны", "price": 50.0, "stock_quantity": 5})
test("TC-06", "Блокировка дубликата ID товара", r.status_code, 409)

# ✏️ ТЕСТ РЕДАКТИРОВАНИЯ ТОВАРА МЕНЕДЖЕРОМ (PUT)
r = requests.put(f"{BASE}/products/1", json={"id": 1, "title": "iPhone 16 Pro Max", "category": "Смартфоны", "price": 120000.0, "stock_quantity": 10, "is_active": True})
test("TC-07", "Редактирование товара менеджером (PUT)", r.status_code, 200, note="Цена: 120,000 ₽")

# --- КОНТЕКСТ 2: ЗАКАЗЫ И МЕЖКОНТЕКСТНОЕ ВЗАИМОДЕЙСТВИЕ ---
r = requests.post(f"{BASE}/orders/new", json={"id": 101, "customer_email": "burikov@uust.ru", "product_id": 1, "quantity": 2, "delivery_address": "г. Уфа"})
test("TC-08", "Создание заказа со списанием склада (2 шт)", r.status_code, 201, note="Сумма: 240,000 ₽")

r = requests.post(f"{BASE}/orders/new", json={"id": 101, "customer_email": "burikov@uust.ru", "product_id": 1, "quantity": 2, "delivery_address": "г. Уфа"})
test("TC-09", "Защита от дублирования номера заказа", r.status_code, 409)

r = requests.get(f"{BASE}/products/1")
stock = r.json().get("stock_quantity")
test("TC-10", "Верификация списания со склада", r.status_code, 200, stock == 8, f"Остаток: {stock} шт. (было 10)")

r = requests.post(f"{BASE}/orders/new", json={"id": 102, "customer_email": "burikov@uust.ru", "product_id": 1, "quantity": 50, "delivery_address": "г. Уфа"})
test("TC-11", "Блокировка заказа при нехватке на складе", r.status_code, 409, note="Запрос 50 шт. при остатке 8")

r = requests.patch(f"{BASE}/orders/101/status?new_status=PAID")
test("TC-12", "Смена жизненного цикла заказа на PAID", r.status_code, 200)

print("─"*95)
passed_count = sum(results)
print(f"ИТОГОВЫЙ РЕЗУЛЬТАТ: Успешно пройдено {passed_count} из {len(results)} тестов ({passed_count/len(results)*100:.0f}% Pass)")
print("="*95 + "\n")
