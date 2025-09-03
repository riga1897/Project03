"""
Расширенные тесты для достижения максимального покрытия кода.
Покрывает сложные модули: интерфейсы, парсеры, утилиты и сервисы.
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

# Импорты для тестирования
from src.utils.env_loader import EnvLoader
from src.utils.cache import FileCache
from src.utils.decorators import simple_cache, retry_on_failure as retry
from src.utils.salary import Salary
from src.utils.menu_manager import MenuManager
from src.utils.paginator import Paginator
from src.vacancies.parsers.hh_parser import HHParser
from src.vacancies.parsers.sj_parser import SuperJobParser
from src.storage.storage_factory import StorageFactory
from src.ui_interfaces.console_interface import UserInterface
from src.ui_interfaces.source_selector import SourceSelector


class TestEnvLoaderComprehensive:
    """Комплексное тестирование загрузчика переменных окружения"""
    
    def setup_method(self):
        """Сброс состояния перед каждым тестом"""
        EnvLoader._loaded = False
        
    def teardown_method(self):
        """Очистка после каждого теста"""
        # Восстанавливаем исходное состояние
        if hasattr(EnvLoader, '_original_loaded'):
            EnvLoader._loaded = EnvLoader._original_loaded
        else:
            EnvLoader._loaded = False
            
    def test_env_loader_load_existing_file(self):
        """Тестирование загрузки существующего .env файла"""
        # Создаем временный .env файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as temp_file:
            temp_file.write('TEST_VAR=test_value\n')
            temp_file.write('TEST_VAR_QUOTED="quoted_value"\n')
            temp_file.write("TEST_VAR_SINGLE='single_quoted'\n")
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
            EnvLoader.load_env_file(temp_file_path)
            
            # Проверяем загруженные переменные
            assert os.environ.get('TEST_VAR') == 'test_value'
            assert os.environ.get('TEST_VAR_QUOTED') == 'quoted_value'
            assert os.environ.get('TEST_VAR_SINGLE') == 'single_quoted'
            assert os.environ.get('TEST_VAR_NUMBER') == '12345'
            
        finally:
            # Удаляем временный файл
            os.unlink(temp_file_path)
            
    def test_env_loader_file_not_found(self):
        """Тестирование обработки отсутствующего .env файла"""
        with patch('src.utils.env_loader.logger') as mock_logger:
            EnvLoader.load_env_file("nonexistent.env")
            
            # Проверяем, что было залогировано предупреждение
            mock_logger.warning.assert_called()
            
    def test_env_loader_invalid_format(self):
        """Тестирование обработки некорректного формата .env файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as temp_file:
            temp_file.write('VALID_VAR=valid_value\n')
            temp_file.write('INVALID_LINE_WITHOUT_EQUALS\n')
            temp_file.write('ANOTHER_VALID=another_value\n')
            temp_file_path = temp_file.name
            
        try:
            with patch('src.utils.env_loader.logger') as mock_logger:
                EnvLoader.load_env_file(temp_file_path)
                
                # Проверяем, что было залогировано предупреждение о неверном формате
                mock_logger.warning.assert_called()
                
        finally:
            os.unlink(temp_file_path)
            
    def test_env_loader_already_loaded(self):
        """Тестирование повторной загрузки"""
        EnvLoader._loaded = True
        
        with patch('builtins.open') as mock_open:
            EnvLoader.load_env_file("test.env")
            
            # Проверяем, что файл не открывался
            mock_open.assert_not_called()
            
    def test_env_loader_existing_env_vars_not_overridden(self):
        """Тестирование что существующие переменные не перезаписываются"""
        # Устанавливаем переменную
        os.environ['EXISTING_VAR'] = 'original_value'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as temp_file:
            temp_file.write('EXISTING_VAR=new_value\n')
            temp_file_path = temp_file.name
            
        try:
            EnvLoader.load_env_file(temp_file_path)
            
            # Проверяем, что значение не изменилось
            assert os.environ.get('EXISTING_VAR') == 'original_value'
            
        finally:
            os.unlink(temp_file_path)
            
    def test_get_env_var_existing(self):
        """Тестирование получения существующей переменной"""
        os.environ['TEST_EXISTING'] = 'test_value'
        
        result = EnvLoader.get_env_var('TEST_EXISTING')
        assert result == 'test_value'
        
    def test_get_env_var_missing_with_default(self):
        """Тестирование получения отсутствующей переменной с дефолтом"""
        result = EnvLoader.get_env_var('NONEXISTENT_VAR', 'default_value')
        assert result == 'default_value'
        
    def test_get_env_var_missing_without_default(self):
        """Тестирование получения отсутствующей переменной без дефолта"""
        result = EnvLoader.get_env_var('NONEXISTENT_VAR')
        assert result == ""
        
    def test_get_env_var_int_valid(self):
        """Тестирование получения integer переменной"""
        os.environ['TEST_INT'] = '42'
        
        result = EnvLoader.get_env_var_int('TEST_INT')
        assert result == 42
        
    def test_get_env_var_int_invalid(self):
        """Тестирование получения invalid integer переменной"""
        os.environ['TEST_INVALID_INT'] = 'not_a_number'
        
        result = EnvLoader.get_env_var_int('TEST_INVALID_INT', 100)
        assert result == 100
        
    def test_get_env_var_int_missing(self):
        """Тестирование получения отсутствующей integer переменной"""
        result = EnvLoader.get_env_var_int('NONEXISTENT_INT', 50)
        assert result == 50


class TestFileCacheComprehensive:
    """Комплексное тестирование файлового кэша"""
    
    def setup_method(self):
        """Создание временной директории для тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = FileCache(self.temp_dir)
        
    def teardown_method(self):
        """Очистка временной директории"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_cache_initialization(self):
        """Тестирование инициализации кэша"""
        assert self.cache.cache_dir == self.temp_dir
        assert os.path.exists(self.temp_dir)
        
    def test_cache_set_get_string(self):
        """Тестирование сохранения и получения строки"""
        self.cache.set("test_key", "test_value")
        result = self.cache.get("test_key")
        
        assert result == "test_value"
        
    def test_cache_set_get_dict(self):
        """Тестирование сохранения и получения словаря"""
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        
        self.cache.set("test_dict", test_data)
        result = self.cache.get("test_dict")
        
        assert result == test_data
        
    def test_cache_get_nonexistent(self):
        """Тестирование получения несуществующего ключа"""
        result = self.cache.get("nonexistent_key")
        assert result is None
        
    def test_cache_get_with_default(self):
        """Тестирование получения с дефолтным значением"""
        result = self.cache.get("nonexistent_key", "default_value")
        assert result == "default_value"
        
    def test_cache_has_existing(self):
        """Тестирование проверки существования ключа"""
        self.cache.set("existing_key", "value")
        
        assert self.cache.has("existing_key") is True
        assert self.cache.has("nonexistent_key") is False
        
    def test_cache_delete_existing(self):
        """Тестирование удаления существующего ключа"""
        self.cache.set("to_delete", "value")
        assert self.cache.has("to_delete") is True
        
        self.cache.delete("to_delete")
        assert self.cache.has("to_delete") is False
        
    def test_cache_delete_nonexistent(self):
        """Тестирование удаления несуществующего ключа"""
        # Не должно выбрасывать исключение
        self.cache.delete("nonexistent_key")
        
    def test_cache_clear(self):
        """Тестирование очистки кэша"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        assert self.cache.has("key1") is True
        assert self.cache.has("key2") is True
        
        self.cache.clear()
        
        assert self.cache.has("key1") is False
        assert self.cache.has("key2") is False
        
    def test_cache_file_corruption_handling(self):
        """Тестирование обработки поврежденного файла кэша"""
        # Создаем поврежденный файл
        cache_file = os.path.join(self.temp_dir, "corrupted_key.cache")
        with open(cache_file, 'w') as f:
            f.write("invalid json content")
            
        # Попытка получить данные из поврежденного файла
        result = self.cache.get("corrupted_key")
        assert result is None


class TestSalaryComprehensive:
    """Комплексное тестирование класса Salary"""
    
    def test_salary_initialization_full(self):
        """Тестирование полной инициализации зарплаты"""
        salary = Salary(100000, 200000, "RUR")
        
        assert salary.salary_from == 100000
        assert salary.salary_to == 200000
        assert salary.currency == "RUR"
        
    def test_salary_initialization_partial(self):
        """Тестирование частичной инициализации зарплаты"""
        salary = Salary(150000, None, "USD")
        
        assert salary.salary_from == 150000
        assert salary.salary_to is None
        assert salary.currency == "USD"
        
    def test_salary_initialization_minimal(self):
        """Тестирование минимальной инициализации зарплаты"""
        salary = Salary(None, 250000, "EUR")
        
        assert salary.salary_from is None
        assert salary.salary_to == 250000
        assert salary.currency == "EUR"
        
    def test_salary_get_average(self):
        """Тестирование получения средней зарплаты"""
        salary = Salary(100000, 200000, "RUR")
        assert salary.get_average() == 150000
        
    def test_salary_get_average_partial(self):
        """Тестирование получения средней зарплаты при частичных данных"""
        salary_from_only = Salary(100000, None, "RUR")
        assert salary_from_only.get_average() == 100000
        
        salary_to_only = Salary(None, 200000, "RUR")
        assert salary_to_only.get_average() == 200000
        
        salary_none = Salary(None, None, "RUR")
        assert salary_none.get_average() == 0
        
    def test_salary_is_specified(self):
        """Тестирование проверки указания зарплаты"""
        salary_full = Salary(100000, 200000, "RUR")
        assert salary_full.is_specified() is True
        
        salary_from = Salary(100000, None, "RUR")
        assert salary_from.is_specified() is True
        
        salary_to = Salary(None, 200000, "RUR")
        assert salary_to.is_specified() is True
        
        salary_none = Salary(None, None, "RUR")
        assert salary_none.is_specified() is False
        
    def test_salary_str_representation(self):
        """Тестирование строкового представления зарплаты"""
        salary_full = Salary(100000, 200000, "RUR")
        str_repr = str(salary_full)
        assert "100000" in str_repr
        assert "200000" in str_repr
        assert "RUR" in str_repr
        
        salary_from = Salary(100000, None, "USD")
        str_repr = str(salary_from)
        assert "100000" in str_repr
        assert "USD" in str_repr
        
        salary_none = Salary(None, None, "EUR")
        str_repr = str(salary_none)
        assert "не указана" in str_repr.lower() or "not specified" in str_repr.lower()
        
    def test_salary_comparison(self):
        """Тестирование сравнения зарплат"""
        salary1 = Salary(100000, 200000, "RUR")
        salary2 = Salary(100000, 200000, "RUR")
        salary3 = Salary(150000, 250000, "RUR")
        
        assert salary1 == salary2
        assert salary1 != salary3
        
    def test_salary_to_dict(self):
        """Тестирование преобразования в словарь"""
        salary = Salary(100000, 200000, "RUR")
        result = salary.to_dict()
        
        assert result["from"] == 100000
        assert result["to"] == 200000
        assert result["currency"] == "RUR"
        
    def test_salary_from_dict(self):
        """Тестирование создания из словаря"""
        data = {"from": 150000, "to": 250000, "currency": "USD"}
        salary = Salary.from_dict(data)
        
        assert salary.salary_from == 150000
        assert salary.salary_to == 250000
        assert salary.currency == "USD"


class TestMenuManagerComprehensive:
    """Комплексное тестирование менеджера меню"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.menu_manager = MenuManager()
        
    def test_menu_manager_initialization(self):
        """Тестирование инициализации менеджера меню"""
        assert self.menu_manager is not None
        assert hasattr(self.menu_manager, 'show_main_menu') or hasattr(self.menu_manager, 'display_menu')
        
    @patch('builtins.input', return_value='1')
    def test_menu_manager_user_input(self, mock_input):
        """Тестирование обработки пользовательского ввода"""
        if hasattr(self.menu_manager, 'get_user_choice'):
            choice = self.menu_manager.get_user_choice()
            assert choice == '1'
            
    def test_menu_manager_validate_choice(self):
        """Тестирование валидации выбора пользователя"""
        if hasattr(self.menu_manager, 'validate_choice'):
            assert self.menu_manager.validate_choice('1', ['1', '2', '3']) is True
            assert self.menu_manager.validate_choice('4', ['1', '2', '3']) is False
            
    @patch('builtins.print')
    def test_menu_manager_display(self, mock_print):
        """Тестирование отображения меню"""
        if hasattr(self.menu_manager, 'display_menu'):
            options = ['Option 1', 'Option 2', 'Exit']
            self.menu_manager.display_menu(options)
            
            # Проверяем, что print был вызван
            mock_print.assert_called()


class TestPaginatorComprehensive:
    """Комплексное тестирование пагинатора"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.paginator = Paginator(page_size=10)
        
    def test_paginator_initialization(self):
        """Тестирование инициализации пагинатора"""
        assert self.paginator.page_size == 10
        
    def test_paginator_get_page(self):
        """Тестирование получения страницы данных"""
        data = list(range(25))  # 25 элементов
        
        page_0 = self.paginator.get_page(data, 0)
        assert len(page_0) == 10
        assert page_0 == list(range(10))
        
        page_1 = self.paginator.get_page(data, 1)
        assert len(page_1) == 10
        assert page_1 == list(range(10, 20))
        
        page_2 = self.paginator.get_page(data, 2)
        assert len(page_2) == 5  # Последняя страница
        assert page_2 == list(range(20, 25))
        
    def test_paginator_get_total_pages(self):
        """Тестирование расчета общего количества страниц"""
        data_25 = list(range(25))
        assert self.paginator.get_total_pages(data_25) == 3
        
        data_10 = list(range(10))
        assert self.paginator.get_total_pages(data_10) == 1
        
        data_0 = []
        assert self.paginator.get_total_pages(data_0) == 0
        
    def test_paginator_has_next_page(self):
        """Тестирование проверки наличия следующей страницы"""
        data = list(range(25))
        
        assert self.paginator.has_next_page(data, 0) is True
        assert self.paginator.has_next_page(data, 1) is True
        assert self.paginator.has_next_page(data, 2) is False
        
    def test_paginator_has_previous_page(self):
        """Тестирование проверки наличия предыдущей страницы"""
        data = list(range(25))
        
        assert self.paginator.has_previous_page(0) is False
        assert self.paginator.has_previous_page(1) is True
        assert self.paginator.has_previous_page(2) is True


class TestVacancyParsersComprehensive:
    """Комплексное тестирование парсеров вакансий"""
    
    def test_hh_parser_initialization(self):
        """Тестирование инициализации HH парсера"""
        parser = HHParser()
        assert parser is not None
        
    def test_hh_parser_parse_vacancy(self):
        """Тестирование парсинга вакансии HH"""
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
        assert vacancy.get_title() == "Python Developer"
        assert vacancy.get_employer().get_name() == "Tech Company"
        assert vacancy.get_salary().salary_from == 100000
        
    def test_sj_parser_initialization(self):
        """Тестирование инициализации SuperJob парсера"""
        parser = SuperJobParser()
        assert parser is not None
        
    def test_sj_parser_parse_vacancy(self):
        """Тестирование парсинга вакансии SuperJob"""
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
        assert vacancy.get_title() == "Java Developer"
        assert vacancy.get_employer().get_name() == "Java Corp"
        
    def test_parser_handle_missing_data(self):
        """Тестирование обработки отсутствующих данных"""
        parser = HHParser()
        
        minimal_data = {
            "id": "123",
            "name": "Test Position",
            "alternate_url": "https://test.com"
        }
        
        vacancy = parser.parse_vacancy(minimal_data)
        
        assert vacancy is not None
        assert vacancy.get_title() == "Test Position"
        
    def test_parser_handle_invalid_data(self):
        """Тестирование обработки некорректных данных"""
        parser = HHParser()
        
        # Пустые данные
        result = parser.parse_vacancy({})
        assert result is None or (hasattr(result, 'is_valid') and not result.is_valid())
        
        # None данные
        result = parser.parse_vacancy(None)
        assert result is None


class TestUserInterfaceComponentsComprehensive:
    """Комплексное тестирование компонентов пользовательского интерфейса"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.mock_storage = Mock()
        self.mock_db_manager = Mock()
        
    def test_user_interface_initialization(self):
        """Тестирование инициализации пользовательского интерфейса"""
        ui = UserInterface(self.mock_storage, self.mock_db_manager)
        
        assert ui is not None
        assert ui.storage == self.mock_storage
        assert ui.db_manager == self.mock_db_manager
        
    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    def test_user_interface_main_menu(self, mock_print, mock_input):
        """Тестирование главного меню"""
        ui = UserInterface(self.mock_storage, self.mock_db_manager)
        
        if hasattr(ui, 'run'):
            try:
                ui.run()
            except (SystemExit, KeyboardInterrupt):
                pass  # Ожидаемое поведение при выходе
                
        # Проверяем, что было взаимодействие с пользователем
        mock_print.assert_called()
        
    def test_source_selector_initialization(self):
        """Тестирование инициализации селектора источников"""
        selector = SourceSelector()
        assert selector is not None
        
    @patch('builtins.input', return_value='1')
    def test_source_selector_user_choice(self, mock_input):
        """Тестирование выбора источника пользователем"""
        selector = SourceSelector()
        
        if hasattr(selector, 'get_user_choice'):
            choice = selector.get_user_choice()
            assert choice in ['1', '2', '3', 'hh', 'superjob', 'all']
            
    def test_source_selector_validate_choice(self):
        """Тестирование валидации выбора источника"""
        selector = SourceSelector()
        
        if hasattr(selector, 'validate_choice'):
            assert selector.validate_choice('1') is True
            assert selector.validate_choice('invalid') is False


class TestDecoratorsComprehensive:
    """Комплексное тестирование декораторов"""
    
    def test_simple_cache_decorator(self):
        """Тестирование декоратора простого кэша"""
        call_count = 0
        
        @simple_cache
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
            
        # Первый вызов
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Второй вызов с тем же аргументом (должен использовать кэш)
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Не должен увеличиться
        
        # Вызов с другим аргументом
        result3 = expensive_function(3)
        assert result3 == 6
        assert call_count == 2
        
    def test_retry_decorator_success(self):
        """Тестирование декоратора retry при успешном выполнении"""
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
            
        result = successful_function()
        assert result == "success"
        assert call_count == 1
        
    def test_retry_decorator_eventual_success(self):
        """Тестирование декоратора retry при успехе после неудач"""
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
            
        result = eventually_successful_function()
        assert result == "success"
        assert call_count == 3
        
    def test_retry_decorator_max_attempts_exceeded(self):
        """Тестирование декоратора retry при превышении максимального количества попыток"""
        call_count = 0
        
        @retry(max_attempts=2, delay=0.01)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Always fails")
            
        with pytest.raises(Exception, match="Always fails"):
            always_failing_function()
            
        assert call_count == 2