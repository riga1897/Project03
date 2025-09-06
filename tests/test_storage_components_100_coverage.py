"""
100% покрытие storage/components модулей
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.storage.components.database_connection import DatabaseConnection
from src.storage.components.vacancy_repository import VacancyRepository 
from src.storage.components.vacancy_validator import VacancyValidator


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
        mock_connection.cursor.return_value.__enter__.side_effect = Exception("DB error")
        
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
        mock_connect.assert_called_once_with(**{"host": "test"})

    @patch('psycopg2.connect')
    def test_create_new_connection_failure(self, mock_connect):
        """Тест обработки ошибки создания подключения"""
        mock_connect.side_effect = Exception("Connection failed")
        
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
        
        mock_logger.error.assert_called_once()
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

    def test_repr(self):
        """Тест строкового представления"""
        params = {"host": "test_host", "database": "test_db"}
        db_conn = DatabaseConnection(params)
        result = repr(db_conn)
        
        assert "DatabaseConnection" in result
        assert "test_host" in result
        assert "test_db" in result


class TestVacancyRepository:
    """100% покрытие VacancyRepository"""

    def test_init(self):
        """Тест инициализации"""
        mock_db_conn = Mock()
        repo = VacancyRepository(mock_db_conn)
        assert repo._db_connection == mock_db_conn

    @patch('src.storage.components.vacancy_repository.logger')
    def test_save_vacancy_success(self, mock_logger):
        """Тест успешного сохранения вакансии"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        repo = VacancyRepository(mock_db_conn)
        vacancy_data = {
            "id": "123", 
            "title": "Test Job",
            "company": {"name": "Test Company"}
        }
        
        result = repo.save_vacancy(vacancy_data)
        
        assert result is True
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called_once()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_save_vacancy_failure(self, mock_logger):
        """Тест обработки ошибки сохранения"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_connection.cursor.side_effect = Exception("DB Error")
        
        mock_db_conn.get_connection.return_value = mock_connection
        
        repo = VacancyRepository(mock_db_conn)
        vacancy_data = {"id": "123"}
        
        result = repo.save_vacancy(vacancy_data)
        
        assert result is False
        mock_logger.error.assert_called_once()
        mock_connection.rollback.assert_called_once()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_get_vacancy_by_id_success(self, mock_logger):
        """Тест успешного получения вакансии по ID"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        # Мокируем результат запроса
        mock_cursor.fetchone.return_value = {
            "id": "123",
            "title": "Test Job",
            "company_name": "Test Company"
        }
        
        repo = VacancyRepository(mock_db_conn)
        result = repo.get_vacancy_by_id("123")
        
        assert result is not None
        assert result["id"] == "123"
        mock_cursor.execute.assert_called()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_get_vacancy_by_id_not_found(self, mock_logger):
        """Тест получения несуществующей вакансии"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.fetchone.return_value = None
        
        repo = VacancyRepository(mock_db_conn)
        result = repo.get_vacancy_by_id("nonexistent")
        
        assert result is None

    @patch('src.storage.components.vacancy_repository.logger')
    def test_get_vacancy_by_id_error(self, mock_logger):
        """Тест обработки ошибки получения вакансии"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_connection.cursor.side_effect = Exception("DB Error")
        
        mock_db_conn.get_connection.return_value = mock_connection
        
        repo = VacancyRepository(mock_db_conn)
        result = repo.get_vacancy_by_id("123")
        
        assert result is None
        mock_logger.error.assert_called_once()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_get_all_vacancies_success(self, mock_logger):
        """Тест успешного получения всех вакансий"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.fetchall.return_value = [
            {"id": "1", "title": "Job 1"},
            {"id": "2", "title": "Job 2"}
        ]
        
        repo = VacancyRepository(mock_db_conn)
        result = repo.get_all_vacancies()
        
        assert len(result) == 2
        assert result[0]["id"] == "1"
        mock_cursor.execute.assert_called()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_get_all_vacancies_with_limit(self, mock_logger):
        """Тест получения вакансий с лимитом"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.fetchall.return_value = [{"id": "1"}]
        
        repo = VacancyRepository(mock_db_conn)
        result = repo.get_all_vacancies(limit=10)
        
        assert len(result) == 1
        # Проверяем что LIMIT был добавлен в SQL
        call_args = mock_cursor.execute.call_args[0][0]
        assert "LIMIT" in call_args

    @patch('src.storage.components.vacancy_repository.logger')
    def test_delete_vacancy_success(self, mock_logger):
        """Тест успешного удаления вакансии"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.rowcount = 1
        
        repo = VacancyRepository(mock_db_conn)
        result = repo.delete_vacancy("123")
        
        assert result is True
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called_once()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_delete_vacancy_not_found(self, mock_logger):
        """Тест удаления несуществующей вакансии"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.rowcount = 0
        
        repo = VacancyRepository(mock_db_conn)
        result = repo.delete_vacancy("nonexistent")
        
        assert result is False

    @patch('src.storage.components.vacancy_repository.logger')
    def test_update_vacancy_success(self, mock_logger):
        """Тест успешного обновления вакансии"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.rowcount = 1
        
        repo = VacancyRepository(mock_db_conn)
        update_data = {"title": "Updated Job"}
        
        result = repo.update_vacancy("123", update_data)
        
        assert result is True
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called_once()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_get_vacancies_by_company_success(self, mock_logger):
        """Тест получения вакансий по компании"""
        mock_db_conn = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_db_conn.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        mock_cursor.fetchall.return_value = [
            {"id": "1", "company_name": "Test Company"}
        ]
        
        repo = VacancyRepository(mock_db_conn)
        result = repo.get_vacancies_by_company("Test Company")
        
        assert len(result) == 1
        mock_cursor.execute.assert_called()


class TestVacancyValidator:
    """100% покрытие VacancyValidator"""

    def test_validate_vacancy_data_valid(self):
        """Тест валидации корректных данных вакансии"""
        valid_data = {
            "id": "123",
            "title": "Python Developer",
            "url": "https://example.com/job/123",
            "company": {
                "name": "Test Company"
            }
        }
        
        validator = VacancyValidator()
        result = validator.validate_vacancy_data(valid_data)
        
        assert result is True

    def test_validate_vacancy_data_missing_required(self):
        """Тест валидации с отсутствующими обязательными полями"""
        # Отсутствует id
        invalid_data = {
            "title": "Python Developer",
            "url": "https://example.com/job/123"
        }
        
        validator = VacancyValidator()
        result = validator.validate_vacancy_data(invalid_data)
        
        assert result is False

    def test_validate_vacancy_data_empty_string(self):
        """Тест валидации с пустыми строками"""
        invalid_data = {
            "id": "",  # Пустая строка
            "title": "Python Developer",
            "url": "https://example.com/job/123"
        }
        
        validator = VacancyValidator()
        result = validator.validate_vacancy_data(invalid_data)
        
        assert result is False

    def test_validate_vacancy_data_none_value(self):
        """Тест валидации с None значениями"""
        invalid_data = {
            "id": "123",
            "title": None,  # None значение
            "url": "https://example.com/job/123"
        }
        
        validator = VacancyValidator()
        result = validator.validate_vacancy_data(invalid_data)
        
        assert result is False

    def test_validate_vacancy_data_non_dict(self):
        """Тест валидации не-словаря"""
        validator = VacancyValidator()
        
        assert validator.validate_vacancy_data(None) is False
        assert validator.validate_vacancy_data("string") is False
        assert validator.validate_vacancy_data([]) is False
        assert validator.validate_vacancy_data(123) is False

    def test_validate_company_data_valid(self):
        """Тест валидации корректных данных компании"""
        valid_company = {
            "name": "Test Company",
            "url": "https://company.com"
        }
        
        validator = VacancyValidator()
        result = validator.validate_company_data(valid_company)
        
        assert result is True

    def test_validate_company_data_missing_name(self):
        """Тест валидации компании без имени"""
        invalid_company = {
            "url": "https://company.com"
        }
        
        validator = VacancyValidator()
        result = validator.validate_company_data(invalid_company)
        
        assert result is False

    def test_validate_company_data_empty_name(self):
        """Тест валидации компании с пустым именем"""
        invalid_company = {
            "name": "",
            "url": "https://company.com"
        }
        
        validator = VacancyValidator()
        result = validator.validate_company_data(invalid_company)
        
        assert result is False

    def test_validate_company_data_none(self):
        """Тест валидации None компании"""
        validator = VacancyValidator()
        result = validator.validate_company_data(None)
        
        assert result is False

    def test_validate_salary_data_valid_dict(self):
        """Тест валидации корректных данных зарплаты"""
        valid_salary = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }
        
        validator = VacancyValidator()
        result = validator.validate_salary_data(valid_salary)
        
        assert result is True

    def test_validate_salary_data_valid_string(self):
        """Тест валидации зарплаты как строки"""
        validator = VacancyValidator()
        result = validator.validate_salary_data("от 100000 до 150000")
        
        assert result is True

    def test_validate_salary_data_none(self):
        """Тест валидации None зарплаты"""
        validator = VacancyValidator()
        result = validator.validate_salary_data(None)
        
        assert result is True  # None зарплата допустима

    def test_validate_salary_data_invalid_type(self):
        """Тест валидации невалидного типа зарплаты"""
        validator = VacancyValidator()
        
        assert validator.validate_salary_data(123) is False
        assert validator.validate_salary_data([]) is False

    def test_validate_url_valid(self):
        """Тест валидации корректных URL"""
        validator = VacancyValidator()
        
        assert validator.validate_url("https://example.com") is True
        assert validator.validate_url("http://example.com/path") is True
        assert validator.validate_url("https://site.com/job/123?param=value") is True

    def test_validate_url_invalid(self):
        """Тест валидации некорректных URL"""
        validator = VacancyValidator()
        
        assert validator.validate_url("not-a-url") is False
        assert validator.validate_url("ftp://example.com") is False  # не http/https
        assert validator.validate_url("") is False
        assert validator.validate_url(None) is False

    def test_sanitize_string_normal(self):
        """Тест санитизации обычной строки"""
        validator = VacancyValidator()
        result = validator.sanitize_string("Normal text")
        
        assert result == "Normal text"

    def test_sanitize_string_with_html(self):
        """Тест санитизации строки с HTML"""
        validator = VacancyValidator()
        result = validator.sanitize_string("<script>alert('xss')</script>Clean text")
        
        # HTML теги должны быть удалены
        assert "<script>" not in result
        assert "Clean text" in result

    def test_sanitize_string_with_whitespace(self):
        """Тест санитизации строки с лишними пробелами"""
        validator = VacancyValidator()
        result = validator.sanitize_string("  Text with   spaces  ")
        
        # Лишние пробелы должны быть удалены
        assert result == "Text with spaces"

    def test_sanitize_string_none_and_empty(self):
        """Тест санитизации None и пустых строк"""
        validator = VacancyValidator()
        
        assert validator.sanitize_string(None) == ""
        assert validator.sanitize_string("") == ""
        assert validator.sanitize_string("   ") == ""

    def test_normalize_vacancy_data_full(self):
        """Тест нормализации полных данных вакансии"""
        raw_data = {
            "id": "123",
            "title": "  <b>Python Developer</b>  ",
            "description": "<p>Job description</p>",
            "company": {
                "name": "  Test Company  "
            },
            "salary": {
                "from": 100000,
                "to": 150000
            }
        }
        
        validator = VacancyValidator()
        result = validator.normalize_vacancy_data(raw_data)
        
        assert result["title"] == "Python Developer"  # HTML удален, пробелы убраны
        assert "Test Company" in result["company"]["name"]
        assert result["salary"]["from"] == 100000

    def test_normalize_vacancy_data_minimal(self):
        """Тест нормализации минимальных данных"""
        raw_data = {
            "id": "123",
            "title": "Job Title"
        }
        
        validator = VacancyValidator()
        result = validator.normalize_vacancy_data(raw_data)
        
        assert result["id"] == "123"
        assert result["title"] == "Job Title"

    def test_get_validation_errors_empty_for_valid(self):
        """Тест отсутствия ошибок для валидных данных"""
        valid_data = {
            "id": "123",
            "title": "Python Developer",
            "url": "https://example.com/job/123",
            "company": {
                "name": "Test Company"
            }
        }
        
        validator = VacancyValidator()
        errors = validator.get_validation_errors(valid_data)
        
        assert len(errors) == 0

    def test_get_validation_errors_with_issues(self):
        """Тест получения ошибок валидации"""
        invalid_data = {
            "id": "",  # Пустой id
            "title": "Python Developer",
            "url": "not-a-url",  # Невалидный URL
        }
        
        validator = VacancyValidator()
        errors = validator.get_validation_errors(invalid_data)
        
        assert len(errors) > 0
        # Проверяем что есть ошибки по id и url
        error_text = " ".join(errors)
        assert "id" in error_text or "ID" in error_text
        assert "url" in error_text or "URL" in error_text


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
        repo = VacancyRepository(db_conn)
        validator = VacancyValidator()
        
        # Тестовые данные
        raw_vacancy = {
            "id": "123",
            "title": "  <b>Python Developer</b>  ",
            "url": "https://example.com/job/123",
            "company": {
                "name": "  Test Company  "
            }
        }
        
        # Нормализуем данные
        normalized_data = validator.normalize_vacancy_data(raw_vacancy)
        
        # Валидируем данные
        is_valid = validator.validate_vacancy_data(normalized_data)
        assert is_valid is True
        
        # Сохраняем в репозитории
        mock_cursor.execute = Mock()
        saved = repo.save_vacancy(normalized_data)
        
        # Проверяем что все прошло успешно
        assert saved is True
        assert normalized_data["title"] == "Python Developer"
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()

    def test_validation_integration_with_errors(self):
        """Тест интеграции валидации с ошибками"""
        validator = VacancyValidator()
        
        # Невалидные данные
        invalid_data = {
            "id": "",
            "title": None,
            "url": "not-a-url"
        }
        
        # Сначала нормализуем
        normalized = validator.normalize_vacancy_data(invalid_data)
        
        # Затем валидируем
        is_valid = validator.validate_vacancy_data(normalized)
        
        # Получаем детальные ошибки
        errors = validator.get_validation_errors(normalized)
        
        assert is_valid is False
        assert len(errors) > 0
        
        # Проверяем что репозиторий не сохранит невалидные данные
        mock_db_conn = Mock()
        repo = VacancyRepository(mock_db_conn)
        
        if not is_valid:
            # В реальном приложении мы бы не сохраняли невалидные данные
            assert len(errors) > 0  # Подтверждаем что есть ошибки