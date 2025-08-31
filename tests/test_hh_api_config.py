
import pytest
from unittest.mock import patch
from src.config.hh_api_config import HHAPIConfig


class TestHHAPIConfig:
    def test_hh_config_initialization(self):
        """Тест инициализации HH API конфигурации"""
        config = HHAPIConfig()
        assert hasattr(config, 'BASE_URL')
        assert hasattr(config, 'VACANCIES_ENDPOINT')
        assert hasattr(config, 'EMPLOYERS_ENDPOINT')

    def test_hh_config_urls(self):
        """Тест URL конфигурации"""
        config = HHAPIConfig()
        assert config.BASE_URL.startswith('https://api.hh.ru')
        assert 'vacancies' in config.VACANCIES_ENDPOINT
        assert 'employers' in config.EMPLOYERS_ENDPOINT

    def test_hh_config_parameters(self):
        """Тест параметров конфигурации"""
        config = HHAPIConfig()
        assert hasattr(config, 'DEFAULT_PER_PAGE')
        assert hasattr(config, 'MAX_PER_PAGE')
        assert config.DEFAULT_PER_PAGE > 0
        assert config.MAX_PER_PAGE >= config.DEFAULT_PER_PAGE

    def test_hh_config_timeout(self):
        """Тест настроек таймаута"""
        config = HHAPIConfig()
        assert hasattr(config, 'TIMEOUT')
        assert config.TIMEOUT > 0

    def test_hh_config_headers(self):
        """Тест заголовков запросов"""
        config = HHAPIConfig()
        if hasattr(config, 'HEADERS'):
            assert isinstance(config.HEADERS, dict)
            assert 'User-Agent' in config.HEADERS
