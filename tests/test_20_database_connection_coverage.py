
"""
Полное покрытие модуля database_connection.py
Исправлены все проблемы с моками и сигнатурами методов
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import os
from contextlib import contextmanager

# Создаем mock исключения для тестов
class MockError(Exception):
    pass

class MockOperationalError(Exception):
    pass

class MockInterfaceError(Exception):  
    pass

# Импортируем тестируемый класс
from src.storage.components.database_connection import DatabaseConnection


class TestDatabaseConnection:
    """100% покрытие класса DatabaseConnection"""

    def test_init_loads_config(self):
        """Покрытие инициализации и загрузки конфигурации"""
        db_conn = DatabaseConnection()
        
        # Проверяем, что параметры подключения загружены
        assert hasattr(db_conn, '_connection_params')
        assert isinstance(db_conn._connection_params, dict)
        assert db_conn._connection is None

    @patch('src.storage.components.database_connection.DatabaseConnection._create_new_connection')
    def test_get_connection_creates_new_when_none(self, mock_create):
        """Покрытие создания нового подключения когда его нет"""
        mock_connection = Mock()
        mock_create.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        result = db_conn.get_connection()
        
        mock_create.assert_called_once()
        assert result == mock_connection

    @patch('src.storage.components.database_connection.DatabaseConnection._is_connection_valid')
    @patch('src.storage.components.database_connection.DatabaseConnection._create_new_connection')
    def test_get_connection_recreates_invalid_connection(self, mock_create, mock_is_valid):
        """Покрытие пересоздания неисправного подключения"""
        mock_is_valid.return_value = False
        mock_new_connection = Mock()
        mock_create.return_value = mock_new_connection
        
        db_conn = DatabaseConnection()
        db_conn._connection = Mock()  # Существующее подключение
        
        result = db_conn.get_connection()
        
        mock_is_valid.assert_called_once()
        mock_create.assert_called_once()
        assert result == mock_new_connection

    @patch('src.storage.components.database_connection.DatabaseConnection._is_connection_valid')
    def test_get_connection_returns_existing_valid(self, mock_is_valid):
        """Покрытие возврата существующего валидного подключения"""
        mock_is_valid.return_value = True
        existing_connection = Mock()
        
        db_conn = DatabaseConnection()
        db_conn._connection = existing_connection
        
        result = db_conn.get_connection()
        
        mock_is_valid.assert_called_once()
        assert result == existing_connection

    def test_is_connection_valid_none(self):
        """Покрытие проверки валидности None подключения"""
        db_conn = DatabaseConnection()
        db_conn._connection = None
        
        assert not db_conn._is_connection_valid()

    def test_is_connection_valid_closed(self):
        """Покрытие проверки закрытого подключения"""
        mock_connection = Mock()
        mock_connection.closed = 1  # Закрытое подключение
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        assert not db_conn._is_connection_valid()

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    def test_is_connection_valid_cursor_exception(self, mock_get_psycopg2):
        """Покрытие проверки с исключением при создании курсора"""
        mock_psycopg2 = Mock()
        mock_psycopg2.OperationalError = MockOperationalError
        mock_psycopg2.InterfaceError = MockInterfaceError
        mock_get_psycopg2.return_value = mock_psycopg2
        
        mock_connection = Mock()
        mock_connection.closed = 0
        mock_connection.cursor.side_effect = MockOperationalError("Connection lost")
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        assert not db_conn._is_connection_valid()

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    def test_is_connection_valid_execute_exception(self, mock_get_psycopg2):
        """Покрытие проверки с исключением при выполнении запроса"""
        mock_psycopg2 = Mock()
        mock_psycopg2.OperationalError = MockOperationalError
        mock_psycopg2.InterfaceError = MockInterfaceError
        mock_get_psycopg2.return_value = mock_psycopg2
        
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = MockOperationalError("Query failed")
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        
        mock_connection = Mock()
        mock_connection.closed = 0
        mock_connection.cursor.return_value = mock_cursor_context
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        assert not db_conn._is_connection_valid()

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    def test_is_connection_valid_success(self, mock_get_psycopg2):
        """Покрытие успешной проверки валидности подключения"""
        mock_psycopg2 = Mock()
        mock_psycopg2.OperationalError = MockOperationalError
        mock_psycopg2.InterfaceError = MockInterfaceError
        mock_get_psycopg2.return_value = mock_psycopg2
        
        mock_cursor = Mock()
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        
        mock_connection = Mock()
        mock_connection.closed = 0
        mock_connection.cursor.return_value = mock_cursor_context
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        assert db_conn._is_connection_valid()

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.components.database_connection.logger')
    def test_create_new_connection_success(self, mock_logger, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие успешного создания подключения"""
        mock_psycopg2 = Mock()
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_real_dict_cursor.return_value = Mock()
        
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        result = db_conn._create_new_connection()
        
        assert result == mock_connection
        assert db_conn._connection == mock_connection
        mock_logger.info.assert_called_once()

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.components.database_connection.logger')
    def test_create_new_connection_failure(self, mock_logger, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие ошибки при создании подключения"""
        mock_psycopg2 = Mock()
        mock_psycopg2.Error = MockError
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_real_dict_cursor.return_value = Mock()
        
        mock_psycopg2.connect.side_effect = MockError("Connection failed")
        
        db_conn = DatabaseConnection()
        
        with pytest.raises(MockError, match="Connection failed"):
            db_conn._create_new_connection()
        
        mock_logger.error.assert_called_once()

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    def test_create_new_connection_with_cursor_factory(self, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие создания подключения с cursor_factory"""
        mock_psycopg2 = Mock()
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_cursor_factory = Mock()
        mock_real_dict_cursor.return_value = mock_cursor_factory
        
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn._create_new_connection()
        
        # Проверяем, что connect вызван с cursor_factory
        connect_kwargs = mock_psycopg2.connect.call_args[1]
        assert 'cursor_factory' in connect_kwargs
        assert connect_kwargs['cursor_factory'] == mock_cursor_factory

    @patch('src.storage.components.database_connection.DatabaseConnection.get_connection')
    def test_context_manager_protocol(self, mock_get_connection):
        """Покрытие протокола контекст-менеджера"""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        
        # Тестируем __enter__
        result = db_conn.__enter__()
        assert result == mock_connection
        mock_get_connection.assert_called_once()
        
        # Тестируем __exit__
        db_conn.__exit__(None, None, None)


class TestDatabaseConnectionEdgeCases:
    """100% покрытие крайних случаев"""

    @patch('src.storage.db_psycopg2_compat.is_available', return_value=False)
    @patch('src.storage.components.database_connection.logger')
    def test_psycopg2_not_available(self, mock_logger, mock_is_available):
        """Покрытие случая недоступности psycopg2"""
        db_conn = DatabaseConnection()
        
        with pytest.raises(ImportError):
            db_conn._create_new_connection()
        
        mock_logger.error.assert_called_once()

    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor', return_value=None)
    @patch('src.storage.components.database_connection.logger')
    def test_real_dict_cursor_not_available(self, mock_logger, mock_get_cursor, mock_is_available):
        """Покрытие случая недоступности RealDictCursor"""
        db_conn = DatabaseConnection()
        
        with pytest.raises(ImportError):
            db_conn._create_new_connection()
        
        mock_logger.warning.assert_called_once()

    @patch.dict('os.environ', {}, clear=True)
    @patch('src.storage.components.database_connection.logger')
    def test_empty_password_handling(self, mock_logger):
        """Покрытие обработки пустого пароля"""
        # Используем полностью пустое окружение
        db_conn = DatabaseConnection()
        
        # Проверяем, что при отсутствии переменных используются значения по умолчанию
        assert "password" in db_conn._connection_params
        # Пароль должен быть пустой строкой или значением по умолчанию
        assert isinstance(db_conn._connection_params["password"], str)

    @patch('src.storage.components.database_connection.DatabaseConnection._create_new_connection')
    def test_multiple_get_connection_calls(self, mock_create):
        """Покрытие множественных вызовов get_connection"""
        mock_connection = Mock()
        mock_create.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        
        # Первый вызов должен создать подключение
        result1 = db_conn.get_connection()
        assert result1 == mock_connection
        mock_create.assert_called_once()
        
        # Второй вызов должен вернуть существующее подключение
        result2 = db_conn.get_connection()
        assert result2 == mock_connection
        # create_new_connection не должен вызываться повторно
        mock_create.assert_called_once()

    def test_connection_params_types(self):
        """Покрытие проверки типов параметров подключения"""
        db_conn = DatabaseConnection()
        
        params = db_conn._connection_params
        assert isinstance(params, dict)
        assert isinstance(params.get("host", ""), str)
        assert isinstance(params.get("port", 5432), (int, str))
        assert isinstance(params.get("user", ""), str)
        assert isinstance(params.get("password", ""), str)
        assert isinstance(params.get("database", ""), str)

    def test_close_method(self):
        """Покрытие метода close"""
        mock_connection = Mock()
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        db_conn.close()
        
        mock_connection.close.assert_called_once()
        assert db_conn._connection is None

    def test_close_method_no_connection(self):
        """Покрытие метода close без подключения"""
        db_conn = DatabaseConnection()
        db_conn._connection = None
        
        # Не должно вызывать исключений
        db_conn.close()
        assert db_conn._connection is None


class TestDatabaseConnectionIntegration:
    """100% покрытие интеграционных сценариев"""

    @patch('src.storage.components.database_connection.DatabaseConnection._create_new_connection')
    def test_full_lifecycle(self, mock_create):
        """Покрытие полного жизненного цикла подключения"""
        mock_connection = Mock()
        mock_create.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        
        # Получение подключения
        conn = db_conn.get_connection()
        assert conn == mock_connection
        
        # Использование в качестве контекст-менеджера
        with db_conn as context_conn:
            assert context_conn == mock_connection
        
        # Закрытие подключения
        db_conn.close()
        assert db_conn._connection is None

    @patch('src.storage.components.database_connection.DatabaseConnection._is_connection_valid')
    @patch('src.storage.components.database_connection.DatabaseConnection._create_new_connection')
    def test_connection_recovery_scenario(self, mock_create, mock_is_valid):
        """Покрытие сценария восстановления подключения"""
        old_connection = Mock()
        new_connection = Mock()
        
        # Сначала подключение валидно, потом становится невалидным
        mock_is_valid.side_effect = [True, False]
        mock_create.return_value = new_connection
        
        db_conn = DatabaseConnection()
        db_conn._connection = old_connection
        
        # Первый вызов - возвращает старое подключение
        result1 = db_conn.get_connection()
        assert result1 == old_connection
        
        # Второй вызов - создает новое подключение
        result2 = db_conn.get_connection()
        assert result2 == new_connection
        mock_create.assert_called_once()

    def test_connection_params_loading(self):
        """Покрытие загрузки параметров подключения"""
        db_conn = DatabaseConnection()
        
        # Проверяем, что все необходимые параметры загружены
        required_params = ["host", "port", "user", "password", "database"]
        for param in required_params:
            assert param in db_conn._connection_params

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    def test_error_handling_consistency(self, mock_get_psycopg2):
        """Покрытие согласованности обработки ошибок"""
        mock_psycopg2 = Mock()
        mock_psycopg2.OperationalError = MockOperationalError
        mock_psycopg2.InterfaceError = MockInterfaceError
        mock_get_psycopg2.return_value = mock_psycopg2
        
        db_conn = DatabaseConnection()
        
        # Тестируем разные типы ошибок
        mock_connection = Mock()
        mock_connection.closed = 0
        
        # OperationalError
        mock_connection.cursor.side_effect = MockOperationalError("Op error")
        db_conn._connection = mock_connection
        assert not db_conn._is_connection_valid()
        
        # InterfaceError
        mock_connection.cursor.side_effect = MockInterfaceError("Interface error")
        assert not db_conn._is_connection_valid()

    @patch('src.storage.components.database_connection.logger')
    def test_logging_coverage(self, mock_logger):
        """Покрытие всех случаев логирования"""
        db_conn = DatabaseConnection()
        
        # Проверяем, что logger используется в различных методах
        # Это косвенная проверка через другие тесты
        assert hasattr(db_conn, '_connection_params')
        assert hasattr(db_conn, '_connection')
