"""
Конфигурация pytest и фикстуры для тестов

Содержит общие фикстуры и настройки для всех тестов проекта.
Обеспечивает единообразное тестовое окружение и тестовые данные.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from pathlib import Path
from src.vacancies.models import Vacancy
from src.storage.postgres_saver import PostgresSaver
from src.utils.salary import Salary


@pytest.fixture
def sample_vacancy():
    """Фикстура с образцом тестовой вакансии для использования в тестах"""
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
    """Фикстура с коллекцией тестовых вакансий для массовых операций"""
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
    """Фикстура для создания временного JSON файла для тестирования файловых операций"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_directory():
    """Фикстура для создания временной директории"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_db_config():
    """Фикстура с имитацией конфигурации базы данных для тестирования"""
    return {
        'host': 'localhost',
        'port': '5432',
        'database': 'test_db',
        'username': 'test_user',
        'password': 'test_pass'
    }


@pytest.fixture
def mock_api_response():
    """Фикстура с имитацией ответа API для тестирования без реальных запросов"""
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

@pytest.fixture(autouse=True)
def mock_all_external_resources():
    """Глобально мокает все внешние ресурсы для всех тестов"""
    with patch('requests.get') as mock_requests, \
         patch('requests.post') as mock_post, \
         patch('psycopg2.connect') as mock_db, \
         patch('src.utils.env_loader.EnvLoader.load_env_file') as mock_env, \
         patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs:

        # Настраиваем моки
        mock_response = Mock()
        mock_response.json.return_value = {"items": [], "found": 0}
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        mock_post.return_value = mock_response

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn

        mock_env.return_value = {}
        mock_exists.return_value = True
        mock_makedirs.return_value = None

        yield