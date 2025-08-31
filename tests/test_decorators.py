
import pytest
from unittest.mock import Mock, patch
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def retry_on_failure(max_attempts=3, delay=1):
    """Декоратор для повторных попыток при неудаче"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


def time_execution(func):
    """Декоратор для измерения времени выполнения"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper


def log_errors(func):
    """Декоратор для логирования ошибок"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
            raise e
    return wrapper


class TestDecorators:
    def test_retry_on_failure_success(self):
        """Тест успешного выполнения с retry декоратором"""
        @retry_on_failure(max_attempts=3)
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"

    def test_retry_on_failure_with_retries(self):
        """Тест retry декоратора с повторными попытками"""
        call_count = 0
        
        @retry_on_failure(max_attempts=3, delay=0.1)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Test error")
            return "success"
        
        result = failing_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_on_failure_max_attempts(self):
        """Тест retry декоратора с превышением максимального количества попыток"""
        @retry_on_failure(max_attempts=2, delay=0.1)
        def always_failing_function():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_failing_function()

    def test_time_execution_decorator(self):
        """Тест декоратора измерения времени выполнения"""
        @time_execution
        def test_function():
            time.sleep(0.1)
            return "done"
        
        with patch('builtins.print') as mock_print:
            result = test_function()
            assert result == "done"
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
        
        with patch('builtins.print') as mock_print:
            with pytest.raises(ValueError):
                failing_function()
            mock_print.assert_called()

    def test_combined_decorators(self):
        """Тест комбинации декораторов"""
        @time_execution
        @log_errors
        @retry_on_failure(max_attempts=2, delay=0.1)
        def combined_function():
            return "combined"
        
        result = combined_function()
        assert result == "combined"
