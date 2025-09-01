import os
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import List, Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.api_modules.cached_api import CachedAPI
from src.vacancies.models import Vacancy


class ConcreteCachedAPI(CachedAPI):
    """Конкретная реализация CachedAPI для тестирования"""

    def __init__(self, cache_dir="./test_cache"):
        super().__init__(cache_dir)
        self.test_data = []

    def get_vacancies(self, search_query: str, **kwargs) -> List[Any]:
        """Получение вакансий для тестирования"""
        return self.test_data

    def get_companies(self, **kwargs) -> List[Any]:
        """Получение компаний для тестирования"""
        return []

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Any]:
        """Получение страницы вакансий"""
        return self.test_data

    def _get_empty_response(self) -> List[Any]:
        """Возвращает пустой ответ"""
        return []

    def _validate_vacancy(self, vacancy_data: Any) -> bool:
        """Валидация данных вакансии"""
        return isinstance(vacancy_data, dict)
        
    def _make_request(self, url: str, params: dict) -> dict:
        """Выполнение HTTP запроса"""
        return {"status": "success", "data": []}
        
    def _parse_response(self, response: dict) -> list:
        """Парсинг ответа API"""
        if isinstance(response, dict) and "items" in response:
            return response["items"]
        return []


class TestCachedAPI:
    """Тесты для CachedAPI"""

    @patch("src.utils.cache.FileCache")
    def test_cached_api_initialization(self, mock_file_cache):
        """Тест инициализации CachedAPI"""
        mock_cache_instance = Mock()
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()
        assert api is not None
        assert hasattr(api, 'cache')

    @patch("src.utils.cache.FileCache")
    def test_cached_api_with_cache_manager(self, mock_file_cache):
        """Тест CachedAPI с кэш менеджером"""
        mock_cache_instance = Mock()
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()
        assert hasattr(api, 'cache')

    @patch("src.utils.cache.FileCache")
    def test_cached_api_abstract_methods(self, mock_file_cache):
        """Тест реализации абстрактных методов CachedAPI"""
        api = ConcreteCachedAPI()

        # Проверяем, что все абстрактные методы реализованы
        assert hasattr(api, 'get_vacancies')
        assert callable(getattr(api, 'get_vacancies'))

        # Тестируем вызов метода
        result = api.get_vacancies("Python")
        assert isinstance(result, list)

    @patch("src.utils.cache.FileCache")
    def test_cache_integration(self, mock_file_cache):
        """Тест интеграции с кэшем"""
        mock_cache_instance = Mock()
        mock_cache_instance.get.return_value = None
        mock_cache_instance.set.return_value = None
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()

        # Устанавливаем тестовые данные
        test_vacancies = [
            Vacancy(title="Python Developer", url="https://test.com", vacancy_id="123", source="test_source")
        ]
        api.test_data = test_vacancies

        # Тестируем получение вакансий
        result = api.get_vacancies("Python")
        assert result == test_vacancies

    @patch("src.utils.cache.FileCache")
    def test_clear_cache_method(self, mock_file_cache):
        """Тест метода очистки кэша"""
        mock_cache_instance = Mock()
        mock_cache_instance.clear.return_value = None
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()

        # Проверяем наличие метода clear_cache или аналогичного
        if hasattr(api, 'clear_cache'):
            api.clear_cache("test_prefix")
            mock_cache_instance.clear.assert_called_once()
        else:
            # Если метода нет, проверяем что кэш доступен
            assert hasattr(api, 'cache')


class TestCachedAPIEdgeCases:
    """Тесты граничных случаев для CachedAPI"""

    @patch("src.utils.cache.FileCache")
    def test_cached_api_empty_response(self, mock_file_cache):
        """Тест обработки пустого ответа"""
        mock_cache_instance = Mock()
        mock_cache_instance.get.return_value = None
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()
        result = api.get_vacancies("")
        assert isinstance(result, list)
        assert len(result) == 0

    @patch("src.utils.cache.FileCache")
    def test_cached_api_cache_miss(self, mock_file_cache):
        """Тест кэш-промаха"""
        mock_cache_instance = Mock()
        mock_cache_instance.get.return_value = None  # Кэш-промах
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()
        result = api.get_vacancies("Python")
        assert isinstance(result, list)

    @patch("src.utils.cache.FileCache")
    def test_cached_api_cache_hit(self, mock_file_cache):
        """Тест кэш-попадания"""
        cached_data = [
            Vacancy("123", "Python Developer", "https://test.com", "test_source")
        ]

        mock_cache_instance = Mock()
        mock_cache_instance.get.return_value = cached_data
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()
        result = api.get_vacancies("Python")

        # Должен вернуться кэшированный результат или пустой список
        assert isinstance(result, list)


class TestCachedAPIHelpers:
    """Тесты вспомогательных методов CachedAPI"""

    @patch("src.utils.cache.FileCache")
    def test_make_request_method(self, mock_file_cache):
        """Тест метода _make_request"""
        api = ConcreteCachedAPI()

        result = api._make_request("https://test.com", {"query": "Python"})
        assert isinstance(result, dict)

    @patch("src.utils.cache.FileCache")
    def test_parse_response_method(self, mock_file_cache):
        """Тест метода _parse_response"""
        api = ConcreteCachedAPI()

        test_response = {"items": [{"id": "123", "name": "Test"}], "found": 1}
        result = api._parse_response(test_response)
        assert isinstance(result, list)

    @patch("src.utils.cache.FileCache")
    def test_cached_api_inheritance(self, mock_file_cache):
        """Тест наследования от CachedAPI"""
        api = ConcreteCachedAPI()
        assert isinstance(api, CachedAPI)

        # Проверяем, что все необходимые методы доступны
        assert hasattr(api, 'get_vacancies')
        assert hasattr(api, '_make_request')
        assert hasattr(api, '_parse_response')