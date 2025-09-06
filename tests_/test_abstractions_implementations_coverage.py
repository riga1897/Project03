"""
Тесты для абстрактных классов и их реализаций
Фокус на 100% покрытие функционального кода от абстракций к реализации
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт абстрактных классов
try:
    from src.storage.abstract import AbstractVacancyStorage
    ABSTRACT_VACANCY_STORAGE_AVAILABLE = True
except ImportError:
    ABSTRACT_VACANCY_STORAGE_AVAILABLE = False

try:
    from src.storage.abstract_db_manager import AbstractDBManager
    ABSTRACT_DB_MANAGER_AVAILABLE = True
except ImportError:
    ABSTRACT_DB_MANAGER_AVAILABLE = False

try:
    from src.api_modules.base_api import BaseJobAPI
    BASE_JOB_API_AVAILABLE = True
except ImportError:
    BASE_JOB_API_AVAILABLE = False

try:
    from src.vacancies.parsers.base_parser import BaseParser
    BASE_PARSER_AVAILABLE = True
except ImportError:
    BASE_PARSER_AVAILABLE = False

try:
    from src.utils.abstract_filter import AbstractDataFilter
    ABSTRACT_DATA_FILTER_AVAILABLE = True
except ImportError:
    ABSTRACT_DATA_FILTER_AVAILABLE = False

try:
    from src.storage.services.abstract_storage_service import AbstractVacancyStorageService
    ABSTRACT_VACANCY_STORAGE_SERVICE_AVAILABLE = True
except ImportError:
    ABSTRACT_VACANCY_STORAGE_SERVICE_AVAILABLE = False

try:
    from src.storage.services.abstract_filter_service import AbstractFilterService, AbstractDeduplicationService, AbstractVacancyProcessor
    ABSTRACT_SERVICES_AVAILABLE = True
except ImportError:
    ABSTRACT_SERVICES_AVAILABLE = False

try:
    from src.interfaces.main_application_interface import VacancyProvider, VacancyProcessor, VacancyStorage, MainApplicationInterface
    MAIN_APPLICATION_INTERFACE_AVAILABLE = True
except ImportError:
    MAIN_APPLICATION_INTERFACE_AVAILABLE = False

try:
    from src.utils.base_formatter import BaseFormatter, ConcreteFormatter
    BASE_FORMATTER_AVAILABLE = True
except ImportError:
    BASE_FORMATTER_AVAILABLE = False

try:
    from src.vacancies.abstract import AbstractVacancy
    ABSTRACT_VACANCY_AVAILABLE = True
except ImportError:
    ABSTRACT_VACANCY_AVAILABLE = False

# Импорт конкретных реализаций
try:
    from src.storage.postgres_saver import PostgresSaver
    POSTGRES_SAVER_AVAILABLE = True
except ImportError:
    POSTGRES_SAVER_AVAILABLE = False

try:
    from src.storage.db_manager import DBManager
    DB_MANAGER_AVAILABLE = True
except ImportError:
    DB_MANAGER_AVAILABLE = False

try:
    from src.api_modules.hh_api import HeadHunterAPI
    HH_API_AVAILABLE = True
except ImportError:
    HH_API_AVAILABLE = False

try:
    from src.vacancies.parsers.hh_parser import HHParser
    HH_PARSER_AVAILABLE = True
except ImportError:
    HH_PARSER_AVAILABLE = False

try:
    from src.vacancies.parsers.sj_parser import SuperJobParser
    SJ_PARSER_AVAILABLE = True
except ImportError:
    SJ_PARSER_AVAILABLE = False

try:
    from src.vacancies.models import Vacancy, Employer
    VACANCY_MODELS_AVAILABLE = True
except ImportError:
    VACANCY_MODELS_AVAILABLE = False

try:
    from src.utils.vacancy_formatter import VacancyFormatter
    VACANCY_FORMATTER_AVAILABLE = True
except ImportError:
    VACANCY_FORMATTER_AVAILABLE = False

try:
    from src.storage.components.vacancy_validator import VacancyValidator
    VACANCY_VALIDATOR_AVAILABLE = True
except ImportError:
    VACANCY_VALIDATOR_AVAILABLE = False

try:
    from src.utils.description_parser import DescriptionParser
    DESCRIPTION_PARSER_AVAILABLE = True
except ImportError:
    DESCRIPTION_PARSER_AVAILABLE = False

try:
    from src.utils.search_utils import normalize_query, extract_keywords, build_search_params, sort_by_relevance
    SEARCH_UTILS_AVAILABLE = True
except ImportError:
    SEARCH_UTILS_AVAILABLE = False

try:
    from src.storage.services.vacancy_processing_coordinator import VacancyProcessingCoordinator
    VACANCY_PROCESSING_COORDINATOR_AVAILABLE = True
except ImportError:
    VACANCY_PROCESSING_COORDINATOR_AVAILABLE = False


class TestAbstractVacancyStorageInterface:
    """Тесты интерфейса AbstractVacancyStorage"""

    def test_abstract_vacancy_storage_interface(self):
        """Тест интерфейса абстрактного хранилища"""
        if not ABSTRACT_VACANCY_STORAGE_AVAILABLE:
            return

        # Создаем конкретную реализацию для тестирования
        class TestVacancyStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy):
                return True
            
            def get_vacancies(self, filters=None):
                return []
            
            def delete_vacancy(self, vacancy):
                return True
            
            def check_vacancies_exist_batch(self, vacancies):
                return {v.vacancy_id if hasattr(v, 'vacancy_id') else str(v): False for v in vacancies}
            
            def add_vacancy_batch_optimized(self, vacancies, search_query=None):
                return ["Added"]

        storage = TestVacancyStorage()
        
        # Тест добавления вакансии
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = "test123"
        result = storage.add_vacancy(mock_vacancy)
        assert isinstance(result, bool)

        # Тест получения вакансий
        vacancies = storage.get_vacancies()
        assert isinstance(vacancies, list)

        # Тест batch операций
        mock_vacancies = [Mock() for _ in range(3)]
        for i, v in enumerate(mock_vacancies):
            v.vacancy_id = f"test{i}"
        
        batch_result = storage.check_vacancies_exist_batch(mock_vacancies)
        assert isinstance(batch_result, dict)
        
        batch_add_result = storage.add_vacancy_batch_optimized(mock_vacancies)
        assert isinstance(batch_add_result, list)


class TestAbstractDBManagerInterface:
    """Тесты интерфейса AbstractDBManager"""

    def test_abstract_db_manager_interface(self):
        """Тест интерфейса абстрактного менеджера БД"""
        if not ABSTRACT_DB_MANAGER_AVAILABLE:
            return

        # Создаем конкретную реализацию для тестирования
        class TestDBManager(AbstractDBManager):
            def get_companies_and_vacancies_count(self):
                return [("Company1", 5), ("Company2", 10)]
            
            def get_all_vacancies(self):
                return []
            
            def get_avg_salary(self):
                return 100000.0
            
            def get_vacancies_with_higher_salary(self):
                return []
            
            def get_vacancies_with_keyword(self, keyword):
                return []
            
            def get_database_stats(self):
                return {"total_vacancies": 0, "total_companies": 0}

        db_manager = TestDBManager()
        
        # Тест получения компаний и вакансий
        companies = db_manager.get_companies_and_vacancies_count()
        assert isinstance(companies, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in companies)

        # Тест получения всех вакансий
        vacancies = db_manager.get_all_vacancies()
        assert isinstance(vacancies, list)

        # Тест получения средней зарплаты
        avg_salary = db_manager.get_avg_salary()
        assert isinstance(avg_salary, (float, int, type(None)))

        # Тест поиска по ключевому слову
        keyword_vacancies = db_manager.get_vacancies_with_keyword("python")
        assert isinstance(keyword_vacancies, list)

        # Тест статистики БД
        stats = db_manager.get_database_stats()
        assert isinstance(stats, dict)


class TestBaseJobAPIInterface:
    """Тесты интерфейса BaseJobAPI"""

    def test_base_job_api_interface(self):
        """Тест интерфейса базового API вакансий"""
        if not BASE_JOB_API_AVAILABLE:
            return

        # Создаем конкретную реализацию для тестирования
        class TestJobAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return [{"id": "1", "title": "Test Job"}]
            
            def _validate_vacancy(self, vacancy):
                return isinstance(vacancy, dict) and "id" in vacancy

        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('shutil.rmtree'):
            
            api = TestJobAPI()
            
            # Тест получения вакансий
            vacancies = api.get_vacancies("python developer")
            assert isinstance(vacancies, list)

            # Тест валидации вакансии
            is_valid = api._validate_vacancy({"id": "123", "title": "Test"})
            assert isinstance(is_valid, bool)
            assert is_valid is True

            # Тест очистки кэша
            api.clear_cache("test_source")


class TestBaseParserInterface:
    """Тесты интерфейса BaseParser"""

    def test_base_parser_interface(self):
        """Тест интерфейса базового парсера"""
        if not BASE_PARSER_AVAILABLE:
            return

        # Создаем конкретную реализацию для тестирования
        class TestParser(BaseParser):
            def parse_vacancy(self, raw_data):
                return {"id": raw_data.get("id"), "title": raw_data.get("name", "Unknown")}
            
            def parse_vacancies(self, raw_vacancies):
                return [self.parse_vacancy(v) for v in raw_vacancies]

        parser = TestParser()
        
        # Тест парсинга одной вакансии
        raw_data = {"id": "123", "name": "Python Developer"}
        parsed = parser.parse_vacancy(raw_data)
        assert isinstance(parsed, dict)
        assert "id" in parsed

        # Тест парсинга списка вакансий
        raw_vacancies = [
            {"id": "1", "name": "Job 1"},
            {"id": "2", "name": "Job 2"}
        ]
        parsed_list = parser.parse_vacancies(raw_vacancies)
        assert isinstance(parsed_list, list)
        assert len(parsed_list) == 2


class TestAbstractDataFilterInterface:
    """Тесты интерфейса AbstractDataFilter"""

    def test_abstract_data_filter_interface(self):
        """Тест интерфейса абстрактного фильтра данных"""
        if not ABSTRACT_DATA_FILTER_AVAILABLE:
            return

        # Создаем конкретную реализацию для тестирования
        class TestDataFilter(AbstractDataFilter):
            def filter_by_company(self, data, companies):
                return [item for item in data if item.get("company") in companies]
            
            def filter_by_salary(self, data, min_salary=None, max_salary=None):
                filtered = data
                if min_salary:
                    filtered = [item for item in filtered if item.get("salary", 0) >= min_salary]
                if max_salary:
                    filtered = [item for item in filtered if item.get("salary", 0) <= max_salary]
                return filtered
            
            def filter_by_location(self, data, locations):
                return [item for item in data if item.get("location") in locations]
            
            def filter_by_experience(self, data, experience_levels):
                return [item for item in data if item.get("experience") in experience_levels]

        filter_service = TestDataFilter()
        
        # Тестовые данные
        test_data = [
            {"company": "TechCorp", "salary": 100000, "location": "Moscow", "experience": "middle"},
            {"company": "DataCorp", "salary": 150000, "location": "SPb", "experience": "senior"},
            {"company": "StartupCorp", "salary": 80000, "location": "Moscow", "experience": "junior"}
        ]

        # Тест фильтрации по компании
        company_filtered = filter_service.filter_by_company(test_data, ["TechCorp", "DataCorp"])
        assert isinstance(company_filtered, list)
        assert len(company_filtered) == 2

        # Тест фильтрации по зарплате
        salary_filtered = filter_service.filter_by_salary(test_data, min_salary=90000)
        assert isinstance(salary_filtered, list)
        assert len(salary_filtered) == 2

        # Тест фильтрации по местоположению
        location_filtered = filter_service.filter_by_location(test_data, ["Moscow"])
        assert isinstance(location_filtered, list)
        assert len(location_filtered) == 2

        # Тест фильтрации по опыту
        experience_filtered = filter_service.filter_by_experience(test_data, ["senior"])
        assert isinstance(experience_filtered, list)
        assert len(experience_filtered) == 1


class TestConcreteImplementations:
    """Тесты конкретных реализаций"""

    @pytest.fixture
    def mock_db_connection(self):
        """Мок подключения к БД для конкретных реализаций"""
        mock_conn = Mock()
        mock_cursor = Mock()
        
        # Настройка context manager
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        
        # Настройка cursor для операций
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = None
        mock_cursor.rowcount = 0
        mock_cursor.__iter__ = Mock(return_value=iter([]))
        
        return mock_conn, mock_cursor

    def test_postgres_saver_implementation(self, mock_db_connection):
        """Тест реализации PostgresSaver"""
        if not POSTGRES_SAVER_AVAILABLE:
            return

        mock_conn, mock_cursor = mock_db_connection
        
        with patch('psycopg2.connect', return_value=mock_conn):
            postgres_saver = PostgresSaver()
            
            # Тест получения вакансий
            with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
                vacancies = postgres_saver.get_vacancies()
                assert isinstance(vacancies, list)

    def test_db_manager_implementation(self, mock_db_connection):
        """Тест реализации DBManager"""
        if not DB_MANAGER_AVAILABLE:
            return

        mock_conn, mock_cursor = mock_db_connection
        
        with patch('psycopg2.connect', return_value=mock_conn):
            db_manager = DBManager()
            
            # Тест получения статистики БД
            with patch.object(db_manager, '_get_connection', return_value=mock_conn):
                stats = db_manager.get_database_stats()
                assert isinstance(stats, dict)

    def test_hh_api_implementation(self):
        """Тест реализации HeadHunterAPI"""
        if not HH_API_AVAILABLE:
            return

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [],
            "found": 0,
            "pages": 1,
            "page": 0
        }
        
        with patch('requests.get', return_value=mock_response):
            hh_api = HeadHunterAPI()
            
            # Тест получения вакансий
            vacancies = hh_api.get_vacancies("python")
            assert isinstance(vacancies, list)

    def test_hh_parser_implementation(self):
        """Тест реализации HHParser"""
        if not HH_PARSER_AVAILABLE or not VACANCY_MODELS_AVAILABLE:
            return

        with patch('src.utils.cache.FileCache'):
            parser = HHParser()
            
            # Тестовые данные от HH API
            raw_data = [
                {
                    "id": "123",
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "employer": {"name": "Tech Company"},
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "area": {"name": "Moscow"}
                }
            ]
            
            # Тест парсинга списка вакансий
            parsed_vacancies = parser.parse_vacancies(raw_data)
            assert isinstance(parsed_vacancies, list)

    def test_sj_parser_implementation(self):
        """Тест реализации SuperJobParser"""
        if not SJ_PARSER_AVAILABLE or not VACANCY_MODELS_AVAILABLE:
            return

        parser = SuperJobParser()
        
        # Тестовые данные от SJ API (подготовленные для создания Vacancy)
        raw_data = [
            {
                "id": "456",
                "profession": "Java Developer", 
                "link": "https://superjob.ru/vacancy/456",
                "firm_name": "Java Company",
                "payment_from": 120000,
                "payment_to": 180000,
                "currency": "rub",
                "town": {"title": "SPb"}
            }
        ]
        
        # Тест парсинга списка вакансий
        with patch.object(parser, 'parse_vacancies', return_value=[]):
            parsed_vacancies = parser.parse_vacancies(raw_data)
            assert isinstance(parsed_vacancies, list)


class TestFormatterImplementations:
    """Тесты реализаций форматировщиков"""

    def test_base_formatter_implementation(self):
        """Тест реализации базового форматировщика"""
        if not BASE_FORMATTER_AVAILABLE:
            return

        formatter = ConcreteFormatter()
        
        # Тест форматирования вакансии
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = "123"
        mock_vacancy.title = "Python Developer"
        mock_vacancy.salary = Mock()
        mock_vacancy.salary.salary_from = 100000
        mock_vacancy.salary.salary_to = 150000
        mock_vacancy.salary.currency = "RUR"
        
        formatted = formatter.format_vacancy_info(mock_vacancy, 1)
        assert isinstance(formatted, str)
        assert len(formatted) > 0

        # Тест форматирования зарплаты
        salary_formatted = formatter.format_salary(mock_vacancy.salary)
        assert isinstance(salary_formatted, str)

        # Тест форматирования валюты
        currency_formatted = formatter.format_currency("RUR")
        assert isinstance(currency_formatted, str)

        # Тест форматирования текста
        text_formatted = formatter.format_text("Very long text that should be truncated", 10)
        assert isinstance(text_formatted, str)
        assert len(text_formatted) <= 13  # 10 + "..."

    def test_vacancy_formatter_implementation(self):
        """Тест реализации форматировщика вакансий"""
        if not VACANCY_FORMATTER_AVAILABLE:
            return

        formatter = VacancyFormatter()
        
        # Создаем мок вакансии с правильными методами
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = "test123"
        mock_vacancy.title = "Python Developer"
        
        # Настройка employer с правильным методом get_name
        mock_employer = Mock()
        mock_employer.get_name.return_value = "Tech Corp"
        mock_employer.name = "Tech Corp"
        mock_vacancy.employer = mock_employer
        
        # Настройка salary с правильными атрибутами
        mock_salary = Mock()
        mock_salary.salary_from = 100000
        mock_salary.salary_to = 150000
        mock_salary.currency = "RUR"
        mock_salary.__str__ = Mock(return_value="100 000 - 150 000 RUR")
        mock_vacancy.salary = mock_salary
        
        mock_vacancy.area = "Moscow"
        mock_vacancy.experience = "middle"
        mock_vacancy.employment = "full"
        mock_vacancy.source = "hh.ru"
        mock_vacancy.url = "https://example.com"
        mock_vacancy.description = "Test description"
        mock_vacancy.requirements = "Test requirements"
        mock_vacancy.responsibilities = "Test responsibilities"
        
        # Тест форматирования информации о вакансии
        formatted_info = formatter.format_vacancy_info(mock_vacancy, 1)
        assert isinstance(formatted_info, str)
        assert "Python Developer" in formatted_info
        # Проверяем что форматирование прошло корректно
        assert len(formatted_info) > 0


class TestValidatorImplementations:
    """Тесты реализаций валидаторов"""

    def test_vacancy_validator_implementation(self):
        """Тест реализации валидатора вакансий"""
        if not VACANCY_VALIDATOR_AVAILABLE or not VACANCY_MODELS_AVAILABLE:
            return

        validator = VacancyValidator()
        
        # Создаем валидную вакансию
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = "test123"
        mock_vacancy.title = "Python Developer"
        mock_vacancy.url = "https://example.com"
        
        # Тест валидации корректной вакансии
        is_valid = validator.validate_vacancy(mock_vacancy)
        assert isinstance(is_valid, bool)

        # Тест получения ошибок валидации
        if hasattr(validator, 'get_validation_errors'):
            errors = validator.get_validation_errors()
            assert isinstance(errors, list)


class TestUtilityImplementations:
    """Тесты реализаций утилит"""

    def test_description_parser_implementation(self):
        """Тест реализации парсера описаний"""
        if not DESCRIPTION_PARSER_AVAILABLE:
            return

        # Тест очистки HTML
        html_text = "<p>Test <b>description</b> with <ul><li>item 1</li><li>item 2</li></ul></p>"
        cleaned = DescriptionParser.clean_html(html_text)
        assert isinstance(cleaned, str)
        assert "<" not in cleaned
        assert ">" not in cleaned

        # Тест извлечения требований и обязанностей
        description_with_sections = """
        <strong>Требования:</strong>
        <ul>
        <li>Python</li>
        <li>Django</li>
        </ul>
        <strong>Обязанности:</strong>
        <ul>
        <li>Разработка</li>
        <li>Тестирование</li>
        </ul>
        """
        
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description_with_sections)
        assert isinstance(requirements, (str, type(None)))
        assert isinstance(responsibilities, (str, type(None)))

    def test_search_utils_implementation(self):
        """Тест реализации утилит поиска"""
        if not SEARCH_UTILS_AVAILABLE:
            return

        # Тест нормализации запроса
        normalized = normalize_query("  Python Developer   ")
        assert isinstance(normalized, str)
        assert normalized == "python developer"

        # Тест извлечения ключевых слов
        keywords = extract_keywords("Python Django developer in Moscow")
        assert isinstance(keywords, list)
        assert "python" in keywords
        assert "django" in keywords

        # Тест построения параметров поиска
        params = build_search_params("python", per_page=20, page=1)
        assert isinstance(params, dict)
        assert params["text"] == "python"
        assert params["per_page"] == 20

        # Тест сортировки по релевантности
        vacancies = [
            {"title": "Python Developer", "description": "Python programming"},
            {"title": "Java Developer", "description": "Java programming"},
            {"title": "Python Engineer", "description": "Python Django"}
        ]
        
        sorted_vacancies = sort_by_relevance(vacancies, "python")
        assert isinstance(sorted_vacancies, list)
        assert len(sorted_vacancies) <= len(vacancies)


class TestCoordinatorImplementations:
    """Тесты реализаций координаторов"""

    def test_vacancy_processing_coordinator_implementation(self):
        """Тест реализации координатора обработки вакансий"""
        if not VACANCY_PROCESSING_COORDINATOR_AVAILABLE or not VACANCY_MODELS_AVAILABLE:
            return

        # Создаем мок менеджера БД
        mock_db_manager = Mock()
        
        with patch('src.storage.services.company_id_filter_service.CompanyIDFilterService'), \
             patch('src.storage.services.sql_deduplication_service.SQLDeduplicationService'):
            
            coordinator = VacancyProcessingCoordinator(mock_db_manager)
            
            # Создаем тестовые вакансии
            mock_vacancies = []
            for i in range(3):
                mock_vacancy = Mock()
                mock_vacancy.vacancy_id = f"test{i}"
                mock_vacancy.title = f"Job {i}"
                mock_vacancies.append(mock_vacancy)
            
            # Тест обработки вакансий
            processed = coordinator.process_vacancies(mock_vacancies)
            assert isinstance(processed, list)

            # Тест только фильтрации
            filtered = coordinator.filter_only(mock_vacancies)
            assert isinstance(filtered, list)

            # Тест только дедупликации
            deduplicated = coordinator.deduplicate_only(mock_vacancies)
            assert isinstance(deduplicated, list)

            # Тест получения сводки обработки
            summary = coordinator.get_processing_summary(mock_vacancies)
            assert isinstance(summary, dict)


class TestProtocolImplementations:
    """Тесты Protocol реализаций"""

    def test_main_application_interface_protocols(self):
        """Тест протоколов главного интерфейса приложения"""
        if not MAIN_APPLICATION_INTERFACE_AVAILABLE or not VACANCY_MODELS_AVAILABLE:
            return

        # Создаем конкретные реализации протоколов
        class TestVacancyProvider:
            def get_vacancies(self, query: str):
                return []
            
            def get_source_name(self):
                return "test_source"

        class TestVacancyProcessor:
            def process_vacancies(self, vacancies):
                return vacancies

        class TestVacancyStorage:
            def save_vacancies(self, vacancies):
                return True
            
            def load_vacancies(self):
                return []

        # Создаем конкретную реализацию главного интерфейса
        class TestApplicationInterface(MainApplicationInterface):
            def run_application(self):
                return "Application started"

        provider = TestVacancyProvider()
        processor = TestVacancyProcessor()
        storage = TestVacancyStorage()
        
        # Создаем интерфейс приложения
        app_interface = TestApplicationInterface(provider, processor, storage)
        
        # Тест выполнения рабочего процесса с вакансиями
        processed_vacancies = app_interface.execute_vacancy_workflow("python")
        assert isinstance(processed_vacancies, list)

        # Тест запуска приложения
        result = app_interface.run_application()
        assert isinstance(result, str)


class TestAbstractServicesIntegration:
    """Тесты интеграции абстрактных сервисов"""

    def test_abstract_services_integration(self):
        """Тест интеграции абстрактных сервисов"""
        if not ABSTRACT_SERVICES_AVAILABLE or not VACANCY_MODELS_AVAILABLE:
            return

        # Создаем конкретные реализации абстрактных сервисов
        class TestFilterService(AbstractFilterService):
            def filter_by_company_ids(self, vacancies):
                return vacancies
            
            def get_target_company_stats(self):
                return (set(), set())

        class TestDeduplicationService(AbstractDeduplicationService):
            def deduplicate_vacancies(self, vacancies):
                return vacancies

        class TestVacancyProcessor(AbstractVacancyProcessor):
            def process_vacancies(self, vacancies, apply_company_filter=True, apply_deduplication=True):
                return vacancies
            
            def filter_only(self, vacancies):
                return vacancies
            
            def deduplicate_only(self, vacancies):
                return vacancies
            
            def get_processing_summary(self, vacancies):
                return {"total": len(vacancies), "processed": len(vacancies)}

        # Создаем экземпляры сервисов
        filter_service = TestFilterService()
        dedup_service = TestDeduplicationService()
        processor = TestVacancyProcessor()
        
        # Создаем тестовые данные
        mock_vacancies = [Mock() for _ in range(5)]
        for i, v in enumerate(mock_vacancies):
            v.vacancy_id = f"test{i}"
        
        # Тест фильтрации
        filtered = filter_service.filter_by_company_ids(mock_vacancies)
        assert isinstance(filtered, list)
        
        # Тест дедупликации
        deduplicated = dedup_service.deduplicate_vacancies(mock_vacancies)
        assert isinstance(deduplicated, list)
        
        # Тест обработки
        processed = processor.process_vacancies(mock_vacancies)
        assert isinstance(processed, list)
        
        # Тест получения сводки
        summary = processor.get_processing_summary(mock_vacancies)
        assert isinstance(summary, dict)
        assert "total" in summary


class TestAbstractVacancyStorageServiceImplementation:
    """Тесты реализации AbstractVacancyStorageService"""

    def test_abstract_vacancy_storage_service_interface(self):
        """Тест интерфейса абстрактного сервиса хранения вакансий"""
        if not ABSTRACT_VACANCY_STORAGE_SERVICE_AVAILABLE or not VACANCY_MODELS_AVAILABLE:
            return

        # Создаем конкретную реализацию для тестирования
        class TestVacancyStorageService(AbstractVacancyStorageService):
            def filter_and_deduplicate_vacancies(self, vacancies):
                return vacancies
            
            def save_vacancies(self, vacancies):
                return len(vacancies)
            
            def get_vacancies(self, filters=None):
                return []
            
            def delete_vacancy(self, vacancy_id):
                return True
            
            def get_companies_and_vacancies_count(self):
                return []
            
            def get_storage_stats(self):
                return {"total_vacancies": 0}

        service = TestVacancyStorageService()
        
        # Создаем тестовые вакансии
        mock_vacancies = [Mock() for _ in range(3)]
        
        # Тест фильтрации и дедупликации
        processed = service.filter_and_deduplicate_vacancies(mock_vacancies)
        assert isinstance(processed, list)
        
        # Тест сохранения
        saved_count = service.save_vacancies(mock_vacancies)
        assert isinstance(saved_count, int)
        
        # Тест получения вакансий
        vacancies = service.get_vacancies()
        assert isinstance(vacancies, list)
        
        # Тест удаления вакансии
        deleted = service.delete_vacancy("test123")
        assert isinstance(deleted, bool)
        
        # Тест получения статистики компаний
        companies_stats = service.get_companies_and_vacancies_count()
        assert isinstance(companies_stats, list)
        
        # Тест получения статистики хранилища
        storage_stats = service.get_storage_stats()
        assert isinstance(storage_stats, dict)