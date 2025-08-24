#!/usr/bin/env python3
"""
Приложение для поиска вакансий с консольным интерфейсом
"""

from src.user_interface import main
from src.storage.db_manager import DBManager
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Инициализируем DBManager и создаем необходимые таблицы
        db_manager = DBManager()
        db_manager.create_tables()
        db_manager.populate_companies_table()
        
        main()
    except Exception as e:
        logger.error(f"Ошибка при инициализации приложения: {e}")
        print(f"Ошибка при запуске: {e}")
        main()  # Запускаем приложение даже при ошибке инициализации БД