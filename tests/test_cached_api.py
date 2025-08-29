
"""
Тесты для кэшированного API
"""

import pytest
import tempfile
from unittest.mock import Mock, patch
from src.api_modules.cached_api import CachedAPI


class ConcreteCachedAPI(CachedAPI):
    """Конкретная реализация для тестирования"""
    
    def _get_empty_response(self):
        return {"items": []}
    
    def _validate_vacancy(self, vacancy):
        return True


class TestCachedAPI:
    """Тесты для CachedAPI"""

    def test_initialization(self):
        """Тест инициализации"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            assert api is not None
            assert hasattr(api, 'cache')

    @patch('src.api_modules.cached_api.APIConnector')
    def test_connect_to_api_with_cache(self, mock_connector):
        """Тест подключения к API с кэшем"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокируем кэш
            api.cache.load_response = Mock(return_value={"data": {"items": []}})
            
            result = api._CachedAPI__connect_to_api("http://test.com", {}, "test")
            
            # Должен вернуть данные из кэша
            assert result == {"items": []}

    @patch('src.api_modules.cached_api.APIConnector')
    def test_connect_to_api_without_cache(self, mock_connector):
        """Тест подключения к API без кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокируем отсутствие кэша и API ответ
            api.cache.load_response = Mock(return_value=None)
            api.cache.save_response = Mock()
            
            mock_instance = Mock()
            mock_instance.connect.return_value = {"items": [{"id": "1"}]}
            mock_connector.return_value = mock_instance
            
            result = api._CachedAPI__connect_to_api("http://test.com", {}, "test")
            
            # Должен вернуть данные из API и сохранить в кэш
            assert result == {"items": [{"id": "1"}]}
            api.cache.save_response.assert_called_once()

    def test_clear_cache(self):
        """Тест очистки кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            
            # Мокируем метод очистки кэша
            api.cache.clear_cache = Mock()
            
            api.clear_cache("test")
            
            api.cache.clear_cache.assert_called_once_with("test")
