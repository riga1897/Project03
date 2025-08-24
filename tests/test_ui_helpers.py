
"""
Тесты для UI помощников
"""

import pytest
from unittest.mock import patch, Mock
from src.utils.ui_helpers import (
    get_positive_integer,
    filter_vacancies_by_keyword,
    parse_salary_range
)
from src.vacancies.models import Vacancy


class TestUIHelpers:
    """Тесты для UI помощников"""

    @patch('builtins.input', return_value='10')
    def test_get_positive_integer_valid(self, mock_input):
        """Тест получения корректного положительного числа"""
        result = get_positive_integer("Enter number: ")
        
        assert result == 10

    @patch('builtins.input', side_effect=['-5', '0', '15'])
    def test_get_positive_integer_invalid_then_valid(self, mock_input):
        """Тест получения числа с некорректными вводами сначала"""
        with patch('builtins.print'):  # Подавляем вывод ошибок
            result = get_positive_integer("Enter number: ")
        
        assert result == 15

    @patch('builtins.input', return_value='not_a_number')
    def test_get_positive_integer_non_numeric(self, mock_input):
        """Тест ввода нечислового значения"""
        with patch('builtins.print'):
            result = get_positive_integer("Enter number: ", max_attempts=1)
        
        assert result is None

    def test_filter_vacancies_by_keyword_in_title(self):
        """Тест фильтрации вакансий по ключевому слову в названии"""
        vacancies = [
            Vacancy(title="Python Developer", vacancy_id="1"),
            Vacancy(title="Java Developer", vacancy_id="2"),
            Vacancy(title="Senior Python Engineer", vacancy_id="3"),
        ]
        
        result = filter_vacancies_by_keyword(vacancies, "Python")
        
        assert len(result) == 2
        vacancy_ids = [v.vacancy_id for v in result]
        assert "1" in vacancy_ids
        assert "3" in vacancy_ids

    def test_filter_vacancies_by_keyword_in_description(self):
        """Тест фильтрации по ключевому слову в описании"""
        vacancies = [
            Vacancy(title="Developer", description="Python programming", vacancy_id="1"),
            Vacancy(title="Developer", description="Java programming", vacancy_id="2"),
        ]
        
        result = filter_vacancies_by_keyword(vacancies, "Python")
        
        assert len(result) == 1
        assert result[0].vacancy_id == "1"

    def test_filter_vacancies_by_keyword_case_insensitive(self):
        """Тест фильтрации с нечувствительностью к регистру"""
        vacancies = [
            Vacancy(title="python developer", vacancy_id="1"),
            Vacancy(title="PYTHON ENGINEER", vacancy_id="2"),
            Vacancy(title="Java Developer", vacancy_id="3"),
        ]
        
        result = filter_vacancies_by_keyword(vacancies, "PYTHON")
        
        assert len(result) == 2
        vacancy_ids = [v.vacancy_id for v in result]
        assert "1" in vacancy_ids
        assert "2" in vacancy_ids

    def test_filter_vacancies_by_keyword_no_matches(self):
        """Тест фильтрации без совпадений"""
        vacancies = [
            Vacancy(title="Java Developer", vacancy_id="1"),
            Vacancy(title="C# Developer", vacancy_id="2"),
        ]
        
        result = filter_vacancies_by_keyword(vacancies, "Python")
        
        assert len(result) == 0

    def test_parse_salary_range_both_values(self):
        """Тест парсинга диапазона зарплат с обеими границами"""
        result = parse_salary_range("100000-150000")
        
        assert result == (100000, 150000)

    def test_parse_salary_range_only_min(self):
        """Тест парсинга только минимальной зарплаты"""
        result = parse_salary_range("80000-")
        
        assert result == (80000, None)

    def test_parse_salary_range_only_max(self):
        """Тест парсинга только максимальной зарплаты"""
        result = parse_salary_range("-120000")
        
        assert result == (None, 120000)

    def test_parse_salary_range_single_value(self):
        """Тест парсинга одного значения зарплаты"""
        result = parse_salary_range("100000")
        
        assert result == (100000, 100000)

    def test_parse_salary_range_invalid_format(self):
        """Тест парсинга некорректного формата"""
        result = parse_salary_range("not-a-salary")
        
        assert result == (None, None)

    def test_parse_salary_range_empty_string(self):
        """Тест парсинга пустой строки"""
        result = parse_salary_range("")
        
        assert result == (None, None)

    def test_parse_salary_range_with_spaces(self):
        """Тест парсинга с пробелами"""
        result = parse_salary_range(" 100000 - 150000 ")
        
        assert result == (100000, 150000)
