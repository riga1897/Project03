import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
from pathlib import Path
from abc import ABC

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.cached_api import CachedAPI


class TestCachedAPIImplementation(CachedAPI):
    """Тестовая реализация CachedAPI для тестирования"""

    def __init__(self, cache_dir="test_cache"):
        super().__init__(cache_dir)

    def _get_empty_response(self):
        return {"items": []}

    def _validate_vacancy(self, vacancy):
        return True

    def get_vacancies(self, search_query, **kwargs):
        """Реализация абстрактного метода get_vacancies"""
        return [{"id": "1", "title": "Test Vacancy", "url": "https://test.com"}]

    def get_vacancies_page(self, search_query, page=0, **kwargs):
        """Реализация абстрактного метода get_vacancies_page"""
        return {"items": [{"id": "1", "title": "Test Vacancy"}], "pages": 1}


class TestCachedAPI:
    """Тесты для CachedAPI с консолидированными моками"""

    @patch('src.utils.cache.FileCache')
    def test_cached_api_initialization(self, mock_file_cache):
        """Тест инициализации CachedAPI"""
        mock_cache_instance = Mock()
        mock_file_cache.return_value = mock_cache_instance

        api = TestCachedAPIImplementation()
        assert hasattr(api, 'cache')

    @patch('src.utils.cache.FileCache')
    def test_cached_api_with_cache_manager(self, mock_file_cache):
        """Тест CachedAPI с кэш менеджером"""
        mock_cache_instance = Mock()
        mock_file_cache.return_value = mock_cache_instance

        api = TestCachedAPIImplementation()
        assert api.cache is not None

    @patch('src.utils.cache.FileCache')
    def test_cached_api_abstract_methods(self, mock_file_cache):
        """Тест абстрактных методов CachedAPI"""
        api = TestCachedAPIImplementation()

        # Тестируем что абстрактные методы реализованы
        empty_response = api._get_empty_response()
        assert isinstance(empty_response, dict)

        is_valid = api._validate_vacancy({"test": "data"})
        assert isinstance(is_valid, bool)

    @patch('src.utils.cache.FileCache')
    def test_cache_integration(self, mock_file_cache):
        """Тест интеграции с кэшем"""
        mock_cache_instance = Mock()
        mock_cache_instance.get.return_value = None
        mock_cache_instance.set.return_value = None
        mock_file_cache.return_value = mock_cache_instance

        api = TestCachedAPIImplementation()

        # Проверяем что кэш используется
        assert api.cache is not None

    @patch('src.utils.cache.FileCache')
    def test_clear_cache_method(self, mock_file_cache):
        """Тест метода очистки кэша"""
        mock_cache_instance = Mock()
        mock_cache_instance.clear.return_value = None
        mock_file_cache.return_value = mock_cache_instance

        api = TestCachedAPIImplementation()
        
        # Мокаем все методы кэширования для полной изоляции
        with patch.object(api, '_get_cache_key', return_value='test_key'):
            with patch.object(api, '_cache', mock_cache_instance):
                api.clear_cache("test")

        # Проверяем что метод clear был вызван
        mock_cache_instance.clear.assert_called_once()