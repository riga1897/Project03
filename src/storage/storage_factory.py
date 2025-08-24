from typing import Union, Dict, Optional
from src.storage.json_saver import JSONSaver
from src.storage.postgres_saver import PostgresSaver
from src.storage.abstract import AbstractVacancyStorage
from src.config.db_config import DatabaseConfig


class StorageFactory:
    """Фабрика для создания объектов хранилища"""

    @staticmethod
    def create_storage(storage_type: str) -> AbstractVacancyStorage:
        """
        Создает экземпляр хранилища указанного типа

        Args:
            storage_type: Тип хранилища ('json' или 'postgres')

        Returns:
            AbstractVacancyStorage: Экземпляр хранилища
        """
        if storage_type == "json":
            return JSONSaver()
        elif storage_type == "postgres":
            from src.config.app_config import AppConfig
            app_config = AppConfig()
            return PostgresSaver(app_config.get_db_config())
        else:
            raise ValueError(f"Неподдерживаемый тип хранилища: {storage_type}")

    @staticmethod
    def get_default_storage() -> AbstractVacancyStorage:
        """
        Возвращает хранилище по умолчанию

        Returns:
            AbstractVacancyStorage: Хранилище по умолчанию (PostgreSQL)
        """
        return StorageFactory.create_storage("postgres")