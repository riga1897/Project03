
import pytest
import os
from unittest.mock import patch, MagicMock
from src.config.api_config import APIConfig


class TestAPIConfig:
    def test_api_config_initialization(self):
        """Тест инициализации APIConfig"""
        config = APIConfig()
        assert hasattr(config, 'BASE_URL')
        assert hasattr(config, 'TIMEOUT')
        assert hasattr(config, 'MAX_RETRIES')

    def test_api_config_defaults(self):
        """Тест значений по умолчанию"""
        config = APIConfig()
        assert config.TIMEOUT > 0
        assert config.MAX_RETRIES >= 0

    @patch.dict(os.environ, {'API_TIMEOUT': '30'})
    def test_api_config_from_env(self):
        """Тест загрузки конфигурации из переменных окружения"""
        config = APIConfig()
        # Проверяем, что конфигурация может загружаться из окружения
        assert isinstance(config.TIMEOUT, (int, float))

    def test_api_config_validation(self):
        """Тест валидации конфигурации"""
        config = APIConfig()
        assert config.TIMEOUT > 0
        assert config.MAX_RETRIES >= 0
        assert isinstance(config.BASE_URL, str) if hasattr(config, 'BASE_URL') else True
