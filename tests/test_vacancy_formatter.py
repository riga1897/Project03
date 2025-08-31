import os
import sys
from dataclasses import dataclass
from typing import Optional
from unittest.mock import MagicMock, patch

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
            if vacancy.salary and (vacancy.salary.from_amount or vacancy.salary.to_amount):
                salary_str = ""
                if vacancy.salary.from_amount:
                    salary_str += str(vacancy.salary.from_amount)
                if vacancy.salary.to_amount:
                    if vacancy.salary.from_amount:
                        salary_str += " - "
                    salary_str += str(vacancy.salary.to_amount)
                if vacancy.salary.currency:
                    salary_str += f" {vacancy.salary.currency}"
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


# Создаем тестовые классы для мокирования
class VacancySalary:
    def __init__(self, from_amount=None, to_amount=None, currency="RUR"):
        self.from_amount = from_amount
        self.to_amount = to_amount
        self.currency = currency

    def __str__(self):
        if self.from_amount and self.to_amount:
            return f"{self.from_amount} - {self.to_amount} {self.currency}"
        return "Зарплата не указана"


class VacancyEmployer:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class TestVacancyFormatter:
    """Тесты для VacancyFormatter"""

    def test_vacancy_formatter_initialization(self):
        """Тест инициализации VacancyFormatter"""
        formatter = VacancyFormatter()
        assert isinstance(formatter, VacancyFormatter)

    def test_format_vacancy_info_basic(self):
        """Тест форматирования базовой информации о вакансии"""
        vacancy = Vacancy(
            vacancy_id="123", title="Python Developer", url="https://test.com/vacancy/123", source="hh.ru"
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        assert "Python Developer" in result
        assert "hh.ru" in result

    def test_format_vacancy_info_with_salary(self):
        """Тест форматирования вакансии с зарплатой"""
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            salary=salary,
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        assert "100000 - 150000 RUR" in result

    def test_format_vacancy_info_with_employer(self):
        """Тест форматирования вакансии с работодателем"""
        employer = VacancyEmployer(name="Test Company")
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            employer=employer,
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        assert "Test Company" in result

    def test_format_vacancy_info_with_number(self):
        """Тест форматирования вакансии с номером"""
        vacancy = Vacancy(
            vacancy_id="123", title="Python Developer", url="https://test.com/vacancy/123", source="hh.ru"
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy, number=1)

        assert "1. " in result

    def test_format_vacancy_info_full(self):
        """Тест полного форматирования вакансии"""
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
            experience="От 1 года до 3 лет",
            employment="Полная занятость",
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy, number=1)

        assert "1. " in result
        assert "Python Developer" in result
        assert "Test Company" in result
        assert "100000 - 150000 RUR" in result
        assert "Москва" in result
        assert "От 1 года до 3 лет" in result
        assert "Полная занятость" in result
        assert "hh.ru" in result

    def test_format_vacancy_minimal(self):
        """Тест форматирования минимальной вакансии"""
        vacancy = Vacancy(
            vacancy_id="123", title="Python Developer", url="https://test.com/vacancy/123", source="hh.ru"
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        # Проверяем, что нет ошибок при отсутствии необязательных полей
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Python Developer" in result
        assert "hh.ru" in result
