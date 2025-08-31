
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.cached_api import CachedAPI


class TestCachedAPI:
    """Тесты для CachedAPI"""

    def test_cached_api_initialization(self):
        """Тест инициализации CachedAPI"""
        api = CachedAPI()
        assert hasattr(api, 'cache_manager')
        assert api.cache_manager is not None

    @patch('src.api_modules.cached_api.CacheManager')
    def test_cached_api_with_cache_manager(self, mock_cache_manager):
        """Тест инициализации с кэш-менеджером"""
        mock_cm = Mock()
        mock_cache_manager.return_value = mock_cm
        
        api = CachedAPI()
        assert api.cache_manager == mock_cm

    def test_cached_api_abstract_methods(self):
        """Тест абстрактных методов CachedAPI"""
        api = CachedAPI()
        
        # Проверяем, что абстрактные методы определены
        assert hasattr(api, 'get_vacancies')
        assert hasattr(api, 'get_vacancy_by_id')

    @patch('src.utils.cache.CacheManager')
    def test_cache_integration(self, mock_cache_manager):
        """Тест интеграции с кэшем"""
        mock_cache = Mock()
        mock_cache_manager.return_value = mock_cache
        
        api = CachedAPI()
        
        # Проверяем, что кэш-менеджер правильно интегрирован
        assert api.cache_manager == mock_cache

    def test_cached_api_inheritance(self):
        """Тест наследования от BaseAPI"""
        from src.api_modules.base_api import BaseAPI
        
        api = CachedAPI()
        assert isinstance(api, BaseAPI)
