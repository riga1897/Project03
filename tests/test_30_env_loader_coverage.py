#!/usr/bin/env python3
"""
Тесты модуля env_loader для 100% покрытия.

Покрывает все функции в src/utils/env_loader.py:
- EnvLoader - класс для загрузки переменных окружения из .env файла
- load_env_file - загрузка .env файла с парсингом
- get_env_var - получение переменной окружения со значением по умолчанию
- get_env_var_int - получение переменной как целое число

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

import logging
import os
import pytest
from typing import Optional
from unittest.mock import patch, mock_open, MagicMock

# Импорты из реального кода для покрытия
from src.utils.env_loader import EnvLoader


class TestEnvLoaderLoadEnvFile:
    """100% покрытие load_env_file метода"""

    def setup_method(self):
        """Сброс состояния класса перед каждым тестом"""
        EnvLoader._loaded = False

    @patch('src.utils.env_loader.os.path.exists')
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_already_loaded(self, mock_logger, mock_exists):
        """Покрытие случая когда файл уже загружен"""
        EnvLoader._loaded = True
        
        EnvLoader.load_env_file()
        
        # Не должно быть никаких обращений к файловой системе
        mock_exists.assert_not_called()
        mock_logger.assert_not_called()

    @patch('src.utils.env_loader.os.path.exists')
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_not_found(self, mock_logger, mock_exists):
        """Покрытие случая когда .env файл не найден"""
        mock_exists.return_value = False
        
        EnvLoader.load_env_file()
        
        assert EnvLoader._loaded is True
        mock_exists.assert_called_once_with(".env")
        mock_logger.warning.assert_any_call("Файл .env не найден в следующих местах: ['.env']")
        mock_logger.warning.assert_any_call("Используются переменные окружения системы.")

    @patch('src.utils.env_loader.os.path.exists')
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_custom_path_not_found(self, mock_logger, mock_exists):
        """Покрытие случая когда кастомный .env файл не найден"""
        mock_exists.return_value = False
        custom_path = "/custom/.env"
        
        EnvLoader.load_env_file(custom_path)
        
        assert EnvLoader._loaded is True
        mock_exists.assert_called_once_with(custom_path)
        mock_logger.warning.assert_any_call(f"Файл .env не найден в следующих местах: ['{custom_path}']")

    @patch('src.utils.env_loader.os.path.exists')
    @patch('src.utils.env_loader.os.environ', {})
    @patch('builtins.open', mock_open(read_data="KEY1=value1\nKEY2=value2\n"))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_success(self, mock_logger, mock_exists):
        """Покрытие успешной загрузки .env файла"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True):
            EnvLoader.load_env_file()
        
        assert EnvLoader._loaded is True
        mock_logger.info.assert_called_once_with("Переменные окружения загружены из .env")

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data='KEY1="quoted value"\nKEY2=\'single quoted\'\n'))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_quoted_values(self, mock_logger, mock_exists):
        """Покрытие парсинга значений в кавычках"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True) as mock_environ:
            EnvLoader.load_env_file()
            
            # Проверяем что кавычки были убраны
            assert mock_environ['KEY1'] == 'quoted value'
            assert mock_environ['KEY2'] == 'single quoted'

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data="# Comment line\n\nKEY1=value1\n  \n"))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_skip_comments_and_empty(self, mock_logger, mock_exists):
        """Покрытие пропуска комментариев и пустых строк"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True) as mock_environ:
            EnvLoader.load_env_file()
            
            # Только KEY1 должна быть загружена
            assert 'KEY1' in mock_environ
            assert mock_environ['KEY1'] == 'value1'

    @patch('src.utils.env_loader.os.path.exists')
    @patch('src.utils.env_loader.os.environ', {})
    @patch('builtins.open', mock_open(read_data="INVALID_LINE_WITHOUT_EQUALS\nKEY1=value1\n"))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_invalid_format_warning(self, mock_logger, mock_exists):
        """Покрытие предупреждения о неверном формате строки"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True):
            EnvLoader.load_env_file()
        
        mock_logger.warning.assert_called_with("Неверный формат строки 1 в .env: INVALID_LINE_WITHOUT_EQUALS")

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data="KEY1=new_value\nKEY2=value2\n"))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_preserve_existing_env_vars(self, mock_logger, mock_exists):
        """Покрытие сохранения уже существующих переменных окружения"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {'KEY1': 'existing_value'}, clear=True) as mock_environ:
            EnvLoader.load_env_file()
            
            # Существующая переменная не должна быть перезаписана
            assert mock_environ['KEY1'] == 'existing_value'
            assert mock_environ['KEY2'] == 'value2'

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_file_read_error(self, mock_logger, mock_open, mock_exists):
        """Покрытие ошибки чтения файла"""
        mock_exists.return_value = True
        
        EnvLoader.load_env_file()
        
        assert EnvLoader._loaded is True
        mock_logger.error.assert_called_once_with("Ошибка при загрузке .env: Permission denied")

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte'))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_encoding_error(self, mock_logger, mock_open, mock_exists):
        """Покрытие ошибки кодировки файла"""
        mock_exists.return_value = True
        
        EnvLoader.load_env_file()
        
        assert EnvLoader._loaded is True
        # Проверяем что ошибка была залогирована
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Ошибка при загрузке .env:" in error_call

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data="KEY1=value with=multiple equals\n"))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_value_with_equals(self, mock_logger, mock_exists):
        """Покрытие значения со знаками равенства"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True) as mock_environ:
            EnvLoader.load_env_file()
            
            # split("=", 1) должен оставить все после первого "=" как значение
            assert mock_environ['KEY1'] == 'value with=multiple equals'

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data="  KEY1  =  value1  \n"))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_whitespace_trimming(self, mock_logger, mock_exists):
        """Покрытие обрезки пробелов вокруг ключей и значений"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True) as mock_environ:
            EnvLoader.load_env_file()
            
            assert mock_environ['KEY1'] == 'value1'

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data='KEY1=""\nKEY2=\'\'\n'))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_empty_quoted_values(self, mock_logger, mock_exists):
        """Покрытие пустых значений в кавычках"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True) as mock_environ:
            EnvLoader.load_env_file()
            
            assert mock_environ['KEY1'] == ''
            assert mock_environ['KEY2'] == ''

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data='KEY1="value with spaces"\n'))
    @patch('src.utils.env_loader.logger')
    def test_load_env_file_debug_logging(self, mock_logger, mock_exists):
        """Покрытие debug логирования загруженных переменных"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True):
            EnvLoader.load_env_file()
        
        mock_logger.debug.assert_called_with("Загружена переменная окружения: KEY1")


class TestEnvLoaderGetEnvVar:
    """100% покрытие get_env_var статического метода"""

    def test_get_env_var_with_value(self):
        """Покрытие получения существующей переменной окружения"""
        with patch.dict('os.environ', {'TEST_KEY': 'test_value'}):
            result = EnvLoader.get_env_var("TEST_KEY", "default")
            assert result == "test_value"

    def test_get_env_var_with_default(self):
        """Покрытие получения переменной с значением по умолчанию"""
        with patch.dict('os.environ', {}, clear=True):
            result = EnvLoader.get_env_var("MISSING_KEY", "default_value")
            assert result == "default_value"

    def test_get_env_var_no_default(self):
        """Покрытие получения переменной без явного default"""
        with patch.dict('os.environ', {}, clear=True):
            result = EnvLoader.get_env_var("KEY")
            assert result == ""

    def test_get_env_var_none_default(self):
        """Покрытие получения переменной с None как default"""
        with patch.dict('os.environ', {}, clear=True):
            result = EnvLoader.get_env_var("KEY", None)
            assert result is None

    def test_get_env_var_empty_string_default(self):
        """Покрытие получения переменной с пустой строкой как default"""
        with patch.dict('os.environ', {}, clear=True):
            result = EnvLoader.get_env_var("KEY", "")
            assert result == ""


class TestEnvLoaderGetEnvVarInt:
    """100% покрытие get_env_var_int статического метода"""

    def test_get_env_var_int_valid_integer(self):
        """Покрытие получения корректного целого числа"""
        with patch.dict('os.environ', {'INT_KEY': '42'}):
            result = EnvLoader.get_env_var_int("INT_KEY", 0)
            assert result == 42

    def test_get_env_var_int_negative_integer(self):
        """Покрытие получения отрицательного целого числа"""
        with patch.dict('os.environ', {'NEG_KEY': '-123'}):
            result = EnvLoader.get_env_var_int("NEG_KEY", 0)
            assert result == -123

    def test_get_env_var_int_zero(self):
        """Покрытие получения нуля"""
        with patch.dict('os.environ', {'ZERO_KEY': '0'}):
            result = EnvLoader.get_env_var_int("ZERO_KEY", 999)
            assert result == 0

    def test_get_env_var_int_none_value(self):
        """Покрытие случая когда переменная не установлена (None)"""
        with patch.dict('os.environ', {}, clear=True):
            result = EnvLoader.get_env_var_int("MISSING_KEY", 100)
            assert result == 100

    @patch('src.utils.env_loader.logger')
    def test_get_env_var_int_invalid_value(self, mock_logger):
        """Покрытие случая с невалидным значением для int"""
        with patch.dict('os.environ', {'INVALID_KEY': 'not_a_number'}):
            result = EnvLoader.get_env_var_int("INVALID_KEY", 50)
            
            assert result == 50
            mock_logger.warning.assert_called_once_with(
                "Не удалось преобразовать INVALID_KEY в int, используется значение по умолчанию: 50"
            )

    @patch('src.utils.env_loader.logger')
    def test_get_env_var_int_float_value(self, mock_logger):
        """Покрытие случая с float значением"""
        with patch.dict('os.environ', {'FLOAT_KEY': '42.5'}):
            result = EnvLoader.get_env_var_int("FLOAT_KEY", 25)
            
            assert result == 25  # Default value из-за ValueError
            mock_logger.warning.assert_called_once()

    @patch('src.utils.env_loader.logger')
    def test_get_env_var_int_empty_string(self, mock_logger):
        """Покрытие случая с пустой строкой"""
        with patch.dict('os.environ', {'EMPTY_KEY': ''}):
            result = EnvLoader.get_env_var_int("EMPTY_KEY", 75)
            
            assert result == 75  # Default value из-за ValueError
            mock_logger.warning.assert_called_once()

    def test_get_env_var_int_default_zero(self):
        """Покрытие использования default=0"""
        with patch.dict('os.environ', {}, clear=True):
            result = EnvLoader.get_env_var_int("KEY")  # default=0 по умолчанию
            assert result == 0

    def test_get_env_var_int_large_number(self):
        """Покрытие работы с большими числами"""
        with patch.dict('os.environ', {'LARGE_KEY': '999999999'}):
            result = EnvLoader.get_env_var_int("LARGE_KEY", 1)
            assert result == 999999999

    def test_get_env_var_int_whitespace(self):
        """Покрытие случая со значением содержащим пробелы"""
        with patch.dict('os.environ', {'SPACE_KEY': '  123  '}):
            result = EnvLoader.get_env_var_int("SPACE_KEY", 10)
            # int() автоматически обрезает пробелы
            assert result == 123


class TestEnvLoaderIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    def setup_method(self):
        """Сброс состояния класса перед каждым тестом"""
        EnvLoader._loaded = False

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data="DATABASE_URL=postgres://user:pass@host:5432/db\nDEBUG=true\nPORT=8080\n"))
    @patch('src.utils.env_loader.logger')
    def test_full_workflow_scenario(self, mock_logger, mock_exists):
        """Покрытие полного рабочего сценария"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True) as mock_environ:
            # Загружаем файл
            EnvLoader.load_env_file()
            
            # Проверяем что переменные загружены
            assert mock_environ['DATABASE_URL'] == 'postgres://user:pass@host:5432/db'
            assert mock_environ['DEBUG'] == 'true'
            assert mock_environ['PORT'] == '8080'
        
            # Тестируем получение переменных через реальные os.environ
            db_url = EnvLoader.get_env_var('DATABASE_URL')
            debug = EnvLoader.get_env_var('DEBUG', 'false')
            port = EnvLoader.get_env_var_int('PORT', 3000)
            missing = EnvLoader.get_env_var('MISSING', 'default')
            
            assert db_url == 'postgres://user:pass@host:5432/db'
            assert debug == 'true'
            assert port == 8080
            assert missing == 'default'

    def test_class_state_consistency(self):
        """Покрытие согласованности состояния класса"""
        # Начальное состояние
        assert EnvLoader._loaded is False
        
        with patch('src.utils.env_loader.os.path.exists', return_value=False):
            with patch('src.utils.env_loader.logger'):
                EnvLoader.load_env_file()
        
        # После первой загрузки
        assert EnvLoader._loaded is True
        
        # Повторные вызовы не должны ничего делать
        with patch('src.utils.env_loader.os.path.exists') as mock_exists:
            EnvLoader.load_env_file()
            mock_exists.assert_not_called()

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data="KEY1=value1\nKEY2=value2\n"))
    @patch('src.utils.env_loader.logger')
    def test_multiple_file_paths_logic(self, mock_logger, mock_exists):
        """Покрытие логики поиска файла в нескольких путях"""
        mock_exists.return_value = True
        custom_path = "custom.env"
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True):
            EnvLoader.load_env_file(custom_path)
        
        # Должен проверить кастомный путь
        mock_exists.assert_called_once_with(custom_path)

    def test_static_methods_independence(self):
        """Покрытие независимости статических методов от состояния класса"""
        # Статические методы должны работать независимо от _loaded флага
        EnvLoader._loaded = False
        
        with patch.dict('os.environ', {'TEST_KEY': 'test', 'INT_KEY': '42'}):
            result1 = EnvLoader.get_env_var('TEST_KEY')
            assert result1 == 'test'
            
            result2 = EnvLoader.get_env_var_int('INT_KEY')
            assert result2 == 42
        
        # Состояние не должно измениться
        assert EnvLoader._loaded is False

    @patch('src.utils.env_loader.os.path.exists')
    @patch('builtins.open', mock_open(read_data="# Database config\nDB_HOST=localhost\n\n# API settings\nAPI_KEY=secret\n"))
    @patch('src.utils.env_loader.logger')
    def test_complex_env_file_parsing(self, mock_logger, mock_exists):
        """Покрытие сложного парсинга .env файла с комментариями"""
        mock_exists.return_value = True
        
        with patch.dict('src.utils.env_loader.os.environ', {}, clear=True) as mock_environ:
            EnvLoader.load_env_file()
            
            # Только переменные должны быть загружены, комментарии пропущены
            assert 'DB_HOST' in mock_environ
            assert 'API_KEY' in mock_environ
            assert mock_environ['DB_HOST'] == 'localhost'
            assert mock_environ['API_KEY'] == 'secret'