#!/usr/bin/env python3
"""
Главная точка входа приложения для поиска вакансий

Для использования вне Replit:
1. Создайте файл .env в корневой папке проекта
2. Добавьте параметры подключения к PostgreSQL:

   Вариант 1 - отдельные параметры:
   PGHOST=localhost
   PGPORT=5432
   PGDATABASE=job_search_app
   PGUSER=postgres
   PGPASSWORD=your_password

   Вариант 2 - DATABASE_URL (приоритетнее):
   DATABASE_URL=postgresql://username:password@hostname:port/database

3. Настройте другие параметры при необходимости:
   SUPERJOB_API_KEY=your_api_key
   CACHE_TTL=3600
   LOG_LEVEL=INFO
"""

import os
import sys

from src.user_interface import main
from src.utils.env_loader import EnvLoader

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения из .env
EnvLoader.load_env_file()

if __name__ == "__main__":
    main()
