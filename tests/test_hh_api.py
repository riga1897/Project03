import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.hh_api import HeadHunterAPI


class TestHeadHunterAPI:
    """Тесты для HeadHunterAPI"""

    def test_hh_api_initialization(self):
        """Тест инициализации HeadHunterAPI"""
        api = HeadHunterAPI()
        assert hasattr(api, 'base_url')
        assert api.base_url == "https://api.hh.ru"

    def test_hh_api_inheritance(self):
        """Тест наследования от CachedAPI"""
        from src.api_modules.cached_api import CachedAPI

        api = HeadHunterAPI()
        assert isinstance(api, CachedAPI)

    @patch('requests.Session.get')
    def test_get_vacancies_success(self, mock_get):
        """Тест успешного получения вакансий"""
        # Настраиваем мок ответа
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "123",
                    "name": "Python Developer",
                    "employer": {"name": "Test Company"},
                    "salary": {"from": 100000, "to": 150000},
                    "area": {"name": "Москва"}
                }
            ],
            "pages": 1,
            "per_page": 20,
            "page": 0
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        result = api.get_vacancies("Python")

        assert isinstance(result, list)
        mock_get.assert_called()

    @patch('requests.Session.get')
    def test_get_vacancy_by_id_success(self, mock_get):
        """Тест успешного получения вакансии по ID"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "name": "Python Developer",
            "employer": {"name": "Test Company"}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        result = api.get_vacancy_by_id("123")

        assert result is not None
        mock_get.assert_called()

    @patch('requests.Session.get')
    def test_get_vacancies_network_error(self, mock_get):
        """Тест обработки сетевой ошибки"""
        mock_get.side_effect = Exception("Network error")

        api = HeadHunterAPI()
        result = api.get_vacancies("Python")

        # API должен вернуть пустой список при ошибке
        assert result == []

    def test_build_search_params(self):
        """Тест построения параметров поиска"""
        api = HeadHunterAPI()

        # Проверяем базовые параметры
        params = api._build_search_params("Python", page=0)
        assert "text" in params
        assert "page" in params
        assert params["text"] == "Python"
        assert params["page"] == 0

    def test_process_vacancies_response(self):
        """Тест обработки ответа с вакансиями"""
        api = HeadHunterAPI()

        test_response = {
            "items": [
                {
                    "id": "123",
                    "name": "Python Developer",
                    "employer": {"name": "Test Company"}
                }
            ]
        }

        result = api._process_vacancies_response(test_response)
        assert isinstance(result, list)
        assert len(result) > 0