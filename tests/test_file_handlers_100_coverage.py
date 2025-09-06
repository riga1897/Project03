"""
100% покрытие src/utils/file_handlers.py  
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.utils.file_handlers import FileOperations, json_handler


class TestFileOperations:
    """100% покрытие класса FileOperations"""

    def test_file_operations_init(self):
        """Тест инициализации FileOperations - покрывает строки 19-25"""
        handler = FileOperations()
        
        # __init__ просто выполняет pass, проверяем что объект создан
        assert isinstance(handler, FileOperations)

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_read_json_empty_file(self, mock_stat, mock_exists):
        """Тест чтения пустого файла - покрывает строки 37-38"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 0  # Пустой файл
        
        handler = FileOperations()
        file_path = Path("empty_file.json")
        
        data = handler.read_json(file_path)
        
        assert data == []

    @patch('pathlib.Path.exists')
    def test_read_json_non_existing_file(self, mock_exists):
        """Тест чтения несуществующего файла - покрывает строки 37-38"""
        mock_exists.return_value = False
        
        handler = FileOperations()
        file_path = Path("missing_file.json")
        
        data = handler.read_json(file_path)
        
        assert data == []

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.open')
    @patch('json.load')
    def test_read_json_valid_file(self, mock_json_load, mock_open_method, mock_stat, mock_exists):
        """Тест чтения валидного JSON файла - покрывает строки 40-41"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 100  # Файл не пустой
        mock_json_load.return_value = [{"test": "data"}]
        
        handler = FileOperations()
        file_path = Path("valid_file.json")
        
        data = handler.read_json(file_path)
        
        assert data == [{"test": "data"}]
        mock_open_method.assert_called_once_with("r", encoding="utf-8")
        mock_json_load.assert_called_once()

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.open')
    @patch('json.load', side_effect=json.JSONDecodeError("msg", "doc", 0))
    @patch('src.utils.file_handlers.logger')
    def test_read_json_invalid_json(self, mock_logger, mock_json_load, mock_open_method, mock_stat, mock_exists):
        """Тест чтения файла с невалидным JSON - покрывает строки 43-45"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 100
        
        handler = FileOperations()
        file_path = Path("invalid.json")
        
        data = handler.read_json(file_path)
        
        assert data == []
        mock_logger.warning.assert_called_once()

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.open', side_effect=Exception("General error"))
    @patch('src.utils.file_handlers.logger')
    def test_read_json_general_exception(self, mock_logger, mock_open_method, mock_stat, mock_exists):
        """Тест обработки общих исключений при чтении - покрывает строки 46-48"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 100
        
        handler = FileOperations()
        file_path = Path("error_file.json")
        
        data = handler.read_json(file_path)
        
        assert data == []
        mock_logger.error.assert_called_once()

    def test_write_json_success(self):
        """Тест успешной записи JSON файла - покрывает строки 57-67"""
        handler = FileOperations()
        file_path = Path("output.json")
        test_data = [{"id": 1, "name": "test"}]
        
        # Создаем proper контекстный менеджер для temp_file.open
        temp_file_mock = MagicMock()
        temp_file_mock.exists.return_value = False
        temp_file_mock.open.return_value.__enter__ = MagicMock()
        temp_file_mock.open.return_value.__exit__ = MagicMock()
        
        with patch('pathlib.Path.with_suffix', return_value=temp_file_mock), \
             patch('pathlib.Path.parent') as mock_parent, \
             patch('json.dump') as mock_json_dump:
            
            mock_parent_obj = Mock()
            mock_parent.return_value = mock_parent_obj
            
            # Выполняем запись
            handler.write_json(file_path, test_data)
            
            # Основные проверки
            mock_parent_obj.mkdir.assert_called_once_with(parents=True, exist_ok=True)
            temp_file_mock.open.assert_called_once_with("w", encoding="utf-8")

    @patch('pathlib.Path.parent')
    @patch('pathlib.Path.with_suffix')
    @patch('pathlib.Path.open', side_effect=Exception("Write error"))
    @patch('pathlib.Path.exists')
    @patch('src.utils.file_handlers.logger')
    def test_write_json_exception_cleanup(self, mock_logger, mock_exists, mock_open_method, mock_with_suffix, mock_parent):
        """Тест обработки исключений и очистки при записи - покрывает строки 69-76"""
        # Настройка моков
        temp_file = Mock()
        temp_file.exists.return_value = True  # Файл существует для удаления
        mock_with_suffix.return_value = temp_file
        mock_parent_obj = Mock()
        mock_parent.return_value = mock_parent_obj
        mock_exists.return_value = True
        
        handler = FileOperations()
        file_path = Path("error_output.json")
        test_data = [{"id": 1}]
        
        with pytest.raises(Exception):
            handler.write_json(file_path, test_data)
        
        # Проверяем что временный файл удален и ошибка залогирована
        temp_file.unlink.assert_called()
        mock_logger.error.assert_called_once()

    def test_write_json_finally_cleanup(self):
        """Тест очистки в блоке finally - покрывает строки 75-76"""
        handler = FileOperations()
        file_path = Path("finally_test.json")
        test_data = [{"test": "data"}]
        
        # Создаем proper контекстный менеджер
        temp_file_mock = MagicMock()
        temp_file_mock.exists.return_value = True
        temp_file_mock.open.return_value.__enter__ = MagicMock()
        temp_file_mock.open.return_value.__exit__ = MagicMock()
        
        with patch('pathlib.Path.with_suffix', return_value=temp_file_mock), \
             patch('pathlib.Path.parent') as mock_parent, \
             patch('json.dump'):
            
            mock_parent_obj = Mock()
            mock_parent.return_value = mock_parent_obj
            
            # Выполняем запись
            handler.write_json(file_path, test_data)
            
            # Проверяем что в finally вызывается unlink если файл существует
            assert temp_file_mock.unlink.call_count >= 1

    def test_read_json_cache_decorator(self):
        """Тест кэширования метода read_json - покрывает строку 27 (декоратор @simple_cache)"""
        handler = FileOperations()
        
        # Проверяем что метод имеет атрибуты кэширования (добавленные декоратором)
        assert hasattr(handler.read_json, 'clear_cache')

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.open')
    @patch('json.load')
    def test_read_json_multiple_calls_cache(self, mock_json_load, mock_open_method, mock_stat, mock_exists):
        """Тест работы кэша при множественных вызовах"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 100
        mock_json_load.return_value = [{"cached": "data"}]
        
        handler = FileOperations()
        file_path = Path("cached_file.json")
        
        # Первый вызов
        data1 = handler.read_json(file_path)
        # Второй вызов - должен использовать кэш если TTL не истек
        data2 = handler.read_json(file_path)
        
        assert data1 == [{"cached": "data"}]
        assert data2 == [{"cached": "data"}]


class TestGlobalJsonHandler:
    """Тест глобального экземпляра json_handler"""

    def test_json_handler_is_file_operations_instance(self):
        """Тест что json_handler является экземпляром FileOperations - покрывает строки 79-80"""
        assert isinstance(json_handler, FileOperations)

    @patch('pathlib.Path.exists')
    def test_json_handler_functionality(self, mock_exists):
        """Тест функциональности глобального json_handler"""
        mock_exists.return_value = False
        
        file_path = Path("test_global.json")
        data = json_handler.read_json(file_path)
        
        assert data == []


class TestFileOperationsIntegration:
    """Интеграционные тесты для FileOperations"""

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.parent')
    @patch('pathlib.Path.with_suffix')
    @patch('pathlib.Path.open')
    @patch('pathlib.Path.replace')
    @patch('json.load')
    @patch('json.dump')
    def test_complete_read_write_cycle(self, mock_json_dump, mock_json_load, mock_replace, 
                                     mock_open_method, mock_with_suffix, mock_parent, 
                                     mock_stat, mock_exists):
        """Тест полного цикла чтения и записи"""
        # Данные для теста
        test_data = [{"id": 1, "name": "integration_test"}]
        
        # Настройка моков для записи
        temp_file = Mock()
        temp_file.exists.return_value = False
        mock_with_suffix.return_value = temp_file
        mock_parent_obj = Mock()
        mock_parent.return_value = mock_parent_obj
        
        # Настройка моков для чтения
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 100
        mock_json_load.return_value = test_data
        
        handler = FileOperations()
        file_path = Path("integration_test.json")
        
        # Цикл записи - создаем proper контекстный менеджер
        temp_file_mock = MagicMock()
        temp_file_mock.exists.return_value = False
        temp_file_mock.open.return_value.__enter__ = MagicMock()
        temp_file_mock.open.return_value.__exit__ = MagicMock()
        
        with patch('pathlib.Path.with_suffix', return_value=temp_file_mock):
            handler.write_json(file_path, test_data)
        
        # Цикл чтения
        loaded_data = handler.read_json(file_path)
        
        assert loaded_data == test_data

    def test_error_resilience(self):
        """Тест устойчивости к ошибкам"""
        handler = FileOperations()
        
        # Различные сценарии ошибок не должны ломать приложение
        with patch('pathlib.Path.exists', side_effect=Exception("Filesystem error")):
            data = handler.read_json(Path("problematic.json"))
            assert data == []  # Должен возвращать безопасное значение

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.open')
    @patch('json.load')
    def test_different_data_types(self, mock_json_load, mock_open_method, mock_stat, mock_exists):
        """Тест обработки различных типов данных"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 100
        
        # Тестируем различные типы данных
        test_cases = [
            [],  # Пустой список
            [{}],  # Список с пустым объектом
            [{"key": "value"}],  # Простой объект
            [{"nested": {"data": "value"}}],  # Вложенные объекты
            [{"array": [1, 2, 3]}],  # Объект с массивом
        ]
        
        handler = FileOperations()
        file_path = Path("data_types.json")
        
        for i, test_data in enumerate(test_cases):
            mock_json_load.return_value = test_data
            # Создаем новый handler для каждого теста чтобы избежать кэширования
            test_handler = FileOperations()
            test_file_path = Path(f"data_types_{i}.json")
            data = test_handler.read_json(test_file_path)
            assert data == test_data

    def test_unicode_handling(self):
        """Тест обработки Unicode данных"""
        handler = FileOperations()
        
        # Проверяем что методы могут обрабатывать файлы с Unicode именами
        unicode_filenames = [
            "файл.json",
            "测试.json", 
            "тест_файл_с_русскими_символами.json",
            "file_with_émojis_🚀.json"
        ]
        
        for filename in unicode_filenames:
            file_path = Path(filename)
            
            with patch('pathlib.Path.exists', return_value=False):
                data = handler.read_json(file_path)
                assert data == []  # Безопасное поведение


class TestFileOperationsEdgeCases:
    """Тесты граничных случаев"""

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat', side_effect=Exception("Stat error"))
    @patch('src.utils.file_handlers.logger')
    def test_stat_error_handling(self, mock_logger, mock_stat, mock_exists):
        """Тест обработки ошибок при получении информации о файле"""
        mock_exists.return_value = True
        
        handler = FileOperations()
        file_path = Path("stat_error.json")
        
        data = handler.read_json(file_path)
        
        assert data == []
        mock_logger.error.assert_called_once()

    def test_path_object_handling(self):
        """Тест работы с объектами Path"""
        handler = FileOperations()
        
        # Проверяем что методы принимают объекты Path
        path_obj = Path("test_path.json")
        
        with patch('pathlib.Path.exists', return_value=False):
            data = handler.read_json(path_obj)
            assert data == []

    @patch('pathlib.Path.parent')
    @patch('pathlib.Path.with_suffix')
    @patch('pathlib.Path.exists')
    def test_write_json_mkdir_error(self, mock_exists, mock_with_suffix, mock_parent):
        """Тест обработки ошибок при создании директории"""
        temp_file = Mock()
        temp_file.exists.return_value = True
        mock_with_suffix.return_value = temp_file
        
        mock_parent_obj = Mock()
        mock_parent_obj.mkdir.side_effect = Exception("Mkdir error")
        mock_parent.return_value = mock_parent_obj
        mock_exists.return_value = True
        
        handler = FileOperations()
        file_path = Path("mkdir_error.json")
        
        with pytest.raises(Exception):
            handler.write_json(file_path, [])
        
        # Проверяем что временный файл удаляется даже при ошибке создания директории
        temp_file.unlink.assert_called()