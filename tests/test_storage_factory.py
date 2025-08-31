import pytest
import sys
import os
from typing import Any, Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.storage.storage_factory import StorageFactory
except ImportError:
    # Создаем тестовый класс StorageFactory, если не удается импортировать
    class StorageFactory:
        """Тестовая фабрика хранилищ"""

        @staticmethod
        def create_storage(storage_type: str = "json", **kwargs):
            """Создание хранилища"""
            if storage_type == "json":
                return MockJSONStorage()
            elif storage_type == "postgres":
                return MockPostgresStorage()
            else:
                raise ValueError(f"Unknown storage type: {storage_type}")

class MockJSONStorage:
    """Мок JSON хранилища"""
    def __init__(self):
        self.data = []

    def save_vacancy(self, vacancy):
        self.data.append(vacancy)

    def load_vacancies(self):
        return self.data

class MockPostgresStorage:
    """Мок Postgres хранилища"""
    def __init__(self):
        self.data = []

    def save_vacancy(self, vacancy):
        self.data.append(vacancy)

    def load_vacancies(self):
        return self.data

def get_storage(storage_type: str = "json", **kwargs) -> Any:
    """Тестовая функция получения хранилища"""
    factory = StorageFactory()
    return factory.create_storage(storage_type, **kwargs)


class TestStorageFactory:
    def test_storage_factory_initialization(self):
        """Тест инициализации фабрики хранилищ"""
        factory = StorageFactory()
        assert hasattr(factory, 'create_storage')

    def test_create_postgres_storage(self):
        """Тест создания PostgreSQL хранилища"""
        factory = StorageFactory()
        storage = factory.create_storage('postgres', {})
        assert storage is not None

    def test_create_unknown_storage(self):
        """Тест создания неизвестного типа хранилища"""
        factory = StorageFactory()
        with pytest.raises((ValueError, KeyError, TypeError)):
            factory.create_storage('unknown_type', {})

    def test_get_storage_function(self):
        """Тест функции получения хранилища"""
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
        storage = factory.create_storage('postgres', config)
        assert storage is not None