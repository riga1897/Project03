
"""
Тесты для системы кэширования API
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from src.utils.cache import CacheManager


class TestCacheManager:
    """Тесты для CacheManager"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Создает временную директорию для кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """Создает CacheManager с временной директорией"""
        return CacheManager(base_cache_dir=temp_cache_dir)

    def test_cache_initialization(self, cache_manager, temp_cache_dir):
        """Тест инициализации кэша"""
        assert cache_manager.base_cache_dir == temp_cache_dir
        assert os.path.exists(os.path.join(temp_cache_dir, 'hh'))
        assert os.path.exists(os.path.join(temp_cache_dir, 'sj'))

    def test_get_cache_key(self, cache_manager):
        """Тест генерации ключа кэша"""
        params = {'text': 'python', 'area': '1', 'per_page': '20'}
        key = cache_manager._get_cache_key(params)
        
        assert isinstance(key, str)
        assert len(key) > 0
        # Ключ должен быть детерминированным
        key2 = cache_manager._get_cache_key(params)
        assert key == key2

    def test_get_cache_key_different_params(self, cache_manager):
        """Тест генерации разных ключей для разных параметров"""
        params1 = {'text': 'python', 'area': '1'}
        params2 = {'text': 'java', 'area': '1'}
        
        key1 = cache_manager._get_cache_key(params1)
        key2 = cache_manager._get_cache_key(params2)
        
        assert key1 != key2

    def test_save_and_get_cache(self, cache_manager):
        """Тест сохранения и получения кэша"""
        source = 'hh'
        params = {'text': 'python', 'area': '1'}
        data = {'items': [{'name': 'Python Developer', 'id': '1'}], 'found': 1}

        # Сохраняем в кэш
        cache_manager.save_cache(source, params, data)

        # Получаем из кэша
        cached_data = cache_manager.get_cache(source, params)
        
        assert cached_data is not None
        assert cached_data['items'][0]['name'] == 'Python Developer'
        assert cached_data['found'] == 1

    def test_get_cache_nonexistent(self, cache_manager):
        """Тест получения несуществующего кэша"""
        source = 'hh'
        params = {'text': 'nonexistent', 'area': '1'}
        
        cached_data = cache_manager.get_cache(source, params)
        assert cached_data is None

    def test_is_cache_valid_fresh(self, cache_manager):
        """Тест проверки валидности свежего кэша"""
        source = 'hh'
        params = {'text': 'python', 'area': '1'}
        data = {'items': []}

        # Сохраняем кэш
        cache_manager.save_cache(source, params, data)

        # Проверяем валидность (должен быть валиден)
        assert cache_manager.is_cache_valid(source, params) is True

    @patch('time.time')
    def test_is_cache_valid_expired(self, mock_time, cache_manager):
        """Тест проверки валидности просроченного кэша"""
        source = 'hh'
        params = {'text': 'python', 'area': '1'}
        data = {'items': []}

        # Имитируем время создания кэша
        mock_time.return_value = 1000
        cache_manager.save_cache(source, params, data)

        # Имитируем время через час + 1 минуту
        mock_time.return_value = 1000 + 3661  # 1 час 1 минута
        
        assert cache_manager.is_cache_valid(source, params) is False

    def test_clear_cache_source(self, cache_manager):
        """Тест очистки кэша определенного источника"""
        # Сохраняем кэш для HH
        hh_params = {'text': 'python', 'area': '1'}
        hh_data = {'items': []}
        cache_manager.save_cache('hh', hh_params, hh_data)

        # Сохраняем кэш для SJ
        sj_params = {'text': 'python', 'area': '1'}
        sj_data = {'items': []}
        cache_manager.save_cache('sj', sj_params, sj_data)

        # Очищаем только HH
        cache_manager.clear_cache('hh')

        # Проверяем, что HH очищен, а SJ остался
        assert cache_manager.get_cache('hh', hh_params) is None
        assert cache_manager.get_cache('sj', sj_params) is not None

    def test_clear_cache_all(self, cache_manager):
        """Тест полной очистки кэша"""
        # Сохраняем кэш для обоих источников
        hh_params = {'text': 'python', 'area': '1'}
        cache_manager.save_cache('hh', hh_params, {'items': []})
        
        sj_params = {'text': 'python', 'area': '1'}
        cache_manager.save_cache('sj', sj_params, {'items': []})

        # Очищаем весь кэш
        cache_manager.clear_cache()

        # Проверяем, что оба очищены
        assert cache_manager.get_cache('hh', hh_params) is None
        assert cache_manager.get_cache('sj', sj_params) is None

    def test_get_cache_stats(self, cache_manager):
        """Тест получения статистики кэша"""
        # Добавляем несколько записей в кэш
        for i in range(3):
            params = {'text': f'query_{i}', 'area': '1'}
            data = {'items': [f'item_{i}'], 'found': 1}
            cache_manager.save_cache('hh', params, data)

        for i in range(2):
            params = {'text': f'query_{i}', 'area': '2'}
            data = {'items': [f'item_{i}'], 'found': 1}
            cache_manager.save_cache('sj', params, data)

        stats = cache_manager.get_cache_stats()
        
        assert stats['hh']['count'] == 3
        assert stats['sj']['count'] == 2
        assert 'total_size' in stats['hh']
        assert 'total_size' in stats['sj']

    def test_cache_with_complex_params(self, cache_manager):
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
        cache_manager.save_cache(source, params, data)
        cached_data = cache_manager.get_cache(source, params)
        
        assert cached_data is not None
        assert cached_data['found'] == 0

    def test_cache_file_corrupted(self, cache_manager, temp_cache_dir):
        """Тест обработки поврежденного файла кэша"""
        source = 'hh'
        params = {'text': 'python', 'area': '1'}
        
        # Создаем поврежденный файл кэша
        cache_key = cache_manager._get_cache_key(params)
        cache_file_path = os.path.join(temp_cache_dir, source, f"{cache_key}.json")
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        
        with open(cache_file_path, 'w') as f:
            f.write("invalid json content")

        # Попытка получить кэш должна вернуть None
        cached_data = cache_manager.get_cache(source, params)
        assert cached_data is None

    def test_cache_directory_permissions(self, temp_cache_dir):
        """Тест обработки проблем с правами доступа"""
        # Этот тест может не работать на Windows
        if os.name == 'nt':
            pytest.skip("Пропускаем тест прав доступа на Windows")

        # Делаем директорию недоступной для записи
        cache_dir = os.path.join(temp_cache_dir, 'readonly')
        os.makedirs(cache_dir, mode=0o555)  # только чтение и выполнение
        
        try:
            cache_manager = CacheManager(base_cache_dir=cache_dir)
            
            # Попытка сохранить в недоступную директорию
            params = {'text': 'python'}
            data = {'items': []}
            
            # Не должно вызывать исключение, но и не должно сохранять
            cache_manager.save_cache('hh', params, data)
            
            # Проверяем, что кэш не сохранился
            cached_data = cache_manager.get_cache('hh', params)
            assert cached_data is None
            
        finally:
            # Восстанавливаем права для удаления
            os.chmod(cache_dir, 0o755)

    def test_cache_unicode_support(self, cache_manager):
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
        cache_manager.save_cache(source, params, data)
        cached_data = cache_manager.get_cache(source, params)
        
        assert cached_data is not None
        assert cached_data['items'][0]['name'] == 'Senior Python разработчик 👨‍💻'
