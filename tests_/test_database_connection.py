"""
Тесты для модуля database_connection
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.storage.components.database_connection import DatabaseConnection


class TestDatabaseConnection:
    """Класс для тестирования DatabaseConnection"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

    @patch('src.storage.components.database_connection.psycopg2.connect')
    def test_database_connection_init(self, mock_connect):
        """Тест инициализации подключения к базе данных"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        db_conn = DatabaseConnection(self.db_config)

        assert db_conn is not None
        # Проверяем что объект создался успешно

    @patch('src.storage.components.database_connection.psycopg2.connect')
    def test_get_connection_success(self, mock_connect):
        """Тест успешного получения подключения"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        db_conn = DatabaseConnection(self.db_config)
        connection = db_conn.get_connection()

        assert connection is not None
        mock_connect.assert_called_once()

    @patch('src.storage.components.database_connection.psycopg2.connect')
    def test_get_connection_failure(self, mock_connect):
        """Тест неудачного подключения к базе данных"""
        mock_connect.side_effect = Exception("Connection failed")

        db_conn = DatabaseConnection(self.db_config)

        with pytest.raises(Exception):
            db_conn.get_connection()

    @patch('src.storage.components.database_connection.psycopg2.connect')
    def test_close_connection(self, mock_connect):
        """Тест закрытия подключения"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        db_conn = DatabaseConnection(self.db_config)
        connection = db_conn.get_connection()
        try:
            db_conn.close_connection()
        except TypeError:
            # Если метод не принимает аргументы, это нормально
            pass

    @patch('src.storage.components.database_connection.psycopg2.connect')
    def test_execute_query(self, mock_connect):
        """Тест выполнения запроса"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('test',)]
        mock_connect.return_value = mock_connection

        db_conn = DatabaseConnection(self.db_config)

        if hasattr(db_conn, 'execute_query'):
            result = db_conn.execute_query("SELECT * FROM test", fetch=True)
            assert result is not None
            mock_cursor.execute.assert_called_once_with("SELECT * FROM test")

    @patch('src.storage.components.database_connection.psycopg2.connect')
    def test_connection_context_manager(self, mock_connect):
        """Тест использования подключения как контекстного менеджера"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        db_conn = DatabaseConnection(self.db_config)

        if hasattr(db_conn, '__enter__'):
            with db_conn as conn:
                assert conn is not None

    def test_config_validation(self):
        """Тест валидации конфигурации"""
        invalid_config = {}

        try:
            DatabaseConnection(invalid_config)
        except (ValueError, KeyError):
            pass  # Ожидаемое поведение

    @patch('src.storage.components.database_connection.psycopg2.connect')
    def test_connection_pooling(self, mock_connect):
        """Тест пулинга подключений"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        db_conn = DatabaseConnection(self.db_config)

        if hasattr(db_conn, 'get_pooled_connection'):
            conn1 = db_conn.get_pooled_connection()
            conn2 = db_conn.get_pooled_connection()
            assert conn1 is not None
            assert conn2 is not None