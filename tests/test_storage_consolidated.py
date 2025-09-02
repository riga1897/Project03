
"""
Консолидированные тесты для всех модулей хранения данных
Объединяет тесты abstract, abstract_db_manager, db_manager, postgres_saver, storage_factory
"""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock, Mock, patch, call
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорты модулей хранения
try:
    from src.storage.abstract import AbstractSaver
    from src.storage.abstract_db_manager import AbstractDBManager
    from src.storage.db_manager import DBManager
    from src.storage.postgres_saver import PostgresSaver
    from src.storage.storage_factory import StorageFactory
    from src.vacancies.models import Vacancy
    STORAGE_MODULES_AVAILABLE = True
except ImportError:
    STORAGE_MODULES_AVAILABLE = False


class MockConnection:
    """Мок подключения к базе данных"""
    
    def __init__(self):
        self.cursor_instance = MockCursor()
        self.closed = False
        self.committed = False
    
    def cursor(self):
        return self.cursor_instance
    
    def commit(self):
        self.committed = True
    
    def close(self):
        self.closed = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MockCursor:
    """Мок курсора базы данных"""
    
    def __init__(self):
        self.results = []
        self.executed_queries = []
        self.closed = False
    
    def execute(self, query: str, params=None):
        self.executed_queries.append((query, params))
    
    def fetchall(self) -> List[Tuple]:
        return self.results
    
    def fetchone(self) -> Optional[Tuple]:
        return self.results[0] if self.results else None
    
    def set_results(self, results: List[Tuple]):
        self.results = results
    
    def close(self):
        self.closed = True


class TestStorageConsolidated:
    """Консолидированные тесты для всех модулей хранения"""

    @pytest.fixture
    def mock_connection(self):
        """Фикстура мок подключения"""
        return MockConnection()

    @pytest.fixture
    def sample_vacancy_data(self):
        """Образец данных вакансии"""
        return {
            "id": "123456",
            "name": "Python Developer",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "employer": {"name": "Test Company"},
            "area": {"name": "Москва"},
            "experience": {"name": "От 1 года до 3 лет"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"},
            "description": "Test description with Python",
            "url": "https://test.com/vacancy/123456",
            "alternate_url": "https://test.com/vacancy/123456",
            "published_at": "2025-01-01T00:00:00+0300",
        }

    def test_abstract_saver_interface(self) -> None:
        """Тест интерфейса AbstractSaver"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        # Проверяем что AbstractSaver является абстрактным классом
        try:
            # Попытка создания экземпляра должна вызвать ошибку
            AbstractSaver()
            pytest.fail("AbstractSaver should not be instantiable")
        except TypeError:
            # Ожидаемое поведение для абстрактного класса
            pass

        # Проверяем наличие абстрактных методов
        if hasattr(AbstractSaver, '__abstractmethods__'):
            abstract_methods = AbstractSaver.__abstractmethods__
            expected_methods = {'save_vacancies', 'get_vacancies'}
            assert len(abstract_methods.intersection(expected_methods)) > 0

    def test_abstract_db_manager_interface(self) -> None:
        """Тест интерфейса AbstractDBManager"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        try:
            AbstractDBManager()
            pytest.fail("AbstractDBManager should not be instantiable")
        except TypeError:
            pass

        # Проверяем наличие абстрактных методов
        if hasattr(AbstractDBManager, '__abstractmethods__'):
            abstract_methods = AbstractDBManager.__abstractmethods__
            expected_methods = {'get_connection', 'execute_query'}
            assert len(abstract_methods.intersection(expected_methods)) > 0

    def test_postgres_saver_functionality(self, mock_connection: MockConnection, sample_vacancy_data: Dict) -> None:
        """Тест функциональности PostgresSaver"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        with patch('psycopg2.connect', return_value=mock_connection):
            postgres_saver = PostgresSaver()
            
            # Тест сохранения вакансий
            vacancies = [Vacancy.from_dict(sample_vacancy_data)]
            postgres_saver.save_vacancies(vacancies)
            
            # Проверяем что были выполнены SQL запросы
            assert len(mock_connection.cursor_instance.executed_queries) > 0
            assert mock_connection.committed

    def test_db_manager_functionality(self, mock_connection: MockConnection) -> None:
        """Тест функциональности DBManager"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        with patch('psycopg2.connect', return_value=mock_connection):
            db_manager = DBManager()
            
            # Тест получения подключения
            connection = db_manager.get_connection()
            assert connection is not None
            
            # Тест выполнения запроса
            mock_connection.cursor_instance.set_results([("test_result",)])
            result = db_manager.execute_query("SELECT * FROM test")
            assert result == [("test_result",)]

    def test_storage_factory_functionality(self) -> None:
        """Тест функциональности StorageFactory"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        # Тест создания PostgresSaver
        postgres_saver = StorageFactory.create_storage("postgres")
        assert isinstance(postgres_saver, PostgresSaver)
        
        # Тест создания DBManager
        db_manager = StorageFactory.create_db_manager("postgres")
        assert isinstance(db_manager, DBManager)
        
        # Тест неизвестного типа хранилища
        with pytest.raises((ValueError, KeyError)):
            StorageFactory.create_storage("unknown")

    def test_database_operations(self, mock_connection: MockConnection) -> None:
        """Тест операций с базой данных"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        with patch('psycopg2.connect', return_value=mock_connection):
            db_manager = DBManager()
            
            # Тест создания таблиц
            db_manager.create_tables()
            assert len(mock_connection.cursor_instance.executed_queries) > 0
            
            # Тест получения статистики
            mock_connection.cursor_instance.set_results([(10, 5)])
            stats = db_manager.get_database_stats()
            assert isinstance(stats, dict)

    def test_vacancy_storage_operations(self, mock_connection: MockConnection, sample_vacancy_data: Dict) -> None:
        """Тест операций хранения вакансий"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        with patch('psycopg2.connect', return_value=mock_connection):
            postgres_saver = PostgresSaver()
            
            # Тест сохранения одной вакансии
            vacancy = Vacancy.from_dict(sample_vacancy_data)
            postgres_saver.save_vacancy(vacancy)
            
            # Тест получения вакансий
            mock_connection.cursor_instance.set_results([
                ("123456", "Python Developer", "Test Company", 100000, 150000, "https://test.com/vacancy/123456")
            ])
            
            vacancies = postgres_saver.get_vacancies()
            assert isinstance(vacancies, list)

    def test_database_connection_management(self, mock_connection: MockConnection) -> None:
        """Тест управления подключениями к БД"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        with patch('psycopg2.connect', return_value=mock_connection):
            db_manager = DBManager()
            
            # Тест контекстного менеджера
            with db_manager.get_connection() as conn:
                assert conn is not None
                assert not mock_connection.closed
            
            # После выхода из контекста соединение должно закрыться
            assert mock_connection.closed

    def test_error_handling_in_storage(self, mock_connection: MockConnection) -> None:
        """Тест обработки ошибок в модулях хранения"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        # Тест обработки ошибки подключения
        with patch('psycopg2.connect', side_effect=Exception("Connection failed")):
            db_manager = DBManager()
            
            try:
                db_manager.get_connection()
                pytest.fail("Should raise exception on connection failure")
            except Exception:
                pass

    def test_storage_performance_optimization(self, mock_connection: MockConnection) -> None:
        """Тест оптимизации производительности хранения"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        with patch('psycopg2.connect', return_value=mock_connection):
            postgres_saver = PostgresSaver()
            
            # Тест пакетного сохранения вакансий
            vacancies = []
            for i in range(100):
                vacancy_data = {
                    "id": f"12345{i}",
                    "name": f"Developer {i}",
                    "url": f"https://test.com/vacancy/12345{i}",
                    "source": "test"
                }
                vacancies.append(Vacancy.from_dict(vacancy_data))
            
            postgres_saver.save_vacancies(vacancies)
            
            # Проверяем что было выполнено оптимальное количество запросов
            queries_count = len(mock_connection.cursor_instance.executed_queries)
            assert queries_count > 0
            # Пакетное сохранение должно использовать меньше запросов чем по одной записи
            assert queries_count < len(vacancies)

    def test_storage_data_consistency(self, mock_connection: MockConnection) -> None:
        """Тест целостности данных в хранилище"""
        if not STORAGE_MODULES_AVAILABLE:
            pytest.skip("Storage modules not available")

        with patch('psycopg2.connect', return_value=mock_connection):
            postgres_saver = PostgresSaver()
            
            # Тест транзакционности
            mock_connection.cursor_instance.execute = Mock(side_effect=Exception("SQL Error"))
            
            vacancy_data = {
                "id": "123456",
                "name": "Test Vacancy",
                "url": "https://test.com/vacancy/123456",
                "source": "test"
            }
            vacancy = Vacancy.from_dict(vacancy_data)
            
            try:
                postgres_saver.save_vacancy(vacancy)
            except Exception:
                # При ошибке транзакция должна быть откачена
                assert not mock_connection.committed
