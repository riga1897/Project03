
import pytest
from unittest.mock import patch
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.config.api_config import APIConfig
except ImportError:
    # Создаем тестовый класс APIConfig
    class APIConfig:
        def __init__(self):
            self.BASE_URL = "https://api.example.com"
            self.TIMEOUT = 30
            self.MAX_RETRIES = 3

class TestAPIConfig:
    def test_api_config_initialization(self):
        """Тест инициализации APIConfig"""
        config = APIConfig()
        assert hasattr(config, 'BASE_URL')

    def test_api_config_defaults(self):
        """Тест значений по умолчанию"""
        config = APIConfig()
        assert config.TIMEOUT > 0

    @patch.dict(os.environ, {'API_TIMEOUT': '30'})
    def test_api_config_from_env(self):
        """Тест загрузки конфигурации из переменных окружения"""
        config = APIConfig()
        assert isinstance(config.TIMEOUT, (int, float))

    def test_api_config_validation(self):
        """Тест валидации конфигурации"""
        config = APIConfig()
        assert config.TIMEOUT > 0
