"""
Интеграционные тесты для проверки взаимодействия компонентов
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.storage.postgres_saver import PostgresSaver
from src.vacancies.models import Vacancy
from src.utils.cache import CacheManager


class TestStorageIntegration:
    """Интеграционные тесты для хранилища"""

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура с тестовой вакансией"""
        return Vacancy(
            title="Test Vacancy",
            url="https://test.com/vacancy/1",
            salary={'from': 100000, 'to': 150000, 'currency': 'RUR'},
            description="Test description",
            requirements="Test requirements",
            responsibilities="Test responsibilities",
            experience="Test experience",
            employment="Test employment",
            schedule="Test schedule",
            employer={'name': 'Test Company'},
            vacancy_id="test_1",
            published_at="2024-01-15T10:00:00",
            source="hh.ru"
        )

    @patch('psycopg2.connect')
    def test_postgres_saver_integration(self, mock_connect, sample_vacancy):
        """Тест интеграции с PostgreSQL"""
        # Настраиваем мок подключения
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = (0,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Создаем хранилище и тестируем операции
        storage = PostgresSaver()

        # Тест добавления
        result = storage.add_vacancy(sample_vacancy)
        assert result is True

        # Тест получения
        vacancies = storage.get_vacancies()
        assert isinstance(vacancies, list)

        # Тест подсчета
        count = storage.get_vacancies_count()
        assert isinstance(count, int)


class TestAPIIntegration:
    """Интеграционные тесты для API"""

    @patch('requests.get')
    def test_hh_api_integration(self, mock_get):
        """Тест интеграции с HeadHunter API"""
        # Настраиваем мок ответа
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "123",
                    "name": "Test Vacancy",
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "employer": {"name": "Test Company"},
                    "published_at": "2024-01-01T00:00:00+03:00"
                }
            ],
            "found": 1
        }
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        vacancies = api.search_vacancies(query="python")

        assert len(vacancies) == 1
        assert vacancies[0].title == "Test Vacancy"
        assert vacancies[0].source == "hh.ru"

    @patch('requests.get')
    def test_superjob_api_integration(self, mock_get):
        """Тест интеграции с SuperJob API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "objects": [
                {
                    "id": 456,
                    "profession": "Test Job",
                    "link": "https://superjob.ru/vakansii/test-456.html",
                    "firm_name": "SJ Company",
                    "date_published": 1704067200
                }
            ],
            "total": 1
        }
        mock_get.return_value = mock_response

        api = SuperJobAPI()
        vacancies = api.search_vacancies(query="java")

        assert len(vacancies) == 1
        assert vacancies[0].title == "Test Job"
        assert vacancies[0].source == "superjob.ru"


class TestFullWorkflowIntegration:
    """Интеграционные тесты полного рабочего процесса"""

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура с тестовой вакансией для полного рабочего процесса"""
        return Vacancy(
            title="Integration Test Job",
            url="https://hh.ru/vacancy/789",
            salary=None,
            description="Integration test description",
            requirements="Integration test requirements",
            responsibilities="Integration test responsibilities",
            experience="Integration test experience",
            employment="Integration test employment",
            schedule="Integration test schedule",
            employer={'name': 'Integration Company'},
            vacancy_id="789",
            published_at="2024-01-01T00:00:00+03:00",
            source="hh.ru"
        )

    @patch('psycopg2.connect')
    @patch('requests.get')
    def test_search_and_save_workflow(self, mock_get, mock_connect, sample_vacancy):
        """Тест полного процесса поиска и сохранения"""
        # Настраиваем мок для API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "789",
                    "name": "Integration Test Job",
                    "alternate_url": "https://hh.ru/vacancy/789",
                    "employer": {"name": "Integration Company"},
                    "published_at": "2024-01-01T00:00:00+03:00"
                }
            ],
            "found": 1
        }
        mock_get.return_value = mock_response

        # Настраиваем мок для базы данных
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = (0,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Выполняем поиск
        api = HeadHunterAPI()
        vacancies = api.search_vacancies(query="python")

        # Сохраняем результаты
        storage = PostgresSaver()
        for vacancy in vacancies:
            result = storage.add_vacancy(vacancy)
            assert result is True

        # Проверяем, что все прошло успешно
        assert len(vacancies) == 1
        assert vacancies[0].title == "Integration Test Job"


class TestCacheIntegration:
    """Интеграционные тесты кэширования"""

    @pytest.fixture
    def mock_cache_file(self, tmp_path):
        """Создает временный файл для кэша"""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "hh_test_key.json"
        cache_file.write_text('{"data": {"test": "data"}, "meta": {"params": "test_params"}}')
        return str(cache_dir)

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_cache_integration(self, mock_open, mock_exists, mock_cache_file):
        """Тест интеграции кэширования"""
        mock_exists.return_value = True  # Simulate file existing
        mock_file_handle = Mock()
        mock_open.return_value.__enter__.return_value = mock_file_handle

        cache = CacheManager()

        # Тест сохранения в кэш
        test_data = {"test": "data"}
        cache.save_to_cache("test_key", test_data, "hh")

        # Проверяем, что файл был создан (или попытка записи)
        mock_open.assert_called()

        # Тест загрузки из кэша
        loaded_data = cache.load_from_cache("test_key", "hh")
        assert loaded_data == test_data


class TestErrorHandlingIntegration:
    """Интеграционные тесты обработки ошибок"""

    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Тест обработки ошибок API"""
        mock_get.side_effect = Exception("Network error")

        api = HeadHunterAPI()
        vacancies = api.search_vacancies(query="python")

        # При ошибке должен возвращаться пустой список
        assert vacancies == []

    @patch('psycopg2.connect')
    def test_database_error_handling(self, mock_connect):
        """Тест обработки ошибок базы данных"""
        mock_connect.side_effect = Exception("Database connection error")

        storage = PostgresSaver()

        # При ошибке операции должны возвращать False/пустые результаты
        assert storage.get_vacancies() == []
        assert storage.get_vacancies_count() == 0