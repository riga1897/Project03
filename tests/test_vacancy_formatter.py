
import pytest
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy, VacancySalary, VacancyEmployer


class TestVacancyFormatter:
    """Тесты для VacancyFormatter"""

    def test_vacancy_formatter_initialization(self):
        """Тест инициализации VacancyFormatter"""
        formatter = VacancyFormatter()
        assert isinstance(formatter, VacancyFormatter)

    def test_format_vacancy_info_basic(self):
        """Тест форматирования базовой информации о вакансии"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru"
        )
        
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)
        
        assert "Python Developer" in result
        assert "123" in result
        assert "hh.ru" in result

    def test_format_vacancy_info_with_salary(self):
        """Тест форматирования вакансии с зарплатой"""
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            salary=salary
        )
        
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)
        
        assert "100000" in result
        assert "150000" in result

    def test_format_vacancy_info_with_employer(self):
        """Тест форматирования вакансии с работодателем"""
        employer = VacancyEmployer(name="Test Company")
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            employer=employer
        )
        
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)
        
        assert "Test Company" in result

    def test_format_vacancy_info_with_number(self):
        """Тест форматирования вакансии с номером"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru"
        )
        
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy, number=1)
        
        assert "1." in result

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
            employment="Полная занятость"
        )
        
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy, number=1)
        
        assert "1." in result
        assert "Python Developer" in result
        assert "Test Company" in result
        assert "100000" in result
        assert "Москва" in result
        assert "hh.ru" in result

    def test_format_vacancy_minimal(self):
        """Тест форматирования минимальной вакансии"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru"
        )
        
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)
        
        # Проверяем, что нет ошибок при отсутствии необязательных полей
        assert isinstance(result, str)
        assert len(result) > 0
