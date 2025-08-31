
import pytest
from unittest.mock import Mock, patch, mock_open
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.env_loader import EnvLoader, load_env_file


class TestEnvLoader:
    """Тесты для EnvLoader с консолидированными моками"""

    def test_env_loader_initialization(self):
        """Тест инициализации EnvLoader"""
        loader = EnvLoader()
        assert hasattr(loader, 'get_env_var')

    def test_get_env_var_existing(self):
        """Тест получения существующей переменной окружения"""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            loader = EnvLoader()
            result = loader.get_env_var('TEST_VAR')
            assert result == 'test_value'

    def test_get_env_var_with_default(self):
        """Тест получения переменной с значением по умолчанию"""
        loader = EnvLoader()
        result = loader.get_env_var('NON_EXISTENT_VAR', 'default_value')
        assert result == 'default_value'

    @patch('builtins.open', new_callable=mock_open, read_data='KEY1=value1\nKEY2=value2\n# Comment\n')
    @patch('os.path.exists', return_value=True)
    def test_load_env_file_success(self, mock_exists, mock_file):
        """Тест успешной загрузки .env файла"""
        with patch.dict(os.environ, {}, clear=True):
            result = load_env_file(".env")
            assert result is True

    @patch('os.path.exists', return_value=False)
    def test_load_env_file_not_found(self, mock_exists):
        """Тест загрузки несуществующего .env файла"""
        result = load_env_file(".env")
        assert result is False

    @patch('builtins.open', side_effect=OSError("Read error"))
    @patch('os.path.exists', return_value=True)
    def test_load_env_file_read_error(self, mock_exists, mock_file):
        """Тест ошибки чтения .env файла"""
        result = load_env_file(".env")
        assert result is False

    def test_parse_env_line_valid(self):
        """Тест парсинга валидной строки .env"""
        # Используем статический метод напрямую
        key, value = EnvLoader._parse_line("KEY=value")
        assert key == "KEY"
        assert value == "value"

    def test_parse_env_line_invalid(self):
        """Тест парсинга невалидной строки .env"""
        # Комментарий
        result = EnvLoader._parse_line("# This is a comment")
        assert result == (None, None)
        
        # Пустая строка
        result = EnvLoader._parse_line("")
        assert result == (None, None)
        
        # Строка без знака равенства
        result = EnvLoader._parse_line("INVALID_LINE")
        assert result == (None, None)

    @patch.dict(os.environ, {}, clear=True)
    def test_set_environment_variable(self):
        """Тест установки переменной окружения"""
        EnvLoader._set_env_var("TEST_KEY", "test_value")
        assert os.environ.get("TEST_KEY") == "test_value"

    @patch('builtins.open', new_callable=mock_open, read_data='API_KEY=secret123\nDEBUG=true\n')
    @patch('os.path.exists', return_value=True)
    def test_load_env_file_function(self, mock_exists, mock_file):
        """Тест функции load_env_file"""
        with patch.dict(os.environ, {}, clear=True):
            result = load_env_file(".env")
            assert result is True

    def test_env_var_parsing_with_quotes(self):
        """Тест парсинга переменных с кавычками"""
        key, value = EnvLoader._parse_line('KEY="quoted value"')
        assert key == "KEY"
        assert value == "quoted value"

    def test_env_var_parsing_with_spaces(self):
        """Тест парсинга переменных с пробелами"""
        key, value = EnvLoader._parse_line('KEY = value with spaces ')
        assert key == "KEY"
        assert value == "value with spaces"
