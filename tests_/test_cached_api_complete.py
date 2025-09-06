"""
Полные тесты для кэшированного API
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.api_modules.cached_api import CachedAPI
    from src.utils.cache import FileCache
    CACHED_API_AVAILABLE = True
except ImportError:
    CACHED_API_AVAILABLE = False
    CachedAPI = object
    FileCache = object


class ConcreteCachedAPI(CachedAPI if CACHED_API_AVAILABLE else object):
    """Конкретная реализация CachedAPI для тестирования"""

    def __init__(self, cache_dir="test_cache"):
        if CACHED_API_AVAILABLE:
            super().__init__(cache_dir)

    def _get_empty_response(self):
        """Возвращает пустой ответ"""
        return {"items": [], "found": 0}

    def _validate_vacancy(self, vacancy):
        """Валидация вакансии"""
        return isinstance(vacancy, dict) and "id" in vacancy

    def get_vacancies_page(self, search_query, page=0, **kwargs):
        """Получение одной страницы вакансий"""
        return [{"id": f"test_{page}", "title": search_query}]

    def get_vacancies(self, search_query, **kwargs):
        """Получение всех вакансий"""
        return [{"id": "test", "title": search_query}]


class TestCachedAPI:
    """Тесты для кэшированного API"""

    @pytest.fixture
    def cached_api(self):
        """Фикстура кэшированного API"""
        if not CACHED_API_AVAILABLE:
            return Mock()

        with patch('src.utils.cache.FileCache'), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.exists', return_value=True):
            return ConcreteCachedAPI("test_cache_dir")

    def test_init(self, cached_api):
        """Тест инициализации"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        assert cached_api is not None
        assert hasattr(cached_api, 'cache_dir')
        assert hasattr(cached_api, 'cache')

    def test_get_empty_response(self, cached_api):
        """Тест получения пустого ответа"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        result = cached_api._get_empty_response()
        assert isinstance(result, dict)
        assert "items" in result
        assert result["items"] == []
        assert result["found"] == 0

    def test_validate_vacancy(self, cached_api):
        """Тест валидации вакансии"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        valid_vacancy = {"id": "123", "title": "Test"}
        invalid_vacancy = {"title": "Test"}

        assert cached_api._validate_vacancy(valid_vacancy) == True
        assert cached_api._validate_vacancy(invalid_vacancy) == False

    def test_get_vacancies_page(self, cached_api):
        """Тест получения страницы вакансий"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        result = cached_api.get_vacancies_page("Python", page=0)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Python"
        assert result[0]["id"] == "test_0"

    def test_get_vacancies(self, cached_api):
        """Тест получения вакансий"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        result = cached_api.get_vacancies("Python")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Python"
        assert result[0]["id"] == "test"

    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.exists')
    def test_get_cache_status(self, mock_exists, mock_glob, cached_api):
        """Тест получения статуса кэша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        mock_exists.return_value = True
        mock_glob.return_value = []

        result = cached_api.get_cache_status("test")
        assert isinstance(result, dict)
        assert "cache_dir" in result
        assert "file_cache_count" in result

    def test_clear_cache(self, cached_api):
        """Тест очистки кэша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        with patch.object(cached_api.cache, 'clear') as mock_clear:
            cached_api.clear_cache("test")
            mock_clear.assert_called_once_with("test")

    def test_is_complete_response(self, cached_api):
        """Тест проверки полноты ответа"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        complete_response = {
            "items": [{"id": "1", "title": "Test"}],
            "found": 1
        }
        incomplete_response = {
            "items": [],
            "found": 10
        }
        invalid_response = "invalid"

        assert cached_api._is_complete_response(complete_response, {"page": 0, "per_page": 20}) == True
        assert cached_api._is_complete_response(incomplete_response, {"page": 0, "per_page": 20}) == False
        assert cached_api._is_complete_response(invalid_response, {}) == False

    def test_validate_response_structure(self, cached_api):
        """Тест валидации структуры ответа"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        valid_response = {
            "items": [{"id": "1", "title": "Test"}]
        }
        invalid_response = {
            "items": "not a list"
        }
        not_dict_response = "not a dict"

        assert cached_api._validate_response_structure(valid_response) == True
        assert cached_api._validate_response_structure(invalid_response) == False
        assert cached_api._validate_response_structure(not_dict_response) == False

    @patch('time.time', return_value=1000)
    def test_cached_api_request(self, mock_time, cached_api):
        """Тест кэшированного запроса API"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        url = "test_url"
        params = {"test": "param"}
        api_prefix = "test"

        # Первый вызов - данных в кэше нет
        result = cached_api._cached_api_request(url, params, api_prefix)
        assert result is None

        # Добавляем данные в кэш памяти
        cached_api._memory_cache = {}
        cached_api._cache_timestamps = {}
        import json
        cache_key = f"{url}#{json.dumps(params, sort_keys=True)}"
        cached_api._memory_cache[cache_key] = (1000, {"test": "data"})
        cached_api._cache_timestamps[cache_key] = 1000

        # Второй вызов - данные должны быть из кэша
        result = cached_api._cached_api_request(url, params, api_prefix)
        assert result == {"test": "data"}

    @patch('time.time', return_value=2000)  # Устаревшие данные
    def test_cached_api_request_expired(self, mock_time, cached_api):
        """Тест кэшированного запроса с устаревшими данными"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        url = "test_url"
        params = {"test": "param"}
        api_prefix = "test"

        # Добавляем устаревшие данные в кэш
        cached_api._memory_cache = {}
        cached_api._cache_timestamps = {}
        import json
        cache_key = f"{url}#{json.dumps(params, sort_keys=True)}"
        cached_api._memory_cache[cache_key] = (1000, {"test": "old_data"})  # Старые данные
        cached_api._cache_timestamps[cache_key] = 1000

        # Вызов должен вернуть None, так как данные устарели
        result = cached_api._cached_api_request(url, params, api_prefix)
        assert result is None
        assert cache_key not in cached_api._memory_cache  # Устаревшие данные удалены

    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_with_memory_cache(self, mock_logger, cached_api):
        """Тест подключения к API с использованием кэша памяти"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        # Мокаем кэш памяти для возврата данных
        mock_data = {"items": [{"id": "1"}], "found": 1}
        with patch.object(cached_api, '_cached_api_request', return_value=mock_data):
            result = cached_api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test")
            assert result == mock_data

    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_with_file_cache(self, mock_logger, cached_api):
        """Тест подключения к API с использованием файлового кэша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        # Мокаем кэш памяти (возвращает None) и файловый кэш
        mock_file_data = {"data": {"items": [{"id": "2"}], "found": 1}}
        with patch.object(cached_api, '_cached_api_request', return_value=None), \
             patch.object(cached_api.cache, 'load_response', return_value=mock_file_data):
            result = cached_api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test")
            assert result == mock_file_data["data"]

    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_real_request(self, mock_logger, cached_api):
        """Тест реального запроса к API"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        # Мокаем отсутствие кэшей и реальный запрос
        mock_api_data = {"items": [{"id": "3"}], "found": 1}
        mock_connector = Mock()
        mock_connector._APIConnector__connect = Mock(return_value=mock_api_data)
        cached_api.connector = mock_connector

        with patch.object(cached_api, '_cached_api_request', return_value=None), \
             patch.object(cached_api.cache, 'load_response', return_value=None), \
             patch.object(cached_api, '_is_complete_response', return_value=True), \
             patch.object(cached_api, '_validate_response_structure', return_value=True):

            result = cached_api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test")
            assert result == mock_api_data
            mock_connector._APIConnector__connect.assert_called_once()

    def test_connect_to_api_error_handling(self, cached_api):
        """Тест обработки ошибок при подключении к API"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")

        # Мокаем ошибку соединения
        mock_connector = Mock()
        mock_connector._APIConnector__connect = Mock(side_effect=ConnectionError("Connection failed"))
        cached_api.connector = mock_connector

        with patch.object(cached_api, '_cached_api_request', return_value=None), \
             patch.object(cached_api.cache, 'load_response', return_value=None):

            result = cached_api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test")
            assert result == cached_api._get_empty_response()


class TestCachedAPIImportError:
    """Тесты обработки ошибок импорта CachedAPI"""

    def test_cached_api_not_available(self):
        """Тест когда CachedAPI недоступен"""
        # Проверяем что тест не падает когда модуль недоступен
        if not CACHED_API_AVAILABLE:
            assert CachedAPI == object