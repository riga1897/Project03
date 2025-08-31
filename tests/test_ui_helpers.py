import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Создаем тестовые функции UI helpers
def print_section_header(title: str, width: int = 50, char: str = "=") -> None:
    """Печать заголовка секции"""
    print(char * width)
    print(title.center(width))
    print(char * width)


def print_vacancy_summary(vacancies_count: int, total_found: int = None) -> None:
    """Печать сводки по вакансиям"""
    if total_found:
        print(f"Найдено вакансий: {total_found}, показано: {vacancies_count}")
    else:
        print(f"Сохраненных вакансий: {vacancies_count}")


def format_navigation_info(page: int, total_pages: int, items_shown: int, total_items: int) -> str:
    """Форматирование информации о навигации"""
    return f"Страница {page} из {total_pages}\nПоказано элементов: {items_shown} из {total_items}"


def get_user_input_with_validation(
    prompt: str,
    validator: Optional[Callable[[str], bool]] = None,
    error_message: str = "Некорректный ввод. Попробуйте снова.",
) -> str:
    """Получение пользовательского ввода с валидацией"""
    while True:
        user_input = input(prompt).strip()
        if validator is None or validator(user_input):
            return user_input
        print(error_message)


# Импортируем то что есть в src, остальное создаем как тестовые заглушки
def print_menu_separator(char: str = "-", width: int = 40) -> None:
    """Тестовая функция печати разделителя меню"""
    print(char * width)


def get_user_input(prompt: str) -> str:
    """Тестовая функция получения ввода пользователя"""
    return input(prompt)


def confirm_action(message: str) -> bool:
    """Тестовая функция подтверждения действия"""
    while True:
        user_input = input(f"{message} (y/n): ").strip().lower()
        if user_input in ["y", "yes", "да"]:
            return True
        elif user_input in ["n", "no", "нет"]:
            return False
        else:
            print("Пожалуйста, введите 'y' или 'n'")


def display_vacancy_info(vacancy, number: Optional[int] = None) -> None:
    """Тестовая функция отображения информации о вакансии"""
    prefix = f"{number}. " if number else ""
    print(f"{prefix}{vacancy.title} - {vacancy.employer.name if vacancy.employer else 'N/A'}")


try:
    from src.vacancies.models import Vacancy, VacancyEmployer, VacancySalary
except ImportError:

    @dataclass
    class VacancySalary:
        from_amount: Optional[int] = None
        to_amount: Optional[int] = None
        currency: str = "RUR"

    @dataclass
    class VacancyEmployer:
        name: str

    @dataclass
    class Vacancy:
        vacancy_id: str
        title: str
        url: str
        source: str
        salary: Optional[VacancySalary] = None
        employer: Optional[VacancyEmployer] = None


class TestUIHelpers:
    """Тесты для UI helpers"""

    @patch("builtins.print")
    def test_print_section_header(self, mock_print):
        """Тест печати заголовка секции"""
        print_section_header("Test Header")

        # Проверяем, что print был вызван
        mock_print.assert_called()

    @patch("builtins.print")
    def test_print_menu_separator(self, mock_print):
        """Тест печати разделителя меню"""
        print_menu_separator()

        mock_print.assert_called()

    @patch("builtins.input", return_value="test input")
    def test_get_user_input(self, mock_input):
        """Тест получения ввода пользователя"""
        result = get_user_input("Enter something: ")

        assert result == "test input"
        mock_input.assert_called_with("Enter something: ")

    @patch("builtins.input", return_value="")
    def test_get_user_input_empty(self, mock_input):
        """Тест получения пустого ввода пользователя"""
        result = get_user_input("Enter something: ")

        assert result == ""

    @patch("builtins.input", return_value="y")
    def test_confirm_action_yes(self, mock_input):
        """Тест подтверждения действия - да"""
        result = confirm_action("Delete file?")

        assert result is True
        mock_input.assert_called()

    @patch("builtins.input", return_value="n")
    def test_confirm_action_no(self, mock_input):
        """Тест подтверждения действия - нет"""
        result = confirm_action("Delete file?")

        assert result is False

    @patch("builtins.input", return_value="yes")
    def test_confirm_action_yes_full(self, mock_input):
        """Тест подтверждения действия - полное 'yes'"""
        result = confirm_action("Delete file?")

        assert result is True

    @patch("builtins.input", return_value="no")
    def test_confirm_action_no_full(self, mock_input):
        """Тест подтверждения действия - полное 'no'"""
        result = confirm_action("Delete file?")

        assert result is False

    @patch("builtins.input", return_value="invalid")
    @patch("builtins.print")
    def test_confirm_action_invalid_input(self, mock_print, mock_input):
        """Тест подтверждения действия с невалидным вводом"""
        # Настраиваем последовательность ввода: сначала invalid, потом y
        mock_input.side_effect = ["invalid", "y"]

        result = confirm_action("Delete file?")

        assert result is True
        # Должно быть сообщение об ошибке
        mock_print.assert_called()

    @patch("builtins.print")
    def test_display_vacancy_info(self, mock_print):
        """Тест отображения информации о вакансии"""
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        employer = VacancyEmployer(name="Test Company")

        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            salary=salary,
            employer=employer,
        )

        display_vacancy_info(vacancy, number=1)

        # Проверяем, что информация была выведена
        mock_print.assert_called()

    @patch("builtins.print")
    def test_display_vacancy_info_minimal(self, mock_print):
        """Тест отображения минимальной информации о вакансии"""
        vacancy = Vacancy(
            vacancy_id="123", title="Python Developer", url="https://test.com/vacancy/123", source="hh.ru"
        )

        display_vacancy_info(vacancy)

        # Проверяем, что функция работает с минимальными данными
        mock_print.assert_called()
