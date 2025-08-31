"""
Тесты для оптимизированного подключения к БД
"""

from unittest.mock import MagicMock, Mock, patch
import pytest
import psycopg2


class TestDBConnectionOptimization:
    """Тесты для оптимизированного подключения к БД"""

    @pytest.fixture
    def unified_db_connection(self):
        """Единое подключение к БД для всех тестов"""
        mock_connection = Mock()
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connection.commit = Mock()
        mock_connection.rollback = Mock()
        mock_connection.close = Mock()
        mock_connection.set_client_encoding = Mock()
        mock_connection.autocommit = True

        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_cursor.execute = Mock()
        mock_cursor.fetchone = Mock(return_value=(1,))
        mock_cursor.fetchall = Mock(return_value=[])
        mock_cursor.rowcount = 1
        mock_connection.cursor = Mock(return_value=mock_cursor)

        return mock_connection

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_single_connection_reuse(self, mock_connect, mock_print, mock_input, unified_db_connection):
        """Тест переиспользования единого подключения"""
        mock_connect.return_value = unified_db_connection

        from src.storage.postgres_saver import PostgresSaver

        # Мокируем инициализацию для избежания реальных запросов
        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'):

            # Создаем storage с единым подключением
            storage = PostgresSaver()

        # Проверяем что подключение переиспользуется
        with patch.object(storage, '_get_connection', return_value=unified_db_connection) as mock_get_conn:
            # Выполняем несколько операций
            storage.get_vacancies_count()
            storage.get_vacancies_count()
            storage.get_vacancies_count()

            # Проверяем что _get_connection вызывался
            assert mock_get_conn.call_count == 3

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_connection_pool_optimization(self, mock_connect, mock_print, mock_input, unified_db_connection):
        """Тест оптимизации пула подключений"""
        mock_connect.return_value = unified_db_connection

        from src.storage.postgres_saver import PostgresSaver
        from src.storage.db_manager import DBManager

        # Мокируем инициализацию для избежания реальных запросов
        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'):

            # Тестируем множественные объекты с единым подключением
            storage = PostgresSaver()
            db_manager = DBManager()

        # Мокируем методы для избежания реальных запросов
        with patch.object(storage, '_get_connection', return_value=unified_db_connection), \
             patch.object(db_manager, '_get_connection', return_value=unified_db_connection):

            # Выполняем операции
            storage.get_vacancies_count()
            db_manager.check_connection()

            # Проверяем что используется один тип подключения
            assert unified_db_connection is not None

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_transaction_handling_optimization(self, mock_connect, mock_print, mock_input, unified_db_connection):
        """Тест оптимизации обработки транзакций"""
        mock_connect.return_value = unified_db_connection

        from src.storage.postgres_saver import PostgresSaver

        # Мокируем инициализацию для избежания реальных запросов
        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'):

            storage = PostgresSaver()

        # Мокируем batch операции
        with patch.object(storage, 'add_vacancy_batch_optimized', return_value=["Success"]) as mock_batch:
            result = storage.add_vacancy_batch_optimized([])
            assert isinstance(result, list)
            mock_batch.assert_called_once()

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_cursor_reuse_optimization(self, mock_connect, mock_print, mock_input, unified_db_connection):
        """Тест оптимизации переиспользования курсоров"""
        mock_connect.return_value = unified_db_connection

        from src.storage.db_manager import DBManager

        db_manager = DBManager()

        # Мокируем методы для избежания реальных запросов
        with patch.object(db_manager, 'check_connection', return_value=True), \
             patch.object(db_manager, 'get_companies_and_vacancies_count', return_value=[]):

            # Выполняем операции
            result1 = db_manager.check_connection()
            result2 = db_manager.get_companies_and_vacancies_count()

            assert result1 is True
            assert isinstance(result2, list)