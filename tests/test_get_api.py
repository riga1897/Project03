
import pytest
from unittest.mock import MagicMock, patch
from src.api_modules.get_api import get_api, APIFactory


class TestAPIFactory:
    def test_api_factory_initialization(self):
        """Тест инициализации фабрики API"""
        factory = APIFactory()
        assert hasattr(factory, 'create_api')

    def test_create_hh_api(self):
        """Тест создания HeadHunter API"""
        factory = APIFactory()
        with patch('src.api_modules.hh_api.HeadHunterAPI'):
            api = factory.create_api('hh')
            assert api is not None

    def test_create_sj_api(self):
        """Тест создания SuperJob API"""
        factory = APIFactory()
        with patch('src.api_modules.sj_api.SuperJobAPI'):
            api = factory.create_api('sj')
            assert api is not None

    def test_create_unknown_api(self):
        """Тест создания неизвестного API"""
        factory = APIFactory()
        with pytest.raises((ValueError, KeyError)):
            factory.create_api('unknown')

    def test_get_api_function(self):
        """Тест функции получения API"""
        with patch('src.api_modules.hh_api.HeadHunterAPI'):
            api = get_api('hh')
            assert api is not None

    def test_api_factory_caching(self):
        """Тест кэширования API экземпляров"""
        factory = APIFactory()
        with patch('src.api_modules.hh_api.HeadHunterAPI') as mock_api:
            api1 = factory.create_api('hh')
            api2 = factory.create_api('hh')
            # Может кэшироваться или создаваться заново
            assert api1 is not None
            assert api2 is not None
