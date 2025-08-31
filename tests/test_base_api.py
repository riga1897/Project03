
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.base_api import BaseAPI


class TestBaseAPI:
    """Тесты для BaseAPI"""

    def test_base_api_initialization(self):
        """Тест инициализации BaseAPI"""
        api = BaseAPI()
        assert hasattr(api, 'session')
        assert api.session is not None

    def test_base_api_abstract_methods(self):
        """Тест абстрактных методов BaseAPI"""
        api = BaseAPI()
        
        # Проверяем, что абстрактные методы вызывают NotImplementedError
        with pytest.raises(NotImplementedError):
            api.get_vacancies("test")
        
        with pytest.raises(NotImplementedError):
            api.get_vacancy_by_id("123")

    @patch('requests.Session.get')
    def test_base_api_request_handling(self, mock_get):
        """Тест обработки запросов"""
        # Настраиваем мок
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = BaseAPI()
        
        # Проверяем, что сессия создается правильно
        assert api.session is not None

    def test_base_api_headers(self):
        """Тест заголовков запроса"""
        api = BaseAPI()
        headers = api.session.headers
        assert 'User-Agent' in headers
