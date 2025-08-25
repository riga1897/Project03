"""
Тесты для модуля обработки файлов
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from src.utils.file_handlers import JSONFileHandler, json_handler


class TestJSONFileHandler:
    """Тесты для JSONFileHandler"""

    @pytest.fixture
    def sample_data(self):
        """Фикстура с тестовыми данными"""
        return [
            {"id": "1", "title": "Python Developer", "salary": 100000},
            {"id": "2", "title": "Java Developer", "salary": 120000}
        ]

    @pytest.fixture
    def temp_json_file(self):
        """Фикстура для создания временного JSON файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = Path(temp_file.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_write_json_data(self, sample_data, temp_json_file):
        """Тест записи JSON данных"""
        handler = JSONFileHandler()
        handler.write_json(temp_json_file, sample_data)

        # Проверяем, что файл создан и содержит правильные данные
        with temp_json_file.open('r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data == sample_data

    def test_read_json_data(self, sample_data, temp_json_file):
        """Тест чтения JSON данных"""
        with temp_json_file.open('w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)

        handler = JSONFileHandler()
        loaded_data = handler.read_json(temp_json_file)

        assert loaded_data == sample_data

    def test_read_nonexistent_json_file(self):
        """Тест чтения несуществующего JSON файла"""
        handler = JSONFileHandler()
        nonexistent_path = Path("/nonexistent/file.json")
        loaded_data = handler.read_json(nonexistent_path)

        assert loaded_data == []

    def test_read_empty_json_file(self, temp_json_file):
        """Тест чтения пустого JSON файла"""
        # Создаем пустой файл
        temp_json_file.touch()

        handler = JSONFileHandler()
        loaded_data = handler.read_json(temp_json_file)

        assert loaded_data == []

    def test_read_invalid_json_file(self, temp_json_file):
        """Тест чтения некорректного JSON файла"""
        with temp_json_file.open('w', encoding='utf-8') as f:
            f.write("invalid json content")

        handler = JSONFileHandler()
        loaded_data = handler.read_json(temp_json_file)

        assert loaded_data == []

    def test_write_creates_directory(self, sample_data):
        """Тест создания директории при записи"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nested_path = temp_path / "nested" / "deep" / "test.json"

            handler = JSONFileHandler()
            handler.write_json(nested_path, sample_data)

            assert nested_path.exists()
            loaded_data = handler.read_json(nested_path)
            assert loaded_data == sample_data
            temp_dir.rmdir()

    def test_atomic_write_on_error(self, sample_data, temp_json_file):
        """Тест атомарной записи при ошибке"""
        handler = JSONFileHandler()

        # Мокаем json.dump чтобы вызвать ошибку
        with patch('json.dump', side_effect=Exception("Mocked error")):
            with pytest.raises(Exception):
                handler.write_json(temp_json_file, sample_data)

        # Проверяем, что временный файл не остался
        temp_file_pattern = str(temp_json_file.with_suffix(".tmp"))
        assert not Path(temp_file_pattern).exists()

    def test_cache_clearing_on_write(self, sample_data, temp_json_file):
        """Тест очистки кэша при записи"""
        handler = JSONFileHandler()

        # Сначала читаем (кэшируем)
        initial_data = handler.read_json(temp_json_file)

        # Записываем новые данные
        handler.write_json(temp_json_file, sample_data)

        # Читаем снова - должны получить новые данные
        updated_data = handler.read_json(temp_json_file)
        assert updated_data == sample_data

    def test_global_json_handler_instance(self):
        """Тест глобального экземпляра json_handler"""
        assert json_handler is not None
        assert isinstance(json_handler, JSONFileHandler)

    def test_caching_behavior(self, sample_data, temp_json_file):
        """Тест поведения кэширования"""
        # Записываем данные в файл
        with temp_json_file.open('w', encoding='utf-8') as f:
            json.dump(sample_data, f)

        handler = JSONFileHandler()

        # Первое чтение
        data1 = handler.read_json(temp_json_file)

        # Изменяем файл напрямую
        modified_data = [{"id": "999", "title": "Modified"}]
        with temp_json_file.open('w', encoding='utf-8') as f:
            json.dump(modified_data, f)

        # Второе чтение (в течение TTL должен вернуть кэшированные данные)
        data2 = handler.read_json(temp_json_file)

        # Данные должны быть одинаковыми (из кэша)
        assert data1 == data2 == sample_data

        # Очищаем кэш и читаем снова
        handler.read_json.clear_cache()
        data3 = handler.read_json(temp_json_file)

        # Теперь должны получить измененные данные
        assert data3 == modified_data