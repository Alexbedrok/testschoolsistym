.PHONY: help install run build docker-build docker-run docker-stop clean test

help:
	@echo "Доступные команды:"
	@echo "  make install      - Установить зависимости"
	@echo "  make run          - Запустить приложение в режиме разработки"
	@echo "  make build        - Собрать Docker образ"
	@echo "  make docker-run   - Запустить приложение в Docker контейнере"
	@echo "  make docker-stop  - Остановить Docker контейнер"
	@echo "  make clean        - Очистить временные файлы"
	@echo "  make test         - Запустить тесты (если есть)"

install:
	pip install -r requirements.txt

run:
	python app.py

build:
	docker build -t flaskmanpage:latest .

docker-run:
	docker run -d -p 5000:5000 --name flaskmanpage-app flaskmanpage:latest

docker-stop:
	docker stop flaskmanpage-app || true
	docker rm flaskmanpage-app || true

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete

test:
	@echo "Тесты пока не настроены"

