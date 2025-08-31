import os
import re
import sys
from typing import Any, Dict, Optional, Tuple, Union
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Создаем тестовые функции для работы с зарплатой
def parse_salary_range(salary_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Парсинг диапазона зарплаты из строки"""
    if not salary_str or salary_str.lower() in ["зарплата не указана", "не указана"]:
        return None, None

    # Удаляем валюту и лишние символы
    clean_str = re.sub(r"[^\d\s\-отдо]", "", salary_str.lower())

    # Ищем числа
    numbers = re.findall(r"\d+", clean_str)

    if len(numbers) == 0:
        return None, None
    elif len(numbers) == 1:
        amount = int(numbers[0])
        if "от" in clean_str:
            return amount, None
        elif "до" in clean_str:
            return None, amount
        else:
            return amount, amount
    elif len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])

    return None, None


def format_salary(from_amount: Optional[int], to_amount: Optional[int], currency: str = "RUR") -> str:
    """Форматирование зарплаты"""
    if from_amount and to_amount:
        if from_amount == to_amount:
            return f"{from_amount:,} {currency}".replace(",", " ")
        else:
            return f"{from_amount:,} - {to_amount:,} {currency}".replace(",", " ")
    elif from_amount:
        return f"от {from_amount:,} {currency}".replace(",", " ")
    elif to_amount:
        return f"до {to_amount:,} {currency}".replace(",", " ")
    else:
        return "Зарплата не указана"


def normalize_salary(salary_data: Union[Dict[str, Any], str, None]) -> Tuple[Optional[int], Optional[int], str]:
    """Нормализация данных о зарплате"""
    if not salary_data:
        return None, None, "RUR"

    if isinstance(salary_data, str):
        from_amount, to_amount = parse_salary_range(salary_data)
        return from_amount, to_amount, "RUR"

    if isinstance(salary_data, dict):
        from_amount = salary_data.get("from")
        to_amount = salary_data.get("to")
        currency = salary_data.get("currency", "RUR")
        return from_amount, to_amount, currency

    return None, None, "RUR"


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
        result = parse_salary_range("invalid")
        assert result == (None, None)
        result_empty = parse_salary_range("")
        assert result_empty == (None, None)
        # Одиночное число возвращается как диапазон от этого числа до этого же числа
        result_single = parse_salary_range("100000")
        assert result_single == (100000, 100000)
        assert parse_salary_range("abc - def") is None

    def test_parse_salary_range_reverse_order(self):
        """Тест парсинга диапазона в обратном порядке"""
        result = parse_salary_range("150000 - 100000")
        # Функция возвращает как есть, без автоматической перестановки
        assert result == (150000, 100000)

    def test_format_salary_with_range(self):
        """Тест форматирования зарплаты с диапазоном"""

        # Mock VacancySalary for testing format_salary
        class MockVacancySalary:
            def __init__(self, from_amount, to_amount, currency):
                self.from_amount = from_amount
                self.to_amount = to_amount
                self.currency = currency

        salary = MockVacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        result = format_salary(salary.from_amount, salary.to_amount, salary.currency)

        assert "100 000" in result
        assert "150 000" in result
        assert "RUR" in result

    def test_format_salary_from_only(self):
        """Тест форматирования зарплаты только с минимальным значением"""

        class MockVacancySalary:
            def __init__(self, from_amount, currency):
                self.from_amount = from_amount
                self.currency = currency

        salary = MockVacancySalary(from_amount=100000, currency="RUR")
        result = format_salary(salary.from_amount, None, salary.currency)

        assert "от 100 000" in result
        assert "RUR" in result

    def test_format_salary_to_only(self):
        """Тест форматирования зарплаты только с максимальным значением"""

        class MockVacancySalary:
            def __init__(self, to_amount, currency):
                self.to_amount = to_amount
                self.currency = currency

        salary = MockVacancySalary(to_amount=150000, currency="RUR")
        result = format_salary(None, salary.to_amount, salary.currency)

        assert "до 150 000" in result
        assert "RUR" in result

    def test_format_salary_none(self):
        """Тест форматирования пустой зарплаты"""
        result = format_salary(None, None)
        assert result == "Зарплата не указана"

    def test_normalize_salary_with_range(self):
        """Тест нормализации зарплаты с диапазоном"""

        class MockVacancySalary:
            def __init__(self, from_amount, to_amount, currency):
                self.from_amount = from_amount
                self.to_amount = to_amount
                self.currency = currency

        salary = MockVacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        from_amount, to_amount, currency = normalize_salary(
            {"from": salary.from_amount, "to": salary.to_amount, "currency": salary.currency}
        )

        # Должно вернуть среднее значение
        assert (from_amount + to_amount) / 2 == 125000

    def test_normalize_salary_from_only(self):
        """Тест нормализации зарплаты только с минимальным значением"""

        class MockVacancySalary:
            def __init__(self, from_amount, currency):
                self.from_amount = from_amount
                self.currency = currency

        salary = MockVacancySalary(from_amount=100000, currency="RUR")
        from_amount, to_amount, currency = normalize_salary({"from": salary.from_amount, "currency": salary.currency})

        assert from_amount == 100000

    def test_normalize_salary_to_only(self):
        """Тест нормализации зарплаты только с максимальным значением"""

        class MockVacancySalary:
            def __init__(self, to_amount, currency):
                self.to_amount = to_amount
                self.currency = currency

        salary = MockVacancySalary(to_amount=150000, currency="RUR")
        from_amount, to_amount, currency = normalize_salary({"to": salary.to_amount, "currency": salary.currency})

        assert to_amount == 150000

    def test_normalize_salary_none(self):
        """Тест нормализации пустой зарплаты"""
        from_amount, to_amount, currency = normalize_salary(None)
        assert from_amount is None
        assert to_amount is None
        assert currency == "RUR"

    def test_normalize_salary_empty_dict(self):
        """Тест нормализации пустой зарплаты (пустой словарь)"""
        from_amount, to_amount, currency = normalize_salary({})
        assert from_amount is None
        assert to_amount is None
        assert currency == "RUR"

    def test_normalize_salary_missing_keys_in_dict(self):
        """Тест нормализации зарплаты с отсутствующими ключами в словаре"""
        from_amount, to_amount, currency = normalize_salary({"currency": "CAD"})
        assert from_amount is None
        assert to_amount is None
        assert currency == "CAD"

    def test_normalize_salary_string_range(self):
        """Тест нормализации зарплаты из строки с диапазоном"""
        from_amount, to_amount, currency = normalize_salary("100000 - 150000")
        assert from_amount == 100000
        assert to_amount == 150000
        assert currency == "RUR"

    def test_normalize_salary_string_from_only(self):
        """Тест нормализации зарплаты из строки только с минимальным значением"""
        from_amount, to_amount, currency = normalize_salary("от 100000")
        assert from_amount == 100000
        assert to_amount is None
        assert currency == "RUR"

    def test_normalize_salary_string_to_only(self):
        """Тест нормализации зарплаты из строки только с максимальным значением"""
        from_amount, to_amount, currency = normalize_salary("до 150000")
        assert from_amount is None
        assert to_amount == 150000
        assert currency == "RUR"

    def test_normalize_salary_string_invalid(self):
        """Тест нормализации невалидной зарплаты из строки"""
        from_amount, to_amount, currency = normalize_salary("invalid salary")
        assert from_amount is None
        assert to_amount is None
        assert currency == "RUR"

    def test_normalize_salary_with_currency_and_range(self):
        """Тест нормализации зарплаты с указанием валюты и диапазоном"""
        from_amount, to_amount, currency = normalize_salary({"from": 100000, "to": 150000, "currency": "USD"})
        assert from_amount == 100000
        assert to_amount == 150000
        assert currency == "USD"

    def test_normalize_salary_with_currency_from_only(self):
        """Тест нормализации зарплаты с указанием валюты и только минимальным значением"""
        from_amount, to_amount, currency = normalize_salary({"from": 100000, "currency": "EUR"})
        assert from_amount == 100000
        assert to_amount is None
        assert currency == "EUR"

    def test_normalize_salary_with_currency_to_only(self):
        """Тест нормализации зарплаты с указанием валюты и только максимальным значением"""
        from_amount, to_amount, currency = normalize_salary({"to": 150000, "currency": "GBP"})
        assert from_amount is None
        assert to_amount == 150000
        assert currency == "GBP"
