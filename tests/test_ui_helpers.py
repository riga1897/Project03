
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.ui_helpers import (
    print_section_header, print_menu_separator, get_user_input,
    confirm_action, display_vacancy_info
)
from src.vacancies.models import Vacancy, VacancySalary, VacancyEmployer


class TestUIHelpers:
    """Тесты для UI helpers"""

    @patch('builtins.print')
    def test_print_section_header(self, mock_print):
        """Тест печати заголовка секции"""
        print_section_header("Test Header")
        
        # Проверяем, что print был вызван
        mock_print.assert_called()

    @patch('builtins.print')
    def test_print_menu_separator(self, mock_print):
        """Тест печати разделителя меню"""
        print_menu_separator()
        
        mock_print.assert_called()

    @patch('builtins.input', return_value='test input')
    def test_get_user_input(self, mock_input):
        """Тест получения ввода пользователя"""
        result = get_user_input("Enter something: ")
        
        assert result == "test input"
        mock_input.assert_called_with("Enter something: ")

    @patch('builtins.input', return_value='')
    def test_get_user_input_empty(self, mock_input):
        """Тест получения пустого ввода пользователя"""
        result = get_user_input("Enter something: ")
        
        assert result == ""

    @patch('builtins.input', return_value='y')
    def test_confirm_action_yes(self, mock_input):
        """Тест подтверждения действия - да"""
        result = confirm_action("Delete file?")
        
        assert result is True
        mock_input.assert_called()

    @patch('builtins.input', return_value='n')
    def test_confirm_action_no(self, mock_input):
        """Тест подтверждения действия - нет"""
        result = confirm_action("Delete file?")
        
        assert result is False

    @patch('builtins.input', return_value='yes')
    def test_confirm_action_yes_full(self, mock_input):
        """Тест подтверждения действия - полное 'yes'"""
        result = confirm_action("Delete file?")
        
        assert result is True

    @patch('builtins.input', return_value='no')
    def test_confirm_action_no_full(self, mock_input):
        """Тест подтверждения действия - полное 'no'"""
        result = confirm_action("Delete file?")
        
        assert result is False

    @patch('builtins.input', return_value='invalid')
    @patch('builtins.print')
    def test_confirm_action_invalid_input(self, mock_print, mock_input):
        """Тест подтверждения действия с невалидным вводом"""
        # Настраиваем последовательность ввода: сначала invalid, потом y
        mock_input.side_effect = ['invalid', 'y']
        
        result = confirm_action("Delete file?")
        
        assert result is True
        # Должно быть сообщение об ошибке
        mock_print.assert_called()

    @patch('builtins.print')
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
            area="Москва",
            experience="От 1 года до 3 лет"
        )
        
        display_vacancy_info(vacancy, number=1)
        
        # Проверяем, что информация была выведена
        mock_print.assert_called()

    @patch('builtins.print')
    def test_display_vacancy_info_minimal(self, mock_print):
        """Тест отображения минимальной информации о вакансии"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru"
        )
        
        display_vacancy_info(vacancy)
        
        # Проверяем, что функция работает с минимальными данными
        mock_print.assert_called()
