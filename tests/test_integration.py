
"""
Интеграционные тесты для проверки взаимодействия компонентов
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.storage.postgres_saver import PostgresSaver
from src.vacancies.models import Vacancy
from src.utils.cache import FileCache


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
    def mock_cache_dir(self, tmp_path):
        """Создает временную директорию для кэша"""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return str(cache_dir)

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    @patch('json.dump')
    @patch('json.load')
    def test_cache_integration(self, mock_json_load, mock_json_dump, mock_open, mock_exists, mock_mkdir, mock_cache_dir):
        """Тест интеграции кэширования"""
        mock_exists.return_value = True
        mock_json_load.return_value = {
            "data": {"test": "data"},
            "meta": {"params": "test_params"},
            "timestamp": 1234567890
        }

        cache = FileCache(cache_dir=mock_cache_dir)

        # Тест сохранения в кэш
        test_data = {"test": "data"}
        test_params = {"query": "python"}
        cache.save_response("test", test_params, test_data)

        # Проверяем, что методы были вызваны
        mock_open.assert_called()
        mock_json_dump.assert_called()

        # Тест загрузки из кэша
        loaded_data = cache.load_response("test", test_params)
        assert loaded_data is not None
        assert loaded_data["data"]["test"] == "data"


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


class TestFormatterIntegration:
    """Интеграционные тесты форматирования"""

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура с тестовой вакансией для форматирования"""
        return Vacancy(
            title="Test Formatter Vacancy",
            url="https://test.com/vacancy/123",
            salary={'from': 50000, 'to': 100000, 'currency': 'RUR'},
            description="Test description",
            requirements="Test requirements",
            responsibilities="Test responsibilities",
            experience="Test experience",
            employment="Test employment",
            schedule="Test schedule",
            employer={'name': 'Test Formatter Company'},
            vacancy_id="formatter_123",
            published_at="2024-01-01T00:00:00+03:00",
            source="hh.ru"
        )

    def test_vacancy_formatter_integration(self, sample_vacancy):
        """Тест интеграции форматирования вакансий"""
        from src.utils.vacancy_formatter import VacancyFormatter

        formatter = VacancyFormatter()
        formatted_text = formatter.format_vacancy_info(sample_vacancy, number=1)

        # Проверяем, что форматирование работает
        assert "Test Formatter Vacancy" in formatted_text
        assert "Test Formatter Company" in formatted_text
        assert "от 50" in formatted_text or "до 100" in formatted_text
        assert "formatter_123" in formatted_text

    def test_brief_formatter_integration(self, sample_vacancy):
        """Тест краткого форматирования"""
        from src.utils.vacancy_formatter import VacancyFormatter

        brief_text = VacancyFormatter.format_vacancy_brief(sample_vacancy, number=1)

        # Проверяем краткое форматирование
        assert isinstance(brief_text, str)
        assert "Test Formatter Vacancy" in brief_text
