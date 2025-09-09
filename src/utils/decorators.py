import logging
import time
import json
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

from .env_loader import EnvLoader


def _make_hashable_key(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
    """
    Создает хешируемый ключ из аргументов функции, включая нехешируемые типы
    
    Args:
        args: Позиционные аргументы
        kwargs: Именованные аргументы
        
    Returns:
        str: Безопасный хешируемый ключ
    """
    def make_serializable(obj: Any) -> Any:
        """Рекурсивно преобразует объект в сериализуемый вид"""
        if isinstance(obj, (dict, list)):
            # Для словарей и списков используем JSON сериализацию
            try:
                return json.dumps(obj, sort_keys=True, default=str)
            except (TypeError, ValueError):
                # Если JSON не работает, конвертируем в строку
                return str(obj)
        elif isinstance(obj, (set, frozenset, tuple)):
            # Для множеств и кортежей сортируем и преобразуем элементы
            try:
                return tuple(sorted(make_serializable(item) for item in obj))
            except TypeError:
                return str(obj)
        else:
            # Для примитивных типов возвращаем как есть
            return obj
    
    try:
        # Преобразуем все аргументы в сериализуемый вид
        safe_args = tuple(make_serializable(arg) for arg in args)
        safe_kwargs = {k: make_serializable(v) for k, v in kwargs.items()}
        
        # Создаем единый ключ из всех данных
        key_data = {
            'args': safe_args,
            'kwargs': safe_kwargs
        }
        
        return json.dumps(key_data, sort_keys=True, default=str)
        
    except Exception as e:
        # Если все еще не получается, используем строковое представление
        logging.warning(f"Не удалось создать безопасный ключ кэша: {e}, использую строковое представление")
        return str((args, kwargs))


def simple_cache(ttl: Optional[int] = None, max_size: int = 1000) -> Callable[[Callable[..., Any]], Any]:
    """
    Декоратор для кэширования результатов функций в памяти с ограничением размера
    :param ttl: Время жизни кэша в секундах (по умолчанию 1 час)
    :param max_size: Максимальный размер кэша (по умолчанию 1000 элементов)
    :return: Декорированная функция
    """

    def decorator(func: Callable[..., Any]) -> Any:
        """Внутренняя функция-декоратор для кэширования."""
        cache: Dict[str, Tuple[float, Any]] = {}  # ИСПРАВЛЕНО: ключи теперь строки
        access_times: Dict[str, float] = {}  # Для LRU очистки

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Обёртка для кэширования результатов функций в памяти."""
            # Получаем TTL из переменных окружения или используем переданное значение
            actual_ttl = ttl if ttl is not None else EnvLoader.get_env_var_int("CACHE_TTL", 3600)
            current_time = time.time()

            # ИСПРАВЛЕНО: Создаем безопасный ключ кэша для нехешируемых типов
            cache_key = _make_hashable_key(args, kwargs)

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

        # Добавляем атрибуты с правильной типизацией
        setattr(wrapper, "clear_cache", clear_cache)
        setattr(wrapper, "cache_info", cache_info)
        return wrapper

    return decorator


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0) -> Callable:
    """Декоратор для повторных попыток при ошибке.

    Args:
        max_attempts: Максимальное количество попыток.
        delay: Задержка между попытками в секундах.

    Returns:
        Декорированная функция с логикой повторных попыток.
    """

    def decorator(func: Callable) -> Callable:
        """Внутренний декоратор для обработки повторных попыток.

        Args:
            func: Функция для декорирования.

        Returns:
            Обернутая функция с логикой повторных попыток.
        """

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Обёртка для повторных попыток при ошибках."""
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


def time_execution(func: Callable) -> Callable:
    """Декоратор для измерения времени выполнения.

    Args:
        func: Функция для декорирования.

    Returns:
        Декорированная функция с измерением времени выполнения.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Обёртка для измерения времени выполнения."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {execution_time:.4f} секунд")
        return result

    return wrapper


def log_errors(func: Callable) -> Callable:
    """Декоратор для логирования ошибок.

    Args:
        func: Функция для декорирования.

    Returns:
        Декорированная функция с логированием ошибок.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Обёртка для обработки и логирования ошибок."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__module__)
            logger.error(f"Ошибка в функции {func.__name__}: {e}")
            raise e

    return wrapper
