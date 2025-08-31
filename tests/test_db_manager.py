` tags.

<replit_final_file>
import os
import sys
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.storage.db_manager import DBManager


class MockCursor:
    """Мок курсора базы данных"""

    def __init__(self):
        self.results = []
        self.executed_queries = []

    def execute(self, query, params=None):
        """Мок выполнения запроса"""
        self.executed_queries.append((query, params))

    def fetchone(self):
        """Мок получения одной записи"""
        return ("integer",) if self.results else None

    def fetchall(self):
        """Мок получения всех записей"""
        return self.results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockConnection:
    """Мок соединения с базой данных"""

    def __init__(self):
        self.cursor_mock = MockCursor()
        self.closed = False

    def cursor(self):
        """Возвращает мок курсора"""
        return self.cursor_mock

    def commit(self):
        """Мок коммита"""
        pass

    def rollback(self):
        """Мок отката"""
        pass

    def close(self):
        """Мок закрытия соединения"""
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class TestDBManager:
    """Тесты для DBManager"""

    @patch("src.storage.db_manager.psycopg2.connect")
    def test_db_manager_initialization(self, mock_connect):
        """Тест инициализации DBManager"""
        mock_connection = MockConnection()
        mock_connect.return_value = mock_connection

        db_manager = DBManager()
        assert db_manager is not None

    @patch("src.storage.db_manager.psycopg2.connect")
    def test_check_connection_success(self, mock_connect):
        """Тест успешной проверки соединения"""
        mock_connection = MockConnection()
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Мокируем get_database_version для возврата валидной версии
        with patch.object(db_manager, 'get_database_version', return_value="PostgreSQL 13.0"):
            result = db_manager.check_connection()
            assert result is True

    @patch("src.storage.db_manager.psycopg2.connect")
    def test_create_tables(self, mock_connect):
        """Тест создания таблиц"""
        mock_connection = MockConnection()
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Настраиваем курсор для возврата правильного типа данных
        mock_connection.cursor_mock.results = []

        with patch.object(db_manager, "_get_connection", return_value=mock_connection):
            db_manager.create_tables()

        # Проверяем, что запросы были выполнены
        assert len(mock_connection.cursor_mock.executed_queries) > 0

    @patch("src.storage.db_manager.psycopg2.connect")
    def test_get_database_stats(self, mock_connect):
        """Тест получения статистики базы данных"""
        mock_connection = MockConnection()
        mock_connection.cursor_mock.results = [(100, 50)]
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        with patch.object(db_manager, "_get_connection", return_value=mock_connection):
            result = db_manager.get_database_stats()

        assert isinstance(result, dict)
        assert "companies_count" in result
        assert "vacancies_count" in result

    @patch("src.storage.db_manager.psycopg2.connect")
    def test_get_companies_and_vacancies_count(self, mock_connect):
        """Тест получения количества компаний и вакансий"""
        mock_connection = MockConnection()
        mock_connection.cursor_mock.results = [
            ("Test Company 1", 10),
            ("Test Company 2", 5)
        ]
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        with patch.object(db_manager, "_get_connection", return_value=mock_connection):
            result = db_manager.get_companies_and_vacancies_count()

        assert isinstance(result, list)

    @patch("src.storage.db_manager.psycopg2.connect")
    def test_get_vacancies_with_higher_salary(self, mock_connect):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_connection = MockConnection()
        mock_connection.cursor_mock.results = [
            ("124", "Senior Python Developer", "Test Company", 200000, "Москва", "https://test.com")
        ]
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        with patch.object(db_manager, "_get_connection", return_value=mock_connection):
            with patch.object(db_manager, "create_tables"):
                result = db_manager.get_vacancies_with_higher_salary()

        assert len(result) == 1

    @patch("src.storage.db_manager.psycopg2.connect")
    def test_populate_companies_table(self, mock_connect):
        """Тест заполнения таблицы компаний"""
        mock_connection = MockConnection()
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Создаем тестовую функцию для получения целевых компаний
        def mock_get_target_companies():
            return [{"id": "1", "name": "Test Company 1"}, {"id": "2", "name": "Test Company 2"}]

        with patch.object(db_manager, "_get_connection", return_value=mock_connection):
            with patch("src.config.target_companies.get_target_companies", mock_get_target_companies):
                db_manager.populate_companies_table()

        # Проверяем, что запросы были выполнены
        assert len(mock_connection.cursor_mock.executed_queries) > 0

    @patch("src.storage.db_manager.psycopg2.connect")
    def test_connection_error_handling(self, mock_connect):
        """Тест обработки ошибок соединения"""
        mock_connect.side_effect = Exception("Connection failed")

        db_manager = DBManager()
        result = db_manager.check_connection()

        assert result is False