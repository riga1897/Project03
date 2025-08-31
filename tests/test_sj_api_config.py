
import pytest
from unittest.mock import patch
from src.config.sj_api_config import SJAPIConfig


class TestSJAPIConfig:
    def test_sj_config_initialization(self):
        """Тест инициализации SuperJob API конфигурации"""
        config = SJAPIConfig()
        assert hasattr(config, 'BASE_URL')
        assert hasattr(config, 'VACANCIES_ENDPOINT')

    def test_sj_config_urls(self):
        """Тест URL конфигурации"""
        config = SJAPIConfig()
        assert config.BASE_URL.startswith('https://api.superjob.ru')
        assert 'vacancies' in config.VACANCIES_ENDPOINT

    def test_sj_config_auth(self):
        """Тест настроек аутентификации"""
        config = SJAPIConfig()
        if hasattr(config, 'API_KEY'):
            assert config.API_KEY is not None
        if hasattr(config, 'SECRET_KEY'):
            assert config.SECRET_KEY is not None

    def test_sj_config_parameters(self):
        """Тест параметров конфигурации"""
        config = SJAPIConfig()
        assert hasattr(config, 'DEFAULT_COUNT')
        assert hasattr(config, 'MAX_COUNT')
        if hasattr(config, 'DEFAULT_COUNT'):
            assert config.DEFAULT_COUNT > 0

    def test_sj_config_headers(self):
        """Тест заголовков запросов"""
        config = SJAPIConfig()
        if hasattr(config, 'get_headers'):
            headers = config.get_headers()
            assert isinstance(headers, dict)
