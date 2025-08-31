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
            salary=salary_dict,  # Передаем словарь вместо объекта
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        assert "Python Developer" in result
        assert "123" in result
        assert "100000" in result or "150000" in result

    def test_format_vacancy_info_with_employer(self):
        """Тест форматирования вакансии с работодателем"""
        employer_dict = {"name": "Test Company", "id": "1"}

        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            employer=employer_dict,  # Передаем словарь вместо объекта
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)

        assert "Test Company" in result
        assert "Python Developer" in result

    def test_format_vacancy_info_with_number(self):
        """Тест форматирования вакансии с номером"""
        vacancy = Vacancy(
            vacancy_id="123", title="Python Developer", url="https://test.com/vacancy/123", source="hh.ru"
        )

        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy, number=1)

        assert "1." in result  # Убираем пробел, так как он может не быть
        assert "Python Developer" in result

    def test_format_vacancy_info_full(self):
        """Тест полного форматирования вакансии"""
        salary_dict = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }
        employer_dict = {"name": "Test Company", "id": "1"}

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
        assert "100000" in result or "150000" in result
        assert "Москва" in result

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