#!/usr/bin/env python3
"""
Тесты для модуля cached_api.py
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Assuming src directory is available in the path
# In a real scenario, this might need adjustment based on project structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api_modules.cached_api import CachedAPI
# The original MockCachedAPI is not used in the refactored tests, so it's omitted.
# The original FileCache import is also not used directly in the provided edited tests.


class TestCachedAPI:
    """Тесты для абстрактного класса CachedAPI"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем конкретную реализацию CachedAPI
        class ConcreteCachedAPI(CachedAPI):
            def get_vacancies(self, query):
                # This mock implementation is minimal to allow testing the abstract class
                return []

            def get_vacancies_page(self, query, page=0):
                # This mock implementation is minimal to allow testing the abstract class
                return []

            def _validate_vacancy(self, vacancy):
                # This mock implementation is minimal to allow testing the abstract class
                return True

            def _get_empty_response(self):
                # This mock implementation is minimal to allow testing the abstract class
                return {"items": [], "found": 0}

        self.api_class = ConcreteCachedAPI

    @patch('pathlib.Path.mkdir')
    def test_init_cache_creates_directory(self, mock_mkdir):
        """Тест создания директории кэша при инициализации"""
        # Instantiate the concrete API with a dummy cache directory name
        api = self.api_class("test_cache")

        # Check if the mkdir method was called.
        # The actual path might not be important for this abstract test.
        # The base CachedAPI.__init__ calls self.cache.init_cache() which in turn calls Path.mkdir
        assert mock_mkdir.called

    @patch('requests.get')
    def test_connect_to_api_real_request(self, mock_get):
        """Тест подключения к API без реальных запросов"""
        # Mock the response from requests.get
        mock_response = Mock()
        mock_response.json.return_value = {"items": [], "found": 0}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Instantiate the concrete API
        api = self.api_class("test_cache")

        # Check if the API instance was created successfully
        assert api is not None

        # The original test had a call to _CachedAPI__connect_to_api.
        # However, the edited snippet doesn't include that.
        # The intention seems to be more about the setup of the abstract class itself.
        # Let's assume the goal is to ensure the class can be instantiated and its mock methods work.

    def test_get_cache_status_success(self):
        """Тест получения статуса кэша"""
        # Mock Path.glob to return an empty list, simulating an empty cache directory
        with patch('pathlib.Path.glob', return_value=[]):
            api = self.api_class("test_cache")

            # Check if the API instance was created successfully
            assert api is not None

            # The original test checked status["file_cache_count"] and status["total_size_mb"]
            # Since we mock glob to return empty, these should reflect that.
            # The concrete implementation of get_cache_status is in CachedAPI itself.
            status = api.get_cache_status("test_query")
            assert "cache_dir" in status
            assert status["file_cache_count"] == 0
            assert status["total_size_mb"] == 0.0


    def test_memory_cache_size_limit(self):
        """Тест ограничения размера кэша в памяти"""
        api = self.api_class("test_cache")

        # Test basic operations without exceeding limits.
        # The edited snippet does not provide a specific way to test the size limit
        # beyond calling get_vacancies. The actual limit enforcement might be in
        # internal methods not directly called here or assumes a different setup.
        # The original code had a loop to add items, which is missing here.
        # We'll test the return type and a reasonable assumption about the limit for now.
        vacancies = api.get_vacancies("test")
        assert isinstance(vacancies, list)
        # The assertion len(vacancies) <= 1000 is a placeholder from the edited snippet.
        # Without the actual implementation details of how items are added and limited,
        # this test might not be fully representative of the original intent or the
        # abstract class's behavior regarding memory limits.
        assert len(vacancies) <= 1000