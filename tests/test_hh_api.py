import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.hh_api import HeadHunterAPI


class TestHeadHunterAPI:
    """Тесты для HeadHunter API"""

    @patch.multiple('src.api_modules.hh_api',
                   APIConnector=MagicMock(),
                   CacheManager=MagicMock(),
                   APIConfig=MagicMock(),
                   EnvLoader=MagicMock())
    def test_hh_api_initialization(self):
        """Тест инициализации HeadHunter API"""
        api = HeadHunterAPI()
        assert hasattr(api, 'base_url')
        assert hasattr(api, 'cache_manager')

    @patch.multiple('src.api_modules.hh_api',
                   APIConnector=MagicMock(),
                   CacheManager=MagicMock(),
                   APIConfig=MagicMock(),
                   EnvLoader=MagicMock())
    def test_hh_api_with_connector(self):
        """Тест инициализации с коннектором"""
        api = HeadHunterAPI()
        assert hasattr(api, 'base_url')

    @patch.multiple('src.api_modules.hh_api',
                   APIConnector=MagicMock(),
                   CacheManager=MagicMock(),
                   APIConfig=MagicMock(),
                   EnvLoader=MagicMock())
    def test_get_vacancies_success(self):
        """Тест успешного получения вакансий"""
        # Мок ответа API
        mock_response = {
            "items": [
                {
                    "id": "123",
                    "name": "Python Developer",
                    "employer": {"name": "Test Company"},
                    "salary": {"from": 100000, "to": 150000}
                }
            ]
        }

        # Настраиваем мок коннектора
        mock_conn = MagicMock()
        mock_conn.get.return_value = mock_response
        # Предполагается, что APIConnector является частью hh_api для патчинга
        # Если APIConnector находится в другом модуле, путь должен быть изменен соответствующим образом
        src.api_modules.hh_api.APIConnector.return_value = mock_conn

        api = HeadHunterAPI()
        vacancies = api.get_vacancies("Python")

        assert isinstance(vacancies, list)
        assert len(vacancies) > 0

    @patch.multiple('src.api_modules.hh_api',
                   APIConnector=MagicMock(),
                   CacheManager=MagicMock(),
                   APIConfig=MagicMock(),
                   EnvLoader=MagicMock())
    def test_get_vacancies_empty_response(self):
        """Тест обработки пустого ответа"""
        mock_response = {"items": []}

        mock_conn = MagicMock()
        mock_conn.get.return_value = mock_response
        src.api_modules.hh_api.APIConnector.return_value = mock_conn

        api = HeadHunterAPI()
        vacancies = api.get_vacancies("NonExistentJob")

        assert isinstance(vacancies, list)
        assert len(vacancies) == 0

    @patch.multiple('src.api_modules.hh_api',
                   APIConnector=MagicMock(),
                   CacheManager=MagicMock(),
                   APIConfig=MagicMock(),
                   EnvLoader=MagicMock())
    def test_get_vacancies_api_error(self):
        """Тест обработки ошибки API"""
        mock_conn = MagicMock()
        mock_conn.get.side_effect = Exception("API Error")
        src.api_modules.hh_api.APIConnector.return_value = mock_conn

        api = HeadHunterAPI()

        with pytest.raises(Exception):
            api.get_vacancies("Python")

    @patch.multiple('src.api_modules.hh_api',
                   APIConnector=MagicMock(),
                   CacheManager=MagicMock(),
                   APIConfig=MagicMock(),
                   EnvLoader=MagicMock())
    def test_validate_vacancy_valid(self):
        """Тест валидации корректной вакансии"""
        api = HeadHunterAPI()

        valid_vacancy = {
            "id": "123",
            "name": "Python Developer",
            "employer": {"name": "Test Company"},
            "salary": {"from": 100000, "to": 150000}
        }

        assert api._validate_vacancy(valid_vacancy) is True

    @patch.multiple('src.api_modules.hh_api',
                   APIConnector=MagicMock(),
                   CacheManager=MagicMock(),
                   APIConfig=MagicMock(),
                   EnvLoader=MagicMock())
    def test_validate_vacancy_invalid(self):
        """Тест валидации некорректной вакансии"""
        api = HeadHunterAPI()

        invalid_vacancy = {
            "id": "123"
            # Отсутствуют обязательные поля
        }

        assert api._validate_vacancy(invalid_vacancy) is False