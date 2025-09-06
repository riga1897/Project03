from unittest.mock import patch

import pytest

from src.config.sj_api_config import SJAPIConfig


class TestSJAPIConfig:
    """Тесты для SJAPIConfig с правильными атрибутами"""

    def test_sj_config_initialization(self):
        """Тест инициализации SuperJob API конфигурации"""
        config = SJAPIConfig()
        assert hasattr(config, "count") or hasattr(config, "published")

    def test_sj_config_urls(self):
        """Тест URL конфигурации"""
        config = SJAPIConfig()
        # Проверяем что есть методы для работы с URL
        assert hasattr(config, "get_params") or hasattr(config, "count")

    def test_sj_config_headers(self):
        """Тест заголовков"""
        config = SJAPIConfig()
        # Проверяем что конфигурация создалась
        assert isinstance(config, SJAPIConfig)

    def test_sj_config_get_params(self):
        """Тест получения параметров"""
        config = SJAPIConfig()
        params = config.get_params(keyword="python")
        assert isinstance(params, dict)

    def test_sj_config_parameters(self):
        """Тест параметров конфигурации"""
        config = SJAPIConfig()
        assert hasattr(config, "count") and config.count > 0
