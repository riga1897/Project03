
"""
Полные тесты для модуля cached_api
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.api_modules.cached_api import CachedAPI
    from src.api_modules.base_api import BaseAPI
    CACHED_API_AVAILABLE = True
except ImportError:
    CACHED_API_AVAILABLE = False
    CachedAPI = object
    BaseAPI = object


class ConcreteCachedAPI(CachedAPI if CACHED_API_AVAILABLE else object):
    """Конкретная реализация CachedAPI для тестирования"""
    
    def __init__(self, cache_dir="test_cache", cache_ttl=3600):
        if CACHED_API_AVAILABLE:
            super().__init__(cache_dir, cache_ttl)
        self._test_response = []
        
    def _get_empty_response(self):
        """Возвращает пустой ответ"""
        return []
    
    def _validate_vacancy(self, vacancy):
        """Валидация вакансии"""
        return isinstance(vacancy, dict) and vacancy.get('id') is not None
    
    def get_vacancies(self, query, **kwargs):
        """Получение вакансий с кешированием"""
        if CACHED_API_AVAILABLE:
            return super().get_vacancies(query, **kwargs)
        return self._test_response
    
    def _make_request(self, url, params=None):
        """Симуляция запроса к API"""
        return self._test_response


class TestCachedAPIComplete:
    """Полные тесты для CachedAPI"""

    @pytest.fixture
    def mock_cache_dir(self, tmp_path):
        """Создание временной директории для кеша"""
        cache_dir = tmp_path / "test_cache"
        cache_dir.mkdir()
        return str(cache_dir)

    @pytest.fixture
    def cached_api(self, mock_cache_dir):
        """Создание экземпляра CachedAPI"""
        return ConcreteCachedAPI(cache_dir=mock_cache_dir, cache_ttl=3600)

    def test_init_default_values(self):
        """Тест инициализации с значениями по умолчанию"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        api = ConcreteCachedAPI()
        assert api.cache_dir == "test_cache"
        assert api.cache_ttl == 3600

    def test_init_custom_values(self, mock_cache_dir):
        """Тест инициализации с кастомными значениями"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        api = ConcreteCachedAPI(cache_dir=mock_cache_dir, cache_ttl=7200)
        assert api.cache_dir == mock_cache_dir
        assert api.cache_ttl == 7200

    @patch('os.makedirs')
    def test_ensure_cache_dir_exists_creation(self, mock_makedirs, cached_api):
        """Тест создания директории кеша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        with patch('os.path.exists', return_value=False):
            cached_api._ensure_cache_dir_exists()
            mock_makedirs.assert_called_once_with(cached_api.cache_dir, exist_ok=True)

    @patch('os.makedirs')
    def test_ensure_cache_dir_exists_already_exists(self, mock_makedirs, cached_api):
        """Тест когда директория уже существует"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        with patch('os.path.exists', return_value=True):
            cached_api._ensure_cache_dir_exists()
            mock_makedirs.assert_not_called()

    @patch('os.makedirs', side_effect=OSError("Permission denied"))
    def test_ensure_cache_dir_creation_error(self, mock_makedirs, cached_api):
        """Тест обработки ошибки создания директории"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        with patch('os.path.exists', return_value=False):
            cached_api._ensure_cache_dir_exists()  # Не должно вызывать исключение

    def test_get_cache_key_basic(self, cached_api):
        """Тест генерации ключа кеша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        key = cached_api._get_cache_key("python developer", per_page=50, page=0)
        assert isinstance(key, str)
        assert len(key) > 0

    def test_get_cache_key_with_params(self, cached_api):
        """Тест генерации ключа с параметрами"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        key1 = cached_api._get_cache_key("python", per_page=50)
        key2 = cached_api._get_cache_key("python", per_page=100)
        assert key1 != key2

    def test_get_cache_file_path(self, cached_api):
        """Тест получения пути к файлу кеша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        cache_key = "test_key"
        file_path = cached_api._get_cache_file_path(cache_key)
        expected_path = os.path.join(cached_api.cache_dir, f"{cached_api.__class__.__name__.lower()}_{cache_key}.json")
        assert file_path == expected_path

    @patch('builtins.open', new_callable=mock_open, read_data='{"data": [{"id": "1"}], "timestamp": 1234567890}')
    @patch('os.path.exists', return_value=True)
    def test_load_from_cache_valid(self, mock_exists, mock_file, cached_api):
        """Тест загрузки валидных данных из кеша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        with patch('time.time', return_value=1234567890 + 1800):  # В пределах TTL
            result = cached_api._load_from_cache("test_key")
            assert result == [{"id": "1"}]

    @patch('builtins.open', new_callable=mock_open, read_data='{"data": [{"id": "1"}], "timestamp": 1234567890}')
    @patch('os.path.exists', return_value=True)
    def test_load_from_cache_expired(self, mock_exists, mock_file, cached_api):
        """Тест загрузки устаревших данных из кеша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        with patch('time.time', return_value=1234567890 + 7200):  # Больше TTL
            result = cached_api._load_from_cache("test_key")
            assert result is None

    @patch('os.path.exists', return_value=False)
    def test_load_from_cache_not_exists(self, mock_exists, cached_api):
        """Тест когда файл кеша не существует"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        result = cached_api._load_from_cache("test_key")
        assert result is None

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('os.path.exists', return_value=True)
    def test_load_from_cache_invalid_json(self, mock_exists, mock_file, cached_api):
        """Тест обработки невалидного JSON"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        result = cached_api._load_from_cache("test_key")
        assert result is None

    @patch('builtins.open', side_effect=IOError("File error"))
    @patch('os.path.exists', return_value=True)
    def test_load_from_cache_io_error(self, mock_exists, mock_file, cached_api):
        """Тест обработки ошибки чтения файла"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        result = cached_api._load_from_cache("test_key")
        assert result is None

    @patch('builtins.open', new_callable=mock_open)
    @patch('time.time', return_value=1234567890)
    def test_save_to_cache_success(self, mock_time, mock_file, cached_api):
        """Тест успешного сохранения в кеш"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        data = [{"id": "1", "name": "Test"}]
        with patch.object(cached_api, '_ensure_cache_dir_exists'):
            cached_api._save_to_cache("test_key", data)
            
        mock_file.assert_called_once()
        written_data = json.loads(mock_file().write.call_args[0][0])
        assert written_data["data"] == data
        assert written_data["timestamp"] == 1234567890

    @patch('builtins.open', side_effect=IOError("Write error"))
    def test_save_to_cache_io_error(self, mock_file, cached_api):
        """Тест обработки ошибки записи в кеш"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        data = [{"id": "1"}]
        with patch.object(cached_api, '_ensure_cache_dir_exists'):
            cached_api._save_to_cache("test_key", data)  # Не должно вызывать исключение

    def test_filter_valid_vacancies_all_valid(self, cached_api):
        """Тест фильтрации валидных вакансий"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        vacancies = [
            {"id": "1", "name": "Python Developer"},
            {"id": "2", "name": "Java Developer"}
        ]
        result = cached_api._filter_valid_vacancies(vacancies)
        assert len(result) == 2

    def test_filter_valid_vacancies_mixed(self, cached_api):
        """Тест фильтрации смешанных данных"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        vacancies = [
            {"id": "1", "name": "Python Developer"},
            {"name": "Invalid vacancy"},  # Нет ID
            {"id": "2", "name": "Java Developer"}
        ]
        result = cached_api._filter_valid_vacancies(vacancies)
        assert len(result) == 2
        assert all(v["id"] in ["1", "2"] for v in result)

    def test_filter_valid_vacancies_empty(self, cached_api):
        """Тест фильтрации пустого списка"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        result = cached_api._filter_valid_vacancies([])
        assert result == []

    def test_filter_valid_vacancies_all_invalid(self, cached_api):
        """Тест фильтрации невалидных вакансий"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        vacancies = [
            {"name": "No ID"},
            None,
            "string",
            {}
        ]
        result = cached_api._filter_valid_vacancies(vacancies)
        assert result == []

    @patch.object(ConcreteCachedAPI, '_load_from_cache', return_value=[{"id": "1"}])
    def test_get_vacancies_from_cache(self, mock_load, cached_api):
        """Тест получения вакансий из кеша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        result = cached_api.get_vacancies("python")
        assert result == [{"id": "1"}]
        mock_load.assert_called_once()

    @patch.object(ConcreteCachedAPI, '_load_from_cache', return_value=None)
    @patch.object(ConcreteCachedAPI, '_save_to_cache')
    def test_get_vacancies_from_api(self, mock_save, mock_load, cached_api):
        """Тест получения вакансий через API"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        test_data = [{"id": "1", "name": "Test"}]
        cached_api._test_response = test_data
        
        result = cached_api.get_vacancies("python")
        assert result == test_data
        mock_save.assert_called_once()

    @patch.object(ConcreteCachedAPI, '_load_from_cache', return_value=None)
    @patch.object(ConcreteCachedAPI, '_make_request', side_effect=Exception("API Error"))
    def test_get_vacancies_api_error(self, mock_request, mock_load, cached_api):
        """Тест обработки ошибки API"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        result = cached_api.get_vacancies("python")
        assert result == []

    def test_clear_cache_success(self, cached_api, mock_cache_dir):
        """Тест очистки кеша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        # Создаем тестовые файлы
        test_file = os.path.join(mock_cache_dir, "test_file.json")
        with open(test_file, 'w') as f:
            f.write('{"test": "data"}')
        
        cached_api.clear_cache()
        assert not os.path.exists(test_file)

    @patch('shutil.rmtree', side_effect=OSError("Permission denied"))
    def test_clear_cache_error(self, mock_rmtree, cached_api):
        """Тест обработки ошибки очистки кеша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        cached_api.clear_cache()  # Не должно вызывать исключение

    def test_cache_statistics_empty(self, cached_api):
        """Тест статистики пустого кеша"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        stats = cached_api.get_cache_statistics()
        assert stats["total_files"] == 0
        assert stats["total_size_mb"] == 0.0

    def test_cache_statistics_with_files(self, cached_api, mock_cache_dir):
        """Тест статистики кеша с файлами"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        # Создаем тестовый файл
        test_file = os.path.join(mock_cache_dir, "concretecachedapi_test.json")
        with open(test_file, 'w') as f:
            f.write('{"test": "data"}')
        
        stats = cached_api.get_cache_statistics()
        assert stats["total_files"] > 0
        assert stats["total_size_mb"] > 0

    @patch('os.listdir', side_effect=OSError("Directory error"))
    def test_cache_statistics_error(self, mock_listdir, cached_api):
        """Тест обработки ошибки получения статистики"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        stats = cached_api.get_cache_statistics()
        assert stats["total_files"] == 0
        assert stats["total_size_mb"] == 0.0

    def test_abstract_methods_implemented(self, cached_api):
        """Тест что абстрактные методы реализованы"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        assert hasattr(cached_api, '_get_empty_response')
        assert hasattr(cached_api, '_validate_vacancy')
        assert callable(cached_api._get_empty_response)
        assert callable(cached_api._validate_vacancy)

    def test_inheritance_structure(self):
        """Тест структуры наследования"""
        if not CACHED_API_AVAILABLE:
            pytest.skip("CachedAPI not available")
        
        assert issubclass(CachedAPI, BaseAPI)
        assert hasattr(CachedAPI, 'cache_dir')
        assert hasattr(CachedAPI, 'cache_ttl')
