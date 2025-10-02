.PHONY: help install install-dev test lint type-check build clean release

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить пакет
	pip install -e .

install-dev: ## Установить пакет с зависимостями для разработки
	pip install -e ".[dev]"

test: ## Запустить тесты
	pytest

test-cov: ## Запустить тесты с покрытием
	pytest --cov=main --cov-report=html --cov-report=term

lint: ## Проверить код линтером
	flake8 main.py tests/

type-check: ## Проверить типы
	mypy main.py

check: lint type-check test ## Запустить все проверки

build: ## Собрать пакет
	python -m build

clean: ## Очистить временные файлы
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

release: ## Создать релиз (требует тег)
	@echo "Создание релиза для тега: $(shell git describe --tags --abbrev=0)"
	git push origin $(shell git describe --tags --abbrev=0)

demo: ## Продемонстрировать работу
	@echo "Создание демо-бэкапа..."
	python -m simple-backup create demo_backup.yml --verbose
	@echo "Предварительный просмотр восстановления..."
	python -m simple-backup restore demo_backup.yml demo_restore --preview
	@echo "Восстановление..."
	python -m simple-backup restore demo_backup.yml demo_restore --force
	@echo "Очистка..."
	rm -f demo_backup.yml
	rm -rf demo_restore
	@echo "Демо завершено!"

ci: ## Запустить CI локально
	$(MAKE) check
	$(MAKE) build
