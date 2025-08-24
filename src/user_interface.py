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
        
        # Инициализируем конфигурацию приложения
        app_config = AppConfig()

        # Создаем хранилище согласно конфигурации
        storage = StorageFactory.create_storage(app_config.default_storage_type)
        logger.info(f"Используется хранилище: {type(storage).__name__}")

        # Создаем пользовательский интерфейс с правильным хранилищем
        user_interface = UserInterface(storage)

        # Запускаем основной цикл интерфейса
        user_interface.run()

    except KeyboardInterrupt:
        print("\n\nРабота прервана пользователем. До свидания!")
        logger.info("Приложение завершено пользователем")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        print(f"\nПроизошла непредвиденная ошибка: {e}")
        print("Обратитесь к разработчику для решения проблемы.")


if __name__ == "__main__":
    main()