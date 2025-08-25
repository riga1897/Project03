
"""
Тесты для конфигурационных модулей
"""

import pytest
import os
from unittest.mock import patch, Mock
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
        assert 'host' in db_config
        assert 'port' in db_config
        assert 'database' in db_config
        assert 'username' in db_config
        assert 'password' in db_config

    @patch.dict(os.environ, {
        'PGHOST': 'test_host',
        'PGPORT': '5433',
        'PGDATABASE': 'test_db',
        'PGUSER': 'test_user',
        'PGPASSWORD': 'test_pass'
    })
    def test_db_config_from_env(self):
        """Тест получения конфигурации БД из переменных окружения"""
        config = AppConfig()
        db_config = config.get_db_config()
        
        assert db_config['host'] == 'test_host'
        assert db_config['port'] == '5433'
        assert db_config['database'] == 'test_db'
        assert db_config['username'] == 'test_user'
        assert db_config['password'] == 'test_pass'


class TestDatabaseConfig:
    """Тесты для DatabaseConfig"""

    def test_default_initialization(self):
        """Тест инициализации по умолчанию"""
        config = DatabaseConfig()
        
        assert config.host == 'localhost'
        assert config.port == '5432'
        assert config.database == 'Project03'
        assert config.username == 'postgres'
        assert config.password == ''

    @patch.dict(os.environ, {
        'PGHOST': 'custom_host',
        'PGPORT': '5433',
        'PGDATABASE': 'custom_db',
        'PGUSER': 'custom_user',
        'PGPASSWORD': 'custom_pass'
    })
    def test_initialization_with_env(self):
        """Тест инициализации с переменными окружения"""
        config = DatabaseConfig()
        
        assert config.host == 'custom_host'
        assert config.port == '5433'
        assert config.database == 'custom_db'
        assert config.username == 'custom_user'
        assert config.password == 'custom_pass'

    def test_get_connection_params(self):
        """Тест получения параметров подключения"""
        config = DatabaseConfig()
        params = config.get_connection_params()
        
        expected_keys = {'host', 'port', 'database', 'user', 'password'}
        assert set(params.keys()) == expected_keys
        
        assert params['host'] == config.host
        assert params['port'] == config.port
        assert params['database'] == config.database
        assert params['user'] == config.username
        assert params['password'] == config.password

    def test_get_dsn(self):
        """Тест получения DSN строки"""
        config = DatabaseConfig()
        dsn = config.get_dsn()
        
        assert isinstance(dsn, str)
        assert config.host in dsn
        assert config.port in dsn
        assert config.database in dsn
        assert config.username in dsn

    @patch('src.config.db_config.psycopg2.connect')
    def test_test_connection_success(self, mock_connect):
        """Тест успешной проверки подключения"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        config = DatabaseConfig()
        result = config.test_connection()
        
        assert result is True
        mock_connect.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('src.config.db_config.psycopg2.connect')
    def test_test_connection_failure(self, mock_connect):
        """Тест неудачной проверки подключения"""
        mock_connect.side_effect = Exception("Connection failed")
        
        config = DatabaseConfig()
        result = config.test_connection()
        
        assert result is False


class TestHHAPIConfig:
    """Тесты для HHAPIConfig"""

    def test_initialization(self):
        """Тест инициализации конфигурации HH API"""
        config = HHAPIConfig()
        
        assert config.base_url == "https://api.hh.ru"
        assert config.vacancies_endpoint == "/vacancies"
        assert config.employers_endpoint == "/employers"
        assert config.areas_endpoint == "/areas"
        assert config.user_agent.startswith("VacancySearchApp")

    def test_get_headers(self):
        """Тест получения заголовков"""
        config = HHAPIConfig()
        headers = config.get_headers()
        
        assert isinstance(headers, dict)
        assert 'User-Agent' in headers
        assert headers['User-Agent'] == config.user_agent

    def test_get_vacancies_url(self):
        """Тест получения URL для вакансий"""
        config = HHAPIConfig()
        url = config.get_vacancies_url()
        
        assert url == "https://api.hh.ru/vacancies"

    def test_get_employers_url(self):
        """Тест получения URL для работодателей"""
        config = HHAPIConfig()
        url = config.get_employers_url()
        
        assert url == "https://api.hh.ru/employers"

    def test_get_areas_url(self):
        """Тест получения URL для регионов"""
        config = HHAPIConfig()
        url = config.get_areas_url()
        
        assert url == "https://api.hh.ru/areas"

    def test_get_request_params(self):
        """Тест получения базовых параметров запроса"""
        config = HHAPIConfig()
        params = config.get_request_params()
        
        assert isinstance(params, dict)
        assert 'per_page' in params
        assert params['per_page'] == 100


class TestSJAPIConfig:
    """Тесты для SJAPIConfig"""

    def test_initialization(self):
        """Тест инициализации конфигурации SJ API"""
        config = SJAPIConfig()
        
        assert config.base_url == "https://api.superjob.ru/2.0"
        assert config.vacancies_endpoint == "/vacancies"
        assert config.default_secret_key == ""

    @patch.dict(os.environ, {'SJ_SECRET_KEY': 'test_secret_key'})
    def test_initialization_with_secret_key(self):
        """Тест инициализации с секретным ключом из окружения"""
        config = SJAPIConfig()
        
        assert config.secret_key == 'test_secret_key'

    def test_get_headers_without_key(self):
        """Тест получения заголовков без ключа"""
        config = SJAPIConfig()
        config.secret_key = ""
        
        headers = config.get_headers()
        
        assert isinstance(headers, dict)
        assert 'X-Api-App-Id' not in headers

    def test_get_headers_with_key(self):
        """Тест получения заголовков с ключом"""
        config = SJAPIConfig()
        config.secret_key = "test_key"
        
        headers = config.get_headers()
        
        assert isinstance(headers, dict)
        assert 'X-Api-App-Id' in headers
        assert headers['X-Api-App-Id'] == "test_key"

    def test_get_vacancies_url(self):
        """Тест получения URL для вакансий"""
        config = SJAPIConfig()
        url = config.get_vacancies_url()
        
        assert url == "https://api.superjob.ru/2.0/vacancies"

    def test_set_secret_key(self):
        """Тест установки секретного ключа"""
        config = SJAPIConfig()
        config.set_secret_key("new_secret_key")
        
        assert config.secret_key == "new_secret_key"

    def test_is_configured(self):
        """Тест проверки конфигурации"""
        config = SJAPIConfig()
        
        # Без ключа
        config.secret_key = ""
        assert config.is_configured() is False
        
        # С ключом
        config.secret_key = "test_key"
        assert config.is_configured() is True

    def test_get_request_params(self):
        """Тест получения базовых параметров запроса"""
        config = SJAPIConfig()
        params = config.get_request_params()
        
        assert isinstance(params, dict)
        assert 'count' in params
        assert params['count'] == 100
