import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.db_manager import DBManager


class TestDBManager:
    """Тесты для DBManager"""

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_db_manager_initialization(self, mock_connect):
        """Тест инициализации DBManager"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_connection

        db_manager = DBManager()
        assert isinstance(db_manager, DBManager)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_check_connection_success(self, mock_connect):
        """Тест успешной проверки соединения"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_connection

        db_manager = DBManager()
        result = db_manager.check_connection()

        assert result is True
        mock_cursor.execute.assert_called()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_check_connection_failure(self, mock_connect):
        """Тест неудачной проверки соединения"""
        mock_connect.side_effect = Exception("Connection failed")

        db_manager = DBManager()
        result = db_manager.check_connection()

        assert result is False

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_create_tables(self, mock_connect):
        """Тест создания таблиц"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_connection

        db_manager = DBManager()
        db_manager.create_tables()

        # Проверяем, что SQL для создания таблиц был выполнен
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_companies_and_vacancies_count(self, mock_connect):
        """Тест получения количества компаний и вакансий"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_connection

        # Настраиваем возвращаемые данные
        mock_cursor.fetchall.return_value = [
            ("Test Company", 5),
            ("Another Company", 3)
        ]

        db_manager = DBManager()
        result = db_manager.get_companies_and_vacancies_count()

        assert isinstance(result, list)
        assert len(result) == 2
        mock_cursor.execute.assert_called()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_all_vacancies(self, mock_connect):
        """Тест получения всех вакансий"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_connection

        # Настраиваем возвращаемые данные
        mock_cursor.fetchall.return_value = [
            ("123", "Python Developer", "Test Company", 100000, "Москва", "https://test.com")
        ]

        db_manager = DBManager()
        result = db_manager.get_all_vacancies()

        assert isinstance(result, list)
        mock_cursor.execute.assert_called()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_avg_salary(self, mock_connect):
        """Тест получения средней зарплаты"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_connection

        # Настраиваем возвращаемые данные
        mock_cursor.fetchone.return_value = (125000.0,)

        db_manager = DBManager()
        result = db_manager.get_avg_salary()

        assert result == 125000.0
        mock_cursor.execute.assert_called()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_connection

        # Настраиваем возвращаемые данные
        mock_cursor.fetchall.return_value = [
            ("124", "Senior Python Developer", "Test Company", 200000, "Москва", "https://test.com")
        ]

        db_manager = DBManager()
        result = db_manager.get_vacancies_with_higher_salary()

        assert isinstance(result, list)
        mock_cursor.execute.assert_called()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_keyword(self, mock_connect):
        """Тест получения вакансий по ключевому слову"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_connection

        # Настраиваем возвращаемые данные
        mock_cursor.fetchall.return_value = [
            ("123", "Python Developer", "Test Company", 100000, "Москва", "https://test.com")
        ]

        db_manager = DBManager()
        result = db_manager.get_vacancies_with_keyword("Python")

        assert isinstance(result, list)
        mock_cursor.execute.assert_called()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_populate_companies_table(self, mock_connect):
        """Тест заполнения таблицы компаний"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_connection

        db_manager = DBManager()
        db_manager.populate_companies_table()

        # Проверяем, что SQL для вставки был выполнен
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()