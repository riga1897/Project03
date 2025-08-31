
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.app_config import AppConfig


class TestAppConfig:
    """Тесты для AppConfig с консолидированными моками"""

    @patch('src.config.app_config.DatabaseConfig')
    @patch('src.config.app_config.UIConfig')
    def test_app_config_initialization(self, mock_ui_config, mock_db_config):
        """Тест инициализации конфигурации приложения"""
        mock_db_instance = Mock()
        mock_ui_instance = Mock()
        mock_db_config.return_value = mock_db_instance
        mock_ui_config.return_value = mock_ui_instance
        
        config = AppConfig()
        assert hasattr(config, 'database')
        assert hasattr(config, 'ui')

    @patch('src.config.app_config.DatabaseConfig')
    @patch('src.config.app_config.UIConfig')
    def test_app_config_database(self, mock_ui_config, mock_db_config):
        """Тест конфигурации базы данных"""
        mock_db_instance = Mock()
        mock_db_instance.to_dict.return_value = {'host': 'localhost'}
        mock_db_config.return_value = mock_db_instance
        mock_ui_config.return_value = Mock()
        
        config = AppConfig()
        db_config = config.get_db_config()
        assert isinstance(db_config, dict)

    @patch('src.config.app_config.DatabaseConfig')
    @patch('src.config.app_config.UIConfig')
    def test_app_config_logging(self, mock_ui_config, mock_db_config):
        """Тест конфигурации логирования"""
        config = AppConfig()
        assert hasattr(config, 'setup_logging')

    @patch('src.config.app_config.DatabaseConfig')
    @patch('src.config.app_config.UIConfig')
    def test_app_config_cache(self, mock_ui_config, mock_db_config):
        """Тест конфигурации кэша"""
        config = AppConfig()
        cache_config = config.get_cache_config()
        assert isinstance(cache_config, dict)

    @patch('src.config.app_config.DatabaseConfig')
    @patch('src.config.app_config.UIConfig')
    def test_app_config_api_settings(self, mock_ui_config, mock_db_config):
        """Тест настроек API"""
        config = AppConfig()
        api_settings = config.get_api_settings()
        assert isinstance(api_settings, dict)
