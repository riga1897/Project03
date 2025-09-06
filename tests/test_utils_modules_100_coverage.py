"""
Тесты для модулей утилит с 100% покрытием
Покрывает: env_loader, decorators, salary, search_utils, file_handlers
"""

import os
import sys
import tempfile
import time
from unittest.mock import Mock, patch, mock_open

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.env_loader import EnvLoader
from src.utils.decorators import simple_cache, retry_on_failure
from src.utils.salary import SalaryUtils
from src.utils.search_utils import SearchUtils
from src.utils.file_handlers import FileHandler


class TestEnvLoader:
    """Тесты для EnvLoader"""

    def setup_method(self):
        """Сброс состояния перед каждым тестом"""
        EnvLoader._loaded = False

    def test_load_env_file_not_found(self):
        """Тест загрузки несуществующего .env файла"""
        with patch('os.path.exists', return_value=False):
            EnvLoader.load_env_file("nonexistent.env")
            assert EnvLoader._loaded == True

    def test_load_env_file_already_loaded(self):
        """Тест повторной загрузки когда уже загружено"""
        EnvLoader._loaded = True
        
        with patch('builtins.open', mock_open()) as mock_file:
            EnvLoader.load_env_file(".env")
            mock_file.assert_not_called()

    def test_load_env_file_success(self):
        """Тест успешной загрузки .env файла"""
        env_content = """
# Комментарий
KEY1=value1
KEY2="value2"
KEY3='value3'
KEY4=value4=with=equals

EMPTY_LINE=

# Еще комментарий
KEY5=value5
        """.strip()
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {}, clear=True):
                    EnvLoader.load_env_file(".env")
                    
                    assert os.environ["KEY1"] == "value1"
                    assert os.environ["KEY2"] == "value2"
                    assert os.environ["KEY3"] == "value3"
                    assert os.environ["KEY4"] == "value4=with=equals"
                    assert os.environ["KEY5"] == "value5"

    def test_load_env_file_existing_env_var(self):
        """Тест что существующие переменные не перезаписываются"""
        env_content = "EXISTING_VAR=new_value"
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {"EXISTING_VAR": "old_value"}):
                    EnvLoader.load_env_file(".env")
                    
                    assert os.environ["EXISTING_VAR"] == "old_value"

    def test_load_env_file_invalid_format(self):
        """Тест обработки невалидных строк"""
        env_content = """
VALID_KEY=valid_value
invalid_line_without_equals
ANOTHER_VALID=another_value
        """.strip()
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {}, clear=True):
                    EnvLoader.load_env_file(".env")
                    
                    assert "VALID_KEY" in os.environ
                    assert "ANOTHER_VALID" in os.environ

    def test_load_env_file_exception(self):
        """Тест обработки исключения при чтении файла"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("File error")):
                EnvLoader.load_env_file(".env")
                # Не должно падать

    def test_get_env_var_str_existing(self):
        """Тест получения существующей строковой переменной"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = EnvLoader.get_env_var_str("TEST_VAR", "default")
            assert result == "test_value"

    def test_get_env_var_str_default(self):
        """Тест получения дефолтного значения строковой переменной"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_env_var_str("MISSING_VAR", "default_value")
            assert result == "default_value"

    def test_get_env_var_int_existing(self):
        """Тест получения существующей числовой переменной"""
        with patch.dict(os.environ, {"INT_VAR": "42"}):
            result = EnvLoader.get_env_var_int("INT_VAR", 0)
            assert result == 42

    def test_get_env_var_int_invalid(self):
        """Тест получения невалидной числовой переменной"""
        with patch.dict(os.environ, {"INT_VAR": "not_a_number"}):
            result = EnvLoader.get_env_var_int("INT_VAR", 100)
            assert result == 100

    def test_get_env_var_int_default(self):
        """Тест получения дефолтного значения числовой переменной"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_env_var_int("MISSING_INT", 999)
            assert result == 999

    def test_get_env_var_bool_true_values(self):
        """Тест получения булевых значений true"""
        true_values = ["true", "True", "TRUE", "1", "yes", "Yes", "YES"]
        
        for value in true_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                result = EnvLoader.get_env_var_bool("BOOL_VAR", False)
                assert result == True

    def test_get_env_var_bool_false_values(self):
        """Тест получения булевых значений false"""
        false_values = ["false", "False", "FALSE", "0", "no", "No", "NO"]
        
        for value in false_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                result = EnvLoader.get_env_var_bool("BOOL_VAR", True)
                assert result == False

    def test_get_env_var_bool_default(self):
        """Тест получения дефолтного булевого значения"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_env_var_bool("MISSING_BOOL", True)
            assert result == True


class TestDecorators:
    """Тесты для декораторов"""

    def test_simple_cache_basic(self):
        """Тест базового кэширования"""
        call_count = 0
        
        @simple_cache(ttl=60)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Первый вызов
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1
        
        # Второй вызов - должен использовать кэш
        result2 = test_func(5)
        assert result2 == 10
        assert call_count == 1

    def test_simple_cache_different_args(self):
        """Тест кэширования с разными аргументами"""
        call_count = 0
        
        @simple_cache(ttl=60)
        def test_func(x, y=1):
            nonlocal call_count
            call_count += 1
            return x + y
        
        result1 = test_func(1, 2)
        result2 = test_func(1, y=2)  # Другой способ передачи
        result3 = test_func(2, 2)    # Разные аргументы
        
        assert result1 == 3
        assert result2 == 3
        assert result3 == 4
        assert call_count == 2  # Только 2 уникальных вызова

    def test_simple_cache_ttl_expired(self):
        """Тест истечения TTL кэша"""
        call_count = 0
        
        @simple_cache(ttl=0.1)  # 0.1 секунды
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x
        
        # Первый вызов
        test_func(1)
        assert call_count == 1
        
        # Ждем истечения TTL
        time.sleep(0.2)
        
        # Второй вызов после истечения
        test_func(1)
        assert call_count == 2

    def test_simple_cache_max_size(self):
        """Тест ограничения размера кэша"""
        @simple_cache(max_size=2)
        def test_func(x):
            return x
        
        # Заполняем кэш до лимита
        test_func(1)
        test_func(2)
        test_func(3)  # Должен вытеснить самый старый элемент
        
        cache_info = test_func.cache_info()
        assert cache_info["size"] <= 2

    def test_simple_cache_clear_cache(self):
        """Тест очистки кэша"""
        call_count = 0
        
        @simple_cache(ttl=60)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x
        
        test_func(1)
        assert call_count == 1
        
        test_func.clear_cache()
        
        test_func(1)  # После очистки должен вызвать функцию снова
        assert call_count == 2

    def test_simple_cache_info(self):
        """Тест получения информации о кэше"""
        @simple_cache(max_size=100, ttl=300)
        def test_func(x):
            return x
        
        test_func(1)
        info = test_func.cache_info()
        
        assert info["max_size"] == 100
        assert info["ttl"] == 300
        assert info["size"] == 1

    def test_retry_on_failure_success(self):
        """Тест успешного выполнения без ретраев"""
        call_count = 0
        
        @retry_on_failure(max_attempts=3)
        def test_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = test_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_on_failure_with_retries(self):
        """Тест выполнения с ретраями"""
        call_count = 0
        
        @retry_on_failure(max_attempts=3, delay=0.01)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Error")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert call_count == 3

    def test_retry_on_failure_max_attempts_exceeded(self):
        """Тест превышения максимальных попыток"""
        @retry_on_failure(max_attempts=2, delay=0.01)
        def test_func():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            test_func()


class TestSalaryUtils:
    """Тесты для SalaryUtils"""

    def test_format_salary_range(self):
        """Тест форматирования диапазона зарплат"""
        result = SalaryUtils.format_salary(100000, 150000, "RUR")
        assert "100 000" in result
        assert "150 000" in result

    def test_format_salary_from_only(self):
        """Тест форматирования зарплаты только от"""
        result = SalaryUtils.format_salary(100000, None, "RUR")
        assert "от 100 000" in result

    def test_format_salary_to_only(self):
        """Тест форматирования зарплаты только до"""
        result = SalaryUtils.format_salary(None, 150000, "RUR")
        assert "до 150 000" in result

    def test_format_salary_none(self):
        """Тест форматирования при отсутствии зарплаты"""
        result = SalaryUtils.format_salary(None, None, "RUR")
        assert result == "Не указана"

    def test_format_number_with_spaces(self):
        """Тест форматирования числа с пробелами"""
        assert SalaryUtils._format_number_with_spaces(1000) == "1 000"
        assert SalaryUtils._format_number_with_spaces(1000000) == "1 000 000"
        assert SalaryUtils._format_number_with_spaces(123) == "123"

    def test_parse_salary_valid(self):
        """Тест парсинга валидной зарплаты"""
        result = SalaryUtils.parse_salary("100000-150000")
        assert result == (100000, 150000)

    def test_parse_salary_from_only(self):
        """Тест парсинга зарплаты от"""
        result = SalaryUtils.parse_salary("от 100000")
        assert result == (100000, None)

    def test_parse_salary_to_only(self):
        """Тест парсинга зарплаты до"""
        result = SalaryUtils.parse_salary("до 150000")
        assert result == (None, 150000)

    def test_parse_salary_invalid(self):
        """Тест парсинга невалидной зарплаты"""
        result = SalaryUtils.parse_salary("abc")
        assert result == (None, None)

    def test_compare_salary_higher(self):
        """Тест сравнения зарплат - выше"""
        result = SalaryUtils.compare_salary(120000, 150000, 100000, 130000)
        assert result > 0

    def test_compare_salary_lower(self):
        """Тест сравнения зарплат - ниже"""
        result = SalaryUtils.compare_salary(80000, 100000, 120000, 150000)
        assert result < 0

    def test_compare_salary_equal(self):
        """Тест сравнения одинаковых зарплат"""
        result = SalaryUtils.compare_salary(100000, 150000, 100000, 150000)
        assert result == 0


class TestSearchUtils:
    """Тесты для SearchUtils"""

    def test_normalize_query_basic(self):
        """Тест базовой нормализации запроса"""
        result = SearchUtils.normalize_query("  Python Developer  ")
        assert result == "python developer"

    def test_normalize_query_special_chars(self):
        """Тест нормализации с спецсимволами"""
        result = SearchUtils.normalize_query("C++ / C# Developer!!!")
        assert result == "c++ / c# developer"

    def test_extract_keywords_basic(self):
        """Тест извлечения ключевых слов"""
        result = SearchUtils.extract_keywords("Python Django Web Developer")
        assert "python" in result
        assert "django" in result
        assert "web" in result
        assert "developer" in result

    def test_extract_keywords_stop_words(self):
        """Тест исключения стоп-слов"""
        result = SearchUtils.extract_keywords("Python и Django разработчик")
        assert "python" in result
        assert "django" in result
        assert "и" not in result

    def test_build_search_query_simple(self):
        """Тест построения простого поискового запроса"""
        result = SearchUtils.build_search_query(["python", "developer"])
        assert "python" in result and "developer" in result

    def test_build_search_query_with_operators(self):
        """Тест построения запроса с операторами"""
        result = SearchUtils.build_search_query(
            ["python", "django"],
            operator="AND"
        )
        assert "python" in result and "django" in result

    def test_match_query_in_text_found(self):
        """Тест поиска запроса в тексте (найден)"""
        text = "Требуется Python разработчик со знанием Django"
        result = SearchUtils.match_query_in_text("python django", text)
        assert result == True

    def test_match_query_in_text_not_found(self):
        """Тест поиска запроса в тексте (не найден)"""
        text = "Требуется Java разработчик"
        result = SearchUtils.match_query_in_text("python django", text)
        assert result == False

    def test_highlight_matches(self):
        """Тест выделения совпадений в тексте"""
        text = "Python разработчик со знанием Django"
        result = SearchUtils.highlight_matches(text, "python django")
        assert "<mark>" in result or result != text


class TestFileHandler:
    """Тесты для FileHandler"""

    def test_read_file_success(self):
        """Тест успешного чтения файла"""
        content = "test content"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = FileHandler.read_file("test.txt")
            assert result == content

    def test_read_file_not_found(self):
        """Тест чтения несуществующего файла"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = FileHandler.read_file("missing.txt")
            assert result is None

    def test_write_file_success(self):
        """Тест успешной записи файла"""
        with patch('builtins.open', mock_open()) as mock_file:
            result = FileHandler.write_file("test.txt", "test content")
            assert result == True
            mock_file().write.assert_called_once_with("test content")

    def test_write_file_error(self):
        """Тест ошибки записи файла"""
        with patch('builtins.open', side_effect=IOError):
            result = FileHandler.write_file("test.txt", "content")
            assert result == False

    def test_file_exists_true(self):
        """Тест проверки существования файла (существует)"""
        with patch('os.path.exists', return_value=True):
            result = FileHandler.file_exists("existing.txt")
            assert result == True

    def test_file_exists_false(self):
        """Тест проверки существования файла (не существует)"""
        with patch('os.path.exists', return_value=False):
            result = FileHandler.file_exists("missing.txt")
            assert result == False

    def test_create_directory_success(self):
        """Тест успешного создания директории"""
        with patch('os.makedirs') as mock_makedirs:
            result = FileHandler.create_directory("test_dir")
            assert result == True
            mock_makedirs.assert_called_once()

    def test_create_directory_exists(self):
        """Тест создания уже существующей директории"""
        with patch('os.makedirs', side_effect=OSError):
            result = FileHandler.create_directory("existing_dir")
            assert result == False

    def test_get_file_size_success(self):
        """Тест получения размера файла"""
        with patch('os.path.getsize', return_value=1024):
            result = FileHandler.get_file_size("test.txt")
            assert result == 1024

    def test_get_file_size_error(self):
        """Тест ошибки получения размера файла"""
        with patch('os.path.getsize', side_effect=OSError):
            result = FileHandler.get_file_size("missing.txt")
            assert result == 0