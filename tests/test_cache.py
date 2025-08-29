"""
Тесты для системы кэширования API
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from src.utils.cache import FileCache


class TestFileCache:
    """Тесты для FileCache"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Создает временную директорию для кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def file_cache(self, temp_cache_dir):
        """Создает FileCache с временной директорией"""
        return FileCache(cache_dir=temp_cache_dir)

    def test_cache_initialization(self, file_cache, temp_cache_dir):
        """Тест инициализации кэша"""
        assert str(file_cache.cache_dir) == temp_cache_dir
        assert file_cache.cache_dir.exists()

    def test_generate_params_hash(self, file_cache):
        """Тест генерации хеша параметров"""
        params = {"text": "python", "area": "1", "per_page": "20"}
        key = file_cache._generate_params_hash(params)

        assert isinstance(key, str)
        assert len(key) > 0
        # Хеш должен быть детерминированным
        key2 = file_cache._generate_params_hash(params)
        assert key == key2

    def test_generate_params_hash_different_params(self, file_cache):
        """Тест генерации разных хешей для разных параметров"""
        params1 = {"text": "python", "area": "1"}
        params2 = {"text": "java", "area": "1"}

        key1 = file_cache._generate_params_hash(params1)
        key2 = file_cache._generate_params_hash(params2)

        assert key1 != key2

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_response(self, mock_json_dump, mock_file, file_cache):
        """Тест сохранения ответа"""
        source = "hh"
        params = {"text": "python", "area": "1"}
        data = {"items": [{"name": "Python Developer", "id": "1"}], "found": 1}

        # Сохраняем в кэш
        file_cache.save_response(source, params, data)

        # Проверяем, что файл был открыт и данные записаны
        mock_file.assert_called()
        mock_json_dump.assert_called()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_load_response_success(self, mock_json_load, mock_file, mock_stat, mock_exists, file_cache):
        """Тест успешной загрузки ответа"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1000  # Достаточный размер файла
        mock_json_load.return_value = {
            "data": {"items": [{"name": "Python Developer", "id": "1"}], "found": 1},
            "meta": {"params": {"text": "python", "area": "1"}},
            "timestamp": 1234567890,
        }

        source = "hh"
        params = {"text": "python", "area": "1"}

        # Получаем из кэша
        cached_response = file_cache.load_response(source, params)

        assert cached_response is not None
        assert cached_response["data"]["items"][0]["name"] == "Python Developer"
        assert cached_response["data"]["found"] == 1
        assert cached_response["meta"]["params"] == params

    @patch("pathlib.Path.exists")
    def test_load_response_nonexistent(self, mock_exists, file_cache):
        """Тест получения несуществующего кэша"""
        mock_exists.return_value = False

        source = "hh"
        params = {"text": "nonexistent", "area": "1"}

        cached_response = file_cache.load_response(source, params)
        assert cached_response is None

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.unlink")
    def test_clear_cache_source(self, mock_unlink, mock_glob, file_cache):
        """Тест очистки кэша определенного источника"""
        mock_files = [Mock(), Mock()]
        mock_glob.return_value = mock_files

        # Очищаем только HH
        file_cache.clear("hh")

        # Проверяем, что glob был вызван с правильным паттерном
        mock_glob.assert_called_with("hh_*.json")

        # Проверяем, что все файлы были удалены
        for mock_file in mock_files:
            mock_file.unlink.assert_called_once()

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.unlink")
    def test_clear_cache_all(self, mock_unlink, mock_glob, file_cache):
        """Тест полной очистки кэша"""
        mock_files = [Mock(), Mock(), Mock()]
        mock_glob.return_value = mock_files

        # Очищаем весь кэш
        file_cache.clear()

        # Проверяем, что glob был вызван с паттерном для всех файлов
        mock_glob.assert_called_with("*.json")

        # Проверяем, что все файлы были удалены
        for mock_file in mock_files:
            mock_file.unlink.assert_called_once()

    def test_cache_with_complex_params(self, file_cache):
        """Тест кэширования со сложными параметрами"""
        source = "hh"
        params = {
            "text": "python developer",
            "area": ["1", "2"],  # список
            "salary": 100000,
            "experience": "between1And3",
            "employment": "full",
        }

        # Тестируем только генерацию хеша (остальное уже протестировано выше)
        hash1 = file_cache._generate_params_hash(params)
        hash2 = file_cache._generate_params_hash(params)

        assert hash1 == hash2  # Детерминированность

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("pathlib.Path.unlink")
    def test_cache_file_corrupted(self, mock_unlink, mock_json_load, mock_file, mock_stat, mock_exists, file_cache):
        """Тест обработки поврежденного файла кэша"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1000  # Достаточный размер
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        source = "hh"
        params = {"text": "python", "area": "1"}

        # Попытка получить кэш должна вернуть None
        cached_response = file_cache.load_response(source, params)
        assert cached_response is None

        # Поврежденный файл должен быть удален
        mock_unlink.assert_called()

    def test_is_valid_response(self, file_cache):
        """Тест валидации ответа"""
        # Валидный ответ
        valid_data = {"items": [{"name": "Test"}], "found": 1}
        valid_params = {"page": 0}
        assert file_cache._is_valid_response(valid_data, valid_params) is True

        # Невалидный ответ - не словарь
        assert file_cache._is_valid_response("invalid", valid_params) is False

        # Пустая страница не первая
        empty_data = {"items": [], "found": 0, "pages": 1}
        empty_params = {"page": 1}
        assert file_cache._is_valid_response(empty_data, empty_params) is False

    def test_validate_cached_structure(self, file_cache):
        """Тест валидации структуры кэша"""
        # Валидная структура
        valid_cached = {"timestamp": 1234567890, "data": {"items": []}, "meta": {"params": {}}}
        assert file_cache._validate_cached_structure(valid_cached) is True

        # Невалидная структура - отсутствует обязательное поле
        invalid_cached = {
            "timestamp": 1234567890,
            "data": {"items": []},
            # отсутствует 'meta'
        }
        assert file_cache._validate_cached_structure(invalid_cached) is False

        # Невалидная структура - неправильный тип
        assert file_cache._validate_cached_structure("not a dict") is False
