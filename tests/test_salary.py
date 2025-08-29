"""
Тесты для модуля salary
"""

import pytest

from src.utils.salary import Salary


class TestSalary:
    """Тесты для класса Salary"""

    def test_salary_initialization_with_range(self):
        """Тест инициализации зарплаты с диапазоном"""
        salary = Salary(100000, 150000, "RUR")
        assert salary.salary_from == 100000
        assert salary.salary_to == 150000
        assert salary.currency == "RUR"

    def test_salary_initialization_from_only(self):
        """Тест инициализации зарплаты только с минимумом"""
        salary = Salary(80000, currency="RUR")
        assert salary.salary_from == 80000
        assert salary.salary_to is None
        assert salary.currency == "RUR"

    def test_salary_initialization_to_only(self):
        """Тест инициализации зарплаты только с максимумом"""
        salary = Salary(salary_to=200000, currency="USD")
        assert salary.salary_from is None
        assert salary.salary_to == 200000
        assert salary.currency == "USD"

    def test_salary_initialization_none_values(self):
        """Тест инициализации зарплаты с None значениями"""
        salary = Salary(None, None, None)
        assert salary.salary_from is None
        assert salary.salary_to is None
        assert salary.currency is None

    def test_salary_from_dict_complete(self):
        """Тест создания зарплаты из полного словаря"""
        salary_dict = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary.from_dict(salary_dict)
        assert salary.salary_from == 100000
        assert salary.salary_to == 150000
        assert salary.currency == "RUR"

    def test_salary_from_dict_partial(self):
        """Тест создания зарплаты из частичного словаря"""
        salary_dict = {"from": 80000, "currency": "USD"}
        salary = Salary.from_dict(salary_dict)
        assert salary.salary_from == 80000
        assert salary.salary_to is None
        assert salary.currency == "USD"

    def test_salary_from_dict_none(self):
        """Тест создания зарплаты из None"""
        salary = Salary.from_dict(None)
        assert salary.salary_from is None
        assert salary.salary_to is None
        assert salary.currency is None

    def test_salary_from_dict_empty(self):
        """Тест создания зарплаты из пустого словаря"""
        salary = Salary.from_dict({})
        assert salary.salary_from is None
        assert salary.salary_to is None
        assert salary.currency is None

    def test_salary_to_dict(self):
        """Тест преобразования зарплаты в словарь"""
        salary = Salary(100000, 150000, "RUR")
        salary_dict = salary.to_dict()
        assert salary_dict["from"] == 100000
        assert salary_dict["to"] == 150000
        assert salary_dict["currency"] == "RUR"

    def test_salary_to_dict_partial(self):
        """Тест преобразования частичной зарплаты в словарь"""
        salary = Salary(80000, currency="USD")
        salary_dict = salary.to_dict()
        assert salary_dict["from"] == 80000
        assert salary_dict["to"] is None
        assert salary_dict["currency"] == "USD"

    def test_salary_average_with_both_values(self):
        """Тест расчета средней зарплаты при наличии обоих значений"""
        salary = Salary(100000, 150000, "RUR")
        assert salary.get_average() == 125000

    def test_salary_average_from_only(self):
        """Тест расчета средней зарплаты при наличии только минимума"""
        salary = Salary(100000, currency="RUR")
        assert salary.get_average() == 100000

    def test_salary_average_to_only(self):
        """Тест расчета средней зарплаты при наличии только максимума"""
        salary = Salary(salary_to=150000, currency="RUR")
        assert salary.get_average() == 150000

    def test_salary_average_none_values(self):
        """Тест расчета средней зарплаты при отсутствии значений"""
        salary = Salary(None, None, "RUR")
        assert salary.get_average() is None

    def test_salary_comparison_greater(self):
        """Тест сравнения зарплат - больше"""
        salary1 = Salary(150000, 200000, "RUR")
        salary2 = Salary(100000, 150000, "RUR")
        assert salary1 > salary2

    def test_salary_comparison_less(self):
        """Тест сравнения зарплат - меньше"""
        salary1 = Salary(100000, 150000, "RUR")
        salary2 = Salary(150000, 200000, "RUR")
        assert salary1 < salary2

    def test_salary_comparison_equal(self):
        """Тест сравнения зарплат - равно"""
        salary1 = Salary(100000, 150000, "RUR")
        salary2 = Salary(100000, 150000, "RUR")
        assert salary1 == salary2

    def test_salary_comparison_with_none(self):
        """Тест сравнения зарплат с None значениями"""
        salary1 = Salary(100000, 150000, "RUR")
        salary2 = Salary(None, None, "RUR")
        assert salary1 > salary2
        assert not (salary1 < salary2)
        assert not (salary1 == salary2)

    def test_salary_string_representation_full(self):
        """Тест строкового представления полной зарплаты"""
        salary = Salary(100000, 150000, "RUR")
        result = str(salary)
        assert "100000" in result
        assert "150000" in result
        assert "RUR" in result

    def test_salary_string_representation_from_only(self):
        """Тест строкового представления зарплаты только с минимумом"""
        salary = Salary(100000, currency="RUR")
        result = str(salary)
        assert "100000" in result
        assert "RUR" in result

    def test_salary_string_representation_none(self):
        """Тест строкового представления зарплаты с None значениями"""
        salary = Salary(None, None, None)
        result = str(salary)
        assert "указана" in result.lower() or "не указана" in result.lower()

    def test_salary_is_specified(self):
        """Тест проверки указана ли зарплата"""
        salary1 = Salary(100000, 150000, "RUR")
        salary2 = Salary(100000, currency="RUR")
        salary3 = Salary(None, None, None)

        assert salary1.is_specified() is True
        assert salary2.is_specified() is True
        assert salary3.is_specified() is False

    def test_salary_currency_conversion(self):
        """Тест конвертации валют (если поддерживается)"""
        salary = Salary(1000, 2000, "USD")
        # Если есть метод конвертации
        if hasattr(salary, "convert_to_rub"):
            converted = salary.convert_to_rub()
            assert converted.currency == "RUR"
            assert converted.salary_from > salary.salary_from
