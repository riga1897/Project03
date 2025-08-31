
import pytest
from unittest.mock import Mock, patch, mock_open
import sys
import os
import json
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.cache import CacheManager


class TestCacheManager:
    """Тесты для CacheManager"""

    def test_cache_manager_initialization(self):
        """Тест инициализации CacheManager"""
        cache_manager = CacheManager()
        assert hasattr(cache_manager, 'cache_dir')
        assert isinstance(cache_manager.cache_dir, Path)

    @patch('pathlib.Path.mkdir')
    def test_cache_directory_creation(self, mock_mkdir):
        """Тест создания директории кэша"""
        cache_manager = CacheManager()
        # Директория должна создаваться при инициализации
        mock_mkdir.assert_called()

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_get_cache_hit(self, mock_file, mock_exists):
        """Тест попадания в кэш"""
        mock_exists.return_value = True
        
        cache_manager = CacheManager()
        result = cache_manager.get("test_key")
        
        assert result == {"test": "data"}
        mock_file.assert_called()

    @patch('pathlib.Path.exists')
    def test_get_cache_miss(self, mock_exists):
        """Тест промаха кэша"""
        mock_exists.return_value = False
        
        cache_manager = CacheManager()
        result = cache_manager.get("nonexistent_key")
        
        assert result is None

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_set_cache(self, mock_json_dump, mock_file):
        """Тест установки значения в кэш"""
        cache_manager = CacheManager()
        test_data = {"test": "data"}
        
        cache_manager.set("test_key", test_data)
        
        mock_file.assert_called()
        mock_json_dump.assert_called_with(test_data, mock_file(), ensure_ascii=False, indent=2)

    @patch('shutil.rmtree')
    @patch('pathlib.Path.exists')
    def test_clear_cache(self, mock_exists, mock_rmtree):
        """Тест очистки кэша"""
        mock_exists.return_value = True
        
        cache_manager = CacheManager()
        cache_manager.clear()
        
        mock_rmtree.assert_called()

    def test_generate_cache_key(self):
        """Тест генерации ключа кэша"""
        cache_manager = CacheManager()
        
        key1 = cache_manager._generate_key("test", {"param": "value"})
        key2 = cache_manager._generate_key("test", {"param": "value"})
        key3 = cache_manager._generate_key("test", {"param": "different"})
        
        # Одинаковые параметры должны давать одинаковый ключ
        assert key1 == key2
        # Разные параметры должны давать разные ключи
        assert key1 != key3

    @patch('builtins.open', side_effect=OSError("File error"))
    @patch('pathlib.Path.exists')
    def test_cache_error_handling(self, mock_exists, mock_open):
        """Тест обработки ошибок кэша"""
        mock_exists.return_value = True
        
        cache_manager = CacheManager()
        
        # При ошибке чтения должен возвращаться None
        result = cache_manager.get("test_key")
        assert result is None
