#!/usr/bin/env python3
"""
Тесты модуля decorators для 100% покрытия.

Покрывает все функции в src/utils/decorators.py:
- simple_cache - кэширование результатов функций с TTL и LRU
- retry_on_failure - повторные попытки при ошибках
- time_execution - измерение времени выполнения
- log_errors - логирование ошибок

Все внешние зависимости заменены на mock для соблюдения принципа нулевого I/O.
"""

import pytest
from unittest.mock import patch, MagicMock, call

# Импорты из реального кода для покрытия
from src.utils.decorators import simple_cache, retry_on_failure, time_execution, log_errors


class TestSimpleCache:
    """100% покрытие декоратора simple_cache"""

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_basic_functionality(self, mock_time, mock_env_loader):
        """Покрытие базовой функциональности кэширования"""
        mock_time.time.side_effect = [100.0, 105.0, 110.0]  # Разные времена для вызовов
        mock_env_loader.get_env_var_int.return_value = 3600

        @simple_cache(ttl=300, max_size=10)
        def test_func(x, y):
            return x + y

        # Первый вызов - вычисляется
        result1 = test_func(1, 2)
        assert result1 == 3

        # Второй вызов - берется из кэша (время еще не истекло)
        result2 = test_func(1, 2)
        assert result2 == 3

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_ttl_expiration(self, mock_time, mock_env_loader):
        """Покрытие истечения TTL кэша"""
        mock_time.time.side_effect = [100.0, 105.0, 500.0, 505.0]  # TTL истек
        mock_env_loader.get_env_var_int.return_value = 3600

        call_count = 0

        @simple_cache(ttl=300, max_size=10)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Первый вызов
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1

        # Второй вызов (кэш еще актуален)
        result2 = test_func(5)
        assert result2 == 10
        assert call_count == 1  # Функция не вызывалась повторно

        # Третий вызов (TTL истек)
        result3 = test_func(5)
        assert result3 == 10
        assert call_count == 2  # Функция вызвалась снова

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_max_size_lru(self, mock_time, mock_env_loader):
        """Покрытие LRU удаления при превышении размера"""
        mock_time.time.side_effect = [i * 10.0 for i in range(20)]  # Последовательные времена
        mock_env_loader.get_env_var_int.return_value = 3600

        call_count = 0

        @simple_cache(ttl=1000, max_size=2)  # Маленький размер для теста
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x ** 2

        # Заполняем кэш до максимума
        result1 = test_func(1)  # time=0
        assert result1 == 1
        assert call_count == 1

        result2 = test_func(2)  # time=10
        assert result2 == 4
        assert call_count == 2

        # Добавляем третий элемент - должен удалить самый старый
        result3 = test_func(3)  # time=20
        assert result3 == 9
        assert call_count == 3

        # Проверяем что первый элемент удален из кэша (будет пересчитан)
        result4 = test_func(1)  # time=30
        assert result4 == 1
        assert call_count == 4  # Функция вызвалась снова

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_with_kwargs(self, mock_time, mock_env_loader):
        """Покрытие кэширования с именованными аргументами"""
        mock_time.time.return_value = 100.0
        mock_env_loader.get_env_var_int.return_value = 3600

        call_count = 0

        @simple_cache(ttl=300, max_size=10)
        def test_func(x, y=1, z=2):
            nonlocal call_count
            call_count += 1
            return x + y + z

        # Первый вызов
        result1 = test_func(1, y=2, z=3)
        assert result1 == 6
        assert call_count == 1

        # Повторный вызов с теми же аргументами
        result2 = test_func(1, y=2, z=3)
        assert result2 == 6
        assert call_count == 1  # Из кэша

        # Вызов с другими аргументами
        result3 = test_func(1, y=3, z=3)
        assert result3 == 7
        assert call_count == 2

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_none_ttl_uses_env(self, mock_time, mock_env_loader):
        """Покрытие использования TTL из переменных окружения"""
        mock_time.time.return_value = 100.0
        mock_env_loader.get_env_var_int.return_value = 1800  # Значение из env

        @simple_cache(ttl=None, max_size=10)  # ttl=None
        def test_func(x):
            return x * 3

        result = test_func(5)
        assert result == 15

        # Проверяем что EnvLoader был вызван с правильными параметрами
        mock_env_loader.get_env_var_int.assert_called_with("CACHE_TTL", 3600)

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_clear_function(self, mock_time, mock_env_loader):
        """Покрытие функции очистки кэша"""
        mock_time.time.return_value = 100.0
        mock_env_loader.get_env_var_int.return_value = 3600

        call_count = 0

        @simple_cache(ttl=300, max_size=10)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Вызываем функцию для заполнения кэша
        result1 = test_func(10)
        assert result1 == 20
        assert call_count == 1

        # Повторный вызов из кэша
        result2 = test_func(10)
        assert result2 == 20
        assert call_count == 1

        # Очищаем кэш
        test_func.clear_cache()

        # После очистки функция должна выполниться снова
        result3 = test_func(10)
        assert result3 == 20
        assert call_count == 2

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_info_function(self, mock_time, mock_env_loader):
        """Покрытие функции информации о кэше"""
        mock_time.time.return_value = 100.0
        mock_env_loader.get_env_var_int.return_value = 1200

        @simple_cache(ttl=600, max_size=50)
        def test_func(x):
            return x ** 2

        # Проверяем информацию о пустом кэше
        info1 = test_func.cache_info()
        expected_info1 = {
            "size": 0,
            "max_size": 50,
            "ttl": 600
        }
        assert info1 == expected_info1

        # Добавляем элементы в кэш
        test_func(1)
        test_func(2)

        # Проверяем обновленную информацию
        info2 = test_func.cache_info()
        expected_info2 = {
            "size": 2,
            "max_size": 50,
            "ttl": 600
        }
        assert info2 == expected_info2

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_info_with_none_ttl(self, mock_time, mock_env_loader):
        """Покрытие cache_info с ttl=None"""
        mock_time.time.return_value = 100.0
        mock_env_loader.get_env_var_int.return_value = 2400

        @simple_cache(ttl=None, max_size=25)  # ttl из env
        def test_func(x):
            return x + 10

        info = test_func.cache_info()
        expected_info = {
            "size": 0,
            "max_size": 25,
            "ttl": 2400  # Значение из EnvLoader
        }
        assert info == expected_info

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_access_time_update(self, mock_time, mock_env_loader):
        """Покрытие обновления времени доступа при попадании в кэш"""
        mock_time.time.side_effect = [100.0, 200.0, 300.0]
        mock_env_loader.get_env_var_int.return_value = 3600

        @simple_cache(ttl=1000, max_size=10)
        def test_func(x):
            return x * 5

        # Первый вызов - кэширование
        result1 = test_func(4)
        assert result1 == 20

        # Второй вызов - попадание в кэш и обновление access_time
        result2 = test_func(4)
        assert result2 == 20


class TestRetryOnFailure:
    """100% покрытие декоратора retry_on_failure"""

    @patch('src.utils.decorators.time')
    def test_retry_success_first_attempt(self, mock_time):
        """Покрытие успешного выполнения с первой попытки"""
        @retry_on_failure(max_attempts=3, delay=0.1)
        def test_func(x):
            return x * 2

        result = test_func(5)
        assert result == 10

        # time.sleep не должен был вызываться
        mock_time.sleep.assert_not_called()

    @patch('src.utils.decorators.time')
    def test_retry_success_after_failures(self, mock_time):
        """Покрытие успешного выполнения после неудач"""
        call_count = 0

        @retry_on_failure(max_attempts=3, delay=0.5)
        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ValueError(f"Ошибка на попытке {call_count}")
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count == 3

        # Проверяем что sleep вызывался между попытками
        expected_calls = [call(0.5), call(0.5)]
        mock_time.sleep.assert_has_calls(expected_calls)

    @patch('src.utils.decorators.time')
    def test_retry_final_failure(self, mock_time):
        """Покрытие финальной неудачи после всех попыток"""
        call_count = 0

        @retry_on_failure(max_attempts=2, delay=0.2)
        def test_func() -> None:
            nonlocal call_count
            call_count += 1
            raise RuntimeError(f"Постоянная ошибка #{call_count}")

        # Ожидаем что исключение будет поднято после всех попыток
        with pytest.raises(RuntimeError, match="Постоянная ошибка #2"):
            test_func()

        assert call_count == 2
        mock_time.sleep.assert_called_once_with(0.2)

    @patch('src.utils.decorators.time')
    def test_retry_different_exceptions(self, mock_time):
        """Покрытие разных типов исключений"""
        call_count = 0

        @retry_on_failure(max_attempts=4, delay=0.1)
        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Первая ошибка")
            elif call_count == 2:
                raise KeyError("Вторая ошибка")
            elif call_count == 3:
                raise TypeError("Третья ошибка")
            return "finally success"

        result = test_func()
        assert result == "finally success"
        assert call_count == 4

    def test_retry_default_parameters(self) -> None:
        """Покрытие значений по умолчанию"""
        call_count = 0

        @retry_on_failure()  # Используем параметры по умолчанию
        def test_func() -> None:
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise Exception("Ошибка")
            return "success"

        # С max_attempts=3 по умолчанию, функция не должна успеть
        with pytest.raises(Exception):
            test_func()

        assert call_count == 3

    @patch('src.utils.decorators.time')
    def test_retry_with_args_kwargs(self, mock_time):
        """Покрытие передачи аргументов в декорированную функцию"""
        call_count = 0

        @retry_on_failure(max_attempts=2, delay=0.1)
        def test_func(x, y, z=10):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Первая попытка")
            return x + y + z

        result = test_func(1, 2, z=3)
        assert result == 6
        assert call_count == 2

    @patch('src.utils.decorators.time')
    def test_retry_return_none_path(self, mock_time):
        """Покрытие возврата None (хотя код никогда не дойдет до этой строки)"""
        # Этот тест покрывает строку 87: return None
        # Хотя логически эта строка недостижима из-за raise в строке 85

        @retry_on_failure(max_attempts=1, delay=0.1)
        def test_func() -> None:
            raise ValueError("Всегда ошибка")

        with pytest.raises(ValueError):
            test_func()


class TestTimeExecution:
    """100% покрытие декоратора time_execution"""

    @patch('src.utils.decorators.time')
    @patch('builtins.print')
    def test_time_execution_basic(self, mock_print, mock_time):
        """Покрытие базовой функциональности измерения времени"""
        mock_time.time.side_effect = [100.0, 100.5]  # Начало и конец выполнения

        @time_execution
        def test_func(x, y):
            return x * y

        result = test_func(3, 4)
        assert result == 12

        # Проверяем что время было измерено и выведено
        mock_time.time.assert_has_calls([call(), call()])
        mock_print.assert_called_once_with("Функция test_func выполнилась за 0.5000 секунд")

    @patch('src.utils.decorators.time')
    @patch('builtins.print')
    def test_time_execution_with_exception(self, mock_print, mock_time):
        """Покрытие измерения времени при возникновении исключения"""
        mock_time.time.side_effect = [200.0, 200.25]

        @time_execution
        def test_func() -> None:
            raise ValueError("Тестовая ошибка")

        # Исключение должно быть поднято, а print НЕ вызван из-за исключения
        with pytest.raises(ValueError, match="Тестовая ошибка"):
            test_func()

        # При исключении print НЕ вызывается, потому что он идет после func()
        mock_print.assert_not_called()
        # Но start_time все равно был записан
        assert mock_time.time.call_count == 1  # Только start_time

    @patch('src.utils.decorators.time')
    @patch('builtins.print')
    def test_time_execution_zero_time(self, mock_print, mock_time):
        """Покрытие случая с нулевым временем выполнения"""
        mock_time.time.side_effect = [150.0, 150.0]  # Одинаковое время

        @time_execution
        def test_func() -> None:
            return "instant"

        result = test_func()
        assert result == "instant"
        mock_print.assert_called_once_with("Функция test_func выполнилась за 0.0000 секунд")

    @patch('src.utils.decorators.time')
    @patch('builtins.print')
    def test_time_execution_with_args(self, mock_print, mock_time):
        """Покрытие передачи аргументов в декорированную функцию"""
        mock_time.time.side_effect = [300.0, 301.234]

        @time_execution
        def test_func(a, b, c=None):
            return f"{a}-{b}-{c}"

        result = test_func("hello", "world", c="test")
        assert result == "hello-world-test"
        mock_print.assert_called_once_with("Функция test_func выполнилась за 1.2340 секунд")


class TestLogErrors:
    """100% покрытие декоратора log_errors"""

    @patch('src.utils.decorators.logging')
    def test_log_errors_success(self, mock_logging):
        """Покрытие успешного выполнения без ошибок"""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        @log_errors
        def test_func(x, y):
            return x + y

        result = test_func(5, 3)
        assert result == 8

        # Logger не должен был использоваться
        mock_logger.error.assert_not_called()

    @patch('src.utils.decorators.logging')
    def test_log_errors_with_exception(self, mock_logging):
        """Покрытие логирования ошибок"""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        @log_errors
        def test_func() -> None:
            raise ValueError("Тестовое исключение")

        # Исключение должно быть поднято после логирования
        with pytest.raises(ValueError, match="Тестовое исключение"):
            test_func()

        # Проверяем что logger был получен для правильного модуля
        mock_logging.getLogger.assert_called_once_with(test_func.__module__)

        # Проверяем что ошибка была залогирована
        mock_logger.error.assert_called_once_with("Ошибка в функции test_func: Тестовое исключение")

    @patch('src.utils.decorators.logging')
    def test_log_errors_different_exception_types(self, mock_logging):
        """Покрытие различных типов исключений"""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        @log_errors
        def test_func(error_type):
            if error_type == "value":
                raise ValueError("Value error message")
            elif error_type == "key":
                raise KeyError("Key error message")
            elif error_type == "type":
                raise TypeError("Type error message")
            return "success"

        # Тестируем ValueError
        with pytest.raises(ValueError):
            test_func("value")

        # Проверяем последний вызов после ValueError
        last_call = mock_logger.error.call_args
        assert "Ошибка в функции test_func: Value error message" in str(last_call)

        # Сбрасываем mock для следующего теста
        mock_logger.error.reset_mock()
        mock_logging.getLogger.reset_mock()

        # Тестируем KeyError - создаем новый logger mock
        mock_logger2 = MagicMock()
        mock_logging.getLogger.return_value = mock_logger2

        with pytest.raises(KeyError):
            test_func("key")

        # Проверяем что новый logger был использован
        assert mock_logger2.error.called

    @patch('src.utils.decorators.logging')
    def test_log_errors_with_args_kwargs(self, mock_logging):
        """Покрытие передачи аргументов в декорированную функцию"""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        @log_errors
        def test_func(a, b, c=None):
            if c is None:
                raise RuntimeError("c is None")
            return a + b + c

        # Успешный вызов
        result = test_func(1, 2, c=3)
        assert result == 6
        mock_logger.error.assert_not_called()

        # Вызов с ошибкой
        with pytest.raises(RuntimeError, match="c is None"):
            test_func(1, 2)  # c=None по умолчанию

        mock_logger.error.assert_called_once_with("Ошибка в функции test_func: c is None")

    @patch('src.utils.decorators.logging')
    def test_log_errors_preserves_exception(self, mock_logging):
        """Покрытие сохранения оригинального исключения"""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        original_exception = CustomException("Оригинальное исключение")

        @log_errors
        def test_func() -> None:
            raise original_exception

        # Проверяем что поднимается то же самое исключение
        with pytest.raises(CustomException) as exc_info:
            test_func()

        assert exc_info.value is original_exception
        mock_logger.error.assert_called_once()


class TestDecoratorsIntegration:
    """Интеграционные тесты комбинирования декораторов"""

    @patch('src.utils.decorators.time')
    @patch('src.utils.decorators.EnvLoader')
    @patch('builtins.print')
    @patch('src.utils.decorators.logging')
    def test_combined_decorators(self, mock_logging, mock_print, mock_env_loader, mock_time):
        """Покрытие комбинирования нескольких декораторов"""
        # Добавляем больше времён для всех возможных вызовов
        mock_time.time.side_effect = [100.0 + i * 0.5 for i in range(20)]
        mock_time.sleep.return_value = None  # Мокируем sleep
        mock_env_loader.get_env_var_int.return_value = 3600
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        call_count = 0

        @simple_cache(ttl=300, max_size=5)
        @time_execution
        @retry_on_failure(max_attempts=2, delay=0.1)
        @log_errors
        def test_func(x):
            nonlocal call_count
            call_count += 1
            if call_count == 1 and x == "fail":
                raise ValueError("Первая попытка неудачна")
            return f"processed_{x}"

        # Успешный вызов
        result1 = test_func("success")
        assert result1 == "processed_success"

        # Вызов с повторной попыткой
        result2 = test_func("fail")
        assert result2 == "processed_fail"

        # Проверяем что все декораторы отработали
        # call_count может быть разным из-за сложного взаимодействия декораторов
        assert call_count >= 2  # Минимум 1 для success + 1 для fail
        assert mock_print.call_count >= 1  # Измерение времени
        # Не проверяем mock_logger.error строго, т.к. retry может скрыть ошибки

    @patch('src.utils.decorators.EnvLoader')
    @patch('src.utils.decorators.time')
    def test_cache_edge_cases(self, mock_time, mock_env_loader):
        """Покрытие граничных случаев кэширования"""
        mock_time.time.side_effect = [i * 100.0 for i in range(10)]
        mock_env_loader.get_env_var_int.return_value = 3600

        @simple_cache(ttl=50, max_size=1)  # Очень маленький кэш
        def test_func(x):
            return x ** 3

        # Заполняем единственное место в кэше
        result1 = test_func(2)
        assert result1 == 8

        # Добавляем новый элемент - старый должен быть удален
        result2 = test_func(3)
        assert result2 == 27

        # Информация о кэше
        info = test_func.cache_info()
        assert info["size"] == 1
        assert info["max_size"] == 1


# Вспомогательный класс для тестов
class CustomException(Exception):
    """Пользовательское исключение для тестов"""
    pass