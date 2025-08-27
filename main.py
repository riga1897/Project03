#!/usr/bin/env python3
"""
Приложение для поиска вакансий с консольным интерфейсом
"""

from src.user_interface import main
from src.storage.db_manager import DBManager
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    db_manager = None  # Инициализируем db_manager как None
    # Проверяем подключение к базе данных и инициализируем её
    try:
        logger.info("Инициализация базы данных...")
        db_manager = DBManager()

        # Проверяем подключение к БД
        if not db_manager.check_connection():
            logger.error("Не удается подключиться к базе данных")
            print("⚠️ Работа без базы данных - некоторые функции будут недоступны")
            db_manager = None
        else:
            # Создаем таблицы если их нет
            logger.info("Создание таблиц в базе данных...")
            db_manager.create_tables()
            logger.info("✓ Таблицы созданы/проверены")

            # Заполняем таблицу компаний целевыми компаниями  
            logger.info("Заполнение таблицы companies...")
            db_manager.populate_companies_table()
            logger.info("✓ Таблица companies заполнена")

    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        print(f"❌ Критическая ошибка базы данных: {e}")
        print("Программа не может работать без базы данных. Завершение работы.")
        exit(1)

    # Проверяем, что база данных инициализирована
    if db_manager is None:
        print("❌ База данных недоступна. Программа не может работать без базы данных.")
        exit(1)

    # Запускаем пользовательский интерфейс
    try:
        # Импортируем ConsoleInterface здесь, чтобы избежать ошибок при отсутствии БД
        from src.ui_interfaces.console_interface import UserInterface as ConsoleInterface 
        interface = ConsoleInterface(db_manager=db_manager)
        interface.run()
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
        print("\nПриложение остановлено.")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"Критическая ошибка: {e}")