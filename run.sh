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
        echo "Теперь можете использовать 'python main.py' напрямую"
        echo "Для выхода из окружения наберите 'exit'"
        echo "--------------------------------------------"
        source .venv/bin/activate && bash
        ;;
    "deps")
        echo "Установка зависимостей..."
        poetry install
        ;;
    "check")
        echo "Проверка виртуального окружения..."
        source .venv/bin/activate && python -c "
import sys
print(f'Python: {sys.version}')
print(f'Виртуальное окружение: {sys.prefix}')
try:
    import pydantic, psycopg2
    print('✅ Все зависимости доступны')
except ImportError as e:
    print(f'❌ Ошибка: {e}')
" && deactivate
        ;;
    *)
        echo "Использование: ./run.sh [команда]"
        echo "Команды:"
        echo "  app      - запуск приложения (по умолчанию)"
        echo "  test     - запуск всех тестов (подробно)"
        echo "  test-short - запуск тестов (кратко)"
        echo "  shell    - активация окружения (интерактивно)"
        echo "  check    - проверка окружения (быстро)"
        echo "  deps     - установка зависимостей"
        ;;
esac