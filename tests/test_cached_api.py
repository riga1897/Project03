
import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.api_modules.cached_api import CachedAPI


class ConcreteCachedAPI(CachedAPI):
    """Конкретная реализация CachedAPI для тестирования"""
    
    def __init__(self):
        super().__init__()
        self.test_data = []
    
    def _get_empty_response(self):
        """Возвращает пустой ответ"""
        return {"items": []}
    
    def _validate_vacancy(self, vacancy_data):
        """Валидация данных вакансии"""
        return isinstance(vacancy_data, dict) and "id" in vacancy_data
    
    def get_vacancies_page(self, search_query="", page=0, per_page=50, **kwargs):
        """Получение страницы вакансий"""
        return {"items": self.test_data, "found": len(self.test_data)}


class TestCachedAPI:
    """Тесты для CachedAPI"""

    @patch("src.utils.cache.FileCache")
    def test_cached_api_initialization(self, mock_file_cache):
        """Тест инициализации CachedAPI"""
        mock_cache_instance = Mock()
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()
        assert api is not None
        assert api.cache is not None

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
        
        # Проверяем, что абстрактные методы реализованы
        assert callable(getattr(api, '_get_empty_response'))
        assert callable(getattr(api, '_validate_vacancy'))
        assert callable(getattr(api, 'get_vacancies_page'))

    @patch("src.utils.cache.FileCache")
    def test_cache_integration(self, mock_file_cache):
        """Тест интеграции с кэшем"""
        mock_cache_instance = Mock()
        mock_cache_instance.get.return_value = None
        mock_cache_instance.set.return_value = None
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()
        api.test_data = [{"id": "123", "name": "Test Job"}]
        
        result = api.get_vacancies_page("test")
        assert "items" in result

    @patch("src.utils.cache.FileCache")
    def test_clear_cache_method(self, mock_file_cache):
        """Тест метода очистки кэша"""
        mock_cache_instance = Mock()
        mock_cache_instance.clear.return_value = None
        mock_file_cache.return_value = mock_cache_instance

        api = ConcreteCachedAPI()
        api.clear_cache()
        
        # Проверяем, что метод clear_cache работает без ошибок
        assert True  # Если дошли до этой точки, метод выполнился успешно
