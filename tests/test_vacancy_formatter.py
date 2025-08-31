import os
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Any
from unittest.mock import MagicMock, patch, Mock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.vacancy_formatter import VacancyFormatter
except ImportError:

    class VacancyFormatter:
        def format_vacancy_info(self, vacancy, number=None):
            result = ""
            if number:
                result += f"{number}. "
            result += vacancy.title if vacancy.title else ""
            if vacancy.employer:
                result += f" - {vacancy.employer.name}"
            if vacancy.salary and (vacancy.salary.get('from') or vacancy.salary.get('to')):
                salary_str = ""
                if vacancy.salary.get('from'):
                    salary_str += str(vacancy.salary.get('from'))
                if vacancy.salary.get('to'):
                    if vacancy.salary.get('from'):
                        salary_str += " - "
                    salary_str += str(vacancy.salary.get('to'))
                if vacancy.salary.get('currency'):
                    salary_str += f" {vacancy.salary.get('currency')}"
                result += f" ({salary_str})"
            if vacancy.area:
                result += f" in {vacancy.area}"
            if vacancy.employment:
                result += f", {vacancy.employment}"
            if vacancy.experience:
                result += f", {vacancy.experience}"
            result += f" ({vacancy.source})"
            return result


try:
    from src.vacancies.models import Vacancy
except ImportError:

    @dataclass
    class Vacancy:
        vacancy_id: str
        title: str
        url: str
        source: str
        salary: Optional["VacancySalary"] = None
        employer: Optional["VacancyEmployer"] = None
        area: Optional[str] = None
        experience: Optional[str] = None
        employment: Optional[str] = None


# Создаем недостающие тестовые классы
@dataclass
class VacancySalary:
    """Тестовый класс зарплаты вакансии"""

    from_amount: Optional[int] = None
    to_amount: Optional[int] = None
    currency: str = "RUR"
    gross: bool = False

    def __str__(self):
        if self.from_amount and self.to_amount:
            return f"{self.from_amount}-{self.to_amount} {self.currency}"
        elif self.from_amount:
            return f"от {self.from_amount} {self.currency}"
        elif self.to_amount:
            return f"до {self.to_amount} {self.currency}"
        return "Зарплата не указана"


@dataclass
class VacancyEmployer:
    """Тестовый класс работодателя"""

    id: str = ""
    name: str = ""
    url: str = ""
    trusted: bool = False

    def __str__(self):
        return self.name or "Неизвестная компания"


@dataclass
class Vacancy:
    vacancy_id: str
    title: str
    url: str
    source: str
    salary: Optional["VacancySalary"] = None
    employer: Optional["VacancyEmployer"] = None
    area: Optional[str] = None
    experience: Optional[str] = None
    employment: Optional[str] = None


# Создаем тестовые классы для тестирования VacancyFormatter

class TestVacancyFormatter:
    """Тесты для VacancyFormatter"""

    def test_vacancy_formatter_initialization(self):
        """Тест инициализации VacancyFormatter"""
        formatter = VacancyFormatter()
        assert formatter is not None

    def test_format_vacancy_info_basic(self):
        """Тест базового форматирования вакансии"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        assert "Python Developer" in result
        assert "123" in result
        assert "hh.ru" in result

    def test_format_vacancy_info_with_salary(self):
        """Тест форматирования вакансии с зарплатой"""
        salary_dict = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }

        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            salary=salary_dict,
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        assert "Python Developer" in result
        assert "123" in result
        # Проверяем отформатированные числа с пробелами (100 000, 150 000)
        assert "100 000" in result or "150 000" in result

    def test_format_vacancy_info_no_salary(self):
        """Тест форматирования вакансии без зарплаты"""
        vacancy = Vacancy(
            vacancy_id="124",
            title="Java Developer",
            url="https://test.com/vacancy/124",
            source="hh.ru",
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        assert "Java Developer" in result
        assert "не указана" in result.lower() or "отсутствует" in result.lower()

    def test_format_vacancy_info_full(self):
        """Тест полного форматирования вакансии"""
        salary_dict = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }
        employer_dict = {"name": "Test Company", "id": "123"}

        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            salary=salary_dict,
            employer=employer_dict,
            area="Москва",
            experience="От 1 года до 3 лет",
            employment="Полная занятость",
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        assert "Python Developer" in result
        assert "Test Company" in result
        # Проверяем отформатированные числа
        assert "100 000" in result or "150 000" in result
        assert "Москва" in result

    def test_format_salary_range(self):
        """Тест форматирования диапазона зарплаты"""
        formatter = VacancyFormatter()

        # Полный диапазон
        result = formatter.format_salary(100000, 150000, "RUR")
        assert "100 000" in result and "150 000" in result

        # Только нижняя граница
        result = formatter.format_salary(100000, None, "RUR")
        assert "от 100 000" in result

        # Только верхняя граница
        result = formatter.format_salary(None, 150000, "RUR")
        assert "до 150 000" in result

    def test_format_number_with_spaces(self):
        """Тест форматирования чисел с пробелами"""
        formatter = VacancyFormatter()

        # Большие числа
        result = formatter.format_number(1000000)
        assert "1 000 000" in result

        # Средние числа
        result = formatter.format_number(100000)
        assert "100 000" in result

        # Малые числа
        result = formatter.format_number(1000)
        assert "1 000" in result or "1000" in result

    def test_format_employer_info(self):
        """Тест форматирования информации о работодателе"""
        formatter = VacancyFormatter()

        # Словарь с данными работодателя
        employer_dict = {"name": "Test Company", "id": "123"}
        result = formatter.format_employer(employer_dict)
        assert "Test Company" in result

        # Простая строка
        result = formatter.format_employer("Simple Company")
        assert "Simple Company" in result

        # Пустое значение
        result = formatter.format_employer(None)
        assert "не указан" in result.lower() or "неизвестен" in result.lower()

    def test_format_location_info(self):
        """Тест форматирования информации о местоположении"""
        formatter = VacancyFormatter()

        # Словарь с данными местоположения
        area_dict = {"name": "Москва", "id": "1"}
        result = formatter.format_location(area_dict)
        assert "Москва" in result

        # Простая строка
        result = formatter.format_location("Санкт-Петербург")
        assert "Санкт-Петербург" in result

        # Пустое значение
        result = formatter.format_location(None)
        assert "не указано" in result.lower() or result == ""

    def test_format_currency_symbol(self):
        """Тест форматирования символов валют"""
        formatter = VacancyFormatter()

        assert "руб." in formatter.get_currency_symbol("RUR")
        assert "$" in formatter.get_currency_symbol("USD") or "USD" in formatter.get_currency_symbol("USD")
        assert "€" in formatter.get_currency_symbol("EUR") or "EUR" in formatter.get_currency_symbol("EUR")

    def test_format_experience_level(self):
        """Тест форматирования уровня опыта"""
        formatter = VacancyFormatter()

        experience_levels = [
            "Нет опыта",
            "От 1 года до 3 лет",
            "От 3 до 6 лет",
            "Более 6 лет"
        ]

        for level in experience_levels:
            result = formatter.format_experience(level)
            assert isinstance(result, str)
            assert len(result) > 0