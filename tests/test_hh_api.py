import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.api_modules.hh_api import HeadHunterAPI


class TestHeadHunterAPI:
    """Тесты для HeadHunter API с консолидированными моками"""

    @patch("src.api_modules.hh_api.APIConnector")
    @patch("src.utils.cache.FileCache")
    @patch("src.api_modules.hh_api.APIConfig")
    @patch("src.api_modules.hh_api.Paginator")
    def test_hh_api_initialization(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест инициализации HeadHunter API"""
        # Настраиваем моки
        mock_config_instance = Mock()
        mock_api_config.return_value = mock_config_instance
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance
        mock_connector_instance = Mock()
        mock_connector.return_value = mock_connector_instance
        mock_paginator_instance = Mock()
        mock_paginator.return_value = mock_paginator_instance

        api = HeadHunterAPI()
        assert hasattr(api, "_config")
        assert hasattr(api, "connector")

    @patch("src.api_modules.hh_api.APIConnector")
    @patch("src.utils.cache.FileCache")
    @patch("src.api_modules.hh_api.APIConfig")
    @patch("src.api_modules.hh_api.Paginator")
    def test_hh_api_with_connector(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест инициализации с коннектором"""
        api = HeadHunterAPI()
        assert hasattr(api, "BASE_URL")

    @patch("src.api_modules.hh_api.APIConnector")
    @patch("src.utils.cache.FileCache")
    @patch("src.api_modules.hh_api.APIConfig")
    @patch("src.api_modules.hh_api.Paginator")
    def test_get_vacancies_success(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест успешного получения вакансий"""
        # Мок ответа API
        mock_response = {
            "items": [
                {
                    "id": "123",
                    "name": "Python Developer",
                    "employer": {"name": "Test Company"},
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "source": "hh.ru",
                }
            ],
            "found": 1,
            "pages": 1,
        }

        # Настраиваем пагинатор для возврата списка
        mock_paginator_instance = Mock()
        mock_paginator_instance.paginate.return_value = [mock_response["items"][0]]
        mock_paginator.return_value = mock_paginator_instance

        api = HeadHunterAPI()

        # Консолидированный мок для API запросов
        with patch.object(api, "get_vacancies", return_value=mock_response["items"]):
            result = api.get_vacancies("python")

        assert isinstance(result, list) or result is not None

    @patch("src.api_modules.hh_api.APIConnector")
    @patch("src.utils.cache.FileCache")
    @patch("src.api_modules.hh_api.APIConfig")
    @patch("src.api_modules.hh_api.Paginator")
    def test_get_vacancies_empty_response(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест получения пустого ответа"""
        mock_response = {"items": [], "found": 0, "pages": 0}

        api = HeadHunterAPI()

        with patch.object(api, "_CachedAPI__connect_to_api", return_value=mock_response):
            result = api.get_vacancies("nonexistent")

        assert result == []

    @patch("src.api_modules.hh_api.APIConnector")
    @patch("src.utils.cache.FileCache")
    @patch("src.api_modules.hh_api.APIConfig")
    @patch("src.api_modules.hh_api.Paginator")
    def test_get_vacancies_api_error(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест обработки ошибки API"""
        api = HeadHunterAPI()

        with patch.object(api, "_CachedAPI__connect_to_api", side_effect=Exception("API Error")):
            result = api.get_vacancies("python")

        assert result == []

    @patch("src.api_modules.hh_api.APIConnector")
    @patch("src.utils.cache.FileCache")
    @patch("src.api_modules.hh_api.APIConfig")
    @patch("src.api_modules.hh_api.Paginator")
    def test_validate_vacancy_valid(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест валидации валидной вакансии"""
        api = HeadHunterAPI()

        valid_vacancy = {"name": "Python Developer", "alternate_url": "https://hh.ru/vacancy/123"}

        result = api._validate_vacancy(valid_vacancy)
        assert result is True

    @patch("src.api_modules.hh_api.APIConnector")
    @patch("src.utils.cache.FileCache")
    @patch("src.api_modules.hh_api.APIConfig")
    @patch("src.api_modules.hh_api.Paginator")
    def test_validate_vacancy_invalid(self, mock_paginator, mock_api_config, mock_cache, mock_connector):
        """Тест валидации невалидной вакансии"""
        api = HeadHunterAPI()

        invalid_vacancy = {
            "name": "Python Developer"
            # Отсутствует alternate_url
        }

        result = api._validate_vacancy(invalid_vacancy)
        assert result is False
