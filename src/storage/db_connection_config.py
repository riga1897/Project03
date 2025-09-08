"""
Универсальный модуль для конфигурации подключения к БД

Поддерживает разные способы конфигурации:
1. DATABASE_URL (приоритет)
2. Отдельные параметры (PGHOST, PGPORT, и т.д.)
3. Конфиг-словари
4. Переменные окружения других платформ (POSTGRES_*, DATABASE_*)
"""

import logging
import os
import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DatabaseConnectionConfig:
    """
    Универсальный конфигуратор подключения к базе данных

    Автоматически определяет доступные параметры подключения из различных источников
    и создает единую конфигурацию для psycopg2.
    """

    # Поддерживаемые форматы переменных окружения
    ENV_MAPPINGS = {
        # PostgreSQL стандартные
        "PGHOST": "host",
        "PGPORT": "port",
        "PGDATABASE": "database",
        "PGUSER": "user",
        "PGPASSWORD": "password",
        # Docker/Cloud часто используемые
        "POSTGRES_HOST": "host",
        "POSTGRES_PORT": "port",
        "POSTGRES_DB": "database",
        "POSTGRES_DATABASE": "database",
        "POSTGRES_USER": "user",
        "POSTGRES_USERNAME": "user",
        "POSTGRES_PASSWORD": "password",
        # Альтернативные названия
        "DATABASE_HOST": "host",
        "DATABASE_PORT": "port",
        "DATABASE_NAME": "database",
        "DATABASE_USER": "user",
        "DATABASE_PASSWORD": "password",
        "DB_HOST": "host",
        "DB_PORT": "port",
        "DB_NAME": "database",
        "DB_USER": "user",
        "DB_PASSWORD": "password",
    }

    # Значения по умолчанию
    DEFAULTS = {
        "host": "localhost",
        "port": "5432",
        "database": "postgres",
        "user": "postgres",
        "password": "",
        "connect_timeout": "10",
        "command_timeout": "30",
    }

    def __init__(self) -> None:
        """Инициализация конфигуратора"""
        self.config = {}

    def get_connection_params(
        self, db_config: Optional[Dict[str, Any]] = None, database_url: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Получает параметры подключения из всех доступных источников

        Приоритет:
        1. Явно переданный database_url
        2. DATABASE_URL из окружения
        3. Явно переданный db_config
        4. Переменные окружения (все поддерживаемые форматы)
        5. Значения по умолчанию

        Args:
            db_config: Словарь с параметрами подключения
            database_url: URL подключения к БД

        Returns:
            Dict[str, str]: Параметры подключения для psycopg2
        """
        config = {}

        # 1. Пробуем DATABASE_URL (приоритет)
        url_to_parse = database_url or os.getenv("DATABASE_URL")
        if url_to_parse:
            try:
                url_config = self._parse_database_url(url_to_parse)
                config.update(url_config)
                logger.debug("Загружена конфигурация из DATABASE_URL")
            except Exception as e:
                logger.warning(f"Не удалось распарсить DATABASE_URL: {e}")

        # 2. Дополняем из явного db_config
        if db_config:
            # Нормализуем ключи
            normalized_config = self._normalize_config_keys(db_config)
            config.update(normalized_config)
            logger.debug("Загружена конфигурация из переданного db_config")

        # 3. Дополняем из переменных окружения
        env_config = self._load_from_environment()
        for key, value in env_config.items():
            if key not in config or not config[key]:  # Не перезаписываем уже установленные значения
                config[key] = value

        # 4. Применяем значения по умолчанию
        for key, default_value in self.DEFAULTS.items():
            if key not in config or not config[key]:
                config[key] = default_value

        # Валидируем и очищаем конфигурацию
        config = self._validate_and_clean_config(config)

        logger.debug(
            f"Итоговая конфигурация БД: host={config.get('host')}, port={config.get('port')}, database={config.get('database')}, user={config.get('user')}"
        )
        return config

    def _parse_database_url(self, database_url: str) -> Dict[str, str]:
        """
        Парсит DATABASE_URL в различных форматах

        Поддерживаемые форматы:
        - postgresql://user:pass@host:port/db
        - postgres://user:pass@host:port/db
        - psql://user:pass@host:port/db

        Args:
            database_url: URL подключения

        Returns:
            Dict[str, str]: Распарсенные параметры
        """
        # Нормализуем URL
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        elif database_url.startswith("psql://"):
            database_url = database_url.replace("psql://", "postgresql://", 1)

        try:
            parsed = urlparse(database_url)

            config = {}
            if parsed.hostname:
                config["host"] = parsed.hostname
            if parsed.port:
                config["port"] = str(parsed.port)
            if parsed.username:
                config["user"] = parsed.username
            if parsed.password:
                config["password"] = parsed.password
            if parsed.path and len(parsed.path) > 1:  # Убираем ведущий /
                config["database"] = parsed.path[1:]

            # Парсим дополнительные параметры
            if parsed.query:
                for param in parsed.query.split("&"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        if key == "sslmode":
                            config["sslmode"] = value

            return config

        except Exception as e:
            raise ValueError(f"Некорректный формат DATABASE_URL: {e}")

    def _load_from_environment(self) -> Dict[str, str]:
        """Загружает параметры из переменных окружения"""
        config = {}

        for env_var, param_key in self.ENV_MAPPINGS.items():
            value = os.getenv(env_var)
            if value:
                # Берем первое найденное значение для каждого параметра
                if param_key not in config:
                    config[param_key] = value
                    logger.debug(f"Загружен параметр {param_key} из {env_var}")

        return config

    def _normalize_config_keys(self, db_config: Dict[str, Any]) -> Dict[str, str]:
        """
        Нормализует ключи конфигурации к стандартному формату psycopg2

        Args:
            db_config: Исходная конфигурация

        Returns:
            Dict[str, str]: Нормализованная конфигурация
        """
        normalized = {}

        # Маппинг альтернативных ключей
        key_mappings = {
            "username": "user",
            "hostname": "host",
            "dbname": "database",
            "db": "database",
            "passwd": "password",
            "pwd": "password",
        }

        for key, value in db_config.items():
            if value is not None:
                # Нормализуем ключ
                normalized_key = key_mappings.get(key.lower(), key.lower())
                normalized[normalized_key] = str(value)

        return normalized

    def _validate_and_clean_config(self, config: Dict[str, str]) -> Dict[str, str]:
        """
        Валидирует и очищает конфигурацию

        Args:
            config: Конфигурация для валидации

        Returns:
            Dict[str, str]: Валидная конфигурация
        """
        # Проверяем обязательные параметры
        required_params = ["host", "port", "database", "user"]
        for param in required_params:
            if not config.get(param):
                logger.warning(f"Не задан обязательный параметр {param}, используется значение по умолчанию")
                config[param] = self.DEFAULTS.get(param, "")

        # Валидируем порт
        try:
            port = int(config["port"])
            if not (1 <= port <= 65535):
                raise ValueError
        except (ValueError, TypeError):
            logger.warning(f"Некорректный порт {config['port']}, используется 5432")
            config["port"] = "5432"

        # Очищаем пустые значения (кроме пароля, он может быть пустым)
        cleaned_config = {}
        for key, value in config.items():
            if value or key == "password":
                cleaned_config[key] = value

        return cleaned_config

    @classmethod
    def create_from_environment(cls) -> "DatabaseConnectionConfig":
        """Создает конфигуратор и автоматически загружает параметры из окружения"""
        configurator = cls()
        return configurator


# Удобные функции для быстрого использования
def get_db_connection_params(
    db_config: Optional[Dict[str, Any]] = None, database_url: Optional[str] = None
) -> Dict[str, str]:
    """
    Быстрая функция для получения параметров подключения к БД

    Args:
        db_config: Словарь с параметрами подключения
        database_url: URL подключения к БД

    Returns:
        Dict[str, str]: Параметры подключения для psycopg2
    """
    configurator = DatabaseConnectionConfig()
    return configurator.get_connection_params(db_config, database_url)
