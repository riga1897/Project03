#!/usr/bin/env python3
"""
Приложение для поиска вакансий с консольным интерфейсом
"""

from src.user_interface import main
from src.storage.db_manager import DBManager
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Проверяем подключение к базе данных и инициализируем её
    try:
        logger.info("Инициализация базы данных...")
        db_manager = DBManager()

        # Проверяем подключение к БД
        logger.info("Проверка подключения к базе данных...")
        if not db_manager.check_connection():
            raise Exception("Не удается подключиться к базе данных")

        # Создаем таблицы если их нет
        logger.info("Создание/проверка таблиц в базе данных...")
        db_manager.create_tables()
        logger.info("✓ Таблицы созданы/проверены")

        # Заполняем таблицу компаний целевыми компаниями  
        logger.info("Заполнение таблицы companies...")
        db_manager.populate_companies_table()
        logger.info("✓ Таблица companies заполнена")
        
        # Дополнительная проверка корректности инициализации
        logger.info("Проверка корректности инициализации...")
        test_companies = db_manager.get_companies_and_vacancies_count()
        logger.info(f"✓ База данных инициализирована корректно. Найдено {len(test_companies)} компаний")

    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        print(f"❌ Критическая ошибка базы данных: {e}")
        print("Программа не может работать без базы данных. Завершение работы.")
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