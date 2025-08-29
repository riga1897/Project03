
"""
Интеграционные тесты для проверки взаимодействия компонентов
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.utils.vacancy_operations import VacancyOperations
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
        # Исправляем мок для field_info - возвращаем правильную структуру
        # Добавляем больше ответов для всех возможных запросов
        mock_responses = [
            (0,),  # для check database exists
        ]
        # Добавляем ответы для каждого поля в required_fields (около 20 полей)
        for _ in range(25):
            mock_responses.extend([
                ("column_name", "integer"),
                ("column_name", "text"), 
                ("column_name", "varchar"),
                ("column_name", "timestamp"),
            ])
        
        mock_cursor.fetchone.side_effect = mock_responses
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
        # Настраиваем правильные ответы для всех запросов
        mock_responses = [
            (0,),  # для check database exists
        ]
        # Добавляем ответы для каждого поля в required_fields (около 20 полей)
        for _ in range(25):
            mock_responses.extend([
                ("column_name", "integer"),
                ("column_name", "text"), 
                ("column_name", "varchar"),
                ("column_name", "timestamp"),
            ])
        
        mock_cursor.fetchone.side_effect = mock_responses
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

    def test_cache_integration(self, mock_cache_dir):
        """Тест интеграции кэширования"""
        cache = FileCache(cache_dir=mock_cache_dir)

        # Тест сохранения в кэш
        test_data = {"test": "data"}
        test_params = {"query": "python"}
        cache.save_response("test", test_params, test_data)

        # Тест загрузки из кэша
        loaded_data = cache.load_response("test", test_params)
        
        # Проверяем, что данные загрузились
        assert loaded_data is not None
        assert loaded_data["data"]["test"] == "data"

        # Проверяем, что кэш работает правильно
        # FileCache не имеет метода clear_cache, поэтому просто проверяем загрузку
        loaded_again = cache.load_response("test", test_params)
        assert loaded_again is not None
        assert loaded_again["data"]["test"] == "data"


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

        # Тест должен перехватывать исключение при создании storage
        with pytest.raises(Exception) as exc_info:
            PostgresSaver()
        
        assert "Database connection error" in str(exc_info.value)


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

        formatted_text = formatter.format_vacancy_info(sample_vacancy, number=1)

        # Проверяем, что форматирование работает
        assert "Test Formatter Vacancy" in formatted_text
        assert "Test Formatter Company" in formatted_text
        assert "formatter_123" in formatted_text

        # Проверяем наличие методов у VacancyOperations
        assert hasattr(VacancyOperations, "filter_vacancies_by_multiple_keywords")
        assert hasattr(VacancyOperations, "search_vacancies_advanced")

    def test_brief_formatter_integration(self, sample_vacancy):
        """Тест краткого форматирования"""
        brief_text = VacancyFormatter.format_vacancy_brief(sample_vacancy, number=1)

        # Проверяем краткое форматирование
        assert isinstance(brief_text, str)
        assert "Test Formatter Vacancy" in brief_text


class TestVacancyOperationsIntegration:
    """Интеграционные тесты для VacancyOperations"""

    @pytest.fixture
    def test_vacancies(self):
        """Фикстура с тестовыми вакансиями"""
        return [
            Vacancy(
                title="Python Developer",
                url="https://test.com/1",
                vacancy_id="1",
                source="hh.ru",
                salary={"from": 100000, "to": 150000, "currency": "RUR"},
                description="Python Django PostgreSQL",
                requirements="Python, Django, PostgreSQL",
            ),
            Vacancy(
                title="Java Developer",
                url="https://test.com/2",
                vacancy_id="2",
                source="superjob.ru",
                salary={"from": 120000, "to": 180000, "currency": "RUR"},
                description="Java Spring Boot",
                requirements="Java, Spring Boot",
            ),
            Vacancy(
                title="Frontend Developer",
                url="https://test.com/3",
                vacancy_id="3",
                source="hh.ru",
                description="JavaScript React Vue",
                requirements="JavaScript, React, Vue",
            ),
        ]

    def test_vacancy_operations_filters(self, test_vacancies):
        """Тест фильтрации вакансий"""
        ops = VacancyOperations()

        # Тест фильтрации по зарплате
        with_salary = ops.get_vacancies_with_salary(test_vacancies)
        assert len(with_salary) == 2

        # Тест фильтрации по минимальной зарплате
        # Java Developer имеет salary_from=120000, что >= 110000
        # Python Developer имеет salary_from=100000, что < 110000
        high_salary = ops.filter_vacancies_by_min_salary(test_vacancies, 110000)
        assert len(high_salary) == 1  # Только Java Developer

        # Тест сортировки по зарплате
        sorted_vacancies = ops.sort_vacancies_by_salary(test_vacancies)
        assert len(sorted_vacancies) == 3

    def test_vacancy_operations_search(self, test_vacancies):
        """Тест поиска вакансий"""
        ops = VacancyOperations()

        # Тест поиска по ключевым словам
        python_vacancies = ops.filter_vacancies_by_multiple_keywords(test_vacancies, ["Python"])
        assert len(python_vacancies) == 1
        assert python_vacancies[0].vacancy_id == "1"

        # Тест расширенного поиска - "Python OR Java" должен находить вакансии
        advanced_search = ops.search_vacancies_advanced(test_vacancies, "Python OR Java")
        # Проверяем реальное поведение: должно найти минимум 2 вакансии
        assert len(advanced_search) >= 2

        # Тест поиска с AND оператором
        and_search = ops.search_vacancies_advanced(test_vacancies, "Python AND Django")
        assert len(and_search) >= 1
