
"""
Полные тесты для BaseFormatter с 100% покрытием
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch
from abc import ABC, abstractmethod

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.base_formatter import BaseFormatter


class ConcreteFormatter(BaseFormatter):
    """Конкретная реализация BaseFormatter для тестов"""

    def format_vacancy_info(self, vacancy, number=None):
        """Форматирование информации о вакансии"""
        if not vacancy:
            return "Без названия"
        
        lines = []
        if number:
            lines.append(f"{number}.")
        
        title = getattr(vacancy, 'title', None) or vacancy.get('title', 'Без названия') if hasattr(vacancy, 'get') else 'Без названия'
        lines.append(f"Название: {title}")
        
        salary = getattr(vacancy, 'salary', None) or vacancy.get('salary') if hasattr(vacancy, 'get') else None
        if salary:
            lines.append(f"Зарплата: {self.format_salary(salary)}")
        
        return "\n".join(lines)

    def format_salary(self, salary):
        """Форматирование зарплаты"""
        if not salary:
            return "Не указана"
        
        if hasattr(salary, 'get'):
            salary_from = salary.get('from')
            salary_to = salary.get('to')
            currency = salary.get('currency', 'RUR')
        else:
            salary_from = getattr(salary, 'salary_from', None)
            salary_to = getattr(salary, 'salary_to', None)
            currency = getattr(salary, 'currency', 'RUR')
        
        if salary_from and salary_to:
            return f"{self.format_number(salary_from)} - {self.format_number(salary_to)} {self.format_currency(currency)}"
        elif salary_from:
            return f"от {self.format_number(salary_from)} {self.format_currency(currency)}"
        elif salary_to:
            return f"до {self.format_number(salary_to)} {self.format_currency(currency)}"
        else:
            return "Не указана"

    def format_currency(self, currency):
        """Форматирование валюты"""
        currency_map = {
            'RUR': 'руб.',
            'RUB': 'руб.',
            'USD': 'долл.',
            'EUR': 'евро'
        }
        return currency_map.get(currency, currency)

    def format_text(self, text, max_length=150):
        """Форматирование текста с возможностью усечения"""
        if not text:
            return "Не указано"
        
        clean_text = self.clean_html_tags(str(text))
        if len(clean_text) > max_length:
            return clean_text[:max_length] + "..."
        return clean_text

    def format_date(self, date_str):
        """Форматирование даты"""
        if not date_str:
            return "Не указано"
        
        # Простое форматирование для тестов
        if "T" in str(date_str):
            return str(date_str).split("T")[0]
        return str(date_str)

    def format_experience(self, experience):
        """Форматирование опыта работы"""
        if not experience:
            return "Не указан"
        return str(experience)

    def format_employment_type(self, employment):
        """Форматирование типа занятости"""
        if not employment:
            return "Не указан"
        return str(employment)

    def format_schedule(self, schedule):
        """Форматирование графика работы"""
        if not schedule:
            return "Не указан"
        return str(schedule)

    def format_company_name(self, company):
        """Форматирование названия компании"""
        if not company:
            return "Не указана"
        
        if hasattr(company, 'get'):
            return company.get('name', 'Не указана')
        elif hasattr(company, 'name'):
            return company.name
        return str(company)

    def clean_html_tags(self, text):
        """Очистка HTML тегов из текста"""
        import re
        if not text:
            return ""
        
        clean = re.compile('<.*?>')
        result = re.sub(clean, '', str(text))
        return result.strip()

    def format_number(self, number):
        """Форматирование числа с разделителями тысяч"""
        if not isinstance(number, (int, float)):
            return str(number)
        return f"{number:,}".replace(",", " ")


class TestBaseFormatterComplete:
    """Полные тесты для BaseFormatter"""

    @pytest.fixture
    def formatter(self):
        """Фикстура форматтера"""
        return ConcreteFormatter()

    @pytest.fixture
    def mock_vacancy(self):
        """Мок вакансии"""
        return {
            'title': 'Python Developer',
            'salary': {
                'from': 100000,
                'to': 150000,
                'currency': 'RUR'
            },
            'company': {'name': 'Test Company'},
            'experience': 'От 1 года до 3 лет'
        }

    def test_format_vacancy_info_complete(self, formatter, mock_vacancy):
        """Тест полного форматирования вакансии"""
        result = formatter.format_vacancy_info(mock_vacancy, 1)
        
        assert "1." in result
        assert "Python Developer" in result
        assert "100 000 - 150 000 руб." in result

    def test_format_vacancy_info_empty(self, formatter):
        """Тест форматирования пустой вакансии"""
        result = formatter.format_vacancy_info(None)
        assert result == "Без названия"

    def test_format_vacancy_info_minimal(self, formatter):
        """Тест форматирования минимальной вакансии"""
        minimal_vacancy = {'title': 'Test Job'}
        result = formatter.format_vacancy_info(minimal_vacancy)
        assert "Test Job" in result

    def test_format_salary_range(self, formatter):
        """Тест форматирования диапазона зарплат"""
        salary = {'from': 100000, 'to': 150000, 'currency': 'RUR'}
        result = formatter.format_salary(salary)
        assert result == "100 000 - 150 000 руб."

    def test_format_salary_from_only(self, formatter):
        """Тест форматирования зарплаты только от"""
        salary = {'from': 100000, 'currency': 'USD'}
        result = formatter.format_salary(salary)
        assert result == "от 100 000 долл."

    def test_format_salary_to_only(self, formatter):
        """Тест форматирования зарплаты только до"""
        salary = {'to': 150000, 'currency': 'EUR'}
        result = formatter.format_salary(salary)
        assert result == "до 150 000 евро"

    def test_format_salary_empty(self, formatter):
        """Тест форматирования пустой зарплаты"""
        result = formatter.format_salary(None)
        assert result == "Не указана"

    def test_format_salary_no_amounts(self, formatter):
        """Тест форматирования зарплаты без сумм"""
        salary = {'currency': 'RUR'}
        result = formatter.format_salary(salary)
        assert result == "Не указана"

    def test_format_currency_known(self, formatter):
        """Тест форматирования известных валют"""
        assert formatter.format_currency('RUR') == 'руб.'
        assert formatter.format_currency('RUB') == 'руб.'
        assert formatter.format_currency('USD') == 'долл.'
        assert formatter.format_currency('EUR') == 'евро'

    def test_format_currency_unknown(self, formatter):
        """Тест форматирования неизвестной валюты"""
        assert formatter.format_currency('GBP') == 'GBP'

    def test_format_text_normal(self, formatter):
        """Тест нормального форматирования текста"""
        text = "Обычный текст без HTML"
        result = formatter.format_text(text)
        assert result == text

    def test_format_text_with_html(self, formatter):
        """Тест форматирования текста с HTML"""
        text = "<p>Текст с <b>HTML</b> тегами</p>"
        result = formatter.format_text(text)
        assert result == "Текст с HTML тегами"

    def test_format_text_long(self, formatter):
        """Тест форматирования длинного текста"""
        long_text = "a" * 200
        result = formatter.format_text(long_text, 100)
        assert len(result) == 103  # 100 + "..."
        assert result.endswith("...")

    def test_format_text_empty(self, formatter):
        """Тест форматирования пустого текста"""
        result = formatter.format_text("")
        assert result == "Не указано"

    def test_format_date_iso(self, formatter):
        """Тест форматирования ISO даты"""
        date_str = "2025-01-15T10:30:00+03:00"
        result = formatter.format_date(date_str)
        assert result == "2025-01-15"

    def test_format_date_simple(self, formatter):
        """Тест форматирования простой даты"""
        date_str = "2025-01-15"
        result = formatter.format_date(date_str)
        assert result == "2025-01-15"

    def test_format_date_empty(self, formatter):
        """Тест форматирования пустой даты"""
        result = formatter.format_date("")
        assert result == "Не указано"

    def test_format_experience_normal(self, formatter):
        """Тест форматирования опыта"""
        result = formatter.format_experience("От 1 года до 3 лет")
        assert result == "От 1 года до 3 лет"

    def test_format_experience_empty(self, formatter):
        """Тест форматирования пустого опыта"""
        result = formatter.format_experience("")
        assert result == "Не указан"

    def test_format_employment_type_normal(self, formatter):
        """Тест форматирования типа занятости"""
        result = formatter.format_employment_type("Полная занятость")
        assert result == "Полная занятость"

    def test_format_employment_type_empty(self, formatter):
        """Тест форматирования пустого типа занятости"""
        result = formatter.format_employment_type("")
        assert result == "Не указан"

    def test_format_schedule_normal(self, formatter):
        """Тест форматирования графика"""
        result = formatter.format_schedule("Полный день")
        assert result == "Полный день"

    def test_format_schedule_empty(self, formatter):
        """Тест форматирования пустого графика"""
        result = formatter.format_schedule("")
        assert result == "Не указан"

    def test_format_company_name_dict(self, formatter):
        """Тест форматирования названия компании из словаря"""
        company = {'name': 'Test Company'}
        result = formatter.format_company_name(company)
        assert result == "Test Company"

    def test_format_company_name_object(self, formatter):
        """Тест форматирования названия компании из объекта"""
        company = Mock()
        company.name = "Test Company"
        result = formatter.format_company_name(company)
        assert result == "Test Company"

    def test_format_company_name_string(self, formatter):
        """Тест форматирования названия компании из строки"""
        result = formatter.format_company_name("Test Company")
        assert result == "Test Company"

    def test_format_company_name_empty(self, formatter):
        """Тест форматирования пустого названия компании"""
        result = formatter.format_company_name("")
        assert result == "Не указана"

    def test_clean_html_tags_simple(self, formatter):
        """Тест очистки простых HTML тегов"""
        text = "<p>Hello <b>World</b></p>"
        result = formatter.clean_html_tags(text)
        assert result == "Hello World"

    def test_clean_html_tags_complex(self, formatter):
        """Тест очистки сложных HTML тегов"""
        text = '<div class="content"><span style="color: red;">Text</span></div>'
        result = formatter.clean_html_tags(text)
        assert result == "Text"

    def test_clean_html_tags_empty(self, formatter):
        """Тест очистки пустого текста"""
        result = formatter.clean_html_tags("")
        assert result == ""

    def test_format_number_integer(self, formatter):
        """Тест форматирования целого числа"""
        result = formatter.format_number(1000000)
        assert result == "1 000 000"

    def test_format_number_float(self, formatter):
        """Тест форматирования дробного числа"""
        result = formatter.format_number(1000.5)
        assert result == "1 000.5"

    def test_format_number_invalid(self, formatter):
        """Тест форматирования некорректного числа"""
        result = formatter.format_number("invalid")
        assert result == "invalid"

    def test_abstract_methods_coverage(self):
        """Тест покрытия абстрактных методов"""
        # Проверяем что BaseFormatter действительно абстрактный
        assert BaseFormatter.__abstractmethods__
        
        # Проверяем что все абстрактные методы определены
        expected_methods = {
            'format_vacancy_info', 'format_salary', 'format_currency',
            'format_text', 'format_date', 'format_experience',
            'format_employment_type', 'format_schedule', 'format_company_name',
            'clean_html_tags', 'format_number'
        }
        
        actual_methods = BaseFormatter.__abstractmethods__
        assert expected_methods.issubset(actual_methods)

    def test_concrete_implementation_all_methods(self, formatter):
        """Тест что конкретная реализация имеет все методы"""
        required_methods = [
            'format_vacancy_info', 'format_salary', 'format_currency',
            'format_text', 'format_date', 'format_experience',
            'format_employment_type', 'format_schedule', 'format_company_name',
            'clean_html_tags', 'format_number'
        ]
        
        for method_name in required_methods:
            assert hasattr(formatter, method_name)
            assert callable(getattr(formatter, method_name))
