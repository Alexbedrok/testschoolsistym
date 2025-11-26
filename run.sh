#!/bin/bash

# Скрипт для запуска приложения в продакшене

echo "Запуск Flask приложения..."

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt

# Запуск приложения
echo "Запуск приложения на http://127.0.0.1:5000"
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

