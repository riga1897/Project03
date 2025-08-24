
"""
Конфигурация pytest и фикстуры для тестов
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from src.vacancies.models import Vacancy
from src.storage.postgres_saver import PostgresSaver
from src.storage.json_saver import JSONSaver


@pytest.fixture
def sample_vacancy():
    """Фикстура с тестовой вакансией"""
    return Vacancy(
        title="Python Developer",
        url="https://hh.ru/vacancy/12345",
        salary={
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        },
        description="Test description",
        requirements="Python, Django",
        responsibilities="Development",
        experience="От 1 года до 3 лет",
        employment="Полная занятость",
        schedule="Полный день",
        employer={"name": "Test Company"},
        vacancy_id="12345",
        published_at="2024-01-01T00:00:00"
    )


@pytest.fixture
def sample_vacancies(sample_vacancy):
    """Фикстура с несколькими тестовыми вакансиями"""
    vacancy2 = Vacancy(
        title="Java Developer",
        url="https://hh.ru/vacancy/67890",
        salary={
            "from": 80000,
            "to": 120000,
            "currency": "RUR"
        },
        description="Java development",
        requirements="Java, Spring",
        responsibilities="Backend development",
        experience="От 3 до 6 лет",
        employment="Полная занятость",
        schedule="Полный день",
        employer={"name": "Java Corp"},
        vacancy_id="67890",
        published_at="2024-01-02T00:00:00"
    )
    return [sample_vacancy, vacancy2]


@pytest.fixture
def temp_json_file():
    """Фикстура для временного JSON файла"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mock_db_config():
    """Фикстура с мок-конфигурацией БД"""
    return {
        'host': 'localhost',
        'port': '5432',
        'database': 'test_db',
        'username': 'test_user',
        'password': 'test_pass'
    }


@pytest.fixture
def mock_api_response():
    """Фикстура с мок-ответом API"""
    return {
        "items": [
            {
                "id": "12345",
                "name": "Python Developer",
                "alternate_url": "https://hh.ru/vacancy/12345",
                "salary": {
                    "from": 100000,
                    "to": 150000,
                    "currency": "RUR"
                },
                "snippet": {
                    "requirement": "Python, Django",
                    "responsibility": "Development"
                },
                "employer": {"name": "Test Company"},
                "published_at": "2024-01-01T00:00:00+03:00"
            }
        ],
        "found": 1,
        "pages": 1,
        "page": 0,
        "per_page": 20
    }
