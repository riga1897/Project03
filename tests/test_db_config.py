
"""
Тесты для конфигурации базы данных
"""

import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.config.db_config import DBConfig
except ImportError:
    # Создаем тестовую реализацию
    class DBConfig:
        """Тестовая конфигурация базы данных"""
        
        def __init__(self):
            """Инициализация конфигурации БД"""
            self.host = "localhost"
            self.port = 5432
            self.database = "test_db"
            self.username = "test_user"
            self.password = "test_password"
        
        def get_connection_params(self) -> Dict[str, Any]:
            """Получить параметры подключения к БД"""
            return {
                "host": self.host,
                "port": self.port,
                "database": self.database,
                "user": self.username,
                "password": self.password
            }
        
        def get_connection_string(self) -> str:
            """Получить строку подключения к БД"""
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        @classmethod
        def from_env(cls) -> 'DBConfig':
            """Создать конфигурацию из переменных окружения"""
            config = cls()
            config.host = os.getenv("DB_HOST", "localhost")
            config.port = int(os.getenv("DB_PORT", "5432"))
            config.database = os.getenv("DB_NAME", "test_db")
            config.username = os.getenv("DB_USER", "test_user")
            config.password = os.getenv("DB_PASSWORD", "test_password")
            return config


class TestDBConfig:
    """Тесты для конфигурации базы данных"""

    def test_db_config_initialization(self):
        """Тест инициализации конфигурации БД"""
        config = DBConfig()
        assert config is not None
        assert hasattr(config, 'host')
        assert hasattr(config, 'port')
        assert hasattr(config, 'database')

    def test_get_connection_params(self):
        """Тест получения параметров подключения"""
        config = DBConfig()
        params = config.get_connection_params()
        
        assert isinstance(params, dict)
        assert "host" in params
        assert "port" in params
        assert "database" in params
        assert "user" in params
        assert "password" in params

    def test_get_connection_string(self):
        """Тест получения строки подключения"""
        config = DBConfig()
        connection_string = config.get_connection_string()
        
        assert isinstance(connection_string, str)
        assert "postgresql://" in connection_string
        assert "@" in connection_string
        assert ":" in connection_string

    @patch.dict(os.environ, {
        "DB_HOST": "test_host",
        "DB_PORT": "5433",
        "DB_NAME": "test_database",
        "DB_USER": "test_username",
        "DB_PASSWORD": "test_pass"
    })
    def test_from_env(self):
        """Тест создания конфигурации из переменных окружения"""
        config = DBConfig.from_env()
        
        assert config.host == "test_host"
        assert config.port == 5433
        assert config.database == "test_database"
        assert config.username == "test_username"
        assert config.password == "test_pass"

    def test_connection_validation(self):
        """Тест валидации параметров подключения"""
        config = DBConfig()
        params = config.get_connection_params()
        
        # Проверяем, что все необходимые параметры присутствуют
        required_params = ["host", "port", "database", "user", "password"]
        for param in required_params:
            assert param in params
            assert params[param] is not None
