
#!/usr/bin/env python3
"""
Тесты для модуля app_config.py
"""

import os
from unittest.mock import patch, Mock
import pytest

from src.config.app_config import AppConfig


class TestAppConfig:
    """Тесты для класса AppConfig"""

    @pytest.fixture
    def app_config(self):
        """Создание экземпляра AppConfig для тестов"""
        return AppConfig()

    def test_app_config_initialization(self, app_config):
        """Тест инициализации AppConfig"""
        assert app_config.default_storage_type == "postgres"
        assert app_config.storage_type == "postgres"
        assert isinstance(app_config.db_config, dict)

    def test_db_config_structure(self, app_config):
        """Тест структуры конфигурации БД"""
        db_config = app_config.db_config

        required_keys = ["host", "port", "database", "username", "password"]
        for key in required_keys:
            assert key in db_config
            assert isinstance(db_config[key], str)

    @patch.dict(os.environ, {
        'PGHOST': 'test_host',
        'PGPORT': '5433',
        'PGDATABASE': 'test_db',
        'PGUSER': 'test_user',
        'PGPASSWORD': 'test_password'
    })
    def test_db_config_from_environment(self):
        """Тест загрузки конфигурации БД из переменных окружения"""
        app_config = AppConfig()

        assert app_config.db_config["host"] == "test_host"
        assert app_config.db_config["port"] == "5433"
        assert app_config.db_config["database"] == "test_db"
        assert app_config.db_config["username"] == "test_user"
        assert app_config.db_config["password"] == "test_password"

    def test_db_config_default_values(self, app_config):
        """Тест значений по умолчанию для конфигурации БД"""
        with patch.dict(os.environ, {}, clear=True):
            app_config = AppConfig()

            assert app_config.db_config["host"] == "localhost"
            assert app_config.db_config["port"] == "5432"
            assert app_config.db_config["database"] == "Project03"
            assert app_config.db_config["username"] == "postgres"
            assert app_config.db_config["password"] == ""

    def test_get_storage_type(self, app_config):
        """Тест получения типа хранилища"""
        storage_type = app_config.get_storage_type()
        assert storage_type == "postgres"
        assert isinstance(storage_type, str)

    def test_set_storage_type_valid(self, app_config):
        """Тест установки валидного типа хранилища"""
        app_config.set_storage_type("postgres")
        assert app_config.storage_type == "postgres"
        assert app_config.get_storage_type() == "postgres"

    def test_set_storage_type_invalid(self, app_config):
        """Тест установки невалидного типа хранилища"""
        with pytest.raises(ValueError, match="Поддерживается только PostgreSQL: invalid_type"):
            app_config.set_storage_type("invalid_type")

        # Проверяем, что значение не изменилось
        assert app_config.storage_type == "postgres"

    def test_get_db_config_returns_copy(self, app_config):
        """Тест, что get_db_config возвращает копию конфигурации"""
        db_config = app_config.get_db_config()
        
        # Изменяем возвращенную копию
        db_config["host"] = "modified_host"

        # Проверяем, что оригинал не изменился
        assert app_config.db_config["host"] != "modified_host"

    def test_set_db_config_updates_existing(self, app_config):
        """Тест обновления существующей конфигурации БД"""
        # Обновляем конфигурацию
        new_config = {"host": "localhost", "port": "5434"}
        app_config.set_db_config(new_config)

        # Проверяем, что значения обновились
        assert app_config.db_config["host"] == "localhost"
        assert app_config.db_config["port"] == "5434"

        # Проверяем, что другие значения остались
        assert "database" in app_config.db_config
        assert "username" in app_config.db_config
