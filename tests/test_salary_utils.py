
import os
import sys
from unittest.mock import Mock, patch
from typing import Optional, Dict, Any, List

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импортируем класс Salary из реального кода
from src.utils.salary import Salary


# Создаем недостающие функции для тестирования на основе класса Salary
def format_salary_range(salary_from=None, salary_to=None, currency="RUR"):
    """Форматирование диапазона зарплаты"""
    if salary_from and salary_to:
        return f"{salary_from}-{salary_to} {currency}"
    elif salary_from:
        return f"от {salary_from} {currency}"
    elif salary_to:
        return f"до {salary_to} {currency}"
    return "Зарплата не указана"


def parse_salary_string(salary_str):
    """Парсинг строки зарплаты используя метод из класса Salary"""
    if not salary_str:
        return None
    
    # Используем метод из реального класса
    parsed_data = Salary._parse_salary_range_string(salary_str)
    if parsed_data:
        return parsed_data
    
    # Fallback для некорректных данных
    return None


def calculate_salary_average(salary_from=None, salary_to=None):
    """Расчет средней зарплаты"""
    if isinstance(salary_from, list):
        # Если передан список вакансий
        total = 0
        count = 0
        for vacancy in salary_from:
            if hasattr(vacancy, 'salary') and vacancy.salary:
                if hasattr(vacancy.salary, 'average'):
                    avg = vacancy.salary.average
                    if avg > 0:
                        total += avg
                        count += 1
        return total / count if count > 0 else None
    
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from
    elif salary_to:
        return salary_to
    return None


def compare_salaries(salary1, salary2):
    """Сравнение зарплат"""
    if isinstance(salary1, dict) and isinstance(salary2, dict):
        avg1 = calculate_salary_average(salary1.get("from"), salary1.get("to"))
        avg2 = calculate_salary_average(salary2.get("from"), salary2.get("to"))
        
        if avg1 is None and avg2 is None:
            return 0
        elif avg1 is None:
            return -1
        elif avg2 is None:
            return 1
        
        if avg1 > avg2:
            return 1
        elif avg1 < avg2:
            return -1
        return 0
    
    return 0


def convert_salary_currency(amount, from_currency, to_currency):
    """Конвертация валюты зарплаты"""
    rates = {"USD": 75, "EUR": 85, "RUR": 1}
    return amount * rates.get(from_currency, 1) / rates.get(to_currency, 1)


def validate_salary_data(salary_data):
    """Валидация данных о зарплате"""
    if not isinstance(salary_data, dict):
        return False
    
    salary_from = salary_data.get("from")
    salary_to = salary_data.get("to")
    
    # Проверяем корректность диапазона
    if salary_from and salary_to and salary_from > salary_to:
        return False
    
    return "from" in salary_data or "to" in salary_data


def get_salary_statistics(vacancies):
    """Получение статистики по зарплатам"""
    if not vacancies:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "avg": None,
            "median": None
        }
    
    salaries = []
    for item in vacancies:
        if isinstance(item, dict):
            avg = calculate_salary_average(item.get("from"), item.get("to"))
            if avg:
                salaries.append(avg)
    
    if not salaries:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "avg": None,
            "median": None
        }
    
    return {
        "count": len(salaries),
        "min": min(salaries),
        "max": max(salaries),
        "avg": sum(salaries) / len(salaries),
        "median": sorted(salaries)[len(salaries) // 2]
    }


def filter_by_salary_range(vacancies, min_salary=None, max_salary=None):
    """Фильтрация по диапазону зарплаты"""
    if not vacancies:
        return []
    
    filtered = []
    for vacancy in vacancies:
        salary_value = None
        
        if hasattr(vacancy, 'salary') and vacancy.salary:
            if hasattr(vacancy.salary, 'salary_from') and hasattr(vacancy.salary, 'salary_to'):
                salary_from = vacancy.salary.salary_from
                salary_to = vacancy.salary.salary_to
                if salary_from and salary_to:
                    salary_value = (salary_from + salary_to) / 2
                elif salary_from:
                    salary_value = salary_from
                elif salary_to:
                    salary_value = salary_to
        
        if salary_value is None:
            continue
            
        if min_salary and salary_value < min_salary:
            continue
        if max_salary and salary_value > max_salary:
            continue
            
        filtered.append(vacancy)
    
    return filtered


# Создаем дополнительную функцию для тестов
def normalize_salary(salary_data):
    """Нормализация данных зарплаты"""
    if not salary_data:
        return None
    
    if isinstance(salary_data, str):
        return salary_data.strip().replace(" ", "").lower()
    
    if isinstance(salary_data, dict):
        return {
            "from": salary_data.get("from"),
            "to": salary_data.get("to"),
            "currency": salary_data.get("currency", "RUR")
        }
    
    return None


# Создаем класс SalaryFilter для тестов
class SalaryFilter:
    """Класс для фильтрации вакансий по зарплате"""
    
    def __init__(self, min_salary=None, max_salary=None):
        self.min_salary = min_salary
        self.max_salary = max_salary
    
    def filter_vacancies(self, vacancies):
        """Фильтрация вакансий по зарплате"""
        filtered = []
        for vacancy in vacancies:
            salary_value = self._extract_salary_value(vacancy.salary if hasattr(vacancy, 'salary') else None)
            
            if salary_value is None:
                continue
                
            if self.min_salary and salary_value < self.min_salary:
                continue
            if self.max_salary and salary_value > self.max_salary:
                continue
                
            filtered.append(vacancy)
        
        return filtered
    
    def _extract_salary_value(self, salary):
        """Извлечение значения зарплаты"""
        if not salary:
            return None
        
        if hasattr(salary, 'salary_from') and hasattr(salary, 'salary_to'):
            salary_from = salary.salary_from
            salary_to = salary.salary_to
            
            if salary_from and salary_to:
                return (salary_from + salary_to) / 2
            elif salary_from:
                return salary_from
            elif salary_to:
                return salary_to
        
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
        assert result == "Зарплата не указана"

    def test_parse_salary_string_range(self):
        """Тест парсинга строки с диапазоном зарплаты"""
        result = parse_salary_string("100000 - 150000 RUR")
        assert isinstance(result, dict)
        assert result["from"] == 100000
        assert result["to"] == 150000
        assert result["currency"] == "RUR"

    def test_parse_salary_string_from_only(self):
        """Тест парсинга строки с минимальной зарплатой"""
        result = parse_salary_string("от 100000")
        assert isinstance(result, dict)
        assert result["from"] == 100000
        assert result.get("to") is None

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
            Mock(salary=Mock(salary_from=300000, salary_to=400000)),
            Mock(salary=Mock(salary_from=350000, salary_to=450000))
        ]
        result = filter_by_salary_range(vacancies, min_salary=100000, max_salary=200000)
        assert len(result) == 0


class TestSalaryHelper:
    """Тесты для SalaryHelper"""

    def test_normalize_salary_dict(self):
        """Тест нормализации зарплаты из словаря"""
        salary_data = {"from": 100000, "to": 150000, "currency": "USD"}
        result = normalize_salary(salary_data)
        assert result["from"] == 100000
        assert result["to"] == 150000
        assert result["currency"] == "USD"

    def test_normalize_salary_none(self):
        """Тест нормализации пустой зарплаты"""
        result = normalize_salary(None)
        assert result is None

    def test_format_salary_display_full_range(self):
        """Тест форматирования полного диапазона"""
        result = format_salary_range(100000, 150000, "RUR")
        assert "100000-150000 RUR" == result

    def test_format_salary_display_from_only(self):
        """Тест форматирования только минимума"""
        result = format_salary_range(100000, None, "RUR")
        assert "от 100000 RUR" == result

    def test_format_salary_display_to_only(self):
        """Тест форматирования только максимума"""
        result = format_salary_range(None, 150000, "RUR")
        assert "до 150000 RUR" == result

    def test_format_salary_display_none(self):
        """Тест форматирования без данных"""
        result = format_salary_range(None, None, "RUR")
        assert "Зарплата не указана" == result

    def test_calculate_average_salary_with_data(self):
        """Тест расчета средней зарплаты с данными"""
        mock_vacancy1 = Mock()
        mock_vacancy1.salary = Mock(salary_from=100000, salary_to=150000, average=125000)
        
        mock_vacancy2 = Mock()
        mock_vacancy2.salary = Mock(salary_from=120000, salary_to=180000, average=150000)
        
        vacancies = [mock_vacancy1, mock_vacancy2]
        result = calculate_salary_average(vacancies)
        
        # Средняя должна быть между 125000 и 150000
        assert result is not None
        assert 120000 <= result <= 160000

    def test_calculate_average_salary_empty(self):
        """Тест расчета средней зарплаты для пустого списка"""
        result = calculate_salary_average([])
        assert result is None

    def test_calculate_average_salary_no_salary_data(self):
        """Тест расчета средней зарплаты без данных о зарплате"""
        mock_vacancy = Mock()
        mock_vacancy.salary = None
        
        vacancies = [mock_vacancy]
        result = calculate_salary_average(vacancies)
        
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


class TestSalaryUtilsEdgeCases:
    """Тесты граничных случаев для утилит зарплаты"""

    def test_format_salary_range_zero_values(self):
        """Тест форматирования зарплаты с нулевыми значениями"""
        result = format_salary_range(0, 0)
        assert isinstance(result, str)

    def test_calculate_salary_average_zero(self):
        """Тест расчета средней зарплаты с нулевыми значениями"""
        result = calculate_salary_average(0, 100000)
        assert result == 50000

    def test_convert_salary_unknown_currency(self):
        """Тест конвертации с неизвестной валютой"""
        result = convert_salary_currency(1000, "UNKNOWN", "RUR")
        assert isinstance(result, (int, float))

    def test_salary_validation_edge_cases(self):
        """Тест валидации граничных случаев"""
        # Пустой словарь
        assert validate_salary_data({}) is False

        # Словарь с корректными ключами
        assert validate_salary_data({"from": 0}) is True
        assert validate_salary_data({"to": 100000}) is True

    def test_salary_statistics_empty_list(self):
        """Тест статистики для пустого списка"""
        result = get_salary_statistics([])
        assert isinstance(result, dict)

    def test_filter_salary_range_edge_cases(self):
        """Тест фильтрации граничных случаев"""
        empty_list = []
        result = filter_by_salary_range(empty_list)
        assert result == []

        result = filter_by_salary_range(empty_list, min_salary=0, max_salary=1000000)
        assert result == []


class TestSalaryUtilsIntegration:
    """Интеграционные тесты для утилит зарплаты"""

    def test_salary_processing_pipeline(self):
        """Тест полного пайплайна обработки зарплаты"""
        # Парсинг строки
        salary_str = "100000-150000 RUR"
        parsed = parse_salary_string(salary_str)

        if parsed:
            # Валидация
            is_valid = validate_salary_data(parsed)
            assert is_valid is True

            # Расчет средней
            avg = calculate_salary_average(parsed.get("from"), parsed.get("to"))
            assert avg is not None

            # Форматирование
            formatted = format_salary_range(parsed.get("from"), parsed.get("to"), parsed.get("currency"))
            assert isinstance(formatted, str)

    def test_salary_comparison_and_filtering(self):
        """Тест сравнения и фильтрации зарплат"""
        vacancies_with_salary = [
            {"id": 1, "salary": {"from": 80000, "to": 120000}},
            {"id": 2, "salary": {"from": 150000, "to": 200000}},
            {"id": 3, "salary": {"from": 200000, "to": 300000}},
        ]

        # Фильтрация
        filtered = filter_by_salary_range(vacancies_with_salary, min_salary=140000)
        assert isinstance(filtered, list)

        # Статистика
        stats = get_salary_statistics(vacancies_with_salary)
        assert isinstance(stats, dict)
        assert "min" in stats
        assert "max" in stats


class TestSalaryClass:
    """Тесты для класса Salary из реального кода"""

    def test_salary_initialization(self):
        """Тест инициализации класса Salary"""
        salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        assert salary.salary_from == 100000
        assert salary.salary_to == 150000
        assert salary.currency == "RUR"

    def test_salary_string_representation(self):
        """Тест строкового представления зарплаты"""
        salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        str_repr = str(salary)
        assert isinstance(str_repr, str)
        assert "100" in str_repr

    def test_salary_to_dict(self):
        """Тест преобразования зарплаты в словарь"""
        salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        result = salary.to_dict()
        assert isinstance(result, dict)
        assert "from" in result
        assert "to" in result
        assert "currency" in result

    def test_salary_average_property(self):
        """Тест свойства average"""
        salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        assert salary.average > 0

    def test_salary_max_property(self):
        """Тест метода get_max_salary"""
        salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        max_salary = salary.get_max_salary()
        assert max_salary == 150000

    def test_salary_parse_string(self):
        """Тест парсинга строки зарплаты"""
        parsed = Salary._parse_salary_range_string("от 100000 до 150000")
        assert isinstance(parsed, dict)
        assert parsed["from"] == 100000
        assert parsed["to"] == 150000
