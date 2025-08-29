"""
Тесты для UI помощников

Содержит тесты для проверки функций пользовательского интерфейса
без реального взаимодействия с пользователем.
"""

from unittest.mock import Mock, patch

import pytest

from src.utils.ui_helpers import confirm_action, display_vacancy_info, get_user_input, parse_salary_range
from src.vacancies.models import Vacancy


class TestUIHelpers:
    """Тесты для UI помощников"""

    @patch("builtins.input")
    def test_confirm_action_yes(self, mock_input):
        """Тест подтверждения действия - да"""
        mock_input.return_value = "y"
        result = confirm_action("Удалить файл?")
        assert result is True

    @patch("builtins.input")
    def test_confirm_action_no(self, mock_input):
        """Тест подтверждения действия - нет"""
        mock_input.return_value = "n"
        result = confirm_action("Удалить файл?")
        assert result is False

    @patch("builtins.input")
    def test_confirm_action_default(self, mock_input):
        """Тест подтверждения действия - по умолчанию"""
        mock_input.return_value = ""
        result = confirm_action("Продолжить?", default=True)
        assert result is True

    @patch("builtins.input")
    def test_get_user_input(self, mock_input):
        """Тест получения ввода пользователя"""
        mock_input.return_value = "test input"
        result = get_user_input("Введите текст: ")
        assert result == "test input"

    @patch("builtins.input")
    def test_get_user_input_empty(self, mock_input):
        """Тест получения пустого ввода"""
        mock_input.return_value = ""
        result = get_user_input("Введите текст: ")
        assert result == ""

    def test_parse_salary_range_valid(self):
        """Тест парсинга корректного диапазона зарплат"""
        result = parse_salary_range("100000 - 150000")
        assert result == (100000, 150000)

    def test_parse_salary_range_single_dash(self):
        """Тест парсинга диапазона с одним тире"""
        result = parse_salary_range("80000-120000")
        assert result == (80000, 120000)

    def test_parse_salary_range_invalid(self):
        """Тест парсинга некорректного диапазона"""
        result = parse_salary_range("invalid range")
        assert result is None

    def test_parse_salary_range_reversed(self):
        """Тест парсинга обращенного диапазона"""
        result = parse_salary_range("150000 - 100000")
        assert result == (100000, 150000)

    @patch("builtins.print")
    def test_display_vacancy_info(self, mock_print, sample_vacancy):
        """Тест отображения информации о вакансии"""
        display_vacancy_info(sample_vacancy, 1)
        # Проверяем, что print был вызван
        assert mock_print.called

    @patch("builtins.print")
    def test_display_vacancy_info_no_number(self, mock_print, sample_vacancy):
        """Тест отображения информации о вакансии без номера"""
        display_vacancy_info(sample_vacancy)
        # Проверяем, что print был вызван
        assert mock_print.called


class TestSalaryParsing:
    """Тесты для парсинга зарплатных диапазонов"""

    def test_various_formats(self):
        """Тест различных форматов диапазонов"""
        test_cases = [
            ("100000 - 150000", (100000, 150000)),
            ("100000-150000", (100000, 150000)),
            ("100 000 - 150 000", (100000, 150000)),
            ("100,000-150,000", (100000, 150000)),
            ("50000", None),  # Одно число не является диапазоном
            ("abc - def", None),  # Некорректный формат
            ("", None),  # Пустая строка
        ]

        for input_str, expected in test_cases:
            result = parse_salary_range(input_str)
            assert result == expected, f"Failed for input: {input_str}"
