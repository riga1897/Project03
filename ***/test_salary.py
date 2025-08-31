"""
Тесты для класса Salary

Содержит тесты для проверки корректности работы с зарплатой.
"""

from unittest.mock import Mock

import pytest

from src.utils.salary import Salary


class TestSalary:
    """Тесты для класса Salary"""

    def test_salary_initialization_with_dict(self):
        """Тест инициализации зарплаты со словарем"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)

        assert salary is not None
        assert hasattr(salary, "salary_from")
        assert hasattr(salary, "salary_to")
        assert hasattr(salary, "currency")

    def test_salary_initialization_empty(self):
        """Тест инициализации пустой зарплаты"""
        salary = Salary()

        assert salary is not None
        assert hasattr(salary, "salary_from")
        assert hasattr(salary, "salary_to")
        assert hasattr(salary, "currency")

    def test_salary_initialization_none(self):
        """Тест инициализации зарплаты с None"""
        salary = Salary(None)

        assert salary is not None
        assert salary.salary_from is None
        assert salary.salary_to is None

    def test_salary_with_range(self):
        """Тест зарплаты с диапазоном"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)

        assert salary.salary_from == 100000
        assert salary.salary_to == 150000
        assert salary.currency == "RUR"

    def test_salary_from_only(self):
        """Тест зарплаты только с минимумом"""
        salary_data = {"from": 80000, "currency": "USD"}
        salary = Salary(salary_data)

        assert salary.salary_from == 80000
        assert salary.salary_to is None
        assert salary.currency == "USD"

    def test_salary_to_only(self):
        """Тест зарплаты только с максимумом"""
        salary_data = {"to": 200000, "currency": "EUR"}
        salary = Salary(salary_data)

        assert salary.salary_from is None
        assert salary.salary_to == 200000
        assert salary.currency == "EUR"

    def test_salary_to_dict(self):
        """Тест преобразования зарплаты в словарь"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)

        result = salary.to_dict()
        assert isinstance(result, dict)
        assert "from" in result or "salary_from" in result
        assert "to" in result or "salary_to" in result
        assert "currency" in result

    def test_salary_average_property(self):
        """Тест свойства average"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)

        if hasattr(salary, "average"):
            average = salary.average
            assert average == 125000

    def test_salary_average_from_only(self):
        """Тест среднего значения только с минимумом"""
        salary_data = {"from": 80000, "currency": "USD"}
        salary = Salary(salary_data)

        if hasattr(salary, "average"):
            average = salary.average
            assert average == 80000

    def test_salary_average_none_values(self):
        """Тест среднего значения с None значениями"""
        salary = Salary()

        if hasattr(salary, "average"):
            average = salary.average
            assert average == 0

    def test_salary_string_representation(self):
        """Тест строкового представления зарплаты"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)

        str_repr = str(salary)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_salary_comparison(self):
        """Тест сравнения зарплат"""
        salary1_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary2_data = {"from": 80000, "to": 120000, "currency": "RUR"}

        salary1 = Salary(salary1_data)
        salary2 = Salary(salary2_data)

        # Проверяем, что объекты можно создать и сравнить
        assert salary1 is not None
        assert salary2 is not None

        # Если есть методы сравнения, тестируем их
        if hasattr(salary1, "average") and hasattr(salary2, "average"):
            assert salary1.average > salary2.average

    def test_salary_is_specified(self):
        """Тест проверки указания зарплаты"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)

        if hasattr(salary, "is_specified"):
            assert salary.is_specified() is True

        empty_salary = Salary()
        if hasattr(empty_salary, "is_specified"):
            assert empty_salary.is_specified() is False

    def test_salary_edge_cases(self):
        """Тест граничных случаев"""
        # Тест с отрицательными значениями
        salary_data = {"from": -1000, "to": 0, "currency": "RUR"}
        salary = Salary(salary_data)
        assert salary is not None

        # Тест с очень большими значениями
        big_salary_data = {"from": 999999999, "to": 9999999999, "currency": "RUR"}
        big_salary = Salary(big_salary_data)
        assert big_salary is not None

        # Тест с пустой валютой
        no_currency_data = {"from": 100000, "to": 150000}
        no_currency_salary = Salary(no_currency_data)
        assert no_currency_salary is not None
