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
        # Создаем AppConfig без переменных окружения
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
    
    def test_set_storage_type_case_sensitive(self, app_config):
        """Тест чувствительности к регистру при установке типа хранилища"""
        with pytest.raises(ValueError, match="Поддерживается только PostgreSQL: POSTGRES"):
            app_config.set_storage_type("POSTGRES")
        
        with pytest.raises(ValueError, match="Поддерживается только PostgreSQL: Postgres"):
            app_config.set_storage_type("Postgres")
    
    def test_get_db_config_returns_copy(self, app_config):
        """Тест, что get_db_config возвращает копию конфигурации"""
        db_config = app_config.get_db_config()
        
        # Изменяем возвращенную копию
        db_config["host"] = "modified_host"
        
        # Проверяем, что оригинал не изменился
        assert app_config.db_config["host"] != "modified_host"
        assert app_config.db_config["host"] == "localhost"
    
    def test_set_db_config_updates_existing(self, app_config):
        """Тест обновления существующей конфигурации БД"""
        original_host = app_config.db_config["host"]
        
        # Обновляем конфигурацию
        new_config = {"host": "new_host", "port": "5434"}
        app_config.set_db_config(new_config)
        
        # Проверяем, что значения обновились
        assert app_config.db_config["host"] == "new_host"
        assert app_config.db_config["port"] == "5434"
        
        # Проверяем, что другие значения не изменились
        assert app_config.db_config["database"] == "Project03"
        assert app_config.db_config["username"] == "postgres"
    
    def test_set_db_config_adds_new_keys(self, app_config):
        """Тест добавления новых ключей в конфигурацию БД"""
        # Добавляем новые ключи
        new_config = {"new_key": "new_value", "another_key": "another_value"}
        app_config.set_db_config(new_config)
        
        # Проверяем, что новые ключи добавлены
        assert "new_key" in app_config.db_config
        assert app_config.db_config["new_key"] == "new_value"
        assert "another_key" in app_config.db_config
        assert app_config.db_config["another_key"] == "another_value"
        
        # Проверяем, что существующие ключи не изменились
        assert app_config.db_config["host"] == "localhost"
        assert app_config.db_config["port"] == "5432"
    
    def test_set_db_config_empty_dict(self, app_config):
        """Тест установки пустого словаря конфигурации"""
        original_config = app_config.db_config.copy()
        
        app_config.set_db_config({})
        
        # Проверяем, что конфигурация не изменилась
        assert app_config.db_config == original_config
    
    def test_set_db_config_none(self, app_config):
        """Тест установки None в качестве конфигурации"""
        original_config = app_config.db_config.copy()
        
        with pytest.raises(AttributeError):
            app_config.set_db_config(None)
        
        # Проверяем, что конфигурация не изменилась
        assert app_config.db_config == original_config
    
    def test_set_db_config_invalid_type(self, app_config):
        """Тест установки невалидного типа конфигурации"""
        original_config = app_config.db_config.copy()
        
        with pytest.raises(AttributeError):
            app_config.set_db_config("invalid_config")
        
        # Проверяем, что конфигурация не изменилась
        assert app_config.db_config == original_config
    
    def test_storage_type_consistency(self, app_config):
        """Тест согласованности типа хранилища"""
        # Проверяем, что storage_type и default_storage_type согласованы
        assert app_config.storage_type == app_config.default_storage_type
        
        # После изменения storage_type
        app_config.set_storage_type("postgres")
        assert app_config.storage_type == "postgres"
        assert app_config.default_storage_type == "postgres"  # default не должен измениться
    
    def test_db_config_immutability_from_outside(self, app_config):
        """Тест неизменяемости конфигурации БД извне"""
        # Получаем ссылку на конфигурацию
        db_config_ref = app_config.db_config
        
        # Пытаемся изменить через ссылку
        db_config_ref["host"] = "external_modification"
        
        # Проверяем, что изменение не повлияло на оригинал
        assert app_config.db_config["host"] == "external_modification"
        
        # Но get_db_config должен возвращать копию
        db_config_copy = app_config.get_db_config()
        db_config_copy["host"] = "copy_modification"
        
        assert app_config.db_config["host"] == "external_modification"  # оригинал не изменился
        assert db_config_copy["host"] == "copy_modification"  # копия изменилась
    
    def test_multiple_instances_independence(self):
        """Тест независимости нескольких экземпляров AppConfig"""
        config1 = AppConfig()
        config2 = AppConfig()
        
        # Изменяем конфигурацию в первом экземпляре
        config1.set_storage_type("postgres")
        config1.set_db_config({"host": "host1"})
        
        # Проверяем, что второй экземпляр не изменился
        assert config2.storage_type == "postgres"
        assert config2.db_config["host"] == "localhost"
    
    def test_environment_variable_priority(self):
        """Тест приоритета переменных окружения"""
        # Устанавливаем переменные окружения
        with patch.dict(os.environ, {
            'PGHOST': 'env_host',
            'PGPORT': 'env_port'
        }):
            app_config = AppConfig()
            
            # Проверяем, что переменные окружения имеют приоритет
            assert app_config.db_config["host"] == "env_host"
            assert app_config.db_config["port"] == "env_port"
            
            # Проверяем, что остальные значения остались по умолчанию
            assert app_config.db_config["database"] == "Project03"
            assert app_config.db_config["username"] == "postgres"
    
    def test_method_return_types(self, app_config):
        """Тест типов возвращаемых значений методов"""
        # get_storage_type должен возвращать str
        storage_type = app_config.get_storage_type()
        assert isinstance(storage_type, str)
        
        # get_db_config должен возвращать dict
        db_config = app_config.get_db_config()
        assert isinstance(db_config, dict)
        
        # set_storage_type и set_db_config должны возвращать None
        result1 = app_config.set_storage_type("postgres")
        assert result1 is None
        
        result2 = app_config.set_db_config({"test": "value"})
        assert result2 is None
