#!/bin/bash

# Скрипт для сборки Docker образа

echo "Сборка Docker образа для Flask приложения..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "Ошибка: Docker не установлен. Установите Docker для продолжения."
    exit 1
fi

# Сборка образа
docker build -t flaskmanpage:latest .

if [ $? -eq 0 ]; then
    echo "✓ Образ успешно собран: flaskmanpage:latest"
    echo ""
    echo "Для запуска используйте:"
    echo "  docker run -d -p 5000:5000 --name flaskmanpage-app flaskmanpage:latest"
    echo ""
    echo "Или используйте Makefile:"
    echo "  make docker-run"
else
    echo "✗ Ошибка при сборке образа"
    exit 1
fi

