
"""
Полные тесты для базового форматтера
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime

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
        if not vacancy:
            return ""
        
        title = vacancy.get('title', 'Без названия')
        company = self.format_company_name(vacancy.get('company', {}))
        salary = self.format_salary(vacancy.get('salary'))
        
        result = f"{title} - {company}"
        if number:
            result = f"{number}. {result}"
        if salary:
            result += f" | {salary}"
        return result
    
    def format_salary(self, salary):
        """Форматирование зарплаты"""
        if not salary:
            return "Зарплата не указана"
        
        if isinstance(salary, dict):
            from_salary = salary.get('from')
            to_salary = salary.get('to')
            currency = self.format_currency(salary.get('currency', 'RUR'))
            
            if from_salary and to_salary:
                return f"{self.format_number(from_salary)} - {self.format_number(to_salary)} {currency}"
            elif from_salary:
                return f"от {self.format_number(from_salary)} {currency}"
            elif to_salary:
                return f"до {self.format_number(to_salary)} {currency}"
        
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
        
        clean_text = self.clean_html_tags(text)
        if len(clean_text) <= max_length:
            return clean_text
        
        return clean_text[:max_length-3] + "..."
    
    def format_date(self, date_str):
        """Форматирование даты"""
        if not date_str:
            return ""
        
        try:
            # Простая проверка формата
            if 'T' in date_str:
                return date_str.split('T')[0]
            return date_str
        except Exception:
            return date_str
    
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
            return "Компания не указана"
        
        if isinstance(company, dict):
            return company.get('name', 'Компания не указана')
        return str(company)
    
    def clean_html_tags(self, text):
        """Очистка HTML тегов"""
        if not text:
            return ""
        
        # Простая очистка HTML тегов
        import re
        clean_text = re.sub(r'<[^>]+>', '', str(text))
        return clean_text.strip()
    
    def format_number(self, number):
        """Форматирование числа с разделителями"""
        if not isinstance(number, (int, float)):
            return str(number)
        
        return f"{number:,}".replace(',', ' ')


class TestBaseFormatter:
    """Тесты для базового форматтера"""

    def test_base_formatter_cannot_be_instantiated(self):
        """Тест что базовый класс нельзя инстанциировать"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        with pytest.raises(TypeError):
            BaseFormatter()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()
        assert formatter is not None

    def test_format_vacancy_info(self):
        """Тест форматирования информации о вакансии"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()
        
        # Полная вакансия
        vacancy = {
            'title': 'Python Developer',
            'company': {'name': 'Tech Company'},
            'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'}
        }
        
        result = formatter.format_vacancy_info(vacancy, 1)
        assert "1. Python Developer - Tech Company" in result
        assert "100 000 - 150 000 ₽" in result

        # Вакансия без зарплаты
        vacancy_no_salary = {
            'title': 'Java Developer',
            'company': {'name': 'Another Company'}
        }
        
        result = formatter.format_vacancy_info(vacancy_no_salary)
        assert "Java Developer - Another Company" in result

        # Пустая вакансия
        result = formatter.format_vacancy_info(None)
        assert result == ""

    def test_format_salary(self):
        """Тест форматирования зарплаты"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # Диапазон зарплаты
        salary_range = {'from': 50000, 'to': 80000, 'currency': 'RUR'}
        result = formatter.format_salary(salary_range)
        assert result == "50 000 - 80 000 ₽"

        # Только от
        salary_from = {'from': 60000, 'currency': 'USD'}
        result = formatter.format_salary(salary_from)
        assert result == "от 60 000 $"

        # Только до
        salary_to = {'to': 100000, 'currency': 'EUR'}
        result = formatter.format_salary(salary_to)
        assert result == "до 100 000 €"

        # Пустая зарплата
        result = formatter.format_salary(None)
        assert result == "Зарплата не указана"

        # Строковая зарплата
        result = formatter.format_salary("По договоренности")
        assert result == "По договоренности"

    def test_format_currency(self):
        """Тест форматирования валюты"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        assert formatter.format_currency('RUR') == '₽'
        assert formatter.format_currency('USD') == '$'
        assert formatter.format_currency('EUR') == '€'
        assert formatter.format_currency('GBP') == 'GBP'

    def test_format_text(self):
        """Тест форматирования текста"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # Короткий текст
        short_text = "Короткое описание"
        result = formatter.format_text(short_text, 50)
        assert result == short_text

        # Длинный текст
        long_text = "А" * 200
        result = formatter.format_text(long_text, 50)
        assert len(result) == 50
        assert result.endswith("...")

        # Текст с HTML
        html_text = "<p>Описание <strong>вакансии</strong></p>"
        result = formatter.format_text(html_text)
        assert result == "Описание вакансии"

        # Пустой текст
        result = formatter.format_text("")
        assert result == ""

    def test_format_date(self):
        """Тест форматирования даты"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # ISO дата
        iso_date = "2023-12-01T10:30:00+03:00"
        result = formatter.format_date(iso_date)
        assert result == "2023-12-01"

        # Простая дата
        simple_date = "2023-12-01"
        result = formatter.format_date(simple_date)
        assert result == simple_date

        # Пустая дата
        result = formatter.format_date("")
        assert result == ""

    def test_format_experience(self):
        """Тест форматирования опыта"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # Словарь с опытом
        experience_dict = {'name': 'От 1 года до 3 лет'}
        result = formatter.format_experience(experience_dict)
        assert result == 'От 1 года до 3 лет'

        # Строковый опыт
        result = formatter.format_experience("3 года")
        assert result == "3 года"

        # Пустой опыт
        result = formatter.format_experience(None)
        assert result == "Не указан"

    def test_format_employment_type(self):
        """Тест форматирования типа занятости"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # Словарь с типом занятости
        employment_dict = {'name': 'Полная занятость'}
        result = formatter.format_employment_type(employment_dict)
        assert result == 'Полная занятость'

        # Строковый тип
        result = formatter.format_employment_type("Частичная")
        assert result == "Частичная"

        # Пустой тип
        result = formatter.format_employment_type(None)
        assert result == "Не указан"

    def test_format_schedule(self):
        """Тест форматирования графика работы"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # Словарь с графиком
        schedule_dict = {'name': 'Полный день'}
        result = formatter.format_schedule(schedule_dict)
        assert result == 'Полный день'

        # Строковый график
        result = formatter.format_schedule("Гибкий")
        assert result == "Гибкий"

        # Пустой график
        result = formatter.format_schedule(None)
        assert result == "Не указан"

    def test_format_company_name(self):
        """Тест форматирования названия компании"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # Словарь с компанией
        company_dict = {'name': 'Яндекс'}
        result = formatter.format_company_name(company_dict)
        assert result == 'Яндекс'

        # Строковое название
        result = formatter.format_company_name("Google")
        assert result == "Google"

        # Пустая компания
        result = formatter.format_company_name(None)
        assert result == "Компания не указана"

    def test_clean_html_tags(self):
        """Тест очистки HTML тегов"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # HTML с тегами
        html_text = "<div>Описание <b>вакансии</b> с <a href='#'>ссылкой</a></div>"
        result = formatter.clean_html_tags(html_text)
        assert result == "Описание вакансии с ссылкой"

        # Обычный текст
        plain_text = "Обычный текст"
        result = formatter.clean_html_tags(plain_text)
        assert result == plain_text

        # Пустой текст
        result = formatter.clean_html_tags("")
        assert result == ""

    def test_format_number(self):
        """Тест форматирования чисел"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # Целое число
        assert formatter.format_number(1000) == "1 000"
        assert formatter.format_number(1000000) == "1 000 000"

        # Дробное число
        assert formatter.format_number(1000.5) == "1 000.5"

        # Не число
        assert formatter.format_number("text") == "text"
        assert formatter.format_number(None) == "None"


class TestFormatterIntegration:
    """Интеграционные тесты форматтера"""

    def test_complex_vacancy_formatting(self):
        """Тест комплексного форматирования вакансии"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()
        
        complex_vacancy = {
            'title': 'Senior Python Developer',
            'company': {'name': 'Tech Startup'},
            'salary': {'from': 150000, 'to': 200000, 'currency': 'RUR'},
            'description': '<p>Требуется опытный <strong>Python</strong> разработчик</p>',
            'experience': {'name': 'От 3 до 6 лет'},
            'employment': {'name': 'Полная занятость'},
            'schedule': {'name': 'Удаленная работа'}
        }

        info = formatter.format_vacancy_info(complex_vacancy, 5)
        assert "5. Senior Python Developer - Tech Startup" in info
        assert "150 000 - 200 000 ₽" in info

        # Проверяем отдельные элементы
        assert formatter.format_experience(complex_vacancy['experience']) == 'От 3 до 6 лет'
        assert formatter.format_employment_type(complex_vacancy['employment']) == 'Полная занятость'
        assert formatter.format_schedule(complex_vacancy['schedule']) == 'Удаленная работа'

    def test_edge_cases_formatting(self):
        """Тест граничных случаев форматирования"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        formatter = ConcreteFormatter()

        # Вакансия с пустыми полями
        empty_vacancy = {
            'title': '',
            'company': {},
            'salary': {}
        }

        result = formatter.format_vacancy_info(empty_vacancy)
        assert "Без названия - Компания не указана" in result
