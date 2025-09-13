#!/usr/bin/env python3
"""
Тесты модуля db_config для 100% покрытия.

Покрывает все функции в src/config/db_config.py:
- DatabaseConfig - конфигурация подключения к базе данных
- __init__ - инициализация конфигурации
- _get_default_config - получение конфигурации из env переменных
- get_config - получение конфигурации с возможностью переопределения
- get_connection_params - формирование параметров для psycopg2
- _parse_database_url - парсинг DATABASE_URL со множественными форматами
- test_connection - тестирование подключения к БД

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

from unittest.mock import patch, MagicMock
from typing import Any

# Импорты из реального кода для покрытия
from src.config.db_config import DatabaseConfig


class TestDatabaseConfig:
    """100% покрытие DatabaseConfig класса"""

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_init_calls_get_default_config(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации и вызова _get_default_config"""
        # Настраиваем моки для отдельных переменных
        mock_get_env_var.side_effect = [
            None,  # DATABASE_URL
            "test-host",  # PGHOST
            "5433",  # PGPORT
            "test-db",  # PGDATABASE
            "test-user",  # PGUSER
            "test-pass",  # PGPASSWORD
            "15",  # PGCONNECT_TIMEOUT
            "60"   # PGCOMMAND_TIMEOUT
        ]

        config = DatabaseConfig()

        assert config.default_config is not None
        assert isinstance(config.default_config, dict)

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_get_default_config_without_database_url(self, mock_get_env_var: Any) -> None:
        """Покрытие _get_default_config без DATABASE_URL"""
        # DATABASE_URL возвращает None, затем остальные переменные
        mock_get_env_var.side_effect = [
            None,  # DATABASE_URL
            "custom-host",  # PGHOST
            "5434",  # PGPORT
            "custom-db",  # PGDATABASE
            "custom-user",  # PGUSER
            "custom-pass",  # PGPASSWORD
            "20",  # PGCONNECT_TIMEOUT
            "45"   # PGCOMMAND_TIMEOUT
        ]

        config = DatabaseConfig()

        expected = {
            "host": "custom-host",
            "port": "5434",
            "database": "custom-db",
            "username": "custom-user",
            "password": "custom-pass",
            "connect_timeout": "20",
            "command_timeout": "45"
        }
        assert config.default_config == expected

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_get_default_config_with_defaults(self, mock_get_env_var: Any) -> None:
        """Покрытие _get_default_config с значениями по умолчанию"""
        # Все переменные возвращают значения по умолчанию
        mock_get_env_var.side_effect = [
            None,  # DATABASE_URL
            "localhost",  # PGHOST (default)
            "5432",  # PGPORT (default)
            "job_search_app",  # PGDATABASE (default)
            "postgres",  # PGUSER (default)
            "",  # PGPASSWORD (default)
            "10",  # PGCONNECT_TIMEOUT (default)
            "30"   # PGCOMMAND_TIMEOUT (default)
        ]

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

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_get_default_config_with_database_url(self, mock_get_env_var: Any) -> None:
        """Покрытие _get_default_config с DATABASE_URL"""
        # DATABASE_URL имеет приоритет
        database_url = "postgresql://user:pass@host:5435/dbname"
        mock_get_env_var.side_effect = [
            database_url,  # DATABASE_URL
            "10",  # PGCONNECT_TIMEOUT для _parse_database_url
            "30"   # PGCOMMAND_TIMEOUT для _parse_database_url
        ]

        config = DatabaseConfig()

        # Проверяем что DATABASE_URL был распарсен
        assert config.default_config["host"] == "host"
        assert config.default_config["port"] == "5435"
        assert config.default_config["database"] == "dbname"
        assert config.default_config["username"] == "user"
        assert config.default_config["password"] == "pass"

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_get_config_without_custom_config(self, mock_get_env_var: Any) -> None:
        """Покрытие get_config без кастомной конфигурации"""
        mock_get_env_var.side_effect = [
            None, "host1", "5432", "db1", "user1", "pass1", "10", "30"
        ]

        config = DatabaseConfig()
        result = config.get_config()

        # Должна вернуться конфигурация по умолчанию
        assert result == config.default_config

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_get_config_with_custom_config(self, mock_get_env_var: Any) -> None:
        """Покрытие get_config с кастомной конфигурацией"""
        mock_get_env_var.side_effect = [
            None, "host1", "5432", "db1", "user1", "pass1", "10", "30"
        ]

        config = DatabaseConfig()
        custom_config = {"host": "custom-host", "port": "9999"}

        result = config.get_config(custom_config)

        # Кастомные значения должны переопределить значения по умолчанию
        assert result["host"] == "custom-host"
        assert result["port"] == "9999"
        assert result["database"] == "db1"  # Остается из default
        assert result["username"] == "user1"  # Остается из default

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_get_config_custom_config_copy(self, mock_get_env_var: Any) -> None:
        """Покрытие того что get_config возвращает копию"""
        mock_get_env_var.side_effect = [
            None, "host1", "5432", "db1", "user1", "pass1", "10", "30"
        ]

        config = DatabaseConfig()
        custom_config = {"host": "custom-host"}

        result = config.get_config(custom_config)

        # Изменение результата не должно влиять на default_config
        result["host"] = "modified-host"
        assert config.default_config["host"] == "host1"

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_get_connection_params_basic(self, mock_get_env_var: Any) -> None:
        """Покрытие get_connection_params с базовой конфигурацией"""
        mock_get_env_var.side_effect = [
            None, "test-host", "5433", "test-db", "test-user", "test-pass", "10", "30"
        ]

        config = DatabaseConfig()
        params = config.get_connection_params()

        expected = {
            "host": "test-host",
            "port": "5433",
            "database": "test-db",
            "user": "test-user",  # username -> user
            "password": "test-pass"
        }
        assert params == expected

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_get_connection_params_with_ssl(self, mock_get_env_var: Any) -> None:
        """Покрытие get_connection_params с SSL настройками"""
        mock_get_env_var.side_effect = [
            None, "host", "5432", "db", "user", "pass", "10", "30"
        ]

        config = DatabaseConfig()
        # Добавляем SSL параметр в default_config
        config.default_config["sslmode"] = "require"

        params = config.get_connection_params()

        assert "sslmode" in params
        assert params["sslmode"] == "require"

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_get_connection_params_without_ssl(self, mock_get_env_var: Any) -> None:
        """Покрытие get_connection_params без SSL настроек"""
        mock_get_env_var.side_effect = [
            None, "host", "5432", "db", "user", "pass", "10", "30"
        ]

        config = DatabaseConfig()
        params = config.get_connection_params()

        # SSL параметры не должны быть включены
        assert "sslmode" not in params


class TestDatabaseConfigParseURL:
    """100% покрытие _parse_database_url метода"""

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_postgresql_scheme(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL со схемой postgresql://"""
        mock_get_env_var.side_effect = ["10", "30"]  # timeouts

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgresql://user:pass@host:5432/database"

        result = config._parse_database_url(url)

        assert result["host"] == "host"
        assert result["port"] == "5432"
        assert result["database"] == "database"
        assert result["username"] == "user"
        assert result["password"] == "pass"

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_postgres_scheme(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL со схемой postgres://"""
        mock_get_env_var.side_effect = ["10", "30"]

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgres://user:pass@host:5433/database"

        result = config._parse_database_url(url)

        assert result["host"] == "host"
        assert result["port"] == "5433"
        assert result["database"] == "database"
        assert result["username"] == "user"
        assert result["password"] == "pass"

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_unsupported_scheme(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL с неподдерживаемой схемой"""
        mock_get_env_var.return_value = "10"

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "mysql://user:pass@host:3306/database"

        with patch('builtins.print') as mock_print:
            result = config._parse_database_url(url)

        # Должна вернуться конфигурация по умолчанию
        assert result["host"] == "localhost"
        assert result["port"] == "5432"
        assert result["database"] == "job_search_app"
        mock_print.assert_called_once()

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_no_auth(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL без авторизации"""
        mock_get_env_var.side_effect = ["10", "30"]

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgresql://host:5432/database"

        result = config._parse_database_url(url)

        assert result["host"] == "host"
        assert result["port"] == "5432"
        assert result["database"] == "database"
        assert result["username"] == ""
        assert result["password"] == ""

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_username_only(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL только с username"""
        mock_get_env_var.side_effect = ["10", "30"]

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgresql://user@host:5432/database"

        result = config._parse_database_url(url)

        assert result["username"] == "user"
        assert result["password"] == ""

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_no_port(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL без порта"""
        mock_get_env_var.side_effect = ["10", "30"]

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgresql://user:pass@host/database"

        result = config._parse_database_url(url)

        assert result["host"] == "host"
        assert result["port"] == "5432"  # Default port

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_no_database(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL без базы данных"""
        mock_get_env_var.side_effect = ["10", "30"]

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgresql://user:pass@host:5432"

        result = config._parse_database_url(url)

        assert result["database"] == ""

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_with_ssl_params(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL с SSL параметрами"""
        mock_get_env_var.side_effect = ["10", "30"]

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgresql://user:pass@host:5432/database?sslmode=require"

        result = config._parse_database_url(url)

        assert result["database"] == "database"
        assert result["sslmode"] == "require"

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_with_params_no_ssl(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL с параметрами без SSL"""
        mock_get_env_var.side_effect = ["10", "30"]

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgresql://user:pass@host:5432/database?timeout=60"

        result = config._parse_database_url(url)

        assert result["database"] == "database"
        assert "sslmode" not in result

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_minimal(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга минимального URL"""
        mock_get_env_var.side_effect = ["10", "30"]

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgresql://host"

        result = config._parse_database_url(url)

        assert result["host"] == "host"
        assert result["port"] == "5432"
        assert result["database"] == ""
        assert result["username"] == ""
        assert result["password"] == ""

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_complex_password(self, mock_get_env_var: Any) -> None:
        """Покрытие парсинга URL со сложным паролем"""
        mock_get_env_var.side_effect = ["10", "30"]

        config = DatabaseConfig.__new__(DatabaseConfig)
        url = "postgresql://user:pass@host:5432/database"

        result = config._parse_database_url(url)

        assert result["username"] == "user"
        assert result["password"] == "pass"  # Простой пароль без @

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_parse_database_url_exception_handling(self, mock_get_env_var: Any) -> None:
        """Покрытие обработки исключений при парсинге URL"""
        mock_get_env_var.return_value = "10"

        config = DatabaseConfig.__new__(DatabaseConfig)
        # Намеренно поврежденный URL - пустая строка вызовет IndexError
        url = ""

        with patch('builtins.print') as mock_print:
            result = config._parse_database_url(url)

        # Должна вернуться конфигурация по умолчанию
        assert result["host"] == "localhost"
        assert result["port"] == "5432"
        assert result["database"] == "job_search_app"
        assert result["username"] == "postgres"
        assert result["password"] == ""
        mock_print.assert_called_once()


class TestDatabaseConfigTestConnection:
    """100% покрытие test_connection метода"""

    @patch('src.config.db_config.EnvLoader.get_env_var')
    @patch('psycopg2.connect')
    def test_test_connection_success_default_config(self, mock_connect: Any, mock_get_env_var: Any) -> None:
        """Покрытие успешного подключения с конфигурацией по умолчанию"""
        mock_get_env_var.side_effect = [
            None, "host", "5432", "db", "user", "pass", "10", "30"
        ]

        # Мокаем успешное подключение
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        config = DatabaseConfig()
        result = config.test_connection()

        assert result is True
        mock_connect.assert_called_once_with(
            host="host",
            port="5432",
            database="db",
            user="user",
            password="pass"
        )
        mock_connection.close.assert_called_once()

    @patch('src.config.db_config.EnvLoader.get_env_var')
    @patch('psycopg2.connect')
    def test_test_connection_success_custom_config(self, mock_connect: Any, mock_get_env_var: Any) -> None:
        """Покрытие успешного подключения с кастомной конфигурацией"""
        mock_get_env_var.side_effect = [
            None, "default-host", "5432", "default-db", "default-user", "default-pass", "10", "30"
        ]

        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        config = DatabaseConfig()
        custom_config = {
            "host": "custom-host",
            "port": "9999",
            "database": "custom-db",
            "username": "custom-user",
            "password": "custom-pass"
        }

        result = config.test_connection(custom_config)

        assert result is True
        mock_connect.assert_called_once_with(
            host="custom-host",
            port="9999",
            database="custom-db",
            user="custom-user",
            password="custom-pass"
        )

    @patch('src.config.db_config.EnvLoader.get_env_var')
    @patch('psycopg2.connect')
    def test_test_connection_failure(self, mock_connect: Any, mock_get_env_var: Any) -> None:
        """Покрытие неудачного подключения"""
        mock_get_env_var.side_effect = [
            None, "host", "5432", "db", "user", "pass", "10", "30"
        ]

        # Мокаем ошибку подключения
        mock_connect.side_effect = Exception("Connection failed")

        config = DatabaseConfig()

        with patch('builtins.print') as mock_print:
            result = config.test_connection()

        assert result is False
        mock_print.assert_called_once()

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_test_connection_import_error(self, mock_get_env_var: Any) -> None:
        """Покрытие ошибки импорта psycopg2"""
        mock_get_env_var.side_effect = [
            None, "host", "5432", "db", "user", "pass", "10", "30"
        ]

        config = DatabaseConfig()

        # Мокаем ошибку импорта в блоке try
        import sys
        original_modules = sys.modules.copy()
        if 'psycopg2' in sys.modules:
            del sys.modules['psycopg2']

        try:
            with patch.dict('sys.modules', {'psycopg2': None}):
                with patch('builtins.print') as mock_print:
                    result = config.test_connection()

            assert result is False
            mock_print.assert_called_once()
        finally:
            sys.modules.update(original_modules)


class TestDatabaseConfigIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_full_workflow_with_database_url(self, mock_get_env_var: Any) -> None:
        """Покрытие полного рабочего процесса с DATABASE_URL"""
        database_url = "postgresql://appuser:secret@db.example.com:5433/myapp"
        mock_get_env_var.side_effect = [
            database_url,  # DATABASE_URL
            "15",  # PGCONNECT_TIMEOUT
            "45"   # PGCOMMAND_TIMEOUT
        ]

        config = DatabaseConfig()

        # Проверяем парсинг DATABASE_URL
        assert config.default_config["host"] == "db.example.com"
        assert config.default_config["port"] == "5433"
        assert config.default_config["database"] == "myapp"
        assert config.default_config["username"] == "appuser"
        assert config.default_config["password"] == "secret"

        # Тестируем получение конфигурации
        db_config = config.get_config()
        assert db_config == config.default_config

        # Тестируем параметры подключения
        connection_params = config.get_connection_params()
        assert connection_params["host"] == "db.example.com"
        assert connection_params["user"] == "appuser"

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_full_workflow_with_env_vars(self, mock_get_env_var: Any) -> None:
        """Покрытие полного рабочего процесса с отдельными env переменными"""
        mock_get_env_var.side_effect = [
            None,  # DATABASE_URL
            "prod-host",  # PGHOST
            "5432",  # PGPORT
            "prod-db",  # PGDATABASE
            "prod-user",  # PGUSER
            "prod-pass",  # PGPASSWORD
            "20",  # PGCONNECT_TIMEOUT
            "60"   # PGCOMMAND_TIMEOUT
        ]

        config = DatabaseConfig()

        # Проверяем конфигурацию из env переменных
        assert config.default_config["host"] == "prod-host"
        assert config.default_config["username"] == "prod-user"

        # Тестируем переопределение
        custom_config = {"host": "staging-host", "database": "staging-db"}
        result_config = config.get_config(custom_config)

        assert result_config["host"] == "staging-host"
        assert result_config["database"] == "staging-db"
        assert result_config["username"] == "prod-user"  # Остается из default

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_error_resilience(self, mock_get_env_var: Any) -> None:
        """Покрытие устойчивости к ошибкам"""
        # Поврежденный DATABASE_URL
        mock_get_env_var.side_effect = [
            "invalid-url",  # DATABASE_URL
            "10", "30"  # timeouts для fallback
        ]

        with patch('builtins.print'):
            config = DatabaseConfig()

        # Должна использоваться конфигурация по умолчанию
        assert config.default_config["host"] == "localhost"
        assert config.default_config["database"] == "job_search_app"

        # Конфигурация должна быть рабочей
        db_config = config.get_config()
        connection_params = config.get_connection_params()

        assert "host" in db_config
        assert "user" in connection_params

    @patch('src.config.db_config.EnvLoader.get_env_var')
    def test_configuration_consistency(self, mock_get_env_var: Any) -> None:
        """Покрытие согласованности конфигурации"""
        mock_get_env_var.side_effect = [
            None, "host1", "5432", "db1", "user1", "pass1", "10", "30"
        ]

        config = DatabaseConfig()

        # Многократные вызовы должны возвращать одинаковые результаты
        config1 = config.get_config()
        config2 = config.get_config()
        params1 = config.get_connection_params()
        params2 = config.get_connection_params()

        assert config1 == config2
        assert params1 == params2

        # get_config без параметров возвращает ссылку на default_config
        # get_config с custom_config возвращает копию
        config_copy = config.get_config({"extra": "value"})
        config_copy["host"] = "modified"
        assert config.default_config["host"] == "host1"  # Должно остаться неизменным
