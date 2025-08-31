import json
import os
import sys
from unittest.mock import Mock, mock_open, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.file_handlers import FileOperations, JSONFileHandler


class TestJSONFileHandler:
    """Тесты для JSONFileHandler"""

    def test_json_file_handler_initialization(self):
        """Тест инициализации JSONFileHandler"""
        handler = JSONFileHandler()
        assert isinstance(handler, JSONFileHandler)

    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_json_success(self, mock_file):
        """Тест успешной загрузки JSON"""
        handler = JSONFileHandler()
        result = handler.load_json("test.json")

        assert result == {"test": "data"}
        mock_file.assert_called_with("test.json", "r", encoding="utf-8")

    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_load_json_file_not_found(self, mock_file):
        """Тест загрузки несуществующего JSON файла"""
        handler = JSONFileHandler()
        result = handler.load_json("nonexistent.json")

        assert result is None

    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    def test_load_json_invalid_format(self, mock_file):
        """Тест загрузки невалидного JSON"""
        handler = JSONFileHandler()
        result = handler.load_json("invalid.json")

        assert result is None

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_json_success(self, mock_json_dump, mock_file):
        """Тест успешного сохранения JSON"""
        handler = JSONFileHandler()
        test_data = {"test": "data"}

        result = handler.save_json("test.json", test_data)

        assert result is True
        mock_file.assert_called_with("test.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_with(test_data, mock_file(), ensure_ascii=False, indent=2)

    @patch("builtins.open", side_effect=OSError("Write error"))
    def test_save_json_error(self, mock_file):
        """Тест ошибки при сохранении JSON"""
        handler = JSONFileHandler()
        test_data = {"test": "data"}

        result = handler.save_json("test.json", test_data)

        assert result is False


class TestFileOperations:
    """Тесты для FileOperations"""

    def test_file_operations_initialization(self):
        """Тест инициализации FileOperations"""
        ops = FileOperations()
        assert isinstance(ops, FileOperations)

    @patch("pathlib.Path.exists")
    def test_file_exists(self, mock_exists):
        """Тест проверки существования файла"""
        mock_exists.return_value = True

        ops = FileOperations()
        result = ops.file_exists("test.txt")

        assert result is True
        mock_exists.assert_called()

    @patch("pathlib.Path.mkdir")
    def test_create_directory(self, mock_mkdir):
        """Тест создания директории"""
        ops = FileOperations()
        ops.create_directory("test_dir")

        mock_mkdir.assert_called()

    @patch("pathlib.Path.unlink")
    @patch("pathlib.Path.exists")
    def test_delete_file(self, mock_exists, mock_unlink):
        """Тест удаления файла"""
        mock_exists.return_value = True

        ops = FileOperations()
        result = ops.delete_file("test.txt")

        assert result is True
        mock_unlink.assert_called()

    @patch("pathlib.Path.exists")
    def test_delete_nonexistent_file(self, mock_exists):
        """Тест удаления несуществующего файла"""
        mock_exists.return_value = False

        ops = FileOperations()
        result = ops.delete_file("nonexistent.txt")

        assert result is False

    @patch("shutil.copy2")
    @patch("pathlib.Path.exists")
    def test_copy_file(self, mock_exists, mock_copy):
        """Тест копирования файла"""
        mock_exists.return_value = True

        ops = FileOperations()
        result = ops.copy_file("source.txt", "dest.txt")

        assert result is True
        mock_copy.assert_called()
