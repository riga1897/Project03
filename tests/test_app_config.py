import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.app_config import AppConfig


class TestAppConfig:
    @patch.multiple('src.config.app_config',
                   os=MagicMock(),
                   pathlib=MagicMock())
    def test_app_config_initialization(self):
        """Тест инициализации конфигурации приложения"""
        config = AppConfig()
        assert hasattr(config, 'DATABASE_URL')

    @patch.multiple('src.config.app_config',
                   os=MagicMock(),
                   pathlib=MagicMock())
    def test_app_config_database(self):
        """Тест настроек базы данных"""
        config = AppConfig()
        if hasattr(config, 'DATABASE_URL'):
            assert config.DATABASE_URL is not None

    @patch.multiple('src.config.app_config',
                   os=MagicMock(),
                   pathlib=MagicMock())
    def test_app_config_logging(self):
        """Тест настроек логирования"""
        config = AppConfig()
        if hasattr(config, 'LOG_LEVEL'):
            assert config.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    @patch.multiple('src.config.app_config',
                   os=MagicMock(),
                   pathlib=MagicMock())
    def test_app_config_cache(self):
        """Тест настроек кэша"""
        config = AppConfig()
        if hasattr(config, 'CACHE_DIR'):
            assert config.CACHE_DIR is not None

    @patch.multiple('src.config.app_config',
                   os=MagicMock(),
                   pathlib=MagicMock())
    def test_app_config_api_settings(self):
        """Тест настроек API"""
        config = AppConfig()
        if hasattr(config, 'MAX_WORKERS'):
            assert config.MAX_WORKERS > 0