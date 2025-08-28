
"""
Тесты для модулей работы с внешними API

Содержит тесты для проверки корректности работы с API различных
платформ поиска вакансий (HH.ru, SuperJob.ru).
"""

import pytest
from unittest.mock import Mock, patch

# Мокаем все внешние API запросы
@pytest.fixture(autouse=True)
def mock_api_requests():
    """Мокает все API запросы для тестов"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {"items": [], "found": 0}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        yield mock_get

from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.config.api_config import APIConfig


class TestHeadHunterAPI:
    """Набор тестов для API клиента HeadHunter"""

    def test_api_initialization(self):
        """Тестирование корректной инициализации API клиента"""
        api = HeadHunterAPI()
        
        assert api.BASE_URL == "https://api.hh.ru/vacancies"
        assert api._config is not None

    def test_validate_vacancy_valid(self):
        """Тестирование валидации корректной структуры вакансии"""
        api = HeadHunterAPI()
        valid_vacancy = {
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/12345",
            "salary": {"from": 100000}
        }
        
        result = api._validate_vacancy(valid_vacancy)
        assert result is True

    def test_validate_vacancy_invalid(self):
        """Тестирование валидации некорректной структуры вакансии"""
        api = HeadHunterAPI()
        invalid_vacancy = {
            "name": "",  # Пустое название должно провалить валидацию
            "alternate_url": "https://hh.ru/vacancy/12345"
        }
        
        result = api._validate_vacancy(invalid_vacancy)
        assert result is False

    @patch('src.api_modules.cached_api.CachedAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_page_success(self, mock_connect):
        """Тестирование успешного получения страницы вакансий от API"""
        mock_connect.return_value = {
            "items": [
                {
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/12345"
                }
            ]
        }
        
        api = HeadHunterAPI()
        result = api.get_vacancies_page("python", page=0)
        
        assert len(result) == 1
        assert result[0]["name"] == "Python Developer"

    @patch('src.api_modules.cached_api.CachedAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_empty_response(self, mock_connect):
        """Тестирование обработки пустого ответа от API"""
        mock_connect.return_value = {"items": []}
        
        api = HeadHunterAPI()
        result = api.get_vacancies_page("nonexistent", page=0)
        
        assert result == []

    def test_empty_response_structure(self):
        """Тестирование корректной структуры пустого ответа API"""
        api = HeadHunterAPI()
        empty_response = api._get_empty_response()
        
        assert "items" in empty_response
        assert empty_response["items"] == []


class TestSuperJobAPI:
    """Набор тестов для API клиента SuperJob"""

    @patch.dict('os.environ', {'SUPERJOB_API_KEY': 'test_key'})
    def test_api_initialization_with_custom_key(self):
        """Тестирование инициализации с пользовательским API ключом"""
        api = SuperJobAPI()
        
        assert api.BASE_URL == "https://api.superjob.ru/2.0/vacancies"
        assert api.connector.headers["X-Api-App-Id"] == "test_key"

    def test_validate_vacancy_valid(self):
        """Тестирование валидации корректной вакансии SuperJob"""
        api = SuperJobAPI()
        valid_vacancy = {
            "profession": "Python Developer",
            "link": "https://superjob.ru/vacancy/12345"
        }
        
        result = api._validate_vacancy(valid_vacancy)
        assert result is True

    def test_validate_vacancy_invalid(self):
        """Тестирование валидации некорректной вакансии SuperJob"""
        api = SuperJobAPI()
        invalid_vacancy = {
            "profession": "",  # Пустое название должно провалить валидацию
            "link": "https://superjob.ru/vacancy/12345"
        }
        
        result = api._validate_vacancy(invalid_vacancy)
        assert result is False

    @patch('src.api_modules.cached_api.CachedAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_page_with_source(self, mock_connect):
        """Тестирование получения страницы с автоматическим добавлением источника"""
        mock_connect.return_value = {
            "objects": [
                {
                    "profession": "Java Developer",
                    "link": "https://superjob.ru/vacancy/67890"
                }
            ]
        }
        
        api = SuperJobAPI()
        result = api.get_vacancies_page("java", page=0)
        
        assert len(result) == 1
        assert result[0]["profession"] == "Java Developer"
        assert result[0]["source"] == "superjob.ru"

    def test_empty_response_structure(self):
        """Тестирование корректной структуры пустого ответа SuperJob API"""
        api = SuperJobAPI()
        empty_response = api._get_empty_response()
        
        assert "objects" in empty_response
        assert empty_response["objects"] == []
