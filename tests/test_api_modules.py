
"""
Тесты для модулей работы с внешними API

Содержит тесты для проверки корректности работы с API различных
платформ поиска вакансий (HH.ru, SuperJob.ru).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI


class TestHeadHunterAPI:
    """Тесты для HeadHunter API"""

    def test_api_initialization(self):
        """Тест инициализации API"""
        api = HeadHunterAPI()
        assert api is not None
        assert hasattr(api, 'search_vacancies')

    @patch('requests.get')
    def test_search_vacancies_success(self, mock_get):
        """Тест успешного поиска вакансий"""
        # Настраиваем мок ответа
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "12345",
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/12345",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "snippet": {"requirement": "Python", "responsibility": "Development"},
                    "employer": {"name": "Test Company"},
                    "published_at": "2024-01-01T00:00:00+03:00"
                }
            ],
            "found": 1
        }
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        vacancies = api.search_vacancies(query="Python", per_page=1)

        assert len(vacancies) == 1
        assert vacancies[0].title == "Python Developer"
        assert vacancies[0].vacancy_id == "12345"

    @patch('requests.get')
    def test_search_vacancies_empty_response(self, mock_get):
        """Тест поиска без результатов"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "found": 0}
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        vacancies = api.search_vacancies(query="NonExistentJob")

        assert len(vacancies) == 0

    @patch('requests.get')
    def test_search_vacancies_network_error(self, mock_get):
        """Тест обработки сетевой ошибки"""
        mock_get.side_effect = Exception("Network error")

        api = HeadHunterAPI()
        vacancies = api.search_vacancies(query="Python")

        assert len(vacancies) == 0


class TestSuperJobAPI:
    """Тесты для SuperJob API"""

    def test_api_initialization(self):
        """Тест инициализации API"""
        api = SuperJobAPI()
        assert api is not None
        assert hasattr(api, 'search_vacancies')

    @patch('requests.get')
    def test_search_vacancies_success(self, mock_get):
        """Тест успешного поиска вакансий"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "objects": [
                {
                    "id": 54321,
                    "profession": "Java Developer",
                    "link": "https://superjob.ru/vakansii/java-developer-54321.html",
                    "payment_from": 80000,
                    "payment_to": 120000,
                    "currency": "rub",
                    "candidat": "Java, Spring",
                    "vacancyRichText": "Backend development",
                    "firm_name": "Java Corp",
                    "date_published": 1704067200
                }
            ],
            "total": 1
        }
        mock_get.return_value = mock_response

        api = SuperJobAPI()
        vacancies = api.search_vacancies(query="Java", count=1)

        assert len(vacancies) == 1
        assert vacancies[0].title == "Java Developer"
        assert vacancies[0].vacancy_id == "54321"

    @patch('requests.get')
    def test_search_vacancies_empty_response(self, mock_get):
        """Тест поиска без результатов"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"objects": [], "total": 0}
        mock_get.return_value = mock_response

        api = SuperJobAPI()
        vacancies = api.search_vacancies(query="NonExistentJob")

        assert len(vacancies) == 0


class TestUnifiedAPI:
    """Тесты для Unified API"""

    def test_initialization(self):
        """Тест инициализации"""
        api = UnifiedAPI()
        assert api is not None

    def test_get_available_sources(self):
        """Тест получения доступных источников"""
        api = UnifiedAPI()
        sources = api.get_available_sources()
        assert isinstance(sources, list)
        assert len(sources) > 0

    @patch.object(HeadHunterAPI, 'search_vacancies')
    def test_search_vacancies_single_source(self, mock_hh_search):
        """Тест поиска через один источник"""
        # Мокируем результат поиска
        mock_vacancy = Mock()
        mock_vacancy.title = "Test Vacancy"
        mock_vacancy.source = "hh.ru"
        mock_hh_search.return_value = [mock_vacancy]

        api = UnifiedAPI()
        vacancies = api.search_vacancies(query="Python", sources=["hh.ru"])

        assert len(vacancies) == 1
        assert vacancies[0].title == "Test Vacancy"
        mock_hh_search.assert_called_once()

    def test_clear_cache(self):
        """Тест очистки кэша"""
        api = UnifiedAPI()
        # Метод не должен вызывать исключений
        api.clear_cache()
