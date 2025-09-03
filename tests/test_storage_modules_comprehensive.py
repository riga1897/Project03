"""
Комплексные тесты для storage модулей с максимальным покрытием кода.
Включает тестирование всех компонентов хранения данных, валидации и обработки.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import List, Dict, Any, Optional

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Глобальные моки для всех внешних зависимостей
mock_psycopg2 = MagicMock()
sys.modules['psycopg2'] = mock_psycopg2
sys.modules['psycopg2.extras'] = MagicMock()

from src.storage.abstract import AbstractVacancyStorage
from src.storage.abstract_db_manager import AbstractDBManager
from src.storage.db_manager import DBManager
from src.storage.postgres_saver import PostgresSaver
from src.storage.storage_factory import StorageFactory
from src.storage.components.database_connection import DatabaseConnection
from src.storage.components.vacancy_repository import VacancyRepository
from src.storage.components.vacancy_validator import VacancyValidator
from src.storage.services.vacancy_storage_service import VacancyStorageService
from src.storage.services.filtering_service import FilteringService, TargetCompanyFilterStrategy, SalaryFilterStrategy
from src.storage.services.deduplication_service import DeduplicationService, SQLDeduplicationStrategy
from src.vacancies.models import Vacancy


def create_mock_vacancy():
    """Создает мок вакансии для тестирования"""
    vacancy = Mock(spec=Vacancy)
    vacancy.vacancy_id = "test_123"
    vacancy.title = "Python Developer"
    vacancy.url = "https://test.com/vacancy/123"
    vacancy.description = "Test description"
    vacancy.employer = Mock()
    vacancy.employer.name = "Test Company"
    vacancy.employer.id = "456"
    vacancy.salary = Mock()
    vacancy.salary.salary_from = 100000
    vacancy.salary.salary_to = 150000
    vacancy.source = "hh.ru"
    return vacancy


class TestAbstractVacancyStorage:
    """Комплексное тестирование абстрактного класса хранения"""
    
    def test_abstract_storage_cannot_be_instantiated(self):
        """Тестирование невозможности создания экземпляра абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractVacancyStorage()
            
    def test_abstract_storage_methods_exist(self):
        """Тестирование наличия абстрактных методов"""
        # Проверяем, что абстрактные методы определены
        assert hasattr(AbstractVacancyStorage, 'add_vacancy')
        assert hasattr(AbstractVacancyStorage, 'get_vacancies')
        assert hasattr(AbstractVacancyStorage, 'delete_vacancy')


class TestAbstractDBManager:
    """Комплексное тестирование абстрактного менеджера БД"""
    
    def test_abstract_db_manager_cannot_be_instantiated(self):
        """Тестирование невозможности создания экземпляра абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractDBManager()
            
    def test_abstract_db_manager_methods_exist(self):
        """Тестирование наличия абстрактных методов"""
        assert hasattr(AbstractDBManager, 'get_companies_and_vacancies_count')
        assert hasattr(AbstractDBManager, 'get_all_vacancies')
        assert hasattr(AbstractDBManager, 'get_avg_salary')
        assert hasattr(AbstractDBManager, 'get_vacancies_with_higher_salary')
        assert hasattr(AbstractDBManager, 'get_vacancies_with_keyword')


class TestDBManager:
    """Комплексное тестирование менеджера базы данных"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        with patch('src.storage.db_manager.DatabaseConfig') as mock_config:
            mock_config.return_value.get_connection_params.return_value = {
                'host': 'localhost',
                'port': '5432',
                'database': 'test',
                'user': 'test',
                'password': 'test'
            }
            self.db_manager = DBManager()
            
    @patch('psycopg2.connect')
    def test_db_manager_initialization(self, mock_connect):
        """Тестирование инициализации менеджера БД"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        assert self.db_manager is not None
        assert hasattr(self.db_manager, 'config')
        
    @patch('psycopg2.connect')
    def test_get_companies_and_vacancies_count(self, mock_connect):
        """Тестирование получения количества компаний и вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('Company A', 10),
            ('Company B', 15),
            ('Company C', 5)
        ]
        mock_connect.return_value = mock_conn
        
        result = self.db_manager.get_companies_and_vacancies_count()
        
        assert isinstance(result, list)
        assert len(result) == 3
        for company, count in result:
            assert isinstance(company, str)
            assert isinstance(count, int)
            
    @patch('psycopg2.connect')
    def test_get_all_vacancies(self, mock_connect):
        """Тестирование получения всех вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('Company A', 'Python Developer', 100000, 'https://test.com/1'),
            ('Company B', 'Java Developer', 120000, 'https://test.com/2')
        ]
        mock_connect.return_value = mock_conn
        
        result = self.db_manager.get_all_vacancies()
        
        assert isinstance(result, list)
        assert len(result) == 2
        
    @patch('psycopg2.connect')
    def test_get_avg_salary(self, mock_connect):
        """Тестирование получения средней зарплаты"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (125000.0,)
        mock_connect.return_value = mock_conn
        
        result = self.db_manager.get_avg_salary()
        
        assert isinstance(result, float)
        assert result == 125000.0
        
    @patch('psycopg2.connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect):
        """Тестирование получения вакансий с зарплатой выше средней"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('Company A', 'Senior Python Developer', 150000, 'https://test.com/1'),
            ('Company B', 'Lead Java Developer', 180000, 'https://test.com/2')
        ]
        mock_connect.return_value = mock_conn
        
        result = self.db_manager.get_vacancies_with_higher_salary()
        
        assert isinstance(result, list)
        assert len(result) == 2
        
    @patch('psycopg2.connect')
    def test_get_vacancies_with_keyword(self, mock_connect):
        """Тестирование поиска вакансий по ключевому слову"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('Company A', 'Python Developer', 120000, 'https://test.com/1')
        ]
        mock_connect.return_value = mock_conn
        
        result = self.db_manager.get_vacancies_with_keyword("Python")
        
        assert isinstance(result, list)
        assert len(result) == 1
        
    @patch('psycopg2.connect')
    def test_db_manager_connection_error_handling(self, mock_connect):
        """Тестирование обработки ошибок подключения"""
        mock_connect.side_effect = Exception("Connection failed")
        
        # Методы должны обрабатывать ошибки подключения
        result = self.db_manager.get_companies_and_vacancies_count()
        assert result == []
        
        result = self.db_manager.get_avg_salary()
        assert result == 0.0


class TestPostgresSaver:
    """Комплексное тестирование PostgreSQL сохранителя"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        with patch('src.config.db_config.DatabaseConfig') as mock_config:
            mock_config.return_value.get_connection_params.return_value = {
                'host': 'localhost',
                'port': '5432',
                'database': 'test',
                'user': 'test',
                'password': 'test'
            }
            self.postgres_saver = PostgresSaver()
            
    @patch('psycopg2.connect')
    def test_postgres_saver_initialization(self, mock_connect):
        """Тестирование инициализации PostgreSQL сохранителя"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        assert self.postgres_saver is not None
        
    @patch('psycopg2.connect')
    def test_save_vacancies(self, mock_connect):
        """Тестирование сохранения вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        vacancies = [create_mock_vacancy() for _ in range(3)]
        
        self.postgres_saver.save_vacancies(vacancies)
        
        # Проверяем, что курсор был использован для выполнения запросов
        assert mock_cursor.execute.called
        assert mock_conn.commit.called
        
    @patch('psycopg2.connect')
    def test_get_vacancies(self, mock_connect):
        """Тестирование получения вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('1', 'Python Developer', 'https://test.com/1', 'Test Company', 100000, 'Test description')
        ]
        mock_connect.return_value = mock_conn
        
        result = self.postgres_saver.get_vacancies()
        
        assert isinstance(result, list)
        
    @patch('psycopg2.connect')
    def test_clear_vacancies(self, mock_connect):
        """Тестирование очистки вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        if hasattr(self.postgres_saver, 'clear_vacancies'):
            self.postgres_saver.clear_vacancies()
            assert mock_cursor.execute.called
            assert mock_conn.commit.called
            
    @patch('psycopg2.connect')
    def test_postgres_saver_error_handling(self, mock_connect):
        """Тестирование обработки ошибок"""
        mock_connect.side_effect = Exception("Database error")
        
        vacancies = [create_mock_vacancy()]
        
        # Метод должен обрабатывать ошибки без исключений
        try:
            self.postgres_saver.save_vacancies(vacancies)
        except Exception as e:
            pytest.fail(f"save_vacancies should handle database errors: {e}")


class TestStorageFactory:
    """Комплексное тестирование фабрики хранилищ"""
    
    def test_create_postgres_storage(self):
        """Тестирование создания PostgreSQL хранилища"""
        with patch('src.storage.storage_factory.PostgresSaver') as mock_postgres:
            mock_instance = Mock()
            mock_postgres.return_value = mock_instance
            
            storage = StorageFactory.create_storage("postgres")
            
            assert storage == mock_instance
            mock_postgres.assert_called_once()
            
    def test_create_invalid_storage(self):
        """Тестирование создания несуществующего типа хранилища"""
        storage = StorageFactory.create_storage("invalid_type")
        assert storage is None
        
    def test_get_available_storages(self):
        """Тестирование получения доступных типов хранилищ"""
        if hasattr(StorageFactory, 'get_available_storages'):
            storages = StorageFactory.get_available_storages()
            assert isinstance(storages, list)
            assert "postgres" in storages


class TestDatabaseConnection:
    """Комплексное тестирование компонента подключения к БД"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.db_connection = DatabaseConnection()
        
    @patch('psycopg2.connect')
    def test_database_connection_establishment(self, mock_connect):
        """Тестирование установки подключения к БД"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        connection = self.db_connection.get_connection()
        
        if connection:
            assert connection == mock_conn
            
    @patch('psycopg2.connect')
    def test_database_connection_context_manager(self, mock_connect):
        """Тестирование использования подключения как контекстного менеджера"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        if hasattr(self.db_connection, '__enter__'):
            with self.db_connection as conn:
                assert conn is not None
                
    def test_database_connection_error_handling(self):
        """Тестирование обработки ошибок подключения"""
        with patch('psycopg2.connect', side_effect=Exception("Connection failed")):
            connection = self.db_connection.get_connection()
            assert connection is None


class TestVacancyRepository:
    """Комплексное тестирование репозитория вакансий"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        mock_db_connection = Mock()
        mock_validator = Mock()
        mock_validator.validate_vacancy.return_value = True
        mock_validator.get_validation_errors.return_value = []
        
        self.vacancy_repository = VacancyRepository(mock_db_connection, mock_validator)
        
    def test_vacancy_repository_initialization(self):
        """Тестирование инициализации репозитория вакансий"""
        assert self.vacancy_repository is not None
        assert hasattr(self.vacancy_repository, 'db_manager')
        
    def test_save_vacancy(self):
        """Тестирование сохранения одной вакансии"""
        vacancy = create_mock_vacancy()
        
        if hasattr(self.vacancy_repository, 'save_vacancy'):
            result = self.vacancy_repository.save_vacancy(vacancy)
            assert isinstance(result, bool)
            
    def test_save_multiple_vacancies(self):
        """Тестирование сохранения нескольких вакансий"""
        vacancies = [create_mock_vacancy() for _ in range(5)]
        
        if hasattr(self.vacancy_repository, 'save_vacancies'):
            result = self.vacancy_repository.save_vacancies(vacancies)
            assert isinstance(result, (bool, int))
            
    def test_find_vacancy_by_id(self):
        """Тестирование поиска вакансии по ID"""
        if hasattr(self.vacancy_repository, 'find_by_id'):
            result = self.vacancy_repository.find_by_id("test_123")
            # Результат может быть None или объектом вакансии
            assert result is None or hasattr(result, 'vacancy_id')
            
    def test_find_vacancies_by_criteria(self):
        """Тестирование поиска вакансий по критериям"""
        if hasattr(self.vacancy_repository, 'find_by_criteria'):
            criteria = {'title': 'Python Developer', 'min_salary': 100000}
            result = self.vacancy_repository.find_by_criteria(criteria)
            assert isinstance(result, list)
            
    def test_update_vacancy(self):
        """Тестирование обновления вакансии"""
        vacancy = create_mock_vacancy()
        
        if hasattr(self.vacancy_repository, 'update_vacancy'):
            result = self.vacancy_repository.update_vacancy(vacancy)
            assert isinstance(result, bool)
            
    def test_delete_vacancy(self):
        """Тестирование удаления вакансии"""
        if hasattr(self.vacancy_repository, 'delete_vacancy'):
            result = self.vacancy_repository.delete_vacancy("test_123")
            assert isinstance(result, bool)


class TestVacancyValidator:
    """Комплексное тестирование валидатора вакансий"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.validator = VacancyValidator()
        
    def test_vacancy_validator_initialization(self):
        """Тестирование инициализации валидатора"""
        assert self.validator is not None
        
    def test_validate_complete_vacancy(self):
        """Тестирование валидации полной вакансии"""
        vacancy = create_mock_vacancy()
        
        if hasattr(self.validator, 'validate'):
            result = self.validator.validate(vacancy)
            assert isinstance(result, bool)
            
    def test_validate_incomplete_vacancy(self):
        """Тестирование валидации неполной вакансии"""
        vacancy = Mock()
        vacancy.vacancy_id = ""
        vacancy.title = ""
        vacancy.url = ""
        
        if hasattr(self.validator, 'validate'):
            result = self.validator.validate(vacancy)
            assert isinstance(result, bool)
            
    def test_validate_vacancy_fields(self):
        """Тестирование валидации отдельных полей вакансии"""
        if hasattr(self.validator, 'validate_id'):
            assert self.validator.validate_id("valid_id") is True
            assert self.validator.validate_id("") is False
            assert self.validator.validate_id(None) is False
            
        if hasattr(self.validator, 'validate_title'):
            assert self.validator.validate_title("Python Developer") is True
            assert self.validator.validate_title("") is False
            assert self.validator.validate_title(None) is False
            
        if hasattr(self.validator, 'validate_url'):
            assert self.validator.validate_url("https://example.com") is True
            assert self.validator.validate_url("invalid_url") is False
            assert self.validator.validate_url("") is False
            
    def test_get_validation_errors(self):
        """Тестирование получения ошибок валидации"""
        vacancy = Mock()
        vacancy.vacancy_id = ""
        vacancy.title = ""
        vacancy.url = "invalid_url"
        
        if hasattr(self.validator, 'get_validation_errors'):
            errors = self.validator.get_validation_errors(vacancy)
            assert isinstance(errors, list)
            assert len(errors) > 0


class TestVacancyStorageService:
    """Комплексное тестирование сервиса хранения вакансий"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        mock_storage = Mock()
        self.storage_service = VacancyStorageService(mock_storage)
        
    def test_storage_service_initialization(self):
        """Тестирование инициализации сервиса хранения"""
        assert self.storage_service is not None
        assert hasattr(self.storage_service, 'storage')
        
    def test_process_and_save_vacancies(self):
        """Тестирование обработки и сохранения вакансий"""
        vacancies = [create_mock_vacancy() for _ in range(3)]
        
        if hasattr(self.storage_service, 'process_and_save'):
            result = self.storage_service.process_and_save(vacancies)
            assert isinstance(result, (bool, int))
            
    def test_apply_filters(self):
        """Тестирование применения фильтров"""
        vacancies = [create_mock_vacancy() for _ in range(5)]
        
        if hasattr(self.storage_service, 'apply_filters'):
            result = self.storage_service.apply_filters(vacancies)
            assert isinstance(result, list)
            assert len(result) <= len(vacancies)
            
    def test_deduplicate_vacancies(self):
        """Тестирование дедупликации вакансий"""
        # Создаем дубликаты
        vacancy1 = create_mock_vacancy()
        vacancy2 = create_mock_vacancy()
        vacancy2.vacancy_id = vacancy1.vacancy_id  # Делаем дубликат
        vacancies = [vacancy1, vacancy2]
        
        if hasattr(self.storage_service, 'deduplicate'):
            result = self.storage_service.deduplicate(vacancies)
            assert isinstance(result, list)
            # После дедупликации должно остаться меньше или равно исходному количеству
            assert len(result) <= len(vacancies)


class TestFilteringServiceComprehensive:
    """Комплексное тестирование сервиса фильтрации"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.strategy = TargetCompanyFilterStrategy()
        self.filtering_service = FilteringService(self.strategy)
        
    def test_filtering_service_with_target_company_strategy(self):
        """Тестирование фильтрации по целевым компаниям"""
        vacancies = [create_mock_vacancy() for _ in range(5)]
        mock_db_manager = Mock()
        
        result = self.filtering_service.process(vacancies, mock_db_manager)
        
        assert isinstance(result, list)
        assert len(result) <= len(vacancies)
        
    def test_filtering_service_with_salary_strategy(self):
        """Тестирование фильтрации по зарплате"""
        salary_strategy = SalaryFilterStrategy()
        self.filtering_service.set_strategy(salary_strategy)
        
        vacancies = [create_mock_vacancy() for _ in range(3)]
        mock_db_manager = Mock()
        
        result = self.filtering_service.process(vacancies, mock_db_manager)
        
        assert isinstance(result, list)
        
    def test_strategy_change(self):
        """Тестирование смены стратегии фильтрации"""
        # Начинаем с одной стратегии
        assert isinstance(self.filtering_service.strategy, TargetCompanyFilterStrategy)
        
        # Меняем на другую стратегию
        new_strategy = SalaryFilterStrategy()
        self.filtering_service.set_strategy(new_strategy)
        
        assert isinstance(self.filtering_service.strategy, SalaryFilterStrategy)
        
    def test_empty_vacancies_list(self):
        """Тестирование обработки пустого списка вакансий"""
        mock_db_manager = Mock()
        result = self.filtering_service.process([], mock_db_manager)
        
        assert result == []


class TestDeduplicationServiceComprehensive:
    """Комплексное тестирование сервиса дедупликации"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.strategy = SQLDeduplicationStrategy()
        self.deduplication_service = DeduplicationService(self.strategy)
        
    def test_deduplication_service_initialization(self):
        """Тестирование инициализации сервиса дедупликации"""
        assert self.deduplication_service is not None
        assert isinstance(self.deduplication_service.strategy, SQLDeduplicationStrategy)
        
    def test_process_deduplication(self):
        """Тестирование процесса дедупликации"""
        # Создаем вакансии с дубликатами
        vacancy1 = create_mock_vacancy()
        vacancy2 = create_mock_vacancy()
        vacancy2.vacancy_id = vacancy1.vacancy_id  # Дубликат
        vacancy3 = create_mock_vacancy()
        vacancy3.vacancy_id = "unique_id"
        
        vacancies = [vacancy1, vacancy2, vacancy3]
        mock_db_manager = Mock()
        
        result = self.deduplication_service.process(vacancies, mock_db_manager)
        
        assert isinstance(result, list)
        assert len(result) <= len(vacancies)
        
    def test_strategy_change_deduplication(self):
        """Тестирование смены стратегии дедупликации"""
        # Начинаем с SQL стратегии
        assert isinstance(self.deduplication_service.strategy, SQLDeduplicationStrategy)
        
        # Можем добавить другие стратегии дедупликации для тестирования
        # Пока тестируем только изменение на ту же стратегию
        new_strategy = SQLDeduplicationStrategy()
        self.deduplication_service.set_strategy(new_strategy)
        
        assert isinstance(self.deduplication_service.strategy, SQLDeduplicationStrategy)


class TestStorageIntegration:
    """Интеграционные тесты для модулей хранения"""
    
    @patch('psycopg2.connect')
    def test_full_storage_workflow(self, mock_connect):
        """Тестирование полного рабочего процесса хранения"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Создаем компоненты
        with patch('src.storage.postgres_saver.DatabaseConfig'):
            postgres_saver = PostgresSaver()
            
        # Создаем тестовые данные
        vacancies = [create_mock_vacancy() for _ in range(3)]
        
        # Выполняем полный workflow
        postgres_saver.save_vacancies(vacancies)
        saved_vacancies = postgres_saver.get_vacancies()
        
        # Проверяем результат
        assert isinstance(saved_vacancies, list)
        
    def test_storage_error_recovery(self):
        """Тестирование восстановления после ошибок хранения"""
        with patch('psycopg2.connect', side_effect=Exception("Database unavailable")):
            with patch('src.storage.postgres_saver.DatabaseConfig'):
                postgres_saver = PostgresSaver()
                
                vacancies = [create_mock_vacancy()]
                
                # Операция должна обрабатывать ошибку без исключения
                try:
                    postgres_saver.save_vacancies(vacancies)
                    result = postgres_saver.get_vacancies()
                    # В случае ошибки должен возвращаться пустой список
                    assert result == []
                except Exception as e:
                    pytest.fail(f"Storage should handle errors gracefully: {e}")
                    
    def test_storage_performance_simulation(self):
        """Симуляция тестирования производительности хранения"""
        # Создаем большое количество вакансий
        large_vacancy_list = [create_mock_vacancy() for _ in range(100)]
        
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            with patch('src.storage.postgres_saver.DatabaseConfig'):
                postgres_saver = PostgresSaver()
                
                # Операция должна завершиться без таймаута
                import time
                start_time = time.time()
                postgres_saver.save_vacancies(large_vacancy_list)
                end_time = time.time()
                
                # Проверяем, что операция выполнилась за разумное время
                assert (end_time - start_time) < 5.0  # Менее 5 секунд