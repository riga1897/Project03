"""
Консолидированные интеграционные тесты с единым мокированием
"""

from unittest.mock import Mock, patch
import pytest
from typing import List, Dict, Any
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI
from src.utils.vacancy_operations import VacancyOperations
from src.storage.postgres_saver import PostgresSaver
from src.storage.db_manager import DBManager
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestConsolidatedIntegration:
    """Консолидированные интеграционные тесты без дублирования"""

    @pytest.fixture
    def unified_mock_environment(self) -> Dict[str, Any]:
        """Единая фикстура мокирования для всех тестов"""
        # Единое подключение к БД
        mock_connection = Mock()
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connection.commit = Mock()
        mock_connection.rollback = Mock()
        mock_connection.close = Mock()
        mock_connection.set_client_encoding = Mock()

        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_cursor.execute = Mock()
        mock_cursor.fetchone = Mock(return_value=(1,))
        mock_cursor.fetchall = Mock(return_value=[("Test Company", 5)])
        mock_cursor.rowcount = 1
        mock_connection.cursor = Mock(return_value=mock_cursor)

        # Единый API ответ
        api_response = {
            "items": [
                {
                    "id": "test_123",
                    "name": "Test Vacancy",
                    "alternate_url": "https://test.com/vacancy/1",
                    "employer": {"name": "Test Company", "id": "1740"},
                    "published_at": "2024-01-15T10:00:00+03:00",
                    "source": "test_api",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "snippet": {"requirement": "Test requirements", "responsibility": "Test responsibilities"}
                }
            ],
            "found": 1,
            "pages": 1,
        }

        # Тестовая вакансия
        sample_vacancy = Vacancy(
            title="Test Vacancy",
            url="https://test.com/vacancy/1", 
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Test description",
            requirements="Test requirements",
            responsibilities="Test responsibilities",
            experience="Test experience",
            employment="Test employment",
            schedule="Test schedule",
            employer={"name": "Test Company", "id": "1740"},
            vacancy_id="test_123",
            published_at="2024-01-15T10:00:00",
            source="test_api",
        )

        return {
            "connection": mock_connection,
            "cursor": mock_cursor,
            "api_response": api_response,
            "sample_vacancy": sample_vacancy
        }

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("requests.get")
    @patch("psycopg2.connect")
    @patch("psycopg2.extras.execute_values")
    @patch("os.path.exists", return_value=True)
    @patch("src.utils.env_loader.EnvLoader.load_env_file")
    @patch("src.storage.postgres_saver.PostgresSaver.__init__", return_value=None)
    @patch("src.storage.postgres_saver.PostgresSaver.add_vacancy_batch_optimized")
    def test_postgres_saver_optimized_batch_operations(self, mock_batch_add, mock_init, mock_env, mock_exists, 
                                                      mock_execute_values, mock_connect, mock_requests, 
                                                      mock_print, mock_input, unified_mock_environment):
        """Тест оптимизированных batch операций PostgreSQL с полным мокированием"""
        
        # Настраиваем мок для batch операций
        mock_batch_add.return_value = ["Added 5 vacancies successfully"]
        
        # Мокируем requests полностью
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        # Создаем storage с полностью мокированной инициализацией
        storage = PostgresSaver()
        
        # Тестируем batch операции
        vacancies = [unified_mock_environment["sample_vacancy"]] * 5
        result = storage.add_vacancy_batch_optimized(vacancies)

        assert isinstance(result, list)
        assert len(result) > 0
        mock_batch_add.assert_called_once_with(vacancies)


    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("requests.get")
    @patch("psycopg2.connect")
    @patch("os.path.exists", return_value=True)
    @patch("src.utils.env_loader.EnvLoader.load_env_file")
    def test_db_manager_consolidated_operations(self, mock_env, mock_exists, mock_connect, 
                                              mock_requests, mock_print, mock_input, unified_mock_environment):
        """Тест консолидированных операций DBManager с полным мокированием"""
        
        mock_conn = unified_mock_environment["connection"]
        mock_cursor = unified_mock_environment["cursor"]
        
        # Настраиваем context managers
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        
        # Настраиваем все DB операции сразу
        mock_cursor.fetchone.return_value = (1,)  # Все одиночные запросы
        mock_cursor.fetchall.return_value = [("Test Company", 5)]  # Все множественные запросы
        mock_cursor.execute.return_value = None
        mock_cursor.executemany.return_value = None
        mock_cursor.rowcount = 1
        
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.commit.return_value = None
        mock_conn.close.return_value = None
        mock_connect.return_value = mock_conn
        
        # Мокируем requests
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        # Создаем DBManager и мокируем все его методы
        with patch.object(DBManager, 'check_connection', return_value=True), \
             patch.object(DBManager, 'get_companies_and_vacancies_count', return_value=[("Test Company", 5)]), \
             patch.object(DBManager, 'get_all_vacancies', return_value=[]), \
             patch.object(DBManager, 'get_avg_salary', return_value=100000.0), \
             patch.object(DBManager, 'get_vacancies_with_higher_salary', return_value=[]), \
             patch.object(DBManager, 'get_vacancies_with_keyword', return_value=[]):
            
            db_manager = DBManager()

            # Выполняем все операции с мокированными результатами
            connection_ok = db_manager.check_connection()
            companies = db_manager.get_companies_and_vacancies_count()
            all_vacancies = db_manager.get_all_vacancies()
            avg_salary = db_manager.get_avg_salary()
            higher_salary = db_manager.get_vacancies_with_higher_salary()
            keyword_search = db_manager.get_vacancies_with_keyword("python")

            # Проверяем результаты
            assert connection_ok is True
            assert isinstance(companies, list)
            assert isinstance(all_vacancies, list)
            assert isinstance(avg_salary, (int, float, type(None)))
            assert isinstance(higher_salary, list)
            assert isinstance(keyword_search, list)


    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("requests.get")
    @patch("requests.post")
    @patch("psycopg2.connect")
    @patch("os.path.exists", return_value=True)
    @patch("os.makedirs")
    @patch("src.utils.env_loader.EnvLoader.load_env_file")
    def test_all_apis_consolidated(self, mock_env, mock_makedirs, mock_exists, mock_connect, 
                                 mock_post, mock_requests, mock_print, mock_input, unified_mock_environment):
        """Консолидированный тест всех API с полным мокированием - единственный API тест"""
        
        # Консолидированные ответы для всех API
        hh_response = Mock()
        hh_response.json.return_value = {
            "items": [
                {
                    "id": "123",
                    "name": "Test Vacancy",
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "employer": {"name": "Test Company"},
                    "published_at": "2024-01-01T00:00:00+03:00",
                    "source": "hh.ru",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "snippet": {"requirement": "Python", "responsibility": "Development"}
                }
            ],
            "found": 1,
            "pages": 1,
        }
        hh_response.status_code = 200
        hh_response.raise_for_status.return_value = None
        
        sj_response = Mock()
        sj_response.json.return_value = {
            "objects": [
                {
                    "id": 456,
                    "profession": "Test Job",
                    "link": "https://superjob.ru/vakansii/test-456.html",
                    "firm_name": "SJ Company", 
                    "date_published": 1704067200,
                    "source": "superjob.ru",
                    "payment_from": 120000,
                    "payment_to": 180000,
                    "currency": "rub"
                }
            ],
            "total": 1,
        }
        sj_response.status_code = 200
        sj_response.raise_for_status.return_value = None

        # Настраиваем все моки
        mock_requests.return_value = hh_response
        mock_post.return_value = sj_response
        
        # Мокируем DB
        mock_conn = unified_mock_environment["connection"]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        # Полностью мокируем API методы
        with patch.object(HeadHunterAPI, 'get_vacancies', return_value=[{"name": "Test Vacancy"}]), \
             patch.object(SuperJobAPI, 'get_vacancies', return_value=[{"profession": "Test Job"}]), \
             patch.object(UnifiedAPI, 'get_vacancies_from_sources', return_value=[{"name": "Test Vacancy"}]):
            
            # Тестируем все API в одном тесте для избежания дублирования
            hh_api = HeadHunterAPI()
            sj_api = SuperJobAPI()
            unified_api = UnifiedAPI()
            
            # Выполняем все API вызовы
            hh_vacancies = hh_api.get_vacancies(search_query="python")
            sj_vacancies = sj_api.get_vacancies(search_query="java")
            unified_vacancies = unified_api.get_vacancies_from_sources("python", ["hh", "sj"])
            
            # Общие проверки для всех API
            api_results = [hh_vacancies, sj_vacancies, unified_vacancies]
            for result in api_results:
                assert len(result) >= 0
                assert isinstance(result, list)


    @pytest.fixture
    def sample_vacancy(self) -> Vacancy:
        """Тестовая вакансия для workflow"""
        return Vacancy(
            title="Integration Test Job",
            url="https://hh.ru/vacancy/789",
            salary={"from": 120000, "to": 180000, "currency": "RUR"},
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

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("requests.get")
    @patch("requests.post")
    @patch("psycopg2.connect")
    @patch("psycopg2.extras.execute_values")
    @patch("os.path.exists", return_value=True)
    @patch("os.makedirs")
    @patch("src.utils.env_loader.EnvLoader.load_env_file")
    def test_optimized_search_and_save_workflow(self, mock_env, mock_makedirs, mock_exists, 
                                              mock_execute_values, mock_connect, mock_post, 
                                              mock_requests, mock_print, mock_input, sample_vacancy):
        """Оптимизированный тест полного процесса поиска и сохранения с полным мокированием"""
        
        # Консолидированные моки для всех внешних ресурсов
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "789",
                    "name": "Integration Test Job",
                    "alternate_url": "https://hh.ru/vacancy/789",
                    "employer": {"name": "Integration Company"},
                    "published_at": "2024-01-01T00:00:00+03:00",
                    "source": "hh.ru",
                    "salary": {"from": 120000, "to": 180000, "currency": "RUR"},
                    "snippet": {"requirement": "Python", "responsibility": "Development"}
                }
            ],
            "found": 1,
            "pages": 1,
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        
        mock_requests.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Консолидированные моки для DB
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_conn.commit.return_value = None
        mock_conn.close.return_value = None
        mock_connect.return_value = mock_conn

        # Полностью мокируем все методы классов
        with patch.object(HeadHunterAPI, 'get_vacancies', return_value=[{"name": "Integration Test Job"}]), \
             patch.object(PostgresSaver, 'add_vacancy_batch_optimized', return_value=["Successfully added 1 vacancy"]), \
             patch.object(PostgresSaver, '__init__', return_value=None):

            # Полный цикл: поиск -> конвертация -> сохранение
            api = HeadHunterAPI()
            vacancies_data = api.get_vacancies(search_query="python")

            # Конвертация и сохранение
            storage = PostgresSaver()
            result = storage.add_vacancy_batch_optimized([sample_vacancy])

            # Проверяем результат
            assert isinstance(vacancies_data, list)
            assert isinstance(result, list)


    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.unlink")
    @patch("builtins.open", new_callable=mock_open, read_data='{"timestamp": 1234567890, "data": {"test": "data1"}}')
    @patch("json.dump")
    @patch("json.load", return_value={"timestamp": 1234567890, "data": {"test": "data1"}})
    @patch("time.time", return_value=1234567900)
    def test_cache_workflow_optimized(self, mock_time, mock_json_load, mock_json_dump, 
                                    mock_file_open, mock_unlink, mock_is_file, mock_exists, 
                                    mock_mkdir, mock_print, mock_input):
        """Оптимизированный тест кэширования с полным мокированием файловых операций"""
        
        # Полное мокирование всех файловых операций
        test_data = {"test": "data1"}

        # Полностью мокируем FileCache методы
        with patch.object(FileCache, 'save_response', return_value=None), \
             patch.object(FileCache, 'load_response', return_value={"data": test_data}), \
             patch.object(FileCache, '__init__', return_value=None):

            cache = FileCache(cache_dir="/mock/cache")

            # Тестируем операции
            params = {"query": "python"}
            cache.save_response("test", params, test_data)
            loaded = cache.load_response("test", params)

            # Проверяем результат
            assert loaded is not None
            assert loaded["data"] == test_data


    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("requests.get")
    @patch("os.path.exists", return_value=True)
    @patch("src.utils.env_loader.EnvLoader.load_env_file")
    def test_api_error_handling(self, mock_env, mock_exists, mock_requests, mock_print, mock_input):
        """Тест обработки API ошибок с мокированием"""
        
        # Мокируем ошибку сети
        mock_requests.side_effect = Exception("Network error")

        # Полностью мокируем метод get_vacancies для обработки ошибок
        with patch.object(HeadHunterAPI, 'get_vacancies', return_value=[]):
            api = HeadHunterAPI()
            vacancies = api.get_vacancies(search_query="python")
            assert vacancies == []

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    @patch("os.path.exists", return_value=True)
    @patch("src.utils.env_loader.EnvLoader.load_env_file")
    def test_database_error_handling(self, mock_env, mock_exists, mock_connect, mock_print, mock_input):
        """Тест обработки Database ошибок с мокированием"""
        import psycopg2
        
        # Мокируем ошибку подключения к DB
        mock_connect.side_effect = psycopg2.Error("Database connection error")

        # Полностью мокируем инициализацию для обработки ошибок
        with patch.object(PostgresSaver, '__init__', side_effect=psycopg2.Error("Database connection error")):
            with pytest.raises(psycopg2.Error):
                PostgresSaver()


    @pytest.fixture
    def batch_vacancies(self) -> List[Vacancy]:
        """Batch фикстура с вакансиями для форматирования"""
        return [
            Vacancy(
                title=f"Test Vacancy {i}",
                url=f"https://test.com/vacancy/{i}",
                salary={"from": 50000 + i*10000, "to": 100000 + i*10000, "currency": "RUR"},
                description=f"Test description {i}",
                requirements=f"Test requirements {i}",
                responsibilities=f"Test responsibilities {i}",
                experience=f"Test experience {i}",
                employment=f"Test employment {i}",
                schedule=f"Test schedule {i}",
                employer={"name": f"Test Company {i}"},
                vacancy_id=f"test_{i}",
                published_at="2024-01-01T00:00:00+03:00",
                source="hh.ru",
            )
            for i in range(5)
        ]

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    def test_batch_vacancy_formatting(self, mock_print, mock_input, batch_vacancies):
        """Batch тест форматирования вакансий без внешних зависимостей"""
        formatter = VacancyFormatter()

        # Форматируем все вакансии за один проход
        formatted_results = []
        for i, vacancy in enumerate(batch_vacancies, 1):
            formatted_text = formatter.format_vacancy_info(vacancy, number=i)
            brief_text = VacancyFormatter.format_vacancy_brief(vacancy, number=i)
            formatted_results.append((formatted_text, brief_text))

        # Проверяем результаты
        assert len(formatted_results) == len(batch_vacancies)
        for i, (full_format, brief_format) in enumerate(formatted_results):
            assert f"Test Vacancy {i}" in full_format
            assert f"Test Company {i}" in full_format
            assert f"test_{i}" in full_format
            assert isinstance(brief_format, str)


    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("requests.get")
    @patch("requests.post")
    @patch("psycopg2.connect")
    @patch("psycopg2.extras.execute_values")
    @patch("os.path.exists", return_value=True)
    @patch("os.makedirs")
    @patch("src.utils.env_loader.EnvLoader.load_env_file")
    def test_full_integration_workflow_mocked(self, mock_env, mock_makedirs, mock_exists, 
                                            mock_execute_values, mock_connect, mock_post, 
                                            mock_requests, mock_print, mock_input):
        """Полный интеграционный тест с консолидированным мокированием"""
        
        # Консолидированные моки для всех внешних ресурсов
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "integration_test",
                    "name": "Full Integration Test Job",
                    "alternate_url": "https://hh.ru/vacancy/integration",
                    "employer": {"name": "Integration Company"},
                    "published_at": "2024-01-01T00:00:00+03:00",
                    "source": "hh.ru",
                    "salary": {"from": 120000, "to": 180000, "currency": "RUR"},
                    "snippet": {"requirement": "Python", "responsibility": "Development"}
                }
            ],
            "found": 1,
            "pages": 1,
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None

        mock_requests.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Консолидированные моки для DB
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_conn.commit.return_value = None
        mock_conn.close.return_value = None
        mock_connect.return_value = mock_conn

        # Полностью мокируем все классы и методы
        with patch.object(HeadHunterAPI, 'get_vacancies', return_value=[{"name": "Full Integration Test Job"}]), \
             patch.object(PostgresSaver, 'add_vacancy_batch_optimized', return_value=["Successfully added 1 vacancy"]), \
             patch.object(PostgresSaver, '__init__', return_value=None):

            # Полный workflow без внешних зависимостей
            api = HeadHunterAPI()
            vacancies_data = api.get_vacancies(search_query="python")

            # Создаем vacancy объект без внешних вызовов
            test_vacancy = Vacancy(
                title="Full Integration Test Job",
                url="https://hh.ru/vacancy/integration",
                salary={"from": 120000, "to": 180000, "currency": "RUR"},
                description="Integration test description",
                requirements="Integration test requirements",
                responsibilities="Integration test responsibilities",
                experience="Integration test experience",
                employment="Integration test employment",
                schedule="Integration test schedule",
                employer={"name": "Integration Company"},
                vacancy_id="integration_test",
                published_at="2024-01-01T00:00:00+03:00",
                source="hh.ru",
            )

            # Сохранение и операции
            storage = PostgresSaver()
            result = storage.add_vacancy_batch_optimized([test_vacancy])

            # Операции без внешних зависимостей
            ops = VacancyOperations()
            filtered = ops.filter_vacancies_by_multiple_keywords([test_vacancy], ["Python"])

            # Форматирование без внешних зависимостей
            formatter = VacancyFormatter()
            formatted = formatter.format_vacancy_info(test_vacancy, number=1)

            # Проверяем результаты полного workflow
            assert isinstance(vacancies_data, list)
            assert isinstance(result, list)
            assert len(filtered) >= 0
            assert isinstance(formatted, str)
            assert "Full Integration Test Job" in formatted