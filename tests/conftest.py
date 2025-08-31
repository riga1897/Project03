import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from unittest.mock import MagicMock

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
