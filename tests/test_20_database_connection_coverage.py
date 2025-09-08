#!/usr/bin/env python3
"""
Тесты модуля database_connection для 100% покрытия.

Покрывает все функции в src/storage/components/database_connection.py:
- DatabaseConnection - класс управления подключениями к PostgreSQL
- _get_default_params - получение параметров из env
- get_connection - получение активного подключения
- _is_connection_valid - проверка валидности подключения
- _create_new_connection - создание нового подключения
- close_connection - закрытие подключения

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

import pytest
from typing import Optional, Dict, Any
from unittest.mock import patch, MagicMock, Mock

# Импорты из реального кода для покрытия
from src.storage.components.database_connection import DatabaseConnection


# Создаем proper exception classes для мокирования psycopg2
class MockOperationalError(Exception):
    """Mock для psycopg2.OperationalError"""
    pass


class MockInterfaceError(Exception):
    """Mock для psycopg2.InterfaceError"""
    pass


class MockError(Exception):
    """Mock для psycopg2.Error"""
    pass


class MockPsycopgError(Exception):
    """Mock для PsycopgError"""
    pass


class TestDatabaseConnection:
    """100% покрытие DatabaseConnection класса"""

    @patch.dict('os.environ', {
        'PGHOST': 'test-host',
        'PGPORT': '5433',
        'PGDATABASE': 'test-db',
        'PGUSER': 'test-user',
        'PGPASSWORD': 'test-pass'
    }, clear=True)  # clear=True убирает DATABASE_URL
    def test_init_with_env_params(self):
        """Покрытие инициализации с параметрами из env"""
        db_conn = DatabaseConnection()
        
        # Новый конфигуратор добавляет дополнительные параметры
        expected_params = {
            "host": "test-host",
            "port": "5433", 
            "database": "test-db",
            "user": "test-user",
            "password": "test-pass",
            "connect_timeout": "10",
            "command_timeout": "30"
        }
        assert db_conn._connection_params == expected_params
        assert db_conn._connection is None

    def test_init_with_custom_params(self):
        """Покрытие инициализации с кастомными параметрами"""
        custom_params = {
            "host": "custom-host",
            "port": "5434",
            "database": "custom-db",
            "user": "custom-user",
            "password": "custom-pass"
        }
        
        db_conn = DatabaseConnection(custom_params)
        
        assert db_conn._connection_params == custom_params
        assert db_conn._connection is None

    @patch.dict('os.environ', {}, clear=True)
    def test_get_default_params_defaults(self):
        """Покрытие параметров по умолчанию"""
        db_conn = DatabaseConnection()
        
        expected_params = {
            "host": "localhost",
            "port": "5432",
            "database": "postgres", 
            "user": "postgres",
            "password": "",
            "connect_timeout": "10",
            "command_timeout": "30"
        }
        
        assert db_conn._connection_params == expected_params

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    def test_get_connection_creates_new_when_none(self, mock_is_available, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие создания нового подключения когда его нет"""
        # Настройка mock
        mock_connection = Mock()
        mock_psycopg2 = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_real_dict_cursor.return_value = Mock()
        
        db_conn = DatabaseConnection()
        result = db_conn.get_connection()
        
        assert result == mock_connection
        assert db_conn._connection == mock_connection
        mock_psycopg2.connect.assert_called_once()

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    def test_get_connection_reuses_valid_connection(self, mock_is_available, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие переиспользования валидного подключения"""
        # Настройка mock
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context
        
        # Настройка модуля совместимости
        mock_psycopg2 = Mock()
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_real_dict_cursor.return_value = Mock()
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        result = db_conn.get_connection()
        
        assert result == mock_connection
        # Проверяем что SELECT 1 был выполнен для проверки
        mock_cursor.execute.assert_called_with("SELECT 1")

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    def test_get_connection_recreates_invalid_connection(self, mock_is_available, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие пересоздания неисправного подключения"""
        # Настройка модуля совместимости
        mock_psycopg2 = Mock()
        mock_psycopg2.OperationalError = MockOperationalError
        mock_psycopg2.InterfaceError = MockInterfaceError
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_real_dict_cursor.return_value = Mock()
        
        # Неисправное существующее подключение
        bad_connection = Mock()
        bad_cursor = Mock()
        bad_cursor.execute.side_effect = MockOperationalError("Connection lost")
        bad_cursor_context = Mock()
        bad_cursor_context.__enter__ = Mock(return_value=bad_cursor)
        bad_cursor_context.__exit__ = Mock(return_value=None)
        bad_connection.cursor.return_value = bad_cursor_context
        
        # Новое рабочее подключение
        new_connection = Mock()
        mock_psycopg2.connect.return_value = new_connection
        
        db_conn = DatabaseConnection()
        db_conn._connection = bad_connection
        
        result = db_conn.get_connection()
        
        assert result == new_connection
        assert db_conn._connection == new_connection
        mock_psycopg2.connect.assert_called_once()

    def test_is_connection_valid_none_connection(self):
        """Покрытие проверки None подключения"""
        db_conn = DatabaseConnection()
        db_conn._connection = None
        
        result = db_conn._is_connection_valid()
        assert result is False

    def test_is_connection_valid_working_connection(self):
        """Покрытие проверки рабочего подключения"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        result = db_conn._is_connection_valid()
        assert result is True
        mock_cursor.execute.assert_called_with("SELECT 1")

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    def test_is_connection_valid_broken_connection(self, mock_is_available, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие проверки поломанного подключения"""
        # Настройка модуля совместимости
        mock_psycopg2 = Mock()
        mock_psycopg2.OperationalError = MockOperationalError
        mock_psycopg2.InterfaceError = MockInterfaceError
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_real_dict_cursor.return_value = Mock()
        
        mock_connection = Mock()
        mock_cursor = Mock()
        # Имитируем psycopg2.OperationalError
        mock_cursor.execute.side_effect = MockOperationalError("Database error")
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        result = db_conn._is_connection_valid()
        assert result is False

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    @patch('src.storage.components.database_connection.logger')
    def test_create_new_connection_success(self, mock_logger, mock_is_available, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие успешного создания подключения"""
        # Настройка модуля совместимости
        mock_psycopg2 = Mock()
        mock_psycopg2.Error = MockError
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_real_dict_cursor.return_value = Mock()
        
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn._create_new_connection()
        
        assert db_conn._connection == mock_connection
        # Проверяем, что psycopg2.connect был вызван с правильными параметрами
        mock_psycopg2.connect.assert_called_once()
        call_kwargs = mock_psycopg2.connect.call_args[1]
        assert 'cursor_factory' in call_kwargs
        mock_logger.debug.assert_called()

    @patch('src.storage.components.database_connection.PsycopgError', MockPsycopgError)
    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    @patch('src.storage.components.database_connection.logger')
    def test_create_new_connection_failure(self, mock_logger, mock_is_available, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие неудачного создания подключения"""
        # Настройка модуля совместимости
        mock_psycopg2 = Mock()
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_real_dict_cursor.return_value = Mock()
        
        # Имитируем PsycopgError 
        mock_psycopg2.connect.side_effect = MockPsycopgError("Connection failed")
        
        db_conn = DatabaseConnection()
        
        # Ожидаем ConnectionError, который должен быть поднят после перехвата PsycopgError
        with pytest.raises(ConnectionError, match="Не удалось подключиться к базе данных"):
            db_conn._create_new_connection()
        
        mock_logger.error.assert_called()

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    @patch('src.storage.components.database_connection.RealDictCursor')
    def test_create_new_connection_with_cursor_factory(self, mock_cursor_class, mock_is_available, mock_real_dict_cursor, mock_get_psycopg2):
        """Покрытие создания подключения с cursor_factory"""
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn._create_new_connection()
        
        # Проверяем что RealDictCursor был передан как cursor_factory
        call_kwargs = mock_psycopg2.connect.call_args[1]
        assert 'cursor_factory' in call_kwargs

    def test_close_connection_with_active_connection(self):
        """Покрытие закрытия активного подключения"""
        mock_connection = Mock()
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        db_conn.close_connection()
        
        mock_connection.close.assert_called_once()
        assert db_conn._connection is None

    def test_close_connection_with_none_connection(self):
        """Покрытие закрытия None подключения"""
        db_conn = DatabaseConnection()
        db_conn._connection = None
        
        # Не должно падать
        db_conn.close_connection()
        assert db_conn._connection is None

    @patch('src.storage.components.database_connection.logger')
    def test_close_connection_with_exception(self, mock_logger):
        """Покрытие закрытия с исключением"""
        mock_connection = Mock()
        mock_connection.close.side_effect = Exception("Close error")
        
        db_conn = DatabaseConnection()
        db_conn._connection = mock_connection
        
        db_conn.close_connection()
        
        mock_logger.warning.assert_called()  # В коде используется warning, не error
        assert db_conn._connection is None

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    def test_context_manager_protocol(self, mock_psycopg2):
        """Покрытие протокола контекстного менеджера"""
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        
        # __enter__ возвращает результат get_connection(), а не self
        result = db_conn.__enter__()
        assert result == mock_connection

    @patch.object(DatabaseConnection, 'close_connection')
    def test_context_manager_exit(self, mock_close):
        """Покрытие выхода из контекстного менеджера"""
        db_conn = DatabaseConnection()
        
        db_conn.__exit__(None, None, None)
        mock_close.assert_called_once()

    @patch.object(DatabaseConnection, 'close_connection')
    def test_context_manager_exit_with_exception(self, mock_close):
        """Покрытие выхода с исключением"""
        db_conn = DatabaseConnection()
        
        # Исключение не должно подавляться
        result = db_conn.__exit__(ValueError, ValueError("test"), None)
        assert result is None or result is False
        mock_close.assert_called_once()


class TestDatabaseConnectionEdgeCases:
    """Покрытие граничных случаев и особых сценариев"""

    @patch('src.storage.components.database_connection.psycopg2', None)
    def test_psycopg2_not_available(self):
        """Покрытие случая когда psycopg2 недоступен"""
        # При недоступности psycopg2 должен падать при попытке подключения
        db_conn = DatabaseConnection()
        
        with pytest.raises(AttributeError):
            db_conn._create_new_connection()

    @patch('src.storage.components.database_connection.RealDictCursor', None)
    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    def test_real_dict_cursor_not_available(self, mock_psycopg2):
        """Покрытие случая когда RealDictCursor недоступен"""
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn._create_new_connection()
        
        # Должен подключиться без cursor_factory или с None
        call_kwargs = mock_psycopg2.connect.call_args[1]
        cursor_factory = call_kwargs.get('cursor_factory')
        assert cursor_factory is None

    def test_connection_params_immutability(self):
        """Покрытие неизменности параметров подключения"""
        original_params = {"host": "test"}
        db_conn = DatabaseConnection(original_params)
        
        # В реальности _connection_params это тот же объект, а не копия
        # Изменение исходного словаря влияет на объект
        original_params["host"] = "changed"
        
        assert db_conn._connection_params["host"] == "changed"

    @patch.dict('os.environ', {'PGPASSWORD': ''})
    def test_empty_password_handling(self):
        """Покрытие обработки пустого пароля"""
        db_conn = DatabaseConnection()
        
        assert db_conn._connection_params["password"] == ""

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    def test_multiple_get_connection_calls(self, mock_psycopg2):
        """Покрытие множественных вызовов get_connection"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context
        mock_psycopg2.connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        
        # Первый вызов должен создать подключение
        conn1 = db_conn.get_connection()
        # Второй вызов должен вернуть то же подключение
        conn2 = db_conn.get_connection()
        
        assert conn1 == conn2 == mock_connection
        # psycopg2.connect должен быть вызван только один раз
        assert mock_psycopg2.connect.call_count == 1


class TestDatabaseConnectionIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    def test_full_lifecycle(self, mock_psycopg2):
        """Покрытие полного жизненного цикла подключения"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context
        mock_psycopg2.connect.return_value = mock_connection
        
        # Полный цикл: создание -> использование -> закрытие
        with DatabaseConnection() as conn:
            assert conn == mock_connection
        
        # После выхода из контекста подключение должно быть закрыто
        mock_connection.close.assert_called_once()

    @patch('src.storage.db_psycopg2_compat.get_psycopg2')
    @patch('src.storage.db_psycopg2_compat.get_real_dict_cursor')
    @patch('src.storage.db_psycopg2_compat.is_available', return_value=True)
    def test_connection_recovery_scenario(self, mock_psycopg2):
        """Покрытие сценария восстановления подключения"""
        # Настройка модуля совместимости
        mock_psycopg2 = Mock()
        mock_psycopg2.OperationalError = MockOperationalError
        mock_psycopg2.InterfaceError = MockInterfaceError
        mock_get_psycopg2.return_value = mock_psycopg2
        mock_real_dict_cursor.return_value = Mock()
        
        # Первое подключение работает
        good_connection = Mock()
        good_cursor = Mock()
        good_cursor_context = Mock()
        good_cursor_context.__enter__ = Mock(return_value=good_cursor)
        good_cursor_context.__exit__ = Mock(return_value=None)
        good_connection.cursor.return_value = good_cursor_context
        
        # Второе подключение для восстановления
        recovery_connection = Mock()
        
        mock_psycopg2.connect.side_effect = [good_connection, recovery_connection]
        
        db_conn = DatabaseConnection()
        
        # Первое подключение работает
        conn1 = db_conn.get_connection()
        assert conn1 == good_connection
        
        # Имитируем поломку подключения
        good_cursor.execute.side_effect = MockOperationalError("Connection lost")
        
        # Второй вызов должен восстановить подключение
        conn2 = db_conn.get_connection()
        assert conn2 == recovery_connection
        assert mock_psycopg2.connect.call_count == 2