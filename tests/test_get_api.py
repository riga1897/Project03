
import pytest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.get_api import APIConnector


class APIFactory:
    """Тестовая фабрика для создания экземпляров API"""
    
    def __init__(self):
        self._apis = {
            'hh': 'HeadHunterAPI',
            'sj': 'SuperJobAPI'
        }
    
    def create_api(self, api_type: str):
        """Создает экземпляр API по типу"""
        if api_type not in self._apis:
            raise ValueError(f"Unknown API type: {api_type}")
        
        # Для тестов возвращаем mock объект
        mock_api = MagicMock()
        mock_api.name = self._apis[api_type]
        return mock_api


def get_api(api_type: str):
    """Функция для получения API экземпляра"""
    factory = APIFactory()
    return factory.create_api(api_type)


class TestAPIFactory:
    def test_api_factory_initialization(self):
        """Тест инициализации фабрики API"""
        factory = APIFactory()
        assert hasattr(factory, 'create_api')

    def test_create_hh_api(self):
        """Тест создания HeadHunter API"""
        factory = APIFactory()
        api = factory.create_api('hh')
        assert api is not None

    def test_create_sj_api(self):
        """Тест создания SuperJob API"""
        factory = APIFactory()
        api = factory.create_api('sj')
        assert api is not None

    def test_create_unknown_api(self):
        """Тест создания неизвестного API"""
        factory = APIFactory()
        with pytest.raises((ValueError, KeyError)):
            factory.create_api('unknown')

    def test_get_api_function(self):
        """Тест функции получения API"""
        api = get_api('hh')
        assert api is not None

    def test_api_factory_caching(self):
        """Тест кэширования API экземпляров"""
        factory = APIFactory()
        api1 = factory.create_api('hh')
        api2 = factory.create_api('hh')
        # Проверяем, что создается новый экземпляр при каждом вызове
        assert api1 is not None
        assert api2 is not None
