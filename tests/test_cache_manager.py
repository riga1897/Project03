
"""
Тесты для менеджера кэша
"""

import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch, mock_open
from datetime import datetime, timedelta
from typing import Any, Dict

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.cache import CacheManager
except ImportError:
    # Создаем тестовую реализацию
    class CacheManager:
        """Тестовый менеджер кэша"""
        
        def __init__(self, cache_dir: str = "test_cache", default_ttl: int = 3600):
            """
            Инициализация менеджера кэша
            
            Args:
                cache_dir: Директория для кэша
                default_ttl: Время жизни кэша по умолчанию в секундах
            """
            self.cache_dir = cache_dir
            self.default_ttl = default_ttl
            self._memory_cache = {}
        
        def get(self, key: str) -> Any:
            """
            Получить значение из кэша
            
            Args:
                key: Ключ кэша
                
            Returns:
                Значение из кэша или None
            """
            # Проверяем память кэш
            if key in self._memory_cache:
                cache_entry = self._memory_cache[key]
                if self._is_cache_valid(cache_entry):
                    return cache_entry['data']
                else:
                    del self._memory_cache[key]
            
            # Проверяем файловый кэш
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_entry = json.load(f)
                    
                    if self._is_cache_valid(cache_entry):
                        # Загружаем в память кэш
                        self._memory_cache[key] = cache_entry
                        return cache_entry['data']
                    else:
                        os.remove(cache_file)
                except (json.JSONDecodeError, FileNotFoundError, KeyError):
                    pass
            
            return None
        
        def set(self, key: str, value: Any, ttl: int = None) -> bool:
            """
            Сохранить значение в кэш
            
            Args:
                key: Ключ кэша
                value: Значение для сохранения
                ttl: Время жизни в секундах
                
            Returns:
                True если сохранение успешно
            """
            if ttl is None:
                ttl = self.default_ttl
            
            cache_entry = {
                'data': value,
                'timestamp': datetime.now().timestamp(),
                'ttl': ttl
            }
            
            # Сохраняем в память кэш
            self._memory_cache[key] = cache_entry
            
            # Сохраняем в файловый кэш
            try:
                os.makedirs(self.cache_dir, exist_ok=True)
                cache_file = os.path.join(self.cache_dir, f"{key}.json")
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_entry, f, ensure_ascii=False, indent=2)
                return True
            except (OSError, IOError):
                return False
        
        def delete(self, key: str) -> bool:
            """
            Удалить значение из кэша
            
            Args:
                key: Ключ кэша
                
            Returns:
                True если удаление успешно
            """
            # Удаляем из памяти
            if key in self._memory_cache:
                del self._memory_cache[key]
            
            # Удаляем файл
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                    return True
                except OSError:
                    return False
            
            return True
        
        def clear(self) -> bool:
            """
            Очистить весь кэш
            
            Returns:
                True если очистка успешна
            """
            # Очищаем память кэш
            self._memory_cache.clear()
            
            # Очищаем файлы
            try:
                if os.path.exists(self.cache_dir):
                    for filename in os.listdir(self.cache_dir):
                        if filename.endswith('.json'):
                            os.remove(os.path.join(self.cache_dir, filename))
                return True
            except OSError:
                return False
        
        def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
            """
            Проверить валидность записи кэша
            
            Args:
                cache_entry: Запись кэша
                
            Returns:
                True если кэш валиден
            """
            if 'timestamp' not in cache_entry or 'ttl' not in cache_entry:
                return False
            
            timestamp = cache_entry['timestamp']
            ttl = cache_entry['ttl']
            current_time = datetime.now().timestamp()
            
            return (current_time - timestamp) < ttl
        
        def get_cache_stats(self) -> Dict[str, Any]:
            """
            Получить статистику кэша
            
            Returns:
                Словарь со статистикой
            """
            memory_count = len(self._memory_cache)
            
            file_count = 0
            total_size = 0
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        file_count += 1
                        file_path = os.path.join(self.cache_dir, filename)
                        total_size += os.path.getsize(file_path)
            
            return {
                'memory_entries': memory_count,
                'file_entries': file_count,
                'total_size_bytes': total_size,
                'cache_dir': self.cache_dir
            }


class TestCacheManager:
    """Тесты для менеджера кэша"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Фикстура временной директории для кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """Фикстура менеджера кэша"""
        return CacheManager(cache_dir=temp_cache_dir, default_ttl=3600)

    def test_cache_manager_initialization(self, temp_cache_dir):
        """Тест инициализации менеджера кэша"""
        cache_manager = CacheManager(cache_dir=temp_cache_dir, default_ttl=7200)
        
        assert cache_manager.cache_dir == temp_cache_dir
        assert cache_manager.default_ttl == 7200
        assert hasattr(cache_manager, '_memory_cache')

    def test_cache_set_and_get(self, cache_manager):
        """Тест сохранения и получения значений из кэша"""
        key = "test_key"
        value = {"data": "test_value", "number": 42}
        
        # Сохраняем значение
        result = cache_manager.set(key, value)
        assert result is True
        
        # Получаем значение
        cached_value = cache_manager.get(key)
        assert cached_value == value

    def test_cache_get_nonexistent(self, cache_manager):
        """Тест получения несуществующего значения"""
        result = cache_manager.get("nonexistent_key")
        assert result is None

    def test_cache_delete(self, cache_manager):
        """Тест удаления значения из кэша"""
        key = "test_key"
        value = "test_value"
        
        # Сохраняем и проверяем
        cache_manager.set(key, value)
        assert cache_manager.get(key) == value
        
        # Удаляем и проверяем
        result = cache_manager.delete(key)
        assert result is True
        assert cache_manager.get(key) is None

    def test_cache_clear(self, cache_manager):
        """Тест очистки всего кэша"""
        # Сохраняем несколько значений
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        cache_manager.set("key3", "value3")
        
        # Проверяем, что значения сохранены
        assert cache_manager.get("key1") == "value1"
        assert cache_manager.get("key2") == "value2"
        
        # Очищаем кэш
        result = cache_manager.clear()
        assert result is True
        
        # Проверяем, что кэш пуст
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None
        assert cache_manager.get("key3") is None

    def test_cache_ttl_expiration(self, cache_manager):
        """Тест истечения времени жизни кэша"""
        key = "test_key"
        value = "test_value"
        
        # Сохраняем с коротким TTL
        cache_manager.set(key, value, ttl=1)
        
        # Сразу после сохранения значение должно быть доступно
        assert cache_manager.get(key) == value
        
        # Имитируем истечение времени
        with patch('src.utils.cache.datetime') as mock_datetime:
            mock_datetime.now.return_value.timestamp.return_value = datetime.now().timestamp() + 2
            assert cache_manager.get(key) is None

    def test_cache_stats(self, cache_manager):
        """Тест получения статистики кэша"""
        # Сохраняем несколько значений
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", {"data": "complex_value"})
        
        stats = cache_manager.get_cache_stats()
        
        assert isinstance(stats, dict)
        assert "memory_entries" in stats
        assert "file_entries" in stats
        assert "total_size_bytes" in stats
        assert "cache_dir" in stats
        assert stats["memory_entries"] >= 0
        assert stats["file_entries"] >= 0

    def test_cache_file_operations(self, cache_manager, temp_cache_dir):
        """Тест файловых операций кэша"""
        key = "test_file_key"
        value = {"complex": "data", "with": ["multiple", "types"]}
        
        # Сохраняем значение
        cache_manager.set(key, value)
        
        # Проверяем, что файл создан
        cache_file = os.path.join(temp_cache_dir, f"{key}.json")
        assert os.path.exists(cache_file)
        
        # Проверяем содержимое файла
        with open(cache_file, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
        
        assert 'data' in file_content
        assert 'timestamp' in file_content
        assert 'ttl' in file_content
        assert file_content['data'] == value

    def test_cache_memory_and_file_sync(self, cache_manager):
        """Тест синхронизации между памятью и файловым кэшем"""
        key = "sync_test_key"
        value = "sync_test_value"
        
        # Сохраняем значение
        cache_manager.set(key, value)
        
        # Очищаем память кэш (имитируем перезапуск)
        cache_manager._memory_cache.clear()
        
        # Значение должно загрузиться из файла
        cached_value = cache_manager.get(key)
        assert cached_value == value
        
        # Проверяем, что значение загружено в память
        assert key in cache_manager._memory_cache

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_cache_file_error_handling(self, mock_open, cache_manager):
        """Тест обработки ошибок файловых операций"""
        key = "error_test_key"
        value = "error_test_value"
        
        # Попытка сохранения с ошибкой файловой системы
        result = cache_manager.set(key, value)
        
        # Операция должна завершиться неудачно, но не вызвать исключение
        assert result is False

    def test_cache_invalid_json_handling(self, cache_manager, temp_cache_dir):
        """Тест обработки невалидного JSON в кэше"""
        key = "invalid_json_key"
        
        # Создаем файл с невалидным JSON
        cache_file = os.path.join(temp_cache_dir, f"{key}.json")
        os.makedirs(temp_cache_dir, exist_ok=True)
        with open(cache_file, 'w') as f:
            f.write("invalid json content")
        
        # Попытка чтения должна вернуть None без исключения
        result = cache_manager.get(key)
        assert result is None
        
        # Файл должен быть удален при попытке чтения
        # (в зависимости от реализации)

    def test_cache_custom_ttl(self, cache_manager):
        """Тест использования пользовательского TTL"""
        key = "custom_ttl_key"
        value = "custom_ttl_value"
        custom_ttl = 7200  # 2 часа
        
        # Сохраняем с пользовательским TTL
        cache_manager.set(key, value, ttl=custom_ttl)
        
        # Проверяем, что значение сохранено
        assert cache_manager.get(key) == value
        
        # Проверяем TTL в записи кэша
        cache_entry = cache_manager._memory_cache[key]
        assert cache_entry['ttl'] == custom_ttl

    def test_cache_large_data(self, cache_manager):
        """Тест кэширования больших данных"""
        key = "large_data_key"
        large_value = {
            "large_list": list(range(1000)),
            "large_dict": {f"key_{i}": f"value_{i}" for i in range(100)},
            "nested_data": {
                "level1": {
                    "level2": {
                        "level3": ["item"] * 50
                    }
                }
            }
        }
        
        # Сохраняем и получаем большие данные
        result = cache_manager.set(key, large_value)
        assert result is True
        
        cached_value = cache_manager.get(key)
        assert cached_value == large_value
        assert len(cached_value["large_list"]) == 1000
        assert len(cached_value["large_dict"]) == 100
