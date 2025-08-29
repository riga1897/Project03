
"""
Тесты для кэшированного API
"""

import tempfile
import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.api_modules.cached_api import CachedAPI


class ConcreteCachedAPI(CachedAPI):
    """Конкретная реализация CachedAPI для тестирования"""
    
    def __init__(self, cache_dir):
        super().__init__(cache_dir)
    
    def get_vacancies(self, search_query=None, **kwargs):
        """Реализация абстрактного метода"""
        return [{"id": "1", "title": "Test Vacancy"}]
    
    def get_vacancies_page(self, search_query=None, page=0, **kwargs):
        """Реализация абстрактного метода"""
        return [{"id": f"page_{page}_1", "title": f"Test Vacancy Page {page}"}]


class TestCachedAPI:
    """Тесты для CachedAPI"""
    
    def test_initialization(self):
        """Тест инициализации"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            assert api.cache_dir == temp_dir
    
    @patch('src.api_modules.get_api.APIConnector')
    def test_connect_to_api_with_cache(self, mock_connector_class):
        """Тест подключения к API с кэшем"""
        # Настройка мока
        mock_connector = MagicMock()
        mock_connector_class.return_value = mock_connector
        
        test_data = {"items": [{"id": "1", "title": "Test"}]}
        mock_connector.get_json.return_value = test_data
        
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокаем методы кэша
            with patch.object(api, '_get_cache_path', return_value='test_cache.json'), \
                 patch('os.path.exists', return_value=False), \
                 patch('builtins.open', mock_open()):
                
                result = api._CachedAPI__connect_to_api("http://test.com", {}, "test")
                
                assert result == test_data
                mock_connector.get_json.assert_called_once()
    
    @patch('src.api_modules.get_api.APIConnector')
    def test_connect_to_api_without_cache(self, mock_connector_class):
        """Тест подключения к API без кэша"""
        # Настройка мока
        mock_connector = MagicMock()
        mock_connector_class.return_value = mock_connector
        
        test_data = {"items": [{"id": "2", "title": "Test2"}]}
        mock_connector.get_json.return_value = test_data
        
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокаем методы для случая без кэша
            with patch.object(api, '_get_cache_path', return_value='test_cache.json'), \
                 patch('os.path.exists', return_value=False), \
                 patch('builtins.open', mock_open()):
                
                result = api._CachedAPI__connect_to_api("http://test.com", {}, "test")
                
                assert result == test_data
    
    def test_clear_cache(self):
        """Тест очистки кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокаем существование файлов кэша
            with patch('os.listdir', return_value=['test_cache.json', 'other_file.txt']), \
                 patch('os.path.isfile', return_value=True), \
                 patch('os.remove') as mock_remove:
                
                api.clear_cache("test")
                
                # Проверяем, что файл кэша был удален
                mock_remove.assert_called()
    
    def test_get_cache_path(self):
        """Тест генерации пути к кэшу"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            url = "http://api.test.com/vacancies"
            params = {"text": "python", "page": "0"}
            prefix = "test"
            
            cache_path = api._get_cache_path(url, params, prefix)
            
            # Проверяем, что путь содержит правильные компоненты
            assert temp_dir in cache_path
            assert prefix in cache_path
            assert cache_path.endswith('.json')
    
    def test_is_cache_valid(self):
        """Тест проверки валидности кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокаем файл с недавней датой модификации
            import time
            recent_time = time.time() - 1800  # 30 минут назад
            
            with patch('os.path.getmtime', return_value=recent_time):
                assert api._is_cache_valid('test_file.json') is True
            
            # Мокаем файл со старой датой модификации
            old_time = time.time() - 7200  # 2 часа назад
            
            with patch('os.path.getmtime', return_value=old_time):
                assert api._is_cache_valid('test_file.json') is False
    
    def test_save_to_cache(self):
        """Тест сохранения в кэш"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            test_data = {"test": "data"}
            cache_path = "test_cache.json"
            
            with patch('os.makedirs'), \
                 patch('builtins.open', mock_open()) as mock_file:
                
                api._save_to_cache(test_data, cache_path)
                
                # Проверяем, что файл был открыт для записи
                mock_file.assert_called_once()
    
    def test_load_from_cache(self):
        """Тест загрузки из кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            test_data = '{"test": "cached_data"}'
            
            with patch('builtins.open', mock_open(read_data=test_data)):
                result = api._load_from_cache('test_cache.json')
                
                assert result == {"test": "cached_data"}
    
    def test_load_from_cache_invalid_json(self):
        """Тест загрузки невалидного JSON из кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            invalid_json = '{"test": invalid_json}'
            
            with patch('builtins.open', mock_open(read_data=invalid_json)):
                result = api._load_from_cache('test_cache.json')
                
                # При ошибке парсинга должен возвращаться None
                assert result is None
    
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
