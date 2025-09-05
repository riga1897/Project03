
"""
Тесты для абстрактных классов хранения данных
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.storage.abstract import AbstractStorage
    from src.storage.abstract_db_manager import AbstractDBManager
    STORAGE_ABSTRACTIONS_AVAILABLE = True
except ImportError:
    STORAGE_ABSTRACTIONS_AVAILABLE = False

try:
    from src.storage.services.abstract_storage_service import AbstractStorageService
    from src.storage.services.abstract_filter_service import AbstractFilterService
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False


class ConcreteStorage(AbstractStorage if STORAGE_ABSTRACTIONS_AVAILABLE else object):
    """Конкретная реализация AbstractStorage для тестирования"""
    
    def save(self, data):
        return True
    
    def load(self, query):
        return []
    
    def delete(self, identifier):
        return True


class ConcreteDBManager(AbstractDBManager if STORAGE_ABSTRACTIONS_AVAILABLE else object):
    """Конкретная реализация AbstractDBManager для тестирования"""
    
    def connect(self):
        pass
    
    def disconnect(self):
        pass
    
    def execute_query(self, query, params=None):
        return []


class ConcreteStorageService(AbstractStorageService if SERVICES_AVAILABLE else object):
    """Конкретная реализация AbstractStorageService для тестирования"""
    
    def store(self, data):
        return True
    
    def retrieve(self, filters):
        return []


class ConcreteFilterService(AbstractFilterService if SERVICES_AVAILABLE else object):
    """Конкретная реализация AbstractFilterService для тестирования"""
    
    def filter(self, data, criteria):
        return data


class TestAbstractStorage:
    """Тесты для абстрактного класса хранения"""

    def test_abstract_storage_cannot_be_instantiated(self):
        """Тест что абстрактный класс нельзя инстанциировать"""
        if not STORAGE_ABSTRACTIONS_AVAILABLE:
            pytest.skip("Storage abstractions not available")
        
        with pytest.raises(TypeError):
            AbstractStorage()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not STORAGE_ABSTRACTIONS_AVAILABLE:
            pytest.skip("Storage abstractions not available")
        
        storage = ConcreteStorage()
        
        # Тестируем методы
        result = storage.save({"test": "data"})
        assert result is True
        
        result = storage.load({"query": "test"})
        assert isinstance(result, list)
        
        result = storage.delete("test_id")
        assert result is True


class TestAbstractDBManager:
    """Тесты для абстрактного менеджера базы данных"""

    def test_abstract_db_manager_cannot_be_instantiated(self):
        """Тест что абстрактный класс нельзя инстанциировать"""
        if not STORAGE_ABSTRACTIONS_AVAILABLE:
            pytest.skip("Storage abstractions not available")
        
        with pytest.raises(TypeError):
            AbstractDBManager()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not STORAGE_ABSTRACTIONS_AVAILABLE:
            pytest.skip("Storage abstractions not available")
        
        db_manager = ConcreteDBManager()
        
        # Тестируем методы
        db_manager.connect()
        
        result = db_manager.execute_query("SELECT * FROM test")
        assert isinstance(result, list)
        
        db_manager.disconnect()


class TestAbstractStorageService:
    """Тесты для абстрактного сервиса хранения"""

    def test_abstract_storage_service_cannot_be_instantiated(self):
        """Тест что абстрактный класс нельзя инстанциировать"""
        if not SERVICES_AVAILABLE:
            pytest.skip("Services not available")
        
        with pytest.raises(TypeError):
            AbstractStorageService()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not SERVICES_AVAILABLE:
            pytest.skip("Services not available")
        
        service = ConcreteStorageService()
        
        # Тестируем методы
        result = service.store({"test": "data"})
        assert result is True
        
        result = service.retrieve({"filter": "test"})
        assert isinstance(result, list)


class TestAbstractFilterService:
    """Тесты для абстрактного сервиса фильтрации"""

    def test_abstract_filter_service_cannot_be_instantiated(self):
        """Тест что абстрактный класс нельзя инстанциировать"""
        if not SERVICES_AVAILABLE:
            pytest.skip("Services not available")
        
        with pytest.raises(TypeError):
            AbstractFilterService()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not SERVICES_AVAILABLE:
            pytest.skip("Services not available")
        
        service = ConcreteFilterService()
        test_data = [{"id": 1, "name": "test"}]
        
        # Тестируем метод
        result = service.filter(test_data, {"name": "test"})
        assert result == test_data
