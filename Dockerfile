FROM python:3.11-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Создаем директорию для данных
RUN mkdir -p /app/data

# Устанавливаем переменные окружения
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Открываем порт
EXPOSE 5000

# Команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]

