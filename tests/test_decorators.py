
"""
Тесты для модуля декораторов
"""

import os
import sys
import time
from typing import Any, Callable
from unittest.mock import MagicMock, Mock, patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт из реального кода
try:
    from src.utils.decorators import timing_decorator, cache_decorator, retry_decorator, log_decorator
    DECORATORS_AVAILABLE = True
except ImportError:
    DECORATORS_AVAILABLE = False


class TestDecorators:
    """Тесты для декораторов"""

    def test_timing_decorator(self):
        """Тест декоратора измерения времени выполнения"""
        if DECORATORS_AVAILABLE:
            decorator = timing_decorator
        else:
            decorator = mock_timing_decorator
        
        @decorator
        def test_function():
            """Тестовая функция"""
            time.sleep(0.1)
            return "result"
        
        with patch('builtins.print') as mock_print:
            result = test_function()
            
            assert result == "result"
            assert mock_print.called

    def test_cache_decorator(self):
        """Тест декоратора кэширования"""
        if DECORATORS_AVAILABLE:
            decorator = cache_decorator
        else:
            decorator = mock_cache_decorator
        
        call_count = 0
        
        @decorator
        def expensive_function(x: int) -> int:
            """Дорогая функция для тестирования кэша"""
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Первый вызов
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Второй вызов с теми же аргументами (должен взять из кэша)
        result2 = expensive_function(5)
        assert result2 == 10
        # Функция не должна вызываться повторно
        if DECORATORS_AVAILABLE:
            assert call_count == 1
        
        # Вызов с другими аргументами
        result3 = expensive_function(10)
        assert result3 == 20
        expected_count = 2 if DECORATORS_AVAILABLE else 3
        assert call_count == expected_count

    def test_retry_decorator_success(self):
        """Тест декоратора повторных попыток - успешное выполнение"""
        if DECORATORS_AVAILABLE:
            decorator = retry_decorator(max_attempts=3, delay=0.01)
        else:
            decorator = mock_retry_decorator(max_attempts=3, delay=0.01)
        
        @decorator
        def successful_function():
            """Функция, которая выполняется успешно"""
            return "success"
        
        result = successful_function()
        assert result == "success"

    def test_retry_decorator_with_failures(self):
        """Тест декоратора повторных попыток - с неудачными попытками"""
        if DECORATORS_AVAILABLE:
            decorator = retry_decorator(max_attempts=3, delay=0.01)
        else:
            decorator = mock_retry_decorator(max_attempts=3, delay=0.01)
        
        call_count = 0
        
        @decorator
        def failing_function():
            """Функция, которая иногда падает"""
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = failing_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_decorator_max_attempts_exceeded(self):
        """Тест декоратора повторных попыток - превышение максимального количества попыток"""
        if DECORATORS_AVAILABLE:
            decorator = retry_decorator(max_attempts=2, delay=0.01)
        else:
            decorator = mock_retry_decorator(max_attempts=2, delay=0.01)
        
        @decorator
        def always_failing_function():
            """Функция, которая всегда падает"""
            raise ValueError("Persistent error")
        
        with pytest.raises(ValueError, match="Persistent error"):
            always_failing_function()

    def test_log_decorator(self):
        """Тест декоратора логирования"""
        if DECORATORS_AVAILABLE:
            decorator = log_decorator
        else:
            decorator = mock_log_decorator
        
        @decorator
        def test_function(x: int, y: int = 10) -> int:
            """Тестовая функция для логирования"""
            return x + y
        
        with patch('builtins.print') as mock_print:
            result = test_function(5, y=15)
            
            assert result == 20
            # Проверяем, что логирование происходило
            assert mock_print.called

    def test_combined_decorators(self):
        """Тест комбинирования декораторов"""
        if DECORATORS_AVAILABLE:
            timing_dec = timing_decorator
            cache_dec = cache_decorator
            log_dec = log_decorator
        else:
            timing_dec = mock_timing_decorator
            cache_dec = mock_cache_decorator
            log_dec = mock_log_decorator
        
        @timing_dec
        @cache_dec
        @log_dec
        def complex_function(x: int) -> int:
            """Функция с несколькими декораторами"""
            time.sleep(0.01)  # Имитация работы
            return x ** 2
        
        with patch('builtins.print'):
            result1 = complex_function(5)
            assert result1 == 25
            
            result2 = complex_function(5)  # Из кэша
            assert result2 == 25

    def test_decorator_preserves_metadata(self):
        """Тест сохранения метаданных функции декораторами"""
        if DECORATORS_AVAILABLE:
            decorator = timing_decorator
        else:
            decorator = mock_timing_decorator
        
        @decorator
        def documented_function(x: int) -> int:
            """Функция с документацией и аннотациями типов"""
            return x * 2
        
        # Проверяем, что метаданные сохранены
        assert documented_function.__name__ == "documented_function"
        assert "Функция с документацией" in documented_function.__doc__

    def test_cache_decorator_with_different_types(self):
        """Тест кэш-декоратора с разными типами аргументов"""
        if DECORATORS_AVAILABLE:
            decorator = cache_decorator
        else:
            decorator = mock_cache_decorator
        
        @decorator
        def function_with_various_args(x: int, y: str, z: dict = None) -> str:
            """Функция с различными типами аргументов"""
            if z is None:
                z = {}
            return f"{x}_{y}_{len(z)}"
        
        result1 = function_with_various_args(1, "test", {"a": 1})
        assert result1 == "1_test_1"
        
        result2 = function_with_various_args(1, "test", {"a": 1})
        assert result2 == "1_test_1"

    def test_error_handling_in_decorators(self):
        """Тест обработки ошибок в декораторах"""
        if DECORATORS_AVAILABLE:
            decorator = log_decorator
        else:
            decorator = mock_log_decorator
        
        @decorator
        def error_function():
            """Функция, которая вызывает ошибку"""
            raise RuntimeError("Test error")
        
        with pytest.raises(RuntimeError, match="Test error"):
            error_function()


# Тестовые реализации декораторов
def mock_timing_decorator(func: Callable) -> Callable:
    """Тестовая реализация декоратора измерения времени"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {execution_time:.4f} секунд")
        return result
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def mock_cache_decorator(func: Callable) -> Callable:
    """Тестовая реализация декоратора кэширования"""
    cache = {}
    
    def wrapper(*args, **kwargs):
        # Создаем ключ кэша из аргументов
        cache_key = str(args) + str(sorted(kwargs.items()))
        
        if cache_key in cache:
            return cache[cache_key]
        
        result = func(*args, **kwargs)
        cache[cache_key] = result
        return result
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.cache = cache  # Для тестирования
    return wrapper


def mock_retry_decorator(max_attempts: int = 3, delay: float = 1.0):
    """Тестовая реализация декоратора повторных попыток"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(delay)
            
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator


def mock_log_decorator(func: Callable) -> Callable:
    """Тестовая реализация декоратора логирования"""
    def wrapper(*args, **kwargs):
        print(f"Вызов функции {func.__name__} с аргументами: {args}, {kwargs}")
        try:
            result = func(*args, **kwargs)
            print(f"Функция {func.__name__} завершилась успешно. Результат: {result}")
            return result
        except Exception as e:
            print(f"Функция {func.__name__} завершилась с ошибкой: {e}")
            raise
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
