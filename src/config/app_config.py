import os
from typing import Dict


class AppConfig:
    """Класс для управления конфигурацией приложения"""

    def __init__(self) -> None:
        """Инициализация конфигурации приложения с настройками по умолчанию."""
        # По умолчанию используем PostgreSQL хранилище
        self.default_storage_type = "postgres"
        self.storage_type = self.default_storage_type

        # Настройки БД
        self.db_config = {
            "host": os.getenv("PGHOST", "localhost"),
            "port": os.getenv("PGPORT", "5432"),
            "database": os.getenv("PGDATABASE", "Project03"),
            "username": os.getenv("PGUSER", "postgres"),
            "password": os.getenv("PGPASSWORD", ""),
        }

    def get_storage_type(self) -> str:
        """Возвращает тип хранилища"""
        return self.storage_type

    def set_storage_type(self, storage_type: str) -> None:
        """Устанавливает тип хранилища"""
        if storage_type != "postgres":
            raise ValueError(f"Поддерживается только PostgreSQL: {storage_type}")
        self.storage_type = storage_type

    def get_db_config(self) -> Dict[str, str]:
        """Возвращает конфигурацию БД"""
        return self.db_config.copy()

    def set_db_config(self, config: Dict[str, str]) -> None:
        """Обновляет конфигурацию БД"""
        self.db_config.update(config)
