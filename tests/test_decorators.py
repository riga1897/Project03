
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
        """Тест декоратора retry при успешном выполнении"""
        @retry_on_failure(max_attempts=3, delay=0.1)
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"

    def test_retry_on_failure_with_retries(self):
        """Тест декоратора retry с повторными попытками"""
        call_count = 0
        
        @retry_on_failure(max_attempts=3, delay=0.1)
        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = failing_then_success()
        assert result == "success"
        assert call_count == 3

    def test_retry_on_failure_max_attempts(self):
        """Тест декоратора retry с превышением попыток"""
        @retry_on_failure(max_attempts=2, delay=0.1)
        def always_failing():
            raise Exception("Always fails")
        
        with pytest.raises(Exception):
            always_failing()

    def test_time_execution_decorator(self):
        """Тест декоратора измерения времени выполнения"""
        @time_execution
        def timed_function():
            time.sleep(0.1)
            return "result"
        
        with patch('builtins.print') as mock_print:
            result = timed_function()
        
        assert result == "result"
        # Проверяем, что время выполнения было выведено
        mock_print.assert_called()

    def test_log_errors_decorator_success(self):
        """Тест декоратора логирования ошибок при успехе"""
        @log_errors
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"

    def test_log_errors_decorator_with_error(self):
        """Тест декоратора логирования ошибок при ошибке"""
        @log_errors
        def failing_function():
            raise ValueError("Test error")
        
        with patch('logging.getLogger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            with pytest.raises(ValueError):
                failing_function()
            
            # Проверяем, что ошибка была залогирована
            mock_logger_instance.error.assert_called()

    def test_multiple_decorators(self):
        """Тест комбинирования нескольких декораторов"""
        @time_execution
        @log_errors
        @retry_on_failure(max_attempts=2, delay=0.1)
        def complex_function():
            return "complex_result"
        
        with patch('builtins.print'):
            result = complex_function()
        
        assert result == "complex_result"
</new_str>
