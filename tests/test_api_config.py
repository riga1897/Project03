
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.api_config import APIConfig


class TestAPIConfig:
    """Тесты для APIConfig с консолидированными моками"""

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_api_config_initialization(self, mock_sj_config, mock_hh_config):
        """Тест инициализации API конфигурации"""
        mock_hh_instance = Mock()
        mock_sj_instance = Mock()
        mock_hh_config.return_value = mock_hh_instance
        mock_sj_config.return_value = mock_sj_instance
        
        config = APIConfig()
        assert hasattr(config, 'hh_config')
        assert hasattr(config, 'sj_config')

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_api_config_urls(self, mock_sj_config, mock_hh_config):
        """Тест URL конфигурации"""
        config = APIConfig()
        assert hasattr(config, 'get_pagination_params')

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_api_config_headers(self, mock_sj_config, mock_hh_config):
        """Тест заголовков конфигурации"""
        config = APIConfig()
        headers = config.get_default_headers()
        assert isinstance(headers, dict)

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_api_config_parameters(self, mock_sj_config, mock_hh_config):
        """Тест параметров конфигурации"""
        config = APIConfig()
        params = config.get_pagination_params()
        assert isinstance(params, dict)
        assert 'max_pages' in params
