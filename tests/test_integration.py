"""
Интеграционные тесты для проверки взаимодействия компонентов
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.operations.vacancy_operations import VacancyOperations
from src.storage.postgres_saver import PostgresSaver
from src.utils.cache import FileCache
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestStorageIntegration:
    """Интеграционные тесты для хранилища"""

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура с тестовой вакансией"""
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
            source="hh.ru",
        )

    @patch("psycopg2.connect")
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

    @patch("src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api")
    def test_hh_api_integration(self, mock_connect):
        """Тест интеграции с HeadHunter API"""
        # Настраиваем мок ответа
        mock_connect.return_value = {
            "items": [
                {
                    "id": "123",
                    "name": "Test Vacancy",
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "employer": {"name": "Test Company"},
                    "published_at": "2024-01-01T00:00:00+03:00",
                    "source": "hh.ru",
                }
            ],
            "found": 1,
            "pages": 1,
        }

        api = HeadHunterAPI()
        vacancies = api.get_vacancies(search_query="python")

        assert len(vacancies) == 1
        assert vacancies[0]["name"] == "Test Vacancy"
        assert vacancies[0]["source"] == "hh.ru"

    @patch("src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api")
    def test_superjob_api_integration(self, mock_connect):
        """Тест интеграции с SuperJob API"""
        mock_connect.return_value = {
            "objects": [
                {
                    "id": 456,
                    "profession": "Test Job",
                    "link": "https://superjob.ru/vakansii/test-456.html",
                    "firm_name": "SJ Company",
                    "date_published": 1704067200,
                    "source": "superjob.ru",
                }
            ],
            "total": 1,
        }

        api = SuperJobAPI()
        vacancies = api.get_vacancies(search_query="java")

        assert len(vacancies) == 1
        assert vacancies[0]["profession"] == "Test Job"
        assert vacancies[0]["source"] == "superjob.ru"


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
            employer={"name": "Integration Company"},
            vacancy_id="789",
            published_at="2024-01-01T00:00:00+03:00",
            source="hh.ru",
        )

    @patch("psycopg2.connect")
    @patch("src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api")
    def test_search_and_save_workflow(self, mock_connect_api, mock_connect_db, sample_vacancy):
        """Тест полного процесса поиска и сохранения"""
        # Настраиваем мок для API
        mock_connect_api.return_value = {
            "items": [
                {
                    "id": "789",
                    "name": "Integration Test Job",
                    "alternate_url": "https://hh.ru/vacancy/789",
                    "employer": {"name": "Integration Company"},
                    "published_at": "2024-01-01T00:00:00+03:00",
                    "source": "hh.ru",
                }
            ],
            "found": 1,
            "pages": 1,
        }

        # Настраиваем мок для базы данных
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = (0,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect_db.return_value = mock_conn

        # Выполняем поиск
        api = HeadHunterAPI()
        vacancies_data = api.get_vacancies(search_query="python")

        # Конвертируем в объекты Vacancy
        vacancies = [Vacancy.from_dict(item) for item in vacancies_data]

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

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    @patch("builtins.open")
    @patch("json.dump")
    @patch("json.load")
    def test_cache_integration(
        self, mock_json_load, mock_json_dump, mock_open, mock_exists, mock_mkdir, mock_cache_dir
    ):
        """Тест интеграции кэширования"""
        mock_exists.return_value = True
        mock_json_load.return_value = {
            "data": {"test": "data"},
            "meta": {"params": "test_params"},
            "timestamp": 1234567890,
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

    @patch("src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api")
    def test_api_error_handling(self, mock_connect):
        """Тест обработки ошибок API"""
        mock_connect.side_effect = Exception("Network error")

        api = HeadHunterAPI()
        vacancies = api.get_vacancies(search_query="python")

        # При ошибке должен возвращаться пустой список
        assert vacancies == []

    @patch("psycopg2.connect")
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
            salary={"from": 50000, "to": 100000, "currency": "RUR"},
            description="Test description",
            requirements="Test requirements",
            responsibilities="Test responsibilities",
            experience="Test experience",
            employment="Test employment",
            schedule="Test schedule",
            employer={"name": "Test Formatter Company"},
            vacancy_id="formatter_123",
            published_at="2024-01-01T00:00:00+03:00",
            source="hh.ru",
        )

    def test_vacancy_formatter_integration(self, sample_vacancy):
        """Тест интеграции форматирования вакансий"""
        formatter = VacancyFormatter()
        operations = VacancyOperations(storage=None, api=None)  # Имитация инициализации operations

        formatted_text = formatter.format_vacancy_info(sample_vacancy, number=1)

        # Проверяем, что форматирование работает
        assert "Test Formatter Vacancy" in formatted_text
        assert "Test Formatter Company" in formatted_text
        assert "от 50" in formatted_text or "до 100" in formatted_text
        assert "formatter_123" in formatted_text
        assert hasattr(formatter, "format_vacancy_info")
        assert hasattr(operations, "filter_vacancies_by_multiple_keywords")

    def test_brief_formatter_integration(self, sample_vacancy):
        """Тест краткого форматирования"""
        brief_text = VacancyFormatter.format_vacancy_brief(sample_vacancy, number=1)

        # Проверяем краткое форматирование
        assert isinstance(brief_text, str)
        assert "Test Formatter Vacancy" in brief_text


from unittest.mock import MagicMock, Mock, patch

import pytest

from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.operations.vacancy_operations import VacancyOperations
from src.storage.postgres_saver import PostgresSaver
from src.utils.cache import FileCache
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestStorageIntegration:
    """Интеграционные тесты для хранилища"""

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура с тестовой вакансией"""
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
            source="hh.ru",
        )

    @patch("psycopg2.connect")
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

    @patch("src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api")
    def test_hh_api_integration(self, mock_connect):
        """Тест интеграции с HeadHunter API"""
        # Настраиваем мок ответа
        mock_connect.return_value = {
            "items": [
                {
                    "id": "123",
                    "name": "Test Vacancy",
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "employer": {"name": "Test Company"},
                    "published_at": "2024-01-01T00:00:00+03:00",
                    "source": "hh.ru",
                }
            ],
            "found": 1,
            "pages": 1,
        }

        api = HeadHunterAPI()
        vacancies = api.get_vacancies(search_query="python")

        assert len(vacancies) == 1
        assert vacancies[0]["name"] == "Test Vacancy"
        assert vacancies[0]["source"] == "hh.ru"

    @patch("src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api")
    def test_superjob_api_integration(self, mock_connect):
        """Тест интеграции с SuperJob API"""
        mock_connect.return_value = {
            "objects": [
                {
                    "id": 456,
                    "profession": "Test Job",
                    "link": "https://superjob.ru/vakansii/test-456.html",
                    "firm_name": "SJ Company",
                    "date_published": 1704067200,
                    "source": "superjob.ru",
                }
            ],
            "total": 1,
        }

        api = SuperJobAPI()
        vacancies = api.get_vacancies(search_query="java")

        assert len(vacancies) == 1
        assert vacancies[0]["profession"] == "Test Job"
        assert vacancies[0]["source"] == "superjob.ru"


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
            employer={"name": "Integration Company"},
            vacancy_id="789",
            published_at="2024-01-01T00:00:00+03:00",
            source="hh.ru",
        )

    @patch("psycopg2.connect")
    @patch("src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api")
    def test_search_and_save_workflow(self, mock_connect_api, mock_connect_db, sample_vacancy):
        """Тест полного процесса поиска и сохранения"""
        # Настраиваем мок для API
        mock_connect_api.return_value = {
            "items": [
                {
                    "id": "789",
                    "name": "Integration Test Job",
                    "alternate_url": "https://hh.ru/vacancy/789",
                    "employer": {"name": "Integration Company"},
                    "published_at": "2024-01-01T00:00:00+03:00",
                    "source": "hh.ru",
                }
            ],
            "found": 1,
            "pages": 1,
        }

        # Настраиваем мок для базы данных
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = (0,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect_db.return_value = mock_conn

        # Выполняем поиск
        api = HeadHunterAPI()
        vacancies_data = api.get_vacancies(search_query="python")

        # Конвертируем в объекты Vacancy
        vacancies = [Vacancy.from_dict(item) for item in vacancies_data]

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

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    @patch("builtins.open")
    @patch("json.dump")
    @patch("json.load")
    def test_cache_integration(
        self, mock_json_load, mock_json_dump, mock_open, mock_exists, mock_mkdir, mock_cache_dir
    ):
        """Тест интеграции кэширования"""
        mock_exists.return_value = True
        mock_json_load.return_value = {
            "data": {"test": "data"},
            "meta": {"params": "test_params"},
            "timestamp": 1234567890,
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

    @patch("src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api")
    def test_api_error_handling(self, mock_connect):
        """Тест обработки ошибок API"""
        mock_connect.side_effect = Exception("Network error")

        api = HeadHunterAPI()
        vacancies = api.get_vacancies(search_query="python")

        # При ошибке должен возвращаться пустой список
        assert vacancies == []

    @patch("psycopg2.connect")
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
            salary={"from": 50000, "to": 100000, "currency": "RUR"},
            description="Test description",
            requirements="Test requirements",
            responsibilities="Test responsibilities",
            experience="Test experience",
            employment="Test employment",
            schedule="Test schedule",
            employer={"name": "Test Formatter Company"},
            vacancy_id="formatter_123",
            published_at="2024-01-01T00:00:00+03:00",
            source="hh.ru",
        )

    def test_vacancy_formatter_integration(self, sample_vacancy):
        """Тест интеграции форматирования вакансий"""
        formatter = VacancyFormatter()
        # Имитация инициализации operations с моками
        mock_storage = Mock()
        mock_api = Mock()
        operations = VacancyOperations(storage=mock_storage, api=mock_api)

        formatted_text = formatter.format_vacancy_info(sample_vacancy, number=1)

        # Проверяем, что форматирование работает
        assert "Test Formatter Vacancy" in formatted_text
        assert "Test Formatter Company" in formatted_text
        # Проверка зарплаты с учетом возможных форматов
        salary_from = sample_vacancy.salary.get("from")
        salary_to = sample_vacancy.salary.get("to")
        salary_str = ""
        if salary_from is not None and salary_to is not None:
            salary_str = f"от {salary_from:,} до {salary_to:,} RUR".replace(",", " ")
        elif salary_from is not None:
            salary_str = f"от {salary_from:,} RUR".replace(",", " ")
        elif salary_to is not None:
            salary_str = f"до {salary_to:,} RUR".replace(",", " ")

        assert salary_str in formatted_text
        assert "formatter_123" in formatted_text
        assert hasattr(formatter, "format_vacancy_info")
        assert hasattr(operations, "filter_vacancies_by_multiple_keywords")

    def test_brief_formatter_integration(self, sample_vacancy):
        """Тест краткого форматирования"""
        brief_text = VacancyFormatter.format_vacancy_brief(sample_vacancy, number=1)

        # Проверяем краткое форматирование
        assert isinstance(brief_text, str)
        assert "Test Formatter Vacancy" in brief_text
