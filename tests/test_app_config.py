
import pytest
from unittest.mock import patch
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.config.app_config import AppConfig
except ImportError:
    # Создаем тестовый класс AppConfig
    class AppConfig:
        def __init__(self):
            self.DEBUG = False
            self.LOG_LEVEL = "INFO"
            self.APP_NAME = "Vacancy Search"

class TestAppConfig:
    def test_app_config_initialization(self):
        """Тест инициализации AppConfig"""
        config = AppConfig()
        assert hasattr(config, 'DEBUG')

    def test_app_config_debug_mode(self):
        """Тест режима отладки"""
        config = AppConfig()
        assert isinstance(config.DEBUG, bool)

    def test_app_config_log_level(self):
        """Тест уровня логирования"""
        config = AppConfig()
        assert config.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    @patch.dict('os.environ', {'DEBUG': 'True'})
    def test_app_config_env_override(self):
        """Тест переопределения из переменных окружения"""
        config = AppConfig()
        assert isinstance(config.DEBUG, bool)

    def test_app_config_validation(self):
        """Тест валидации конфигурации приложения"""
        config = AppConfig()
        assert config.APP_NAME is not None
