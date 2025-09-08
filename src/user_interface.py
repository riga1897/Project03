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

        # Создаем базу данных если она не существует
        logger.info("Проверка и создание базы данных...")
        try:
            db_manager._ensure_database_exists()
        except Exception as db_create_error:
            logger.error(f"Ошибка при создании базы данных: {db_create_error}")
            raise Exception(f"Не удалось создать базу данных: {db_create_error}")

        # Проверяем подключение к БД
        logger.info("Проверка подключения к базе данных...")
        if not db_manager.check_connection():
            raise Exception("Не удается подключиться к базе данных")

        # Инициализируем базу данных (создание таблиц + заполнение компаний)
        logger.info("Инициализация структуры базы данных...")
        try:
            db_manager.create_tables()
            db_manager.populate_companies_table()
        except Exception as init_error:
            logger.error(f"Ошибка при инициализации структуры БД: {init_error}")
            raise Exception(f"Не удалось инициализировать структуру базы данных: {init_error}")

        # Проверка корректности инициализации
        try:
            test_companies = db_manager.get_companies_and_vacancies_count()
            logger.info(f"База данных инициализирована корректно. Найдено {len(test_companies)} компаний")
        except Exception as db_error:
            logger.error(f"Ошибка при проверке инициализации БД: {db_error}")
            raise Exception(f"База данных не была корректно инициализирована: {db_error}")

        # Инициализируем конфигурацию приложения
        app_config = AppConfig()

        # Создаем хранилище согласно конфигурации
        # PostgresSaver больше не создает базу данных - это делает DBManager
        storage = StorageFactory.create_storage(app_config.default_storage_type)
        logger.info(f"Используется хранилище: {type(storage).__name__}")

        # Создаем пользовательский интерфейс с правильным хранилищем и db_manager

        user_interface = UserInterface(storage, db_manager=db_manager)

        # Запускаем основной цикл интерфейса
        user_interface.run()

    except KeyboardInterrupt:
        print("\n\nРабота прервана пользователем. До свидания!")
        logger.info("Приложение завершено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\nКритическая ошибка: {e}")
        if any(keyword in str(e).lower() for keyword in ["базы данных", "database", "connection", "подключ"]):
            print("Программа не может работать без базы данных. Завершение работы.")
            print("Проверьте:")
            print("1. Настройки подключения в файле .env")
            print("2. Что PostgreSQL сервер запущен и доступен")
            print("3. Правильность параметров подключения")
        else:
            print("Обратитесь к разработчику для решения проблемы.")
        return


if __name__ == "__main__":
    main()
