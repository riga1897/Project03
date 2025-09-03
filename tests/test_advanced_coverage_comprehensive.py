"""
Расширенные тесты для достижения максимального покрытия кода.
Покрывает сложные модули: интерфейсы, парсеры, утилиты и сервисы.

Все тесты используют консолидированные моки без fallback методов.
Классы и методы импортируются из реального кода в src.
"""

import os
import sys
import pytest
import tempfile
import json
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any, Optional
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Консолидированные моки для всех тестов
class ConsolidatedMocks:
    """
    Консолидированная система моков для всех компонентов.

    Обеспечивает единообразное поведение моков без fallback логики.
    """

    def __init__(self) -> None:
        """Инициализация всех моков системы"""
        self.mocks = self._create_all_mocks()
        self._configure_mock_behavior()

    def _create_all_mocks(self) -> Dict[str, Mock]:
        """
        Создает все моки для компонентов системы.

        Returns:
            Dict[str, Mock]: Словарь моков для всех зависимостей
        """
        return {
            # API моки
            'requests': Mock(),
            'hh_response': Mock(),
            'sj_response': Mock(),

            # База данных моки
            'psycopg2': Mock(),
            'connection': Mock(),
            'cursor': Mock(),

            # Файловая система моки
            'file_system': Mock(),
            'temp_file': Mock(),

            # UI моки
            'input': Mock(),
            'print': Mock(),

            # Модели данных моки
            'vacancy': Mock(),
            'employer': Mock(),
            'salary': Mock()
        }

    def _configure_mock_behavior(self) -> None:
        """Настраивает поведение всех моков"""
        # HTTP запросы
        self.mocks['requests'].get.return_value = self.mocks['hh_response']
        self.mocks['hh_response'].json.return_value = {
            'items': [{'id': '123', 'name': 'Python Developer'}],
            'found': 1
        }
        self.mocks['hh_response'].status_code = 200

        # База данных
        self.mocks['psycopg2'].connect.return_value = self.mocks['connection']
        self.mocks['connection'].cursor.return_value = self.mocks['cursor']
        self.mocks['cursor'].fetchall.return_value = []

        # Пользовательский ввод
        self.mocks['input'].return_value = '1'

        # Модели данных
        self.mocks['vacancy'].title = 'Test Vacancy'
        self.mocks['employer'].name = 'Test Company'
        self.mocks['salary'].salary_from = 100000


# Глобальный экземпляр моков
consolidated_mocks = ConsolidatedMocks()


class TestEnvLoaderComprehensive:
    """Комплексное тестирование загрузчика переменных окружения"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        from src.utils.env_loader import EnvLoader
        self.env_loader = EnvLoader

    def test_env_loader_load_existing_file(self) -> None:
        """Тестирование загрузки существующего .env файла"""
        # Создаем временный .env файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as temp_file:
            temp_file.write('TEST_VAR=test_value\n')
            temp_file.write('TEST_VAR_QUOTED="quoted_value"\n')
            temp_file.write("TEST_VAR_SINGLE='single_quoted'\n')
            temp_file.write('# This is a comment\n')
            temp_file.write('\n')  # Empty line
            temp_file.write('TEST_VAR_NUMBER=12345\n')
            temp_file_path = temp_file.name

        try:
            # Очищаем переменные окружения
            for var in ['TEST_VAR', 'TEST_VAR_QUOTED', 'TEST_VAR_SINGLE', 'TEST_VAR_NUMBER']:
                if var in os.environ:
                    del os.environ[var]

            # Загружаем файл
            self.env_loader.load_env_file(temp_file_path)

            # Проверяем загруженные переменные
            assert os.environ.get('TEST_VAR') == 'test_value'
            assert os.environ.get('TEST_VAR_QUOTED') == 'quoted_value'
            assert os.environ.get('TEST_VAR_SINGLE') == 'single_quoted'
            assert os.environ.get('TEST_VAR_NUMBER') == '12345'

        finally:
            # Удаляем временный файл
            os.unlink(temp_file_path)

    def test_env_loader_file_not_found(self) -> None:
        """Тестирование обработки отсутствующего .env файла"""
        with patch('src.utils.env_loader.logger') as mock_logger:
            self.env_loader.load_env_file("nonexistent.env")
            mock_logger.warning.assert_called()

    def test_get_env_var_with_default(self) -> None:
        """Тестирование получения переменной с дефолтным значением"""
        # Существующая переменная
        os.environ['EXISTING_VAR'] = 'existing_value'
        result = self.env_loader.get_env_var('EXISTING_VAR', 'default')
        assert result == 'existing_value'

        # Несуществующая переменная
        result = self.env_loader.get_env_var('NON_EXISTING_VAR', 'default')
        assert result == 'default'

    def test_get_env_var_int(self) -> None:
        """Тестирование получения целочисленной переменной"""
        os.environ['INT_VAR'] = '42'
        result = self.env_loader.get_env_var_int('INT_VAR', 0)
        assert result == 42

        # Некорректное значение
        os.environ['INVALID_INT'] = 'not_a_number'
        result = self.env_loader.get_env_var_int('INVALID_INT', 10)
        assert result == 10


class TestFileCacheComprehensive:
    """Комплексное тестирование системы файлового кэширования"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        from src.utils.cache import FileCache
        self.temp_dir = tempfile.mkdtemp()
        self.cache = FileCache(cache_dir=self.temp_dir)

    def test_cache_initialization(self) -> None:
        """Тестирование инициализации кэша"""
        assert self.cache is not None
        assert str(self.cache.cache_dir) == self.temp_dir

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


class TestSalaryComprehensive:
    """Комплексное тестирование класса Salary"""

    def test_salary_initialization_with_dict(self) -> None:
        """Тестирование инициализации с данными в виде словаря"""
        from src.utils.salary import Salary

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
        from src.utils.salary import Salary

        salary = Salary({"from": 100000, "to": 150000})
        average = salary.get_average()
        assert average == 125000

    def test_salary_is_specified(self) -> None:
        """Тестирование проверки указания зарплаты"""
        from src.utils.salary import Salary

        salary_full = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        assert salary_full.is_specified() is True

        salary_none = Salary({"from": None, "to": None, "currency": "RUR"})
        assert salary_none.is_specified() is False

    def test_salary_string_representation(self) -> None:
        """Тестирование строкового представления зарплаты"""
        from src.utils.salary import Salary

        salary_full = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        str_repr = str(salary_full)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0


class TestVacancyParsersComprehensive:
    """Комплексное тестирование парсеров вакансий"""

    def test_hh_parser_initialization(self) -> None:
        """Тестирование инициализации HH парсера"""
        from src.vacancies.parsers.hh_parser import HHParser

        parser = HHParser()
        assert parser is not None

    def test_hh_parser_parse_vacancy(self) -> None:
        """Тестирование парсинга вакансии HH"""
        from src.vacancies.parsers.hh_parser import HHParser

        parser = HHParser()

        hh_data = {
            "id": "123",
            "name": "Python Developer",
            "employer": {"name": "Tech Company", "id": "456"},
            "salary": {"from": 100000, "to": 200000, "currency": "RUR"},
            "alternate_url": "https://hh.ru/vacancy/123",
            "snippet": {
                "requirement": "Python, Django",
                "responsibility": "Development"
            },
            "experience": {"name": "От 1 года до 3 лет"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"}
        }

        vacancy = parser.parse_vacancy(hh_data)
        assert vacancy is not None

    def test_sj_parser_initialization(self) -> None:
        """Тестирование инициализации SuperJob парсера"""
        from src.vacancies.parsers.sj_parser import SuperJobParser

        parser = SuperJobParser()
        assert parser is not None

    def test_sj_parser_parse_vacancy(self) -> None:
        """Тестирование парсинга вакансии SuperJob"""
        from src.vacancies.parsers.sj_parser import SuperJobParser

        parser = SuperJobParser()

        sj_data = {
            "id": 789,
            "profession": "Java Developer",
            "firm_name": "Java Corp",
            "payment_from": 150000,
            "payment_to": 250000,
            "currency": "rub",
            "link": "https://superjob.ru/vacancy/789",
            "candidat": "Java, Spring",
            "work": "Backend development",
            "experience": {"title": "От 3 до 6 лет"},
            "type_of_work": {"title": "Полная занятость"}
        }

        vacancy = parser.parse_vacancy(sj_data)
        assert vacancy is not None


class TestAPIModulesComprehensive:
    """Комплексное тестирование API модулей"""

    def setup_method(self) -> None:
        """Настройка моков перед каждым тестом"""
        self.mocks = consolidated_mocks.mocks

    @patch('requests.get')
    def test_hh_api_search_vacancies(self, mock_get: Mock) -> None:
        """Тестирование поиска вакансий через HH API"""
        from src.api_modules.hh_api import HeadHunterAPI

        mock_get.return_value = self.mocks['hh_response']

        api = HeadHunterAPI()
        result = api.search_vacancies('python developer')

        assert isinstance(result, list)
        mock_get.assert_called()

    @patch('requests.get')
    def test_sj_api_search_vacancies(self, mock_get: Mock) -> None:
        """Тестирование поиска вакансий через SuperJob API"""
        from src.api_modules.sj_api import SuperJobAPI

        # Настраиваем мок для SuperJob ответа
        sj_response = Mock()
        sj_response.json.return_value = {
            'objects': [
                {
                    'id': 456,
                    'profession': 'Java Developer',
                    'firm_name': 'Dev Company',
                    'payment_from': 120000,
                    'payment_to': 180000,
                    'currency': 'rub'
                }
            ],
            'total': 1
        }
        mock_get.return_value = sj_response

        api = SuperJobAPI('test_api_key')
        result = api.search_vacancies('java developer')

        assert isinstance(result, list)
        mock_get.assert_called()


class TestUIComponentsComprehensive:
    """Комплексное тестирование UI компонентов"""

    def test_ui_navigation_initialization(self) -> None:
        """Тестирование инициализации UI навигации"""
        from src.utils.ui_navigation import UINavigation

        ui_nav = UINavigation()
        assert ui_nav is not None

    def test_menu_manager_initialization(self) -> None:
        """Тестирование инициализации менеджера меню"""
        from src.utils.menu_manager import MenuManager

        menu_manager = MenuManager()
        assert menu_manager is not None

    def test_paginator_initialization(self) -> None:
        """Тестирование инициализации пагинатора"""
        from src.utils.paginator import Paginator

        items = list(range(100))
        paginator = Paginator(items, page_size=10)
        assert paginator is not None
        assert len(paginator.items) == 100
        assert paginator.page_size == 10

    def test_paginator_get_page(self) -> None:
        """Тестирование получения страницы данных"""
        from src.utils.paginator import Paginator

        items = list(range(25))
        paginator = Paginator(items, page_size=10)

        page_0 = paginator.get_page(0)
        assert len(page_0) == 10
        assert page_0 == list(range(10))

    def test_paginator_get_total_pages(self) -> None:
        """Тестирование расчета общего количества страниц"""
        from src.utils.paginator import Paginator

        items = list(range(25))
        paginator = Paginator(items, page_size=10)

        total_pages = paginator.get_total_pages()
        assert total_pages == 3

    def test_paginator_has_next_page(self) -> None:
        """Тестирование проверки наличия следующей страницы"""
        from src.utils.paginator import Paginator

        items = list(range(25))
        paginator = Paginator(items, page_size=10)

        assert paginator.has_next_page(0) is True
        assert paginator.has_next_page(2) is False

    def test_paginator_has_previous_page(self) -> None:
        """Тестирование проверки наличия предыдущей страницы"""
        from src.utils.paginator import Paginator

        items = list(range(25))
        paginator = Paginator(items, page_size=10)

        assert paginator.has_previous_page(0) is False
        assert paginator.has_previous_page(1) is True


class TestStorageModulesComprehensive:
    """Комплексное тестирование модулей хранения данных"""

    def setup_method(self) -> None:
        """Настройка моков для тестирования БД"""
        self.mocks = consolidated_mocks.mocks

    @patch('psycopg2.connect')
    def test_db_manager_initialization(self, mock_connect: Mock) -> None:
        """Тестирование инициализации менеджера БД"""
        from src.storage.db_manager import DBManager

        mock_connect.return_value = self.mocks['connection']

        db = DBManager()
        assert db is not None

    @patch('psycopg2.connect')
    def test_db_manager_check_connection(self, mock_connect: Mock) -> None:
        """Тестирование проверки подключения к БД"""
        from src.storage.db_manager import DBManager

        mock_connect.return_value = self.mocks['connection']

        db = DBManager()
        result = db.check_connection()
        assert isinstance(result, bool)

    def test_storage_factory_create_storage(self) -> None:
        """Тестирование создания хранилищ через фабрику"""
        from src.storage.storage_factory import StorageFactory

        storage = StorageFactory.create_storage('postgresql')
        assert storage is not None


class TestVacancyModelsComprehensive:
    """Комплексное тестирование моделей вакансий"""

    def test_vacancy_initialization(self) -> None:
        """Тестирование инициализации вакансии"""
        from src.vacancies.models import Vacancy, Employer

        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1"
        )

        assert vacancy.title == "Python Developer"
        assert vacancy.employer.name == "Test Company"

    def test_employer_initialization(self) -> None:
        """Тестирование инициализации работодателя"""
        from src.vacancies.models import Employer

        employer = Employer("Test Company", "123")
        assert employer.get_name() == "Test Company"
        assert employer.get_id() == "123"

    def test_salary_model_comprehensive(self) -> None:
        """Тестирование модели зарплаты"""
        from src.utils.salary import Salary

        salary = Salary({"from": 100000, "to": 200000, "currency": "RUR"})
        assert salary.salary_from == 100000
        assert salary.salary_to == 200000
        assert salary.currency == "RUR"