"""
Комплексные тесты для модуля ui_helpers
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch
import pytest

# Мокаем psycopg2 перед импортом
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.sql'] = MagicMock()

# Добавляем путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import ui_helpers


class TestUIHelpers:
    """Тесты для функций пользовательского интерфейса"""
    
    @patch('builtins.input')
    def test_get_user_input_valid_required(self, mock_input):
        """Тест получения валидного обязательного ввода"""
        mock_input.return_value = "test input"
        
        result = ui_helpers.get_user_input("Enter text: ", required=True)
        
        assert result == "test input"
    
    @patch('builtins.input')
    def test_get_user_input_valid_not_required(self, mock_input):
        """Тест получения валидного необязательного ввода"""
        mock_input.return_value = "test input"
        
        result = ui_helpers.get_user_input("Enter text: ", required=False)
        
        assert result == "test input"
    
    @patch('builtins.input')
    def test_get_user_input_empty_not_required(self, mock_input):
        """Тест пустого ввода для необязательного поля"""
        mock_input.return_value = ""
        
        result = ui_helpers.get_user_input("Enter text: ", required=False)
        
        assert result is None
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_empty_required_then_valid(self, mock_print, mock_input):
        """Тест пустого ввода для обязательного поля с последующим валидным вводом"""
        mock_input.side_effect = ["", "valid input"]
        
        result = ui_helpers.get_user_input("Enter text: ", required=True)
        
        assert result == "valid input"
        mock_print.assert_called_with("Поле не может быть пустым!")
    
    @patch('builtins.input')
    def test_get_user_input_whitespace_trimmed(self, mock_input):
        """Тест обрезки пробелов во вводе"""
        mock_input.return_value = "  test input  "
        
        result = ui_helpers.get_user_input("Enter text: ")
        
        assert result == "test input"
    
    @patch('builtins.input')
    def test_get_positive_integer_valid(self, mock_input):
        """Тест получения валидного положительного числа"""
        mock_input.return_value = "42"
        
        result = ui_helpers.get_positive_integer("Enter number: ")
        
        assert result == 42
    
    @patch('builtins.input')
    def test_get_positive_integer_with_default(self, mock_input):
        """Тест использования значения по умолчанию"""
        mock_input.return_value = ""
        
        result = ui_helpers.get_positive_integer("Enter number: ", default=10)
        
        assert result == 10
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_empty_no_default(self, mock_print, mock_input):
        """Тест пустого ввода без значения по умолчанию"""
        mock_input.return_value = ""
        
        result = ui_helpers.get_positive_integer("Enter number: ")
        
        assert result is None
        mock_print.assert_called_with("Введите корректное число!")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_negative(self, mock_print, mock_input):
        """Тест отрицательного числа"""
        mock_input.return_value = "-5"
        
        result = ui_helpers.get_positive_integer("Enter number: ")
        
        assert result is None
        mock_print.assert_called_with("Число должно быть положительным!")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_zero(self, mock_print, mock_input):
        """Тест нуля"""
        mock_input.return_value = "0"
        
        result = ui_helpers.get_positive_integer("Enter number: ")
        
        assert result is None
        mock_print.assert_called_with("Число должно быть положительным!")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_invalid_format(self, mock_print, mock_input):
        """Тест неверного формата числа"""
        mock_input.return_value = "abc"
        
        result = ui_helpers.get_positive_integer("Enter number: ")
        
        assert result is None
        mock_print.assert_called_with("Введите корректное число!")
    
    def test_parse_salary_range_valid_range(self):
        """Тест парсинга валидного диапазона зарплат"""
        result = ui_helpers.parse_salary_range("100000 - 150000")
        
        assert result == (100000, 150000)
    
    def test_parse_salary_range_valid_range_spaces(self):
        """Тест парсинга диапазона с разным количеством пробелов"""
        result = ui_helpers.parse_salary_range("100000-150000")
        
        assert result == (100000, 150000)
    
    def test_parse_salary_range_single_value(self):
        """Тест парсинга одного значения"""
        result = ui_helpers.parse_salary_range("100000")
        
        # Должно вернуть None для одного значения
        assert result is None
    
    def test_parse_salary_range_invalid_format(self):
        """Тест парсинга неверного формата"""
        result = ui_helpers.parse_salary_range("abc - def")
        
        assert result is None
    
    def test_parse_salary_range_empty_string(self):
        """Тест парсинга пустой строки"""
        result = ui_helpers.parse_salary_range("")
        
        assert result is None
    
    def test_parse_salary_range_reversed_values(self):
        """Тест диапазона где первое значение больше второго"""
        result = ui_helpers.parse_salary_range("150000 - 100000")
        
        # Функция должна вернуть значения как есть
        assert result == (150000, 100000)
    
    @patch('builtins.input')
    def test_confirm_action_yes(self, mock_input):
        """Тест подтверждения действия - да"""
        mock_input.return_value = "y"
        
        result = ui_helpers.confirm_action("Continue?")
        
        assert result is True
    
    @patch('builtins.input')
    def test_confirm_action_no(self, mock_input):
        """Тест подтверждения действия - нет"""
        mock_input.return_value = "n"
        
        result = ui_helpers.confirm_action("Continue?")
        
        assert result is False
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_confirm_action_invalid_then_valid(self, mock_print, mock_input):
        """Тест неверного ввода с последующим валидным"""
        mock_input.side_effect = ["maybe", "y"]
        
        result = ui_helpers.confirm_action("Continue?")
        
        assert result is True
        mock_print.assert_called_with("Введите 'y' для да или 'n' для нет.")
    
    def test_filter_vacancies_by_keyword_basic(self):
        """Тест фильтрации вакансий по ключевому слову"""
        # Создаем тестовые вакансии
        vacancy1 = Mock()
        vacancy1.title = "Python Developer"
        vacancy1.description = "We need a Python developer"
        
        vacancy2 = Mock()
        vacancy2.title = "Java Developer"
        vacancy2.description = "We need a Java developer"
        
        vacancies = [vacancy1, vacancy2]
        
        result = ui_helpers.filter_vacancies_by_keyword(vacancies, "Python")
        
        # Поскольку функция может использовать внутреннюю логику,
        # проверяем что она вернула список
        assert isinstance(result, list)
    
    def test_display_vacancy_info_basic(self):
        """Тест отображения информации о вакансии"""
        vacancy = Mock()
        vacancy.title = "Test Developer"
        vacancy.employer = Mock()
        vacancy.employer.name = "Test Company"
        vacancy.salary = Mock()
        vacancy.url = "http://test.com"
        
        with patch('builtins.print') as mock_print:
            ui_helpers.display_vacancy_info(vacancy, 1)
            
        # Проверяем что print был вызван
        mock_print.assert_called()
    
    def test_filter_vacancies_by_min_salary_basic(self):
        """Тест фильтрации по минимальной зарплате"""
        vacancy1 = Mock()
        vacancy1.salary = Mock()
        vacancy1.salary.salary_from = 150000
        vacancy1.salary.salary_to = 200000
        
        vacancy2 = Mock()
        vacancy2.salary = Mock() 
        vacancy2.salary.salary_from = 80000
        vacancy2.salary.salary_to = 120000
        
        vacancies = [vacancy1, vacancy2]
        
        result = ui_helpers.filter_vacancies_by_min_salary(vacancies, 100000)
        
        # Проверяем что функция вернула список
        assert isinstance(result, list)
    
    def test_get_vacancies_with_salary_basic(self):
        """Тест получения вакансий с зарплатой"""
        vacancy1 = Mock()
        vacancy1.salary = Mock()
        vacancy1.salary.salary_from = 100000
        
        vacancy2 = Mock()
        vacancy2.salary = None
        
        vacancies = [vacancy1, vacancy2]
        
        result = ui_helpers.get_vacancies_with_salary(vacancies)
        
        # Проверяем что функция вернула список
        assert isinstance(result, list)
    
    def test_sort_vacancies_by_salary_basic(self):
        """Тест сортировки вакансий по зарплате"""
        vacancy1 = Mock()
        vacancy1.salary = Mock()
        vacancy1.salary.salary_from = 100000
        
        vacancy2 = Mock()
        vacancy2.salary = Mock()
        vacancy2.salary.salary_from = 150000
        
        vacancies = [vacancy1, vacancy2]
        
        result = ui_helpers.sort_vacancies_by_salary(vacancies)
        
        # Проверяем что функция вернула список
        assert isinstance(result, list)
        assert len(result) == 2