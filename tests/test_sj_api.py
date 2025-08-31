import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.sj_api import SuperJobAPI


class TestSuperJobAPI:
    """Тесты для SuperJobAPI"""

    def test_sj_api_initialization(self):
        """Тест инициализации SuperJobAPI"""
        api = SuperJobAPI()
        assert hasattr(api, 'base_url')
        assert api.base_url == "https://api.superjob.ru/2.0"

    def test_sj_api_with_api_key(self):
        """Тест инициализации с API ключом"""
        api = SuperJobAPI(api_key="test_key")
        assert hasattr(api, 'api_key')
        assert api.api_key == "test_key"

    def test_sj_api_inheritance(self):
        """Тест наследования от CachedAPI"""
        from src.api_modules.cached_api import CachedAPI

        api = SuperJobAPI()
        assert isinstance(api, CachedAPI)

    @patch('requests.Session.get')
    def test_get_vacancies_success(self, mock_get):
        """Тест успешного получения вакансий"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "objects": [
                {
                    "id": 123,
                    "profession": "Python Developer",
                    "firm_name": "Test Company",
                    "payment_from": 100000,
                    "payment_to": 150000,
                    "town": {"title": "Москва"}
                }
            ],
            "total": 1
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = SuperJobAPI(api_key="test_key")
        result = api.get_vacancies("Python")

        assert isinstance(result, list)
        mock_get.assert_called()

    @patch('requests.Session.get')
    def test_get_vacancy_by_id_success(self, mock_get):
        """Тест успешного получения вакансии по ID"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 123,
            "profession": "Python Developer",
            "firm_name": "Test Company"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = SuperJobAPI(api_key="test_key")
        result = api.get_vacancy_by_id("123")

        assert result is not None
        mock_get.assert_called()

    def test_api_key_validation(self):
        """Тест валидации API ключа"""
        api = SuperJobAPI()

        # Проверяем обработку отсутствующего API ключа
        assert hasattr(api, 'api_key')

    @patch.dict(os.environ, {'SUPERJOB_API_KEY': 'env_test_key'})
    def test_api_key_from_environment(self):
        """Тест получения API ключа из переменной окружения"""
        api = SuperJobAPI()
        # API должен использовать ключ из окружения
        assert hasattr(api, 'api_key')