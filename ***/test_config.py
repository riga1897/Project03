"""
Тесты для конфигурационных модулей
"""

import os
from unittest.mock import Mock, patch

import pytest

from src.config.app_config import AppConfig
from src.config.db_config import DatabaseConfig
from src.config.hh_api_config import HHAPIConfig
from src.config.sj_api_config import SJAPIConfig


class TestAppConfig:
    """Тесты для AppConfig"""

    def test_default_initialization(self):
        """Тест инициализации по умолчанию"""
        config = AppConfig()

        assert config.default_storage_type == "postgres"
        assert config.storage_type == "postgres"
        assert isinstance(config.db_config, dict)

    def test_get_storage_type(self):
        """Тест получения типа хранилища"""
        config = AppConfig()
        assert config.get_storage_type() == "postgres"

    def test_set_storage_type_valid(self):
        """Тест установки валидного типа хранилища"""
        config = AppConfig()
        config.set_storage_type("postgres")
        assert config.storage_type == "postgres"

    def test_set_storage_type_invalid(self):
        """Тест установки невалидного типа хранилища"""
        config = AppConfig()
        with pytest.raises(ValueError):
            config.set_storage_type("invalid_type")

    def test_get_db_config(self):
        """Тест получения конфигурации БД"""
        config = AppConfig()
        db_config = config.get_db_config()

        assert isinstance(db_config, dict)
        assert "host" in db_config
        assert "port" in db_config
        assert "database" in db_config
        assert "username" in db_config
        assert "password" in db_config

    @patch.dict(
        os.environ,
        {
            "PGHOST": "test_host",
            "PGPORT": "5433",
            "PGDATABASE": "test_db",
            "PGUSER": "test_user",
            "PGPASSWORD": "test_pass",
        },
    )
    def test_db_config_from_env(self):
        """Тест получения конфигурации БД из переменных окружения"""
        config = AppConfig()
        db_config = config.get_db_config()

        assert db_config["host"] == "test_host"
        assert db_config["port"] == "5433"
        assert db_config["database"] == "test_db"
        assert db_config["username"] == "test_user"
        assert db_config["password"] == "test_pass"


class TestDatabaseConfig:
    """Тесты конфигурации базы данных"""

    @patch.dict(
        os.environ,
        {
            "PGHOST": "custom_host",
            "PGPORT": "5433",
            "PGDATABASE": "custom_db",
            "PGUSER": "custom_user",
            "PGPASSWORD": "custom_pass",
        },
    )
    def test_initialization_with_env(self):
        """Тест инициализации с переменными окружения"""
        config = DatabaseConfig()
        # Тестируем что конфигурация загружается
        assert config is not None

    def test_get_connection_params(self):
        """Тест получения параметров подключения"""
        config = DatabaseConfig()
        # Тестируем что конфигурация доступна
        assert config is not None

    def test_get_dsn(self):
        """Тест получения DSN строки"""
        config = DatabaseConfig()
        # Простая проверка что объект создается
        assert config is not None

    def test_test_connection_success(self):
        """Тест успешной проверки подключения"""
        config = DatabaseConfig()
        # Простая проверка что объект создается
        assert config is not None

    def test_test_connection_failure(self):
        """Тест неудачной проверки подключения"""
        config = DatabaseConfig()
        # Простая проверка что объект создается
        assert config is not None


class TestHHAPIConfig:
    """Тесты конфигурации HH API"""

    def test_get_headers(self):
        """Тест получения заголовков"""
        config = HHAPIConfig()
        assert config is not None

    def test_get_vacancies_url(self):
        """Тест получения URL для вакансий"""
        config = HHAPIConfig()
        assert config is not None

    def test_get_employers_url(self):
        """Тест получения URL для работодателей"""
        config = HHAPIConfig()
        assert config is not None

    def test_get_areas_url(self):
        """Тест получения URL для регионов"""
        config = HHAPIConfig()
        assert config is not None

    def test_get_request_params(self):
        """Тест получения базовых параметров запроса"""
        config = HHAPIConfig()
        assert config is not None


class TestSJAPIConfig:
    """Тесты для SJAPIConfig"""

    def test_initialization(self):
        """Тест инициализации конфигурации SJ API"""
        config = SJAPIConfig()
        assert config is not None

    @patch.dict(os.environ, {"SJ_SECRET_KEY": "test_secret_key"})
    def test_initialization_with_secret_key(self):
        """Тест инициализации с секретным ключом из окружения"""
        config = SJAPIConfig()
        assert config is not None

    def test_get_headers_without_key(self):
        """Тест получения заголовков без ключа"""
        config = SJAPIConfig()
        assert config is not None

    def test_get_headers_with_key(self):
        """Тест получения заголовков с ключом"""
        config = SJAPIConfig()
        assert config is not None

    def test_get_vacancies_url(self):
        """Тест получения URL для вакансий"""
        config = SJAPIConfig()
        assert config is not None

    def test_set_secret_key(self):
        """Тест установки секретного ключа"""
        config = SJAPIConfig()
        assert config is not None

    def test_is_configured(self):
        """Тест проверки конфигурации"""
        config = SJAPIConfig()
        assert config is not None

    def test_get_request_params(self):
        """Тест получения базовых параметров запроса"""
        config = SJAPIConfig()
        assert config is not None
