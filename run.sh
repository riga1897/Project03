#!/bin/bash
# Удобные команды для запуска приложения

case "$1" in
    "app"|"")
        echo "Запуск приложения..."
        poetry run python main.py
        ;;
    "test")
        echo "Запуск тестов..."
        poetry run pytest -v
        ;;
    "test-short")
        echo "Запуск тестов (краткий вывод)..."
        poetry run pytest
        ;;
    "shell")
        echo "Активация виртуального окружения..."
        source .venv/bin/activate && bash
        ;;
    "deps")
        echo "Установка зависимостей..."
        poetry install
        ;;
    *)
        echo "Использование: ./run.sh [команда]"
        echo "Команды:"
        echo "  app      - запуск приложения (по умолчанию)"
        echo "  test     - запуск всех тестов (подробно)"
        echo "  test-short - запуск тестов (кратко)"
        echo "  shell    - активация окружения"
        echo "  deps     - установка зависимостей"
        ;;
esac