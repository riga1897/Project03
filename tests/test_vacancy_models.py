import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vacancies.models import Vacancy


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


# Создаем тестовые классы для изолированного тестирования
class VacancySalary:
    """Тестовый класс зарплаты вакансии"""

    def __init__(self, from_amount=None, to_amount=None, currency="RUR"):
        self.from_amount = from_amount
        self.to_amount = to_amount
        self.currency = currency

    def __str__(self):
        if self.from_amount and self.to_amount:
            return f"{self.from_amount} - {self.to_amount} {self.currency}"
        elif self.from_amount:
            return f"от {self.from_amount} {self.currency}"
        elif self.to_amount:
            return f"до {self.to_amount} {self.currency}"
        return "Зарплата не указана"


class VacancyEmployer:
    """Тестовый класс работодателя"""

    def __init__(self, id=None, name=None, url=None, trusted=False):
        self.id = id
        self.name = name
        self.url = url
        self.trusted = trusted

    def __str__(self):
        return f"VacancyEmployer(id='{self.id}', name='{self.name}', url={self.url}, trusted={self.trusted})"


class TestVacancySalary:
    """Тесты для VacancySalary"""

    def test_vacancy_salary_initialization(self):
        """Тест инициализации VacancySalary"""
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        assert salary.from_amount == 100000
        assert salary.to_amount == 150000
        assert salary.currency == "RUR"

    def test_vacancy_salary_str_representation(self):
        """Тест строкового представления VacancySalary"""
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        assert "100000" in str(salary)
        assert "150000" in str(salary)


class TestVacancyEmployer:
    """Тесты для VacancyEmployer"""

    def test_vacancy_employer_initialization(self):
        """Тест инициализации VacancyEmployer"""
        employer = VacancyEmployer(id="1", name="Test Company")
        assert employer.id == "1"
        assert employer.name == "Test Company"

    def test_vacancy_employer_str_representation(self):
        """Тест строкового представления VacancyEmployer"""
        employer = VacancyEmployer(id="1", name="Test Company")
        str_repr = str(employer)
        assert "Test Company" in str_repr
        assert "1" in str_repr


class TestVacancy:
    """Тесты для Vacancy"""

    def test_vacancy_initialization(self):
        """Тест инициализации Vacancy"""
        vacancy = Vacancy(
            title="Python Developer",
            url="https://test.com/vacancy/123",
            vacancy_id="123",
            source="hh.ru",
            description="Test description",
        )

        assert vacancy.vacancy_id == "123"
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://test.com/vacancy/123"
        assert vacancy.source == "hh.ru"
        assert vacancy.description == "Test description"

    def test_vacancy_with_salary(self):
        """Тест вакансии с зарплатой"""
        salary_dict = {"from": 100000, "to": 150000, "currency": "RUR"}
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            salary=salary_dict,
            source="hh.ru",
        )

        assert vacancy.vacancy_id == "123"
        assert vacancy.title == "Python Developer"
        assert vacancy.salary is not None

    def test_vacancy_with_employer(self):
        """Тест вакансии с работодателем"""
        employer_dict = {"id": "1", "name": "Test Company"}
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            employer=employer_dict,
            description="Test description",
            source="hh.ru",
        )

        assert vacancy.vacancy_id == "123"
        assert vacancy.title == "Python Developer"

    def test_vacancy_str_representation(self):
        """Тест строкового представления Vacancy"""
        vacancy = Vacancy(
            vacancy_id="123", title="Python Developer", url="https://test.com/vacancy/123", source="hh.ru"
        )
        # Устанавливаем работодателя после создания
        vacancy.employer = {"name": "Test Company"}
        str_repr = str(vacancy)
        assert "Python Developer" in str_repr
        assert "123" in str_repr
        assert "Test Company" in str_repr
        assert "hh.ru" in str_repr

    # Mock data for hh.ru
    @pytest.fixture
    def mock_vacancy_data_hh(self):
        return {
            "id": "123456",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/123456",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR", "gross": False},
            "employer": {"id": "1", "name": "Test Company HH", "url": "https://hh.ru/employer/1", "trusted": True},
            "snippet": {"requirement": "Experience with Python"},
        }

    # Mock data for SuperJob
    @pytest.fixture
    def mock_vacancy_data_sj(self):
        return {
            "id": 789012,
            "profession": "Java Developer",
            "firm_name": "Another Company SJ",
            "payment_from": 120000,
            "payment_to": 180000,
            "currency": "rub",
            "town": {"title": "Санкт-Петербург"},
            "link": "https://superjob.ru/vacancy/789012",
            "description": "<p>Java developer position</p>",
        }

    def test_vacancy_from_dict_hh(self, mock_vacancy_data_hh):
        """Тест создания вакансии из словаря HH"""
        # Тестируем метод from_dict
        vacancy = Vacancy.from_dict(mock_vacancy_data_hh)

        assert vacancy.vacancy_id == "123456"
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://hh.ru/vacancy/123456"
        assert vacancy.source == "hh.ru"

    def test_vacancy_from_dict_sj(self, mock_vacancy_data_sj):
        """Тест создания вакансии из словаря SuperJob"""
        # Тестируем метод from_dict для SuperJob
        vacancy = Vacancy.from_dict(mock_vacancy_data_sj)

        assert vacancy.vacancy_id == "789012"
        assert vacancy.title == "Java Developer"
        assert vacancy.url == "https://superjob.ru/vacancy/789012"
        assert vacancy.source == "superjob.ru"

    def test_vacancy_comparison(self):
        """Тест сравнения вакансий"""
        vacancy1 = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
        )

        vacancy2 = Vacancy(
            vacancy_id="124",
            title="Java Developer",
            url="https://test.com/vacancy/124",
            source="hh.ru",
        )

        # Проверяем операторы сравнения
        assert vacancy1 != vacancy2
        assert vacancy1 == vacancy1

    def test_vacancy_to_dict(self):
        """Тест преобразования вакансии в словарь"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
        )

        result = vacancy.to_dict()

        assert result["vacancy_id"] == "123"
        assert result["title"] == "Python Developer"
        assert result["url"] == "https://test.com/vacancy/123"
        assert result["source"] == "hh.ru"