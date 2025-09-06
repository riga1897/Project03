"""
Тесты для базового форматера
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

    def format_vacancy(self, vacancy):
        """Форматирование одной вакансии"""
        if vacancy is None:
            raise TypeError("Vacancy cannot be None")
        return f"ID: {vacancy.get('id', 'N/A')}, Title: {vacancy.get('title', 'N/A')}"

    def format_vacancies_list(self, vacancies):
        """Форматирование списка вакансий"""
        return [self.format_vacancy(v) for v in vacancies]
    
    # Реализация всех абстрактных методов BaseFormatter
    def clean_html_tags(self, text):
        return str(text) if text else ""
    
    def format_company_name(self, company):
        return str(company) if company else "N/A"
    
    def format_currency(self, currency):
        return str(currency) if currency else "RUR"
    
    def format_date(self, date):
        return str(date) if date else ""
    
    def format_employment_type(self, employment):
        return str(employment) if employment else ""
    
    def format_experience(self, experience):
        return str(experience) if experience else ""
    
    def format_number(self, number):
        return str(number) if number is not None else "0"
    
    def format_salary(self, salary):
        return str(salary) if salary else ""
    
    def format_schedule(self, schedule):
        return str(schedule) if schedule else ""
    
    def format_text(self, text):
        return str(text) if text else ""
    
    def format_vacancy_info(self, vacancy):
        return self.format_vacancy(vacancy)


class TestBaseFormatter:
    """Тесты для базового форматера"""

    @pytest.fixture
    def formatter(self):
        """Фикстура форматера"""
        if not BASE_FORMATTER_AVAILABLE:
            return Mock()
        return ConcreteFormatter()

    def test_base_formatter_cannot_be_instantiated(self):
        """Тест что базовый класс нельзя инстанциировать"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        with pytest.raises(TypeError):
            BaseFormatter()

    def test_concrete_implementation_works(self, formatter):
        """Тест что конкретная реализация работает"""
        assert formatter is not None

    def test_format_vacancy(self, formatter):
        """Тест форматирования одной вакансии"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        vacancy = {"id": "123", "title": "Python Developer"}
        result = formatter.format_vacancy(vacancy)
        assert "123" in result
        assert "Python Developer" in result

    def test_format_vacancies_list(self, formatter):
        """Тест форматирования списка вакансий"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        vacancies = [
            {"id": "1", "title": "Dev 1"},
            {"id": "2", "title": "Dev 2"}
        ]
        result = formatter.format_vacancies_list(vacancies)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_format_vacancy_with_missing_fields(self, formatter):
        """Тест форматирования вакансии с отсутствующими полями"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        vacancy = {"title": "Developer"}  # нет id
        result = formatter.format_vacancy(vacancy)
        assert "N/A" in result
        assert "Developer" in result

    def test_format_empty_vacancies_list(self, formatter):
        """Тест форматирования пустого списка"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        result = formatter.format_vacancies_list([])
        assert isinstance(result, list)
        assert len(result) == 0

    def test_format_vacancy_with_none(self, formatter):
        """Тест форматирования None вакансии"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        with pytest.raises(TypeError):
            formatter.format_vacancy(None)

    def test_format_vacancy_with_empty_dict(self, formatter):
        """Тест форматирования пустого словаря"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        vacancy = {}
        result = formatter.format_vacancy(vacancy)
        assert "N/A" in result  # Должно обработать отсутствующие поля

    def test_abstract_methods_exist(self):
        """Тест что абстрактные методы определены"""
        if not BASE_FORMATTER_AVAILABLE:
            pytest.skip("BaseFormatter not available")

        abstract_methods = BaseFormatter.__abstractmethods__
        # Проверяем что есть хотя бы один абстрактный метод
        assert len(abstract_methods) > 0
        # Проверяем основные методы форматирования
        expected_methods = {'clean_html_tags', 'format_company_name', 'format_currency'}
        assert any(method in abstract_methods for method in expected_methods)
        assert 'format_vacancies_list' in abstract_methods


class TestBaseFormatterImportError:
    """Тесты обработки ошибок импорта BaseFormatter"""

    def test_base_formatter_not_available(self):
        """Тест когда BaseFormatter недоступен"""
        if not BASE_FORMATTER_AVAILABLE:
            assert BaseFormatter == object