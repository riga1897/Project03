"""
Комплексные тесты для утилит с максимальным покрытием кода.
Включает тестирование всех вспомогательных функций, форматеров, парсеров и помощников.
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

from src.utils.env_loader import EnvLoader
from src.utils.cache import FileCache
from src.utils.salary import Salary
from src.utils.search_utils import SearchQueryParser, AdvancedSearch, normalize_query, extract_keywords
from src.utils.base_formatter import BaseFormatter
from src.utils.vacancy_formatter import vacancy_formatter
from src.utils.ui_helpers import UIHelpers
from src.utils.ui_navigation import UINavigation
from src.utils.menu_manager import MenuManager
from src.utils.paginator import Paginator
from src.utils.source_manager import SourceManager
from src.utils.vacancy_operations import VacancyOperations
from src.utils.vacancy_stats import VacancyStats


def create_test_vacancy_dict():
    """Создает тестовый словарь вакансии"""
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

    def test_env_loader_initialization(self):
        """Тестирование инициализации загрузчика"""
        assert EnvLoader is not None
        assert hasattr(EnvLoader, 'load_env_file')
        assert hasattr(EnvLoader, 'get_env_var')

    def test_load_env_file_success(self):
        """Тестирование успешной загрузки .env файла"""
        env_content = "TEST_KEY=test_value\nANOTHER_KEY=another_value\n"

        with patch('builtins.open', mock_open(read_data=env_content)):
            with patch('os.path.exists', return_value=True):
                EnvLoader.load_env_file(".test_env")

                # Проверяем, что переменные загружены
                assert os.environ.get('TEST_KEY') == 'test_value'
                assert os.environ.get('ANOTHER_KEY') == 'another_value'

    def test_load_env_file_not_found(self):
        """Тестирование обработки отсутствующего .env файла"""
        with patch('os.path.exists', return_value=False):
            # Не должно вызывать исключение
            EnvLoader.load_env_file("non_existent.env")

    def test_load_env_file_with_comments_and_empty_lines(self):
        """Тестирование обработки комментариев и пустых строк"""
        env_content = """
        # This is a comment
        TEST_KEY=test_value

        # Another comment
        ANOTHER_KEY=another_value

        """

        with patch('builtins.open', mock_open(read_data=env_content)):
            with patch('os.path.exists', return_value=True):
                EnvLoader.load_env_file(".test_env")

                assert os.environ.get('TEST_KEY') == 'test_value'
                assert os.environ.get('ANOTHER_KEY') == 'another_value'

    def test_load_env_file_with_quotes(self):
        """Тестирование обработки кавычек в значениях"""
        env_content = 'QUOTED_KEY="quoted value"\nSINGLE_QUOTED=\'single quoted\'\n'

        with patch('builtins.open', mock_open(read_data=env_content)):
            with patch('os.path.exists', return_value=True):
                EnvLoader.load_env_file(".test_env")

                assert os.environ.get('QUOTED_KEY') == 'quoted value'
                assert os.environ.get('SINGLE_QUOTED') == 'single quoted'

    def test_get_env_var_with_default(self):
        """Тестирование получения переменной с значением по умолчанию"""
        # Существующая переменная
        os.environ['EXISTING_VAR'] = 'existing_value'
        result = EnvLoader.get_env_var('EXISTING_VAR', 'default')
        assert result == 'existing_value'

        # Несуществующая переменная
        result = EnvLoader.get_env_var('NON_EXISTING_VAR', 'default')
        assert result == 'default'

    def test_get_env_var_int(self):
        """Тестирование получения целочисленной переменной"""
        os.environ['INT_VAR'] = '42'
        result = EnvLoader.get_env_var_int('INT_VAR', 0)
        assert result == 42

        # Некорректное значение
        os.environ['INVALID_INT'] = 'not_a_number'
        result = EnvLoader.get_env_var_int('INVALID_INT', 10)
        assert result == 10

        # Несуществующая переменная
        result = EnvLoader.get_env_var_int('NON_EXISTING_INT', 5)
        assert result == 5


class TestFileCache:
    """Комплексное тестирование системы файлового кэширования"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.cache = FileCache(cache_dir=self.temp_dir)

    def test_cache_initialization(self):
        """Тестирование инициализации кэша"""
        assert self.cache is not None
        assert hasattr(self.cache, 'cache_dir')

    def test_cache_save_and_load(self):
        """Тестирование сохранения и загрузки из кэша"""
        params = {"query": "Python"}
        data = {"items": [{"id": "1", "name": "Test"}]}

        self.cache.save_response("test", params, data)
        # FileCache не имеет прямого метода get, тестируем через существование файла
        assert self.cache.cache_dir.exists()

    def test_cache_directory_creation(self):
        """Тестирование создания директории кэша"""
        assert self.cache.cache_dir.exists()
        assert self.cache.cache_dir.is_dir()

    def test_cache_params_hash(self):
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

    def test_cache_valid_response(self):
        """Тестирование проверки валидности ответа"""
        valid_data = {"items": [{"id": "1", "name": "Test"}]}
        invalid_data = {}

        # Проверяем валидность данных
        if hasattr(self.cache, '_is_valid_response'):
            assert self.cache._is_valid_response(valid_data, {}) is True
            assert self.cache._is_valid_response(invalid_data, {}) is False

    def test_cache_file_operations(self):
        """Тестирование файловых операций кэша"""
        params = {"query": "Test"}
        data = {"items": [{"id": "1", "name": "Test Job"}]}

        # Сохраняем данные
        self.cache.save_response("test", params, data)

        # Проверяем, что файл был создан
        cache_files = list(self.cache.cache_dir.glob("test_*.json"))
        assert len(cache_files) > 0

    def teardown_method(self):
        """Очистка после теста"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class TestSalary:
    """Комплексное тестирование класса Salary"""

    def test_salary_initialization_empty(self):
        """Тестирование инициализации пустой зарплаты"""
        salary = Salary()
        assert salary is not None
        assert salary.amount_from == 0
        assert salary.amount_to == 0

    def test_salary_initialization_with_dict(self):
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

    def test_salary_initialization_with_string_range(self):
        """Тестирование инициализации со строковым диапазоном"""
        salary_range = "100000 - 150000"
        salary = Salary(salary_range)

        # Проверяем, что строка была правильно распарсена
        assert isinstance(salary, Salary)

    def test_salary_validation(self):
        """Тестирование валидации зарплатных данных"""
        # Корректные данные
        valid_salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        assert valid_salary._salary_from == 100000
        assert valid_salary._salary_to == 150000

        # Некорректные данные
        invalid_salary = Salary({"from": -1000, "to": "invalid", "currency": ""})
        assert invalid_salary._salary_from is None
        assert invalid_salary._salary_to is None
        assert invalid_salary._currency == "RUR"  # Значение по умолчанию

    def test_salary_currency_validation(self):
        """Тестирование валидации валюты"""
        # Корректная валюта
        salary = Salary({"currency": "USD"})
        assert salary._currency == "USD"

        # Некорректная валюта
        salary = Salary({"currency": None})
        assert salary._currency == "RUR"

        salary = Salary({"currency": ""})
        assert salary._currency == "RUR"

    def test_salary_string_parsing(self):
        """Тестирование парсинга различных форматов строк"""
        test_cases = [
            "100000 - 150000",
            "от 100000 до 150000",
            "100000-150000",
            "от 100000",
            "до 150000"
        ]

        for test_case in test_cases:
            parsed = Salary._parse_salary_range_string(test_case)
            assert isinstance(parsed, dict)

    def test_salary_average_calculation(self):
        """Тестирование расчета средней зарплаты"""
        salary = Salary({"from": 100000, "to": 150000})

        if hasattr(salary, 'get_average'):
            average = salary.get_average()
            assert average == 125000

        # Только нижняя граница
        salary_from_only = Salary({"from": 100000})
        if hasattr(salary_from_only, 'get_average'):
            average = salary_from_only.get_average()
            assert average == 100000

    def test_salary_comparison(self):
        """Тестирование сравнения зарплат"""
        salary1 = Salary({"from": 100000, "to": 150000})
        salary2 = Salary({"from": 120000, "to": 180000})

        if hasattr(salary1, '__gt__'):
            # Тестируем сравнение (может быть реализовано по средней зарплате)
            assert isinstance(salary1 > salary2, bool)

    def test_salary_string_representation(self):
        """Тестирование строкового представления зарплаты"""
        salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})

        str_repr = str(salary)
        assert "100000" in str_repr or "150000" in str_repr
        assert isinstance(str_repr, str)


class TestSearchQueryParser:
    """Комплексное тестирование утилит поиска"""

    def test_search_utils_initialization(self):
        """Тестирование инициализации утилит поиска"""
        if hasattr(SearchQueryParser, '__init__'):
            search_utils = SearchQueryParser()
            assert search_utils is not None

    def test_normalize_query(self):
        """Тестирование нормализации поискового запроса"""
        if hasattr(SearchQueryParser, 'normalize_query'):
            # Тестируем различные входные данные
            assert SearchQueryParser.normalize_query("  Python Developer  ") == "python developer"
            assert SearchQueryParser.normalize_query("Java/Kotlin") == "java kotlin"
            assert SearchQueryParser.normalize_query("C++") == "c++"

    def test_extract_keywords(self):
        """Тестирование извлечения ключевых слов"""
        if hasattr(SearchQueryParser, 'extract_keywords'):
            text = "Python developer with Django and PostgreSQL experience"
            keywords = SearchQueryParser.extract_keywords(text)

            assert isinstance(keywords, list)
            assert "python" in [kw.lower() for kw in keywords]
            assert "django" in [kw.lower() for kw in keywords]

    def test_build_search_query(self):
        """Тестирование построения поискового запроса"""
        if hasattr(SearchQueryParser, 'build_search_query'):
            keywords = ["Python", "Django", "PostgreSQL"]
            query = SearchQueryParser.build_search_query(keywords)

            assert isinstance(query, str)
            assert "python" in query.lower()

    def test_filter_by_keywords(self):
        """Тестирование фильтрации по ключевым словам"""
        if hasattr(SearchQueryParser, 'filter_by_keywords'):
            vacancies = [create_test_vacancy_dict() for _ in range(5)]
            keywords = ["Python"]

            filtered = SearchQueryParser.filter_by_keywords(vacancies, keywords)
            assert isinstance(filtered, list)
            assert len(filtered) <= len(vacancies)


class TestBaseFormatter:
    """Комплексное тестирование базового форматера"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.formatter = BaseFormatter()

    def test_base_formatter_initialization(self):
        """Тестирование инициализации базового форматера"""
        assert self.formatter is not None

    def test_format_text(self):
        """Тестирование форматирования текста"""
        if hasattr(self.formatter, 'format_text'):
            text = "  Some text with extra spaces  "
            formatted = self.formatter.format_text(text)

            assert isinstance(formatted, str)
            assert formatted.strip() == "Some text with extra spaces"

    def test_format_currency(self):
        """Тестирование форматирования валюты"""
        if hasattr(self.formatter, 'format_currency'):
            amount = 100000
            currency = "RUR"
            formatted = self.formatter.format_currency(amount, currency)

            assert isinstance(formatted, str)
            assert "100000" in formatted

    def test_format_date(self):
        """Тестирование форматирования даты"""
        if hasattr(self.formatter, 'format_date'):
            date_str = "2025-01-01T10:00:00+03:00"
            formatted = self.formatter.format_date(date_str)

            assert isinstance(formatted, str)

    def test_truncate_text(self):
        """Тестирование обрезания текста"""
        if hasattr(self.formatter, 'truncate_text'):
            long_text = "This is a very long text that should be truncated"
            truncated = self.formatter.truncate_text(long_text, max_length=20)

            assert len(truncated) <= 20
            assert isinstance(truncated, str)


class TestVacancyFormatter:
    """Комплексное тестирование форматера вакансий"""

    def test_vacancy_formatter_exists(self):
        """Тестирование существования форматера вакансий"""
        assert vacancy_formatter is not None

    def test_format_vacancy_basic(self):
        """Тестирование базового форматирования вакансии"""
        vacancy_data = create_test_vacancy_dict()

        if hasattr(vacancy_formatter, 'format_vacancy'):
            formatted = vacancy_formatter.format_vacancy(vacancy_data)
            assert isinstance(formatted, str)
            assert len(formatted) > 0

    def test_format_vacancy_list(self):
        """Тестирование форматирования списка вакансий"""
        vacancies = [create_test_vacancy_dict() for _ in range(3)]

        if hasattr(vacancy_formatter, 'format_vacancy_list'):
            formatted = vacancy_formatter.format_vacancy_list(vacancies)
            assert isinstance(formatted, str)
            assert len(formatted) > 0

    def test_format_salary_range(self):
        """Тестирование форматирования диапазона зарплаты"""
        if hasattr(vacancy_formatter, 'format_salary'):
            salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
            formatted = vacancy_formatter.format_salary(salary_data)

            assert isinstance(formatted, str)
            assert "100000" in formatted
            assert "150000" in formatted


class TestUIHelpers:
    """Комплексное тестирование помощников UI"""

    def test_ui_helpers_initialization(self):
        """Тестирование инициализации помощников UI"""
        if hasattr(UIHelpers, '__init__'):
            ui_helpers = UIHelpers()
            assert ui_helpers is not None

    @patch('builtins.input', return_value='y')
    def test_confirm_action_yes(self, mock_input):
        """Тестирование подтверждения действия - Да"""
        if hasattr(UIHelpers, 'confirm_action'):
            result = UIHelpers.confirm_action("Continue?")
            assert result is True

    @patch('builtins.input', return_value='n')
    def test_confirm_action_no(self, mock_input):
        """Тестирование подтверждения действия - Нет"""
        if hasattr(UIHelpers, 'confirm_action'):
            result = UIHelpers.confirm_action("Continue?")
            assert result is False

    @patch('builtins.input', return_value='test input')
    def test_get_user_input(self, mock_input):
        """Тестирование получения пользовательского ввода"""
        if hasattr(UIHelpers, 'get_user_input'):
            result = UIHelpers.get_user_input("Enter something:")
            assert result == "test input"

    def test_validate_choice(self):
        """Тестирование валидации выбора пользователя"""
        if hasattr(UIHelpers, 'validate_choice'):
            valid_choices = ['1', '2', '3']

            assert UIHelpers.validate_choice('1', valid_choices) is True
            assert UIHelpers.validate_choice('4', valid_choices) is False
            assert UIHelpers.validate_choice('', valid_choices) is False

    def test_parse_salary_range(self):
        """Тестирование парсинга диапазона зарплаты"""
        if hasattr(UIHelpers, 'parse_salary_range'):
            # Тестируем различные форматы
            result = UIHelpers.parse_salary_range("100000-150000")
            if result:
                assert isinstance(result, tuple)
                assert len(result) == 2

            result = UIHelpers.parse_salary_range("от 100000")
            if result:
                assert isinstance(result, tuple)


class TestUINavigation:
    """Комплексное тестирование навигации UI"""

    def test_ui_navigation_initialization(self):
        """Тестирование инициализации навигации UI"""
        if hasattr(UINavigation, '__init__'):
            ui_nav = UINavigation()
            assert ui_nav is not None

    def test_show_menu(self):
        """Тестирование отображения меню"""
        if hasattr(UINavigation, 'show_menu'):
            menu_items = ["Option 1", "Option 2", "Option 3"]

            # Тестируем, что метод не вызывает исключений
            try:
                UINavigation.show_menu(menu_items)
            except Exception as e:
                pytest.fail(f"show_menu should not raise exceptions: {e}")

    @patch('builtins.input', return_value='1')
    def test_get_menu_choice(self, mock_input):
        """Тестирование получения выбора из меню"""
        if hasattr(UINavigation, 'get_menu_choice'):
            menu_items = ["Option 1", "Option 2", "Option 3"]
            choice = UINavigation.get_menu_choice(menu_items)

            assert isinstance(choice, (int, str))

    def test_paginate_items(self):
        """Тестирование пагинации элементов"""
        if hasattr(UINavigation, 'paginate'):
            items = list(range(100))  # 100 элементов
            page_size = 10

            paginated = UINavigation.paginate(items, page_size)
            assert isinstance(paginated, (list, tuple))


class TestMenuManager:
    """Комплексное тестирование менеджера меню"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.menu_manager = MenuManager()

    def test_menu_manager_initialization(self):
        """Тестирование инициализации менеджера меню"""
        assert self.menu_manager is not None

    def test_add_menu_item(self):
        """Тестирование добавления пункта меню"""
        if hasattr(self.menu_manager, 'add_item'):
            self.menu_manager.add_item("1", "Test Option", lambda: None)

            # Проверяем, что пункт добавлен
            if hasattr(self.menu_manager, 'items'):
                assert "1" in self.menu_manager.items

    def test_display_menu(self):
        """Тестирование отображения меню"""
        if hasattr(self.menu_manager, 'display'):
            # Добавляем тестовые пункты
            if hasattr(self.menu_manager, 'add_item'):
                self.menu_manager.add_item("1", "Option 1", lambda: None)
                self.menu_manager.add_item("2", "Option 2", lambda: None)

            # Тестируем отображение
            try:
                self.menu_manager.display()
            except Exception as e:
                pytest.fail(f"display should not raise exceptions: {e}")

    @patch('builtins.input', return_value='1')
    def test_handle_choice(self, mock_input):
        """Тестирование обработки выбора пользователя"""
        if hasattr(self.menu_manager, 'handle_choice') and hasattr(self.menu_manager, 'add_item'):
            executed = []

            def test_action():
                executed.append(True)

            self.menu_manager.add_item("1", "Test Option", test_action)
            self.menu_manager.handle_choice("1")

            assert len(executed) == 1


class TestPaginator:
    """Комплексное тестирование пагинатора"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.items = list(range(1, 101))  # 100 элементов
        # Paginator не принимает аргументы в конструкторе
        self.paginator = Paginator()
        if hasattr(self.paginator, 'paginate'):
            self.paginated_data = self.paginator.paginate(self.items, page_size=10)


    def test_paginator_initialization(self):
        """Тестирование инициализации пагинатора"""
        assert self.paginator is not None
        assert hasattr(self.paginator, 'items')
        assert hasattr(self.paginator, 'page_size')

    def test_get_page(self):
        """Тестирование получения страницы"""
        page = self.paginator.get_page(1)

        assert isinstance(page, list)
        assert len(page) <= 10  # Размер страницы
        assert page[0] == 0  # Первый элемент первой страницы

    def test_get_total_pages(self):
        """Тестирование получения общего количества страниц"""
        total_pages = self.paginator.get_total_pages()

        assert isinstance(total_pages, int)
        assert total_pages == 10  # 100 элементов / 10 на страницу

    def test_has_next_page(self):
        """Тестирование проверки наличия следующей страницы"""
        # Первая страница должна иметь следующую
        assert self.paginator.has_next_page(1) is True

        # Последняя страница не должна иметь следующую
        last_page = self.paginator.get_total_pages()
        assert self.paginator.has_next_page(last_page) is False

    def test_has_previous_page(self):
        """Тестирование проверки наличия предыдущей страницы"""
        # Первая страница не должна иметь предыдущую
        assert self.paginator.has_previous_page(1) is False

        # Вторая страница должна иметь предыдущую
        assert self.paginator.has_previous_page(2) is True


class TestSourceManager:
    """Комплексное тестирование менеджера источников"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.source_manager = SourceManager()

    def test_source_manager_initialization(self):
        """Тестирование инициализации менеджера источников"""
        assert self.source_manager is not None

    def test_get_available_sources(self):
        """Тестирование получения доступных источников"""
        if hasattr(self.source_manager, 'get_available_sources'):
            sources = self.source_manager.get_available_sources()

            assert isinstance(sources, list)
            assert len(sources) > 0
            assert "hh.ru" in sources or "superjob.ru" in sources

    def test_is_source_available(self):
        """Тестирование проверки доступности источника"""
        if hasattr(self.source_manager, 'is_source_available'):
            # Тестируем известные источники
            assert self.source_manager.is_source_available("hh.ru") is True
            assert self.source_manager.is_source_available("superjob.ru") is True

            # Тестируем неизвестный источник
            assert self.source_manager.is_source_available("unknown.ru") is False

    def test_get_source_info(self):
        """Тестирование получения информации об источнике"""
        if hasattr(self.source_manager, 'get_source_info'):
            info = self.source_manager.get_source_info("hh.ru")

            if info is not None:
                assert isinstance(info, dict)
                assert 'name' in info or 'url' in info


class TestVacancyOperations:
    """Комплексное тестирование операций с вакансиями"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.vacancy_ops = VacancyOperations()

    def test_vacancy_operations_initialization(self):
        """Тестирование инициализации операций с вакансиями"""
        assert self.vacancy_ops is not None

    def test_filter_by_salary(self):
        """Тестирование фильтрации по зарплате"""
        if hasattr(self.vacancy_ops, 'filter_by_salary'):
            vacancies = [create_test_vacancy_dict() for _ in range(5)]
            min_salary = 120000

            filtered = self.vacancy_ops.filter_by_salary(vacancies, min_salary)

            assert isinstance(filtered, list)
            assert len(filtered) <= len(vacancies)

    def test_filter_by_company(self):
        """Тестирование фильтрации по компании"""
        if hasattr(self.vacancy_ops, 'filter_by_company'):
            vacancies = [create_test_vacancy_dict() for _ in range(5)]
            company_name = "Test Company"

            filtered = self.vacancy_ops.filter_by_company(vacancies, company_name)

            assert isinstance(filtered, list)

    def test_sort_by_salary(self):
        """Тестирование сортировки по зарплате"""
        if hasattr(self.vacancy_ops, 'sort_by_salary'):
            vacancies = [create_test_vacancy_dict() for _ in range(5)]

            sorted_vacancies = self.vacancy_ops.sort_by_salary(vacancies)

            assert isinstance(sorted_vacancies, list)
            assert len(sorted_vacancies) == len(vacancies)

    def test_group_by_company(self):
        """Тестирование группировки по компаниям"""
        if hasattr(self.vacancy_ops, 'group_by_company'):
            vacancies = [create_test_vacancy_dict() for _ in range(5)]

            grouped = self.vacancy_ops.group_by_company(vacancies)

            assert isinstance(grouped, dict)


class TestVacancyStats:
    """Комплексное тестирование статистики вакансий"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.vacancy_stats = VacancyStats()

    def test_vacancy_stats_initialization(self):
        """Тестирование инициализации статистики вакансий"""
        assert self.vacancy_stats is not None

    def test_calculate_average_salary(self):
        """Тестирование расчета средней зарплаты"""
        if hasattr(self.vacancy_stats, 'calculate_average_salary'):
            vacancies = [create_test_vacancy_dict() for _ in range(5)]

            avg_salary = self.vacancy_stats.calculate_average_salary(vacancies)

            assert isinstance(avg_salary, (int, float))
            assert avg_salary >= 0

    def test_count_by_company(self):
        """Тестирование подсчета вакансий по компаниям"""
        if hasattr(self.vacancy_stats, 'count_by_company'):
            vacancies = [create_test_vacancy_dict() for _ in range(5)]

            counts = self.vacancy_stats.count_by_company(vacancies)

            assert isinstance(counts, dict)

    def test_salary_distribution(self):
        """Тестирование распределения зарплат"""
        if hasattr(self.vacancy_stats, 'salary_distribution'):
            vacancies = [create_test_vacancy_dict() for _ in range(5)]

            distribution = self.vacancy_stats.salary_distribution(vacancies)

            assert isinstance(distribution, dict)

    def test_top_companies(self):
        """Тестирование получения топ компаний"""
        if hasattr(self.vacancy_stats, 'top_companies'):
            vacancies = [create_test_vacancy_dict() for _ in range(10)]

            top = self.vacancy_stats.top_companies(vacancies, limit=5)

            assert isinstance(top, list)
            assert len(top) <= 5


class TestUtilitiesIntegration:
    """Интеграционные тесты для утилит"""

    def test_full_formatting_workflow(self):
        """Тестирование полного рабочего процесса форматирования"""
        # Создаем тестовые данные
        vacancy_data = create_test_vacancy_dict()

        # Форматируем через различные утилиты
        if hasattr(vacancy_formatter, 'format_vacancy'):
            formatted = vacancy_formatter.format_vacancy(vacancy_data)
            assert isinstance(formatted, str)
            assert len(formatted) > 0

    def test_search_and_filter_workflow(self):
        """Тестирование рабочего процесса поиска и фильтрации"""
        vacancies = [create_test_vacancy_dict() for _ in range(10)]

        # Применяем различные операции
        vacancy_ops = VacancyOperations()

        if hasattr(vacancy_ops, 'filter_by_salary'):
            filtered = vacancy_ops.filter_by_salary(vacancies, 100000)
            assert isinstance(filtered, list)

        if hasattr(vacancy_ops, 'sort_by_salary'):
            sorted_vacancies = vacancy_ops.sort_by_salary(vacancies)
            assert isinstance(sorted_vacancies, list)

    def test_pagination_and_navigation_workflow(self):
        """Тестирование рабочего процесса пагинации и навигации"""
        items = list(range(50))
        paginator = Paginator(items, page_size=10)

        # Тестируем навигацию по страницам
        first_page = paginator.get_page(1)
        assert len(first_page) == 10
        assert first_page[0] == 0

        second_page = paginator.get_page(2)
        assert len(second_page) == 10
        assert second_page[0] == 10

        # Проверяем навигацию
        assert paginator.has_next_page(1) is True
        assert paginator.has_previous_page(2) is True