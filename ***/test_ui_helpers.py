"""
Тесты для UI помощников
"""

from unittest.mock import MagicMock, patch

import pytest

# Импортируем функции напрямую из ui_helpers
from src.utils.ui_helpers import confirm_action, get_positive_integer, get_user_input, parse_salary_range


class TestUIHelpers:
    """Тесты для UI помощников с консолидированными моками"""

    @pytest.fixture(autouse=True)
    def setup_consolidated_mocks(self):
        """Консолидированная настройка всех моков"""
        with patch("builtins.input") as mock_input, patch("builtins.print") as mock_print:

            self.mock_input = mock_input
            self.mock_print = mock_print
            yield

    def test_confirm_action_yes(self):
        """Тест подтверждения действия - да"""
        self.mock_input.return_value = "y"
        result = confirm_action("Продолжить?")
        assert result is True

    def test_confirm_action_no(self):
        """Тест подтверждения действия - нет"""
        self.mock_input.return_value = "n"
        result = confirm_action("Продолжить?")
        assert result is False

    def test_confirm_action_case_insensitive(self):
        """Тест подтверждения без учета регистра"""
        self.mock_input.return_value = "Y"
        result = confirm_action("Продолжить?")
        assert result is True

    def test_confirm_action_retry_logic(self):
        """Тест повторного подтверждения при некорректном вводе"""
        # Мокируем последовательность: неверный ввод -> корректный ввод
        self.mock_input.side_effect = ["invalid", "y"]
        result = confirm_action("Продолжить?")
        assert result is True
        # Проверяем, что input был вызван дважды
        assert self.mock_input.call_count == 2

    def test_get_user_input_basic(self):
        """Тест получения пользовательского ввода"""
        self.mock_input.return_value = "test input"
        result = get_user_input("Введите данные:")
        assert result == "test input"

    def test_get_user_input_empty_required(self):
        """Тест пустого ввода при required=True"""
        # Мокируем последовательность: пустой ввод -> корректный ввод
        self.mock_input.side_effect = ["", "valid input"]
        result = get_user_input("Введите данные:", required=True)
        assert result == "valid input"

    def test_get_user_input_empty_not_required(self):
        """Тест пустого ввода при required=False"""
        self.mock_input.return_value = ""
        result = get_user_input("Введите данные:", required=False)
        assert result is None

    def test_get_positive_integer_valid(self):
        """Тест получения положительного числа - валидное значение"""
        self.mock_input.return_value = "42"
        result = get_positive_integer("Введите число:")
        assert result == 42

    def test_get_positive_integer_with_default(self):
        """Тест положительного числа с дефолтным значением"""
        self.mock_input.return_value = ""
        result = get_positive_integer("Введите число:", default=10)
        assert result == 10

    def test_get_positive_integer_invalid_then_valid(self):
        """Тест повторного запроса при некорректном вводе"""
        self.mock_input.side_effect = ["invalid", "42"]
        result = get_positive_integer("Введите число:")
        # Функция возвращает None при первом неверном вводе, затем нужен повторный вызов
        assert result is None  # Первый вызов с "invalid"

        # Второй вызов
        self.mock_input.return_value = "42"
        result = get_positive_integer("Введите число:")
        assert result == 42

    def test_get_positive_integer_negative(self):
        """Тест ввода отрицательного числа"""
        self.mock_input.return_value = "-5"
        result = get_positive_integer("Введите число:")
        assert result is None  # Функция должна вернуть None для отрицательного числа

    def test_get_positive_integer_zero(self):
        """Тест ввода нуля"""
        self.mock_input.return_value = "0"
        result = get_positive_integer("Введите число:")
        assert result is None  # 0 не является положительным числом

    def test_parse_salary_range_valid_with_spaces(self):
        """Тест парсинга корректного диапазона с пробелами"""
        result = parse_salary_range("100000 - 150000")
        assert result == (100000, 150000)

    def test_parse_salary_range_valid_without_spaces(self):
        """Тест парсинга диапазона без пробелов"""
        result = parse_salary_range("100000-150000")
        assert result == (100000, 150000)

    def test_parse_salary_range_reversed(self):
        """Тест парсинга диапазона с обратным порядком"""
        result = parse_salary_range("150000 - 100000")
        assert result == (100000, 150000)  # Функция должна поменять местами

    def test_parse_salary_range_invalid_format(self):
        """Тест парсинга некорректного формата"""
        result = parse_salary_range("invalid format")
        assert result is None

    def test_parse_salary_range_invalid_numbers(self):
        """Тест парсинга с некорректными числами"""
        result = parse_salary_range("abc - def")
        assert result is None

    def test_ui_helpers_module_structure(self):
        """Тест структуры модуля ui_helpers"""
        import src.utils.ui_helpers as ui_helpers

        expected_functions = ["confirm_action", "get_user_input", "get_positive_integer", "parse_salary_range"]

        for func_name in expected_functions:
            assert hasattr(ui_helpers, func_name), f"Функция {func_name} не найдена"
            assert callable(getattr(ui_helpers, func_name)), f"{func_name} не является функцией"

    def test_all_functions_with_mocked_input(self):
        """Комплексный тест всех функций с мокированным вводом"""
        # Тест confirm_action
        self.mock_input.return_value = "y"
        assert confirm_action("Test?") is True

        # Тест get_user_input
        self.mock_input.return_value = "test"
        assert get_user_input("Test prompt:") == "test"

        # Тест get_positive_integer
        self.mock_input.return_value = "42"
        assert get_positive_integer("Number:") == 42

        # Тест parse_salary_range (не требует input)
        assert parse_salary_range("100-200") == (100, 200)

    def test_edge_cases_consolidated(self):
        """Консолидированный тест граничных случаев"""
        # Пустые строки
        self.mock_input.return_value = ""

        # get_user_input с required=False
        result = get_user_input("Test:", required=False)
        assert result is None

        # get_positive_integer с default
        result = get_positive_integer("Test:", default=5)
        assert result == 5

        # confirm_action с русскими символами
        self.mock_input.return_value = "да"
        assert confirm_action("Тест?") is True

        self.mock_input.return_value = "нет"
        assert confirm_action("Тест?") is False

    def test_error_handling_consolidated(self):
        """Консолидированный тест обработки ошибок"""
        # Тест parse_salary_range с различными ошибками
        error_cases = [
            "not_a_range",
            "100",  # одно число
            "",  # пустая строка
            "abc-def",  # не числа
            "100--200",  # двойное тире
        ]

        for case in error_cases:
            result = parse_salary_range(case)
            assert result is None, f"parse_salary_range должен вернуть None для '{case}'"

    def test_function_return_types(self):
        """Тест типов возвращаемых значений"""
        # confirm_action должен возвращать bool
        self.mock_input.return_value = "y"
        result = confirm_action("Test?")
        assert isinstance(result, bool)

        # get_user_input должен возвращать str или None
        self.mock_input.return_value = "test"
        result = get_user_input("Test:")
        assert isinstance(result, str)

        # get_positive_integer должен возвращать int или None
        self.mock_input.return_value = "42"
        result = get_positive_integer("Test:")
        assert isinstance(result, int)

        # parse_salary_range должен возвращать tuple или None
        result = parse_salary_range("100-200")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_input_sanitization(self):
        """Тест санитизации ввода"""
        # Тест что пробелы обрезаются
        self.mock_input.return_value = "  test  "
        result = get_user_input("Test:")
        assert result == "test"  # Пробелы должны быть обрезаны

        # Тест регистронезависимости для confirm_action
        test_cases = ["Y", "y", "YES", "yes", "Да", "ДА"]
        for case in test_cases:
            self.mock_input.return_value = case
            result = confirm_action("Test?")
            assert result is True, f"'{case}' должен быть интерпретирован как True"
