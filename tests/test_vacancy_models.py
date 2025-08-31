
import pytest
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.vacancies.models import Vacancy, VacancySalary, VacancyEmployer


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
        str_repr = str(salary)
        assert "100000" in str_repr
        assert "150000" in str_repr

    def test_vacancy_salary_only_from(self):
        """Тест зарплаты только с минимальным значением"""
        salary = VacancySalary(from_amount=100000, currency="RUR")
        assert salary.from_amount == 100000
        assert salary.to_amount is None

    def test_vacancy_salary_only_to(self):
        """Тест зарплаты только с максимальным значением"""
        salary = VacancySalary(to_amount=150000, currency="RUR")
        assert salary.from_amount is None
        assert salary.to_amount == 150000

    def test_vacancy_salary_comparison(self):
        """Тест сравнения зарплат"""
        salary1 = VacancySalary(from_amount=100000, to_amount=150000)
        salary2 = VacancySalary(from_amount=100000, to_amount=150000)
        
        assert salary1.from_amount == salary2.from_amount
        assert salary1.to_amount == salary2.to_amount


class TestVacancyEmployer:
    """Тесты для VacancyEmployer"""

    def test_vacancy_employer_initialization(self):
        """Тест инициализации VacancyEmployer"""
        employer = VacancyEmployer(name="Test Company", url="https://test.com")
        assert employer.name == "Test Company"
        assert employer.url == "https://test.com"

    def test_vacancy_employer_str_representation(self):
        """Тест строкового представления VacancyEmployer"""
        employer = VacancyEmployer(name="Test Company")
        assert str(employer) == "Test Company"

    def test_vacancy_employer_minimal(self):
        """Тест минимальной инициализации VacancyEmployer"""
        employer = VacancyEmployer(name="Test Company")
        assert employer.name == "Test Company"
        assert employer.url is None


class TestVacancy:
    """Тесты для Vacancy"""

    def test_vacancy_initialization(self):
        """Тест инициализации Vacancy"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru"
        )
        assert vacancy.vacancy_id == "123"
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://test.com/vacancy/123"
        assert vacancy.source == "hh.ru"

    def test_vacancy_with_salary(self):
        """Тест вакансии с зарплатой"""
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            salary=salary
        )
        assert vacancy.salary == salary
        assert vacancy.salary.from_amount == 100000

    def test_vacancy_with_employer(self):
        """Тест вакансии с работодателем"""
        employer = VacancyEmployer(name="Test Company")
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            employer=employer
        )
        assert vacancy.employer == employer
        assert vacancy.employer.name == "Test Company"

    def test_vacancy_str_representation(self):
        """Тест строкового представления Vacancy"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru"
        )
        str_repr = str(vacancy)
        assert "Python Developer" in str_repr
        assert "123" in str_repr

    def test_vacancy_from_dict_hh(self, mock_vacancy_data):
        """Тест создания вакансии из словаря HH"""
        vacancy = Vacancy.from_dict(mock_vacancy_data, "hh.ru")
        assert vacancy.vacancy_id == "123456"
        assert vacancy.title == "Python Developer"
        assert vacancy.source == "hh.ru"

    def test_vacancy_from_dict_sj(self):
        """Тест создания вакансии из словаря SuperJob"""
        sj_data = {
            "id": 123456,
            "profession": "Python Developer",
            "firm_name": "Test Company",
            "payment_from": 100000,
            "payment_to": 150000,
            "currency": "rub",
            "town": {"title": "Москва"},
            "link": "https://test.com/vacancy/123456"
        }
        
        vacancy = Vacancy.from_dict(sj_data, "superjob.ru")
        assert vacancy.vacancy_id == "123456"
        assert vacancy.title == "Python Developer"
        assert vacancy.source == "superjob.ru"

    def test_vacancy_comparison(self):
        """Тест сравнения вакансий"""
        vacancy1 = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru"
        )
        vacancy2 = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru"
        )
        
        # Вакансии с одинаковыми ID должны считаться равными
        assert vacancy1.vacancy_id == vacancy2.vacancy_id

    def test_vacancy_to_dict(self):
        """Тест преобразования вакансии в словарь"""
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        employer = VacancyEmployer(name="Test Company")
        
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            salary=salary,
            employer=employer
        )
        
        vacancy_dict = vacancy.to_dict()
        assert isinstance(vacancy_dict, dict)
        assert vacancy_dict["vacancy_id"] == "123"
        assert vacancy_dict["title"] == "Python Developer"
