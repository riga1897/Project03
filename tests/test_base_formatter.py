
"""
Тесты для базового форматировщика
"""

import pytest
from src.utils.base_formatter import BaseFormatter


class ConcreteFormatter(BaseFormatter):
    """Конкретная реализация BaseFormatter для тестирования"""
    
    def format_vacancy_info(self, vacancy, index=None):
        """Заглушка для абстрактного метода"""
        return f"Test format for vacancy: {vacancy}"


class TestBaseFormatter:
    """Тесты для BaseFormatter"""

    @pytest.fixture
    def formatter(self):
        """Фикстура конкретного форматировщика"""
        return ConcreteFormatter()

    def test_format_salary_full_range(self, formatter):
        """Тест форматирования зарплаты с диапазоном"""
        salary = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = formatter.format_salary(salary)
        assert result == "от 100,000 до 150,000 ₽"

    def test_format_salary_from_only(self, formatter):
        """Тест форматирования зарплаты только от"""
        salary = {"from": 100000, "currency": "RUR"}
        result = formatter.format_salary(salary)
        assert result == "от 100,000 ₽"

    def test_format_salary_to_only(self, formatter):
        """Тест форматирования зарплаты только до"""
        salary = {"to": 150000, "currency": "RUR"}
        result = formatter.format_salary(salary)
        assert result == "до 150,000 ₽"

    def test_format_salary_none(self, formatter):
        """Тест форматирования пустой зарплаты"""
        result = formatter.format_salary(None)
        assert result == "Не указана"

    def test_format_salary_empty_dict(self, formatter):
        """Тест форматирования пустого словаря зарплаты"""
        result = formatter.format_salary({})
        assert result == "Не указана"

    def test_format_currency_rur(self, formatter):
        """Тест форматирования валюты RUR"""
        result = formatter.format_currency("RUR")
        assert result == "₽"

    def test_format_currency_usd(self, formatter):
        """Тест форматирования валюты USD"""
        result = formatter.format_currency("USD")
        assert result == "$"

    def test_format_currency_eur(self, formatter):
        """Тест форматирования валюты EUR"""
        result = formatter.format_currency("EUR")
        assert result == "€"

    def test_format_currency_unknown(self, formatter):
        """Тест форматирования неизвестной валюты"""
        result = formatter.format_currency("UNKNOWN")
        assert result == "UNKNOWN"

    def test_format_text_truncate(self, formatter):
        """Тест усечения длинного текста"""
        long_text = "a" * 200
        result = formatter.format_text(long_text, max_length=50)
        assert len(result) == 53  # 50 + "..."
        assert result.endswith("...")

    def test_format_text_short(self, formatter):
        """Тест короткого текста"""
        short_text = "Short text"
        result = formatter.format_text(short_text, max_length=50)
        assert result == short_text

    def test_format_text_none(self, formatter):
        """Тест форматирования None текста"""
        result = formatter.format_text(None)
        assert result == "Не указано"

    def test_format_date_string(self, formatter):
        """Тест форматирования даты-строки"""
        date_str = "2024-01-01T12:00:00"
        result = formatter.format_date(date_str)
        assert result == "01.01.2024"

    def test_format_date_none(self, formatter):
        """Тест форматирования None даты"""
        result = formatter.format_date(None)
        assert result == "Не указано"

    def test_format_experience_string(self, formatter):
        """Тест форматирования опыта работы"""
        experience = "От 3 до 6 лет"
        result = formatter.format_experience(experience)
        assert result == experience

    def test_format_experience_none(self, formatter):
        """Тест форматирования None опыта"""
        result = formatter.format_experience(None)
        assert result == "Не указан"

    def test_format_employment_type(self, formatter):
        """Тест форматирования типа занятости"""
        employment = "Полная занятость"
        result = formatter.format_employment_type(employment)
        assert result == employment

    def test_format_schedule(self, formatter):
        """Тест форматирования графика работы"""
        schedule = "Полный день"
        result = formatter.format_schedule(schedule)
        assert result == schedule

    def test_format_company_name(self, formatter):
        """Тест форматирования названия компании"""
        company = "Test Company"
        result = formatter.format_company_name(company)
        assert result == company

    def test_format_company_name_dict(self, formatter):
        """Тест форматирования названия компании из словаря"""
        company = {"name": "Test Company"}
        result = formatter.format_company_name(company)
        assert result == "Test Company"

    def test_format_company_name_none(self, formatter):
        """Тест форматирования None компании"""
        result = formatter.format_company_name(None)
        assert result == "Не указана"

    def test_clean_html_tags(self, formatter):
        """Тест очистки HTML тегов"""
        html_text = "<p>Test <b>text</b> with <em>tags</em></p>"
        result = formatter.clean_html_tags(html_text)
        assert result == "Test text with tags"

    def test_clean_html_none(self, formatter):
        """Тест очистки None от HTML"""
        result = formatter.clean_html_tags(None)
        assert result == ""

    def test_format_number_thousands(self, formatter):
        """Тест форматирования числа с разделителями тысяч"""
        result = formatter.format_number(1234567)
        assert result == "1,234,567"
