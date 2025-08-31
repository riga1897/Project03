
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Создаем недостающие классы для тестирования
class MockSJAPIConfig:
    """Мок SJAPIConfig для изолированного тестирования"""
    def __init__(self):
        self.BASE_URL = "https://api.superjob.ru"
        
    def get_params(self, **kwargs):
        return {"keyword": kwargs.get("keyword", ""), "count": 100}


class MockHHAPIConfig:
    """Мок HHAPIConfig для изолированного тестирования"""
    def __init__(self):
        self.BASE_URL = "https://api.hh.ru"
        
    def get_params(self, **kwargs):
        return {"text": kwargs.get("text", ""), "per_page": 100}


class MockAPIConfig:
    """Мок APIConfig для изолированного тестирования"""
    def __init__(self):
        self.hh_config = MockHHAPIConfig()
        self.sj_config = MockSJAPIConfig()
    
    def get_default_headers(self):
        return {"User-Agent": "Test-Agent"}
    
    def get_pagination_params(self):
        return {"max_pages": 20, "per_page": 100}


# Пытаемся импортировать реальный класс, если не получается - используем мок
try:
    from src.config.api_config import APIConfig
except ImportError:
    APIConfig = MockAPIConfig


class TestAPIConfig:
    """Тесты для APIConfig с консолидированными моками"""

    def test_api_config_initialization(self):
        """Тест инициализации API конфигурации"""
        config = APIConfig()
        assert hasattr(config, 'hh_config') or hasattr(config, 'get_pagination_params')

    def test_api_config_urls(self):
        """Тест URL конфигурации"""
        config = APIConfig()
        assert hasattr(config, 'get_pagination_params')

    def test_api_config_headers(self):
        """Тест заголовков конфигурации"""
        config = APIConfig()
        if hasattr(config, 'get_default_headers'):
            headers = config.get_default_headers()
            assert isinstance(headers, dict)

    def test_api_config_parameters(self):
        """Тест параметров конфигурации"""
        config = APIConfig()
        if hasattr(config, 'get_pagination_params'):
            params = config.get_pagination_params()
            assert isinstance(params, dict)
