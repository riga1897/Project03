
"""
Тесты для системы кэширования API
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from src.utils.cache import FileCache


class TestFileCache:
    """Тесты для CacheManager"""

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
        params = {'text': 'python', 'area': '1', 'per_page': '20'}
        key = file_cache._generate_params_hash(params)
        
        assert isinstance(key, str)
        assert len(key) > 0
        # Хеш должен быть детерминированным
        key2 = file_cache._generate_params_hash(params)
        assert key == key2

    def test_generate_params_hash_different_params(self, file_cache):
        """Тест генерации разных хешей для разных параметров"""
        params1 = {'text': 'python', 'area': '1'}
        params2 = {'text': 'java', 'area': '1'}
        
        key1 = file_cache._generate_params_hash(params1)
        key2 = file_cache._generate_params_hash(params2)
        
        assert key1 != key2

    def test_save_and_load_response(self, file_cache):
        """Тест сохранения и загрузки ответа"""
        source = 'hh'
        params = {'text': 'python', 'area': '1'}
        data = {'items': [{'name': 'Python Developer', 'id': '1'}], 'found': 1}

        # Сохраняем в кэш
        file_cache.save_response(source, params, data)

        # Получаем из кэша
        cached_response = file_cache.load_response(source, params)
        
        assert cached_response is not None
        assert cached_response['data']['items'][0]['name'] == 'Python Developer'
        assert cached_response['data']['found'] == 1
        assert cached_response['meta']['params'] == params

    def test_load_response_nonexistent(self, file_cache):
        """Тест получения несуществующего кэша"""
        source = 'hh'
        params = {'text': 'nonexistent', 'area': '1'}
        
        cached_response = file_cache.load_response(source, params)
        assert cached_response is None

    def test_clear_cache_source(self, file_cache):
        """Тест очистки кэша определенного источника"""
        # Сохраняем кэш для HH
        hh_params = {'text': 'python', 'area': '1'}
        hh_data = {'items': []}
        file_cache.save_response('hh', hh_params, hh_data)

        # Сохраняем кэш для SJ
        sj_params = {'text': 'python', 'area': '1'}
        sj_data = {'items': []}
        file_cache.save_response('sj', sj_params, sj_data)

        # Очищаем только HH
        file_cache.clear('hh')

        # Проверяем, что HH очищен, а SJ остался
        assert file_cache.load_response('hh', hh_params) is None
        assert file_cache.load_response('sj', sj_params) is not None

    def test_clear_cache_all(self, file_cache):
        """Тест полной очистки кэша"""
        # Сохраняем кэш для обоих источников
        hh_params = {'text': 'python', 'area': '1'}
        file_cache.save_response('hh', hh_params, {'items': []})
        
        sj_params = {'text': 'python', 'area': '1'}
        file_cache.save_response('sj', sj_params, {'items': []})

        # Очищаем весь кэш
        file_cache.clear()

        # Проверяем, что оба очищены
        assert file_cache.load_response('hh', hh_params) is None
        assert file_cache.load_response('sj', sj_params) is None

    def test_cache_with_complex_params(self, file_cache):
        """Тест кэширования со сложными параметрами"""
        source = 'hh'
        params = {
            'text': 'python developer',
            'area': ['1', '2'],  # список
            'salary': 100000,
            'experience': 'between1And3',
            'employment': 'full'
        }
        data = {'items': [], 'found': 0}

        # Сохраняем и получаем
        file_cache.save_response(source, params, data)
        cached_response = file_cache.load_response(source, params)
        
        assert cached_response is not None
        assert cached_response['data']['found'] == 0

    def test_cache_file_corrupted(self, file_cache, temp_cache_dir):
        """Тест обработки поврежденного файла кэша"""
        source = 'hh'
        params = {'text': 'python', 'area': '1'}
        
        # Создаем поврежденный файл кэша
        cache_key = file_cache._generate_params_hash(params)
        cache_file_path = os.path.join(temp_cache_dir, f"{source}_{cache_key}.json")
        
        with open(cache_file_path, 'w') as f:
            f.write("invalid json content")

        # Попытка получить кэш должна вернуть None
        cached_response = file_cache.load_response(source, params)
        assert cached_response is None

    def test_cache_unicode_support(self, file_cache):
        """Тест поддержки Unicode в кэше"""
        source = 'hh'
        params = {'text': 'разработчик python 🐍', 'area': 'Москва'}
        data = {
            'items': [
                {'name': 'Senior Python разработчик 👨‍💻', 'id': '1'}
            ],
            'found': 1
        }

        # Сохраняем и получаем
        file_cache.save_response(source, params, data)
        cached_response = file_cache.load_response(source, params)
        
        assert cached_response is not None
        assert cached_response['data']['items'][0]['name'] == 'Senior Python разработчик 👨‍💻'
