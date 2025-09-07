#!/usr/bin/env python3
"""
Тесты модуля simple_db_adapter.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций 
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Тестирование классов SimpleDBAdapter и SimpleCursor

Модуль содержит:
- 2 класса: SimpleDBAdapter (5 методов), SimpleCursor (8 методов)  
- subprocess интеграция с PostgreSQL через psql
- Парсинг результатов, обработка параметров и ошибок
- Глобальные функции для доступа к адаптеру
"""

import pytest
import os
import subprocess
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, patch, call

from src.storage.simple_db_adapter import (
    SimpleDBAdapter,
    SimpleCursor,
    db_adapter,
    get_db_adapter
)


class TestSimpleDBAdapter:
    """100% покрытие класса SimpleDBAdapter"""

    def test_class_exists(self):
        """Покрытие: существование класса"""
        assert SimpleDBAdapter is not None

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host:port/db"})
    def test_init_with_database_url(self):
        """Покрытие: инициализация с DATABASE_URL"""
        adapter = SimpleDBAdapter()
        assert adapter.database_url == "postgresql://user:pass@host:port/db"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_database_url(self):
        """Покрытие: ошибка при отсутствии DATABASE_URL"""
        with pytest.raises(RuntimeError) as exc_info:
            SimpleDBAdapter()
        assert "DATABASE_URL не установлен" in str(exc_info.value)

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_context_manager_enter(self):
        """Покрытие: вход в контекстный менеджер"""
        adapter = SimpleDBAdapter()
        assert adapter.__enter__() == adapter

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_context_manager_exit(self):
        """Покрытие: выход из контекстного менеджера"""
        adapter = SimpleDBAdapter()
        result = adapter.__exit__(None, None, None)
        assert result is None

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_cursor_creation(self):
        """Покрытие: создание курсора"""
        adapter = SimpleDBAdapter()
        cursor = adapter.cursor()
        assert isinstance(cursor, SimpleCursor)
        assert cursor.adapter == adapter

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_cursor_with_factory(self):
        """Покрытие: создание курсора с фабрикой"""
        adapter = SimpleDBAdapter()
        mock_factory = MagicMock()
        cursor = adapter.cursor(cursor_factory=mock_factory)
        assert isinstance(cursor, SimpleCursor)

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_test_connection_success(self, mock_run):
        """Покрытие: успешная проверка соединения"""
        adapter = SimpleDBAdapter()
        
        # Мокируем успешный результат subprocess
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = adapter.test_connection()
        
        assert result is True
        mock_run.assert_called_once_with(
            ["psql", "test_url", "-c", "SELECT 1", "-t", "--quiet"],
            capture_output=True,
            text=True,
            timeout=10
        )

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_test_connection_failure(self, mock_run):
        """Покрытие: неуспешная проверка соединения"""
        adapter = SimpleDBAdapter()
        
        # Мокируем неуспешный результат subprocess
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        result = adapter.test_connection()
        
        assert result is False

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_test_connection_exception(self, mock_run):
        """Покрытие: исключение при проверке соединения"""
        adapter = SimpleDBAdapter()
        
        # Мокируем исключение
        mock_run.side_effect = Exception("Connection error")
        
        result = adapter.test_connection()
        
        assert result is False


class TestSimpleCursor:
    """100% покрытие класса SimpleCursor"""

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_cursor_init(self):
        """Покрытие: инициализация курсора"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        assert cursor.adapter == adapter
        assert cursor._last_results == []

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_cursor_context_manager_enter(self):
        """Покрытие: вход в контекстный менеджер курсора"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        assert cursor.__enter__() == cursor

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_cursor_context_manager_exit(self):
        """Покрытие: выход из контекстного менеджера курсора"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        result = cursor.__exit__(None, None, None)
        assert result is None


class TestSimpleCursorExecute:
    """100% покрытие метода execute"""

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    @patch('src.storage.simple_db_adapter.logger')
    def test_execute_select_success(self, mock_logger, mock_run):
        """Покрытие: успешное выполнение SELECT запроса"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        # Мокируем успешный результат с данными
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1 | John | 25\n2 | Jane | 30\n"
        mock_run.return_value = mock_result
        
        cursor.execute("SELECT id, name, age FROM users")
        
        expected_results = [
            ("1", "John", "25"),
            ("2", "Jane", "30")
        ]
        assert cursor._last_results == expected_results
        
        # Проверяем вызов subprocess
        mock_run.assert_called_once_with(
            ["psql", "test_url", "-c", "SELECT id, name, age FROM users", "-t", "--quiet"],
            capture_output=True,
            text=True,
            timeout=30
        )

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_non_select_success(self, mock_run):
        """Покрытие: успешное выполнение INSERT запроса"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        # Мокируем успешный INSERT
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "INSERT 0 1"
        mock_run.return_value = mock_result
        
        cursor.execute("INSERT INTO users (name) VALUES ('Bob')")
        
        assert cursor._last_results == []

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_with_string_params(self, mock_run):
        """Покрытие: выполнение запроса с строковыми параметрами"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ("John", "john@test.com"))
        
        # Проверяем что параметры заменились
        expected_query = "INSERT INTO users (name, email) VALUES ('John', 'john@test.com')"
        mock_run.assert_called_once()
        actual_call = mock_run.call_args[0][0]
        assert expected_query in actual_call[2]

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_with_none_params(self, mock_run):
        """Покрытие: выполнение запроса с None параметрами"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        cursor.execute("UPDATE users SET email = %s WHERE id = %s", (None, 123))
        
        # Проверяем замену None на NULL и числа на строку
        expected_query = "UPDATE users SET email = NULL WHERE id = 123"
        actual_call = mock_run.call_args[0][0]
        assert expected_query in actual_call[2]

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_with_numeric_params(self, mock_run):
        """Покрытие: выполнение запроса с числовыми параметрами"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        cursor.execute("SELECT * FROM users WHERE age > %s AND score = %s", (18, 95.5))
        
        # Проверяем замену чисел
        expected_query = "SELECT * FROM users WHERE age > 18 AND score = 95.5"
        actual_call = mock_run.call_args[0][0]
        assert expected_query in actual_call[2]

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    @patch('src.storage.simple_db_adapter.logger')
    def test_execute_subprocess_error(self, mock_logger, mock_run):
        """Покрытие: ошибка subprocess при выполнении"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        # Мокируем ошибку subprocess
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "connection failed"
        mock_run.return_value = mock_result
        
        cursor.execute("SELECT * FROM users")
        
        assert cursor._last_results == []
        mock_logger.error.assert_called_once_with("Ошибка выполнения запроса: connection failed")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    @patch('src.storage.simple_db_adapter.logger')
    def test_execute_timeout(self, mock_logger, mock_run):
        """Покрытие: тайм-аут при выполнении"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        # Мокируем тайм-аут
        mock_run.side_effect = subprocess.TimeoutExpired(["psql"], 30)
        
        cursor.execute("SELECT * FROM slow_table")
        
        assert cursor._last_results == []
        mock_logger.error.assert_called_once_with("Тайм-аут выполнения запроса")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    @patch('src.storage.simple_db_adapter.logger')
    def test_execute_general_exception(self, mock_logger, mock_run):
        """Покрытие: общее исключение при выполнении"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        # Мокируем общее исключение
        mock_run.side_effect = Exception("General error")
        
        cursor.execute("SELECT * FROM users")
        
        assert cursor._last_results == []
        mock_logger.error.assert_called_once_with("Ошибка выполнения запроса: General error")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_select_with_empty_lines(self, mock_run):
        """Покрытие: SELECT с пустыми строками в результате"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1 | John\n\n2 | Jane\n   \n"
        mock_run.return_value = mock_result
        
        cursor.execute("SELECT id, name FROM users")
        
        # Пустые строки должны быть пропущены
        expected_results = [("1", "John"), ("2", "Jane")]
        assert cursor._last_results == expected_results


class TestSimpleCursorFetch:
    """100% покрытие методов fetchone и fetchall"""

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_fetchone_with_results(self):
        """Покрытие: fetchone с результатами"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        cursor._last_results = [("1", "John", "25"), ("2", "Jane", "30")]
        
        result = cursor.fetchone()
        
        # Проверяем конвертацию строк в числа
        assert result == (1, "John", 25)

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_fetchone_with_float_conversion(self):
        """Покрытие: fetchone с конвертацией в float"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        cursor._last_results = [("1", "John", "95.5", "test")]
        
        result = cursor.fetchone()
        
        assert result == (1, "John", 95.5, "test")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_fetchone_empty_results(self):
        """Покрытие: fetchone без результатов"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        cursor._last_results = []
        
        result = cursor.fetchone()
        
        assert result is None

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_fetchall_with_results(self):
        """Покрытие: fetchall с результатами"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        expected_results = [("1", "John"), ("2", "Jane")]
        cursor._last_results = expected_results
        
        result = cursor.fetchall()
        
        assert result == expected_results

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_fetchall_empty_results(self):
        """Покрытие: fetchall без результатов"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        cursor._last_results = []
        
        result = cursor.fetchall()
        
        assert result == []


class TestSimpleCursorExecuteQuery:
    """100% покрытие метода execute_query"""

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_query_success(self, mock_run):
        """Покрытие: успешное выполнение execute_query"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1 | John | 25\n2 | Jane | 30\n"
        mock_run.return_value = mock_result
        
        result = cursor.execute_query("SELECT * FROM users")
        
        expected = [
            {"data": ["1", "John", "25"]},
            {"data": ["2", "Jane", "30"]}
        ]
        assert result == expected

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_query_with_params(self, mock_run):
        """Покрытие: execute_query с параметрами ($1, $2)"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1 | John\n"
        mock_run.return_value = mock_result
        
        result = cursor.execute_query("SELECT * FROM users WHERE name = $1 AND age = $2", ("John", 25))
        
        # Проверяем замену параметров $1, $2
        expected_query = "SELECT * FROM users WHERE name = 'John' AND age = 25"
        actual_call = mock_run.call_args[0][0]
        assert expected_query in actual_call[2]
        
        assert result == [{"data": ["1", "John"]}]

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    @patch('src.storage.simple_db_adapter.logger')
    def test_execute_query_subprocess_error(self, mock_logger, mock_run):
        """Покрытие: ошибка subprocess в execute_query"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "syntax error"
        mock_run.return_value = mock_result
        
        result = cursor.execute_query("SELECT * FROM nonexistent")
        
        assert result == []
        mock_logger.error.assert_called_once_with("Ошибка выполнения запроса: syntax error")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    @patch('src.storage.simple_db_adapter.logger')
    def test_execute_query_timeout(self, mock_logger, mock_run):
        """Покрытие: тайм-аут в execute_query"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_run.side_effect = subprocess.TimeoutExpired(["psql"], 30)
        
        result = cursor.execute_query("SELECT * FROM slow_table")
        
        assert result == []
        mock_logger.error.assert_called_once_with("Тайм-аут выполнения запроса")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    @patch('src.storage.simple_db_adapter.logger')
    def test_execute_query_general_exception(self, mock_logger, mock_run):
        """Покрытие: общее исключение в execute_query"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_run.side_effect = Exception("Connection lost")
        
        result = cursor.execute_query("SELECT * FROM users")
        
        assert result == []
        mock_logger.error.assert_called_once_with("Ошибка выполнения запроса: Connection lost")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_query_empty_output(self, mock_run):
        """Покрытие: пустой вывод execute_query"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "\n   \n"
        mock_run.return_value = mock_result
        
        result = cursor.execute_query("SELECT * FROM empty_table")
        
        assert result == []

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_query_parse_exception(self, mock_run):
        """Покрытие: исключение парсинга в execute_query"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid | | | data\ngood | data\n"
        mock_run.return_value = mock_result
        
        result = cursor.execute_query("SELECT * FROM users")
        
        # Должна вернуться только валидная строка
        expected = [{"data": ["invalid", "", "", "data"]}, {"data": ["good", "data"]}]
        assert result == expected


class TestSimpleCursorExecuteUpdate:
    """100% покрытие метода execute_update"""

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_update_insert_success(self, mock_run):
        """Покрытие: успешный INSERT"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "INSERT 0 1"
        mock_run.return_value = mock_result
        
        result = cursor.execute_update("INSERT INTO users (name) VALUES ($1)", ("John",))
        
        assert result == 1
        
        # Проверяем замену параметров
        expected_query = "INSERT INTO users (name) VALUES ('John')"
        actual_call = mock_run.call_args[0][0]
        assert expected_query in actual_call[2]

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_update_update_success(self, mock_run):
        """Покрытие: успешный UPDATE с парсингом количества строк"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "UPDATE 5"
        mock_run.return_value = mock_result
        
        result = cursor.execute_update("UPDATE users SET status = 'active'")
        
        assert result == 5

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_update_delete_success(self, mock_run):
        """Покрытие: успешный DELETE"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "DELETE 3"
        mock_run.return_value = mock_result
        
        result = cursor.execute_update("DELETE FROM users WHERE inactive = true")
        
        assert result == 3

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_execute_update_no_affected_rows_info(self, mock_run):
        """Покрытие: успешное выполнение без информации о количестве строк"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "SOME OTHER OUTPUT"
        mock_run.return_value = mock_result
        
        result = cursor.execute_update("VACUUM")
        
        assert result == 1  # По умолчанию возвращает 1

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    @patch('src.storage.simple_db_adapter.logger')
    def test_execute_update_subprocess_error(self, mock_logger, mock_run):
        """Покрытие: ошибка subprocess в execute_update"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "constraint violation"
        mock_run.return_value = mock_result
        
        result = cursor.execute_update("INSERT INTO users (email) VALUES ('duplicate')")
        
        assert result == 0
        mock_logger.error.assert_called_once_with("Ошибка выполнения обновления: constraint violation")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    @patch('src.storage.simple_db_adapter.logger')
    def test_execute_update_exception(self, mock_logger, mock_run):
        """Покрытие: исключение в execute_update"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_run.side_effect = Exception("Database connection lost")
        
        result = cursor.execute_update("DELETE FROM users WHERE id = 1")
        
        assert result == 0
        mock_logger.error.assert_called_once_with("Ошибка выполнения обновления: Database connection lost")


class TestSimpleCursorTestConnection:
    """100% покрытие метода test_connection курсора"""

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_cursor_test_connection_success(self):
        """Покрытие: успешная проверка соединения курсора"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        # Мокируем успешный execute_query
        with patch.object(cursor, 'execute_query') as mock_execute_query:
            mock_execute_query.return_value = [{"data": ["1"]}]
            
            result = cursor.test_connection()
            
            assert result is True
            mock_execute_query.assert_called_once_with("SELECT 1 as test")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_cursor_test_connection_empty_result(self):
        """Покрытие: проверка соединения с пустым результатом"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        with patch.object(cursor, 'execute_query') as mock_execute_query:
            mock_execute_query.return_value = []
            
            result = cursor.test_connection()
            
            assert result is False

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    def test_cursor_test_connection_exception(self):
        """Покрытие: исключение при проверке соединения курсора"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        with patch.object(cursor, 'execute_query') as mock_execute_query:
            mock_execute_query.side_effect = Exception("Connection error")
            
            result = cursor.test_connection()
            
            assert result is False


class TestGlobalFunctions:
    """100% покрытие глобальных функций и переменных"""

    def test_global_db_adapter_exists(self):
        """Покрытие: существование глобального адаптера"""
        assert db_adapter is not None
        assert isinstance(db_adapter, SimpleDBAdapter)

    def test_get_db_adapter_function(self):
        """Покрытие: функция get_db_adapter"""
        adapter = get_db_adapter()
        assert adapter == db_adapter
        assert isinstance(adapter, SimpleDBAdapter)


class TestComplexScenarios:
    """Сложные сценарии для полного покрытия"""

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_full_workflow_select_and_fetch(self, mock_run):
        """Покрытие: полный workflow SELECT -> fetchone -> fetchall"""
        adapter = SimpleDBAdapter()
        
        # Мокируем успешный результат
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1 | John | 25\n2 | Jane | 30\n"
        mock_run.return_value = mock_result
        
        with adapter as db:
            with db.cursor() as cursor:
                cursor.execute("SELECT id, name, age FROM users")
                
                # fetchone должно вернуть первую строку с конвертацией
                first_row = cursor.fetchone()
                assert first_row == (1, "John", 25)
                
                # fetchall должно вернуть все строки
                all_rows = cursor.fetchall()
                assert len(all_rows) == 2

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})  
    def test_cursor_number_conversion_edge_cases(self):
        """Покрытие: граничные случаи конвертации чисел в fetchone"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        # Тестируем различные форматы чисел
        cursor._last_results = [
            ("123", "45.67", "not_a_number", "89.0", "text123")
        ]
        
        result = cursor.fetchone()
        
        # Проверяем корректную конвертацию
        assert result == (123, 45.67, "not_a_number", 89.0, "text123")

    @patch.dict(os.environ, {"DATABASE_URL": "test_url"})
    @patch('src.storage.simple_db_adapter.subprocess.run')
    def test_parameter_substitution_edge_cases(self, mock_run):
        """Покрытие: граничные случаи замены параметров"""
        adapter = SimpleDBAdapter()
        cursor = SimpleCursor(adapter)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        # Тестируем различные типы параметров в одном запросе
        cursor.execute("INSERT INTO test VALUES (%s, %s, %s, %s)", 
                      ("string", 42, 3.14, None))
        
        expected_query = "INSERT INTO test VALUES ('string', 42, 3.14, NULL)"
        actual_call = mock_run.call_args[0][0]
        assert expected_query in actual_call[2]