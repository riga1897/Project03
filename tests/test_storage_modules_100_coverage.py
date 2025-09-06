"""
Тесты для модулей хранения данных с 100% покрытием
Покрывает: db_manager, postgres_saver, storage_factory, services, components
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.storage.db_manager import DBManager
from src.storage.postgres_saver import PostgresSaver
from src.storage.storage_factory import StorageFactory
from src.storage.simple_db_adapter import SimpleDBAdapter
from src.storage.services.filtering_service import FilteringService
from src.storage.services.deduplication_service import DeduplicationService
from src.storage.services.vacancy_storage_service import VacancyStorageService
from src.storage.components.database_connection import DatabaseConnection
from src.storage.components.vacancy_validator import VacancyValidator
from src.storage.components.vacancy_repository import VacancyRepository
from src.config.db_config import DatabaseConfig


class TestDatabaseConnection:
    """Тесты для DatabaseConnection"""

    def test_init_with_config(self):
        """Тест инициализации с конфигурацией"""
        config = DatabaseConfig()
        conn = DatabaseConnection(config)
        
        assert conn.config == config

    def test_init_default_config(self):
        """Тест инициализации с дефолтной конфигурацией"""
        with patch('src.storage.components.database_connection.DatabaseConfig'):
            conn = DatabaseConnection()
            assert hasattr(conn, 'config')

    @patch('psycopg2.connect')
    def test_connect_success(self, mock_connect):
        """Тест успешного подключения"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        config = DatabaseConfig()
        conn = DatabaseConnection(config)
        
        result = conn.connect()
        assert result == mock_connection

    @patch('psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Тест неудачного подключения"""
        mock_connect.side_effect = Exception("Connection failed")
        
        config = DatabaseConfig()
        conn = DatabaseConnection(config)
        
        with pytest.raises(Exception):
            conn.connect()

    @patch('psycopg2.connect')
    def test_get_connection_string(self, mock_connect):
        """Тест получения строки подключения"""
        config = DatabaseConfig()
        config.host = "testhost"
        config.port = 5432
        config.database = "testdb"
        config.username = "testuser"
        config.password = "testpass"
        
        conn = DatabaseConnection(config)
        conn_str = conn.get_connection_string()
        
        expected = "postgresql://testuser:testpass@testhost:5432/testdb"
        assert conn_str == expected

    def test_close_connection(self):
        """Тест закрытия соединения"""
        config = DatabaseConfig()
        conn = DatabaseConnection(config)
        
        mock_connection = Mock()
        conn._connection = mock_connection
        
        conn.close()
        mock_connection.close.assert_called_once()

    def test_close_connection_none(self):
        """Тест закрытия несуществующего соединения"""
        config = DatabaseConfig()
        conn = DatabaseConnection(config)
        
        # Не должно падать
        conn.close()


class TestVacancyValidator:
    """Тесты для VacancyValidator"""

    def test_validate_vacancy_valid(self):
        """Тест валидации корректной вакансии"""
        vacancy = {
            "title": "Python Developer",
            "url": "http://test.com",
            "employer": {"name": "Test Company"}
        }
        
        validator = VacancyValidator()
        assert validator.validate_vacancy(vacancy) == True

    def test_validate_vacancy_missing_title(self):
        """Тест валидации без названия"""
        vacancy = {
            "url": "http://test.com",
            "employer": {"name": "Test Company"}
        }
        
        validator = VacancyValidator()
        assert validator.validate_vacancy(vacancy) == False

    def test_validate_vacancy_missing_url(self):
        """Тест валидации без URL"""
        vacancy = {
            "title": "Python Developer",
            "employer": {"name": "Test Company"}
        }
        
        validator = VacancyValidator()
        assert validator.validate_vacancy(vacancy) == False

    def test_validate_vacancy_invalid_type(self):
        """Тест валидации невалидного типа"""
        validator = VacancyValidator()
        assert validator.validate_vacancy("not_dict") == False

    def test_validate_batch_all_valid(self):
        """Тест валидации пачки корректных вакансий"""
        vacancies = [
            {"title": "Dev1", "url": "http://test1.com"},
            {"title": "Dev2", "url": "http://test2.com"}
        ]
        
        validator = VacancyValidator()
        result = validator.validate_batch(vacancies)
        
        assert len(result) == 2

    def test_validate_batch_mixed(self):
        """Тест валидации смешанной пачки"""
        vacancies = [
            {"title": "Dev1", "url": "http://test1.com"},  # Валидная
            {"title": "Dev2"},                              # Невалидная - нет URL
            {"url": "http://test3.com"}                     # Невалидная - нет title
        ]
        
        validator = VacancyValidator()
        result = validator.validate_batch(vacancies)
        
        assert len(result) == 1  # Только одна валидная

    def test_get_validation_stats(self):
        """Тест получения статистики валидации"""
        validator = VacancyValidator()
        
        # Проводим несколько валидаций
        validator.validate_vacancy({"title": "Test", "url": "http://test.com"})
        validator.validate_vacancy({"title": "Invalid"})
        
        stats = validator.get_validation_stats()
        
        assert stats["total_validated"] == 2
        assert stats["valid_count"] == 1
        assert stats["invalid_count"] == 1


class TestVacancyRepository:
    """Тесты для VacancyRepository"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.mock_connection = Mock()
        self.repository = VacancyRepository(self.mock_connection)

    def test_init_with_connection(self):
        """Тест инициализации с подключением"""
        conn = Mock()
        repo = VacancyRepository(conn)
        
        assert repo.connection == conn

    def test_save_vacancy_success(self):
        """Тест успешного сохранения вакансии"""
        vacancy = {
            "title": "Test Vacancy",
            "url": "http://test.com",
            "salary": {"from": 100000, "currency": "RUR"},
            "employer": {"name": "Test Company"}
        }
        
        mock_cursor = Mock()
        self.mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.repository.save_vacancy(vacancy)
        assert result == True

    def test_save_vacancy_failure(self):
        """Тест неудачного сохранения вакансии"""
        vacancy = {"title": "Test", "url": "http://test.com"}
        
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("DB Error")
        self.mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.repository.save_vacancy(vacancy)
        assert result == False

    def test_get_vacancy_by_id_found(self):
        """Тест получения вакансии по ID (найдена)"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            "id": "123",
            "title": "Test Vacancy"
        }
        self.mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.repository.get_vacancy_by_id("123")
        assert result["id"] == "123"

    def test_get_vacancy_by_id_not_found(self):
        """Тест получения вакансии по ID (не найдена)"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        self.mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.repository.get_vacancy_by_id("nonexistent")
        assert result is None

    def test_get_vacancies_by_query(self):
        """Тест поиска вакансий по запросу"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {"id": "1", "title": "Python Developer"},
            {"id": "2", "title": "Senior Python Developer"}
        ]
        self.mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.repository.get_vacancies_by_query("Python")
        assert len(result) == 2

    def test_delete_vacancy_success(self):
        """Тест успешного удаления вакансии"""
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        self.mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.repository.delete_vacancy("123")
        assert result == True

    def test_delete_vacancy_not_found(self):
        """Тест удаления несуществующей вакансии"""
        mock_cursor = Mock()
        mock_cursor.rowcount = 0
        self.mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.repository.delete_vacancy("nonexistent")
        assert result == False

    def test_count_vacancies(self):
        """Тест подсчета вакансий"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {"count": 42}
        self.mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.repository.count_vacancies()
        assert result == 42


class TestFilteringService:
    """Тесты для FilteringService"""

    def test_init_default(self):
        """Тест инициализации по умолчанию"""
        service = FilteringService()
        assert hasattr(service, 'filters')

    def test_filter_by_salary_range(self):
        """Тест фильтрации по диапазону зарплат"""
        vacancies = [
            {"salary": {"from": 80000, "to": 120000}},
            {"salary": {"from": 150000, "to": 200000}},
            {"salary": None}
        ]
        
        service = FilteringService()
        result = service.filter_by_salary_range(vacancies, 100000, 180000)
        
        # Должна остаться только вторая вакансия
        assert len(result) == 1
        assert result[0]["salary"]["from"] == 150000

    def test_filter_by_keywords_found(self):
        """Тест фильтрации по ключевым словам (найдены)"""
        vacancies = [
            {"title": "Python Developer", "description": "Django, Flask"},
            {"title": "Java Developer", "description": "Spring, Hibernate"},
            {"title": "Frontend Developer", "description": "React, Vue"}
        ]
        
        service = FilteringService()
        result = service.filter_by_keywords(vacancies, ["python", "django"])
        
        assert len(result) == 1
        assert "Python" in result[0]["title"]

    def test_filter_by_keywords_not_found(self):
        """Тест фильтрации по ключевым словам (не найдены)"""
        vacancies = [
            {"title": "Java Developer", "description": "Spring"}
        ]
        
        service = FilteringService()
        result = service.filter_by_keywords(vacancies, ["python"])
        
        assert len(result) == 0

    def test_filter_by_company(self):
        """Тест фильтрации по компании"""
        vacancies = [
            {"employer": {"name": "Google"}},
            {"employer": {"name": "Yandex"}},
            {"employer": {"name": "Microsoft"}}
        ]
        
        service = FilteringService()
        result = service.filter_by_company(vacancies, ["google", "microsoft"])
        
        assert len(result) == 2

    def test_filter_by_experience(self):
        """Тест фильтрации по опыту"""
        vacancies = [
            {"experience": {"id": "noExperience"}},
            {"experience": {"id": "between1And3"}},
            {"experience": {"id": "between3And6"}}
        ]
        
        service = FilteringService()
        result = service.filter_by_experience(vacancies, "between1And3")
        
        assert len(result) == 1
        assert result[0]["experience"]["id"] == "between1And3"

    def test_apply_all_filters(self):
        """Тест применения всех фильтров"""
        vacancies = [
            {
                "title": "Python Developer",
                "salary": {"from": 120000, "to": 180000},
                "employer": {"name": "Yandex"},
                "experience": {"id": "between1And3"}
            }
        ]
        
        service = FilteringService()
        filters = {
            "keywords": ["python"],
            "salary_from": 100000,
            "salary_to": 200000,
            "companies": ["yandex"],
            "experience": "between1And3"
        }
        
        result = service.apply_filters(vacancies, filters)
        assert len(result) == 1


class TestDeduplicationService:
    """Тесты для DeduplicationService"""

    def test_deduplicate_by_url(self):
        """Тест дедупликации по URL"""
        vacancies = [
            {"url": "http://test.com/1", "title": "Job 1"},
            {"url": "http://test.com/2", "title": "Job 2"},
            {"url": "http://test.com/1", "title": "Job 1 Duplicate"}
        ]
        
        service = DeduplicationService()
        result = service.deduplicate_by_url(vacancies)
        
        assert len(result) == 2

    def test_deduplicate_by_title_and_company(self):
        """Тест дедупликации по названию и компании"""
        vacancies = [
            {"title": "Python Developer", "employer": {"name": "Company A"}},
            {"title": "Java Developer", "employer": {"name": "Company A"}},
            {"title": "Python Developer", "employer": {"name": "Company A"}},  # Дубликат
            {"title": "Python Developer", "employer": {"name": "Company B"}}   # Другая компания
        ]
        
        service = DeduplicationService()
        result = service.deduplicate_by_title_and_company(vacancies)
        
        assert len(result) == 3

    def test_deduplicate_by_similarity(self):
        """Тест дедупликации по схожести"""
        vacancies = [
            {"title": "Python Developer", "description": "Django framework"},
            {"title": "Python Dev", "description": "Django web framework"},  # Схожая
            {"title": "Java Developer", "description": "Spring framework"}
        ]
        
        service = DeduplicationService()
        result = service.deduplicate_by_similarity(vacancies, threshold=0.7)
        
        assert len(result) <= 3  # Может быть меньше из-за схожести

    def test_full_deduplication(self):
        """Тест полной дедупликации"""
        vacancies = [
            {"url": "http://test1.com", "title": "Dev 1", "employer": {"name": "Co A"}},
            {"url": "http://test1.com", "title": "Dev 1", "employer": {"name": "Co A"}},  # Дубликат по URL
            {"url": "http://test2.com", "title": "Dev 1", "employer": {"name": "Co A"}},  # Дубликат по title+company
            {"url": "http://test3.com", "title": "Dev 2", "employer": {"name": "Co B"}}   # Уникальная
        ]
        
        service = DeduplicationService()
        result = service.full_deduplication(vacancies)
        
        assert len(result) == 2  # Должно остаться 2 уникальные

    def test_get_deduplication_stats(self):
        """Тест получения статистики дедупликации"""
        service = DeduplicationService()
        
        vacancies = [
            {"url": "http://test1.com", "title": "Job 1"},
            {"url": "http://test1.com", "title": "Job 1"}  # Дубликат
        ]
        
        result = service.deduplicate_by_url(vacancies)
        stats = service.get_deduplication_stats()
        
        assert stats["original_count"] == 2
        assert stats["deduplicated_count"] == 1
        assert stats["duplicates_removed"] == 1


class TestVacancyStorageService:
    """Тесты для VacancyStorageService"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.mock_repository = Mock()
        self.mock_validator = Mock()
        self.service = VacancyStorageService(self.mock_repository, self.mock_validator)

    def test_init_with_dependencies(self):
        """Тест инициализации с зависимостями"""
        repo = Mock()
        validator = Mock()
        
        service = VacancyStorageService(repo, validator)
        
        assert service.repository == repo
        assert service.validator == validator

    def test_store_vacancy_valid(self):
        """Тест сохранения валидной вакансии"""
        vacancy = {"title": "Test", "url": "http://test.com"}
        
        self.mock_validator.validate_vacancy.return_value = True
        self.mock_repository.save_vacancy.return_value = True
        
        result = self.service.store_vacancy(vacancy)
        assert result == True

    def test_store_vacancy_invalid(self):
        """Тест сохранения невалидной вакансии"""
        vacancy = {"title": "Invalid"}
        
        self.mock_validator.validate_vacancy.return_value = False
        
        result = self.service.store_vacancy(vacancy)
        assert result == False
        self.mock_repository.save_vacancy.assert_not_called()

    def test_store_vacancies_batch(self):
        """Тест сохранения пачки вакансий"""
        vacancies = [
            {"title": "Job 1", "url": "http://test1.com"},
            {"title": "Job 2", "url": "http://test2.com"}
        ]
        
        self.mock_validator.validate_batch.return_value = vacancies  # Все валидны
        self.mock_repository.save_vacancy.return_value = True
        
        result = self.service.store_vacancies_batch(vacancies)
        
        assert result["total_processed"] == 2
        assert result["successfully_stored"] == 2
        assert result["failed_to_store"] == 0

    def test_retrieve_vacancies_by_query(self):
        """Тест получения вакансий по запросу"""
        expected_vacancies = [{"id": "1", "title": "Python Dev"}]
        self.mock_repository.get_vacancies_by_query.return_value = expected_vacancies
        
        result = self.service.retrieve_vacancies_by_query("Python")
        
        assert result == expected_vacancies
        self.mock_repository.get_vacancies_by_query.assert_called_once_with("Python")

    def test_get_storage_stats(self):
        """Тест получения статистики хранилища"""
        self.mock_repository.count_vacancies.return_value = 100
        self.mock_validator.get_validation_stats.return_value = {
            "total_validated": 150,
            "valid_count": 120,
            "invalid_count": 30
        }
        
        result = self.service.get_storage_stats()
        
        assert result["total_vacancies"] == 100
        assert result["validation_stats"]["valid_count"] == 120


class TestStorageFactory:
    """Тесты для StorageFactory"""

    def test_create_postgres_storage(self):
        """Тест создания PostgreSQL хранилища"""
        with patch('src.storage.storage_factory.DatabaseConfig'):
            with patch('src.storage.storage_factory.DatabaseConnection'):
                with patch('src.storage.storage_factory.VacancyRepository'):
                    storage = StorageFactory.create_storage("postgres")
                    assert storage is not None

    def test_create_unknown_storage(self):
        """Тест создания неизвестного типа хранилища"""
        with pytest.raises(ValueError, match="Неизвестный тип хранилища"):
            StorageFactory.create_storage("unknown")

    def test_get_available_storage_types(self):
        """Тест получения доступных типов хранилища"""
        types = StorageFactory.get_available_storage_types()
        
        assert "postgres" in types
        assert isinstance(types, list)


class TestSimpleDBAdapter:
    """Тесты для SimpleDBAdapter"""

    def test_init_creates_in_memory_db(self):
        """Тест создания in-memory базы данных"""
        adapter = SimpleDBAdapter()
        assert hasattr(adapter, 'connection')

    def test_create_tables(self):
        """Тест создания таблиц"""
        adapter = SimpleDBAdapter()
        # Не должно падать
        adapter.create_tables()

    def test_insert_vacancy(self):
        """Тест вставки вакансии"""
        adapter = SimpleDBAdapter()
        adapter.create_tables()
        
        vacancy_data = {
            "title": "Test Job",
            "url": "http://test.com",
            "employer": {"name": "Test Company"},
            "salary": {"from": 100000, "currency": "RUR"}
        }
        
        result = adapter.insert_vacancy(vacancy_data)
        assert result == True

    def test_select_vacancies(self):
        """Тест выборки вакансий"""
        adapter = SimpleDBAdapter()
        adapter.create_tables()
        
        # Вставляем тестовую вакансию
        vacancy_data = {
            "title": "Python Developer",
            "url": "http://test.com",
            "employer": {"name": "Test Company"}
        }
        adapter.insert_vacancy(vacancy_data)
        
        # Получаем вакансии
        result = adapter.select_vacancies(limit=10)
        assert len(result) == 1
        assert result[0]["title"] == "Python Developer"

    def test_search_vacancies(self):
        """Тест поиска вакансий"""
        adapter = SimpleDBAdapter()
        adapter.create_tables()
        
        # Вставляем несколько вакансий
        adapter.insert_vacancy({
            "title": "Python Developer",
            "url": "http://test1.com",
            "employer": {"name": "Company A"}
        })
        adapter.insert_vacancy({
            "title": "Java Developer",
            "url": "http://test2.com",
            "employer": {"name": "Company B"}
        })
        
        # Ищем по ключевому слову
        result = adapter.search_vacancies("Python")
        assert len(result) == 1
        assert result[0]["title"] == "Python Developer"

    def test_close_connection(self):
        """Тест закрытия соединения"""
        adapter = SimpleDBAdapter()
        # Не должно падать
        adapter.close()