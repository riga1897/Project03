"""
Тесты для модулей API

Содержит тесты для проверки корректности работы API модулей:
- HeadHunterAPI
- SuperJobAPI
- UnifiedAPI
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
        assert hasattr(api, 'get_vacancies')
        assert hasattr(api, 'BASE_URL')

    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_success(self, mock_connect):
        """Тест успешного получения вакансий"""
        # Настраиваем мок ответа
        mock_connect.return_value = {
            "items": [
                {
                    "id": "12345",
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/12345",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "snippet": {"requirement": "Python", "responsibility": "Development"},
                    "employer": {"name": "Test Company"},
                    "published_at": "2024-01-01T00:00:00+03:00",
                    "source": "hh.ru"
                }
            ],
            "found": 1,
            "pages": 1
        }

        api = HeadHunterAPI()
        vacancies = api.get_vacancies(search_query="Python", per_page=1)

        assert len(vacancies) == 1
        assert vacancies[0]["name"] == "Python Developer"
        assert vacancies[0]["source"] == "hh.ru"

    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_empty_response(self, mock_connect):
        """Тест получения пустого результата"""
        mock_connect.return_value = {"items": [], "found": 0}

        api = HeadHunterAPI()
        vacancies = api.get_vacancies(search_query="NonExistentJob")

        assert len(vacancies) == 0

    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_network_error(self, mock_connect):
        """Тест обработки сетевой ошибки"""
        mock_connect.side_effect = Exception("Network error")

        api = HeadHunterAPI()
        vacancies = api.get_vacancies(search_query="Python")

        # При ошибке должен возвращаться пустой список
        assert vacancies == []


class TestSuperJobAPI:
    """Тесты для SuperJob API"""

    def test_api_initialization(self):
        """Тест инициализации API"""
        api = SuperJobAPI()
        assert api is not None
        assert hasattr(api, 'get_vacancies')
        assert hasattr(api, 'BASE_URL')

    @patch('requests.get')
    def test_get_vacancies_success(self, mock_get):
        """Тест успешного получения вакансий"""
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
        vacancies = api.get_vacancies(query="Java", count=1)

        assert len(vacancies) == 1
        assert vacancies[0].title == "Java Developer"
        assert vacancies[0].source == "superjob.ru"

    @patch('requests.get')
    def test_get_vacancies_empty_response(self, mock_get):
        """Тест получения пустого результата"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"objects": [], "total": 0}
        mock_get.return_value = mock_response

        api = SuperJobAPI()
        vacancies = api.get_vacancies(query="NonExistentJob")

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

    @patch.object(HeadHunterAPI, 'get_vacancies')
    def test_get_vacancies_single_source(self, mock_hh_get):
        """Тест получения вакансий из одного источника"""
        # Мокируем результат получения
        mock_vacancy = Mock()
        mock_vacancy.title = "Test Vacancy"
        mock_vacancy.source = "hh.ru"
        mock_hh_get.return_value = [mock_vacancy]

        api = UnifiedAPI()
        vacancies = api.get_vacancies_from_source("hh.ru", query="python")

        assert len(vacancies) == 1
        assert vacancies[0].title == "Test Vacancy"

    def test_clear_cache_with_sources(self):
        """Тест очистки кэша с указанными источниками"""
        api = UnifiedAPI()
        # Метод должен принимать список источников
        try:
            api.clear_cache(['hh.ru'])
            # Если нет исключений, тест прошел
            assert True
        except Exception as e:
            pytest.fail(f"clear_cache() raised an exception: {e}")

    def test_clear_cache_all_sources(self):
        """Тест очистки всего кэша"""
        api = UnifiedAPI()
        try:
            api.clear_cache(['hh.ru', 'superjob.ru'])
            # Если нет исключений, тест прошел
            assert True
        except Exception as e:
            pytest.fail(f"clear_cache() raised an exception: {e}")