#!/usr/bin/env python3
"""
Модуль для запуска пользовательского интерфейса
"""

import logging

from src.config.app_config import AppConfig
from src.storage.storage_factory import StorageFactory
from src.ui_interfaces.console_interface import ConsoleInterface
from src.utils.menu_manager import MenuManager


def main() -> None:
    """
    Основная функция для запуска пользовательского интерфейса
    """
    try:
        # Создаем менеджер меню
        menu_manager = MenuManager()

        # Инициализируем конфигурацию приложения
        app_config = AppConfig()

        # Создаем хранилище согласно конфигурации
        storage = StorageFactory.create_storage(app_config.default_storage_type)

        # Создаем консольный интерфейс с хранилищем
        console_interface = ConsoleInterface(storage)

        # Запускаем основной цикл интерфейса
        console_interface.run()

    except KeyboardInterrupt:
        print("\n\nРабота прервана пользователем. До свидания!")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        print(f"\nПроизошла непредвиденная ошибка: {e}")
        print("Обратитесь к разработчику для решения проблемы.")


if __name__ == "__main__":
    main()