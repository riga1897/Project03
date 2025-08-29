
"""
Полные тесты для VacancyFormatter
"""

import pytest
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestVacancyFormatterComplete:
    """Полное тестирование VacancyFormatter"""

    @pytest.fixture
    def formatter(self):
        """Фикстура VacancyFormatter"""
        return VacancyFormatter()

    @pytest.fixture
    def test_vacancy_full(self):
        """Вакансия с полными данными"""
        return Vacancy(
            title="Senior Python Developer",
            url="https://hh.ru/vacancy/123456",
            salary={"from": 150000, "to": 200000, "currency": "RUR"},
            description="Разработка высоконагруженных веб-приложений",
            requirements="Python, Django, PostgreSQL, Redis",
            responsibilities="Проектирование архитектуры, код-ревью",
            experience="От 3 до 6 лет",
            employment="Полная занятость",
            schedule="Полный день",
            employer={"name": "Tech Company"},
            vacancy_id="123456",
            published_at="2024-01-15T10:00:00+03:00",
            source="hh.ru"
        )

    @pytest.fixture
    def test_vacancy_minimal(self):
        """Вакансия с минимальными данными"""
        return Vacancy(
            title="Junior Developer",
            url="https://example.com/minimal",
            vacancy_id="minimal001",
            source="test"
        )

    def test_format_vacancy_info_full(self, formatter, test_vacancy_full):
        """Тест полного форматирования вакансии"""
        result = formatter.format_vacancy_info(test_vacancy_full, 1)
        
        assert "1." in result
        assert "Senior Python Developer" in result
        assert "123456" in result
        assert "Tech Company" in result
        assert "150,000" in result or "150 000" in result
        assert "200,000" in result or "200 000" in result

    def test_format_vacancy_info_minimal(self, formatter, test_vacancy_minimal):
        """Тест форматирования минимальной вакансии"""
        result = formatter.format_vacancy_info(test_vacancy_minimal, 2)
        
        assert "2." in result
        assert "Junior Developer" in result
        assert "minimal001" in result
        assert "Не указана" in result  # зарплата
        assert "Не указана" in result or "Не указано" in result  # компания

    def test_format_vacancy_brief_static(self, test_vacancy_full):
        """Тест статического метода краткого форматирования"""
        result = VacancyFormatter.format_vacancy_brief(test_vacancy_full, 5)
        
        assert "5." in result
        assert "Senior Python Developer" in result
        assert "Tech Company" in result
        assert isinstance(result, str)

    def test_format_salary_variations(self, formatter):
        """Тест форматирования различных вариантов зарплаты"""
        # Полный диапазон
        salary_range = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = formatter.format_salary(salary_range)
        assert "от 100" in result and "до 150" in result
        
        # Только от
        salary_from = {"from": 80000, "currency": "RUR"}
        result = formatter.format_salary(salary_from)
        assert "от 80" in result and "до" not in result
        
        # Только до
        salary_to = {"to": 120000, "currency": "RUR"}
        result = formatter.format_salary(salary_to)
        assert "до 120" in result and "от" not in result
        
        # Без валюты
        salary_no_currency = {"from": 100000, "to": 150000}
        result = formatter.format_salary(salary_no_currency)
        assert "руб." in result
        
        # Пустое
        result = formatter.format_salary({})
        assert result == "Не указана"
        
        # None
        result = formatter.format_salary(None)
        assert result == "Не указана"

    def test_format_text_method(self, formatter):
        """Тест метода format_text"""
        # Обычный текст
        assert formatter.format_text("Тестовый текст") == "Тестовый текст"
        
        # Пустая строка
        assert formatter.format_text("") == "Не указано"
        
        # None
        assert formatter.format_text(None) == "Не указано"
        
        # Только пробелы
        assert formatter.format_text("   ") == "Не указано"

    def test_format_employer(self, formatter):
        """Тест форматирования работодателя"""
        # Словарь с названием
        employer_dict = {"name": "Test Company"}
        result = formatter._format_employer(employer_dict)
        assert result == "Test Company"
        
        # Пустой словарь
        result = formatter._format_employer({})
        assert result == "Не указана"
        
        # None
        result = formatter._format_employer(None)
        assert result == "Не указана"
        
        # Строка (на всякий случай)
        result = formatter._format_employer("String Company")
        assert result == "String Company"

    def test_format_with_number_variations(self, formatter, test_vacancy_full):
        """Тест форматирования с различными номерами"""
        # Без номера
        result = formatter.format_vacancy_info(test_vacancy_full)
        assert "Senior Python Developer" in result
        
        # С номером
        result = formatter.format_vacancy_info(test_vacancy_full, 10)
        assert "10." in result
        
        # Большой номер
        result = formatter.format_vacancy_info(test_vacancy_full, 999)
        assert "999." in result
