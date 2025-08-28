#!/usr/bin/env python3
"""
Модуль для запуска пользовательского интерфейса
"""

import logging

from src.config.app_config import AppConfig
from src.storage.storage_factory import StorageFactory
from src.ui_interfaces.console_interface import UserInterface

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Основная функция для запуска пользовательского интерфейса
    """
    try:
        logger.info("Запуск приложения поиска вакансий")
        
        # Инициализация и проверка базы данных
        from src.storage.db_manager import DBManager
        
        logger.info("Инициализация базы данных...")
        db_manager = DBManager()

        # Проверяем подключение к БД
        logger.info("Проверка подключения к базе данных...")
        if not db_manager.check_connection():
            raise Exception("Не удается подключиться к базе данных")

        # Инициализируем базу данных (создание таблиц + заполнение компаний)
        logger.info("Инициализация структуры базы данных...")
        db_manager.create_tables()
        db_manager.populate_companies_table()
        
        # Проверка корректности инициализации
        test_companies = db_manager.get_companies_and_vacancies_count()
        logger.info(f"✓ База данных инициализирована корректно. Найдено {len(test_companies)} компаний")

        # Инициализируем конфигурацию приложения
        app_config = AppConfig()

        # Создаем хранилище согласно конфигурации
        storage = StorageFactory.create_storage(app_config.default_storage_type)
        logger.info(f"Используется хранилище: {type(storage).__name__}")

        # Создаем пользовательский интерфейс с правильным хранилищем и db_manager
        from src.ui_interfaces.console_interface import UserInterface as ConsoleInterface 
        user_interface = ConsoleInterface(storage, db_manager=db_manager)

        # Запускаем основной цикл интерфейса
        user_interface.run()

    except KeyboardInterrupt:
        print("\n\nРабота прервана пользователем. До свидания!")
        logger.info("Приложение завершено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Критическая ошибка: {e}")
        if "базы данных" in str(e).lower() or "database" in str(e).lower():
            print("Программа не может работать без базы данных. Завершение работы.")
        else:
            print("Обратитесь к разработчику для решения проблемы.")
        return


if __name__ == "__main__":
    main()