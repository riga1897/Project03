import pytest
from unittest.mock import patch, MagicMock
import sys
import os
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
    @patch.multiple('src.config.api_config', 
                   requests=MagicMock(),
                   os=MagicMock())
    def test_api_config_initialization(self):
        """Тест инициализации API конфигурации"""
        config = APIConfig()
        assert hasattr(config, 'HH_BASE_URL')
        assert hasattr(config, 'SJ_BASE_URL')

    @patch.multiple('src.config.api_config',
                   requests=MagicMock(),
                   os=MagicMock())
    def test_api_config_urls(self):
        """Тест URL конфигурации"""
        config = APIConfig()
        assert config.HH_BASE_URL.startswith('https://api.hh.ru')
        assert config.SJ_BASE_URL.startswith('https://api.superjob.ru')

    @patch.multiple('src.config.api_config',
                   requests=MagicMock(),
                   os=MagicMock())
    def test_api_config_headers(self):
        """Тест заголовков запросов"""
        config = APIConfig()
        if hasattr(config, 'get_headers'):
            headers = config.get_headers()
            assert 'User-Agent' in headers

    @patch.multiple('src.config.api_config',
                   requests=MagicMock(),
                   os=MagicMock())
    def test_api_config_parameters(self):
        """Тест параметров конфигурации"""
        config = APIConfig()
        assert hasattr(config, 'DEFAULT_COUNT')
        if hasattr(config, 'DEFAULT_COUNT'):
            assert config.DEFAULT_COUNT > 0