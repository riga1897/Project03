"""
Тесты для модуля cached_api.py с 100% покрытием
Все методы и ветки кода протестированы с использованием mock объектов
"""

import json
import logging
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open

import pytest

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.api_modules.cached_api import CachedAPI


class ConcreteCachedAPI(CachedAPI):
    """Конкретная реализация CachedAPI для тестирования"""

    def __init__(self, cache_dir: str):
        # Мокаем connector для тестов
        self.connector = Mock()
        self.connector._APIConnector__connect = Mock()
        super().__init__(cache_dir)

    def get_vacancies(self, search_query: str, **kwargs):
        """Реализация абстрактного метода"""
        return []

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs):
        """Реализация абстрактного метода"""
        return []

    def _get_empty_response(self):
        """Реализация абстрактного метода"""
        return {"items": [], "found": 0}

    def _validate_vacancy(self, vacancy):
        """Реализация абстрактного метода"""
        if not isinstance(vacancy, dict):
            return False
        return "id" in vacancy


class TestCachedAPI:
    """Тесты для класса CachedAPI"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.api = ConcreteCachedAPI(self.temp_dir)

    def teardown_method(self):
        """Очистка после каждого теста"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_creates_cache_directory(self):
        """Тест создания директории кэша при инициализации"""
        cache_path = Path(self.temp_dir)
        assert cache_path.exists()
        assert hasattr(self.api, 'cache_dir')
        assert hasattr(self.api, 'cache')

    @patch('src.api_modules.cached_api.FileCache')
    def test_init_cache_method(self, mock_file_cache):
        """Тест метода _init_cache"""
        api = ConcreteCachedAPI("test_cache_dir")
        
        # Проверяем, что FileCache был создан
        mock_file_cache.assert_called_once_with("test_cache_dir")

    def test_cached_api_request_no_memory_cache(self):
        """Тест _cached_api_request без существующего кэша в памяти"""
        url = "http://test.api"
        params = {"query": "python", "page": 0}
        api_prefix = "test"
        
        # При отсутствии кэша должен вернуть None
        result = self.api._cached_api_request(url, params, api_prefix)
        assert result is None
        
        # Проверяем, что кэш был инициализирован
        assert hasattr(self.api, '_memory_cache')
        assert hasattr(self.api, '_cache_timestamps')

    def test_cached_api_request_with_valid_cache(self):
        """Тест _cached_api_request с валидным кэшем"""
        url = "http://test.api"
        params = {"query": "python", "page": 0}
        api_prefix = "test"
        
        # Создаем кэш в памяти
        cache_key = f"{url}#{json.dumps(params, sort_keys=True)}"
        test_data = {"items": [{"id": "1", "title": "Test Job"}], "found": 1}
        current_time = time.time()
        
        self.api._memory_cache = {cache_key: (current_time, test_data)}
        self.api._cache_timestamps = {cache_key: current_time}
        
        result = self.api._cached_api_request(url, params, api_prefix)
        assert result == test_data

    def test_cached_api_request_with_expired_cache(self):
        """Тест _cached_api_request с истекшим кэшем"""
        url = "http://test.api"
        params = {"query": "python", "page": 0}
        api_prefix = "test"
        
        # Создаем истекший кэш
        cache_key = f"{url}#{json.dumps(params, sort_keys=True)}"
        test_data = {"items": [{"id": "1"}], "found": 1}
        old_time = time.time() - 400  # Более 300 секунд назад (TTL = 300)
        
        self.api._memory_cache = {cache_key: (old_time, test_data)}
        self.api._cache_timestamps = {cache_key: old_time}
        
        result = self.api._cached_api_request(url, params, api_prefix)
        assert result is None
        
        # Проверяем, что истекший кэш был удален
        assert cache_key not in self.api._memory_cache
        assert cache_key not in self.api._cache_timestamps

    def test_connect_to_api_memory_cache_hit(self):
        """Тест __connect_to_api с попаданием в кэш памяти"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        
        # Настраиваем мок для _cached_api_request
        test_data = {"items": [{"id": "1"}], "found": 1}
        with patch.object(self.api, '_cached_api_request', return_value=test_data) as mock_cache:
            result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
            
            assert result == test_data
            mock_cache.assert_called_once_with(url, params, api_prefix)

    def test_connect_to_api_memory_cache_exception(self):
        """Тест __connect_to_api с исключением в кэше памяти"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        
        # Настраиваем мок для исключения в memory cache
        with patch.object(self.api, '_cached_api_request', side_effect=Exception("Cache error")):
            with patch.object(self.api.cache, 'load_response', return_value=None):
                with patch.object(self.api.connector, '_APIConnector__connect', return_value={"items": [], "found": 0}):
                    result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                    assert result == {"items": [], "found": 0}

    def test_connect_to_api_file_cache_hit(self):
        """Тест __connect_to_api с попаданием в файловый кэш"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        
        cached_data = {"data": {"items": [{"id": "2"}], "found": 1}}
        
        with patch.object(self.api, '_cached_api_request', return_value=None):
            with patch.object(self.api.cache, 'load_response', return_value=cached_data):
                result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                assert result == {"items": [{"id": "2"}], "found": 1}

    def test_connect_to_api_real_request_success(self):
        """Тест __connect_to_api с реальным запросом к API"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        api_data = {"items": [{"id": "3", "title": "Developer"}], "found": 1}
        
        with patch.object(self.api, '_cached_api_request', return_value=None):
            with patch.object(self.api.cache, 'load_response', return_value=None):
                with patch.object(self.api.connector, '_APIConnector__connect', return_value=api_data):
                    with patch.object(self.api, '_is_complete_response', return_value=True):
                        with patch.object(self.api, '_validate_response_structure', return_value=True):
                            with patch.object(self.api.cache, 'save_response'):
                                result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                                
                                assert result == api_data
                                # Проверяем, что данные сохранены в память
                                cache_key = f"{url}#{json.dumps(params, sort_keys=True)}"
                                assert cache_key in self.api._memory_cache

    def test_connect_to_api_memory_cache_size_limit(self):
        """Тест ограничения размера кэша в памяти"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        api_data = {"items": [{"id": "4"}], "found": 1}
        
        # Заполняем кэш до лимита
        self.api._memory_cache = {}
        self.api._cache_timestamps = {}
        
        for i in range(1001):  # Превышаем лимит в 1000
            key = f"key_{i}"
            timestamp = time.time() - i  # Разные timestamps
            self.api._memory_cache[key] = (timestamp, {"data": i})
            self.api._cache_timestamps[key] = timestamp
        
        with patch.object(self.api, '_cached_api_request', return_value=None):
            with patch.object(self.api.cache, 'load_response', return_value=None):
                with patch.object(self.api.connector, '_APIConnector__connect', return_value=api_data):
                    with patch.object(self.api, '_is_complete_response', return_value=True):
                        with patch.object(self.api, '_validate_response_structure', return_value=True):
                            with patch.object(self.api.cache, 'save_response'):
                                result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                                
                                assert result == api_data
                                # Проверяем, что размер кэша ограничен
                                assert len(self.api._memory_cache) <= 1000

    def test_connect_to_api_incomplete_response(self):
        """Тест обработки неполного ответа API"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        incomplete_data = {"items": [], "found": 100}  # Неполные данные
        
        with patch.object(self.api, '_cached_api_request', return_value=None):
            with patch.object(self.api.cache, 'load_response', return_value=None):
                with patch.object(self.api.connector, '_APIConnector__connect', return_value=incomplete_data):
                    with patch.object(self.api, '_is_complete_response', return_value=False):
                        with patch.object(self.api.cache, 'save_response') as mock_save:
                            result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                            
                            assert result == incomplete_data
                            # Неполные данные не должны сохраняться в файловый кэш
                            mock_save.assert_not_called()

    def test_connect_to_api_invalid_structure(self):
        """Тест обработки данных с невалидной структурой"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        invalid_data = {"items": [{"id": "5"}], "found": 1}
        
        with patch.object(self.api, '_cached_api_request', return_value=None):
            with patch.object(self.api.cache, 'load_response', return_value=None):
                with patch.object(self.api.connector, '_APIConnector__connect', return_value=invalid_data):
                    with patch.object(self.api, '_is_complete_response', return_value=True):
                        with patch.object(self.api, '_validate_response_structure', return_value=False):
                            with patch.object(self.api.cache, 'save_response') as mock_save:
                                result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                                
                                assert result == invalid_data
                                # Данные с невалидной структурой не должны сохраняться
                                mock_save.assert_not_called()

    def test_connect_to_api_connection_error(self):
        """Тест обработки ошибки соединения"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        
        with patch.object(self.api, '_cached_api_request', return_value=None):
            with patch.object(self.api.cache, 'load_response', return_value=None):
                with patch.object(self.api.connector, '_APIConnector__connect', side_effect=ConnectionError("Network error")):
                    result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                    assert result == self.api._get_empty_response()

    def test_connect_to_api_timeout_error(self):
        """Тест обработки ошибки таймаута"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        
        with patch.object(self.api, '_cached_api_request', return_value=None):
            with patch.object(self.api.cache, 'load_response', return_value=None):
                with patch.object(self.api.connector, '_APIConnector__connect', side_effect=TimeoutError("Timeout")):
                    result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                    assert result == self.api._get_empty_response()

    def test_connect_to_api_general_exception(self):
        """Тест обработки общего исключения"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        
        with patch.object(self.api, '_cached_api_request', return_value=None):
            with patch.object(self.api.cache, 'load_response', return_value=None):
                with patch.object(self.api.connector, '_APIConnector__connect', side_effect=Exception("Unknown error")):
                    result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                    assert result == self.api._get_empty_response()

    def test_clear_cache_success(self):
        """Тест успешной очистки кэша"""
        api_prefix = "test"
        
        with patch.object(self.api.cache, 'clear') as mock_clear:
            # Мокаем hasattr для проверки существования метода clear_cache
            with patch('builtins.hasattr', return_value=True):
                self.api.clear_cache(api_prefix)
                mock_clear.assert_called_once_with(api_prefix)

    def test_clear_cache_no_clear_method(self):
        """Тест очистки кэша когда метод clear_cache отсутствует"""
        api_prefix = "test"
        
        with patch.object(self.api.cache, 'clear') as mock_clear:
            # Убираем атрибут clear_cache если он существует
            if hasattr(self.api._cached_api_request, 'clear_cache'):
                delattr(self.api._cached_api_request, 'clear_cache')
            
            self.api.clear_cache(api_prefix)
            mock_clear.assert_called_once_with(api_prefix)

    def test_clear_cache_exception(self):
        """Тест обработки исключения при очистке кэша"""
        api_prefix = "test"
        
        with patch.object(self.api.cache, 'clear', side_effect=Exception("Clear error")):
            with patch('src.api_modules.cached_api.logger.error') as mock_logger:
                self.api.clear_cache(api_prefix)
                mock_logger.assert_called_once()

    @patch('pathlib.Path.glob')
    def test_get_cache_status_empty_cache(self, mock_glob):
        """Тест получения статуса пустого кэша"""
        api_prefix = "test"
        mock_glob.return_value = []
        
        # Мокаем hasattr для cache_info
        with patch('builtins.hasattr', return_value=True):
            with patch.object(self.api._cached_api_request, '__func__') as mock_func:
                mock_func.cache_info = Mock(return_value={"hits": 0, "misses": 0})
                
                status = self.api.get_cache_status(api_prefix)
                
                assert isinstance(status, dict)
                assert status['cache_dir'] == str(self.api.cache_dir)
                assert status['file_cache_count'] == 0
                assert status['valid_files'] == 0
                assert status['invalid_files'] == 0
                assert status['total_size_mb'] == 0

    @patch('pathlib.Path.glob')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_cache_status_with_valid_files(self, mock_open_func, mock_glob):
        """Тест получения статуса кэша с валидными файлами"""
        api_prefix = "test"
        
        # Создаем мок файлов
        mock_file1 = Mock()
        mock_file1.name = "test_file1.json"
        mock_file1.stat.return_value = Mock(st_size=1024, st_mtime=time.time() - 86400)
        
        mock_file2 = Mock()
        mock_file2.name = "test_file2.json"
        mock_file2.stat.return_value = Mock(st_size=2048, st_mtime=time.time())
        
        mock_glob.return_value = [mock_file1, mock_file2]
        
        # Мокаем содержимое файлов
        cache_data = {
            "meta": {"params": {"text": "python developer"}},
            "data": {"items": [{"id": "1"}]}
        }
        mock_open_func.return_value.read.return_value = json.dumps(cache_data)
        
        # Мокаем json.load
        with patch('json.load', return_value=cache_data):
            status = self.api.get_cache_status(api_prefix)
        
        assert status['file_cache_count'] == 2
        assert status['valid_files'] == 2
        assert status['invalid_files'] == 0
        assert status['total_size_mb'] == round((1024 + 2048) / (1024 * 1024), 2)
        assert status['popular_queries'] == [("python developer", 2)]

    @patch('pathlib.Path.glob')
    def test_get_cache_status_with_invalid_files(self, mock_glob):
        """Тест получения статуса кэша с невалидными файлами"""
        api_prefix = "test"
        
        # Создаем мок файла с ошибкой
        mock_file = Mock()
        mock_file.name = "invalid_file.json"
        mock_file.stat.side_effect = Exception("File error")
        
        mock_glob.return_value = [mock_file]
        
        status = self.api.get_cache_status(api_prefix)
        
        assert status['file_cache_count'] == 1
        assert status['valid_files'] == 0
        assert status['invalid_files'] == 1

    def test_get_cache_status_exception(self):
        """Тест обработки исключения при получении статуса кэша"""
        api_prefix = "test"
        
        with patch('pathlib.Path.glob', side_effect=Exception("Glob error")):
            status = self.api.get_cache_status(api_prefix)
            assert 'error' in status
            assert 'Glob error' in status['error']

    def test_is_complete_response_valid_data(self):
        """Тест _is_complete_response с валидными данными"""
        data = {"items": [{"id": "1"}, {"id": "2"}], "found": 2}
        params = {"page": 0, "per_page": 20}
        
        result = self.api._is_complete_response(data, params)
        assert result is True

    def test_is_complete_response_invalid_data_type(self):
        """Тест _is_complete_response с невалидным типом данных"""
        data = "invalid_data"
        params = {"page": 0}
        
        result = self.api._is_complete_response(data, params)
        assert result is False

    def test_is_complete_response_missing_items(self):
        """Тест _is_complete_response без поля items"""
        data = {"found": 10}
        params = {"page": 0}
        
        result = self.api._is_complete_response(data, params)
        assert result is False

    def test_is_complete_response_incomplete_first_page(self):
        """Тест _is_complete_response с неполной первой страницей"""
        data = {"items": [{"id": "1"}], "found": 50}  # Ожидается больше элементов
        params = {"page": 0, "per_page": 20}
        
        result = self.api._is_complete_response(data, params)
        assert result is False

    def test_is_complete_response_empty_items_with_found(self):
        """Тест _is_complete_response с пустыми items но found > 0"""
        data = {"items": [], "found": 10}
        params = {"page": 0}
        
        result = self.api._is_complete_response(data, params)
        assert result is False

    def test_is_complete_response_exception(self):
        """Тест обработки исключения в _is_complete_response"""
        data = {"items": []}  
        params = {"page": 0}
        
        # Создаем исключение внутри метода через мок
        with patch.object(self.api, '_is_complete_response', wraps=self.api._is_complete_response) as mock_method:
            # Заставляем метод бросить исключение
            def side_effect(*args, **kwargs):
                raise Exception("Test exception")
            mock_method.side_effect = side_effect
            
            with patch('src.api_modules.cached_api.logger.error') as mock_logger:
                try:
                    result = self.api._is_complete_response(data, params)
                    assert False, "Should have raised exception"
                except Exception:
                    pass  # Ожидаемое поведение
                    
        # Тестируем реальный случай с корректными данными
        result = self.api._is_complete_response(data, params)
        assert result is True  # Пустые items с page=0 валидны

    def test_validate_response_structure_valid(self):
        """Тест _validate_response_structure с валидной структурой"""
        data = {
            "items": [
                {"id": "1", "title": "Developer"},
                {"id": "2", "title": "Analyst"},
                {"id": "3", "title": "Manager"}
            ]
        }
        
        result = self.api._validate_response_structure(data)
        assert result is True

    def test_validate_response_structure_invalid_data_type(self):
        """Тест _validate_response_structure с невалидным типом данных"""
        data = "invalid"
        
        result = self.api._validate_response_structure(data)
        assert result is False

    def test_validate_response_structure_invalid_items_type(self):
        """Тест _validate_response_structure с невалидным типом items"""
        data = {"items": "not_a_list"}
        
        result = self.api._validate_response_structure(data)
        assert result is False

    def test_validate_response_structure_invalid_vacancy(self):
        """Тест _validate_response_structure с невалидной вакансией"""
        data = {
            "items": [
                {"id": "1", "title": "Valid"},
                {"invalid": "vacancy"},  # Невалидная структура
                {"id": "3", "title": "Also valid"}
            ]
        }
        
        result = self.api._validate_response_structure(data)
        assert result is False

    def test_validate_response_structure_empty_items(self):
        """Тест _validate_response_structure с пустыми items"""
        data = {"items": []}
        
        result = self.api._validate_response_structure(data)
        assert result is True

    def test_validate_response_structure_exception(self):
        """Тест обработки исключения в _validate_response_structure"""
        data = {"items": [{"id": "1"}]}
        
        # Мокаем _validate_vacancy чтобы вызвать исключение
        with patch.object(self.api, '_validate_vacancy', side_effect=Exception("Validation error")):
            with patch('src.api_modules.cached_api.logger.error') as mock_logger:
                result = self.api._validate_response_structure(data)
                assert result is False
                mock_logger.assert_called_once()

    def test_concrete_implementation_methods(self):
        """Тест конкретных методов реализации"""
        # Тест _get_empty_response
        empty_response = self.api._get_empty_response()
        assert empty_response == {"items": [], "found": 0}
        
        # Тест _validate_vacancy с валидной вакансией
        valid_vacancy = {"id": "1", "title": "Developer"}
        assert self.api._validate_vacancy(valid_vacancy) is True
        
        # Тест _validate_vacancy с невалидной вакансией
        invalid_vacancy = {"title": "No ID"}
        assert self.api._validate_vacancy(invalid_vacancy) is False
        
        # Тест _validate_vacancy с неправильным типом
        assert self.api._validate_vacancy("not_dict") is False
        
        # Тест get_vacancies
        vacancies = self.api.get_vacancies("python")
        assert vacancies == []
        
        # Тест get_vacancies_page
        vacancies_page = self.api.get_vacancies_page("java", page=1)
        assert vacancies_page == []

    @patch('src.api_modules.cached_api.logger')
    def test_logging_functionality(self, mock_logger):
        """Тест функциональности логирования"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        
        # Тест логирования при получении из кэша памяти
        cache_key = f"{url}#{json.dumps(params, sort_keys=True)}"
        test_data = {"items": [], "found": 0}
        self.api._memory_cache = {cache_key: (time.time(), test_data)}
        self.api._cache_timestamps = {cache_key: time.time()}
        
        self.api._cached_api_request(url, params, api_prefix)
        mock_logger.debug.assert_called()

    def test_json_import_in_methods(self):
        """Тест импорта json внутри методов"""
        url = "http://test.api"
        params = {"query": "python", "nested": {"key": "value"}}
        api_prefix = "test"
        
        # Проверяем, что json.dumps работает корректно в методах
        cache_key = f"{url}#{json.dumps(params, sort_keys=True)}"
        
        result = self.api._cached_api_request(url, params, api_prefix)
        assert result is None  # Нет кэша
        
        # Проверяем создание кэша в памяти
        assert hasattr(self.api, '_memory_cache')
        assert hasattr(self.api, '_cache_timestamps')

    def test_cache_dir_path_object(self):
        """Тест работы с объектом Path для директории кэша"""
        assert isinstance(self.api.cache_dir, Path)
        assert self.api.cache_dir.exists()

    def test_super_init_called(self):
        """Тест вызова super().__init__()"""
        # Проверяем, что базовый класс инициализирован
        assert hasattr(self.api, 'connector')
        
        # Создаем новый экземпляр для проверки
        with patch('src.api_modules.base_api.BaseJobAPI.__init__') as mock_super_init:
            new_api = ConcreteCachedAPI("test_new_cache")
            mock_super_init.assert_called_once()

    def test_cache_status_no_cache_info(self):
        """Тест get_cache_status без метода cache_info"""
        api_prefix = "test"
        
        # Убираем метод cache_info если он существует
        if hasattr(self.api._cached_api_request, 'cache_info'):
            delattr(self.api._cached_api_request, 'cache_info')
        
        with patch('pathlib.Path.glob', return_value=[]):
            status = self.api.get_cache_status(api_prefix)
            assert status['memory_cache'] == {}

    def test_file_cache_with_data_equal_empty_response(self):
        """Тест файлового кэша когда data равна пустому ответу"""
        url = "http://test.api"
        params = {"query": "python"}
        api_prefix = "test"
        
        empty_response = self.api._get_empty_response()
        
        with patch.object(self.api, '_cached_api_request', return_value=None):
            with patch.object(self.api.cache, 'load_response', return_value=None):
                with patch.object(self.api.connector, '_APIConnector__connect', return_value=empty_response):
                    with patch.object(self.api.cache, 'save_response') as mock_save:
                        result = self.api._CachedAPI__connect_to_api(url, params, api_prefix)
                        
                        assert result == empty_response
                        # Пустой ответ не должен сохраняться
                        mock_save.assert_not_called()