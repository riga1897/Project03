
"""
Тесты для кэшированного API
"""

import tempfile
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from src.api_modules.cached_api import CachedAPI


class ConcreteCachedAPI(CachedAPI):
    """Конкретная реализация CachedAPI для тестирования"""
    
    def __init__(self, cache_dir):
        super().__init__(cache_dir)
        from src.api_modules.get_api import APIConnector
        self.connector = APIConnector()
    
    def get_vacancies(self, search_query=None, **kwargs):
        """Реализация абстрактного метода"""
        return [{"id": "1", "title": "Test Vacancy"}]
    
    def get_vacancies_page(self, search_query=None, page=0, **kwargs):
        """Реализация абстрактного метода"""
        return [{"id": f"page_{page}_1", "title": f"Test Vacancy Page {page}"}]
    
    def _get_empty_response(self):
        """Реализация абстрактного метода"""
        return {"items": []}
    
    def _validate_vacancy(self, vacancy):
        """Реализация абстрактного метода"""
        return isinstance(vacancy, dict) and "id" in vacancy


class TestCachedAPI:
    """Тесты для CachedAPI"""
    
    def test_initialization(self):
        """Тест инициализации"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            assert str(api.cache_dir) == temp_dir
            assert api.cache_dir.exists()
    
    @patch('src.api_modules.get_api.APIConnector')
    def test_connect_to_api_with_cache(self, mock_connector_class):
        """Тест подключения к API с кэшем"""
        # Настройка мока
        mock_connector = MagicMock()
        mock_connector_class.return_value = mock_connector
        
        test_data = {"items": [{"id": "1", "title": "Test"}]}
        mock_connector._APIConnector__connect.return_value = test_data
        
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокаем FileCache
            with patch.object(api.cache, 'load_response', return_value=None), \
                 patch.object(api.cache, 'save_response'):
                
                result = api._CachedAPI__connect_to_api("http://test.com", {}, "test")
                
                assert result == test_data
                mock_connector._APIConnector__connect.assert_called_once()
    
    @patch('src.api_modules.get_api.APIConnector')
    def test_connect_to_api_from_file_cache(self, mock_connector_class):
        """Тест получения данных из файлового кэша"""
        # Настройка мока
        mock_connector = MagicMock()
        mock_connector_class.return_value = mock_connector
        
        cached_data = {"items": [{"id": "2", "title": "Cached Test"}]}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокаем FileCache для возврата кэшированных данных
            with patch.object(api.cache, 'load_response', return_value={"data": cached_data}):
                
                result = api._CachedAPI__connect_to_api("http://test.com", {}, "test")
                
                assert result == cached_data
                # API не должен вызываться, так как данные берутся из кэша
                mock_connector._APIConnector__connect.assert_not_called()
    
    def test_clear_cache(self):
        """Тест очистки кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокаем только методы FileCache
            with patch.object(api.cache, 'clear') as mock_clear:
                
                api.clear_cache("test")
                
                # Проверяем, что метод очистки файлового кэша был вызван
                mock_clear.assert_called_once_with("test")
    
    def test_get_cache_status(self):
        """Тест получения статуса кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Создаем тестовый файл кэша
            test_cache_file = Path(temp_dir) / "test_cache.json"
            test_cache_file.write_text('{"test": "data"}')
            
            status = api.get_cache_status("test")
            
            assert isinstance(status, dict)
            assert "cache_dir" in status
            assert "cache_dir_exists" in status
            assert status["cache_dir_exists"] is True
    
    def test_is_complete_response_valid(self):
        """Тест проверки полноты валидного ответа"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            valid_data = {
                "items": [{"id": "1", "title": "Test"}],
                "found": 1
            }
            params = {"page": 0, "per_page": 20}
            
            assert api._is_complete_response(valid_data, params) is True
    
    def test_is_complete_response_invalid(self):
        """Тест проверки полноты невалидного ответа"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Ответ без обязательного поля items
            invalid_data = {"found": 1}
            params = {"page": 0, "per_page": 20}
            
            assert api._is_complete_response(invalid_data, params) is False
    
    def test_validate_response_structure_valid(self):
        """Тест валидации корректной структуры ответа"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            valid_data = {
                "items": [{"id": "1", "title": "Test"}]
            }
            
            assert api._validate_response_structure(valid_data) is True
    
    def test_validate_response_structure_invalid(self):
        """Тест валидации некорректной структуры ответа"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Некорректная структура - items не список
            invalid_data = {
                "items": "not a list"
            }
            
            assert api._validate_response_structure(invalid_data) is False
    
    @patch('src.api_modules.get_api.APIConnector')
    def test_memory_cache_integration(self, mock_connector_class):
        """Тест интеграции с кэшем в памяти"""
        mock_connector = MagicMock()
        mock_connector_class.return_value = mock_connector
        
        test_data = {"items": [{"id": "1", "title": "Memory Test"}]}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокаем кэш в памяти для возврата данных
            with patch.object(api, '_cached_api_request', return_value=test_data):
                
                result = api._CachedAPI__connect_to_api("http://test.com", {}, "test")
                
                assert result == test_data
    
    def test_inherited_abstract_methods(self):
        """Тест что конкретная реализация имеет все необходимые методы"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Проверяем наличие методов от BaseJobAPI
            assert hasattr(api, 'get_vacancies')
            assert hasattr(api, 'get_vacancies_page')
            assert callable(getattr(api, 'get_vacancies'))
            assert callable(getattr(api, 'get_vacancies_page'))
            
            # Тестируем вызов методов
            vacancies = api.get_vacancies("python")
            assert isinstance(vacancies, list)
            assert len(vacancies) > 0
            
            page_vacancies = api.get_vacancies_page("python", 0)
            assert isinstance(page_vacancies, list)
            assert len(page_vacancies) > 0
    
    def test_error_handling_in_cache_operations(self):
        """Тест обработки ошибок в операциях кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Тестируем обработку ошибок при очистке кэша
            with patch.object(api.cache, 'clear', side_effect=Exception("Cache error")):
                # Не должно вызывать исключение
                api.clear_cache("test")
            
            # Тестируем обработку ошибок при получении статуса
            # Мокаем glob через Path.glob
            with patch('pathlib.Path.glob', side_effect=Exception("Glob error")):
                status = api.get_cache_status("test")
                assert "error" in status
