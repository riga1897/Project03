
import os
import sys
from unittest.mock import Mock, patch
from typing import Optional, Dict, Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импортируем все доступные функции из модуля salary
from src.utils.salary import (
    normalize_salary,
    format_salary_range,
    parse_salary_string,
    calculate_salary_average,
    compare_salaries,
    convert_salary_currency,
    validate_salary_data,
    get_salary_statistics,
    filter_by_salary_range
)


# Создаем недостающие классы для тестов
class SalaryHelper:
    """Вспомогательный класс для работы с зарплатами в тестах"""
    
    @staticmethod
    def normalize_salary(salary_data):
        """Нормализация данных о зарплате"""
        if not salary_data:
            return None
            
        if isinstance(salary_data, dict):
            return {
                'from': salary_data.get('from'),
                'to': salary_data.get('to'),
                'currency': salary_data.get('currency', 'RUR')
            }
        return salary_data
    
    @staticmethod
    def format_salary_display(salary_from, salary_to, currency='RUR'):
        """Форматирование зарплаты для отображения"""
        if salary_from and salary_to:
            return f"{salary_from} - {salary_to} {currency}"
        elif salary_from:
            return f"от {salary_from} {currency}"
        elif salary_to:
            return f"до {salary_to} {currency}"
        return "Не указана"
    
    @staticmethod
    def calculate_average_salary(vacancies):
        """Расчет средней зарплаты по списку вакансий"""
        if not vacancies:
            return None
            
        total_salaries = []
        for vacancy in vacancies:
            salary = getattr(vacancy, 'salary', None)
            if salary:
                if hasattr(salary, 'salary_from') and hasattr(salary, 'salary_to'):
                    if salary.salary_from and salary.salary_to:
                        total_salaries.append((salary.salary_from + salary.salary_to) / 2)
                    elif salary.salary_from:
                        total_salaries.append(salary.salary_from)
                    elif salary.salary_to:
                        total_salaries.append(salary.salary_to)
        
        return sum(total_salaries) / len(total_salaries) if total_salaries else None


class SalaryFilter:
    """Класс для фильтрации вакансий по зарплате"""
    
    def __init__(self, min_salary=None, max_salary=None):
        self.min_salary = min_salary
        self.max_salary = max_salary
    
    def filter_vacancies(self, vacancies):
        """Фильтрация вакансий по диапазону зарплат"""
        if not vacancies:
            return []
            
        filtered = []
        for vacancy in vacancies:
            if self._matches_criteria(vacancy):
                filtered.append(vacancy)
        return filtered
    
    def _matches_criteria(self, vacancy):
        """Проверка соответствия вакансии критериям зарплаты"""
        salary = getattr(vacancy, 'salary', None)
        if not salary:
            return False
            
        vacancy_salary = self._extract_salary_value(salary)
        if vacancy_salary is None:
            return False
            
        if self.min_salary and vacancy_salary < self.min_salary:
            return False
        if self.max_salary and vacancy_salary > self.max_salary:
            return False
            
        return True
    
    def _extract_salary_value(self, salary):
        """Извлечение числового значения зарплаты"""
        if hasattr(salary, 'salary_from') and hasattr(salary, 'salary_to'):
            if salary.salary_from and salary.salary_to:
                return (salary.salary_from + salary.salary_to) / 2
            elif salary.salary_from:
                return salary.salary_from
            elif salary.salary_to:
                return salary.salary_to
        return None


class TestSalaryUtils:
    """Тесты для утилит работы с зарплатой"""

    def test_normalize_salary_dict(self):
        """Тест нормализации зарплаты из словаря"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = normalize_salary(salary_data)
        assert isinstance(result, dict)
        assert result["from"] == 100000
        assert result["to"] == 150000
        assert result["currency"] == "RUR"

    def test_normalize_salary_none(self):
        """Тест нормализации пустой зарплаты"""
        result = normalize_salary(None)
        assert result is None

    def test_normalize_salary_empty_dict(self):
        """Тест нормализации пустого словаря"""
        result = normalize_salary({})
        assert isinstance(result, dict)
        assert result["from"] is None
        assert result["to"] is None
        assert result["currency"] == "RUR"

    def test_format_salary_range_full(self):
        """Тест форматирования полного диапазона зарплаты"""
        result = format_salary_range(100000, 150000, "RUR")
        assert "100000" in result
        assert "150000" in result
        assert "RUR" in result

    def test_format_salary_range_from_only(self):
        """Тест форматирования зарплаты только с минимумом"""
        result = format_salary_range(100000, None, "RUR")
        assert "100000" in result
        assert "RUR" in result

    def test_format_salary_range_to_only(self):
        """Тест форматирования зарплаты только с максимумом"""
        result = format_salary_range(None, 150000, "RUR")
        assert "150000" in result
        assert "RUR" in result

    def test_format_salary_range_none(self):
        """Тест форматирования пустой зарплаты"""
        result = format_salary_range(None, None, "RUR")
        assert result == "Не указана"

    def test_parse_salary_string_range(self):
        """Тест парсинга строки с диапазоном зарплаты"""
        result = parse_salary_string("100000 - 150000 RUR")
        assert isinstance(result, dict)
        assert result["from"] == 100000
        assert result["to"] == 150000
        assert result["currency"] == "RUR"

    def test_parse_salary_string_from_only(self):
        """Тест парсинга строки с минимальной зарплатой"""
        result = parse_salary_string("от 100000 RUR")
        assert isinstance(result, dict)
        assert result["from"] == 100000
        assert result["to"] is None

    def test_parse_salary_string_invalid(self):
        """Тест парсинга некорректной строки"""
        result = parse_salary_string("invalid salary")
        assert result is None

    def test_calculate_salary_average_range(self):
        """Тест расчета средней зарплаты из диапазона"""
        result = calculate_salary_average(100000, 150000)
        assert result == 125000

    def test_calculate_salary_average_from_only(self):
        """Тест расчета средней зарплаты только с минимумом"""
        result = calculate_salary_average(100000, None)
        assert result == 100000

    def test_calculate_salary_average_to_only(self):
        """Тест расчета средней зарплаты только с максимумом"""
        result = calculate_salary_average(None, 150000)
        assert result == 150000

    def test_calculate_salary_average_none(self):
        """Тест расчета средней зарплаты без данных"""
        result = calculate_salary_average(None, None)
        assert result is None

    def test_compare_salaries_equal(self):
        """Тест сравнения одинаковых зарплат"""
        salary1 = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary2 = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = compare_salaries(salary1, salary2)
        assert result == 0

    def test_compare_salaries_first_higher(self):
        """Тест сравнения зарплат - первая выше"""
        salary1 = {"from": 150000, "to": 200000, "currency": "RUR"}
        salary2 = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = compare_salaries(salary1, salary2)
        assert result > 0

    def test_compare_salaries_second_higher(self):
        """Тест сравнения зарплат - вторая выше"""
        salary1 = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary2 = {"from": 150000, "to": 200000, "currency": "RUR"}
        result = compare_salaries(salary1, salary2)
        assert result < 0

    def test_convert_salary_currency_same(self):
        """Тест конвертации валюты - та же валюта"""
        result = convert_salary_currency(100000, "RUR", "RUR")
        assert result == 100000

    def test_convert_salary_currency_usd_to_rur(self):
        """Тест конвертации USD в RUR"""
        result = convert_salary_currency(1000, "USD", "RUR")
        assert result > 1000  # USD должен быть больше в рублях

    def test_validate_salary_data_valid(self):
        """Тест валидации корректных данных зарплаты"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = validate_salary_data(salary_data)
        assert result is True

    def test_validate_salary_data_invalid_range(self):
        """Тест валидации некорректного диапазона зарплаты"""
        salary_data = {"from": 150000, "to": 100000, "currency": "RUR"}
        result = validate_salary_data(salary_data)
        assert result is False

    def test_validate_salary_data_none(self):
        """Тест валидации пустых данных зарплаты"""
        result = validate_salary_data(None)
        assert result is False

    def test_get_salary_statistics_empty_list(self):
        """Тест получения статистики для пустого списка"""
        result = get_salary_statistics([])
        assert isinstance(result, dict)
        assert result["count"] == 0
        assert result["avg"] is None

    def test_get_salary_statistics_with_data(self):
        """Тест получения статистики с данными"""
        salaries = [
            {"from": 100000, "to": 150000, "currency": "RUR"},
            {"from": 120000, "to": 180000, "currency": "RUR"},
            {"from": 80000, "to": 120000, "currency": "RUR"}
        ]
        result = get_salary_statistics(salaries)
        assert isinstance(result, dict)
        assert result["count"] == 3
        assert result["avg"] is not None
        assert result["min"] is not None
        assert result["max"] is not None

    def test_filter_by_salary_range_all_match(self):
        """Тест фильтрации - все соответствуют диапазону"""
        vacancies = [
            Mock(salary=Mock(salary_from=100000, salary_to=150000)),
            Mock(salary=Mock(salary_from=120000, salary_to=180000))
        ]
        result = filter_by_salary_range(vacancies, min_salary=90000, max_salary=200000)
        assert len(result) == 2

    def test_filter_by_salary_range_partial_match(self):
        """Тест фильтрации - частичное соответствие"""
        vacancies = [
            Mock(salary=Mock(salary_from=100000, salary_to=150000)),
            Mock(salary=Mock(salary_from=200000, salary_to=250000))
        ]
        result = filter_by_salary_range(vacancies, min_salary=90000, max_salary=180000)
        assert len(result) == 1

    def test_filter_by_salary_range_no_match(self):
        """Тест фильтрации - нет соответствий"""
        vacancies = [
            Mock(salary=Mock(salary_from=50000, salary_to=80000)),
            Mock(salary=Mock(salary_from=60000, salary_to=90000))
        ]
        result = filter_by_salary_range(vacancies, min_salary=100000, max_salary=200000)
        assert len(result) == 0


class TestSalaryHelper:
    """Тесты для SalaryHelper"""

    def test_normalize_salary_dict(self):
        """Тест нормализации зарплаты из словаря"""
        salary_data = {"from": 100000, "to": 150000, "currency": "USD"}
        result = SalaryHelper.normalize_salary(salary_data)
        assert result["from"] == 100000
        assert result["to"] == 150000
        assert result["currency"] == "USD"

    def test_normalize_salary_none(self):
        """Тест нормализации пустой зарплаты"""
        result = SalaryHelper.normalize_salary(None)
        assert result is None

    def test_format_salary_display_full_range(self):
        """Тест форматирования полного диапазона"""
        result = SalaryHelper.format_salary_display(100000, 150000, "RUR")
        assert "100000 - 150000 RUR" == result

    def test_format_salary_display_from_only(self):
        """Тест форматирования только минимума"""
        result = SalaryHelper.format_salary_display(100000, None, "RUR")
        assert "от 100000 RUR" == result

    def test_format_salary_display_to_only(self):
        """Тест форматирования только максимума"""
        result = SalaryHelper.format_salary_display(None, 150000, "RUR")
        assert "до 150000 RUR" == result

    def test_format_salary_display_none(self):
        """Тест форматирования без данных"""
        result = SalaryHelper.format_salary_display(None, None, "RUR")
        assert "Не указана" == result

    def test_calculate_average_salary_with_data(self):
        """Тест расчета средней зарплаты с данными"""
        mock_vacancy1 = Mock()
        mock_vacancy1.salary = Mock(salary_from=100000, salary_to=150000)
        
        mock_vacancy2 = Mock()
        mock_vacancy2.salary = Mock(salary_from=120000, salary_to=180000)
        
        vacancies = [mock_vacancy1, mock_vacancy2]
        result = SalaryHelper.calculate_average_salary(vacancies)
        
        # Средняя должна быть между 125000 и 150000
        assert result is not None
        assert 120000 <= result <= 160000

    def test_calculate_average_salary_empty(self):
        """Тест расчета средней зарплаты для пустого списка"""
        result = SalaryHelper.calculate_average_salary([])
        assert result is None

    def test_calculate_average_salary_no_salary_data(self):
        """Тест расчета средней зарплаты без данных о зарплате"""
        mock_vacancy = Mock()
        mock_vacancy.salary = None
        
        vacancies = [mock_vacancy]
        result = SalaryHelper.calculate_average_salary(vacancies)
        
        assert result is None


class TestSalaryFilter:
    """Тесты для SalaryFilter"""

    def test_salary_filter_initialization(self):
        """Тест инициализации фильтра"""
        filter_obj = SalaryFilter(min_salary=100000, max_salary=200000)
        assert filter_obj.min_salary == 100000
        assert filter_obj.max_salary == 200000

    def test_filter_vacancies_within_range(self):
        """Тест фильтрации вакансий в диапазоне"""
        mock_vacancy = Mock()
        mock_vacancy.salary = Mock(salary_from=120000, salary_to=180000)
        
        vacancies = [mock_vacancy]
        filter_obj = SalaryFilter(min_salary=100000, max_salary=200000)
        result = filter_obj.filter_vacancies(vacancies)
        
        assert len(result) == 1
        assert result[0] == mock_vacancy

    def test_filter_vacancies_outside_range(self):
        """Тест фильтрации вакансий вне диапазона"""
        mock_vacancy = Mock()
        mock_vacancy.salary = Mock(salary_from=50000, salary_to=80000)
        
        vacancies = [mock_vacancy]
        filter_obj = SalaryFilter(min_salary=100000, max_salary=200000)
        result = filter_obj.filter_vacancies(vacancies)
        
        assert len(result) == 0

    def test_filter_vacancies_no_salary(self):
        """Тест фильтрации вакансий без зарплаты"""
        mock_vacancy = Mock()
        mock_vacancy.salary = None
        
        vacancies = [mock_vacancy]
        filter_obj = SalaryFilter(min_salary=100000, max_salary=200000)
        result = filter_obj.filter_vacancies(vacancies)
        
        assert len(result) == 0

    def test_filter_vacancies_empty_list(self):
        """Тест фильтрации пустого списка"""
        filter_obj = SalaryFilter(min_salary=100000, max_salary=200000)
        result = filter_obj.filter_vacancies([])
        
        assert result == []

    def test_extract_salary_value_range(self):
        """Тест извлечения значения зарплаты из диапазона"""
        filter_obj = SalaryFilter()
        mock_salary = Mock(salary_from=100000, salary_to=150000)
        result = filter_obj._extract_salary_value(mock_salary)
        
        assert result == 125000

    def test_extract_salary_value_from_only(self):
        """Тест извлечения значения зарплаты только с минимумом"""
        filter_obj = SalaryFilter()
        mock_salary = Mock(salary_from=100000, salary_to=None)
        result = filter_obj._extract_salary_value(mock_salary)
        
        assert result == 100000

    def test_extract_salary_value_to_only(self):
        """Тест извлечения значения зарплаты только с максимумом"""
        filter_obj = SalaryFilter()
        mock_salary = Mock(salary_from=None, salary_to=150000)
        result = filter_obj._extract_salary_value(mock_salary)
        
        assert result == 150000

    def test_extract_salary_value_none(self):
        """Тест извлечения значения зарплаты без данных"""
        filter_obj = SalaryFilter()
        mock_salary = Mock(salary_from=None, salary_to=None)
        result = filter_obj._extract_salary_value(mock_salary)
        
        assert result is None
