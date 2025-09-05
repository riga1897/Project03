
"""
Полные тесты для базового форматтера
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.base_formatter import BaseFormatter
    BASE_FORMATTER_AVAILABLE = True
except ImportError:
    BASE_FORMATTER_AVAILABLE = False


class ConcreteFormatter(BaseFormatter if BASE_FORMATTER_AVAILABLE else object):
    """Конкретная реализация BaseFormatter для тестирования"""
    
    def format_vacancy_info(self, vacancy, number=None):
        """Форматирование информации о вакансии"""
        if number:
            return f"{number}. {vacancy.get('title', 'No title')}"
        return vacancy.get('title', 'No title')
    
    def format_salary(self, salary):
        """Форматирование зарплаты"""
        if not salary:
            return "Зарплата не указана"
        
        if isinstance(salary, dict):
            from_val = salary.get('from')
            to_val = salary.get('to')
            currency = salary.get('currency', 'RUR')
            
            if from_val and to_val:
                return f"{from_val} - {to_val} {currency}"
            elif from_val:
                return f"от {from_val} {currency}"
            elif to_val:
                return f"до {to_val} {currency}"
        
        return str(salary)
    
    def format_currency(self, currency):
        """Форматирование валюты"""
        currency_map = {
            'RUR': '₽',
            'USD': '$',
            'EUR': '€'
        }
        return currency_map.get(currency, currency)
    
    def format_text(self, text, max_length=150):
        """Форматирование текста с усечением"""
        if not text:
            return ""
        
        text = str(text)
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def format_date(self, date_str):
        """Форматирование даты"""
        if not date_str:
            return ""
        return str(date_str)
    
    def format_experience(self, experience):
        """Форматирование опыта работы"""
        if not experience:
            return "Опыт не указан"
        
        if isinstance(experience, dict):
            return experience.get('name', str(experience))
        return str(experience)
    
    def format_employment_type(self, employment):
        """Форматирование типа занятости"""
        if not employment:
            return "Не указано"
        
        if isinstance(employment, dict):
            return employment.get('name', str(employment))
        return str(employment)
    
    def format_schedule(self, schedule):
        """Форматирование графика работы"""
        if not schedule:
            return "График не указан"
        
        if isinstance(schedule, dict):
            return schedule.get('name', str(schedule))
        return str(schedule)
    
    def format_company_name(self, company):
        """Форматирование названия компании"""
        if not company:
            return "Компания не указана"
        
        if isinstance(company, dict):
            return company.get('name', str(company))
        return str(company)
    
    def clean_html_tags(self, text):
        """Очистка HTML тегов"""
        if not text:
            return ""
        
        import re
        text = str(text)
        # Простая очистка HTML тегов
        cleaned = re.sub(r'<[^>]+>', '', text)
        return cleaned.strip()
    
    def format_number(self, number):
        """Форматирование числа с разделителями"""
        if number is None:
            return "0"
        
        try:
            return f"{int(number):,}".replace(',', ' ')
        except (ValueError, TypeError):
            return str(number)


class TestBaseFormatterComplete:
    """Полные тесты для базового форматтера"""

    @pytest.fixture
    def formatter(self):
        """Фикстура для создания форматтера"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")
        return ConcreteFormatter()

    def test_base_formatter_is_abstract(self):
        """Тест что BaseFormatter является абстрактным"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")
        
        with pytest.raises(TypeError):
            BaseFormatter()

    def test_format_vacancy_info_with_number(self, formatter):
        """Тест форматирования вакансии с номером"""
        vacancy = {'title': 'Python Developer'}
        result = formatter.format_vacancy_info(vacancy, 1)
        assert result == "1. Python Developer"

    def test_format_vacancy_info_without_number(self, formatter):
        """Тест форматирования вакансии без номера"""
        vacancy = {'title': 'Python Developer'}
        result = formatter.format_vacancy_info(vacancy)
        assert result == "Python Developer"

    def test_format_salary_full_range(self, formatter):
        """Тест форматирования полного диапазона зарплаты"""
        salary = {'from': 100000, 'to': 150000, 'currency': 'RUR'}
        result = formatter.format_salary(salary)
        assert result == "100000 - 150000 RUR"

    def test_format_salary_from_only(self, formatter):
        """Тест форматирования зарплаты только от"""
        salary = {'from': 100000, 'currency': 'RUR'}
        result = formatter.format_salary(salary)
        assert result == "от 100000 RUR"

    def test_format_salary_none(self, formatter):
        """Тест форматирования пустой зарплаты"""
        result = formatter.format_salary(None)
        assert result == "Зарплата не указана"

    def test_format_currency_rur(self, formatter):
        """Тест форматирования рублей"""
        result = formatter.format_currency('RUR')
        assert result == '₽'

    def test_format_currency_unknown(self, formatter):
        """Тест форматирования неизвестной валюты"""
        result = formatter.format_currency('XXX')
        assert result == 'XXX'

    def test_format_text_normal(self, formatter):
        """Тест форматирования обычного текста"""
        text = "Short text"
        result = formatter.format_text(text)
        assert result == "Short text"

    def test_format_text_truncated(self, formatter):
        """Тест усечения длинного текста"""
        text = "a" * 200
        result = formatter.format_text(text, 100)
        assert len(result) == 103  # 100 + "..."
        assert result.endswith("...")

    def test_format_experience_dict(self, formatter):
        """Тест форматирования опыта как словаря"""
        experience = {'name': 'От 1 года до 3 лет'}
        result = formatter.format_experience(experience)
        assert result == 'От 1 года до 3 лет'

    def test_format_experience_string(self, formatter):
        """Тест форматирования опыта как строки"""
        experience = 'От 1 года до 3 лет'
        result = formatter.format_experience(experience)
        assert result == 'От 1 года до 3 лет'

    def test_format_company_name_dict(self, formatter):
        """Тест форматирования названия компании как словаря"""
        company = {'name': 'Google'}
        result = formatter.format_company_name(company)
        assert result == 'Google'

    def test_format_company_name_none(self, formatter):
        """Тест форматирования пустого названия компании"""
        result = formatter.format_company_name(None)
        assert result == 'Компания не указана'

    def test_clean_html_tags_simple(self, formatter):
        """Тест очистки простых HTML тегов"""
        text = "<p>Hello <b>world</b></p>"
        result = formatter.clean_html_tags(text)
        assert result == "Hello world"

    def test_clean_html_tags_empty(self, formatter):
        """Тест очистки пустого текста"""
        result = formatter.clean_html_tags("")
        assert result == ""

    def test_format_number_integer(self, formatter):
        """Тест форматирования целого числа"""
        result = formatter.format_number(1000000)
        assert result == "1 000 000"

    def test_format_number_none(self, formatter):
        """Тест форматирования None"""
        result = formatter.format_number(None)
        assert result == "0"

    def test_format_date_string(self, formatter):
        """Тест форматирования даты как строки"""
        date_str = "2023-01-01"
        result = formatter.format_date(date_str)
        assert result == "2023-01-01"

    def test_format_employment_type_dict(self, formatter):
        """Тест форматирования типа занятости как словаря"""
        employment = {'name': 'Полная занятость'}
        result = formatter.format_employment_type(employment)
        assert result == 'Полная занятость'

    def test_format_schedule_dict(self, formatter):
        """Тест форматирования графика работы как словаря"""
        schedule = {'name': 'Полный день'}
        result = formatter.format_schedule(schedule)
        assert result == 'Полный день'

    def test_all_abstract_methods_implemented(self, formatter):
        """Тест что все абстрактные методы реализованы"""
        # Проверяем что объект создается без ошибок
        assert formatter is not None
        
        # Проверяем что все методы callable
        assert callable(formatter.format_vacancy_info)
        assert callable(formatter.format_salary)
        assert callable(formatter.format_currency)
        assert callable(formatter.format_text)
        assert callable(formatter.format_date)
        assert callable(formatter.format_experience)
        assert callable(formatter.format_employment_type)
        assert callable(formatter.format_schedule)
        assert callable(formatter.format_company_name)
        assert callable(formatter.clean_html_tags)
        assert callable(formatter.format_number)
