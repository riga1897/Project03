import os
from typing import Dict, Optional

from src.utils.env_loader import EnvLoader


class DatabaseConfig:
    """Конфигурация подключения к базе данных"""

    def __init__(self):
        self.default_config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, str]:
        """Получает конфигурацию по умолчанию из переменных окружения"""
        # EnvLoader автоматически загружает переменные из .env при импорте
        return {
            "host": EnvLoader.get_env_var("PGHOST", "localhost"),
            "port": EnvLoader.get_env_var("PGPORT", "5432"),
            "database": EnvLoader.get_env_var("PGDATABASE", "Project03"),
            "username": EnvLoader.get_env_var("PGUSER", "postgres"),
            "password": EnvLoader.get_env_var("PGPASSWORD", ""),
            "connect_timeout": EnvLoader.get_env_var("PGCONNECT_TIMEOUT", "10"),
            "command_timeout": EnvLoader.get_env_var("PGCOMMAND_TIMEOUT", "30"),
        }

    def get_config(self, custom_config: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Возвращает конфигурацию БД

        Args:
            custom_config: Пользовательская конфигурация (опционально)

        Returns:
            Dict[str, str]: Конфигурация подключения к БД
        """
        if custom_config:
            config = self.default_config.copy()
            config.update(custom_config)
            return config
        return self.default_config

    def get_connection_params(self) -> Dict[str, str]:
        """
        Возвращает параметры подключения в формате для psycopg2

        Returns:
            Dict[str, str]: Параметры подключения
        """
        return {
            "host": self.default_config["host"],
            "port": self.default_config["port"],
            "database": self.default_config["database"],
            "user": self.default_config["username"],
            "password": self.default_config["password"],
        }

    def get_connection_params(self) -> Dict[str, str]:
        """
        Возвращает параметры подключения в формате для psycopg2

        Returns:
            Dict[str, str]: Параметры подключения
        """
        return {
            "host": self.default_config["host"],
            "port": self.default_config["port"],
            "database": self.default_config["database"],
            "user": self.default_config["username"],
            "password": self.default_config["password"],
        }

    def test_connection(self, config: Optional[Dict[str, str]] = None) -> bool:
        """
        Тестирует подключение к БД

        Args:
            config: Конфигурация для тестирования (опционально)

        Returns:
            bool: True если подключение успешно
        """
        test_config = config or self.default_config

        try:
            import psycopg2

            connection = psycopg2.connect(
                host=test_config["host"],
                port=test_config["port"],
                database=test_config["database"],
                user=test_config["username"],
                password=test_config["password"],
            )
            connection.close()
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False
