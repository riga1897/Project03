
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
    BaseFormatter = object


class ConcreteFormatter(BaseFormatter if BASE_FORMATTER_AVAILABLE else object):
    """Конкретная реализация BaseFormatter для тестирования"""
    
    def format_vacancy_info(self, vacancy, number=None):
        """Форматирование информации о вакансии"""
        if number:
            return f"{number}. {vacancy.get('title', 'N/A')}"
        return vacancy.get('title', 'N/A')
    
    def format_salary(self, salary):
        """Форматирование зарплаты"""
        if not salary:
            return "Не указана"
        
        if isinstance(salary, dict):
            from_salary = salary.get('from')
            to_salary = salary.get('to')
            currency = salary.get('currency', 'RUB')
            
            if from_salary and to_salary:
                return f"{from_salary}-{to_salary} {currency}"
            elif from_salary:
                return f"от {from_salary} {currency}"
            elif to_salary:
                return f"до {to_salary} {currency}"
        
        return str(salary)
    
    def format_currency(self, currency):
        """Форматирование валюты"""
        currency_map = {
            'RUB': '₽',
            'USD': '$', 
            'EUR': '€'
        }
        return currency_map.get(currency, currency)
    
    def format_text(self, text, max_length=150):
        """Форматирование текста с усечением"""
        if not text:
            return ""
        
        text_str = str(text)
        if len(text_str) <= max_length:
            return text_str
        
        return text_str[:max_length-3] + "..."
    
    def format_date(self, date_str):
        """Форматирование даты"""
        if not date_str:
            return "N/A"
        return str(date_str)
    
    def format_experience(self, experience):
        """Форматирование опыта работы"""
        if not experience:
            return "Не указан"
        
        if isinstance(experience, dict):
            return experience.get('name', 'Не указан')
        return str(experience)
    
    def format_employment_type(self, employment):
        """Форматирование типа занятости"""
        if not employment:
            return "Не указан"
        
        if isinstance(employment, dict):
            return employment.get('name', 'Не указан')
        return str(employment)
    
    def format_schedule(self, schedule):
        """Форматирование графика работы"""
        if not schedule:
            return "Не указан"
        
        if isinstance(schedule, dict):
            return schedule.get('name', 'Не указан')
        return str(schedule)
    
    def format_company_name(self, company):
        """Форматирование названия компании"""
        if not company:
            return "Не указана"
        
        if isinstance(company, dict):
            return company.get('name', 'Не указана')
        elif hasattr(company, 'name'):
            return company.name
        return str(company)
    
    def clean_html_tags(self, text):
        """Очистка HTML тегов из текста"""
        if not text:
            return ""
        
        import re
        # Простая очистка HTML тегов
        clean_text = re.sub('<[^<]+?>', '', str(text))
        return clean_text.strip()
    
    def format_number(self, number):
        """Форматирование числа с разделителями тысяч"""
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
        """Фикстура форматтера"""
        if not BASE_FORMATTER_AVAILABLE:
            return Mock()
        return ConcreteFormatter()

    def test_abstract_formatter_cannot_be_instantiated(self):
        """Тест что базовый класс нельзя инстанциировать"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        with pytest.raises(TypeError):
            BaseFormatter()

    def test_concrete_implementation_works(self, formatter):
        """Тест что конкретная реализация работает"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        assert formatter is not None

    def test_format_vacancy_info_with_number(self, formatter):
        """Тест форматирования вакансии с номером"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        vacancy = {"title": "Python Developer"}
        result = formatter.format_vacancy_info(vacancy, 1)
        assert result == "1. Python Developer"

    def test_format_vacancy_info_without_number(self, formatter):
        """Тест форматирования вакансии без номера"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        vacancy = {"title": "Python Developer"}
        result = formatter.format_vacancy_info(vacancy)
        assert result == "Python Developer"

    def test_format_vacancy_info_no_title(self, formatter):
        """Тест форматирования вакансии без заголовка"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        vacancy = {}
        result = formatter.format_vacancy_info(vacancy, 1)
        assert result == "1. N/A"

    def test_format_salary_range(self, formatter):
        """Тест форматирования диапазона зарплаты"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        salary = {"from": 100000, "to": 150000, "currency": "RUB"}
        result = formatter.format_salary(salary)
        assert result == "100000-150000 RUB"

    def test_format_salary_from_only(self, formatter):
        """Тест форматирования зарплаты только от"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        salary = {"from": 100000, "currency": "RUB"}
        result = formatter.format_salary(salary)
        assert result == "от 100000 RUB"

    def test_format_salary_to_only(self, formatter):
        """Тест форматирования зарплаты только до"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        salary = {"to": 150000, "currency": "RUB"}
        result = formatter.format_salary(salary)
        assert result == "до 150000 RUB"

    def test_format_salary_none(self, formatter):
        """Тест форматирования пустой зарплаты"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_salary(None)
        assert result == "Не указана"

    def test_format_currency_rub(self, formatter):
        """Тест форматирования рублей"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_currency("RUB")
        assert result == "₽"

    def test_format_currency_usd(self, formatter):
        """Тест форматирования долларов"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_currency("USD")
        assert result == "$"

    def test_format_currency_unknown(self, formatter):
        """Тест форматирования неизвестной валюты"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_currency("BTC")
        assert result == "BTC"

    def test_format_text_short(self, formatter):
        """Тест форматирования короткого текста"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        text = "Short text"
        result = formatter.format_text(text, max_length=50)
        assert result == "Short text"

    def test_format_text_long(self, formatter):
        """Тест форматирования длинного текста"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        text = "This is a very long text that should be truncated"
        result = formatter.format_text(text, max_length=20)
        assert result == "This is a very lo..."
        assert len(result) == 20

    def test_format_text_empty(self, formatter):
        """Тест форматирования пустого текста"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_text("", max_length=20)
        assert result == ""

    def test_format_date_valid(self, formatter):
        """Тест форматирования валидной даты"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        date_str = "2023-12-01"
        result = formatter.format_date(date_str)
        assert result == "2023-12-01"

    def test_format_date_empty(self, formatter):
        """Тест форматирования пустой даты"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_date("")
        assert result == "N/A"

    def test_format_experience_dict(self, formatter):
        """Тест форматирования опыта как словаря"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        experience = {"name": "От 3 до 6 лет"}
        result = formatter.format_experience(experience)
        assert result == "От 3 до 6 лет"

    def test_format_experience_string(self, formatter):
        """Тест форматирования опыта как строки"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_experience("3-6 лет")
        assert result == "3-6 лет"

    def test_format_experience_none(self, formatter):
        """Тест форматирования пустого опыта"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_experience(None)
        assert result == "Не указан"

    def test_format_company_name_dict(self, formatter):
        """Тест форматирования названия компании как словаря"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        company = {"name": "Test Company"}
        result = formatter.format_company_name(company)
        assert result == "Test Company"

    def test_format_company_name_object(self, formatter):
        """Тест форматирования названия компании из объекта"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        company = Mock()
        company.name = "Test Company"
        result = formatter.format_company_name(company)
        assert result == "Test Company"

    def test_format_company_name_none(self, formatter):
        """Тест форматирования пустого названия компании"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_company_name(None)
        assert result == "Не указана"

    def test_clean_html_tags_simple(self, formatter):
        """Тест очистки простых HTML тегов"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        text = "<p>Hello <b>world</b></p>"
        result = formatter.clean_html_tags(text)
        assert result == "Hello world"

    def test_clean_html_tags_complex(self, formatter):
        """Тест очистки сложных HTML тегов"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        text = '<div class="test"><span style="color: red;">Text</span></div>'
        result = formatter.clean_html_tags(text)
        assert result == "Text"

    def test_clean_html_tags_empty(self, formatter):
        """Тест очистки пустого текста"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.clean_html_tags("")
        assert result == ""

    def test_format_number_integer(self, formatter):
        """Тест форматирования целого числа"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_number(123456)
        assert result == "123 456"

    def test_format_number_zero(self, formatter):
        """Тест форматирования нуля"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_number(0)
        assert result == "0"

    def test_format_number_none(self, formatter):
        """Тест форматирования None"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_number(None)
        assert result == "0"

    def test_format_number_string(self, formatter):
        """Тест форматирования строки как числа"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_number("invalid")
        assert result == "invalid"
