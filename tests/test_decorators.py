import pytest
from unittest.mock import Mock, patch
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.decorators import retry_on_failure, time_execution, log_errors


class TestDecorators:
    """Тесты для декораторов"""

    def test_retry_on_failure_success(self):
        """Тест успешного выполнения с первой попытки"""
        @retry_on_failure(max_retries=3)
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_retry_on_failure_eventual_success(self):
        """Тест успешного выполнения после нескольких попыток"""
        call_count = 0

        @retry_on_failure(max_retries=3)
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        result = eventually_successful_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_on_failure_max_retries_exceeded(self):
        """Тест превышения максимального количества попыток"""
        @retry_on_failure(max_retries=2)
        def always_failing_function():
            raise Exception("Always fails")

        with pytest.raises(Exception, match="Always fails"):
            always_failing_function()

    def test_time_execution_decorator(self):
        """Тест декоратора измерения времени выполнения"""
        @time_execution
        def timed_function():
            time.sleep(0.1)
            return "completed"

        with patch('builtins.print') as mock_print:
            result = timed_function()
            assert result == "completed"
            mock_print.assert_called()

    def test_log_errors_decorator_success(self):
        """Тест декоратора логирования ошибок при успешном выполнении"""
        @log_errors
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_log_errors_decorator_with_error(self):
        """Тест декоратора логирования ошибок при возникновении ошибки"""
        @log_errors
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

    def test_combined_decorators(self):
        """Тест комбинирования декораторов"""
        @log_errors
        @time_execution
        @retry_on_failure(max_retries=2)
        def complex_function():
            return "complex result"

        with patch('builtins.print'):
            result = complex_function()
            assert result == "complex result"

    def test_retry_with_custom_exception(self):
        """Тест retry с определенным типом исключения"""
        call_count = 0

        @retry_on_failure(max_retries=3, exception_types=(ValueError,))
        def function_with_specific_error():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Specific error")
            return "success"

        result = function_with_specific_error()
        assert result == "success"
        assert call_count == 2

    def test_decorator_with_arguments(self):
        """Тест декоратора с аргументами функции"""
        @retry_on_failure(max_retries=2)
        def function_with_args(x, y, z=None):
            if x < 0:
                raise ValueError("Negative value")
            return x + y + (z or 0)

        result = function_with_args(1, 2, z=3)
        assert result == 6