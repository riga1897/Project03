
"""
Консолидированные фикстуры для оптимизированного тестирования
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture(scope="session")
def unified_db_connection():
    """Единое подключение к БД для всех тестов в сессии"""
    mock_connection = Mock()
    mock_connection.__enter__ = Mock(return_value=mock_connection)
    mock_connection.__exit__ = Mock(return_value=None)
    mock_connection.commit = Mock()
    mock_connection.rollback = Mock()
    mock_connection.close = Mock()
    mock_connection.set_client_encoding = Mock()
    mock_connection.autocommit = True
    mock_connection.encoding = "UTF8"

    mock_cursor = Mock()
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=None)
    mock_cursor.execute = Mock()
    mock_cursor.fetchone = Mock(return_value=(1,))
    mock_cursor.fetchall = Mock(return_value=[])
    mock_cursor.rowcount = 1
    mock_cursor.connection = mock_connection
    mock_connection.cursor = Mock(return_value=mock_cursor)

    return mock_connection


@pytest.fixture(scope="session")
def consolidated_external_mocks():
    """Консолидированные моки для всех внешних ресурсов"""
    # HTTP моки
    mock_response = Mock()
    mock_response.json.return_value = {"items": [], "found": 0, "pages": 0}
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.text = '{"items": []}'

    # Файловые моки
    mock_file_content = '{"test": "data"}'
    
    return {
        "http_response": mock_response,
        "file_content": mock_file_content,
        "env_vars": {
            "PGHOST": "localhost",
            "PGPORT": "5432",
            "PGDATABASE": "test_db",
            "PGUSER": "test_user",
            "PGPASSWORD": "test_pass",
            "HH_API_URL": "https://api.hh.ru",
            "SJ_API_URL": "https://api.superjob.ru",
            "SJ_SECRET_KEY": "test_secret_key"
        }
    }


@pytest.fixture(autouse=True)
def global_external_resource_isolation(unified_db_connection, consolidated_external_mocks):
    """Глобальная изоляция от всех внешних ресурсов"""
    with patch("requests.get", return_value=consolidated_external_mocks["http_response"]) as mock_get, \
         patch("requests.post", return_value=consolidated_external_mocks["http_response"]) as mock_post, \
         patch("psycopg2.connect", return_value=unified_db_connection) as mock_db_connect, \
         patch("psycopg2.extras.execute_values") as mock_execute_values, \
         patch("builtins.input", return_value="0") as mock_input, \
         patch("builtins.print") as mock_print, \
         patch("os.path.exists", return_value=True) as mock_exists, \
         patch("os.makedirs") as mock_makedirs, \
         patch("src.utils.env_loader.EnvLoader.load_env_file") as mock_env_load, \
         patch.dict("os.environ", consolidated_external_mocks["env_vars"], clear=False):

        # Возвращаем все моки для использования в тестах
        yield {
            "http_get": mock_get,
            "http_post": mock_post,
            "db_connect": mock_db_connect,
            "execute_values": mock_execute_values,
            "input": mock_input,
            "print": mock_print,
            "path_exists": mock_exists,
            "makedirs": mock_makedirs,
            "env_load": mock_env_load,
            "db_connection": unified_db_connection,
            "external_mocks": consolidated_external_mocks
        }


@pytest.fixture
def sample_vacancy():
    """Стандартная тестовая вакансия"""
    from src.vacancies.models import Vacancy
    
    return Vacancy(
        title="Test Vacancy",
        url="https://test.com/vacancy/1",
        salary={"from": 100000, "to": 150000, "currency": "RUR"},
        description="Test description",
        requirements="Test requirements",
        responsibilities="Test responsibilities",
        experience="Test experience",
        employment="Test employment",
        schedule="Test schedule",
        employer={"name": "Test Company"},
        vacancy_id="test_1",
        published_at="2024-01-15T10:00:00",
        source="test_api"
    )


@pytest.fixture
def mock_db_manager():
    """Мокированный DBManager с едиными методами"""
    mock_manager = Mock()
    mock_manager.check_connection.return_value = True
    mock_manager.get_companies_and_vacancies_count.return_value = [("Test Company", 5)]
    mock_manager.get_all_vacancies.return_value = []
    mock_manager.get_avg_salary.return_value = 100000.0
    mock_manager.get_vacancies_with_higher_salary.return_value = []
    mock_manager.get_vacancies_with_keyword.return_value = []
    mock_manager.get_database_stats.return_value = {}
    mock_manager.get_target_companies_analysis.return_value = []
    return mock_manager


@pytest.fixture
def mock_postgres_saver():
    """Мокированный PostgresSaver с едиными методами"""
    mock_saver = Mock()
    mock_saver.add_vacancy.return_value = True
    mock_saver.add_vacancies.return_value = ["Success"]
    mock_saver.add_vacancy_batch_optimized.return_value = ["Success"]
    mock_saver.get_vacancies.return_value = []
    mock_saver.get_vacancies_count.return_value = 0
    mock_saver.delete_vacancy_by_id.return_value = True
    mock_saver.save_vacancies.return_value = 1
    mock_saver.is_vacancy_exists.return_value = False
    return mock_saver


@pytest.fixture
def consolidated_api_mocks():
    """Консолидированные моки для всех API"""
    mock_hh_api = Mock()
    mock_hh_api.get_vacancies.return_value = [{"name": "HH Test Vacancy"}]
    mock_hh_api.get_vacancies_page.return_value = [{"name": "HH Test Vacancy"}]
    
    mock_sj_api = Mock()
    mock_sj_api.get_vacancies.return_value = [{"profession": "SJ Test Job"}]
    mock_sj_api.get_vacancies_page.return_value = [{"profession": "SJ Test Job"}]
    
    mock_unified_api = Mock()
    mock_unified_api.get_vacancies_from_sources.return_value = [{"name": "Unified Test Vacancy"}]
    
    return {
        "hh_api": mock_hh_api,
        "sj_api": mock_sj_api,
        "unified_api": mock_unified_api
    }
