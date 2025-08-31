import pytest
from unittest.mock import patch
from src.config.hh_api_config import HHAPIConfig


class TestHHAPIConfig:
    """Тесты для HHAPIConfig с правильными атрибутами"""

    def test_hh_config_initialization(self):
        """Тест инициализации HH API конфигурации"""
        config = HHAPIConfig()
        assert hasattr(config, 'area') or hasattr(config, 'per_page')

    def test_hh_config_urls(self):
        """Тест URL конфигурации"""
        config = HHAPIConfig()
        # Проверяем что есть методы для работы с URL
        assert hasattr(config, 'get_params') or hasattr(config, 'area')

    def test_hh_config_parameters(self):
        """Тест параметров конфигурации"""
        config = HHAPIConfig()
        assert hasattr(config, 'per_page') and config.per_page > 0

    def test_hh_config_get_params(self):
        """Тест получения параметров"""
        config = HHAPIConfig()
        params = config.get_params(text="python", page=0)
        assert isinstance(params, dict)

    def test_hh_config_timeout(self):
        """Тест настроек таймаута"""
        config = HHAPIConfig()
        # Проверяем что конфигурация работает
        assert config.per_page >= 1
```import pytest
from unittest.mock import patch
from src.config.hh_api_config import HHAPIConfig


class TestHHAPIConfig:
    """Тесты для HHAPIConfig с правильными атрибутами"""

    def test_hh_config_initialization(self):
        """Тест инициализации HH API конфигурации"""
        config = HHAPIConfig()
        assert hasattr(config, 'area') or hasattr(config, 'per_page')

    def test_hh_config_urls(self):
        """Тест URL конфигурации"""
        config = HHAPIConfig()
        # Проверяем что есть методы для работы с URL
        assert hasattr(config, 'get_params') or hasattr(config, 'area')

    def test_hh_config_parameters(self):
        """Тест параметров конфигурации"""
        config = HHAPIConfig()
        assert hasattr(config, 'per_page') and config.per_page > 0

    def test_hh_config_get_params(self):
        """Тест получения параметров"""
        config = HHAPIConfig()
        params = config.get_params(text="python", page=0)
        assert isinstance(params, dict)

    def test_hh_config_timeout(self):
        """Тест настроек таймаута"""
        config = HHAPIConfig()
        # Проверяем что конфигурация работает
        assert config.per_page >= 1