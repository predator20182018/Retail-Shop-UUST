# Базовый легковесный образ Python на базе Debian Linux
FROM python:3.12-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Отключаем буферизацию логов Python для мгновенного вывода в консоль Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Сначала копируем и устанавливаем зависимости (кэширование слоев Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код проекта внутрь контейнера
COPY . .

# Открываем сетевой порт 8080
EXPOSE 8080

# Команда запуска ASGI-сервера Uvicorn при старте контейнера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
