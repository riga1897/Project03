
"""
Тесты для модуля decorators
"""

import pytest
import time
from unittest.mock import patch, Mock
from src.utils.decorators import simple_cache


class TestDecorators:
    """Тесты для декораторов"""

    def test_simple_cache_basic_functionality(self):
        """Тест базовой функциональности кэша"""
        call_count = 0
        
        @simple_cache()
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Первый вызов
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Второй вызов с теми же аргументами (должен использовать кэш)
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Функция не должна вызываться повторно

        # Вызов с другими аргументами
        result3 = expensive_function(3)
        assert result3 == 6
        assert call_count == 2

    def test_simple_cache_with_ttl(self):
        """Тест кэша с TTL"""
        call_count = 0
        
        @simple_cache(ttl=1)  # 1 секунда TTL
        def cached_function(x):
            nonlocal call_count
            call_count += 1
            return x * 3

        # Первый вызов
        result1 = cached_function(2)
        assert result1 == 6
        assert call_count == 1

        # Второй вызов (должен использовать кэш)
        result2 = cached_function(2)
        assert result2 == 6
        assert call_count == 1

        # Ждем истечения TTL
        time.sleep(1.1)

        # Третий вызов (кэш должен истечь)
        result3 = cached_function(2)
        assert result3 == 6
        assert call_count == 2

    def test_simple_cache_max_size(self):
        """Тест ограничения размера кэша"""
        call_count = 0
        
        @simple_cache(max_size=2)
        def cached_function(x):
            nonlocal call_count
            call_count += 1
            return x * 4

        # Заполняем кэш до лимита
        result1 = cached_function(1)  # call_count = 1
        result2 = cached_function(2)  # call_count = 2
        
        # Проверяем, что результаты кэшированы
        cached_function(1)  # call_count = 2 (из кэша)
        cached_function(2)  # call_count = 2 (из кэша)
        assert call_count == 2

        # Добавляем третий элемент (должен вытеснить первый)
        result3 = cached_function(3)  # call_count = 3
        assert call_count == 3

        # Проверяем, что первый элемент вытеснен
        cached_function(1)  # call_count = 4 (не из кэша)
        assert call_count == 4

    def test_simple_cache_with_kwargs(self):
        """Тест кэширования с именованными аргументами"""
        call_count = 0
        
        @simple_cache()
        def cached_function(x, multiplier=2):
            nonlocal call_count
            call_count += 1
            return x * multiplier

        # Вызовы с разными kwargs
        result1 = cached_function(5, multiplier=2)
        result2 = cached_function(5, multiplier=3)
        result3 = cached_function(5, multiplier=2)  # Должен использовать кэш

        assert result1 == 10
        assert result2 == 15
        assert result3 == 10
        assert call_count == 2  # Третий вызов из кэша

    def test_cache_clear_function(self):
        """Тест функции очистки кэша"""
        call_count = 0
        
        @simple_cache()
        def cached_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Заполняем кэш
        cached_function(1)
        cached_function(2)
        assert call_count == 2

        # Используем кэш
        cached_function(1)
        assert call_count == 2

        # Очищаем кэш
        cached_function.clear_cache()

        # Проверяем, что кэш очищен
        cached_function(1)
        assert call_count == 3

    def test_cache_info_function(self):
        """Тест функции получения информации о кэше"""
        @simple_cache(ttl=300, max_size=100)
        def cached_function(x):
            return x * 2

        # Проверяем информацию о кэше
        info = cached_function.cache_info()
        
        assert "size" in info
        assert "max_size" in info
        assert "ttl" in info
        assert info["max_size"] == 100
        assert info["ttl"] == 300
        assert info["size"] == 0  # Пустой кэш

        # Добавляем элемент в кэш
        cached_function(5)
        info = cached_function.cache_info()
        assert info["size"] == 1

    def test_simple_cache_with_env_variables(self):
        """Тест использования переменных окружения для TTL"""
        with patch('src.utils.env_loader.EnvLoader.get_env_var_int') as mock_env:
            mock_env.return_value = 1800  # 30 минут

            @simple_cache()  # TTL не указан, должен использоваться из переменной окружения
            def cached_function(x):
                return x * 2

            info = cached_function.cache_info()
            assert info["ttl"] == 1800

    def test_cache_with_complex_arguments(self):
        """Тест кэширования с комплексными аргументами"""
        call_count = 0
        
        @simple_cache()
        def cached_function(data_list, data_dict):
            nonlocal call_count
            call_count += 1
            return sum(data_list) + sum(data_dict.values())

        # Первый вызов
        result1 = cached_function([1, 2, 3], {'a': 4, 'b': 5})
        assert result1 == 15
        assert call_count == 1

        # Второй вызов с теми же аргументами
        result2 = cached_function([1, 2, 3], {'a': 4, 'b': 5})
        assert result2 == 15
        assert call_count == 1  # Должен использовать кэш

        # Вызов с другими аргументами
        result3 = cached_function([1, 2], {'a': 4})
        assert result3 == 7
        assert call_count == 2
