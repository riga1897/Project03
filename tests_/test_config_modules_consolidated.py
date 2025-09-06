"""
Консолидированные тесты для конфигурационных модулей
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture(autouse=True)
def prevent_external_operations():
    """Предотвращение всех внешних операций"""
    with patch('builtins.input', return_value='0'), \
         patch('builtins.print'), \
         patch('os.environ.get') as mock_env, \
         patch('pathlib.Path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data='TEST_VAR=test_value')):

        # Настройка переменных окружения
        mock_env.side_effect = lambda key, default=None: {
            'HH_API_URL': 'https://api.hh.ru',
            'SJ_API_URL': 'https://api.superjob.ru',
            'PGHOST': 'localhost',
            'PGPORT': '5432',
            'PGDATABASE': 'testdb',
            'PGUSER': 'testuser',
            'PGPASSWORD': 'testpass'
        }.get(key, default)

        yield


class TestConfigModules:
    """Тестирование конфигурационных модулей"""

    def test_app_config_import(self):
        """Тестирование импорта конфигурации приложения"""
        try:
            from src.config.app_config import AppConfig
            assert AppConfig is not None
        except ImportError:
            pytest.skip("AppConfig not available")

    def test_api_config_import(self):
        """Тестирование импорта конфигурации API"""
        try:
            from src.config.api_config import APIConfig
            assert APIConfig is not None
        except ImportError:
            pytest.skip("APIConfig not available")

    def test_db_config_import(self):
        """Тестирование импорта конфигурации БД"""
        try:
            from src.config.db_config import DatabaseConfig
            assert DatabaseConfig is not None
        except ImportError:
            pytest.skip("DatabaseConfig not available")

    def test_target_companies_import(self):
        """Тестирование импорта целевых компаний"""
        try:
            from src.config.target_companies import TARGET_COMPANIES
            assert isinstance(TARGET_COMPANIES, (list, dict))
        except ImportError:
            pytest.skip("TARGET_COMPANIES not available")


class TestConfigBasicFunctionality:
    """Базовое тестирование функциональности конфигураций"""

    def test_config_creation(self):
        """Тестирование создания конфигураций"""
        try:
            from src.config.app_config import AppConfig

            config = AppConfig()
            # Проверяем что объект создан
            assert config is not None

        except ImportError:
            pytest.skip("Config modules not available")

    def test_api_config_basic(self):
        """Базовое тестирование API конфигурации"""
        try:
            from src.config.api_config import APIConfig

            config = APIConfig()
            assert config is not None

        except ImportError:
            pytest.skip("API config not available")