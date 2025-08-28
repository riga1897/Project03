
"""
Тесты для модуля decorators
"""

import pytest
import time
from unittest.mock import patch, Mock
from src.utils.decorators import timing_decorator, cache_result, error_handler


class TestDecorators:
    """Тесты для декораторов"""

    def test_timing_decorator(self):
        """Тест декоратора измерения времени"""
        @timing_decorator
        def slow_function():
            time.sleep(0.1)
            return "result"

        with patch('builtins.print') as mock_print:
            result = slow_function()
            assert result == "result"
            mock_print.assert_called()
            # Проверяем, что вывод содержит информацию о времени
            call_args = str(mock_print.call_args)
            assert "время выполнения" in call_args or "время" in call_args

    def test_cache_result_decorator(self):
        """Тест декоратора кэширования результатов"""
        call_count = 0
        
        @cache_result
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Первый вызов
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Второй вызов с теми же аргументами (должен использовать кэш)
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Функция не должна вызываться повторно

        # Вызов с другими аргументами
        result3 = expensive_function(3)
        assert result3 == 6
        assert call_count == 2

    def test_error_handler_decorator_success(self):
        """Тест декоратора обработки ошибок при успешном выполнении"""
        @error_handler
        def working_function():
            return "success"

        result = working_function()
        assert result == "success"

    def test_error_handler_decorator_with_exception(self):
        """Тест декоратора обработки ошибок при исключении"""
        @error_handler
        def failing_function():
            raise ValueError("Test error")

        with patch('builtins.print') as mock_print:
            result = failing_function()
            assert result is None
            mock_print.assert_called()

    def test_error_handler_decorator_with_default_return(self):
        """Тест декоратора обработки ошибок с возвратом по умолчанию"""
        @error_handler(default_return="default")
        def failing_function():
            raise RuntimeError("Test error")

        with patch('builtins.print') as mock_print:
            result = failing_function()
            assert result == "default"
            mock_print.assert_called()

    def test_multiple_decorators(self):
        """Тест использования нескольких декораторов вместе"""
        @error_handler
        @timing_decorator
        def decorated_function():
            time.sleep(0.01)
            return "decorated result"

        with patch('builtins.print'):
            result = decorated_function()
            assert result == "decorated result"
