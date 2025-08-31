
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.sj_api import SuperJobAPI
from src.vacancies.models import Vacancy


class TestSuperJobAPI:
    """Тесты для SuperJobAPI"""

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.utils.cache.FileCache')
    @patch('src.api_modules.sj_api.APIConfig')
    @patch('src.api_modules.sj_api.Paginator')
    def test_superjob_api_initialization(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест инициализации SuperJobAPI"""
        mock_config = Mock()
        mock_config.superjob_base_url = "https://api.superjob.ru"
        mock_config.superjob_api_key = "test_key"
        mock_api_config.return_value = mock_config

        api = SuperJobAPI()

        assert api.base_url == "https://api.superjob.ru"
        assert api.api_key == "test_key"

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.utils.cache.FileCache')
    @patch('src.api_modules.sj_api.APIConfig')
    @patch('src.api_modules.sj_api.Paginator')
    def test_get_vacancies_success(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест успешного получения вакансий"""
        mock_config = Mock()
        mock_config.superjob_base_url = "https://api.superjob.ru"
        mock_config.superjob_api_key = "test_key"
        mock_api_config.return_value = mock_config

        # Настраиваем мок коннектора
        mock_connector_instance = Mock()
        mock_connector.return_value = mock_connector_instance

        test_response = {
            "objects": [
                {
                    "id": 123,
                    "profession": "Python Developer",
                    "link": "https://superjob.ru/vacancy/123"
                }
            ]
        }
        mock_connector_instance.get.return_value = test_response

        api = SuperJobAPI()
        result = api.get_vacancies("Python")

        assert len(result) == 1
        assert result[0]["id"] == 123

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.utils.cache.FileCache')
    @patch('src.api_modules.sj_api.APIConfig')
    @patch('src.api_modules.sj_api.Paginator')
    def test_get_vacancies_empty_response(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест получения пустого ответа"""
        mock_config = Mock()
        mock_config.superjob_base_url = "https://api.superjob.ru"
        mock_config.superjob_api_key = "test_key"
        mock_api_config.return_value = mock_config

        mock_connector_instance = Mock()
        mock_connector.return_value = mock_connector_instance
        mock_connector_instance.get.return_value = {"objects": []}

        api = SuperJobAPI()
        result = api.get_vacancies("NonexistentJob")

        assert result == []

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.utils.cache.FileCache')
    @patch('src.api_modules.sj_api.APIConfig')
    @patch('src.api_modules.sj_api.Paginator')
    def test_validate_vacancy_valid(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест валидации валидной вакансии"""
        api = SuperJobAPI()

        valid_vacancy = {
            "profession": "Python Developer",
            "link": "https://superjob.ru/vacancy/123"
        }

        result = api._validate_vacancy(valid_vacancy)
        assert result is True

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.utils.cache.FileCache')
    @patch('src.api_modules.sj_api.APIConfig')
    @patch('src.api_modules.sj_api.Paginator')
    def test_validate_vacancy_invalid(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест валидации невалидной вакансии"""
        api = SuperJobAPI()

        invalid_vacancy = {"id": 123}  # Отсутствуют обязательные поля

        result = api._validate_vacancy(invalid_vacancy)
        assert result is False

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.utils.cache.FileCache')
    @patch('src.api_modules.sj_api.APIConfig')
    @patch('src.api_modules.sj_api.Paginator')
    def test_format_search_params(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест форматирования параметров поиска"""
        api = SuperJobAPI()

        params = api._format_search_params("Python", per_page=50, page=1)

        assert params["keyword"] == "Python"
        assert params["count"] == 50
        assert params["page"] == 1

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.utils.cache.FileCache')
    @patch('src.api_modules.sj_api.APIConfig')
    @patch('src.api_modules.sj_api.Paginator')
    def test_get_companies_success(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест успешного получения компаний"""
        mock_config = Mock()
        mock_config.superjob_base_url = "https://api.superjob.ru"
        mock_config.superjob_api_key = "test_key"
        mock_api_config.return_value = mock_config

        mock_connector_instance = Mock()
        mock_connector.return_value = mock_connector_instance

        test_response = {
            "objects": [
                {
                    "id": 1,
                    "title": "Яндекс",
                    "link": "https://superjob.ru/company/1"
                }
            ]
        }
        mock_connector_instance.get.return_value = test_response

        api = SuperJobAPI()
        result = api.get_companies()

        assert len(result) == 1
        assert result[0]["id"] == 1

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.utils.cache.FileCache')
    @patch('src.api_modules.sj_api.APIConfig')
    @patch('src.api_modules.sj_api.Paginator')
    def test_clear_cache(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест очистки кэша"""
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance

        api = SuperJobAPI()
        api.clear_cache()

        mock_cache_instance.clear.assert_called_once()

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.utils.cache.FileCache')
    @patch('src.api_modules.sj_api.APIConfig')
    @patch('src.api_modules.sj_api.Paginator')
    def test_api_error_handling(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест обработки ошибок API"""
        mock_config = Mock()
        mock_config.superjob_base_url = "https://api.superjob.ru"
        mock_config.superjob_api_key = "test_key"
        mock_api_config.return_value = mock_config

        mock_connector_instance = Mock()
        mock_connector.return_value = mock_connector_instance
        mock_connector_instance.get.side_effect = Exception("API Error")

        api = SuperJobAPI()
        result = api.get_vacancies("Python")

        assert result == []
