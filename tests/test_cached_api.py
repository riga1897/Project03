#!/usr/bin/env python3
"""
Тесты для модуля cached_api.py
"""

import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import pytest

from src.api_modules.cached_api import CachedAPI
from src.utils.cache import FileCache


class MockCachedAPI(CachedAPI):
    """Мок-реализация CachedAPI для тестирования"""
    
    def _get_empty_response(self):
        """Мок-реализация пустого ответа"""
        return {"items": [], "found": 0}
    
    def _validate_vacancy(self, vacancy):
        """Мок-реализация валидации вакансии"""
        return "id" in vacancy and "name" in vacancy
    
    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs):
        """Мок-реализация получения страницы вакансий"""
        return [{"id": "1", "name": "Test Job"}]
    
    def get_vacancies(self, search_query: str, **kwargs):
        """Мок-реализация получения вакансий"""
        return [{"id": "1", "name": "Test Job"}]


class TestCachedAPI:
    """Тесты для класса CachedAPI"""
    
    @pytest.fixture
    def mock_cache_dir(self, tmp_path):
        """Создание временной директории для кэша"""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return str(cache_dir)
    
    @pytest.fixture
    def cached_api(self, mock_cache_dir):
        """Создание экземпляра CachedAPI для тестов"""
        return MockCachedAPI(mock_cache_dir)
    
    def test_cached_api_initialization(self, mock_cache_dir):
        """Тест инициализации CachedAPI"""
        api = MockCachedAPI(mock_cache_dir)
        
        assert api.cache_dir == Path(mock_cache_dir)
        assert hasattr(api, 'cache')
        assert isinstance(api.cache, FileCache)
    
    @patch('src.api_modules.cached_api.Path.mkdir')
    def test_init_cache_creates_directory(self, mock_mkdir, mock_cache_dir):
        """Тест создания директории кэша при инициализации"""
        api = MockCachedAPI(mock_cache_dir)
        
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_cached_api_inheritance(self, cached_api):
        """Тест наследования от BaseJobAPI"""
        from src.api_modules.base_api import BaseJobAPI
        assert isinstance(cached_api, BaseJobAPI)
    
    @patch('src.api_modules.cached_api.logger')
    def test_cached_api_request_memory_cache_hit(self, mock_logger, cached_api):
        """Тест попадания в кэш памяти"""
        # Подготавливаем данные для кэша
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        # Создаем кэш в памяти
        cached_api._memory_cache = {}
        cached_api._cache_timestamps = {}
        
        # Добавляем данные в кэш
        cache_key = f"{url}#{json.dumps(params, sort_keys=True)}"
        test_data = {"items": [{"id": "1", "name": "Test"}]}
        cached_api._memory_cache[cache_key] = (time.time(), test_data)
        cached_api._cache_timestamps[cache_key] = time.time()
        
        # Тестируем получение из кэша
        result = cached_api._cached_api_request(url, params, api_prefix)
        
        assert result == test_data
        mock_logger.debug.assert_called_with("Данные получены из кэша в памяти для test")
    
    def test_cached_api_request_memory_cache_miss(self, cached_api):
        """Тест промаха кэша памяти"""
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        # Очищаем кэш
        cached_api._memory_cache = {}
        cached_api._cache_timestamps = {}
        
        # Тестируем промах кэша
        result = cached_api._cached_api_request(url, params, api_prefix)
        
        assert result is None
    
    def test_cached_api_request_memory_cache_expired(self, cached_api):
        """Тест истечения срока действия кэша памяти"""
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        # Создаем устаревший кэш
        cached_api._memory_cache = {}
        cached_api._cache_timestamps = {}
        
        cache_key = f"{url}#{json.dumps(params, sort_keys=True)}"
        test_data = {"items": [{"id": "1", "name": "Test"}]}
        # Устанавливаем время создания в прошлом (больше 5 минут)
        cached_api._memory_cache[cache_key] = (time.time() - 400, test_data)
        cached_api._cache_timestamps[cache_key] = time.time() - 400
        
        # Тестируем истечение кэша
        result = cached_api._cached_api_request(url, params, api_prefix)
        
        assert result is None
        # Проверяем, что устаревшие данные удалены
        assert cache_key not in cached_api._memory_cache
        assert cache_key not in cached_api._cache_timestamps
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_memory_cache_fallback(self, mock_logger, cached_api):
        """Тест fallback на файловый кэш при ошибке кэша памяти"""
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        # Мокаем ошибку в кэше памяти
        with patch.object(cached_api, '_cached_api_request', side_effect=Exception("Memory cache error")):
            # Мокаем файловый кэш
            cached_api.cache.load_response.return_value = {"data": {"items": [{"id": "1"}]}}
            
            result = cached_api._CachedAPI__connect_to_api(url, params, api_prefix)
            
            mock_logger.warning.assert_called_with("Ошибка кэша памяти: Memory cache error. Переключаемся на файловый кэш")
            assert result == {"items": [{"id": "1"}]}
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_file_cache_hit(self, mock_logger, cached_api):
        """Тест попадания в файловый кэш"""
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        # Мокаем промах кэша памяти
        with patch.object(cached_api, '_cached_api_request', return_value=None):
            # Мокаем файловый кэш
            cached_api.cache.load_response.return_value = {"data": {"items": [{"id": "1"}]}}
            
            result = cached_api._CachedAPI__connect_to_api(url, params, api_prefix)
            
            mock_logger.debug.assert_called_with("Данные получены из файлового кэша для test")
            assert result == {"items": [{"id": "1"}]}
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_real_request(self, mock_logger, cached_api):
        """Тест реального запроса к API"""
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        # Мокаем промах кэшей
        with patch.object(cached_api, '_cached_api_request', return_value=None):
            cached_api.cache.load_response.return_value = None
            
            # Мокаем connector
            mock_connector = Mock()
            mock_connector._APIConnector__connect.return_value = {"items": [{"id": "1", "name": "Test"}]}
            cached_api.connector = mock_connector
            
            # Мокаем валидацию
            with patch.object(cached_api, '_is_complete_response', return_value=True):
                with patch.object(cached_api, '_validate_response_structure', return_value=True):
                    result = cached_api._CachedAPI__connect_to_api(url, params, api_prefix)
                    
                    mock_logger.debug.assert_called_with("Данные получены из API для test")
                    assert result == {"items": [{"id": "1", "name": "Test"}]}
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_connection_error(self, mock_logger, cached_api):
        """Тест обработки ошибки соединения"""
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        # Мокаем промах кэшей
        with patch.object(cached_api, '_cached_api_request', return_value=None):
            cached_api.cache.load_response.return_value = None
            
            # Мокаем connector с ошибкой соединения
            mock_connector = Mock()
            mock_connector._APIConnector__connect.side_effect = ConnectionError("Connection failed")
            cached_api.connector = mock_connector
            
            result = cached_api._CachedAPI__connect_to_api(url, params, api_prefix)
            
            mock_logger.error.assert_called_with("Ошибка соединения с API test: Connection failed")
            assert result == cached_api._get_empty_response()
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_timeout_error(self, mock_logger, cached_api):
        """Тест обработки ошибки таймаута"""
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        # Мокаем промах кэшей
        with patch.object(cached_api, '_cached_api_request', return_value=None):
            cached_api.cache.load_response.return_value = None
            
            # Мокаем connector с ошибкой таймаута
            mock_connector = Mock()
            mock_connector._APIConnector__connect.side_effect = TimeoutError("Request timeout")
            cached_api.connector = mock_connector
            
            result = cached_api._CachedAPI__connect_to_api(url, params, api_prefix)
            
            mock_logger.error.assert_called_with("Ошибка соединения с API test: Request timeout")
            assert result == cached_api._get_empty_response()
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_general_error(self, mock_logger, cached_api):
        """Тест обработки общей ошибки"""
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        # Мокаем промах кэшей
        with patch.object(cached_api, '_cached_api_request', return_value=None):
            cached_api.cache.load_response.return_value = None
            
            # Мокаем connector с общей ошибкой
            mock_connector = Mock()
            mock_connector._APIConnector__connect.side_effect = Exception("Unknown error")
            cached_api.connector = mock_connector
            
            result = cached_api._CachedAPI__connect_to_api(url, params, api_prefix)
            
            mock_logger.error.assert_called_with("Неизвестная ошибка API test: Unknown error")
            assert result == cached_api._get_empty_response()
    
    @patch('src.api_modules.cached_api.logger')
    def test_clear_cache_success(self, mock_logger, cached_api):
        """Тест успешной очистки кэша"""
        # Мокаем файловый кэш
        cached_api.cache.clear.return_value = None
        
        cached_api.clear_cache("test")
        
        cached_api.cache.clear.assert_called_once_with("test")
        mock_logger.info.assert_called_with("Кэш test очищен (файловый и в памяти)")
    
    @patch('src.api_modules.cached_api.logger')
    def test_clear_cache_error(self, mock_logger, cached_api):
        """Тест ошибки при очистке кэша"""
        # Мокаем ошибку в файловом кэше
        cached_api.cache.clear.side_effect = Exception("Clear error")
        
        cached_api.clear_cache("test")
        
        mock_logger.error.assert_called_with("Ошибка очистки кэша test: Clear error")
    
    @patch('src.api_modules.cached_api.logger')
    def test_get_cache_status_success(self, mock_logger, cached_api):
        """Тест успешного получения статуса кэша"""
        # Создаем тестовые файлы кэша
        cache_file1 = cached_api.cache_dir / "test_1.json"
        cache_file2 = cached_api.cache_dir / "test_2.json"
        
        # Мокаем содержимое файлов
        test_data1 = {"meta": {"params": {"text": "Python"}}}
        test_data2 = {"meta": {"params": {"text": "Java"}}}
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data1))):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                mock_stat.return_value.st_mtime = time.time() - 3600  # 1 час назад
                
                status = cached_api.get_cache_status("test")
                
                assert "cache_dir" in status
                assert status["file_cache_count"] >= 0
                assert "total_size_mb" in status
    
    @patch('src.api_modules.cached_api.logger')
    def test_get_cache_status_error(self, mock_logger, cached_api):
        """Тест ошибки при получении статуса кэша"""
        # Мокаем ошибку при чтении файлов
        with patch('pathlib.Path.glob', side_effect=Exception("File error")):
            status = cached_api.get_cache_status("test")
            
            assert "error" in status
            mock_logger.error.assert_called_with("Ошибка получения статуса кэша: File error")
    
    def test_is_complete_response_valid(self, cached_api):
        """Тест валидного полного ответа"""
        data = {
            "items": [{"id": "1", "name": "Test"}],
            "found": 1
        }
        params = {"page": 0, "per_page": 20}
        
        result = cached_api._is_complete_response(data, params)
        assert result is True
    
    def test_is_complete_response_invalid_structure(self, cached_api):
        """Тест невалидной структуры ответа"""
        data = {"found": 1}  # без items
        params = {"page": 0, "per_page": 20}
        
        result = cached_api._is_complete_response(data, params)
        assert result is False
    
    def test_is_complete_response_incomplete_page(self, cached_api):
        """Тест неполной страницы"""
        data = {
            "items": [{"id": "1"}],  # только 1 элемент
            "found": 50  # найдено 50, но на странице только 1
        }
        params = {"page": 0, "per_page": 20}
        
        result = cached_api._is_complete_response(data, params)
        assert result is False
    
    def test_validate_response_structure_valid(self, cached_api):
        """Тест валидной структуры ответа"""
        data = {
            "items": [
                {"id": "1", "name": "Test1"},
                {"id": "2", "name": "Test2"},
                {"id": "3", "name": "Test3"}
            ]
        }
        
        result = cached_api._validate_response_structure(data)
        assert result is True
    
    def test_validate_response_structure_invalid(self, cached_api):
        """Тест невалидной структуры ответа"""
        data = {
            "items": [
                {"id": "1", "name": "Test1"},
                {"name": "Test2"}  # без id
            ]
        }
        
        result = cached_api._validate_response_structure(data)
        assert result is False
    
    def test_validate_response_structure_not_dict(self, cached_api):
        """Тест ответа не в виде словаря"""
        data = "not a dict"
        
        result = cached_api._validate_response_structure(data)
        assert result is False
    
    def test_validate_response_structure_not_list(self, cached_api):
        """Тест ответа с items не в виде списка"""
        data = {"items": "not a list"}
        
        result = cached_api._validate_response_structure(data)
        assert result is False
    
    def test_memory_cache_size_limit(self, cached_api):
        """Тест ограничения размера кэша в памяти"""
        # Создаем большой кэш
        cached_api._memory_cache = {}
        cached_api._cache_timestamps = {}
        
        # Добавляем больше 1000 элементов
        for i in range(1100):
            key = f"key_{i}"
            cached_api._memory_cache[key] = (time.time(), {"data": i})
            cached_api._cache_timestamps[key] = time.time()
        
        # Вызываем метод, который должен ограничить размер
        url = "https://api.test.com/vacancies"
        params = {"text": "Python"}
        api_prefix = "test"
        
        with patch.object(cached_api, '_cached_api_request', return_value=None):
            cached_api.cache.load_response.return_value = None
            
            mock_connector = Mock()
            mock_connector._APIConnector__connect.return_value = {"items": [{"id": "1"}]}
            cached_api.connector = mock_connector
            
            with patch.object(cached_api, '_is_complete_response', return_value=True):
                with patch.object(cached_api, '_validate_response_structure', return_value=True):
                    cached_api._CachedAPI__connect_to_api(url, params, api_prefix)
                    
                    # Проверяем, что размер кэша ограничен
                    assert len(cached_api._memory_cache) <= 1000
                    assert len(cached_api._cache_timestamps) <= 1000
    
    def test_abstract_methods_are_implemented(self, cached_api):
        """Тест, что абстрактные методы реализованы"""
        assert hasattr(cached_api, '_get_empty_response')
        assert hasattr(cached_api, '_validate_vacancy')
        assert hasattr(cached_api, 'get_vacancies_page')
        assert hasattr(cached_api, 'get_vacancies')
        
        # Проверяем, что методы вызываемы
        assert callable(cached_api._get_empty_response)
        assert callable(cached_api._validate_vacancy)
        assert callable(cached_api.get_vacancies_page)
        assert callable(cached_api.get_vacancies)