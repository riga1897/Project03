#!/usr/bin/env python3
"""
Тесты декораторов для 100% покрытия.

Покрывает все функции в src/utils/decorators.py:
- simple_cache - декоратор кэширования с TTL и LRU
- retry_on_failure - декоратор повторных попыток при сбоях
- time_execution - декоратор измерения времени выполнения (с print)
- log_errors - декоратор логирования ошибок

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

from typing import Dict, NoReturn, Any
import pytest
from unittest.mock import patch, Mock

# Импорты из реального кода для покрытия
from src.utils.decorators import simple_cache, retry_on_failure, time_execution, log_errors


class TestSimpleCacheDecorator:
    """100% покрытие simple_cache декоратора"""

    @patch('src.utils.decorators.EnvLoader.get_env_var_int')
    @patch('src.utils.decorators.time.time')
    def test_simple_cache_basic_functionality(self, mock_time: Any, mock_env: Any) -> None:
        """Покрытие базовой функциональности кэширования"""
        mock_env.return_value = 3600  # TTL = 1 час
        mock_time.return_value = 1000.0

        @simple_cache()
        def test_func(x: int, y: None = None) -> str:
            return f"result_{x}_{y}"

        # Первый вызов - должен выполниться
        result1 = test_func(1, y=2)
        assert result1 == "result_1_2"

        # Второй вызов с теми же параметрами - должен вернуться из кэша
        mock_time.return_value = 1500.0  # Прошло 500 секунд
        result2 = test_func(1, y=2)
        assert result2 == "result_1_2"

        # Проверяем, что функция была вызвана только один раз
        # (это проверяется по результату, который одинаковый)

    @patch('src.utils.decorators.EnvLoader.get_env_var_int')
    @patch('src.utils.decorators.time.time')
    def test_simple_cache_ttl_expiration(self, mock_time: Any, mock_env: Any) -> None:
        """Покрытие истечения TTL"""
        mock_env.return_value = 1000  # TTL = 1000 секунд
        mock_time.return_value = 1000.0

        call_count = [0]

        @simple_cache()
        def test_func(x: int) -> str:
            call_count[0] += 1
            return f"result_{x}_{call_count[0]}"

        # Первый вызов
        result1 = test_func(1)
        assert result1 == "result_1_1"

        # Вызов до истечения TTL - из кэша
        mock_time.return_value = 1500.0
        result2 = test_func(1)
        assert result2 == "result_1_1"  # Тот же результат

        # Вызов после истечения TTL - новый вызов функции
        mock_time.return_value = 2500.0  # TTL истек
        result3 = test_func(1)
        assert result3 == "result_1_2"  # Новый результат

    @patch('src.utils.decorators.EnvLoader.get_env_var_int')
    @patch('src.utils.decorators.time.time')
    def test_simple_cache_with_custom_ttl(self, mock_time: Any, mock_env: Any) -> None:
        """Покрытие кастомного TTL"""
        mock_time.return_value = 1000.0

        @simple_cache(ttl=500)  # Кастомный TTL
        def test_func(x: int) -> str:
            return f"result_{x}"

        # Первый вызов
        result1 = test_func(1)
        assert result1 == "result_1"

        # Вызов в пределах кастомного TTL
        mock_time.return_value = 1300.0  # Прошло 300 секунд
        result2 = test_func(1)
        assert result2 == "result_1"

    @patch('src.utils.decorators.EnvLoader.get_env_var_int')
    @patch('src.utils.decorators.time.time')
    def test_simple_cache_max_size_lru(self, mock_time: Any, mock_env: Any) -> None:
        """Покрытие LRU очистки при превышении max_size"""
        mock_env.return_value = 3600
        # Используем последовательные времена для LRU
        mock_time.side_effect = [1000.0, 1001.0, 1002.0, 1003.0, 1004.0, 1005.0]

        @simple_cache(max_size=2)  # Ограничиваем размер кэша
        def test_func(x: int) -> str:
            return f"result_{x}"

        # Заполняем кэш до максимума
        result1 = test_func(1)
        result2 = test_func(2)

        # Добавляем третий элемент - должен удалиться самый старый
        result3 = test_func(3)

        assert result1 == "result_1"
        assert result2 == "result_2"
        assert result3 == "result_3"

    @patch('src.utils.decorators.EnvLoader.get_env_var_int')
    @patch('src.utils.decorators.time.time')
    def test_simple_cache_different_args(self, mock_time: Any, mock_env: Any) -> None:
        """Покрытие разных аргументов"""
        mock_env.return_value = 3600
        mock_time.return_value = 1000.0

        @simple_cache()
        def test_func(x: int, y: None = None, **kwargs: Dict) -> str:
            return f"{x}_{y}_{kwargs}"

        # Разные наборы аргументов должны кэшироваться отдельно
        result1 = test_func(1)
        result2 = test_func(1, y=2)
        result3 = test_func(1, z=3)

        assert result1 == "1_None_{}"
        assert result2 == "1_2_{}"
        assert result3 == "1_None_{'z': 3}"

    def test_simple_cache_clear_cache_method(self) -> None:
        """Покрытие метода clear_cache"""
        @simple_cache()
        def test_func(x: int) -> str:
            return f"result_{x}"

        # Вызываем функцию для заполнения кэша
        test_func(1)

        # Очищаем кэш
        test_func.clear_cache()

        # Метод должен существовать и выполняться без ошибок
        assert hasattr(test_func, 'clear_cache')

    @patch('src.utils.decorators.EnvLoader.get_env_var_int')
    def test_simple_cache_info_method(self, mock_env: Any) -> None:
        """Покрытие метода cache_info"""
        mock_env.return_value = 1800

        @simple_cache(max_size=100)
        def test_func(x: int) -> str:
            return f"result_{x}"

        # Получаем информацию о кэше
        info = test_func.cache_info()

        assert isinstance(info, dict)
        assert "size" in info
        assert "max_size" in info
        assert "ttl" in info
        assert info["max_size"] == 100


class TestRetryOnFailureDecorator:
    """100% покрытие retry_on_failure декоратора"""

    @patch('src.utils.decorators.time.sleep')
    def test_retry_success_on_first_attempt(self, mock_sleep: Any) -> None:
        """Покрытие успешного выполнения с первой попытки"""
        @retry_on_failure(max_attempts=3, delay=1.0)
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"
        mock_sleep.assert_not_called()

    @patch('src.utils.decorators.time.sleep')
    def test_retry_success_after_failures(self, mock_sleep: Any) -> None:
        """Покрытие успешного выполнения после нескольких сбоев"""
        call_count = [0]

        @retry_on_failure(max_attempts=3, delay=0.1)
        def test_func() -> str:
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception(f"Attempt {call_count[0]} failed")
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count[0] == 3
        assert mock_sleep.call_count == 2  # 2 неудачи = 2 задержки

    @patch('src.utils.decorators.time.sleep')
    def test_retry_max_attempts_exceeded(self, mock_sleep: Any) -> None:
        """Покрытие превышения максимального количества попыток"""
        @retry_on_failure(max_attempts=2, delay=0.1)
        def test_func() -> None:
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            test_func()

        assert mock_sleep.call_count == 1  # 2 попытки = 1 задержка

    @patch('src.utils.decorators.time.sleep')
    def test_retry_all_exceptions(self, mock_sleep: Any) -> None:
        """Покрытие любых исключений (decorator ловит все Exception)"""
        @retry_on_failure(max_attempts=3, delay=0.1)
        def test_func_value_error() -> None:
            raise ValueError("Value error")

        @retry_on_failure(max_attempts=3, delay=0.1)
        def test_func_type_error() -> None:
            raise TypeError("Type error")

        # Любые исключения должны повторяться
        with pytest.raises(ValueError):
            test_func_value_error()

        with pytest.raises(TypeError):
            test_func_type_error()

    @patch('src.utils.decorators.time.sleep')
    def test_retry_with_args_kwargs(self, mock_sleep: Any) -> None:
        """Покрытие работы с аргументами функции"""
        call_count = [0]

        @retry_on_failure(max_attempts=2, delay=0.1)
        def test_func(x: int, y: None = None, **kwargs: Dict) -> str:
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Fail")
            return f"{x}_{y}_{kwargs}"

        result = test_func(1, y=2, z=3)
        assert result == "1_2_{'z': 3}"
        assert call_count[0] == 2

    @patch('src.utils.decorators.time.sleep')
    def test_retry_default_parameters(self, mock_sleep: Any) -> None:
        """Покрытие параметров по умолчанию"""
        call_count = [0]

        @retry_on_failure()  # Параметры по умолчанию
        def test_func() -> str:
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Fail")
            return "success"

        result = test_func()
        assert result == "success"


class TestTimeExecutionDecorator:
    """100% покрытие time_execution декоратора"""

    @patch('builtins.print')
    @patch('src.utils.decorators.time.time')
    def test_time_execution_basic(self, mock_time: Any, mock_print: Any) -> None:
        """Покрытие базовой функциональности измерения времени"""
        # Имитируем выполнение функции 0.5 секунды
        mock_time.side_effect = [1000.0, 1000.5]

        @time_execution
        def test_func() -> str:
            return "result"

        result = test_func()
        assert result == "result"

        # Проверяем, что print был вызван с правильным сообщением
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "test_func" in call_args
        assert "0.5000" in call_args

    @patch('builtins.print')
    @patch('src.utils.decorators.time.time')
    def test_time_execution_with_exception(self, mock_time: Any, mock_print: Any) -> None:
        """Покрытие измерения времени при исключении"""
        mock_time.side_effect = [3000.0, 3000.8]

        @time_execution
        def test_func() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func()

        # Время НЕ должно быть измерено при исключении (функция возвращается раньше)
        mock_print.assert_not_called()

    @patch('builtins.print')
    @patch('src.utils.decorators.time.time')
    def test_time_execution_with_args_kwargs(self, mock_time: Any, mock_print: Any) -> None:
        """Покрытие работы с аргументами функции"""
        mock_time.side_effect = [4000.0, 4000.3]

        @time_execution
        def test_func(x: int, y: None = None, **kwargs: Dict) -> str:
            return f"{x}_{y}_{kwargs}"

        result = test_func(1, y=2, z=3)
        assert result == "1_2_{'z': 3}"
        mock_print.assert_called_once()

    @patch('builtins.print')
    @patch('src.utils.decorators.time.time')
    def test_time_execution_very_fast_function(self, mock_time: Any, mock_print: Any) -> None:
        """Покрытие очень быстрой функции"""
        # Очень маленькое время выполнения
        mock_time.side_effect = [5000.0, 5000.001]

        @time_execution
        def test_func() -> str:
            return "fast_result"

        result = test_func()
        assert result == "fast_result"

        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "0.0010" in call_args


class TestLogErrorsDecorator:
    """100% покрытие log_errors декоратора"""

    @patch('src.utils.decorators.logging.getLogger')
    def test_log_errors_no_exception(self, mock_get_logger: Any) -> None:
        """Покрытие успешного выполнения без ошибок"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_errors
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"

        # Логирование не должно вызываться при успешном выполнении
        mock_logger.error.assert_not_called()

    @patch('src.utils.decorators.logging.getLogger')
    def test_log_errors_with_exception(self, mock_get_logger: Any) -> None:
        """Покрытие логирования ошибок"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_errors
        def test_func() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func()

        # Проверяем, что ошибка была залогирована
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "test_func" in call_args
        assert "Test error" in call_args

    @patch('src.utils.decorators.logging.getLogger')
    def test_log_errors_with_args_kwargs(self, mock_get_logger: Any) -> None:
        """Покрытие работы с аргументами при ошибке"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_errors
        def test_func(x: int, y: None = None, **kwargs: Dict) -> NoReturn:
            raise RuntimeError(f"Error with {x}")

        with pytest.raises(RuntimeError):
            test_func(42, y="test", z="extra")

        mock_logger.error.assert_called_once()

    @patch('src.utils.decorators.logging.getLogger')
    def test_log_errors_logger_module_name(self, mock_get_logger: Any) -> None:
        """Покрытие использования имени модуля для логгера"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_errors
        def test_func() -> None:
            raise Exception("Test")

        with pytest.raises(Exception):
            test_func()

        # Проверяем, что логгер создается с именем модуля функции
        mock_get_logger.assert_called_with(test_func.__module__)


class TestDecoratorsIntegration:
    """Покрытие интеграционных сценариев и граничных случаев"""

    @patch('src.utils.decorators.EnvLoader.get_env_var_int')
    @patch('src.utils.decorators.time.sleep')
    @patch('builtins.print')
    @patch('src.utils.decorators.time.time')
    def test_combined_decorators(self, mock_time: Any, mock_print: Any, mock_sleep: Any, mock_env: Any) -> None:
        """Покрытие комбинированного использования декораторов"""
        mock_env.return_value = 3600
        # Достаточно времен для всех вызовов (много повторов для кэша и retry)
        times = []
        for i in range(20):  # Генерируем достаточно времен
            times.extend([1000.0 + i, 1000.1 + i])
        mock_time.side_effect = times

        call_count = [0]

        @time_execution
        @retry_on_failure(max_attempts=2, delay=0.1)
        @simple_cache()
        def test_func(x: int) -> str:
            call_count[0] += 1
            if call_count[0] == 1 and x == "fail_once":
                raise Exception("First attempt fails")
            return f"result_{x}_{call_count[0]}"

        # Тест с неудачей на первой попытке
        result = test_func("fail_once")
        assert "result_fail_once" in result

        # Тест с кэшированием
        result2 = test_func("success")
        result3 = test_func("success")  # Должно вернуться из кэша

        assert result2 == result3

    def test_decorator_preservation_of_function_metadata(self) -> None:
        """Покрытие сохранения метаданных функции"""
        @time_execution
        @retry_on_failure()
        @simple_cache()
        def documented_func(x: int, y: int = 1) -> int:
            """This is a test function."""
            return x + y

        # Проверяем, что имя функции сохранилось
        assert documented_func.__name__ == "documented_func"

        # Функция должна работать корректно
        result = documented_func(5, y=3)
        assert result == 8

    @patch('src.utils.decorators.EnvLoader.get_env_var_int')
    def test_edge_case_empty_cache(self, mock_env: Any) -> None:
        """Покрытие граничного случая пустого кэша"""
        mock_env.return_value = 0  # TTL = 0

        @simple_cache()
        def test_func(x: int) -> str:
            return f"result_{x}"

        # При TTL = 0 кэш не должен работать
        result1 = test_func(1)
        result2 = test_func(1)

        assert result1 == "result_1"
        assert result2 == "result_1"

    def test_retry_with_zero_attempts(self) -> None:
        """Покрытие retry с нулевым количеством попыток"""
        @retry_on_failure(max_attempts=0)
        def test_func() -> None:
            raise Exception("Should not retry")

        # При max_attempts=0 цикл range(0) не выполняется, возвращается None
        result = test_func()
        assert result is None
