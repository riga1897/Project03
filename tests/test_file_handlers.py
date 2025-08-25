"""
Тесты для модуля обработки файлов
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, mock_open
from src.utils.file_handlers import FileHandler, JSONFileHandler, CSVFileHandler


class TestFileHandler:
    """Тесты для базового класса FileHandler"""

    def test_file_handler_initialization(self):
        """Тест инициализации FileHandler"""
        handler = FileHandler()
        assert handler is not None

    def test_file_exists_true(self):
        """Тест проверки существования файла (файл существует)"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            handler = FileHandler()
            assert handler.file_exists(temp_path) is True
        finally:
            os.unlink(temp_path)

    def test_file_exists_false(self):
        """Тест проверки существования файла (файл не существует)"""
        handler = FileHandler()
        assert handler.file_exists("/nonexistent/path/file.txt") is False

    def test_create_directory(self):
        """Тест создания директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_directory")

            handler = FileHandler()
            handler.create_directory(new_dir)

            assert os.path.exists(new_dir)
            assert os.path.isdir(new_dir)

    def test_create_existing_directory(self):
        """Тест создания уже существующей директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileHandler()
            # Не должно вызывать ошибку
            handler.create_directory(temp_dir)

    def test_get_file_size(self):
        """Тест получения размера файла"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name

        try:
            handler = FileHandler()
            size = handler.get_file_size(temp_path)
            assert size == 12  # длина "test content"
        finally:
            os.unlink(temp_path)

    def test_get_file_size_nonexistent(self):
        """Тест получения размера несуществующего файла"""
        handler = FileHandler()
        size = handler.get_file_size("/nonexistent/file.txt")
        assert size == 0


class TestJSONFileHandler:
    """Тесты для JSONFileHandler"""

    @pytest.fixture
    def sample_data(self):
        """Фикстура с тестовыми данными"""
        return {
            "vacancies": [
                {"id": "1", "title": "Python Developer"},
                {"id": "2", "title": "Java Developer"}
            ],
            "total": 2
        }

    @pytest.fixture
    def temp_json_file(self):
        """Фикстура для создания временного JSON файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_save_json_data(self, sample_data, temp_json_file):
        """Тест сохранения JSON данных"""
        handler = JSONFileHandler()
        handler.save_data(temp_json_file, sample_data)

        # Проверяем, что файл создан и содержит правильные данные
        with open(temp_json_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data == sample_data

    def test_load_json_data(self, sample_data, temp_json_file):
        """Тест загрузки JSON данных"""
        with open(temp_json_file, 'w', encoding='utf-8') as temp_file:
            json.dump(sample_data, temp_file, ensure_ascii=False, indent=2)

        handler = JSONFileHandler()
        loaded_data = handler.load_data(temp_json_file)

        assert loaded_data == sample_data

    def test_load_nonexistent_json_file(self):
        """Тест загрузки несуществующего JSON файла"""
        handler = JSONFileHandler()
        loaded_data = handler.load_data("/nonexistent/file.json")

        assert loaded_data is None

    def test_load_invalid_json_file(self, temp_json_file):
        """Тест загрузки некорректного JSON файла"""
        with open(temp_json_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")

        handler = JSONFileHandler()
        loaded_data = handler.load_data(temp_json_file)

        assert loaded_data is None

    def test_append_json_data(self, sample_data, temp_json_file):
        """Тест добавления данных к существующему JSON файлу"""
        with open(temp_json_file, 'w', encoding='utf-8') as temp_file:
            json.dump({"existing": "data"}, temp_file)

        handler = JSONFileHandler()
        handler.append_data(temp_json_file, sample_data)

        # Проверяем результат
        with open(temp_json_file, 'r', encoding='utf-8') as f:
            result_data = json.load(f)

        # Данные должны быть объединены
        assert "existing" in result_data
        assert "vacancies" in result_data
        assert result_data["total"] == 2 # Проверяем, что новые данные добавились


class TestCSVFileHandler:
    """Тесты для CSVFileHandler"""

    @pytest.fixture
    def sample_csv_data(self):
        """Фикстура с тестовыми данными для CSV"""
        return [
            {"id": "1", "title": "Python Developer", "salary": "100000"},
            {"id": "2", "title": "Java Developer", "salary": "120000"}
        ]

    def test_save_csv_data(self, sample_csv_data):
        """Тест сохранения CSV данных"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            handler = CSVFileHandler()
            handler.save_data(temp_path, sample_csv_data)

            # Проверяем, что файл создан
            assert os.path.exists(temp_path)

            # Проверяем содержимое
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Python Developer" in content
                assert "Java Developer" in content
        finally:
            os.unlink(temp_path)

    def test_load_csv_data(self, sample_csv_data):
        """Тест загрузки CSV данных"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Сначала сохраняем данные
            handler = CSVFileHandler()
            handler.save_data(temp_path, sample_csv_data)

            # Затем загружаем
            loaded_data = handler.load_data(temp_path)

            assert len(loaded_data) == 2
            assert loaded_data[0]["title"] == "Python Developer"
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_csv_file(self):
        """Тест загрузки несуществующего CSV файла"""
        handler = CSVFileHandler()
        loaded_data = handler.load_data("/nonexistent/file.csv")

        assert loaded_data is None or loaded_data == []