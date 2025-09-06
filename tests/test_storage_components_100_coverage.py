"""
100% покрытие storage/components модулей
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import pytest
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.storage.components.database_connection import DatabaseConnection
from src.storage.components.vacancy_repository import VacancyRepository 
from src.storage.components.vacancy_validator import VacancyValidator


# Mock класс для AbstractVacancy
class MockVacancy:
    """Mock объект для тестирования валидатора"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestDatabaseConnectionImports:
    """Тесты для покрытия import error блоков в database_connection.py"""
    
    def test_psycopg2_import_error(self):
        """Тест обработки ImportError для psycopg2"""
        # Мокируем отсутствие psycopg2 модуля при импорте
        import sys
        original_modules = sys.modules.copy()
        
        # Убираем psycopg2 из импортированных модулей если он есть
        if 'psycopg2' in sys.modules:
            del sys.modules['psycopg2']
        
        # Мокируем ImportError
        import builtins
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'psycopg2':
                raise ImportError("No module named 'psycopg2'")
            return original_import(name, *args, **kwargs)
        
        builtins.__import__ = mock_import
        
        try:
            # Заново импортируем модуль для покрытия строк 14-16
            import importlib
            import src.storage.components.database_connection
            importlib.reload(src.storage.components.database_connection)
            
            # Проверяем что fallback работает
            assert src.storage.components.database_connection.psycopg2 is None
            assert src.storage.components.database_connection.PsycopgError == Exception
        finally:
            # Восстанавливаем оригинальную функцию импорта
            builtins.__import__ = original_import
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_realdict_cursor_import_error(self):
        """Тест обработки ImportError для RealDictCursor"""
        import sys
        import builtins
        
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'psycopg2.extras':
                raise ImportError("Cannot import RealDictCursor")
            return original_import(name, *args, **kwargs)
        
        builtins.__import__ = mock_import
        
        try:
            import importlib
            import src.storage.components.database_connection
            importlib.reload(src.storage.components.database_connection)
            
            # Проверяем что fallback работает для строк 19-20
            assert src.storage.components.database_connection.RealDictCursor is None
        finally:
            builtins.__import__ = original_import


class TestDatabaseConnection:
    """100% покрытие DatabaseConnection"""

    def test_init_with_params(self):
        """Тест инициализации с параметрами"""
        params = {
            "host": "test_host",
            "port": "5433",
            "database": "test_db",
            "user": "test_user",
            "password": "test_pass"
        }
        db_conn = DatabaseConnection(params)
        assert db_conn._connection_params == params
        assert db_conn._connection is None

    @patch.dict('os.environ', {
        'PGHOST': 'env_host',
        'PGPORT': '5434', 
        'PGDATABASE': 'env_db',
        'PGUSER': 'env_user',
        'PGPASSWORD': 'env_pass'
    })
    def test_init_with_env_vars(self):
        """Тест инициализации с переменными окружения"""
        db_conn = DatabaseConnection()
        expected = {
            "host": "env_host",
            "port": "5434",
            "database": "env_db", 
            "user": "env_user",
            "password": "env_pass"
        }
        assert db_conn._connection_params == expected

    def test_init_default_params(self):
        """Тест инициализации с дефолтными параметрами"""
        with patch.dict('os.environ', {}, clear=True):
            db_conn = DatabaseConnection()
            expected = {
                "host": "localhost",
                "port": "5432",
                "database": "postgres",
                "user": "postgres", 
                "password": ""
            }
            assert db_conn._connection_params == expected

    @patch('psycopg2.connect')
    def test_get_connection_creates_new(self, mock_connect):
        """Тест создания нового подключения"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        result = db_conn.get_connection()
        
        assert result == mock_connection
        assert db_conn._connection == mock_connection
        mock_connect.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_connection_reuses_valid(self, mock_connect):
        """Тест переиспользования валидного подключения"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_cursor.execute = Mock()
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        # Первый вызов создает подключение
        result1 = db_conn.get_connection()
        # Второй вызов должен переиспользовать
        result2 = db_conn.get_connection()
        
        assert result1 == result2 == mock_connection
        # connect должен быть вызван только один раз
        mock_connect.assert_called_once()

    def test_is_connection_valid_none(self):
        """Тест проверки валидности None подключения"""
        db_conn = DatabaseConnection()
        assert not db_conn._is_connection_valid()

    def test_is_connection_valid_exception(self):
        """Тест проверки валидности при исключении"""
        mock_connection = Mock()
        # Мокируем cursor чтобы он вызывал исключение нужного типа
        from src.storage.components.database_connection import psycopg2
        mock_connection.cursor.side_effect = psycopg2.OperationalError("Connection lost")
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        assert not db_conn._is_connection_valid()

    def test_is_connection_valid_true(self):
        """Тест проверки валидности здорового подключения"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        assert db_conn._is_connection_valid()
        mock_cursor.execute.assert_called_once_with("SELECT 1")

    @patch('psycopg2.connect')
    def test_create_new_connection_success(self, mock_connect):
        """Тест успешного создания подключения"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection({"host": "test"})
        db_conn._create_new_connection()
        
        assert db_conn._connection == mock_connection
        # Проверяем что connect вызван с правильными параметрами включая cursor_factory
        mock_connect.assert_called_once()
        call_kwargs = mock_connect.call_args[1]
        assert call_kwargs["host"] == "test"
        assert "cursor_factory" in call_kwargs

    @patch('psycopg2.connect')
    def test_create_new_connection_failure(self, mock_connect):
        """Тест обработки ошибки создания подключения"""
        from src.storage.components.database_connection import PsycopgError
        mock_connect.side_effect = PsycopgError("Connection failed")
        
        db_conn = DatabaseConnection()
        
        with patch('src.storage.components.database_connection.logger') as mock_logger:
            with pytest.raises(ConnectionError):
                db_conn._create_new_connection()
        
        mock_logger.error.assert_called_once()

    def test_close_connection_none(self):
        """Тест закрытия None подключения"""
        db_conn = DatabaseConnection()
        # Не должно вызывать ошибку
        db_conn.close_connection()

    def test_close_connection_success(self):
        """Тест успешного закрытия подключения"""
        mock_connection = Mock()
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        db_conn.close_connection()
        
        mock_connection.close.assert_called_once()
        assert db_conn._connection is None

    def test_close_connection_exception(self):
        """Тест обработки ошибки при закрытии"""
        mock_connection = Mock()
        mock_connection.close.side_effect = Exception("Close failed")
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        with patch('src.storage.components.database_connection.logger') as mock_logger:
            db_conn.close_connection()
        
        mock_logger.warning.assert_called_once()
        assert db_conn._connection is None

    def test_context_manager_success(self):
        """Тест использования как context manager"""
        mock_connection = Mock()
        
        with patch.object(DatabaseConnection, 'get_connection', return_value=mock_connection):
            with patch.object(DatabaseConnection, 'close_connection') as mock_close:
                db_conn = DatabaseConnection()
                
                with db_conn as conn:
                    assert conn == mock_connection
                
                mock_close.assert_called_once()

    def test_context_manager_exception(self):
        """Тест context manager при исключении"""
        mock_connection = Mock()
        
        with patch.object(DatabaseConnection, 'get_connection', return_value=mock_connection):
            with patch.object(DatabaseConnection, 'close_connection') as mock_close:
                db_conn = DatabaseConnection()
                
                try:
                    with db_conn as conn:
                        raise ValueError("Test exception")
                except ValueError:
                    pass
                
                mock_close.assert_called_once()


class TestVacancyRepository:
    """100% покрытие VacancyRepository"""

    def test_init(self):
        """Тест инициализации"""
        mock_db_conn = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_db_conn, mock_validator)
        assert repo._db_connection == mock_db_conn
        assert repo._validator == mock_validator

    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_success(self, mock_logger):
        """Тест успешного добавления вакансии"""
        mock_db_conn = Mock()
        mock_validator = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        # Мокируем валидацию
        mock_validator.validate_vacancy.return_value = True
        
        # Мокируем подключение к БД
        mock_db_conn.get_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_db_conn.get_connection.return_value.__exit__ = Mock(return_value=False)
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        # Создаем mock вакансии
        mock_vacancy = MockVacancy(
            vacancy_id="123",
            title="Test Job", 
            url="https://example.com/job/123",
            salary=None
        )
        
        repo = VacancyRepository(mock_db_conn, mock_validator)
        repo.add_vacancy(mock_vacancy)
        
        mock_validator.validate_vacancy.assert_called_once_with(mock_vacancy)
        mock_cursor.execute.assert_called_once()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_validation_failure(self, mock_logger):
        """Тест добавления невалидной вакансии"""
        mock_db_conn = Mock()
        mock_validator = Mock()
        
        # Мокируем неуспешную валидацию
        mock_validator.validate_vacancy.return_value = False
        mock_validator.get_validation_errors.return_value = ["Error 1", "Error 2"]
        
        mock_vacancy = MockVacancy(vacancy_id="123")
        
        repo = VacancyRepository(mock_db_conn, mock_validator)
        
        with pytest.raises(ValueError) as exc_info:
            repo.add_vacancy(mock_vacancy)
        
        assert "не прошла валидацию" in str(exc_info.value)
        mock_validator.validate_vacancy.assert_called_once()
        mock_validator.get_validation_errors.assert_called_once()

    def test_get_vacancies_no_filters(self):
        """Тест получения вакансий без фильтров"""
        mock_db_conn = Mock()
        mock_validator = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_db_conn.get_connection.return_value.__exit__ = Mock(return_value=False)
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.fetchall.return_value = [
            {"vacancy_id": "1", "title": "Job 1"},
            {"vacancy_id": "2", "title": "Job 2"}
        ]
        
        # Мокируем импорт Vacancy класса
        with patch('src.vacancies.models.Vacancy') as mock_vacancy_class:
            mock_vacancy_instance = Mock()
            mock_vacancy_class.from_dict.return_value = mock_vacancy_instance
            
            repo = VacancyRepository(mock_db_conn, mock_validator)
            result = repo.get_vacancies()
            
            # Проверяем что получили список вакансий
            assert isinstance(result, list)
            mock_cursor.execute.assert_called_once()

    def test_get_vacancies_with_filters(self):
        """Тест получения вакансий с фильтрами"""
        mock_db_conn = Mock()
        mock_validator = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_db_conn.get_connection.return_value.__exit__ = Mock(return_value=False)
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.fetchall.return_value = [{"vacancy_id": "1", "title": "Python Developer"}]
        
        with patch('src.vacancies.models.Vacancy') as mock_vacancy_class:
            mock_vacancy_instance = Mock()
            mock_vacancy_class.from_dict.return_value = mock_vacancy_instance
            
            repo = VacancyRepository(mock_db_conn, mock_validator)
            filters = {"min_salary": 100000, "source": "hh"}
            result = repo.get_vacancies(filters)
            
            # Проверяем что получили результат и SQL содержит WHERE
            assert isinstance(result, list)
            call_args = mock_cursor.execute.call_args[0][0]
            assert "WHERE" in call_args

    def test_delete_vacancy_success(self):
        """Тест успешного удаления вакансии"""
        mock_db_conn = Mock()
        mock_validator = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_db_conn.get_connection.return_value.__exit__ = Mock(return_value=False)
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.rowcount = 1
        
        mock_vacancy = MockVacancy(vacancy_id="123")
        
        repo = VacancyRepository(mock_db_conn, mock_validator)
        repo.delete_vacancy(mock_vacancy)
        
        mock_cursor.execute.assert_called_once()
        # Проверяем что коммит был вызван
        mock_connection.commit.assert_called_once()

    def test_check_vacancies_exist_batch(self):
        """Тест проверки существования вакансий пакетом"""
        mock_db_conn = Mock()
        mock_validator = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_db_conn.get_connection.return_value.__exit__ = Mock(return_value=False)
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.fetchall.return_value = [
            {"vacancy_id": "1"},
            {"vacancy_id": "3"}
        ]
        
        vacancies = [
            MockVacancy(vacancy_id="1"),
            MockVacancy(vacancy_id="2"), 
            MockVacancy(vacancy_id="3")
        ]
        
        repo = VacancyRepository(mock_db_conn, mock_validator)
        result = repo.check_vacancies_exist_batch(vacancies)
        
        assert result["1"] is True
        assert result["2"] is False
        assert result["3"] is True


class TestVacancyValidator:
    """100% покрытие VacancyValidator"""

    def test_init(self):
        """Тест инициализации валидатора"""
        validator = VacancyValidator()
        assert validator._validation_errors == []

    def test_validate_vacancy_success(self):
        """Тест валидации корректной вакансии"""
        validator = VacancyValidator()
        
        mock_vacancy = MockVacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://example.com/job/123",
            salary=None,
            description="Job description"
        )
        
        result = validator.validate_vacancy(mock_vacancy)
        assert result is True
        assert len(validator.get_validation_errors()) == 0

    def test_validate_vacancy_missing_required_field(self):
        """Тест валидации вакансии без обязательного поля"""
        validator = VacancyValidator()
        
        mock_vacancy = MockVacancy(
            title="Python Developer",
            url="https://example.com/job/123"
            # Отсутствует vacancy_id
        )
        
        result = validator.validate_vacancy(mock_vacancy)
        assert result is False
        errors = validator.get_validation_errors()
        assert len(errors) > 0
        assert any("vacancy_id" in error for error in errors)

    def test_validate_vacancy_empty_required_field(self):
        """Тест валидации вакансии с пустым обязательным полем"""
        validator = VacancyValidator()
        
        mock_vacancy = MockVacancy(
            vacancy_id="",  # Пустой ID
            title="Python Developer",
            url="https://example.com/job/123"
        )
        
        result = validator.validate_vacancy(mock_vacancy)
        assert result is False
        errors = validator.get_validation_errors()
        assert any("пустое" in error for error in errors)

    def test_validate_vacancy_wrong_data_type(self):
        """Тест валидации вакансии с неверным типом данных"""
        validator = VacancyValidator()
        
        mock_vacancy = MockVacancy(
            vacancy_id=123,  # Должен быть str, а не int
            title="Python Developer",
            url="https://example.com/job/123"
        )
        
        result = validator.validate_vacancy(mock_vacancy)
        assert result is False
        errors = validator.get_validation_errors()
        assert any("Неверный тип" in error for error in errors)

    def test_validate_data_types_optional_wrong_type(self):
        """Тест валидации опциональных полей с неверным типом"""
        validator = VacancyValidator()
        
        mock_vacancy = MockVacancy(
            vacancy_id="123",
            title="Python Developer", 
            url="https://example.com/job/123",
            requirements=123  # Должен быть str или None, а не int
        )
        
        # Вызываем _validate_data_types напрямую для покрытия строки 99
        result = validator._validate_data_types(mock_vacancy)
        assert result is False
        errors = validator.get_validation_errors()
        assert any("requirements" in error and "Неверный тип" in error for error in errors)

    def test_validate_data_types_early_return(self):
        """Тест досрочного возврата в _validate_data_types при первой ошибке"""
        validator = VacancyValidator()
        
        # Создаем вакансию с несколькими неверными типами опциональных полей
        mock_vacancy = MockVacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://example.com/job/123", 
            requirements=123,  # Неверный тип - int вместо str/None
            responsibilities=456  # Тоже неверный тип
        )
        
        # Вызываем напрямую для покрытия строки 62 (return False)
        result = validator._validate_data_types(mock_vacancy)
        assert result is False
        
        # Проверяем что есть ошибки валидации
        errors = validator.get_validation_errors()
        assert len(errors) > 0

    def test_validate_vacancy_data_types_fail_main_method(self):
        """Тест покрытия строки 62 через основной метод validate_vacancy"""
        validator = VacancyValidator()
        
        # Создаем вакансию с валидными required полями, но неверными optional
        mock_vacancy = MockVacancy(
            vacancy_id="123",
            title="Python Developer", 
            url="https://example.com/job/123",
            requirements=999  # Неверный тип для опционального поля
        )
        
        # Этот вызов должен покрыть строку 62 при возврате False из _validate_data_types
        result = validator.validate_vacancy(mock_vacancy)
        assert result is False
        
        errors = validator.get_validation_errors()
        assert any("requirements" in error and "Неверный тип" in error for error in errors)

    def test_validate_vacancy_invalid_url(self):
        """Тест валидации вакансии с невалидным URL"""
        validator = VacancyValidator()
        
        mock_vacancy = MockVacancy(
            vacancy_id="123",
            title="Python Developer",
            url="invalid-url"  # Невалидный URL
        )
        
        result = validator.validate_vacancy(mock_vacancy)
        assert result is False
        errors = validator.get_validation_errors()
        assert any("URL" in error for error in errors)

    def test_validate_vacancy_long_id(self):
        """Тест валидации вакансии со слишком длинным ID"""
        validator = VacancyValidator()
        
        mock_vacancy = MockVacancy(
            vacancy_id="x" * 150,  # Слишком длинный ID
            title="Python Developer",
            url="https://example.com/job/123"
        )
        
        result = validator.validate_vacancy(mock_vacancy)
        assert result is False
        errors = validator.get_validation_errors()
        assert any("слишком длинный" in error for error in errors)

    def test_validate_vacancy_long_title(self):
        """Тест валидации вакансии со слишком длинным названием"""
        validator = VacancyValidator()
        
        mock_vacancy = MockVacancy(
            vacancy_id="123",
            title="x" * 600,  # Слишком длинное название
            url="https://example.com/job/123"
        )
        
        result = validator.validate_vacancy(mock_vacancy)
        assert result is False
        errors = validator.get_validation_errors()
        assert any("слишком длинное" in error for error in errors)

    def test_validate_vacancy_optional_fields(self):
        """Тест валидации вакансии с опциональными полями"""
        validator = VacancyValidator()
        
        mock_vacancy = MockVacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://example.com/job/123",
            description="Job description",
            requirements="Python, Django",
            responsibilities=None,  # None значение для опционального поля
            experience="3-5 лет"
        )
        
        result = validator.validate_vacancy(mock_vacancy)
        assert result is True

    def test_get_validation_errors(self):
        """Тест получения ошибок валидации"""
        validator = VacancyValidator()
        
        # Сначала проверим пустой список ошибок
        errors = validator.get_validation_errors()
        assert errors == []
        
        # Теперь создадим ошибки валидации
        mock_vacancy = MockVacancy(vacancy_id="")  # Пустой ID
        validator.validate_vacancy(mock_vacancy)
        
        errors = validator.get_validation_errors()
        assert len(errors) > 0
        assert isinstance(errors, list)

    def test_validate_batch_success(self):
        """Тест пакетной валидации успешных вакансий"""
        validator = VacancyValidator()
        
        vacancies = [
            MockVacancy(vacancy_id="1", title="Job 1", url="https://example.com/1"),
            MockVacancy(vacancy_id="2", title="Job 2", url="https://example.com/2")
        ]
        
        results = validator.validate_batch(vacancies)
        
        assert len(results) == 2
        assert results["1"] is True
        assert results["2"] is True

    def test_validate_batch_mixed_results(self):
        """Тест пакетной валидации с смешанными результатами"""
        validator = VacancyValidator()
        
        vacancies = [
            MockVacancy(vacancy_id="1", title="Job 1", url="https://example.com/1"),
            MockVacancy(vacancy_id="", title="Job 2", url="https://example.com/2")  # Невалидная
        ]
        
        with patch('src.storage.components.vacancy_validator.logger') as mock_logger:
            results = validator.validate_batch(vacancies)
        
        assert len(results) == 2
        assert results["1"] is True
        assert results[""] is False
        mock_logger.warning.assert_called()

    def test_validate_batch_exception_handling(self):
        """Тест обработки исключений в пакетной валидации"""
        validator = VacancyValidator()
        
        # Просто проверяем обработку исключений через мок метода validate_vacancy
        with patch.object(validator, 'validate_vacancy', side_effect=Exception("Validation error")):
            with patch('src.storage.components.vacancy_validator.logger') as mock_logger:
                mock_vacancy = MockVacancy(vacancy_id="123")
                results = validator.validate_batch([mock_vacancy])
        
        assert len(results) == 1
        assert results["123"] is False  # Получаем vacancy_id из mock_vacancy
        mock_logger.error.assert_called()


class TestStorageComponentsIntegration:
    """Интеграционные тесты storage components"""

    @patch('psycopg2.connect')
    def test_full_workflow_integration(self, mock_connect):
        """Тест полного workflow с компонентами storage"""
        # Настраиваем мок подключения
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        # Создаем компоненты
        db_conn = DatabaseConnection({"host": "test"})
        validator = VacancyValidator()
        repo = VacancyRepository(db_conn, validator)
        
        # Создаем тестовую вакансию
        mock_vacancy = MockVacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://example.com/job/123",
            salary=None
        )
        
        # Мокируем контекст менеджер для подключения
        with patch.object(db_conn, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__ = Mock(return_value=mock_connection)
            mock_get_conn.return_value.__exit__ = Mock(return_value=False)
            
            # Выполняем валидацию и сохранение
            is_valid = validator.validate_vacancy(mock_vacancy)
            assert is_valid is True
            
            repo.add_vacancy(mock_vacancy)
            
            # Проверяем что все прошло успешно
            mock_cursor.execute.assert_called()

    def test_validation_integration_with_errors(self):
        """Тест интеграции валидации с ошибками"""
        validator = VacancyValidator()
        
        # Невалидная вакансия
        invalid_vacancy = MockVacancy(
            vacancy_id="",  # Пустой ID
            title=None,     # None title
            url="invalid-url"  # Невалидный URL
        )
        
        # Валидируем
        is_valid = validator.validate_vacancy(invalid_vacancy)
        
        # Получаем детальные ошибки
        errors = validator.get_validation_errors()
        
        assert is_valid is False
        assert len(errors) > 0
        
        # Проверяем что репозиторий не сохранит невалидные данные
        mock_db_conn = Mock()
        repo = VacancyRepository(mock_db_conn, validator)
        
        if not is_valid:
            with pytest.raises(ValueError):
                repo.add_vacancy(invalid_vacancy)

    def test_database_connection_context_usage(self):
        """Тест использования подключения как контекст менеджера"""
        db_conn = DatabaseConnection({"host": "test"})
        
        with patch.object(db_conn, 'get_connection') as mock_get_conn:
            with patch.object(db_conn, 'close_connection') as mock_close:
                mock_connection = Mock()
                mock_get_conn.return_value = mock_connection
                
                # Используем как контекст менеджер
                with db_conn as conn:
                    assert conn == mock_connection
                
                mock_close.assert_called_once()

    def test_validator_with_repository_integration(self):
        """Тест интеграции валидатора с репозиторием"""
        mock_db_conn = Mock()
        validator = VacancyValidator()
        repo = VacancyRepository(mock_db_conn, validator)
        
        # Создаем корректную вакансию
        valid_vacancy = MockVacancy(
            vacancy_id="valid_123",
            title="Senior Python Developer",
            url="https://company.com/jobs/123",
            salary=None  # Добавляем атрибут salary
        )
        
        # Создаем некорректную вакансию
        invalid_vacancy = MockVacancy(
            vacancy_id="",
            title="Job",
            url="bad-url",
            salary=None  # Добавляем атрибут salary
        )
        
        # Тестируем что репозиторий использует валидатор
        with patch.object(repo, '_db_connection') as mock_db:
            mock_conn = Mock()
            mock_db.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
            mock_db.get_connection.return_value.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=Mock())
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            
            # Корректная вакансия должна пройти
            try:
                repo.add_vacancy(valid_vacancy)
                success = True
            except ValueError:
                success = False
            
            assert success is True
            
            # Некорректная вакансия должна вызвать исключение
            with pytest.raises(ValueError):
                repo.add_vacancy(invalid_vacancy)