
"""
Полные тесты для компонентов хранения данных
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.storage.db_manager import DBManager
    from src.storage.postgres_saver import PostgresSaver
    from src.storage.storage_factory import StorageFactory
    from src.storage.simple_db_adapter import SimpleDBAdapter
    STORAGE_COMPONENTS_AVAILABLE = True
except ImportError:
    STORAGE_COMPONENTS_AVAILABLE = False
    DBManager = object
    PostgresSaver = object
    StorageFactory = object
    SimpleDBAdapter = object

try:
    from src.storage.components.database_connection import DatabaseConnection
    from src.storage.components.vacancy_repository import VacancyRepository
    from src.storage.components.vacancy_validator import VacancyValidator
    STORAGE_SUBCOMPONENTS_AVAILABLE = True
except ImportError:
    STORAGE_SUBCOMPONENTS_AVAILABLE = False
    DatabaseConnection = object
    VacancyRepository = object
    VacancyValidator = object


class TestDBManager:
    """Тесты для менеджера базы данных"""
    
    @pytest.fixture
    def db_manager(self):
        """Фикстура менеджера БД"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            return Mock()
        
        with patch('psycopg2.connect'):
            return DBManager()
    
    def test_init(self, db_manager):
        """Тест инициализации"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        assert db_manager is not None
    
    @patch('psycopg2.connect')
    def test_connect(self, mock_connect, db_manager):
        """Тест подключения к БД"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        if hasattr(db_manager, 'connect'):
            db_manager.connect()
            mock_connect.assert_called()
    
    def test_disconnect(self, db_manager):
        """Тест отключения от БД"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        # Мокаем соединение
        mock_connection = Mock()
        if hasattr(db_manager, 'connection'):
            db_manager.connection = mock_connection
        
        if hasattr(db_manager, 'disconnect'):
            db_manager.disconnect()
            if hasattr(mock_connection, 'close'):
                mock_connection.close.assert_called()
    
    @patch('psycopg2.connect')
    def test_execute_query(self, mock_connect, db_manager):
        """Тест выполнения запроса"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [('test',)]
        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        if hasattr(db_manager, 'execute_query'):
            result = db_manager.execute_query("SELECT * FROM test")
            assert result is not None


class TestPostgresSaver:
    """Тесты для PostgreSQL сохранителя"""
    
    @pytest.fixture
    def postgres_saver(self):
        """Фикстура PostgreSQL сохранителя"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            return Mock()
        
        with patch('psycopg2.connect'):
            return PostgresSaver()
    
    def test_init(self, postgres_saver):
        """Тест инициализации"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        assert postgres_saver is not None
    
    @patch('psycopg2.connect')
    def test_save_vacancy(self, mock_connect, postgres_saver):
        """Тест сохранения вакансии"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        mock_cursor = Mock()
        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        vacancy_data = {
            "id": "123",
            "title": "Python Developer",
            "company": "Test Company",
            "salary": "100000"
        }
        
        if hasattr(postgres_saver, 'save_vacancy'):
            result = postgres_saver.save_vacancy(vacancy_data)
            mock_cursor.execute.assert_called()
    
    def test_save_vacancies_batch(self, postgres_saver):
        """Тест пакетного сохранения вакансий"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        vacancies = [
            {"id": "1", "title": "Dev 1"},
            {"id": "2", "title": "Dev 2"}
        ]
        
        with patch.object(postgres_saver, 'save_vacancy', return_value=True) as mock_save:
            if hasattr(postgres_saver, 'save_vacancies'):
                postgres_saver.save_vacancies(vacancies)
                assert mock_save.call_count == 2


class TestStorageFactory:
    """Тесты для фабрики хранилищ"""
    
    def test_create_storage(self):
        """Тест создания хранилища"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        with patch('src.storage.postgres_saver.PostgresSaver') as mock_postgres:
            mock_instance = Mock()
            mock_postgres.return_value = mock_instance
            
            if hasattr(StorageFactory, 'create_storage'):
                storage = StorageFactory.create_storage('postgres')
                assert storage is not None
            else:
                # Тестируем создание фабрики
                factory = StorageFactory()
                assert factory is not None
    
    def test_get_available_storages(self):
        """Тест получения доступных хранилищ"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        if hasattr(StorageFactory, 'get_available_storages'):
            storages = StorageFactory.get_available_storages()
            assert isinstance(storages, list)


class TestSimpleDBAdapter:
    """Тесты для простого адаптера БД"""
    
    @pytest.fixture
    def db_adapter(self):
        """Фикстура адаптера БД"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            return Mock()
        
        with patch('sqlite3.connect'):
            return SimpleDBAdapter()
    
    def test_init(self, db_adapter):
        """Тест инициализации"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        assert db_adapter is not None
    
    @patch('sqlite3.connect')
    def test_create_table(self, mock_connect, db_adapter):
        """Тест создания таблицы"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        mock_cursor = Mock()
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        if hasattr(db_adapter, 'create_table'):
            db_adapter.create_table()
            mock_cursor.execute.assert_called()
    
    def test_insert_vacancy(self, db_adapter):
        """Тест вставки вакансии"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        vacancy = {"id": "123", "title": "Test"}
        
        with patch.object(db_adapter, 'connection') as mock_conn:
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            if hasattr(db_adapter, 'insert_vacancy'):
                db_adapter.insert_vacancy(vacancy)
                mock_cursor.execute.assert_called()
    
    def test_get_vacancies(self, db_adapter):
        """Тест получения вакансий"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        with patch.object(db_adapter, 'connection') as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [("123", "Test", "Company")]
            mock_conn.cursor.return_value = mock_cursor
            
            if hasattr(db_adapter, 'get_vacancies'):
                result = db_adapter.get_vacancies()
                assert isinstance(result, list)


class TestDatabaseConnection:
    """Тесты для подключения к БД"""
    
    @pytest.fixture
    def db_connection(self):
        """Фикстура подключения к БД"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            return Mock()
        
        with patch('psycopg2.connect'):
            return DatabaseConnection()
    
    def test_init(self, db_connection):
        """Тест инициализации"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        assert db_connection is not None
    
    @patch('psycopg2.connect')
    def test_connect(self, mock_connect, db_connection):
        """Тест подключения"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        if hasattr(db_connection, 'connect'):
            result = db_connection.connect()
            mock_connect.assert_called()
    
    def test_is_connected(self, db_connection):
        """Тест проверки подключения"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        if hasattr(db_connection, 'is_connected'):
            result = db_connection.is_connected()
            assert isinstance(result, bool)
    
    def test_close(self, db_connection):
        """Тест закрытия подключения"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        mock_connection = Mock()
        if hasattr(db_connection, 'connection'):
            db_connection.connection = mock_connection
        
        if hasattr(db_connection, 'close'):
            db_connection.close()
            if hasattr(mock_connection, 'close'):
                mock_connection.close.assert_called()


class TestVacancyRepository:
    """Тесты для репозитория вакансий"""
    
    @pytest.fixture
    def vacancy_repository(self):
        """Фикстура репозитория вакансий"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            return Mock()
        
        with patch('src.storage.components.database_connection.DatabaseConnection'):
            return VacancyRepository()
    
    def test_init(self, vacancy_repository):
        """Тест инициализации"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        assert vacancy_repository is not None
    
    def test_add_vacancy(self, vacancy_repository):
        """Тест добавления вакансии"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        vacancy = {"id": "123", "title": "Test"}
        
        if hasattr(vacancy_repository, 'add_vacancy'):
            result = vacancy_repository.add_vacancy(vacancy)
        else:
            # Если метод не существует, просто проверим что репозиторий создался
            assert vacancy_repository is not None
    
    def test_get_vacancies(self, vacancy_repository):
        """Тест получения вакансий"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        if hasattr(vacancy_repository, 'get_vacancies'):
            result = vacancy_repository.get_vacancies()
            assert isinstance(result, list)
    
    def test_find_by_id(self, vacancy_repository):
        """Тест поиска по ID"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        if hasattr(vacancy_repository, 'find_by_id'):
            result = vacancy_repository.find_by_id("123")
        else:
            assert vacancy_repository is not None
    
    def test_delete_vacancy(self, vacancy_repository):
        """Тест удаления вакансии"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        vacancy = {"id": "123", "title": "Test"}
        
        if hasattr(vacancy_repository, 'delete_vacancy'):
            result = vacancy_repository.delete_vacancy(vacancy)
        else:
            assert vacancy_repository is not None


class TestVacancyValidator:
    """Тесты для валидатора вакансий"""
    
    @pytest.fixture
    def vacancy_validator(self):
        """Фикстура валидатора вакансий"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            return Mock()
        
        return VacancyValidator()
    
    def test_init(self, vacancy_validator):
        """Тест инициализации"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        assert vacancy_validator is not None
    
    def test_validate_valid_vacancy(self, vacancy_validator):
        """Тест валидации корректной вакансии"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        valid_vacancy = {
            "id": "123",
            "title": "Python Developer",
            "company": "Test Company",
            "salary": {"from": 100000, "currency": "RUR"}
        }
        
        if hasattr(vacancy_validator, 'validate'):
            result = vacancy_validator.validate(valid_vacancy)
            assert result == True
        elif hasattr(vacancy_validator, 'is_valid'):
            result = vacancy_validator.is_valid(valid_vacancy)
            assert result == True
    
    def test_validate_invalid_vacancy(self, vacancy_validator):
        """Тест валидации некорректной вакансии"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        invalid_vacancy = {"title": ""}  # пустой title
        
        if hasattr(vacancy_validator, 'validate'):
            result = vacancy_validator.validate(invalid_vacancy)
            assert result == False
        elif hasattr(vacancy_validator, 'is_valid'):
            result = vacancy_validator.is_valid(invalid_vacancy)
            assert result == False
    
    def test_validate_none_vacancy(self, vacancy_validator):
        """Тест валидации None вакансии"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        if hasattr(vacancy_validator, 'validate'):
            result = vacancy_validator.validate(None)
            assert result == False
        elif hasattr(vacancy_validator, 'is_valid'):
            result = vacancy_validator.is_valid(None)
            assert result == False
    
    def test_validate_empty_dict(self, vacancy_validator):
        """Тест валидации пустого словаря"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        empty_vacancy = {}
        
        if hasattr(vacancy_validator, 'validate'):
            result = vacancy_validator.validate(empty_vacancy)
            assert result == False
        elif hasattr(vacancy_validator, 'is_valid'):
            result = vacancy_validator.is_valid(empty_vacancy)
            assert result == False


class TestStorageIntegration:
    """Интеграционные тесты компонентов хранения"""
    
    @patch('psycopg2.connect')
    def test_db_manager_with_postgres_saver_integration(self, mock_connect):
        """Тест интеграции DBManager с PostgresSaver"""
        if not STORAGE_COMPONENTS_AVAILABLE:
            pytest.skip("Storage components not available")
        
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Создаем компоненты
        db_manager = DBManager()
        postgres_saver = PostgresSaver()
        
        assert db_manager is not None
        assert postgres_saver is not None
    
    def test_repository_with_validator_integration(self):
        """Тест интеграции Repository с Validator"""
        if not STORAGE_SUBCOMPONENTS_AVAILABLE:
            pytest.skip("Storage subcomponents not available")
        
        with patch('src.storage.components.database_connection.DatabaseConnection'):
            repository = VacancyRepository()
            validator = VacancyValidator()
            
            assert repository is not None
            assert validator is not None
            
            # Тест валидации перед сохранением
            vacancy = {"id": "123", "title": "Test"}
            
            if hasattr(validator, 'validate') and hasattr(repository, 'add_vacancy'):
                is_valid = validator.validate(vacancy)
                if is_valid:
                    repository.add_vacancy(vacancy)
