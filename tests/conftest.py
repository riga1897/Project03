"""
Конфигурация pytest и фикстуры для тестов

Содержит общие фикстуры и настройки для всех тестов проекта.
Обеспечивает единообразное тестовое окружение и тестовые данные.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.storage.postgres_saver import PostgresSaver
from src.utils.salary import Salary
from src.vacancies.models import Vacancy


@pytest.fixture
def sample_vacancy():
    """Фикстура с тестовой вакансией"""
    return Vacancy(
        title="Python Developer",
        url="https://example.com/vacancy/12345",
        salary={"from": 100000, "to": 150000, "currency": "RUR"},
        description="Разработка веб-приложений на Python",
        requirements="Знание Python, Django, PostgreSQL",
        responsibilities="Разработка и поддержка веб-сервисов",
        experience="От 3 до 6 лет",
        employment="Полная занятость",
        schedule="Полный день",
        employer={"name": "Test Company"},
        vacancy_id="12345",
        published_at="2024-01-15T10:00:00",
        source="hh.ru",
    )


@pytest.fixture
def sample_vacancies(sample_vacancy):
    """Фикстура с коллекцией тестовых вакансий для массовых операций"""
    vacancy2 = Vacancy(
        title="Java Developer",
        url="https://hh.ru/vacancy/67890",
        salary={"from": 80000, "to": 120000, "currency": "RUR"},
        description="Java development",
        requirements="Java, Spring",
        responsibilities="Backend development",
        experience="От 3 до 6 лет",
        employment="Полная занятость",
        schedule="Полный день",
        employer={"name": "Java Corp"},
        vacancy_id="67890",
        published_at="2024-01-02T00:00:00",
        source="hh.ru",
    )
    return [sample_vacancy, vacancy2]


@pytest.fixture
def temp_json_file():
    """Фикстура для создания временного JSON файла для тестирования файловых операций"""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
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
        "host": "localhost",
        "port": "5432",
        "database": "test_db",
        "username": "test_user",
        "password": "test_pass",
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
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "snippet": {"requirement": "Python, Django", "responsibility": "Development"},
                "employer": {"name": "Test Company"},
                "published_at": "2024-01-01T00:00:00+03:00",
            }
        ],
        "found": 1,
        "pages": 1,
        "page": 0,
        "per_page": 20,
    }


@pytest.fixture
def mock_superjob_response():
    """Фикстура с имитацией ответа SuperJob API"""
    return {
        "objects": [
            {
                "id": 54321,
                "profession": "Java Developer",
                "link": "https://superjob.ru/vakansii/java-developer-54321.html",
                "payment_from": 80000,
                "payment_to": 120000,
                "currency": "rub",
                "candidat": "Java, Spring",
                "vacancyRichText": "Backend development",
                "firm_name": "Java Corp",
                "date_published": 1704067200,
            }
        ],
        "total": 1,
    }


@pytest.fixture
def mock_storage():
    """Мок для хранилища данных"""
    storage = Mock()
    storage.get_vacancies.return_value = []
    storage.add_vacancy.return_value = True
    storage.delete_vacancy_by_id.return_value = True
    storage.delete_vacancies_by_keyword.return_value = 0
    storage.get_vacancies_count.return_value = 0
    storage.clear_vacancies.return_value = True
    return storage


@pytest.fixture
def mock_db_manager():
    """Мок для DBManager"""
    db_manager = Mock()
    db_manager.check_connection.return_value = True
    db_manager.create_tables.return_value = None
    db_manager.populate_companies_table.return_value = None
    db_manager.get_companies_and_vacancies_count.return_value = []
    db_manager.get_all_vacancies.return_value = []
    db_manager.get_avg_salary.return_value = 100000
    db_manager.get_vacancies_with_higher_salary.return_value = []
    db_manager.get_vacancies_with_keyword.return_value = []
    return db_manager


@pytest.fixture(autouse=True)
def mock_all_external_resources():
    """Глобально мокает все внешние ресурсы для всех тестов"""
    with patch("requests.get") as mock_requests, patch("requests.post") as mock_post, patch(
        "psycopg2.connect"
    ) as mock_db, patch("builtins.input") as mock_input, patch(
        "src.utils.env_loader.EnvLoader.load_env_file"
    ) as mock_env, patch(
        "os.path.exists"
    ) as mock_exists, patch(
        "os.makedirs"
    ) as mock_makedirs, patch(
        "psycopg2.extras.execute_values"
    ) as mock_execute_values:

        # Настраиваем моки для HTTP запросов
        mock_response = Mock()
        mock_response.json.return_value = {"items": [], "found": 0}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        mock_post.return_value = mock_response

        # Настраиваем мок для базы данных
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.rowcount = 0
        # Настраиваем кодировку для psycopg2
        mock_connection.encoding = "UTF8"
        mock_cursor.connection = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value = mock_connection

        # Настраиваем мок для execute_values
        mock_execute_values.return_value = None

        # Настраиваем мок для ввода пользователя
        mock_input.return_value = "test_input"

        # Настраиваем остальные моки
        mock_env.return_value = {}
        mock_exists.return_value = True
        mock_makedirs.return_value = None

        yield


@pytest.fixture
def mock_unified_api():
    """Мок для UnifiedAPI"""
    api = Mock()
    api.search_vacancies.return_value = []
    api.get_available_sources.return_value = ["hh.ru"]
    api.clear_cache.return_value = None
    return api


@pytest.fixture
def sample_companies_data():
    """Тестовые данные компаний"""
    return [{"id": 1, "name": "СБЕР", "vacancies_count": 10}, {"id": 2, "name": "Яндекс", "vacancies_count": 5}]