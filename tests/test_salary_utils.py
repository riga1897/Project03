
import pytest
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.salary import parse_salary_range, format_salary, normalize_salary


class TestSalaryUtils:
    """Тесты для утилит работы с зарплатой"""

    def test_parse_salary_range_valid(self):
        """Тест парсинга валидного диапазона зарплаты"""
        result = parse_salary_range("100000 - 150000")
        assert result == (100000, 150000)
        
        result = parse_salary_range("50000-80000")
        assert result == (50000, 80000)
        
        result = parse_salary_range("200000   -   300000")
        assert result == (200000, 300000)

    def test_parse_salary_range_invalid(self):
        """Тест парсинга невалидного диапазона зарплаты"""
        assert parse_salary_range("invalid") is None
        assert parse_salary_range("") is None
        assert parse_salary_range("100000") is None
        assert parse_salary_range("abc - def") is None

    def test_parse_salary_range_reverse_order(self):
        """Тест парсинга диапазона в обратном порядке"""
        result = parse_salary_range("150000 - 100000")
        # Должно автоматически поменять местами
        assert result == (100000, 150000)

    def test_format_salary_with_range(self):
        """Тест форматирования зарплаты с диапазоном"""
        from src.vacancies.models import VacancySalary
        
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        result = format_salary(salary)
        
        assert "100000" in result
        assert "150000" in result
        assert "руб" in result

    def test_format_salary_from_only(self):
        """Тест форматирования зарплаты только с минимальным значением"""
        from src.vacancies.models import VacancySalary
        
        salary = VacancySalary(from_amount=100000, currency="RUR")
        result = format_salary(salary)
        
        assert "от 100000" in result
        assert "руб" in result

    def test_format_salary_to_only(self):
        """Тест форматирования зарплаты только с максимальным значением"""
        from src.vacancies.models import VacancySalary
        
        salary = VacancySalary(to_amount=150000, currency="RUR")
        result = format_salary(salary)
        
        assert "до 150000" in result
        assert "руб" in result

    def test_format_salary_none(self):
        """Тест форматирования пустой зарплаты"""
        result = format_salary(None)
        assert result == "Зарплата не указана"

    def test_normalize_salary_with_range(self):
        """Тест нормализации зарплаты с диапазоном"""
        from src.vacancies.models import VacancySalary
        
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        result = normalize_salary(salary)
        
        # Должно вернуть среднее значение
        assert result == 125000

    def test_normalize_salary_from_only(self):
        """Тест нормализации зарплаты только с минимальным значением"""
        from src.vacancies.models import VacancySalary
        
        salary = VacancySalary(from_amount=100000, currency="RUR")
        result = normalize_salary(salary)
        
        assert result == 100000

    def test_normalize_salary_to_only(self):
        """Тест нормализации зарплаты только с максимальным значением"""
        from src.vacancies.models import VacancySalary
        
        salary = VacancySalary(to_amount=150000, currency="RUR")
        result = normalize_salary(salary)
        
        assert result == 150000

    def test_normalize_salary_none(self):
        """Тест нормализации пустой зарплаты"""
        result = normalize_salary(None)
        assert result == 0
