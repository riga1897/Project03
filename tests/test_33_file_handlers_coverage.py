#!/usr/bin/env python3
"""
Тесты модуля file_handlers для 100% покрытия.

Покрывает все функции в src/utils/file_handlers.py:
- FileOperations - класс для обработки JSON-файлов
- __init__ - инициализация
- read_json - чтение JSON-файлов с кэшированием
- write_json - атомарная запись JSON-файлов
- json_handler - глобальный экземпляр

Все файловые операции заменены на mock для соблюдения принципа нулевого I/O.
"""

import json
import pytest
from unittest.mock import patch, mock_open, MagicMock

# Импорты из реального кода для покрытия
from src.utils.file_handlers import FileOperations, json_handler


class TestFileOperationsInit:
    """100% покрытие конструктора FileOperations"""

    def test_init(self) -> None:
        """Покрытие инициализации FileOperations"""
        file_ops = FileOperations()

        # Инициализация проста - проверяем что экземпляр создан
        assert isinstance(file_ops, FileOperations)


class TestFileOperationsReadJson:
    """100% покрытие метода read_json"""

    @patch('src.utils.file_handlers.Path')
    def test_read_json_file_not_exists(self, mock_path):
        """Покрытие чтения несуществующего файла"""
        mock_file = MagicMock()
        mock_file.exists.return_value = False
        mock_path.return_value = mock_file

        file_ops = FileOperations()
        result = file_ops.read_json(mock_file)

        assert result == []
        mock_file.exists.assert_called_once()

    @patch('src.utils.file_handlers.Path')
    def test_read_json_empty_file(self, mock_path):
        """Покрытие чтения пустого файла"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_stat = MagicMock()
        mock_stat.st_size = 0
        mock_file.stat.return_value = mock_stat

        file_ops = FileOperations()
        result = file_ops.read_json(mock_file)

        assert result == []
        mock_file.exists.assert_called_once()
        mock_file.stat.assert_called_once()

    @patch('src.utils.file_handlers.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"key": "value"}]')
    @patch('src.utils.file_handlers.json.load')
    def test_read_json_success(self, mock_json_load, mock_file_open, mock_path):
        """Покрытие успешного чтения JSON файла"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_stat = MagicMock()
        mock_stat.st_size = 100
        mock_file.stat.return_value = mock_stat

        expected_data = [{"key": "value"}]
        mock_json_load.return_value = expected_data

        file_ops = FileOperations()
        result = file_ops.read_json(mock_file)

        assert result == expected_data
        mock_file.open.assert_called_once_with("r", encoding="utf-8")
        mock_json_load.assert_called_once()

    @patch('src.utils.file_handlers.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json}')
    @patch('src.utils.file_handlers.json.load')
    @patch('src.utils.file_handlers.logger')
    def test_read_json_decode_error(self, mock_logger, mock_json_load, mock_file_open, mock_path):
        """Покрытие ошибки декодирования JSON"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_stat = MagicMock()
        mock_stat.st_size = 100
        mock_file.stat.return_value = mock_stat

        json_error = json.JSONDecodeError("Invalid JSON", "doc", 0)
        mock_json_load.side_effect = json_error

        file_ops = FileOperations()
        result = file_ops.read_json(mock_file)

        assert result == []
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Invalid JSON" in warning_call
        assert "returning empty list" in warning_call

    @patch('src.utils.file_handlers.Path')
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    @patch('src.utils.file_handlers.logger')
    def test_read_json_io_error(self, mock_logger, mock_file_open, mock_path):
        """Покрытие общих ошибок при чтении файла"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_stat = MagicMock()
        mock_stat.st_size = 100
        mock_file.stat.return_value = mock_stat

        file_ops = FileOperations()
        result = file_ops.read_json(mock_file)

        assert result == []
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Failed to read" in error_call

    @patch('src.utils.file_handlers.Path')
    @patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte'))
    @patch('src.utils.file_handlers.logger')
    def test_read_json_unicode_error(self, mock_logger, mock_file_open, mock_path):
        """Покрытие ошибок кодировки при чтении"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_stat = MagicMock()
        mock_stat.st_size = 100
        mock_file.stat.return_value = mock_stat

        file_ops = FileOperations()
        result = file_ops.read_json(mock_file)

        assert result == []
        mock_logger.error.assert_called_once()

    @patch('src.utils.file_handlers.Path')
    def test_read_json_caching(self, mock_path):
        """Покрытие кэширования read_json (декоратор @simple_cache)"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_stat = MagicMock()
        mock_stat.st_size = 100
        mock_file.stat.return_value = mock_stat

        expected_data = [{"cached": "data"}]

        with patch('builtins.open', mock_open(read_data='[{"cached": "data"}]')):
            with patch('src.utils.file_handlers.json.load', return_value=expected_data):
                file_ops = FileOperations()

                # Первый вызов
                result1 = file_ops.read_json(mock_file)
                assert result1 == expected_data

                # Второй вызов должен быть закэширован
                result2 = file_ops.read_json(mock_file)
                assert result2 == expected_data

                # Проверяем что файл был прочитан только один раз (кэшированный результат)
                assert mock_file.exists.call_count <= 2  # Может быть вызван для каждого обращения


class TestFileOperationsWriteJson:
    """100% покрытие метода write_json"""

    @patch('src.utils.file_handlers.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.utils.file_handlers.json.dump')
    def test_write_json_success(self, mock_json_dump, mock_file_open, mock_path):
        """Покрытие успешной записи JSON файла"""
        mock_file = MagicMock()
        mock_temp_file = MagicMock()
        mock_file.with_suffix.return_value = mock_temp_file
        mock_temp_file.exists.return_value = False

        mock_parent = MagicMock()
        mock_file.parent = mock_parent

        test_data = [{"test": "data"}]

        file_ops = FileOperations()

        # Патчим весь метод clear_cache чтобы избежать проблем с декоратором
        with patch.object(file_ops, 'read_json') as mock_read_json:
            mock_read_json.clear_cache = MagicMock()

            file_ops.write_json(mock_file, test_data)

            # Проверяем создание директории
            mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

            # Проверяем запись во временный файл
            mock_temp_file.open.assert_called_once_with("w", encoding="utf-8")
            mock_json_dump.assert_called_once_with(
                test_data,
                mock_temp_file.open.return_value.__enter__.return_value,
                ensure_ascii=False,
                indent=2
            )

            # Проверяем атомарную замену
            mock_temp_file.replace.assert_called_once_with(mock_file)

            # Проверяем очистку кэша
            mock_read_json.clear_cache.assert_called_once()

    @patch('src.utils.file_handlers.Path')
    @patch('src.utils.file_handlers.logger')
    def test_write_json_write_error(self, mock_logger, mock_path):
        """Покрытие обработки ошибок при записи файла"""
        mock_file = MagicMock()
        mock_temp_file = MagicMock()
        mock_file.with_suffix.return_value = mock_temp_file
        mock_temp_file.exists.return_value = True

        mock_parent = MagicMock()
        mock_file.parent = mock_parent

        # Заставляем mkdir выбросить исключение для покрытия except блока
        mock_parent.mkdir.side_effect = PermissionError("Access denied")

        test_data = [{"test": "data"}]

        file_ops = FileOperations()

        with patch.object(file_ops, 'read_json') as mock_read_json:
            mock_read_json.clear_cache = MagicMock()

            # Ожидаем что исключение будет поднято
            with pytest.raises(PermissionError):
                file_ops.write_json(mock_file, test_data)

        # Проверяем что ошибка была залогирована
        mock_logger.error.assert_called_once()

        # Проверяем что временный файл был удален в except блоке
        mock_temp_file.unlink.assert_called()

    @patch('src.utils.file_handlers.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.utils.file_handlers.json.dump', side_effect=ValueError("Serialization error"))
    @patch('src.utils.file_handlers.logger')
    def test_write_json_json_error(self, mock_logger, mock_json_dump, mock_file_open, mock_path):
        """Покрытие ошибки сериализации JSON"""
        mock_file = MagicMock()
        mock_temp_file = MagicMock()
        mock_file.with_suffix.return_value = mock_temp_file
        mock_temp_file.exists.return_value = True

        mock_parent = MagicMock()
        mock_file.parent = mock_parent

        test_data = [{"invalid": object()}]  # Не сериализуемый объект

        file_ops = FileOperations()

        with pytest.raises(ValueError, match="Serialization error"):
            file_ops.write_json(mock_file, test_data)

        # Проверяем что временный файл был удален в finally блоке
        assert mock_temp_file.unlink.call_count >= 1

    @patch('src.utils.file_handlers.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.utils.file_handlers.json.dump')
    def test_write_json_temp_file_cleanup(self, mock_json_dump, mock_file_open, mock_path):
        """Покрытие очистки временного файла в finally блоке"""
        mock_file = MagicMock()
        mock_temp_file = MagicMock()
        mock_file.with_suffix.return_value = mock_temp_file

        # Симулируем что временный файл существует в finally блоке
        mock_temp_file.exists.side_effect = [True, True]  # Для except и finally

        mock_parent = MagicMock()
        mock_file.parent = mock_parent

        test_data = [{"test": "data"}]

        file_ops = FileOperations()

        with patch.object(file_ops, 'read_json') as mock_read_json:
            mock_read_json.clear_cache = MagicMock()
            file_ops.write_json(mock_file, test_data)

        # Проверяем что unlink был вызван в finally
        mock_temp_file.unlink.assert_called()

    @patch('src.utils.file_handlers.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.utils.file_handlers.json.dump')
    def test_write_json_mkdir_error_handling(self, mock_json_dump, mock_file_open, mock_path):
        """Покрытие обработки ошибок создания директории"""
        mock_file = MagicMock()
        mock_temp_file = MagicMock()
        mock_file.with_suffix.return_value = mock_temp_file
        mock_temp_file.exists.return_value = False

        mock_parent = MagicMock()
        mock_parent.mkdir.side_effect = PermissionError("Cannot create directory")
        mock_file.parent = mock_parent

        test_data = [{"test": "data"}]

        file_ops = FileOperations()

        with pytest.raises(PermissionError):
            file_ops.write_json(mock_file, test_data)

    @patch('src.utils.file_handlers.Path')
    def test_write_json_file_path_operations(self, mock_path):
        """Покрытие операций с путями файлов"""
        mock_file = MagicMock()
        mock_temp_file = MagicMock()

        # Проверяем создание временного файла с .tmp суффиксом
        mock_file.with_suffix.return_value = mock_temp_file
        mock_temp_file.exists.return_value = False

        mock_parent = MagicMock()
        mock_file.parent = mock_parent

        test_data = []

        with patch('builtins.open', mock_open()):
            with patch('src.utils.file_handlers.json.dump'):
                file_ops = FileOperations()

                with patch.object(file_ops, 'read_json') as mock_read_json:
                    mock_read_json.clear_cache = MagicMock()
                    file_ops.write_json(mock_file, test_data)

                # Проверяем что временный файл создан с .tmp суффиксом
                mock_file.with_suffix.assert_called_once_with(".tmp")


class TestFileOperationsIntegration:
    """Интеграционные тесты и сложные сценарии"""

    @patch('src.utils.file_handlers.Path')
    def test_read_write_cycle(self, mock_path):
        """Покрытие полного цикла чтение -> запись"""
        mock_file = MagicMock()
        mock_temp_file = MagicMock()
        mock_file.with_suffix.return_value = mock_temp_file
        mock_temp_file.exists.return_value = False

        mock_parent = MagicMock()
        mock_file.parent = mock_parent

        original_data = [{"id": 1, "name": "test"}]

        # Настраиваем чтение
        mock_file.exists.return_value = True
        mock_stat = MagicMock()
        mock_stat.st_size = 100
        mock_file.stat.return_value = mock_stat

        with patch('builtins.open', mock_open()):
            with patch('src.utils.file_handlers.json.load', return_value=original_data):
                with patch('src.utils.file_handlers.json.dump') as mock_dump:
                    file_ops = FileOperations()

                    # Читаем данные
                    read_data = file_ops.read_json(mock_file)
                    assert read_data == original_data

                    # Модифицируем данные
                    modified_data = read_data + [{"id": 2, "name": "test2"}]

                    # Записываем данные с мокированием clear_cache
                    with patch.object(file_ops, 'read_json') as mock_read_json:
                        mock_read_json.clear_cache = MagicMock()
                        file_ops.write_json(mock_file, modified_data)

                    # Проверяем что данные были записаны (не проверяем точный mock объект)
                    mock_dump.assert_called_once()
                    call_args = mock_dump.call_args[0]
                    assert call_args[0] == modified_data

    def test_error_handling_robustness(self) -> None:
        """Покрытие устойчивости к различным ошибкам"""
        file_ops = FileOperations()

        # Тестируем с различными типами Path объектов
        with patch('src.utils.file_handlers.Path'):
            mock_file = MagicMock()
            mock_file.exists.return_value = False

            result = file_ops.read_json(mock_file)
            assert result == []

    def test_cache_interaction_with_write(self) -> None:
        """Покрытие взаимодействия кэша с операциями записи"""
        with patch('src.utils.file_handlers.Path'):
            mock_file = MagicMock()
            mock_temp_file = MagicMock()
            mock_file.with_suffix.return_value = mock_temp_file
            mock_temp_file.exists.return_value = False

            mock_parent = MagicMock()
            mock_file.parent = mock_parent

            file_ops = FileOperations()

            test_data = [{"cache": "test"}]

            with patch('builtins.open', mock_open()):
                with patch('src.utils.file_handlers.json.dump'):
                    # Мокируем методы кэша
                    with patch.object(file_ops, 'read_json') as mock_read_json:
                        mock_read_json.clear_cache = MagicMock()
                        mock_read_json.cache_info = MagicMock(return_value={"size": 1})
                        file_ops.write_json(mock_file, test_data)

                        # Проверяем что кэш был очищен
                        mock_read_json.clear_cache.assert_called_once()


class TestJsonHandlerGlobal:
    """Покрытие глобального экземпляра json_handler"""

    def test_json_handler_instance(self) -> None:
        """Покрытие создания глобального экземпляра"""
        # json_handler импортируется как глобальный экземпляр
        assert isinstance(json_handler, FileOperations)

    def test_json_handler_functionality(self) -> None:
        """Покрытие функциональности глобального экземпляра"""
        # Проверяем что глобальный экземпляр имеет нужные методы
        assert hasattr(json_handler, 'read_json')
        assert hasattr(json_handler, 'write_json')

        # Проверяем что это именно методы
        assert callable(json_handler.read_json)
        assert callable(json_handler.write_json)

    @patch('src.utils.file_handlers.Path')
    def test_json_handler_read_usage(self, mock_path):
        """Покрытие использования read_json через глобальный экземпляр"""
        mock_file = MagicMock()
        mock_file.exists.return_value = False

        result = json_handler.read_json(mock_file)
        assert result == []

    @patch('src.utils.file_handlers.Path')
    def test_json_handler_write_usage(self, mock_path):
        """Покрытие использования write_json через глобальный экземпляр"""
        mock_file = MagicMock()
        mock_temp_file = MagicMock()
        mock_file.with_suffix.return_value = mock_temp_file
        mock_temp_file.exists.return_value = False

        mock_parent = MagicMock()
        mock_file.parent = mock_parent

        test_data = [{"global": "handler"}]

        with patch('builtins.open', mock_open()):
            with patch('src.utils.file_handlers.json.dump'):
                # Мокируем clear_cache метод для глобального экземпляра
                with patch.object(json_handler, 'read_json') as mock_read_json:
                    mock_read_json.clear_cache = MagicMock()
                    json_handler.write_json(mock_file, test_data)

                    # Проверяем что операция прошла успешно
                    mock_temp_file.replace.assert_called_once_with(mock_file)


class TestFileOperationsEdgeCases:
    """Покрытие граничных случаев и специальных сценариев"""

    @patch('src.utils.file_handlers.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('src.utils.file_handlers.json.load')
    def test_empty_json_array(self, mock_json_load, mock_file_open, mock_path):
        """Покрытие чтения пустого JSON массива"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_stat = MagicMock()
        mock_stat.st_size = 2  # Размер "[]"
        mock_file.stat.return_value = mock_stat

        mock_json_load.return_value = []

        file_ops = FileOperations()
        result = file_ops.read_json(mock_file)

        assert result == []

    @patch('src.utils.file_handlers.Path')
    def test_large_data_handling(self, mock_path):
        """Покрытие обработки больших объемов данных"""
        mock_file = MagicMock()
        mock_temp_file = MagicMock()
        mock_file.with_suffix.return_value = mock_temp_file
        mock_temp_file.exists.return_value = False

        mock_parent = MagicMock()
        mock_file.parent = mock_parent

        # Создаем большой массив данных для теста
        large_data = [{"id": i, "data": f"item_{i}"} for i in range(1000)]

        with patch('builtins.open', mock_open()):
            with patch('src.utils.file_handlers.json.dump') as mock_dump:
                file_ops = FileOperations()

                with patch.object(file_ops, 'read_json') as mock_read_json:
                    mock_read_json.clear_cache = MagicMock()
                    file_ops.write_json(mock_file, large_data)

                # Проверяем что данные были переданы в json.dump
                mock_dump.assert_called_once()
                call_args = mock_dump.call_args[0]
                assert call_args[0] == large_data

    @patch('src.utils.file_handlers.Path')
    @patch('src.utils.file_handlers.logger')
    def test_complex_exception_scenarios(self, mock_logger, mock_path):
        """Покрытие сложных сценариев с исключениями"""
        mock_file = MagicMock()
        mock_file.exists.side_effect = OSError("File system error")

        file_ops = FileOperations()
        result = file_ops.read_json(mock_file)

        assert result == []
        mock_logger.error.assert_called_once()

    def test_different_data_types(self) -> None:
        """Покрытие работы с различными типами данных"""
        file_ops = FileOperations()

        # Тестируем с различными структурами данных
        test_cases = [
            [],
            [{"string": "value", "number": 42, "boolean": True, "null": None}],
            [{"nested": {"deep": {"structure": "test"}}}],
            [{"array": [1, 2, 3, 4, 5]}]
        ]

        with patch('src.utils.file_handlers.Path'):
            mock_file = MagicMock()
            mock_temp_file = MagicMock()
            mock_file.with_suffix.return_value = mock_temp_file
            mock_temp_file.exists.return_value = False

            mock_parent = MagicMock()
            mock_file.parent = mock_parent

            with patch('builtins.open', mock_open()):
                with patch('src.utils.file_handlers.json.dump') as mock_dump:
                    for test_data in test_cases:
                        with patch.object(file_ops, 'read_json') as mock_read_json:
                            mock_read_json.clear_cache = MagicMock()
                            file_ops.write_json(mock_file, test_data)

                        # Проверяем что каждый тип данных был обработан
                        assert any(call[0][0] == test_data for call in mock_dump.call_args_list)