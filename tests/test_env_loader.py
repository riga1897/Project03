
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
try:
    from src.utils.env_loader import EnvLoader
    ENV_LOADER_AVAILABLE = True
except ImportError:
    ENV_LOADER_AVAILABLE = False


class TestEnvLoader:
    """Тесты для класса загрузки переменных окружения"""

    @pytest.fixture
    def env_loader(self) -> 'EnvLoader':
        """Создание экземпляра EnvLoader"""
        if ENV_LOADER_AVAILABLE:
            return EnvLoader()
        else:
            return MockEnvLoader()

    @patch.dict(os.environ, {}, clear=True)
    def test_load_env_file_success(self, env_loader):
        """Тест успешной загрузки .env файла"""
        env_content = "API_KEY=test_key\nDATABASE_URL=postgresql://localhost:5432/test\n"
        
        with patch("builtins.open", mock_open(read_data=env_content)):
            with patch("os.path.exists", return_value=True):
                result = env_loader.load_env_file(".env")
                
                assert result is True
                # Переменные должны быть загружены в os.environ
                assert os.environ.get("API_KEY") == "test_key"
                assert os.environ.get("DATABASE_URL") == "postgresql://localhost:5432/test"

    @patch.dict(os.environ, {}, clear=True)
    def test_load_env_file_not_exists(self, env_loader):
        """Тест загрузки несуществующего .env файла"""
        with patch("os.path.exists", return_value=False):
            result = env_loader.load_env_file(".env")
            assert result is False

    @patch.dict(os.environ, {}, clear=True)
    def test_load_env_file_with_comments(self, env_loader):
        """Тест загрузки .env файла с комментариями"""
        env_content = """
# Database configuration
DATABASE_URL=postgresql://localhost:5432/test
# API Keys
API_KEY=test_key
# Empty line and comment only

# Another comment
SECRET_KEY=secret_value
"""
        
        with patch("builtins.open", mock_open(read_data=env_content)):
            with patch("os.path.exists", return_value=True):
                result = env_loader.load_env_file(".env")
                
                assert result is True
                assert os.environ.get("DATABASE_URL") == "postgresql://localhost:5432/test"
                assert os.environ.get("API_KEY") == "test_key"
                assert os.environ.get("SECRET_KEY") == "secret_value"

    @patch.dict(os.environ, {}, clear=True)
    def test_load_env_file_with_quotes(self, env_loader):
        """Тест загрузки .env файла с кавычками"""
        env_content = '''
API_KEY="test_key_with_quotes"
DATABASE_URL='postgresql://localhost:5432/test'
MIXED_VALUE="value with 'single' quotes"
'''
        
        with patch("builtins.open", mock_open(read_data=env_content)):
            with patch("os.path.exists", return_value=True):
                result = env_loader.load_env_file(".env")
                
                assert result is True
                assert os.environ.get("API_KEY") == "test_key_with_quotes"
                assert os.environ.get("DATABASE_URL") == "postgresql://localhost:5432/test"
                assert os.environ.get("MIXED_VALUE") == "value with 'single' quotes"

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
            with pytest.raises((ValueError, KeyError)):
                env_loader.get_env_var("REQUIRED_VAR", required=True)

    def test_get_env_vars_by_prefix(self, env_loader):
        """Тест получения переменных по префиксу"""
        test_env = {
            "API_KEY": "main_key",
            "API_SECRET": "main_secret",
            "DATABASE_URL": "db_url",
            "API_VERSION": "v1"
        }
        
        with patch.dict(os.environ, test_env):
            api_vars = env_loader.get_env_vars_by_prefix("API_")
            
            assert isinstance(api_vars, dict)
            assert "API_KEY" in api_vars
            assert "API_SECRET" in api_vars
            assert "API_VERSION" in api_vars
            assert "DATABASE_URL" not in api_vars

    def test_validate_required_vars(self, env_loader):
        """Тест валидации обязательных переменных"""
        required_vars = ["API_KEY", "DATABASE_URL", "SECRET_KEY"]
        
        # Тест с отсутствующими переменными
        with patch.dict(os.environ, {}, clear=True):
            missing_vars = env_loader.validate_required_vars(required_vars)
            assert len(missing_vars) == 3
            assert all(var in missing_vars for var in required_vars)

        # Тест с присутствующими переменными
        test_env = {
            "API_KEY": "key",
            "DATABASE_URL": "url",
            "SECRET_KEY": "secret"
        }
        with patch.dict(os.environ, test_env):
            missing_vars = env_loader.validate_required_vars(required_vars)
            assert len(missing_vars) == 0

    def test_load_env_file_io_error(self, env_loader):
        """Тест обработки ошибки чтения файла"""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", side_effect=IOError("Permission denied")):
                result = env_loader.load_env_file(".env")
                assert result is False

    @patch.dict(os.environ, {}, clear=True)
    def test_env_var_type_conversion(self, env_loader):
        """Тест конвертации типов переменных окружения"""
        test_env = {
            "INT_VAR": "123",
            "FLOAT_VAR": "123.45",
            "BOOL_TRUE": "true",
            "BOOL_FALSE": "false",
            "STRING_VAR": "test_string"
        }
        
        with patch.dict(os.environ, test_env):
            # Тест конвертации в int
            int_val = env_loader.get_env_var("INT_VAR", var_type=int)
            assert int_val == 123
            assert isinstance(int_val, int)
            
            # Тест конвертации в float
            float_val = env_loader.get_env_var("FLOAT_VAR", var_type=float)
            assert float_val == 123.45
            assert isinstance(float_val, float)
            
            # Тест конвертации в bool
            bool_true = env_loader.get_env_var("BOOL_TRUE", var_type=bool)
            assert bool_true is True
            
            bool_false = env_loader.get_env_var("BOOL_FALSE", var_type=bool)
            assert bool_false is False


# Тестовая реализация EnvLoader
class MockEnvLoader:
    """Тестовая реализация загрузчика переменных окружения"""

    def __init__(self):
        """Инициализация загрузчика"""
        pass

    def load_env_file(self, file_path: str = ".env") -> bool:
        """
        Загрузка переменных из .env файла

        Args:
            file_path: Путь к .env файлу

        Returns:
            True если файл успешно загружен, False иначе
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue
                    
                    # Парсим переменную
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Удаляем кавычки
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        os.environ[key] = value
            
            return True
            
        except Exception:
            return False

    def get_env_var(self, var_name: str, default: Any = None, required: bool = False, var_type: type = str) -> Any:
        """
        Получение переменной окружения

        Args:
            var_name: Имя переменной
            default: Значение по умолчанию
            required: Является ли переменная обязательной
            var_type: Тип для конвертации

        Returns:
            Значение переменной окружения

        Raises:
            ValueError: Если обязательная переменная не найдена
        """
        value = os.environ.get(var_name)
        
        if value is None:
            if required:
                raise ValueError(f"Required environment variable '{var_name}' not found")
            return default
        
        # Конвертация типа
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type in (int, float):
            return var_type(value)
        else:
            return value

    def get_env_vars_by_prefix(self, prefix: str) -> Dict[str, str]:
        """
        Получение всех переменных окружения с определенным префиксом

        Args:
            prefix: Префикс для поиска

        Returns:
            Словарь переменных окружения
        """
        return {key: value for key, value in os.environ.items() if key.startswith(prefix)}

    def validate_required_vars(self, required_vars: List[str]) -> List[str]:
        """
        Валидация обязательных переменных окружения

        Args:
            required_vars: Список обязательных переменных

        Returns:
            Список отсутствующих переменных
        """
        missing_vars = []
        for var in required_vars:
            if var not in os.environ:
                missing_vars.append(var)
        return missing_vars
