
"""
Полные тесты для BaseFormatter
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
        if not vacancy:
            return ""
        
        title = str(vacancy.get('name', 'Без названия'))
        if number:
            return f"{number}. {title}"
        return title
    
    def format_salary(self, salary):
        if not salary:
            return "Не указано"
        
        if isinstance(salary, dict):
            from_sal = salary.get('from')
            to_sal = salary.get('to')
            currency = salary.get('currency', 'RUR')
            
            if from_sal and to_sal:
                return f"{from_sal}-{to_sal} {currency}"
            elif from_sal:
                return f"от {from_sal} {currency}"
            elif to_sal:
                return f"до {to_sal} {currency}"
        
        return str(salary)
    
    def format_currency(self, currency):
        currency_map = {
            'RUR': '₽',
            'USD': '$',
            'EUR': '€'
        }
        return currency_map.get(currency, currency)
    
    def format_text(self, text, max_length=150):
        if not text:
            return ""
        
        text = str(text).strip()
        if len(text) <= max_length:
            return text
        
        return text[:max_length].rsplit(' ', 1)[0] + '...'
    
    def format_date(self, date_str):
        if not date_str:
            return "Дата не указана"
        return str(date_str)
    
    def format_experience(self, experience):
        if not experience:
            return "Опыт не указан"
        
        if isinstance(experience, dict):
            return experience.get('name', str(experience))
        return str(experience)
    
    def format_employment_type(self, employment):
        if not employment:
            return "Тип занятости не указан"
        
        if isinstance(employment, dict):
            return employment.get('name', str(employment))
        return str(employment)
    
    def format_schedule(self, schedule):
        if not schedule:
            return "График не указан"
        
        if isinstance(schedule, dict):
            return schedule.get('name', str(schedule))
        return str(schedule)
    
    def format_company_name(self, company):
        if not company:
            return "Компания не указана"
        
        if isinstance(company, dict):
            return company.get('name', str(company))
        return str(company)
    
    def clean_html_tags(self, text):
        if not text:
            return ""
        
        import re
        # Простая очистка HTML тегов
        text = str(text)
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()
    
    def format_number(self, number):
        if number is None:
            return "0"
        
        try:
            return f"{int(number):,}".replace(',', ' ')
        except (ValueError, TypeError):
            return str(number)


@pytest.mark.skipif(not BASE_FORMATTER_AVAILABLE, reason="BaseFormatter not available")
class TestBaseFormatterComplete:
    """Полное тестирование BaseFormatter"""
    
    @pytest.fixture
    def formatter(self):
        """Экземпляр конкретной реализации форматтера"""
        return ConcreteFormatter()
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Тест что базовый класс абстрактный"""
        with pytest.raises(TypeError):
            BaseFormatter()
    
    def test_format_vacancy_info_basic(self, formatter):
        """Тест базового форматирования информации о вакансии"""
        vacancy = {"name": "Python Developer"}
        result = formatter.format_vacancy_info(vacancy)
        assert result == "Python Developer"
    
    def test_format_vacancy_info_with_number(self, formatter):
        """Тест форматирования с номером"""
        vacancy = {"name": "Python Developer"}
        result = formatter.format_vacancy_info(vacancy, number=1)
        assert result == "1. Python Developer"
    
    def test_format_vacancy_info_empty(self, formatter):
        """Тест форматирования пустой вакансии"""
        result = formatter.format_vacancy_info(None)
        assert result == ""
        
        result2 = formatter.format_vacancy_info({})
        assert result2 == "Без названия"
    
    def test_format_salary_dict_both_values(self, formatter):
        """Тест форматирования зарплаты со всеми значениями"""
        salary = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = formatter.format_salary(salary)
        assert result == "100000-150000 RUR"
    
    def test_format_salary_dict_from_only(self, formatter):
        """Тест форматирования зарплаты только с минимумом"""
        salary = {"from": 100000, "currency": "USD"}
        result = formatter.format_salary(salary)
        assert result == "от 100000 USD"
    
    def test_format_salary_dict_to_only(self, formatter):
        """Тест форматирования зарплаты только с максимумом"""
        salary = {"to": 150000, "currency": "EUR"}
        result = formatter.format_salary(salary)
        assert result == "до 150000 EUR"
    
    def test_format_salary_none(self, formatter):
        """Тест форматирования отсутствующей зарплаты"""
        result = formatter.format_salary(None)
        assert result == "Не указано"
    
    def test_format_salary_string(self, formatter):
        """Тест форматирования зарплаты как строки"""
        result = formatter.format_salary("договорная")
        assert result == "договорная"
    
    def test_format_currency_known(self, formatter):
        """Тест форматирования известных валют"""
        assert formatter.format_currency("RUR") == "₽"
        assert formatter.format_currency("USD") == "$"
        assert formatter.format_currency("EUR") == "€"
    
    def test_format_currency_unknown(self, formatter):
        """Тест форматирования неизвестной валюты"""
        result = formatter.format_currency("GBP")
        assert result == "GBP"
    
    def test_format_text_short(self, formatter):
        """Тест форматирования короткого текста"""
        text = "Короткий текст"
        result = formatter.format_text(text, max_length=50)
        assert result == "Короткий текст"
    
    def test_format_text_long(self, formatter):
        """Тест форматирования длинного текста"""
        text = "Это очень длинный текст который должен быть обрезан до определенной длины для корректного отображения"
        result = formatter.format_text(text, max_length=30)
        assert len(result) <= 33  # С учетом '...'
        assert result.endswith('...')
    
    def test_format_text_empty(self, formatter):
        """Тест форматирования пустого текста"""
        assert formatter.format_text("") == ""
        assert formatter.format_text(None) == ""
        assert formatter.format_text("   ") == ""
    
    def test_format_date_valid(self, formatter):
        """Тест форматирования даты"""
        date_str = "2024-01-01"
        result = formatter.format_date(date_str)
        assert result == "2024-01-01"
    
    def test_format_date_empty(self, formatter):
        """Тест форматирования пустой даты"""
        result = formatter.format_date("")
        assert result == "Дата не указана"
        
        result2 = formatter.format_date(None)
        assert result2 == "Дата не указана"
    
    def test_format_experience_dict(self, formatter):
        """Тест форматирования опыта как словаря"""
        experience = {"name": "От 1 до 3 лет"}
        result = formatter.format_experience(experience)
        assert result == "От 1 до 3 лет"
    
    def test_format_experience_string(self, formatter):
        """Тест форматирования опыта как строки"""
        result = formatter.format_experience("3 года")
        assert result == "3 года"
    
    def test_format_experience_empty(self, formatter):
        """Тест форматирования отсутствующего опыта"""
        result = formatter.format_experience(None)
        assert result == "Опыт не указан"
    
    def test_format_employment_type_dict(self, formatter):
        """Тест форматирования типа занятости как словаря"""
        employment = {"name": "Полная занятость"}
        result = formatter.format_employment_type(employment)
        assert result == "Полная занятость"
    
    def test_format_employment_type_string(self, formatter):
        """Тест форматирования типа занятости как строки"""
        result = formatter.format_employment_type("Частичная занятость")
        assert result == "Частичная занятость"
    
    def test_format_employment_type_empty(self, formatter):
        """Тест форматирования отсутствующего типа занятости"""
        result = formatter.format_employment_type(None)
        assert result == "Тип занятости не указан"
    
    def test_format_schedule_dict(self, formatter):
        """Тест форматирования графика как словаря"""
        schedule = {"name": "Полный день"}
        result = formatter.format_schedule(schedule)
        assert result == "Полный день"
    
    def test_format_schedule_string(self, formatter):
        """Тест форматирования графика как строки"""
        result = formatter.format_schedule("Гибкий график")
        assert result == "Гибкий график"
    
    def test_format_schedule_empty(self, formatter):
        """Тест форматирования отсутствующего графика"""
        result = formatter.format_schedule(None)
        assert result == "График не указан"
    
    def test_format_company_name_dict(self, formatter):
        """Тест форматирования названия компании как словаря"""
        company = {"name": "Яндекс"}
        result = formatter.format_company_name(company)
        assert result == "Яндекс"
    
    def test_format_company_name_string(self, formatter):
        """Тест форматирования названия компании как строки"""
        result = formatter.format_company_name("Google")
        assert result == "Google"
    
    def test_format_company_name_empty(self, formatter):
        """Тест форматирования отсутствующего названия компании"""
        result = formatter.format_company_name(None)
        assert result == "Компания не указана"
    
    def test_clean_html_tags_basic(self, formatter):
        """Тест очистки HTML тегов"""
        html_text = "<p>Текст с <b>жирным</b> шрифтом</p>"
        result = formatter.clean_html_tags(html_text)
        assert result == "Текст с жирным шрифтом"
    
    def test_clean_html_tags_complex(self, formatter):
        """Тест очистки сложных HTML тегов"""
        html_text = '<div class="content"><h1>Заголовок</h1><p style="color:red;">Параграф</p></div>'
        result = formatter.clean_html_tags(html_text)
        assert result == "ЗаголовокПараграф"
    
    def test_clean_html_tags_empty(self, formatter):
        """Тест очистки пустого текста"""
        assert formatter.clean_html_tags("") == ""
        assert formatter.clean_html_tags(None) == ""
    
    def test_clean_html_tags_no_tags(self, formatter):
        """Тест очистки текста без тегов"""
        text = "Обычный текст без тегов"
        result = formatter.clean_html_tags(text)
        assert result == "Обычный текст без тегов"
    
    def test_format_number_integer(self, formatter):
        """Тест форматирования целого числа"""
        result = formatter.format_number(123456)
        assert result == "123 456"
    
    def test_format_number_float(self, formatter):
        """Тест форматирования дробного числа"""
        result = formatter.format_number(123456.789)
        assert result == "123 456"
    
    def test_format_number_zero(self, formatter):
        """Тест форматирования нуля"""
        result = formatter.format_number(0)
        assert result == "0"
    
    def test_format_number_none(self, formatter):
        """Тест форматирования None"""
        result = formatter.format_number(None)
        assert result == "0"
    
    def test_format_number_invalid(self, formatter):
        """Тест форматирования невалидного числа"""
        result = formatter.format_number("не число")
        assert result == "не число"
    
    def test_format_number_string_number(self, formatter):
        """Тест форматирования числа как строки"""
        result = formatter.format_number("123456")
        assert result == "123 456"
    
    def test_all_abstract_methods_implemented(self, formatter):
        """Тест что все абстрактные методы реализованы"""
        # Проверяем что все необходимые методы существуют
        required_methods = [
            'format_vacancy_info', 'format_salary', 'format_currency',
            'format_text', 'format_date', 'format_experience',
            'format_employment_type', 'format_schedule', 'format_company_name',
            'clean_html_tags', 'format_number'
        ]
        
        for method_name in required_methods:
            assert hasattr(formatter, method_name)
            assert callable(getattr(formatter, method_name))


@pytest.mark.skipif(not BASE_FORMATTER_AVAILABLE, reason="BaseFormatter not available")
class TestBaseFormatterIntegration:
    """Интеграционные тесты BaseFormatter"""
    
    def test_complex_vacancy_formatting(self):
        """Тест комплексного форматирования вакансии"""
        formatter = ConcreteFormatter()
        
        complex_vacancy = {
            "name": "Senior Python Developer",
            "salary": {"from": 150000, "to": 200000, "currency": "RUR"},
            "experience": {"name": "От 3 до 6 лет"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Удаленная работа"},
            "employer": {"name": "Яндекс"},
            "description": "<p>Ищем <b>опытного</b> разработчика для работы в команде</p>"
        }
        
        # Тестируем форматирование различных полей
        title = formatter.format_vacancy_info(complex_vacancy, number=1)
        assert "1. Senior Python Developer" == title
        
        salary = formatter.format_salary(complex_vacancy["salary"])
        assert "150000-200000 RUR" == salary
        
        experience = formatter.format_experience(complex_vacancy["experience"])
        assert "От 3 до 6 лет" == experience
        
        clean_description = formatter.clean_html_tags(complex_vacancy["description"])
        assert "Ищем опытного разработчика для работы в команде" == clean_description
    
    def test_edge_cases_handling(self):
        """Тест обработки граничных случаев"""
        formatter = ConcreteFormatter()
        
        # Различные типы некорректных данных
        edge_cases = [None, "", {}, [], 0, False]
        
        for case in edge_cases:
            # Методы не должны падать на граничных случаях
            try:
                formatter.format_vacancy_info(case)
                formatter.format_salary(case)
                formatter.format_experience(case)
                formatter.format_company_name(case)
                formatter.clean_html_tags(case)
                formatter.format_number(case)
            except Exception as e:
                pytest.fail(f"Formatter failed on edge case {case}: {e}")
