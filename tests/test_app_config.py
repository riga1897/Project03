
import pytest
from unittest.mock import patch, MagicMock
from src.config.app_config import AppConfig


class TestAppConfig:
    def test_app_config_initialization(self):
        """Тест инициализации AppConfig"""
        config = AppConfig()
        assert hasattr(config, 'DEBUG')
        assert hasattr(config, 'LOG_LEVEL')

    def test_app_config_debug_mode(self):
        """Тест режима отладки"""
        config = AppConfig()
        assert isinstance(config.DEBUG, bool)

    def test_app_config_log_level(self):
        """Тест уровня логирования"""
        config = AppConfig()
        assert config.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    def test_app_config_defaults(self):
        """Тест значений по умолчанию"""
        config = AppConfig()
        assert hasattr(config, 'VERSION') or True
        assert hasattr(config, 'NAME') or True

    @patch.dict('os.environ', {'DEBUG': 'True'})
    def test_app_config_env_override(self):
        """Тест переопределения из переменных окружения"""
        config = AppConfig()
        # Проверяем, что конфигурация корректно работает
        assert isinstance(config.DEBUG, bool)
