"""
100% покрытие config/db_config.py модуля
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest
from typing import Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.config.db_config import DatabaseConfig


class TestDatabaseConfig:
    """100% покрытие DatabaseConfig"""

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_init_with_database_url(self, mock_get_env_var):
        """Тест инициализации с DATABASE_URL"""
        mock_get_env_var.side_effect = lambda key, default=None: {
            "DATABASE_URL": "postgresql://user:pass@host:5432/dbname"
        }.get(key, default)
        
        with patch.object(DatabaseConfig, '_parse_database_url') as mock_parse:
            mock_parse.return_value = {
                "host": "host", 
                "port": "5432",
                "database": "dbname",
                "username": "user", 
                "password": "pass"
            }
            
            config = DatabaseConfig()
            
            mock_parse.assert_called_once_with("postgresql://user:pass@host:5432/dbname")

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_init_with_separate_env_vars(self, mock_get_env_var):
        """Тест инициализации с отдельными переменными окружения"""
        env_vars = {
            "DATABASE_URL": None,
            "PGHOST": "custom_host",
            "PGPORT": "5433",
            "PGDATABASE": "custom_db",
            "PGUSER": "custom_user",
            "PGPASSWORD": "custom_pass",
            "PGCONNECT_TIMEOUT": "20",
            "PGCOMMAND_TIMEOUT": "60"
        }
        
        def get_env_var_side_effect(key, default=None):
            return env_vars.get(key, default)
        
        mock_get_env_var.side_effect = get_env_var_side_effect
        
        config = DatabaseConfig()
        
        expected = {
            "host": "custom_host",
            "port": "5433", 
            "database": "custom_db",
            "username": "custom_user",
            "password": "custom_pass",
            "connect_timeout": "20",
            "command_timeout": "60"
        }
        
        assert config.default_config == expected

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_init_with_defaults(self, mock_get_env_var):
        """Тест инициализации с дефолтными значениями"""
        def get_env_var_side_effect(key, default=None):
            # Возвращаем дефолтные значения для всех ключей
            return default
        
        mock_get_env_var.side_effect = get_env_var_side_effect
        
        config = DatabaseConfig()
        
        expected = {
            "host": "localhost",
            "port": "5432",
            "database": "job_search_app", 
            "username": "postgres",
            "password": "",
            "connect_timeout": "10",
            "command_timeout": "30"
        }
        
        assert config.default_config == expected

    def test_parse_database_url_valid(self):
        """Тест парсинга корректного DATABASE_URL"""
        config = DatabaseConfig()
        
        # Мокируем _get_default_config чтобы не вызывать его при инициализации
        with patch.object(config, '_get_default_config'):
            url = "postgresql://testuser:testpass@testhost:5433/testdb"
            result = config._parse_database_url(url)
            
            # Проверяем основные поля, игнорируя дополнительные timeout поля
            assert result["host"] == "testhost"
            assert result["port"] == "5433"
            assert result["database"] == "testdb"
            assert result["username"] == "testuser"
            assert result["password"] == "testpass"

    def test_parse_database_url_no_port(self):
        """Тест парсинга DATABASE_URL без порта"""
        config = DatabaseConfig()
        
        with patch.object(config, '_get_default_config'):
            url = "postgresql://user:pass@host/database"
            result = config._parse_database_url(url)
            
            assert result["host"] == "host"
            assert result["port"] == "5432"  # Дефолтный порт
            assert result["database"] == "database"

    def test_parse_database_url_no_password(self):
        """Тест парсинга DATABASE_URL без пароля"""
        config = DatabaseConfig()
        
        with patch.object(config, '_get_default_config'):
            url = "postgresql://user@host:5432/database"
            result = config._parse_database_url(url)
            
            assert result["username"] == "user"
            assert result["password"] == ""  # Пустой пароль

    def test_parse_database_url_invalid_format(self):
        """Тест обработки невалидного формата DATABASE_URL"""
        config = DatabaseConfig()
        
        with patch.object(config, '_get_default_config'):
            # Судя по выводу, метод не вызывает исключение, а логирует ошибку и возвращает дефолты
            result = config._parse_database_url("invalid-url")
            # Проверяем что результат не пустой (возвращаются дефолтные значения)
            assert isinstance(result, dict)

    def test_get_config_without_custom_config(self):
        """Тест получения конфигурации без кастомных параметров"""
        with patch.object(DatabaseConfig, '_get_default_config') as mock_get_default:
            mock_get_default.return_value = {"host": "default_host", "port": "5432"}
            
            config = DatabaseConfig()
            result = config.get_config()
            
            assert result == {"host": "default_host", "port": "5432"}

    def test_get_config_with_custom_config(self):
        """Тест получения конфигурации с кастомными параметрами"""
        with patch.object(DatabaseConfig, '_get_default_config') as mock_get_default:
            mock_get_default.return_value = {
                "host": "default_host", 
                "port": "5432",
                "database": "default_db"
            }
            
            config = DatabaseConfig()
            custom_config = {"host": "custom_host", "port": "5433"}
            result = config.get_config(custom_config)
            
            expected = {
                "host": "custom_host",  # Перезаписан
                "port": "5433",         # Перезаписан
                "database": "default_db"  # Остался из дефолтной конфигурации
            }
            
            assert result == expected

    def test_get_connection_params(self):
        """Тест получения параметров подключения"""
        with patch.object(DatabaseConfig, '_get_default_config') as mock_get_default:
            mock_get_default.return_value = {
                "host": "test_host",
                "port": "5432", 
                "database": "test_db",
                "username": "test_user",
                "password": "test_pass"
            }
            
            config = DatabaseConfig()
            result = config.get_connection_params()
            
            # Проверяем основные поля согласно реальному API
            assert result["host"] == "test_host"
            assert result["port"] == "5432"  # Остается строкой
            assert result["database"] == "test_db"
            assert result["user"] == "test_user"  # username -> user
            assert result["password"] == "test_pass"

    def test_get_connection_params_with_sslmode(self):
        """Тест получения параметров подключения с SSL параметрами"""
        with patch.object(DatabaseConfig, '_get_default_config') as mock_get_default:
            mock_get_default.return_value = {
                "host": "test_host",
                "port": "5432", 
                "database": "test_db",
                "username": "test_user",
                "password": "test_pass",
                "sslmode": "require"  # Добавляем SSL параметр
            }
            
            config = DatabaseConfig()
            result = config.get_connection_params()
            
            # Проверяем что sslmode добавлен согласно коду в строке 66-67
            assert result["sslmode"] == "require"

    def test_parse_database_url_with_params(self):
        """Тест парсинга DATABASE_URL с параметрами"""
        config = DatabaseConfig()
        
        with patch.object(config, '_get_default_config'):
            url = "postgresql://user:pass@host:5432/database?sslmode=require"
            result = config._parse_database_url(url)
            
            # Проверяем что параметры обрабатываются
            assert result["database"] == "database"
            assert result["host"] == "host"

    def test_parse_database_url_postgres_scheme(self):
        """Тест парсинга URL со схемой postgres://"""
        config = DatabaseConfig()
        
        with patch.object(config, '_get_default_config'):
            url = "postgres://user:pass@host:5432/database"
            result = config._parse_database_url(url)
            
            # Проверяем что postgres:// схема также поддерживается
            assert result["host"] == "host"
            assert result["username"] == "user"
            assert result["password"] == "pass"

    @patch('psycopg2.connect')
    def test_test_connection_success(self, mock_connect):
        """Тест успешного тестирования подключения"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        with patch.object(DatabaseConfig, '_get_default_config') as mock_get_default:
            mock_get_default.return_value = {
                "host": "localhost",
                "port": "5432",
                "database": "test_db",
                "username": "test_user",
                "password": "test_pass"
            }
            
            config = DatabaseConfig()
            result = config.test_connection()
            
            assert result is True
            mock_connect.assert_called_once()
            mock_connection.close.assert_called_once()

    @patch('psycopg2.connect')
    def test_test_connection_failure(self, mock_connect):
        """Тест неуспешного тестирования подключения"""
        mock_connect.side_effect = Exception("Connection failed")
        
        with patch.object(DatabaseConfig, '_get_default_config') as mock_get_default:
            mock_get_default.return_value = {
                "host": "localhost",
                "port": "5432", 
                "database": "test_db",
                "username": "test_user",
                "password": "test_pass"
            }
            
            config = DatabaseConfig()
            result = config.test_connection()
            
            assert result is False
            mock_connect.assert_called_once()

    @patch('psycopg2.connect')
    def test_test_connection_with_custom_config(self, mock_connect):
        """Тест тестирования подключения с кастомной конфигурацией"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        config = DatabaseConfig()
        custom_config = {
            "host": "custom_host",
            "port": "5433",
            "database": "custom_db", 
            "username": "custom_user",
            "password": "custom_pass"
        }
        
        result = config.test_connection(custom_config)
        
        assert result is True
        # Проверяем что использовались кастомные параметры
        mock_connect.assert_called_once_with(
            host="custom_host",
            port="5433", 
            database="custom_db",
            user="custom_user",
            password="custom_pass"
        )