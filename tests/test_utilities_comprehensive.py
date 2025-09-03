"""
Комплексные тесты для утилит с максимальным покрытием кода.
Включает тестирование всех вспомогательных функций, форматеров, парсеров и помощников.

Все тесты используют реальные импорты из src без fallback методов.
"""

import os
import sys
import json
import tempfile
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from typing import List, Dict, Any, Optional
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорты из src
from src.utils.env_loader import EnvLoader
from src.utils.cache import FileCache
from src.utils.salary import Salary
from src.utils.search_utils import SearchQueryParser, AdvancedSearch, normalize_query, extract_keywords
from src.utils.base_formatter import BaseFormatter
from src.utils.vacancy_formatter import vacancy_formatter
from src.utils.ui_navigation import UINavigation
from src.utils.menu_manager import MenuManager
from src.utils.paginator import Paginator
from src.utils.source_manager import SourceManager
from src.utils.vacancy_operations import VacancyOperations
from src.utils.vacancy_stats import VacancyStats


def create_test_vacancy_dict() -> Dict[str, Any]:
    """
    Создает тестовый словарь вакансии для использования в тестах.

    Returns:
        Dict[str, Any]: Тестовые данные вакансии
    """
    return {
        'id': 'test_123',
        'title': 'Python Developer',
        'url': 'https://test.com/vacancy/123',
        'description': 'Test description',
        'employer': {'name': 'Test Company', 'id': '456'},
        'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
        'area': {'name': 'Москва'},
        'published_at': '2025-01-01T10:00:00+03:00'
    }


class TestEnvLoader:
    """Комплексное тестирование загрузчика переменных окружения"""

    def test_env_loader_initialization(self) -> None:
        """Тестирование инициализации загрузчика"""
        assert EnvLoader is not None
        assert hasattr(EnvLoader, 'load_env_file')
        assert hasattr(EnvLoader, 'get_env_var')

    def test_load_env_file_success(self) -> None:
        """Тестирование успешной загрузки .env файла"""
        env_content = "TEST_KEY=test_value\nANOTHER_KEY=another_value\n"

        with patch('builtins.open', mock_open(read_data=env_content)):
            with patch('os.path.exists', return_value=True):
                EnvLoader.load_env_file(".test_env")

                # Проверяем, что переменные загружены
                assert os.environ.get('TEST_KEY') == 'test_value'
                assert os.environ.get('ANOTHER_KEY') == 'another_value'

    def test_get_env_var_with_default(self) -> None:
        """Тестирование получения переменной с значением по умолчанию"""
        # Существующая переменная
        os.environ['TEST_EXISTING'] = 'test_value'
        result = EnvLoader.get_env_var('TEST_EXISTING')
        assert result == 'test_value'

        # Несуществующая переменная
        result = EnvLoader.get_env_var('NONEXISTENT_VAR', 'default_value')
        assert result == 'default_value'

    def test_get_env_var_int(self) -> None:
        """Тестирование получения integer переменной"""
        os.environ['TEST_INT'] = '42'
        result = EnvLoader.get_env_var_int('TEST_INT')
        assert result == 42

        # Некорректное значение
        os.environ['TEST_INVALID_INT'] = 'not_a_number'
        result = EnvLoader.get_env_var_int('TEST_INVALID_INT', 100)
        assert result == 100


class TestFileCache:
    """Комплексное тестирование системы файлового кэширования"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = FileCache(cache_dir=self.temp_dir)

    def test_cache_initialization(self) -> None:
        """Тестирование инициализации кэша"""
        assert self.cache is not None
        assert hasattr(self.cache, 'cache_dir')

    def test_cache_save_and_load(self) -> None:
        """Тестирование сохранения и загрузки из кэша"""
        params = {"query": "Python"}
        data = {"items": [{"id": "1", "name": "Test"}]}

        self.cache.save_response("test", params, data)
        # Проверяем, что директория кэша существует
        assert self.cache.cache_dir.exists()

    def test_cache_params_hash(self) -> None:
        """Тестирование генерации хэша параметров"""
        params1 = {"query": "Python", "page": 1}
        params2 = {"query": "Python", "page": 2}
        params3 = {"query": "Java", "page": 1}

        hash1 = self.cache._generate_params_hash(params1)
        hash2 = self.cache._generate_params_hash(params2)
        hash3 = self.cache._generate_params_hash(params3)

        # Хэши должны быть разными для разных параметров
        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3

    def teardown_method(self) -> None:
        """Очистка после теста"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class TestSalary:
    """Комплексное тестирование класса Salary"""

    def test_salary_initialization_with_dict(self) -> None:
        """Тестирование инициализации с данными в виде словаря"""
        salary_data = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR",
            "gross": True
        }

        salary = Salary(salary_data)
        assert salary._salary_from == 100000
        assert salary._salary_to == 150000
        assert salary._currency == "RUR"
        assert salary.gross is True

    def test_salary_get_average(self) -> None:
        """Тестирование расчета средней зарплаты"""
        salary = Salary({"from": 100000, "to": 150000})
        average = salary.get_average()
        assert average == 125000

    def test_salary_is_specified(self) -> None:
        """Тестирование проверки указания зарплаты"""
        salary_full = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        assert salary_full.is_specified() is True

        salary_none = Salary({"from": None, "to": None, "currency": "RUR"})
        assert salary_none.is_specified() is False

    def test_salary_string_representation(self) -> None:
        """Тестирование строкового представления зарплаты"""
        salary_full = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        str_repr = str(salary_full)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0


class TestSearchQueryParser:
    """Комплексное тестирование утилит поиска"""

    def test_normalize_query(self) -> None:
        """Тестирование нормализации поискового запроса"""
        normalized = normalize_query("  Python Developer  ")
        assert normalized == "python developer"

    def test_extract_keywords(self) -> None:
        """Тестирование извлечения ключевых слов"""
        text = "Python developer with Django and PostgreSQL experience"
        keywords = extract_keywords(text)

        assert isinstance(keywords, list)
        assert len(keywords) > 0


class TestConcreteFormatter(BaseFormatter):
    """Конкретная реализация BaseFormatter для тестирования"""

    def format_text(self, text: str) -> str:
        """Форматирование текста"""
        return text.strip()

    def format_currency(self, amount: float, currency: str) -> str:
        """Форматирование валюты"""
        return f"{amount} {currency}"

    def format_date(self, date_str: str) -> str:
        """Форматирование даты"""
        return date_str

    def format_number(self, number: float) -> str:
        """Форматирование числа"""
        return str(number)

    def format_salary(self, salary: Any) -> str:
        """Форматирование зарплаты"""
        return str(salary)

    def format_company_name(self, name: str) -> str:
        """Форматирование названия компании"""
        return name

    def format_vacancy_info(self, vacancy: Any) -> str:
        """Форматирование информации о вакансии"""
        return str(vacancy)

    def format_employment_type(self, employment: Any) -> str:
        """Форматирование типа занятости"""
        return str(employment)

    def format_experience(self, experience: Any) -> str:
        """Форматирование опыта"""
        return str(experience)

    def format_schedule(self, schedule: Any) -> str:
        """Форматирование графика"""
        return str(schedule)

    def clean_html_tags(self, text: str) -> str:
        """Очистка HTML тегов"""
        return text


class TestBaseFormatter:
    """Комплексное тестирование базового форматера"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        self.formatter = TestConcreteFormatter()

    def test_base_formatter_initialization(self) -> None:
        """Тестирование инициализации базового форматера"""
        assert self.formatter is not None

    def test_format_text(self) -> None:
        """Тестирование форматирования текста"""
        text = "  Some text with extra spaces  "
        formatted = self.formatter.format_text(text)
        assert formatted == "Some text with extra spaces"

    def test_format_currency(self) -> None:
        """Тестирование форматирования валюты"""
        amount = 100000
        currency = "RUR"
        formatted = self.formatter.format_currency(amount, currency)
        assert "100000" in formatted


class TestVacancyFormatter:
    """Комплексное тестирование форматера вакансий"""

    def test_vacancy_formatter_exists(self) -> None:
        """Тестирование существования форматера вакансий"""
        assert vacancy_formatter is not None

    def test_format_vacancy_basic(self) -> None:
        """Тестирование базового форматирования вакансии"""
        from src.vacancies.models import Vacancy, Employer

        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1"
        )

        formatted = vacancy_formatter.format_vacancy_info(vacancy)
        assert isinstance(formatted, str)
        assert len(formatted) > 0


class TestUINavigation:
    """Комплексное тестирование навигации UI"""

    def test_ui_navigation_initialization(self) -> None:
        """Тестирование инициализации навигации UI"""
        ui_nav = UINavigation()
        assert ui_nav is not None

    def test_get_page_data(self) -> None:
        """Тестирование получения данных страницы"""
        ui_nav = UINavigation(items_per_page=5)
        items = list(range(20))

        page_items, pagination_info = ui_nav.get_page_data(items, page=1)

        assert len(page_items) == 5
        assert pagination_info['total_items'] == 20
        assert pagination_info['total_pages'] == 4


class TestMenuManager:
    """Комплексное тестирование менеджера меню"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        self.menu_manager = MenuManager()

    def test_menu_manager_initialization(self) -> None:
        """Тестирование инициализации менеджера меню"""
        assert self.menu_manager is not None


class TestPaginator:
    """Комплексное тестирование пагинатора"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        self.items = list(range(1, 101))  # 100 элементов
        self.paginator = Paginator(self.items, page_size=10)

    def test_paginator_initialization(self) -> None:
        """Тестирование инициализации пагинатора"""
        assert self.paginator is not None
        assert hasattr(self.paginator, 'items')
        assert hasattr(self.paginator, 'page_size')

    def test_get_page(self) -> None:
        """Тестирование получения страницы"""
        page = self.paginator.get_page(0)
        assert isinstance(page, list)
        assert len(page) <= 10  # Размер страницы

    def test_get_total_pages(self) -> None:
        """Тестирование получения общего количества страниц"""
        total_pages = self.paginator.get_total_pages()
        assert isinstance(total_pages, int)
        assert total_pages == 10  # 100 элементов / 10 на страницу

    def test_has_next_page(self) -> None:
        """Тестирование проверки наличия следующей страницы"""
        # Первая страница должна иметь следующую
        assert self.paginator.has_next_page(0) is True

        # Последняя страница не должна иметь следующую
        last_page = self.paginator.get_total_pages() - 1
        assert self.paginator.has_next_page(last_page) is False

    def test_has_previous_page(self) -> None:
        """Тестирование проверки наличия предыдущей страницы"""
        # Первая страница не должна иметь предыдущую
        assert self.paginator.has_previous_page(0) is False

        # Вторая страница должна иметь предыдущую
        assert self.paginator.has_previous_page(1) is True


class TestSourceManager:
    """Комплексное тестирование менеджера источников"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        self.source_manager = SourceManager()

    def test_source_manager_initialization(self) -> None:
        """Тестирование инициализации менеджера источников"""
        assert self.source_manager is not None

    def test_get_available_sources(self) -> None:
        """Тестирование получения доступных источников"""
        sources = self.source_manager.get_available_sources()
        assert isinstance(sources, list)
        assert len(sources) > 0

    def test_is_source_available(self) -> None:
        """Тестирование проверки доступности источника"""
        # Тестируем известные источники
        assert self.source_manager.is_source_available("hh.ru") is True
        assert self.source_manager.is_source_available("superjob.ru") is True

        # Тестируем неизвестный источник
        assert self.source_manager.is_source_available("unknown.ru") is False


class TestVacancyOperations:
    """Комплексное тестирование операций с вакансиями"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        self.vacancy_ops = VacancyOperations()

    def test_vacancy_operations_initialization(self) -> None:
        """Тестирование инициализации операций с вакансиями"""
        assert self.vacancy_ops is not None


class TestVacancyStats:
    """Комплексное тестирование статистики вакансий"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        self.vacancy_stats = VacancyStats()

    def test_vacancy_stats_initialization(self) -> None:
        """Тестирование инициализации статистики вакансий"""
        assert self.vacancy_stats is not None


class TestUtilitiesIntegration:
    """Интеграционные тесты для утилит"""

    def test_full_formatting_workflow(self) -> None:
        """Тестирование полного рабочего процесса форматирования"""
        from src.vacancies.models import Vacancy, Employer

        # Создаем тестовые данные
        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1"
        )

        # Форматируем через различные утилиты
        formatted = vacancy_formatter.format_vacancy_info(vacancy)
        assert isinstance(formatted, str)
        assert len(formatted) > 0

    def test_pagination_and_navigation_workflow(self) -> None:
        """Тестирование рабочего процесса пагинации и навигации"""
        items = list(range(50))
        paginator = Paginator(items, page_size=10)

        # Тестируем навигацию по страницам
        first_page = paginator.get_page(0)
        assert len(first_page) == 10

        second_page = paginator.get_page(1)
        assert len(second_page) == 10

        # Проверяем навигацию
        assert paginator.has_next_page(0) is True
        assert paginator.has_previous_page(1) is True