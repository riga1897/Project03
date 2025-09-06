"""
100% покрытие config/app_config.py модуля
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.config.app_config import AppConfig


class TestAppConfig:
    """100% покрытие AppConfig класса"""

    def test_app_config_initialization_defaults(self):
        """Тест инициализации AppConfig с дефолтными значениями - покрывает строки 10, 11, 14-20"""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig()
            
            # Проверяем дефолтные значения
            assert config.default_storage_type == "postgres"
            assert config.storage_type == "postgres"
            assert config.db_config["host"] == "localhost"
            assert config.db_config["port"] == "5432"
            assert config.db_config["database"] == "Project03"
            assert config.db_config["username"] == "postgres"
            assert config.db_config["password"] == ""

    def test_app_config_initialization_with_env_vars(self):
        """Тест инициализации AppConfig с переменными окружения - покрывает строки 15-19"""
        env_vars = {
            "PGHOST": "test_host",
            "PGPORT": "5433",
            "PGDATABASE": "test_db",
            "PGUSER": "test_user",
            "PGPASSWORD": "test_password"
        }
        
        with patch.dict(os.environ, env_vars):
            config = AppConfig()
            
            # Проверяем что используются значения из окружения
            assert config.db_config["host"] == "test_host"
            assert config.db_config["port"] == "5433"
            assert config.db_config["database"] == "test_db"
            assert config.db_config["username"] == "test_user"
            assert config.db_config["password"] == "test_password"

    def test_app_config_partial_env_vars(self):
        """Тест инициализации с частичными переменными окружения"""
        env_vars = {
            "PGHOST": "partial_host",
            "PGUSER": "partial_user"
            # Остальные переменные не установлены
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = AppConfig()
            
            # Проверяем смешение значений из окружения и дефолтных
            assert config.db_config["host"] == "partial_host"
            assert config.db_config["port"] == "5432"  # дефолт
            assert config.db_config["database"] == "Project03"  # дефолт
            assert config.db_config["username"] == "partial_user"
            assert config.db_config["password"] == ""  # дефолт

    def test_get_storage_type(self):
        """Тест метода get_storage_type - покрывает строку 24"""
        config = AppConfig()
        
        # Проверяем дефолтный тип
        assert config.get_storage_type() == "postgres"
        
        # Изменяем тип и проверяем
        config.storage_type = "postgres"  # Принудительно установим
        assert config.get_storage_type() == "postgres"

    def test_set_storage_type_valid(self):
        """Тест метода set_storage_type с валидным типом - покрывает строки 30"""
        config = AppConfig()
        
        # Устанавливаем валидный тип
        config.set_storage_type("postgres")
        assert config.storage_type == "postgres"
        assert config.get_storage_type() == "postgres"

    def test_set_storage_type_invalid(self):
        """Тест метода set_storage_type с невалидным типом - покрывает строки 28, 29"""
        config = AppConfig()
        
        # Пытаемся установить невалидный тип
        with pytest.raises(ValueError) as exc_info:
            config.set_storage_type("mysql")
        
        assert "Поддерживается только PostgreSQL: mysql" in str(exc_info.value)
        
        # Проверяем что тип не изменился
        assert config.storage_type == "postgres"

    def test_set_storage_type_various_invalid_types(self):
        """Тест различных невалидных типов хранилища"""
        config = AppConfig()
        
        invalid_types = ["mysql", "sqlite", "mongodb", "redis", ""]
        
        for invalid_type in invalid_types:
            with pytest.raises(ValueError) as exc_info:
                config.set_storage_type(invalid_type)
            
            assert f"Поддерживается только PostgreSQL: {invalid_type}" in str(exc_info.value)
            # Проверяем что исходный тип не изменился
            assert config.storage_type == "postgres"

    def test_get_db_config(self):
        """Тест метода get_db_config - покрывает строку 34"""
        config = AppConfig()
        
        db_config = config.get_db_config()
        
        # Проверяем структуру возвращаемого словаря
        assert isinstance(db_config, dict)
        assert "host" in db_config
        assert "port" in db_config
        assert "database" in db_config
        assert "username" in db_config
        assert "password" in db_config
        
        # Проверяем что возвращается копия, а не оригинальный объект
        assert db_config is not config.db_config
        
        # Проверяем содержимое
        expected_keys = {"host", "port", "database", "username", "password"}
        assert set(db_config.keys()) == expected_keys

    def test_get_db_config_returns_copy(self):
        """Тест что get_db_config возвращает копию"""
        config = AppConfig()
        
        db_config1 = config.get_db_config()
        db_config2 = config.get_db_config()
        
        # Убеждаемся что это разные объекты
        assert db_config1 is not db_config2
        assert db_config1 == db_config2
        
        # Модификация копии не должна влиять на оригинал
        db_config1["host"] = "modified_host"
        assert config.db_config["host"] != "modified_host"

    def test_set_db_config(self):
        """Тест метода set_db_config - покрывает строку 38"""
        config = AppConfig()
        
        original_host = config.db_config["host"]
        
        # Обновляем конфигурацию
        new_config = {"host": "new_host", "port": "5434"}
        config.set_db_config(new_config)
        
        # Проверяем что значения обновились
        assert config.db_config["host"] == "new_host"
        assert config.db_config["port"] == "5434"
        
        # Проверяем что остальные значения сохранились
        assert "database" in config.db_config
        assert "username" in config.db_config
        assert "password" in config.db_config

    def test_set_db_config_partial_update(self):
        """Тест частичного обновления конфигурации БД"""
        config = AppConfig()
        
        original_config = config.get_db_config()
        
        # Обновляем только некоторые параметры
        partial_config = {"host": "updated_host", "database": "updated_db"}
        config.set_db_config(partial_config)
        
        # Проверяем что обновились только указанные параметры
        assert config.db_config["host"] == "updated_host"
        assert config.db_config["database"] == "updated_db"
        assert config.db_config["port"] == original_config["port"]
        assert config.db_config["username"] == original_config["username"]
        assert config.db_config["password"] == original_config["password"]

    def test_set_db_config_empty_dict(self):
        """Тест обновления конфигурации пустым словарем"""
        config = AppConfig()
        
        original_config = config.get_db_config()
        
        # Обновляем пустым словарем
        config.set_db_config({})
        
        # Проверяем что ничего не изменилось
        assert config.get_db_config() == original_config

    def test_set_db_config_new_keys(self):
        """Тест добавления новых ключей в конфигурацию"""
        config = AppConfig()
        
        # Добавляем новые ключи
        new_config = {"connection_timeout": "30", "sslmode": "require"}
        config.set_db_config(new_config)
        
        # Проверяем что новые ключи добавились
        assert config.db_config["connection_timeout"] == "30"
        assert config.db_config["sslmode"] == "require"
        
        # Проверяем что исходные ключи сохранились
        assert "host" in config.db_config
        assert "port" in config.db_config


class TestAppConfigIntegration:
    """Интеграционные тесты AppConfig"""

    def test_full_workflow(self):
        """Тест полного рабочего процесса с AppConfig"""
        with patch.dict(os.environ, {"PGHOST": "workflow_host", "PGPORT": "5435"}):
            config = AppConfig()
            
            # Проверяем инициализацию
            assert config.get_storage_type() == "postgres"
            assert config.get_db_config()["host"] == "workflow_host"
            assert config.get_db_config()["port"] == "5435"
            
            # Обновляем конфигурацию
            config.set_db_config({"database": "workflow_db"})
            
            # Проверяем обновления
            db_config = config.get_db_config()
            assert db_config["database"] == "workflow_db"
            assert db_config["host"] == "workflow_host"
            assert db_config["port"] == "5435"

    def test_env_vars_precedence(self):
        """Тест приоритета переменных окружения"""
        # Тест без переменных окружения
        with patch.dict(os.environ, {}, clear=True):
            config1 = AppConfig()
            assert config1.db_config["host"] == "localhost"
        
        # Тест с переменными окружения
        with patch.dict(os.environ, {"PGHOST": "env_host"}):
            config2 = AppConfig()
            assert config2.db_config["host"] == "env_host"

    def test_config_immutability_through_methods(self):
        """Тест неизменяемости конфигурации через методы"""
        config = AppConfig()
        
        # Получаем копию конфигурации
        db_config = config.get_db_config()
        original_host = db_config["host"]
        
        # Модифицируем копию
        db_config["host"] = "hacker_host"
        
        # Проверяем что исходная конфигурация не изменилась
        assert config.db_config["host"] == original_host
        assert config.get_db_config()["host"] == original_host


class TestAppConfigEdgeCases:
    """Тесты граничных случаев AppConfig"""

    def test_storage_type_edge_cases(self):
        """Тест граничных случаев для storage_type"""
        config = AppConfig()
        
        # Тест с None
        with pytest.raises(ValueError):
            config.set_storage_type(None)
        
        # Тест с пустой строкой
        with pytest.raises(ValueError):
            config.set_storage_type("")
        
        # Тест с пробелами
        with pytest.raises(ValueError):
            config.set_storage_type("   ")

    def test_db_config_type_consistency(self):
        """Тест консистентности типов в db_config"""
        config = AppConfig()
        
        db_config = config.get_db_config()
        
        # Проверяем что все значения - строки
        for key, value in db_config.items():
            assert isinstance(key, str), f"Key {key} is not string"
            assert isinstance(value, str), f"Value {value} for key {key} is not string"

    def test_env_vars_with_none_values(self):
        """Тест поведения с None значениями в переменных окружения"""
        # os.getenv может вернуть None, но мы тестируем что делают дефолтные значения
        with patch('os.getenv') as mock_getenv:
            def side_effect(key, default):
                # Имитируем что переменная окружения не установлена
                return default
            
            mock_getenv.side_effect = side_effect
            
            config = AppConfig()
            
            # Проверяем что используются дефолтные значения
            assert config.db_config["host"] == "localhost"
            assert config.db_config["port"] == "5432"
            assert config.db_config["database"] == "Project03"
            assert config.db_config["username"] == "postgres"
            assert config.db_config["password"] == ""