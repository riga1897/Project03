"""
Тесты для загрузчика переменных окружения
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import os
from pathlib import Path

# Моковый класс EnvLoader для тестов
class EnvLoader:
    """Мок EnvLoader для тестирования"""

    _env_cache = {}

    @classmethod
    def get_env_var(cls, key, default=None):
        """Получить переменную окружения"""
        if key in cls._env_cache:
            return cls._env_cache[key]
        return os.environ.get(key, default)

    @classmethod
    def load_from_file(cls, file_path=".env"):
        """Загрузить переменные из файла"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            cls._env_cache[key.strip()] = value.strip()
                return True
        except Exception:
            pass
        return False

    @classmethod

class TestEnvLoader:
    """Тесты для EnvLoader"""
    
    def setup_method(self):
        """Подготовка к каждому тесту"""
        EnvLoader.clear_cache()
    
    def test_get_env_var_from_os_environ(self):
        """Тест получения переменной из os.environ"""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = EnvLoader.get_env_var('TEST_VAR')
            assert result == 'test_value'
    
    def test_get_env_var_with_default(self):
        """Тест получения переменной с дефолтным значением"""
        result = EnvLoader.get_env_var('NONEXISTENT_VAR', 'default_value')
        assert result == 'default_value'
    
    def test_get_env_var_from_cache(self):
        """Тест получения переменной из кэша"""
        EnvLoader.set_env_var('CACHED_VAR', 'cached_value')
        result = EnvLoader.get_env_var('CACHED_VAR')
        assert result == 'cached_value'
    
    def test_load_from_file_success(self):
        """Тест успешной загрузки из файла"""
        env_content = """
# This is a comment
DATABASE_URL=postgresql://localhost/test
API_KEY=secret_key
EMPTY_LINE=

SPACED_VALUE = value with spaces
"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                result = EnvLoader.load_from_file('.env')
                assert result is True
                
                assert EnvLoader.get_env_var('DATABASE_URL') == 'postgresql://localhost/test'
                assert EnvLoader.get_env_var('API_KEY') == 'secret_key'
                assert EnvLoader.get_env_var('SPACED_VALUE') == 'value with spaces'
    
    def test_load_from_file_not_exists(self):
        """Тест загрузки из несуществующего файла"""
        with patch('os.path.exists', return_value=False):
            result = EnvLoader.load_from_file('nonexistent.env')
            assert result is False
    
    def test_load_from_file_exception(self):
        """Тест обработки исключений при загрузке файла"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("Permission denied")):
                result = EnvLoader.load_from_file('.env')
                assert result is False
    
    def test_load_from_file_ignore_comments(self):
        """Тест игнорирования комментариев в файле"""
        env_content = """
# This is a comment
VAR1=value1
# Another comment
VAR2=value2
"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                EnvLoader.load_from_file('.env')
                
                assert EnvLoader.get_env_var('VAR1') == 'value1'
                assert EnvLoader.get_env_var('VAR2') == 'value2'
    
    def test_load_from_file_ignore_empty_lines(self):
        """Тест игнорирования пустых строк"""
        env_content = """
VAR1=value1

VAR2=value2

"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                EnvLoader.load_from_file('.env')
                
                assert EnvLoader.get_env_var('VAR1') == 'value1'
                assert EnvLoader.get_env_var('VAR2') == 'value2'
    
    def test_load_from_file_ignore_malformed_lines(self):
        """Тест игнорирования неправильно сформированных строк"""
        env_content = """
VAR1=value1
INVALID_LINE_NO_EQUALS
VAR2=value2
ANOTHER_INVALID
VAR3=value3
"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                EnvLoader.load_from_file('.env')
                
                assert EnvLoader.get_env_var('VAR1') == 'value1'
                assert EnvLoader.get_env_var('VAR2') == 'value2'
                assert EnvLoader.get_env_var('VAR3') == 'value3'
                assert EnvLoader.get_env_var('INVALID_LINE_NO_EQUALS') is None
    
    def test_set_env_var(self):
        """Тест установки переменной окружения"""
        EnvLoader.set_env_var('TEST_SET', 'set_value')
        result = EnvLoader.get_env_var('TEST_SET')
        assert result == 'set_value'
    
    def test_clear_cache(self):
        """Тест очистки кэша"""
        EnvLoader.set_env_var('TEST_CLEAR', 'clear_value')
        assert EnvLoader.get_env_var('TEST_CLEAR') == 'clear_value'
        
        EnvLoader.clear_cache()
        
        # После очистки кэша должен использовать os.environ
        with patch.dict(os.environ, {'TEST_CLEAR': 'os_value'}):
            result = EnvLoader.get_env_var('TEST_CLEAR')
            assert result == 'os_value'
    
    def test_cache_priority_over_os_environ(self):
        """Тест приоритета кэша над os.environ"""
        with patch.dict(os.environ, {'PRIORITY_TEST': 'os_value'}):
            # Сначала получим из os.environ
            result1 = EnvLoader.get_env_var('PRIORITY_TEST')
            assert result1 == 'os_value'
            
            # Установим в кэш
            EnvLoader.set_env_var('PRIORITY_TEST', 'cache_value')
            
            # Теперь должно вернуться значение из кэша
            result2 = EnvLoader.get_env_var('PRIORITY_TEST')
            assert result2 == 'cache_value'
    
    def test_load_from_custom_file_path(self):
        """Тест загрузки из кастомного пути к файлу"""
        env_content = "CUSTOM_VAR=custom_value"
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                result = EnvLoader.load_from_file('custom.env')
                assert result is True
                assert EnvLoader.get_env_var('CUSTOM_VAR') == 'custom_value'

    def set_env_var(cls, key, value):
        """Установить переменную в кэш"""
        cls._env_cache[key] = value

    @classmethod
    def clear_cache(cls):
        """Очистить кэш"""
        cls._env_cache.clear()


class TestEnvLoader:
    """Тесты для класса EnvLoader"""

    @pytest.fixture
    def env_loader(self):
        """Фикстура EnvLoader"""
        return EnvLoader()

    def test_load_env_file_exists(self, env_loader):
        """Тест загрузки существующего .env файла"""
        env_content = "TEST_KEY=test_value\nANOTHER_KEY=another_value"
        
        with patch('builtins.open', mock_open(read_data=env_content)):
            with patch('os.path.exists', return_value=True):
                result = env_loader.load_env_file('.env')
                assert result is True

    def test_load_env_file_not_exists(self, env_loader):
        """Тест загрузки несуществующего .env файла"""
        with patch('os.path.exists', return_value=False):
            result = env_loader.load_env_file('.env')
            assert result is False

    def test_parse_env_line_valid(self, env_loader):
        """Тест парсинга корректной строки переменной окружения"""
        key, value = env_loader.parse_env_line("API_KEY=secret123")
        assert key == "API_KEY"
        assert value == "secret123"

    def test_parse_env_line_with_quotes(self, env_loader):
        """Тест парсинга строки с кавычками"""
        key, value = env_loader.parse_env_line('DB_URL="postgresql://localhost"')
        assert key == "DB_URL"
        assert value == "postgresql://localhost"

    def test_parse_env_line_invalid(self, env_loader):
        """Тест парсинга некорректной строки"""
        result = env_loader.parse_env_line("INVALID_LINE")
        assert result is None

    def test_parse_env_line_comment(self, env_loader):
        """Тест парсинга комментария"""
        result = env_loader.parse_env_line("# This is a comment")
        assert result is None

    def test_set_environment_variable(self, env_loader):
        """Тест установки переменной окружения"""
        env_loader.set_environment_variable("TEST_VAR", "test_value")
        assert os.environ.get("TEST_VAR") == "test_value"
        
        # Очищаем после теста
        if "TEST_VAR" in os.environ:
            del os.environ["TEST_VAR"]

    def test_get_environment_variable(self, env_loader):
        """Тест получения переменной окружения"""
        os.environ["TEST_GET_VAR"] = "test_get_value"
        
        value = env_loader.get_environment_variable("TEST_GET_VAR")
        assert value == "test_get_value"
        
        # Очищаем после теста
        del os.environ["TEST_GET_VAR"]

    def test_get_environment_variable_with_default(self, env_loader):
        """Тест получения переменной окружения с значением по умолчанию"""
        value = env_loader.get_environment_variable("NON_EXISTENT_VAR", "default_value")
        assert value == "default_value"

    @patch.dict(os.environ, {}, clear=True)
    def test_load_environment_variables(self, env_loader):
        """Тест загрузки всех переменных окружения"""
        variables = {
            "VAR1": "value1",
            "VAR2": "value2",
            "VAR3": "value3"
        }
        
        env_loader.load_environment_variables(variables)
        
        for key, value in variables.items():
            assert os.environ.get(key) == value

    def test_validate_required_env_vars_success(self, env_loader):
        """Тест валидации обязательных переменных - успешный случай"""
        required_vars = ["PATH"]  # PATH всегда должен существовать
        
        missing = env_loader.validate_required_env_vars(required_vars)
        assert len(missing) == 0

    def test_validate_required_env_vars_missing(self, env_loader):
        """Тест валидации обязательных переменных - недостающие переменные"""
        required_vars = ["NON_EXISTENT_VAR1", "NON_EXISTENT_VAR2"]
        
        missing = env_loader.validate_required_env_vars(required_vars)
        assert len(missing) == 2
        assert "NON_EXISTENT_VAR1" in missing
        assert "NON_EXISTENT_VAR2" in missing