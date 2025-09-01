import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from unittest.mock import MagicMock
from typing import Any, Dict, List, Optional

import pytest


@pytest.fixture
def mock_db_config():
    """Мок конфигурации базы данных"""
    return {
        "host": "localhost",
        "port": "5432",
        "database": "test_db",
        "username": "test_user",
        "password": "test_password",
    }


@pytest.fixture
def mock_vacancy_data():
    """Тестовые данные вакансии"""
    return {
        "id": "123456",
        "name": "Python Developer",
        "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
        "employer": {"name": "Test Company"},
        "area": {"name": "Москва"},
        "experience": {"name": "От 1 года до 3 лет"},
        "employment": {"name": "Полная занятость"},
        "schedule": {"name": "Полный день"},
        "description": "Test description with Python",
        "url": "https://test.com/vacancy/123456",
        "alternate_url": "https://test.com/vacancy/123456",
        "published_at": "2025-01-01T00:00:00+0300",
    }


# Консолидированные базовые мок-классы
class BaseMockAPI:
    """Базовый мок для API"""
    
    def __init__(self):
        self.cache_cleared = False
    
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict[str, Any]]:
        """Мок получения вакансий"""
        return [{"id": 1, "title": f"{search_query} Developer", "source": self.__class__.__name__.lower()}]
    
    def clear_cache(self, source: str = None):
        """Мок очистки кэша"""
        self.cache_cleared = True


class MockConnection:
    """Консолидированный мок подключения к БД"""
    
    def __init__(self):
        self.cursor_instance = MockCursor()
        self.closed = False
    
    def cursor(self):
        return self.cursor_instance
    
    def commit(self):
        pass
    
    def close(self):
        self.closed = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MockCursor:
    """Консолидированный мок курсора БД"""
    
    def __init__(self):
        self.results = []
        self.executed_queries = []
    
    def execute(self, query: str, params=None):
        self.executed_queries.append((query, params))
    
    def fetchall(self):
        return self.results
    
    def fetchone(self):
        return self.results[0] if self.results else None
    
    def set_results(self, results: List):
        self.results = results
    
    def close(self):
        pass


@pytest.fixture
def mock_connection():
    """Фикстура мок подключения к БД"""
    return MockConnection()


@pytest.fixture
def base_mock_api():
    """Фикстура базового мок API"""
    return BaseMockAPI()
