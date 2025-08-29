"""
Тесты для декораторов

Содержит тесты для проверки корректности работы декораторов
в приложении без использования внешних ресурсов.
"""

import pytest
from unittest.mock import Mock, patch
import time


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
    def timing_decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            return result
        return wrapper

    @timing_decorator
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
    def validate_positive(func):
        def wrapper(number):
            if number <= 0:
                raise ValueError("Number must be positive")
            return func(number)
        return wrapper

    @validate_positive
    def square_root(n):
        return n ** 0.5

    # Тест с корректным значением
    result = square_root(4)
    assert result == 2.0

    # Тест с некорректным значением
    with pytest.raises(ValueError, match="Number must be positive"):
        square_root(-1)


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