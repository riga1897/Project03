"""
Тесты для модуля загрузки переменных окружения
"""

import os
import sys
from typing import Dict, Any, List
from unittest.mock import MagicMock, Mock, patch, mock_open
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт из реального кода
from src.utils.env_loader import EnvLoader


class TestEnvLoader:
    """Тесты для класса загрузки переменных окружения"""

    @pytest.fixture
    def env_loader(self) -> EnvLoader:
        """Создание экземпляра EnvLoader"""
        return EnvLoader()

    @patch.dict(os.environ, {}, clear=True)
    def test_load_env_file_success(self, env_loader):
        """Тест успешной загрузки .env файла"""
        env_content = "API_KEY=test_key\nDATABASE_URL=postgresql://localhost:5432/test\n"

        with patch("builtins.open", mock_open(read_data=env_content)):
            with patch("os.path.exists", return_value=True):
                # Реальный метод называется load_env_file
                result = env_loader.load_env_file(".env")
                # Проверяем что метод отработал
                assert result is True or result is None

                # Проверяем что переменные загружены
                assert env_loader.get_env_var("API_KEY") == "test_key"
                assert env_loader.get_env_var("DATABASE_URL") == "postgresql://localhost:5432/test"

    @patch.dict(os.environ, {}, clear=True)
    def test_load_env_file_not_exists(self, env_loader):
        """Тест загрузки несуществующего .env файла"""
        with patch("os.path.exists", return_value=False):
            result = env_loader.load_env_file(".env")
            assert result is False or result is None

    def test_get_env_var_existing(self, env_loader):
        """Тест получения существующей переменной окружения"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            value = env_loader.get_env_var("TEST_VAR")
            assert value == "test_value"

    def test_get_env_var_with_default(self, env_loader):
        """Тест получения переменной окружения с значением по умолчанию"""
        with patch.dict(os.environ, {}, clear=True):
            value = env_loader.get_env_var("NONEXISTENT_VAR", "default_value")
            assert value == "default_value"

    def test_get_env_var_required(self, env_loader):
        """Тест получения обязательной переменной окружения"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                env_loader.get_env_var("REQUIRED_VAR", required=True)

    def test_get_env_var_type_conversion(self, env_loader):
        """Тест конвертации типов переменных окружения"""
        test_env = {
            "BOOL_TRUE": "true",
            "BOOL_FALSE": "false",
            "INT_VAR": "123",
            "FLOAT_VAR": "123.45"
        }

        with patch.dict(os.environ, test_env):
            # Тест boolean конвертации
            assert env_loader.get_env_var("BOOL_TRUE", var_type=bool) is True
            assert env_loader.get_env_var("BOOL_FALSE", var_type=bool) is False

            # Тест int конвертации
            assert env_loader.get_env_var("INT_VAR", var_type=int) == 123

            # Тест float конвертации
            assert env_loader.get_env_var("FLOAT_VAR", var_type=float) == 123.45

    def test_get_env_vars_by_prefix(self, env_loader):
        """Тест получения переменных по префиксу"""
        test_env = {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "test",
            "API_KEY": "key123"
        }

        with patch.dict(os.environ, test_env):
            db_vars = env_loader.get_env_vars_by_prefix("DB_")
            assert len(db_vars) == 3
            assert "DB_HOST" in db_vars
            assert "DB_PORT" in db_vars
            assert "DB_NAME" in db_vars
            assert "API_KEY" not in db_vars

    def test_validate_required_vars(self, env_loader):
        """Тест валидации обязательных переменных"""
        required_vars = ["API_KEY", "DATABASE_URL"]

        # Тест с отсутствующими переменными
        with patch.dict(os.environ, {}, clear=True):
            missing_vars = env_loader.validate_required_vars(required_vars)
            assert len(missing_vars) == 2
            assert "API_KEY" in missing_vars
            assert "DATABASE_URL" in missing_vars

        # Тест с присутствующими переменными
        test_env = {
            "API_KEY": "key",
            "DATABASE_URL": "url"
        }
        with patch.dict(os.environ, test_env):
            missing_vars = env_loader.validate_required_vars(required_vars)
            assert len(missing_vars) == 0

    def test_env_loader_initialization(self, env_loader):
        """Тест инициализации EnvLoader"""
        assert env_loader is not None
        assert hasattr(env_loader, 'get_env_var')
        assert hasattr(env_loader, 'load_env_file')
        assert hasattr(env_loader, 'get_env_vars_by_prefix')
        assert hasattr(env_loader, 'validate_required_vars')

    def test_env_file_parsing_edge_cases(self, env_loader):
        """Тест граничных случаев парсинга .env файла"""
        # Файл с комментариями и пустыми строками
        env_content = """
# Это комментарий
API_KEY=test_key

# Еще комментарий
DATABASE_URL="postgresql://localhost:5432/test"
DEBUG=true

EMPTY_VAR=
"""

        with patch("builtins.open", mock_open(read_data=env_content)):
            with patch("os.path.exists", return_value=True):
                env_loader.load_env_file(".env")

                # Проверяем что переменные корректно загружены
                assert env_loader.get_env_var("API_KEY") == "test_key"
                assert env_loader.get_env_var("DATABASE_URL") == "postgresql://localhost:5432/test"
                assert env_loader.get_env_var("DEBUG") == "true"
                assert env_loader.get_env_var("EMPTY_VAR") == ""

    def test_env_file_with_quotes(self, env_loader):
        """Тест обработки кавычек в .env файле"""
        env_content = '''
QUOTED_VAR="value with spaces"
SINGLE_QUOTED='single quoted value'
UNQUOTED_VAR=simple_value
'''

        with patch("builtins.open", mock_open(read_data=env_content)):
            with patch("os.path.exists", return_value=True):
                env_loader.load_env_file(".env")

                assert env_loader.get_env_var("QUOTED_VAR") == "value with spaces"
                assert env_loader.get_env_var("SINGLE_QUOTED") == "single quoted value"
                assert env_loader.get_env_var("UNQUOTED_VAR") == "simple_value"

    def test_load_multiple_env_files(self, env_loader):
        """Тест загрузки нескольких .env файлов"""
        env_content1 = "VAR1=value1\nVAR2=value2\n"
        env_content2 = "VAR2=new_value2\nVAR3=value3\n"

        with patch("builtins.open", mock_open(read_data=env_content1)):
            with patch("os.path.exists", return_value=True):
                env_loader.load_env_file(".env")

        with patch("builtins.open", mock_open(read_data=env_content2)):
            with patch("os.path.exists", return_value=True):
                env_loader.load_env_file(".env.local")

        # VAR2 должна быть перезаписана
        assert env_loader.get_env_var("VAR1") == "value1"
        assert env_loader.get_env_var("VAR2") == "new_value2"
        assert env_loader.get_env_var("VAR3") == "value3"

    def test_env_file_error_handling(self, env_loader):
        """Тест обработки ошибок при работе с .env файлом"""
        # Тест ошибки чтения файла
        with patch("builtins.open", side_effect=IOError("File read error")):
            with patch("os.path.exists", return_value=True):
                result = env_loader.load_env_file(".env")
                assert result is False or result is None

    def test_empty_prefix_search(self, env_loader):
        """Тест поиска переменных с пустым префиксом"""
        test_env = {"VAR1": "value1", "VAR2": "value2"}

        with patch.dict(os.environ, test_env):
            # Пустой префикс должен возвращать все переменные
            all_vars = env_loader.get_env_vars_by_prefix("")
            assert len(all_vars) >= 2  # Может быть больше системных переменных
            assert "VAR1" in all_vars
            assert "VAR2" in all_vars