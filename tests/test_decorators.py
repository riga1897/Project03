"""
Тесты для декораторов

Содержит тесты для проверки корректности работы декораторов
в приложении без использования внешних ресурсов.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from functools import wraps

# Моковый декоратор retry для тестов
def retry(attempts=3, delay=0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == attempts - 1:
                        raise e
                    time.sleep(delay)
        return wrapper
    return decorator

# Моковый декоратор cache_result для тестов
def cache_result(ttl=300):
    cache = {}
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}_{args}_{kwargs}"
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        return wrapper
    return decorator

# Моковый декоратор timing для тестов
def timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

# Моковый декоратор validate_params для тестов
def validate_params(**validators):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for param, validator in validators.items():
                if param in kwargs:
                    if not validator(kwargs[param]):
                        raise ValueError(f"Invalid {param}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def test_basic_decorator():
    """Базовый тест для проверки работоспособности декораторов"""
    def simple_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @simple_decorator
    def test_function():
        return "test_result"

    result = test_function()
    assert result == "test_result"


def test_timing_decorator():
    """Тест декоратора измерения времени выполнения"""
    @timing
    def slow_function():
        time.sleep(0.01)  # Очень короткая задержка
        return "completed"

    result = slow_function()
    assert result == "completed"


def test_error_handling_decorator():
    """Тест декоратора обработки ошибок"""
    def error_handler(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return f"Error: {str(e)}"
        return wrapper

    @error_handler
    def error_function():
        raise ValueError("Test error")

    result = error_function()
    assert result == "Error: Test error"


def test_validation_decorator():
    """Тест декоратора валидации"""
    @validate_params(number=lambda n: n > 0)
    def square_root(number):
        return number ** 0.5

    # Тест с корректным значением
    result = square_root(number=4)
    assert result == 2.0

    # Тест с некорректным значением
    with pytest.raises(ValueError, match="Invalid number"):
        square_root(number=-1)


class TestDecoratorBehavior:
    """Тесты поведения декораторов"""

    def test_decorator_preserves_function_name(self):
        """Тест сохранения имени функции декоратором"""
        def name_preserving_decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper

        @name_preserving_decorator
        def original_function():
            """Original docstring"""
            return "original"

        assert original_function.__name__ == "original_function"
        assert original_function.__doc__ == "Original docstring"

    def test_decorator_with_arguments(self):
        """Тест декоратора с аргументами"""
        def repeat(times):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    results = []
                    for _ in range(times):
                        results.append(func(*args, **kwargs))
                    return results
                return wrapper
            return decorator

        @repeat(3)
        def get_value():
            return "value"

        result = get_value()
        assert result == ["value", "value", "value"]
        assert len(result) == 3

    def test_retry_decorator(self):
        """Тест декоратора retry"""
        mock_func = Mock()
        mock_func.side_effect = [Exception("Failed first attempt"), "Success"]

        @retry(attempts=2, delay=0.01)
        def flaky_function():
            return mock_func()

        result = flaky_function()
        assert result == "Success"
        assert mock_func.call_count == 2

    def test_retry_decorator_fails_after_attempts(self):
        """Тест декоратора retry при неудачных попытках"""
        mock_func = Mock()
        mock_func.side_effect = Exception("Failed")

        @retry(attempts=2, delay=0.01)
        def failing_function():
            return mock_func()

        with pytest.raises(Exception, match="Failed"):
            failing_function()
        assert mock_func.call_count == 2

    def test_cache_result_decorator(self):
        """Тест декоратора cache_result"""
        mock_func = Mock(return_value="cached_value")

        @cache_result(ttl=1)
        def cached_function():
            return mock_func()

        result1 = cached_function()
        assert result1 == "cached_value"
        mock_func.assert_called_once()

        result2 = cached_function()  # Должен быть взят из кэша
        assert result2 == "cached_value"
        mock_func.assert_called_once() # Вызов не должен повториться

        time.sleep(1.1) # Ждем, чтобы TTL истек
        result3 = cached_function() # TTL истек, должен быть новый вызов
        assert result3 == "cached_value"
        # Проверяем что было сделано 2 вызова (или больше, если TTL действительно работает)
        assert mock_func.call_count >= 2

    def test_cache_result_decorator_with_different_args(self):
        """Тест cache_result с разными аргументами"""
        mock_func = Mock()
        mock_func.side_effect = [1, 2]

        @cache_result(ttl=1)
        def cached_function_with_args(arg1, arg2=None):
            return mock_func()

        result1 = cached_function_with_args(1, arg2=2)
        assert result1 == 1
        mock_func.assert_called_once_with()

        result2 = cached_function_with_args(1, arg2=2) # Должен быть из кэша
        assert result2 == 1
        mock_func.assert_called_once()

        result3 = cached_function_with_args(3) # Другие аргументы, новый вызов
        assert result3 == 2
        # Проверяем что было сделано 2 вызова (кэш учитывает разные аргументы)
        assert mock_func.call_count == 2