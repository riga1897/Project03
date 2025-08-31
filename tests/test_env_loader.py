
import pytest
from unittest.mock import Mock, patch, mock_open
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.env_loader import EnvLoader, load_env_file


class TestEnvLoader:
    """Тесты для EnvLoader"""

    def test_env_loader_initialization(self):
        """Тест инициализации EnvLoader"""
        loader = EnvLoader()
        assert isinstance(loader, EnvLoader)

    @patch('builtins.open', new_callable=mock_open, read_data='KEY1=value1\nKEY2=value2\n# Comment\n')
    @patch('os.path.exists', return_value=True)
    def test_load_env_file_success(self, mock_exists, mock_file):
        """Тест успешной загрузки .env файла"""
        loader = EnvLoader()
        result = loader.load_file(".env")
        
        assert result is True
        mock_file.assert_called_with(".env", "r", encoding="utf-8")

    @patch('os.path.exists', return_value=False)
    def test_load_env_file_not_found(self, mock_exists):
        """Тест загрузки несуществующего .env файла"""
        loader = EnvLoader()
        result = loader.load_file(".env")
        
        assert result is False

    @patch('builtins.open', side_effect=OSError("Read error"))
    @patch('os.path.exists', return_value=True)
    def test_load_env_file_read_error(self, mock_exists, mock_file):
        """Тест ошибки чтения .env файла"""
        loader = EnvLoader()
        result = loader.load_file(".env")
        
        assert result is False

    def test_parse_env_line_valid(self):
        """Тест парсинга валидной строки .env"""
        loader = EnvLoader()
        
        key, value = loader.parse_line("KEY=value")
        assert key == "KEY"
        assert value == "value"
        
        key, value = loader.parse_line("KEY_WITH_UNDERSCORE=complex_value")
        assert key == "KEY_WITH_UNDERSCORE"
        assert value == "complex_value"

    def test_parse_env_line_invalid(self):
        """Тест парсинга невалидной строки .env"""
        loader = EnvLoader()
        
        # Комментарий
        result = loader.parse_line("# This is a comment")
        assert result == (None, None)
        
        # Пустая строка
        result = loader.parse_line("")
        assert result == (None, None)
        
        # Строка без знака равенства
        result = loader.parse_line("INVALID_LINE")
        assert result == (None, None)

    @patch.dict(os.environ, {}, clear=True)
    def test_set_environment_variable(self):
        """Тест установки переменной окружения"""
        loader = EnvLoader()
        loader.set_env_var("TEST_KEY", "test_value")
        
        assert os.environ.get("TEST_KEY") == "test_value"

    def test_get_environment_variable(self):
        """Тест получения переменной окружения"""
        loader = EnvLoader()
        
        with patch.dict(os.environ, {"TEST_KEY": "test_value"}):
            result = loader.get_env_var("TEST_KEY")
            assert result == "test_value"
        
        result = loader.get_env_var("NONEXISTENT_KEY", "default")
        assert result == "default"

    @patch('builtins.open', new_callable=mock_open, read_data='API_KEY=secret123\nDEBUG=true\n')
    @patch('os.path.exists', return_value=True)
    def test_load_env_file_function(self, mock_exists, mock_file):
        """Тест функции load_env_file"""
        with patch.dict(os.environ, {}, clear=True):
            result = load_env_file(".env")
            
            assert result is True
            assert os.environ.get("API_KEY") == "secret123"
            assert os.environ.get("DEBUG") == "true"
