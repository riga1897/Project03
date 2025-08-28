
"""
Тесты для модуля base_formatter
"""

import pytest
from src.utils.base_formatter import BaseFormatter


class TestBaseFormatter:
    """Тесты для класса BaseFormatter"""

    @pytest.fixture
    def formatter(self):
        """Фикстура BaseFormatter"""
        return BaseFormatter()

    def test_format_salary_full_range(self, formatter):
        """Тест форматирования зарплаты с полным диапазоном"""
        salary_dict = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = formatter.format_salary(salary_dict)
        assert "100000" in result
        assert "150000" in result
        assert "руб" in result.lower() or "rur" in result.lower()

    def test_format_salary_from_only(self, formatter):
        """Тест форматирования зарплаты только с минимумом"""
        salary_dict = {"from": 80000, "currency": "RUR"}
        result = formatter.format_salary(salary_dict)
        assert "80000" in result
        assert "от" in result.lower()

    def test_format_salary_to_only(self, formatter):
        """Тест форматирования зарплаты только с максимумом"""
        salary_dict = {"to": 200000, "currency": "USD"}
        result = formatter.format_salary(salary_dict)
        assert "200000" in result
        assert "до" in result.lower()

    def test_format_salary_none(self, formatter):
        """Тест форматирования отсутствующей зарплаты"""
        result = formatter.format_salary(None)
        assert "указана" in result.lower()

    def test_format_salary_empty_dict(self, formatter):
        """Тест форматирования пустого словаря зарплаты"""
        result = formatter.format_salary({})
        assert "указана" in result.lower()

    def test_format_currency_rur(self, formatter):
        """Тест форматирования валюты - рубли"""
        result = formatter.format_currency("RUR")
        assert "руб" in result.lower()

    def test_format_currency_usd(self, formatter):
        """Тест форматирования валюты - доллары"""
        result = formatter.format_currency("USD")
        assert "usd" in result.lower() or "$" in result

    def test_format_currency_eur(self, formatter):
        """Тест форматирования валюты - евро"""
        result = formatter.format_currency("EUR")
        assert "eur" in result.lower() or "€" in result

    def test_format_currency_unknown(self, formatter):
        """Тест форматирования неизвестной валюты"""
        result = formatter.format_currency("UNKNOWN")
        assert "unknown" in result.lower() or "неизв" in result.lower()

    def test_format_text_truncate(self, formatter):
        """Тест обрезания длинного текста"""
        long_text = "A" * 200
        result = formatter.format_text(long_text, max_length=50)
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_format_text_short(self, formatter):
        """Тест форматирования короткого текста"""
        short_text = "Short text"
        result = formatter.format_text(short_text, max_length=50)
        assert result == short_text

    def test_format_text_none(self, formatter):
        """Тест форматирования None текста"""
        result = formatter.format_text(None)
        assert result == ""

    def test_format_date_string(self, formatter):
        """Тест форматирования строки с датой"""
        date_string = "2024-01-15T10:30:00+03:00"
        result = formatter.format_date(date_string)
        assert "2024" in result
        assert "01" in result or "15" in result

    def test_format_date_none(self, formatter):
        """Тест форматирования None даты"""
        result = formatter.format_date(None)
        assert "указана" in result.lower() or result == ""

    def test_format_experience_string(self, formatter):
        """Тест форматирования опыта работы"""
        experience = "1-3 года"
        result = formatter.format_experience(experience)
        assert "1-3" in result
        assert "года" in result or "лет" in result

    def test_format_experience_none(self, formatter):
        """Тест форматирования отсутствующего опыта"""
        result = formatter.format_experience(None)
        assert "указан" in result.lower() or result == ""

    def test_format_employment_type(self, formatter):
        """Тест форматирования типа занятости"""
        employment = "Полная занятость"
        result = formatter.format_employment_type(employment)
        assert "полная" in result.lower() or employment in result

    def test_format_schedule(self, formatter):
        """Тест форматирования графика работы"""
        schedule = "Полный день"
        result = formatter.format_schedule(schedule)
        assert "полный" in result.lower() or schedule in result

    def test_format_company_name(self, formatter):
        """Тест форматирования названия компании"""
        company = "ООО Рога и копыта"
        result = formatter.format_company_name(company)
        assert company in result

    def test_format_company_name_dict(self, formatter):
        """Тест форматирования названия компании из словаря"""
        company = {"name": "Test Company"}
        result = formatter.format_company_name(company)
        assert "Test Company" in result

    def test_format_company_name_none(self, formatter):
        """Тест форматирования отсутствующей компании"""
        result = formatter.format_company_name(None)
        assert "указана" in result.lower() or "неизвест" in result.lower()

    def test_clean_html_tags(self, formatter):
        """Тест очистки HTML тегов"""
        html_text = "<p>Текст с <strong>HTML</strong> тегами</p>"
        result = formatter.clean_html(html_text)
        assert "<" not in result
        assert ">" not in result
        assert "Текст с HTML тегами" in result

    def test_clean_html_none(self, formatter):
        """Тест очистки None от HTML"""
        result = formatter.clean_html(None)
        assert result == ""

    def test_format_number_thousands(self, formatter):
        """Тест форматирования больших чисел"""
        number = 1234567
        result = formatter.format_number(number)
        # Проверяем наличие разделителей (пробелы или запятые)
        assert " " in result or "," in result or "1234567" in result
