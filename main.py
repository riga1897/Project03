#!/usr/bin/env python3
"""
Главная точка входа приложения для поиска вакансий
"""

import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения из .env
from src.utils.env_loader import EnvLoader
EnvLoader.load_env_file()

if __name__ == "__main__":
    from src.user_interface import main
    main()