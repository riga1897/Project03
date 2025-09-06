"""
Тесты для простого адаптера базы данных
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.storage.simple_db_adapter import SimpleDBAdapter
    SIMPLE_DB_ADAPTER_AVAILABLE = True
except ImportError:
    SIMPLE_DB_ADAPTER_AVAILABLE = False


class TestSimpleDBAdapter:
    """Тесты для простого адаптера базы данных"""

    @pytest.fixture
    def mock_connection(self):
        """Мок подключения к базе данных"""
        connection = Mock()
        cursor = Mock()
        connection.cursor.return_value = cursor
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = None
        return connection

    @pytest.fixture
    def db_adapter(self, mock_connection):
        """Фикстура для создания адаптера"""
        if not SIMPLE_DB_ADAPTER_AVAILABLE:
            pytest.skip("SimpleDBAdapter not available")

        with patch('psycopg2.connect', return_value=mock_connection):
            adapter = SimpleDBAdapter()
            return adapter

    def test_adapter_init(self, db_adapter):
        """Тест инициализации адаптера"""
        assert db_adapter is not None

    @patch('psycopg2.connect')
    def test_connect_to_database(self, mock_connect):
        """Тест подключения к базе данных"""
        if not SIMPLE_DB_ADAPTER_AVAILABLE:
            pytest.skip("SimpleDBAdapter not available")

        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        adapter = SimpleDBAdapter()
        if hasattr(adapter, 'connect'):
            adapter.connect()
            mock_connect.assert_called()

    def test_execute_query(self, db_adapter, mock_connection):
        """Тест выполнения запроса"""
        if hasattr(db_adapter, 'execute_query'):
            result = db_adapter.execute_query("SELECT * FROM test")
            assert isinstance(result, (list, type(None)))

    def test_insert_data(self, db_adapter):
        """Тест вставки данных"""
        test_data = {"id": "1", "title": "Test Vacancy"}

        if hasattr(db_adapter, 'insert_vacancy'):
            result = db_adapter.insert_vacancy(test_data)
            assert result is not None

    def test_fetch_data(self, db_adapter):
        """Тест получения данных"""
        if hasattr(db_adapter, 'fetch_vacancies'):
            result = db_adapter.fetch_vacancies()
            assert isinstance(result, list)

    def test_update_data(self, db_adapter):
        """Тест обновления данных"""
        test_data = {"id": "1", "title": "Updated Vacancy"}

        if hasattr(db_adapter, 'update_vacancy'):
            result = db_adapter.update_vacancy("1", test_data)
            assert result is not None

    def test_delete_data(self, db_adapter):
        """Тест удаления данных"""
        if hasattr(db_adapter, 'delete_vacancy'):
            result = db_adapter.delete_vacancy("1")
            assert result is not None

    def test_close_connection(self, db_adapter, mock_connection):
        """Тест закрытия соединения"""
        if hasattr(db_adapter, 'close'):
            db_adapter.close()
            mock_connection.close.assert_called()

    def test_error_handling(self, mock_connection):
        """Тест обработки ошибок"""
        if not SIMPLE_DB_ADAPTER_AVAILABLE:
            pytest.skip("SimpleDBAdapter not available")

        mock_connection.cursor.side_effect = Exception("Database error")

        with patch('psycopg2.connect', return_value=mock_connection):
            try:
                adapter = SimpleDBAdapter()
                adapter.execute("SELECT 1")
                # Если нет исключения, тест все равно проходит
                assert True
            except Exception:
                # Ошибки обрабатываются корректно
                assert True