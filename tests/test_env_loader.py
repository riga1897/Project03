
"""
Тесты для модуля env_loader
"""

import pytest
import os
from unittest.mock import patch, mock_open
from src.utils.env_loader import EnvLoader


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
