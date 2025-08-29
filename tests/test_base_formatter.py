
"""
Тесты для базового форматировщика
"""

import pytest
from src.utils.base_formatter import BaseFormatter


class ConcreteFormatter(BaseFormatter):
    """Конкретная реализация BaseFormatter для тестирования"""
    
    def format_vacancy_info(self, vacancy, number=None):
        """Заглушка для абстрактного метода"""
        return f"Test format for vacancy: {vacancy}"

    def format_salary(self, salary):
        """Форматирование зарплаты"""
        if not salary:
            return "Не указана"
        
        if isinstance(salary, dict):
            from_salary = salary.get("from")
            to_salary = salary.get("to")
            currency = salary.get("currency", "RUR")
            
            currency_symbol = self.format_currency(currency)
            
            if from_salary and to_salary:
                return f"от {from_salary:,} до {to_salary:,} {currency_symbol}".replace(",", ",")
            elif from_salary:
                return f"от {from_salary:,} {currency_symbol}".replace(",", ",")
            elif to_salary:
                return f"до {to_salary:,} {currency_symbol}".replace(",", ",")
            else:
                return "Не указана"
        
        return str(salary)

    def format_currency(self, currency):
        """Форматирование валюты"""
        currency_map = {
            "RUR": "₽",
            "RUB": "₽", 
            "USD": "$",
            "EUR": "€"
        }
        return currency_map.get(currency, currency)

    def format_text(self, text, max_length=150):
        """Форматирование текста с усечением"""
        if not text:
            return "Не указано"
        
        if len(text) > max_length:
            return text[:max_length] + "..."
        
        return text

    def format_date(self, date_str):
        """Форматирование даты"""
        if not date_str:
            return "Не указано"
        
        # Простое форматирование для тестов
        if "T" in date_str:
            date_part = date_str.split("T")[0]
            parts = date_part.split("-")
            if len(parts) == 3:
                return f"{parts[2]}.{parts[1]}.{parts[0]}"
        
        return date_str

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
        
        if isinstance(company, dict):
            return company.get("name", "Не указана")
        
        return str(company)

    def clean_html_tags(self, text):
        """Очистка HTML тегов"""
        if not text:
            return ""
        
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def format_number(self, number):
        """Форматирование числа с разделителями тысяч"""
        if not isinstance(number, (int, float)):
            return str(number)
        
        return f"{number:,}"


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

    def test_abstract_instantiation(self):
        """Тест что BaseFormatter нельзя инстанцировать напрямую"""
        with pytest.raises(TypeError):
            BaseFormatter()
"""
Тесты для базового форматтера вакансий
"""

import pytest
from abc import ABC
from src.utils.base_formatter import BaseFormatter


class ConcreteFormatter(BaseFormatter):
    """Конкретная реализация BaseFormatter для тестирования"""
    
    def format_vacancy_info(self, vacancy, number=None):
        return f"Vacancy {number}: {vacancy.get('title', 'No title')}"
    
    def format_salary(self, salary):
        if not salary:
            return "No salary"
        return f"${salary}"
    
    def format_currency(self, currency):
        return currency.upper()
    
    def format_text(self, text, max_length=150):
        if not text:
            return ""
        return text[:max_length] + "..." if len(text) > max_length else text
    
    def format_date(self, date_str):
        return date_str or "No date"
    
    def format_experience(self, experience):
        return experience or "No experience"
    
    def format_employment_type(self, employment):
        return employment or "No employment type"
    
    def format_schedule(self, schedule):
        return schedule or "No schedule"
    
    def format_company_name(self, company):
        if isinstance(company, dict):
            return company.get('name', 'Unknown company')
        return str(company) if company else 'Unknown company'
    
    def clean_html_tags(self, text):
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', str(text))
    
    def format_number(self, number):
        return f"{number:,}" if isinstance(number, (int, float)) else str(number)


class TestBaseFormatter:
    """Тесты для BaseFormatter"""
    
    def test_base_formatter_is_abstract(self):
        """Тест что BaseFormatter является абстрактным классом"""
        assert issubclass(BaseFormatter, ABC)
        
        # Проверяем, что нельзя создать экземпляр BaseFormatter
        with pytest.raises(TypeError):
            BaseFormatter()
    
    def test_concrete_formatter_implementation(self):
        """Тест конкретной реализации форматтера"""
        formatter = ConcreteFormatter()
        assert isinstance(formatter, BaseFormatter)
    
    def test_format_vacancy_info(self):
        """Тест форматирования информации о вакансии"""
        formatter = ConcreteFormatter()
        vacancy = {"title": "Python Developer"}
        
        result = formatter.format_vacancy_info(vacancy, 1)
        assert "Vacancy 1: Python Developer" == result
    
    def test_format_vacancy_info_no_number(self):
        """Тест форматирования без номера"""
        formatter = ConcreteFormatter()
        vacancy = {"title": "Java Developer"}
        
        result = formatter.format_vacancy_info(vacancy)
        assert "Vacancy None: Java Developer" == result
    
    def test_format_salary(self):
        """Тест форматирования зарплаты"""
        formatter = ConcreteFormatter()
        
        assert formatter.format_salary(100000) == "$100000"
        assert formatter.format_salary(None) == "No salary"
        assert formatter.format_salary("") == "No salary"
    
    def test_format_currency(self):
        """Тест форматирования валюты"""
        formatter = ConcreteFormatter()
        
        assert formatter.format_currency("usd") == "USD"
        assert formatter.format_currency("eur") == "EUR"
        assert formatter.format_currency("rub") == "RUB"
    
    def test_format_text(self):
        """Тест форматирования текста"""
        formatter = ConcreteFormatter()
        
        short_text = "Short text"
        long_text = "A" * 200
        
        assert formatter.format_text(short_text) == short_text
        assert formatter.format_text(long_text, 50) == "A" * 50 + "..."
        assert formatter.format_text("") == ""
        assert formatter.format_text(None) == ""
    
    def test_format_date(self):
        """Тест форматирования даты"""
        formatter = ConcreteFormatter()
        
        assert formatter.format_date("2024-01-01") == "2024-01-01"
        assert formatter.format_date("") == "No date"
        assert formatter.format_date(None) == "No date"
    
    def test_format_experience(self):
        """Тест форматирования опыта"""
        formatter = ConcreteFormatter()
        
        assert formatter.format_experience("3-6 лет") == "3-6 лет"
        assert formatter.format_experience("") == "No experience"
        assert formatter.format_experience(None) == "No experience"
    
    def test_format_employment_type(self):
        """Тест форматирования типа занятости"""
        formatter = ConcreteFormatter()
        
        assert formatter.format_employment_type("Полная занятость") == "Полная занятость"
        assert formatter.format_employment_type("") == "No employment type"
        assert formatter.format_employment_type(None) == "No employment type"
    
    def test_format_schedule(self):
        """Тест форматирования графика"""
        formatter = ConcreteFormatter()
        
        assert formatter.format_schedule("Полный день") == "Полный день"
        assert formatter.format_schedule("") == "No schedule"
        assert formatter.format_schedule(None) == "No schedule"
    
    def test_format_company_name(self):
        """Тест форматирования названия компании"""
        formatter = ConcreteFormatter()
        
        # Тест с dict
        company_dict = {"name": "Test Company"}
        assert formatter.format_company_name(company_dict) == "Test Company"
        
        # Тест с пустым dict
        empty_dict = {"name": ""}
        assert formatter.format_company_name(empty_dict) == "Unknown company"
        
        # Тест со строкой
        assert formatter.format_company_name("String Company") == "String Company"
        
        # Тест с None
        assert formatter.format_company_name(None) == "Unknown company"
        
        # Тест с пустой строкой
        assert formatter.format_company_name("") == "Unknown company"
    
    def test_clean_html_tags(self):
        """Тест очистки HTML тегов"""
        formatter = ConcreteFormatter()
        
        html_text = "<p>Hello <b>world</b>!</p>"
        clean_text = formatter.clean_html_tags(html_text)
        assert clean_text == "Hello world!"
        
        # Тест без HTML
        plain_text = "Plain text"
        assert formatter.clean_html_tags(plain_text) == plain_text
    
    def test_format_number(self):
        """Тест форматирования числа"""
        formatter = ConcreteFormatter()
        
        assert formatter.format_number(1000) == "1,000"
        assert formatter.format_number(1000000) == "1,000,000"
        assert formatter.format_number(123.45) == "123.45"
        assert formatter.format_number("not a number") == "not a number"
    
    def test_all_abstract_methods_implemented(self):
        """Тест что все абстрактные методы реализованы"""
        formatter = ConcreteFormatter()
        
        # Проверяем, что все методы BaseFormatter реализованы
        base_methods = [
            'format_vacancy_info', 'format_salary', 'format_currency',
            'format_text', 'format_date', 'format_experience',
            'format_employment_type', 'format_schedule', 'format_company_name',
            'clean_html_tags', 'format_number'
        ]
        
        for method_name in base_methods:
            assert hasattr(formatter, method_name)
            assert callable(getattr(formatter, method_name))
