#!/usr/bin/env python3
"""
Тесты для модуля cache.py
"""

import json
import hashlib
import time
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest

from src.utils.cache import FileCache


class TestFileCache:
    """Тесты для класса FileCache"""
    
    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """Создание временной директории для кэша"""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return str(cache_dir)
    
    @pytest.fixture
    def file_cache(self, temp_cache_dir):
        """Создание экземпляра FileCache для тестов"""
        return FileCache(temp_cache_dir)
    
    def test_file_cache_initialization(self, temp_cache_dir):
        """Тест инициализации FileCache"""
        cache = FileCache(temp_cache_dir)
        
        assert cache.cache_dir == Path(temp_cache_dir)
        assert cache.cache_dir.exists()
    
    def test_file_cache_default_directory(self):
        """Тест инициализации с директорией по умолчанию"""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            cache = FileCache()
            
            assert cache.cache_dir == Path("data/cache")
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    @patch('pathlib.Path.mkdir')
    def test_ensure_dir_exists(self, mock_mkdir, temp_cache_dir):
        """Тест создания директории"""
        cache = FileCache(temp_cache_dir)
        
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_generate_params_hash(self, file_cache):
        """Тест генерации хеша параметров"""
        params = {"text": "Python", "page": 1}
        
        # Генерируем хеш
        hash_result = file_cache._generate_params_hash(params)
        
        # Проверяем, что это MD5 хеш
        assert len(hash_result) == 32  # MD5 hex длина
        assert isinstance(hash_result, str)
        
        # Проверяем воспроизводимость
        hash_result2 = file_cache._generate_params_hash(params)
        assert hash_result == hash_result2
        
        # Проверяем уникальность для разных параметров
        params2 = {"text": "Java", "page": 1}
        hash_result3 = file_cache._generate_params_hash(params2)
        assert hash_result != hash_result3
    
    def test_generate_params_hash_different_order(self, file_cache):
        """Тест генерации хеша для параметров в разном порядке"""
        params1 = {"text": "Python", "page": 1}
        params2 = {"page": 1, "text": "Python"}
        
        hash1 = file_cache._generate_params_hash(params1)
        hash2 = file_cache._generate_params_hash(params2)
        
        # Хеши должны быть одинаковыми независимо от порядка
        assert hash1 == hash2
    
    def test_generate_params_hash_empty_params(self, file_cache):
        """Тест генерации хеша для пустых параметров"""
        empty_params = {}
        hash_result = file_cache._generate_params_hash(empty_params)
        
        assert len(hash_result) == 32
        assert hash_result == hashlib.md5(b"{}".encode()).hexdigest()
    
    def test_generate_params_hash_complex_params(self, file_cache):
        """Тест генерации хеша для сложных параметров"""
        complex_params = {
            "text": "Python Developer",
            "salary": {"from": 100000, "to": 150000},
            "experience": ["1-3", "3-6"],
            "schedule": "fullDay"
        }
        
        hash_result = file_cache._generate_params_hash(complex_params)
        assert len(hash_result) == 32
        assert isinstance(hash_result, str)
    
    @patch('src.utils.cache.logger')
    def test_save_response_valid_data(self, mock_logger, file_cache):
        """Тест сохранения валидных данных"""
        params = {"text": "Python", "page": 0}
        data = {"items": [{"id": "1", "name": "Python Developer"}], "found": 1}
        
        with patch('builtins.open', mock_open()) as mock_file:
            file_cache.save_response("hh", params, data)
            
            # Проверяем, что файл был открыт для записи
            mock_file.assert_called_once()
            mock_logger.debug.assert_called_with("Ответ сохранен в кэш: Mock")
    
    @patch('src.utils.cache.logger')
    def test_save_response_invalid_data(self, mock_logger, file_cache):
        """Тест пропуска невалидных данных"""
        params = {"text": "Python", "page": 1}
        data = {"items": [], "found": 0}  # Пустая страница
        
        with patch('builtins.open', mock_open()) as mock_file:
            file_cache.save_response("hh", params, data)
            
            # Проверяем, что файл не был открыт
            mock_file.assert_not_called()
            mock_logger.debug.assert_called_with("Пропускаем сохранение некорректного ответа в кэш: {'text': 'Python', 'page': 1}")
    
    def test_is_valid_response_valid_data(self, file_cache):
        """Тест валидации валидных данных"""
        data = {"items": [{"id": "1"}], "found": 1, "pages": 1}
        params = {"page": 0}
        
        result = file_cache._is_valid_response(data, params)
        assert result is True
    
    def test_is_valid_response_invalid_structure(self, file_cache):
        """Тест валидации невалидной структуры"""
        data = "not a dict"
        params = {"page": 0}
        
        result = file_cache._is_valid_response(data, params)
        assert result is False
    
    def test_is_valid_response_empty_page_after_available(self, file_cache):
        """Тест валидации пустой страницы после доступных"""
        data = {"items": [], "found": 0, "pages": 1}
        params = {"page": 2}  # Страница больше доступных
        
        result = file_cache._is_valid_response(data, params)
        assert result is False
    
    def test_is_valid_response_no_results_page(self, file_cache):
        """Тест валидации страницы без результатов"""
        data = {"items": [], "found": 0, "pages": 5}
        params = {"page": 3}  # Не первая страница, но нет результатов
        
        result = file_cache._is_valid_response(data, params)
        assert result is False
    
    def test_is_valid_response_first_page_no_results(self, file_cache):
        """Тест валидации первой страницы без результатов"""
        data = {"items": [], "found": 0, "pages": 1}
        params = {"page": 0}  # Первая страница без результатов
        
        result = file_cache._is_valid_response(data, params)
        assert result is True
    
    @patch('src.utils.cache.logger')
    def test_save_response_exception_handling(self, mock_logger, file_cache):
        """Тест обработки исключений при сохранении"""
        params = {"text": "Python"}
        data = {"items": [{"id": "1"}]}
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            file_cache.save_response("hh", params, data)
            
            mock_logger.error.assert_called_with("Ошибка сохранения в кэш: Permission denied")
    
    @patch('src.utils.cache.logger')
    def test_load_response_file_not_exists(self, mock_logger, file_cache):
        """Тест загрузки несуществующего файла"""
        params = {"text": "Python"}
        
        result = file_cache.load_response("hh", params)
        
        assert result is None
    
    @patch('src.utils.cache.logger')
    def test_load_response_file_too_small(self, mock_logger, file_cache):
        """Тест загрузки слишком маленького файла"""
        params = {"text": "Python"}
        params_hash = file_cache._generate_params_hash(params)
        filename = f"hh_{params_hash}.json"
        filepath = file_cache.cache_dir / filename
        
        # Создаем слишком маленький файл
        with open(filepath, 'w') as f:
            f.write('{}')  # Минимальный JSON
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 30  # Меньше 50 байт
            
            result = file_cache.load_response("hh", params)
            
            assert result is None
            mock_logger.warning.assert_called_with("Файл кэша слишком маленький (30 байт), удаляем: Mock")
    
    @patch('src.utils.cache.logger')
    def test_load_response_valid_file(self, mock_logger, file_cache):
        """Тест загрузки валидного файла"""
        params = {"text": "Python"}
        params_hash = file_cache._generate_params_hash(params)
        filename = f"hh_{params_hash}.json"
        filepath = file_cache.cache_dir / filename
        
        # Создаем валидный файл кэша
        cache_data = {
            "timestamp": time.time(),
            "meta": {"params": params},
            "data": {"items": [{"id": "1", "name": "Python Developer"}]}
        }
        
        with open(filepath, 'w') as f:
            json.dump(cache_data, f)
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 100  # Больше 50 байт
            
            result = file_cache.load_response("hh", params)
            
            assert result is not None
            assert result["data"]["items"][0]["id"] == "1"
    
    @patch('src.utils.cache.logger')
    def test_load_response_invalid_json(self, mock_logger, file_cache):
        """Тест загрузки файла с невалидным JSON"""
        params = {"text": "Python"}
        params_hash = file_cache._generate_params_hash(params)
        filename = f"hh_{params_hash}.json"
        filepath = file_cache.cache_dir / filename
        
        # Создаем файл с невалидным JSON
        with open(filepath, 'w') as f:
            f.write('{"invalid": json}')
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 100
            
            result = file_cache.load_response("hh", params)
            
            assert result is None
            mock_logger.warning.assert_called()
    
    @patch('src.utils.cache.logger')
    def test_load_response_invalid_structure(self, mock_logger, file_cache):
        """Тест загрузки файла с невалидной структурой"""
        params = {"text": "Python"}
        params_hash = file_cache._generate_params_hash(params)
        filename = f"hh_{params_hash}.json"
        filepath = file_cache.cache_dir / filename
        
        # Создаем файл с невалидной структурой
        cache_data = {"timestamp": time.time()}  # Без data и meta
        
        with open(filepath, 'w') as f:
            json.dump(cache_data, f)
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 100
            
            result = file_cache.load_response("hh", params)
            
            assert result is None
            mock_logger.warning.assert_called()
    
    def test_validate_cached_structure_valid(self, file_cache):
        """Тест валидации валидной структуры кэша"""
        cached_data = {
            "timestamp": time.time(),
            "data": {"items": [{"id": "1"}]},
            "meta": {"params": {"text": "Python"}}
        }
        
        result = file_cache._validate_cached_structure(cached_data)
        assert result is True
    
    def test_validate_cached_structure_missing_fields(self, file_cache):
        """Тест валидации структуры с отсутствующими полями"""
        cached_data = {
            "timestamp": time.time(),
            "data": {"items": [{"id": "1"}]}
            # Отсутствует meta
        }
        
        result = file_cache._validate_cached_structure(cached_data)
        assert result is False
    
    def test_validate_cached_structure_invalid_data_type(self, file_cache):
        """Тест валидации структуры с невалидным типом data"""
        cached_data = {
            "timestamp": time.time(),
            "data": "not a dict",
            "meta": {"params": {"text": "Python"}}
        }
        
        result = file_cache._validate_cached_structure(cached_data)
        assert result is False
    
    def test_validate_cached_structure_invalid_items_type(self, file_cache):
        """Тест валидации структуры с невалидным типом items"""
        cached_data = {
            "timestamp": time.time(),
            "data": {"items": "not a list"},
            "meta": {"params": {"text": "Python"}}
        }
        
        result = file_cache._validate_cached_structure(cached_data)
        assert result is False
    
    @patch('src.utils.cache.logger')
    def test_deduplicate_vacancies_no_existing_cache(self, mock_logger, file_cache):
        """Тест дедупликации без существующего кэша"""
        data = {"items": [{"id": "1", "name": "Python"}]}
        
        result = file_cache._deduplicate_vacancies(data, "hh")
        
        assert result == data
        assert len(result["items"]) == 1
    
    @patch('src.utils.cache.logger')
    def test_deduplicate_vacancies_with_existing_cache(self, mock_logger, file_cache):
        """Тест дедупликации с существующим кэшем"""
        # Создаем существующий файл кэша
        existing_cache = {
            "timestamp": time.time(),
            "meta": {"params": {"text": "Java"}},
            "data": {"items": [{"id": "1", "name": "Java Developer"}]}
        }
        
        cache_file = file_cache.cache_dir / "hh_existing.json"
        with open(cache_file, 'w') as f:
            json.dump(existing_cache, f)
        
        # Новые данные с дубликатом
        new_data = {
            "items": [
                {"id": "1", "name": "Java Developer"},  # Дубликат
                {"id": "2", "name": "Python Developer"}  # Новый
            ]
        }
        
        result = file_cache._deduplicate_vacancies(new_data, "hh")
        
        # Должен остаться только новый элемент
        assert len(result["items"]) == 1
        assert result["items"][0]["id"] == "2"
    
    @patch('src.utils.cache.logger')
    def test_deduplicate_vacancies_error_handling(self, mock_logger, file_cache):
        """Тест обработки ошибок при дедупликации"""
        data = {"items": [{"id": "1", "name": "Python"}]}
        
        # Мокаем ошибку при чтении файлов кэша
        with patch('pathlib.Path.glob', side_effect=Exception("File error")):
            result = file_cache._deduplicate_vacancies(data, "hh")
            
            # При ошибке должны вернуть оригинальные данные
            assert result == data
            mock_logger.error.assert_called_with("Ошибка дедупликации: File error")
    
    def test_clear_cache_specific_source(self, file_cache):
        """Тест очистки кэша для конкретного источника"""
        # Создаем тестовые файлы
        hh_file = file_cache.cache_dir / "hh_test1.json"
        sj_file = file_cache.cache_dir / "sj_test1.json"
        
        hh_file.touch()
        sj_file.touch()
        
        # Очищаем только HH кэш
        file_cache.clear("hh")
        
        assert not hh_file.exists()
        assert sj_file.exists()  # SJ файл должен остаться
    
    def test_clear_cache_all_sources(self, file_cache):
        """Тест очистки всего кэша"""
        # Создаем тестовые файлы
        hh_file = file_cache.cache_dir / "hh_test1.json"
        sj_file = file_cache.cache_dir / "sj_test1.json"
        other_file = file_cache.cache_dir / "other.json"
        
        hh_file.touch()
        sj_file.touch()
        other_file.touch()
        
        # Очищаем весь кэш
        file_cache.clear()
        
        assert not hh_file.exists()
        assert not sj_file.exists()
        assert not other_file.exists()
    
    def test_clear_cache_no_files(self, file_cache):
        """Тест очистки пустого кэша"""
        # Очищаем пустой кэш
        file_cache.clear()
        file_cache.clear("hh")
        
        # Не должно быть ошибок
        assert True
    
    def test_cache_file_naming_convention(self, file_cache):
        """Тест соглашения об именовании файлов кэша"""
        params = {"text": "Python Developer", "page": 1}
        params_hash = file_cache._generate_params_hash(params)
        
        expected_filename = f"hh_{params_hash}.json"
        expected_filepath = file_cache.cache_dir / expected_filename
        
        # Проверяем, что имя файла соответствует ожидаемому
        assert expected_filename.startswith("hh_")
        assert expected_filename.endswith(".json")
        assert len(expected_filename) == len("hh_") + 32 + len(".json")  # 32 - длина MD5 хеша
