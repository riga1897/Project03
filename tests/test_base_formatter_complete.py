
"""
Полные тесты для BaseFormatter с исправлением ошибок
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.base_formatter import BaseFormatter


class ConcreteFormatter(BaseFormatter):
    """Конкретная реализация BaseFormatter для тестирования"""

    def format_vacancy_info(self, vacancy, number=None):
        """Форматирование информации о вакансии"""
        if number is not None:
            return f"{number}. {vacancy.get('title', 'Без названия')}"
        return vacancy.get('title', 'Без названия')

    def format_salary(self, salary):
        """Форматирование зарплаты"""
        if not salary:
            return "Зарплата не указана"
        if isinstance(salary, dict):
            from_sal = salary.get('from')
            to_sal = salary.get('to')
            if from_sal and to_sal:
                return f"{from_sal}-{to_sal}"
            elif from_sal:
                return f"от {from_sal}"
            elif to_sal:
                return f"до {to_sal}"
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
        return text[:max_length-3] + "..."

    def format_date(self, date_str):
        """Форматирование даты"""
        if not date_str:
            return "Дата не указана"
        return str(date_str)

    def format_experience(self, experience):
        """Форматирование опыта работы"""
        if not experience:
            return "Опыт не указан"
        return str(experience)

    def format_employment_type(self, employment):
        """Форматирование типа занятости"""
        if not employment:
            return "Тип занятости не указан"
        return str(employment)

    def format_schedule(self, schedule):
        """Форматирование графика работы"""
        if not schedule:
            return "График не указан"
        return str(schedule)

    def format_company_name(self, company):
        """Форматирование названия компании"""
        if not company:
            return "Компания не указана"
        if isinstance(company, dict):
            return company.get('name', 'Компания не указана')
        return str(company)

    def clean_html_tags(self, text):
        """Очистка HTML тегов"""
        if not text:
            return ""
        import re
        return re.sub(r'<[^>]+>', '', str(text))

    def format_number(self, number):
        """Форматирование числа с разделителями тысяч"""
        if not isinstance(number, (int, float)):
            return str(number)
        return f"{number:,}".replace(',', ' ')


class TestBaseFormatterConcrete:
    """Тесты для конкретной реализации BaseFormatter"""

    @pytest.fixture
    def formatter(self):
        """Фикстура с экземпляром форматтера"""
        return ConcreteFormatter()

    def test_formatter_init(self, formatter):
        """Тест инициализации форматтера"""
        assert formatter is not None
        assert isinstance(formatter, BaseFormatter)

    def test_format_vacancy_info_with_number(self, formatter):
        """Тест форматирования вакансии с номером"""
        vacancy = {'title': 'Python Developer'}
        result = formatter.format_vacancy_info(vacancy, 1)
        assert result == "1. Python Developer"

    def test_format_vacancy_info_without_number(self, formatter):
        """Тест форматирования вакансии без номера"""
        vacancy = {'title': 'Java Developer'}
        result = formatter.format_vacancy_info(vacancy)
        assert result == "Java Developer"

    def test_format_vacancy_info_no_title(self, formatter):
        """Тест форматирования вакансии без названия"""
        vacancy = {}
        result = formatter.format_vacancy_info(vacancy)
        assert result == "Без названия"

    def test_format_salary_range(self, formatter):
        """Тест форматирования диапазона зарплаты"""
        salary = {'from': 100000, 'to': 150000}
        result = formatter.format_salary(salary)
        assert result == "100000-150000"

    def test_format_salary_from_only(self, formatter):
        """Тест форматирования зарплаты только от"""
        salary = {'from': 100000}
        result = formatter.format_salary(salary)
        assert result == "от 100000"

    def test_format_salary_to_only(self, formatter):
        """Тест форматирования зарплаты только до"""
        salary = {'to': 150000}
        result = formatter.format_salary(salary)
        assert result == "до 150000"

    def test_format_salary_none(self, formatter):
        """Тест форматирования отсутствующей зарплаты"""
        result = formatter.format_salary(None)
        assert result == "Зарплата не указана"

    def test_format_currency_rub(self, formatter):
        """Тест форматирования рублей"""
        result = formatter.format_currency('RUR')
        assert result == '₽'

    def test_format_currency_unknown(self, formatter):
        """Тест форматирования неизвестной валюты"""
        result = formatter.format_currency('BTC')
        assert result == 'BTC'

    def test_format_text_short(self, formatter):
        """Тест форматирования короткого текста"""
        text = "Короткий текст"
        result = formatter.format_text(text, 50)
        assert result == text

    def test_format_text_long(self, formatter):
        """Тест форматирования длинного текста"""
        text = "Очень длинный текст" * 10
        result = formatter.format_text(text, 20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_format_text_empty(self, formatter):
        """Тест форматирования пустого текста"""
        result = formatter.format_text("")
        assert result == ""

    def test_format_date_valid(self, formatter):
        """Тест форматирования даты"""
        result = formatter.format_date("2023-01-01")
        assert result == "2023-01-01"

    def test_format_date_empty(self, formatter):
        """Тест форматирования пустой даты"""
        result = formatter.format_date("")
        assert result == "Дата не указана"

    def test_format_experience_valid(self, formatter):
        """Тест форматирования опыта"""
        result = formatter.format_experience("От 1 года до 3 лет")
        assert result == "От 1 года до 3 лет"

    def test_format_experience_empty(self, formatter):
        """Тест форматирования пустого опыта"""
        result = formatter.format_experience("")
        assert result == "Опыт не указан"

    def test_format_employment_type_valid(self, formatter):
        """Тест форматирования типа занятости"""
        result = formatter.format_employment_type("Полная занятость")
        assert result == "Полная занятость"

    def test_format_employment_type_empty(self, formatter):
        """Тест форматирования пустого типа занятости"""
        result = formatter.format_employment_type("")
        assert result == "Тип занятости не указан"

    def test_format_schedule_valid(self, formatter):
        """Тест форматирования графика"""
        result = formatter.format_schedule("Полный день")
        assert result == "Полный день"

    def test_format_schedule_empty(self, formatter):
        """Тест форматирования пустого графика"""
        result = formatter.format_schedule("")
        assert result == "График не указан"

    def test_format_company_name_dict(self, formatter):
        """Тест форматирования названия компании из словаря"""
        company = {'name': 'Tech Corp'}
        result = formatter.format_company_name(company)
        assert result == "Tech Corp"

    def test_format_company_name_string(self, formatter):
        """Тест форматирования названия компании из строки"""
        result = formatter.format_company_name("Tech Corp")
        assert result == "Tech Corp"

    def test_format_company_name_empty(self, formatter):
        """Тест форматирования пустого названия компании"""
        result = formatter.format_company_name("")
        assert result == "Компания не указана"

    def test_clean_html_tags_basic(self, formatter):
        """Тест очистки HTML тегов"""
        text = "<p>Текст с <b>тегами</b></p>"
        result = formatter.clean_html_tags(text)
        assert result == "Текст с тегами"

    def test_clean_html_tags_empty(self, formatter):
        """Тест очистки пустого текста"""
        result = formatter.clean_html_tags("")
        assert result == ""

    def test_format_number_integer(self, formatter):
        """Тест форматирования целого числа"""
        result = formatter.format_number(123456)
        assert result == "123 456"

    def test_format_number_float(self, formatter):
        """Тест форматирования дробного числа"""
        result = formatter.format_number(123456.78)
        assert result == "123 456.78"

    def test_format_number_string(self, formatter):
        """Тест форматирования строки как числа"""
        result = formatter.format_number("not a number")
        assert result == "not a number"


class TestBaseFormatterAbstract:
    """Тесты для абстрактного класса BaseFormatter"""

    def test_base_formatter_is_abstract(self):
        """Тест что BaseFormatter является абстрактным"""
        with pytest.raises(TypeError):
            BaseFormatter()

    def test_abstract_methods_exist(self):
        """Тест наличия абстрактных методов"""
        abstract_methods = [
            'format_vacancy_info',
            'format_salary',
            'format_currency',
            'format_text',
            'format_date',
            'format_experience',
            'format_employment_type',
            'format_schedule',
            'format_company_name',
            'clean_html_tags',
            'format_number'
        ]
        
        for method_name in abstract_methods:
            assert hasattr(BaseFormatter, method_name)
            method = getattr(BaseFormatter, method_name)
            assert getattr(method, '__isabstractmethod__', False)
