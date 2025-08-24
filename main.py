#!/usr/bin/env python3
"""
Приложение для поиска вакансий с консольным интерфейсом
"""

from src.user_interface import main
from src.storage.storage_factory import StorageFactory
from src.config.app_config import AppConfig
from src.user_interface import ConsoleInterface

if __name__ == "__main__":
    # Инициализируем конфигурацию и хранилище
    app_config = AppConfig()
    storage = StorageFactory.get_default_storage()
    # Запускаем пользовательский интерфейс
    interface = ConsoleInterface(storage)
    main(interface)