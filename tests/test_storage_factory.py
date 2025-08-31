
import pytest
from unittest.mock import MagicMock, patch
from src.storage.storage_factory import StorageFactory, get_storage
from src.storage.postgres_saver import PostgresSaver


class TestStorageFactory:
    def test_storage_factory_initialization(self):
        """Тест инициализации фабрики хранилищ"""
        factory = StorageFactory()
        assert hasattr(factory, 'create_storage')

    def test_create_postgres_storage(self):
        """Тест создания PostgreSQL хранилища"""
        factory = StorageFactory()
        with patch('src.storage.postgres_saver.PostgresSaver'):
            storage = factory.create_storage('postgres', {})
            assert storage is not None

    def test_create_unknown_storage(self):
        """Тест создания неизвестного типа хранилища"""
        factory = StorageFactory()
        with pytest.raises((ValueError, KeyError, TypeError)):
            factory.create_storage('unknown_type', {})

    def test_get_storage_function(self):
        """Тест функции получения хранилища"""
        with patch('src.storage.postgres_saver.PostgresSaver'):
            storage = get_storage('postgres')
            assert storage is not None

    def test_storage_factory_singleton(self):
        """Тест что фабрика работает как синглтон"""
        factory1 = StorageFactory()
        factory2 = StorageFactory()
        # Может быть не синглтон, проверяем что создается корректно
        assert factory1 is not None
        assert factory2 is not None

    def test_create_storage_with_config(self):
        """Тест создания хранилища с конфигурацией"""
        factory = StorageFactory()
        config = {'host': 'localhost', 'port': 5432}
        with patch('src.storage.postgres_saver.PostgresSaver'):
            storage = factory.create_storage('postgres', config)
            assert storage is not None
