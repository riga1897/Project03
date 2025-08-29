
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
        # Настраиваем мок ответа для метаданных (первый запрос)
        mock_connect.side_effect = [
            {
                "items": [],
                "found": 1,
                "pages": 1
            },
            # Второй запрос за данными
            {
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
                "found": 1,
                "pages": 1
            }
        ]

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

    @patch('src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_success(self, mock_connect):
        """Тест успешного получения вакансий"""
        # Настраиваем мок ответа для метаданных и данных
        mock_connect.side_effect = [
            {
                "objects": [],
                "total": 1
            },
            {
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
        ]

        api = SuperJobAPI()
        vacancies = api.get_vacancies(search_query="Java", count=1)

        assert len(vacancies) == 1
        assert vacancies[0]["profession"] == "Java Developer"
        assert vacancies[0]["source"] == "superjob.ru"

    @patch('src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_empty_response(self, mock_connect):
        """Тест получения пустого результата"""
        mock_connect.return_value = {"objects": [], "total": 0}

        api = SuperJobAPI()
        vacancies = api.get_vacancies(search_query="NonExistentJob")

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
        mock_vacancy = {
            "id": "1",
            "name": "Test Vacancy",
            "source": "hh.ru",
            "alternate_url": "https://hh.ru/vacancy/1"
        }
        mock_hh_get.return_value = [mock_vacancy]

        api = UnifiedAPI()
        vacancies = api.get_vacancies_from_source("python", "hh.ru")

        assert len(vacancies) == 1
        assert vacancies[0]["name"] == "Test Vacancy"

    def test_clear_cache_with_sources(self):
        """Тест очистки кэша с указанными источниками"""
        api = UnifiedAPI()
        # Метод должен принимать словарь источников
        try:
            api.clear_cache({"hh": True, "sj": False})
            # Если нет исключений, тест прошел
            assert True
        except Exception as e:
            pytest.fail(f"clear_cache() raised an exception: {e}")

    def test_clear_cache_all_sources(self):
        """Тест очистки всего кэша"""
        api = UnifiedAPI()
        try:
            api.clear_cache({"hh": True, "sj": True})
            # Если нет исключений, тест прошел
            assert True
        except Exception as e:
            pytest.fail(f"clear_cache() raised an exception: {e}")

    @patch.object(HeadHunterAPI, 'get_vacancies')
    @patch.object(SuperJobAPI, 'get_vacancies')
    def test_get_vacancies_from_sources(self, mock_sj_get, mock_hh_get):
        """Тест получения вакансий из нескольких источников"""
        # Мокируем результаты
        mock_hh_get.return_value = [{"id": "1", "name": "HH Vacancy", "source": "hh.ru"}]
        mock_sj_get.return_value = [{"id": "2", "profession": "SJ Vacancy", "source": "superjob.ru"}]

        api = UnifiedAPI()
        
        # Мокируем SQL дедупликацию
        with patch('src.api_modules.base_api.BaseJobAPI._deduplicate_vacancies') as mock_dedup:
            mock_dedup.return_value = [{"id": "1", "name": "HH Vacancy", "source": "hh.ru"}]
            
            vacancies = api.get_vacancies_from_sources("python", sources=["hh", "sj"])
            
            assert isinstance(vacancies, list)

    def test_validate_sources(self):
        """Тест валидации источников"""
        api = UnifiedAPI()
        
        # Валидные источники
        valid = api.validate_sources(["hh", "sj"])
        assert "hh" in valid
        assert "sj" in valid
        
        # Невалидные источники должны быть отфильтрованы
        filtered = api.validate_sources(["hh", "invalid_source"])
        assert "hh" in filtered
        assert "invalid_source" not in filtered

    @patch.object(HeadHunterAPI, 'get_vacancies_from_target_companies')
    @patch.object(SuperJobAPI, 'get_vacancies_from_target_companies')
    def test_get_vacancies_from_target_companies(self, mock_sj_target, mock_hh_target):
        """Тест получения вакансий от целевых компаний"""
        mock_hh_target.return_value = [{"id": "1", "name": "Target HH", "source": "hh.ru"}]
        mock_sj_target.return_value = [{"id": "2", "profession": "Target SJ", "source": "superjob.ru"}]

        api = UnifiedAPI()
        vacancies = api.get_vacancies_from_target_companies("python")

        assert isinstance(vacancies, list)
        # Проверяем, что методы были вызваны
        mock_hh_target.assert_called_once()
        mock_sj_target.assert_called_once()
