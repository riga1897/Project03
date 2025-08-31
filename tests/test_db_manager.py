import pytest
from unittest.mock import Mock, patch, MagicMock, create_autospec
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.db_manager import DBManager


class MockConnection:
    """Мок соединения с БД с поддержкой контекстного менеджера"""

    def __init__(self):
        self.cursor_mock = Mock()
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def cursor(self):
        return MockCursor()

    def commit(self):
        pass

    def close(self):
        self.closed = True

    def set_client_encoding(self, encoding):
        """Метод для установки кодировки клиента"""
        pass

    def autocommit(self):
        """Свойство автокоммита"""
        return True


class MockCursor:
    """Мок курсора с поддержкой контекстного менеджера"""

    def __init__(self):
        self.executed_queries = []
        self.fetch_data = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def execute(self, query, params=None):
        self.executed_queries.append((query, params))

    def fetchall(self):
        return self.fetch_data

    def fetchone(self):
        return self.fetch_data[0] if self.fetch_data else None


class TestDBManager:
    """Тесты для DBManager с консолидированными моками"""

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_check_connection_success(self, mock_connect):
        """Тест успешной проверки соединения"""
        mock_connection = MockConnection()
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Мокаем метод проверки соединения
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.check_connection()
            assert result is True

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_create_tables(self, mock_connect):
        """Тест создания таблиц"""
        mock_connection = MockConnection()
        mock_connect.return_value = mock_connection

        db_manager = DBManager()
        # Мокаем метод обеспечения существования таблиц
        with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
             with patch.object(db_manager, '_get_connection', return_value=mock_connection):
                db_manager.create_tables()

        # Проверяем что соединение было установлено
        mock_connect.assert_called()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_companies_and_vacancies_count(self, mock_connect):
        """Тест получения количества компаний и вакансий"""
        mock_connection = MockConnection()
        mock_cursor = mock_connection.cursor()
        mock_cursor.fetch_data = [
            ("Test Company", 5),
            ("Another Company", 3)
        ]
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Мокаем check_connection чтобы вернуть True
        with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
            with patch.object(db_manager, '_get_connection', return_value=mock_connection):
                result = db_manager.get_companies_and_vacancies_count()

        assert isinstance(result, list)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_all_vacancies(self, mock_connect):
        """Тест получения всех вакансий"""
        mock_connection = MockConnection()
        mock_cursor = mock_connection.cursor()
        mock_cursor.fetch_data = [
            ("123", "Python Developer", "Test Company", 100000, "Москва", "https://test.com")
        ]
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Мокаем check_connection и create_tables
        with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
            with patch.object(db_manager, '_get_connection', return_value=mock_connection):
                result = db_manager.get_all_vacancies()

        assert isinstance(result, list)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_avg_salary(self, mock_connect):
        """Тест получения средней зарплаты"""
        mock_connection = MockConnection()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (125000.0,)

        # Правильный мок для курсора как контекстного менеджера
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Мокаем соединение
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.get_avg_salary()

        assert result == 125000.0

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_connection = MockConnection()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("124", "Senior Python Developer", "Test Company", 200000, "Москва", "https://test.com")
        ]

        # Правильный мок для курсора как контекстного менеджера
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Мокаем соединение
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.get_vacancies_with_higher_salary()

        assert len(result) == 1
        assert result[0][0] == "124"

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_keyword(self, mock_connect):
        """Тест получения вакансий по ключевому слову"""
        mock_connection = MockConnection()
        mock_cursor = mock_connection.cursor()
        mock_cursor.fetch_data = [
            ("123", "Python Developer", "Test Company", 100000, "Москва", "https://test.com")
        ]
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Мокаем check_connection и create_tables
        with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
            with patch.object(db_manager, '_get_connection', return_value=mock_connection):
                result = db_manager.get_vacancies_with_keyword("Python")

        assert isinstance(result, list)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_populate_companies_table(self, mock_connect):
        """Тест заполнения таблицы компаний"""
        mock_connection = MockConnection()
        mock_connect.return_value = mock_connection

        db_manager = DBManager()

        # Мокаем функцию получения целевых компаний
        test_companies = [
            {"id": "1", "name": "Test Company 1"},
            {"id": "2", "name": "Test Company 2"}
        ]

        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            # Мокаем функцию получения целевых компаний
            with patch('src.config.target_companies.get_target_companies_data', return_value=test_companies):
                db_manager.populate_companies_table()

        # Проверяем что соединение было установлено
        mock_connect.assert_called()