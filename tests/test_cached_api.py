import json
import os
import sys
from abc import ABC
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.api_modules.cached_api import CachedAPI


class CachedAPIImplementation(CachedAPI):
    """Тестовая реализация CachedAPI для тестирования"""

    def __init__(self):
        super().__init__()
        self.test_data = []

    def _fetch_data(self, endpoint, params=None):
        """Тестовая реализация получения данных"""
        return {"test": "data"}

    def get_vacancies(self, query, **kwargs):
        """Тестовая реализация получения вакансий"""
        return self.test_data


class TestCachedAPI:
    """Тесты для CachedAPI с консолидированными моками"""

    @patch("src.utils.cache.FileCache")
    def test_cached_api_initialization(self, mock_file_cache):
        """Тест инициализации CachedAPI"""
        mock_cache_instance = Mock()
        mock_file_cache.return_value = mock_cache_instance

        api = CachedAPIImplementation()
        assert hasattr(api, "cache")

    @patch("src.utils.cache.FileCache")
    def test_cached_api_with_cache_manager(self, mock_file_cache):
        """Тест CachedAPI с кэш менеджером"""
        mock_cache_instance = Mock()
        mock_file_cache.return_value = mock_cache_instance

        api = CachedAPIImplementation()
        assert api.cache is not None

    @patch("src.utils.cache.FileCache")
    def test_cached_api_abstract_methods(self, mock_file_cache):
        """Тест абстрактных методов CachedAPI"""
        api = CachedAPIImplementation()

        # Проверяем что абстрактные методы реализованы
        empty_response = api._get_empty_response()
        assert isinstance(empty_response, dict)

        is_valid = api._validate_vacancy({"test": "data"})
        assert isinstance(is_valid, bool)

    @patch("src.utils.cache.FileCache")
    def test_cache_integration(self, mock_file_cache):
        """Тест интеграции с кэшем"""
        mock_cache_instance = Mock()
        mock_cache_instance.get.return_value = None
        mock_cache_instance.set.return_value = None
        mock_file_cache.return_value = mock_cache_instance

        api = CachedAPIImplementation()

        # Проверяем что кэш используется
        assert api.cache is not None

    @patch("src.utils.cache.FileCache")
    def test_clear_cache_method(self, mock_file_cache):
        """Тест метода очистки кэша"""
        mock_cache_instance = Mock()
        mock_cache_instance.clear.return_value = None
        mock_file_cache.return_value = mock_cache_instance

        api = CachedAPIImplementation()

        # Мокаем cache атрибут
        api.cache = mock_cache_instance

        # Тестируем метод очистки кэша
        api.clear_cache("test")

        # Проверяем что метод clear был вызван
        mock_cache_instance.clear.assert_called_once()