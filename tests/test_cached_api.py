import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
from pathlib import Path
from abc import ABC
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.cached_api import CachedAPI


class TestCachedAPI:
    """Тесты для CachedAPI"""

    @patch.multiple('src.api_modules.cached_api',
                   CacheManager=MagicMock(),
                   os=MagicMock(),
                   pathlib=MagicMock())
    def test_cached_api_initialization(self):
        """Тест инициализации CachedAPI"""
        api = CachedAPI()
        assert hasattr(api, 'cache_manager')
        assert api.cache_manager is not None

    @patch.multiple('src.api_modules.cached_api',
                   CacheManager=MagicMock(),
                   os=MagicMock(),
                   pathlib=MagicMock())
    def test_cached_api_with_cache_manager(self):
        """Тест инициализации с кэш-менеджером"""
        api = CachedAPI()
        assert hasattr(api, 'cache_manager')

    @patch.multiple('src.api_modules.cached_api',
                   CacheManager=MagicMock(),
                   os=MagicMock(),
                   pathlib=MagicMock())
    def test_cached_api_abstract_methods(self):
        """Тест абстрактных методов CachedAPI"""
        api = CachedAPI()

        # Проверяем, что абстрактные методы определены
        assert hasattr(api, 'get_vacancies')
        assert hasattr(api, 'get_vacancy_by_id')

    @patch.multiple('src.api_modules.cached_api',
                   CacheManager=MagicMock(),
                   os=MagicMock(),
                   pathlib=MagicMock())
    def test_cache_integration(self):
        """Тест интеграции с кэшем"""
        api = CachedAPI()

        # Проверяем, что кэш-менеджер правильно интегрирован
        assert hasattr(api, 'cache_manager')

    def test_cached_api_inheritance(self):
        """Тест наследования от BaseAPI"""
        # Проверяем что CachedAPI это абстрактный класс
        from abc import ABC
        assert issubclass(CachedAPI, ABC)