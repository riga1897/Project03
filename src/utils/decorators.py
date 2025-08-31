import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

from .env_loader import EnvLoader


def simple_cache(ttl: Optional[int] = None, max_size: int = 1000) -> Callable:
    """
    Декоратор для кэширования результатов функций в памяти с ограничением размера
    :param ttl: Время жизни кэша в секундах (по умолчанию 1 час)
    :param max_size: Максимальный размер кэша (по умолчанию 1000 элементов)
    :return: Декорированная функция
    """

    def decorator(func: Callable) -> Callable:
        cache: Dict[Tuple, Tuple[float, Any]] = {}
        access_times: Dict[Tuple, float] = {}  # Для LRU очистки

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Получаем TTL из переменных окружения или используем переданное значение
            actual_ttl = ttl if ttl is not None else EnvLoader.get_env_var_int("CACHE_TTL", 3600)
            current_time = time.time()

            cache_key = (args, frozenset(kwargs.items()))

            # Проверяем существующий кэш
            if cache_key in cache:
                timestamp, result = cache[cache_key]
                if current_time - timestamp < actual_ttl:
                    access_times[cache_key] = current_time  # Обновляем время доступа
                    return result
                else:
                    # Удаляем устаревший элемент
                    del cache[cache_key]
                    if cache_key in access_times:
                        del access_times[cache_key]

            # Проверяем размер кэша
            if len(cache) >= max_size:
                # Удаляем самый старый элемент (LRU)
                oldest_key = min(access_times.keys(), key=lambda k: access_times[k])
                del cache[oldest_key]
                del access_times[oldest_key]

            # Выполняем функцию и кэшируем результат
            result = func(*args, **kwargs)
            cache[cache_key] = (current_time, result)
            access_times[cache_key] = current_time
            return result

        def clear_cache() -> None:
            """Очистка кэша функции"""
            cache.clear()
            access_times.clear()

        def cache_info() -> Dict[str, Any]:
            """Информация о состоянии кэша"""
            return {
                "size": len(cache),
                "max_size": max_size,
                "ttl": ttl if ttl is not None else EnvLoader.get_env_var_int("CACHE_TTL", 3600),
            }

        wrapper.clear_cache = clear_cache
        wrapper.cache_info = cache_info
        return wrapper

    return decorator


def retry_on_failure(max_attempts=3, delay=1.0):
    """Декоратор для повторных попыток при ошибке"""

    def decorator(func):
        @wraps(func)
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

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {execution_time:.4f} секунд")
        return result

    return wrapper


def log_errors(func):
    """Декоратор для логирования ошибок"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__module__)
            logger.error(f"Ошибка в функции {func.__name__}: {e}")
            raise e

    return wrapper
