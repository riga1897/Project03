"""
Тесты для главного интерфейса приложения
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch
import pytest
from typing import List

# Мокаем psycopg2 перед импортом
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.sql'] = MagicMock()

# Добавляем путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.interfaces.main_application_interface import (
    MainApplicationInterface, 
    ConsoleApplicationInterface,
    AdvancedApplicationInterface,
    VacancyProvider,
    VacancyProcessor, 
    VacancyStorage
)


class MockVacancyProvider:
    """Мок провайдера вакансий"""
    
    def get_vacancies(self, query: str):
        return [Mock(title=f"{query} Developer", employer=Mock(name="Test Company"), 
                    salary=Mock(get_formatted_string=lambda: "100000 RUR"), url="http://test.com")]
    
    def get_source_name(self):
        return "MockProvider"


class MockVacancyProcessor:
    """Мок процессора вакансий"""
    
    def process_vacancies(self, vacancies):
        return vacancies


class MockVacancyStorage:
    """Мок хранилища вакансий"""
    
    def __init__(self):
        self.saved_vacancies = []
    
    def save_vacancies(self, vacancies):
        self.saved_vacancies.extend(vacancies)
        return True
    
    def load_vacancies(self):
        return self.saved_vacancies


class TestMainApplicationInterface:
    """Тесты основного интерфейса приложения"""
    
    def test_main_application_interface_creation(self):
        """Тест создания экземпляра главного интерфейса"""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = MockVacancyStorage()
        
        # Не можем создать напрямую, так как это абстрактный класс
        with pytest.raises(TypeError):
            MainApplicationInterface(provider, processor, storage)
    
    def test_execute_vacancy_workflow(self):
        """Тест выполнения полного цикла работы с вакансиями"""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = MockVacancyStorage()
        
        # Создаем конкретную реализацию для тестирования
        app = ConsoleApplicationInterface(provider, processor, storage)
        
        result = app.execute_vacancy_workflow("Python")
        
        assert len(result) == 1
        assert result[0].title == "Python Developer"
        assert len(storage.saved_vacancies) == 1
    
    def test_execute_vacancy_workflow_save_failure(self):
        """Тест обработки ошибки сохранения"""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = Mock()
        storage.save_vacancies.return_value = False
        
        app = ConsoleApplicationInterface(provider, processor, storage)
        
        result = app.execute_vacancy_workflow("Python")
        
        assert result == []


class TestConsoleApplicationInterface:
    """Тесты консольного интерфейса"""
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.provider = MockVacancyProvider()
        self.processor = MockVacancyProcessor()
        self.storage = MockVacancyStorage()
        self.app = ConsoleApplicationInterface(self.provider, self.processor, self.storage)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_vacancy_search_valid_input(self, mock_print, mock_input):
        """Тест поиска вакансий с валидным вводом"""
        mock_input.return_value = "Python Developer"
        
        self.app._handle_vacancy_search()
        
        # Проверяем что были найдены вакансии
        assert len(self.storage.saved_vacancies) == 1
        
        # Проверяем что информация была выведена
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Найдено и обработано" in call for call in print_calls)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_vacancy_search_empty_input(self, mock_print, mock_input):
        """Тест поиска вакансий с пустым вводом"""
        mock_input.return_value = ""
        
        self.app._handle_vacancy_search()
        
        # Проверяем что вакансии не добавились
        assert len(self.storage.saved_vacancies) == 0
        
        # Проверяем что показали сообщение о пустом запросе
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Пустой запрос" in call for call in print_calls)
    
    @patch('builtins.print')
    def test_handle_view_saved_with_vacancies(self, mock_print):
        """Тест просмотра сохраненных вакансий когда есть данные"""
        # Добавляем вакансии в storage
        test_vacancy = Mock()
        test_vacancy.title = "Test Developer"
        test_vacancy.employer = Mock(name="Test Company")
        test_vacancy.salary = Mock(get_formatted_string=lambda: "150000 RUR")
        test_vacancy.url = "http://test.com"
        self.storage.saved_vacancies = [test_vacancy]
        
        self.app._handle_view_saved()
        
        # Проверяем что информация была выведена
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Всего сохранено" in call for call in print_calls)
        assert any("Test Developer" in call for call in print_calls)
    
    @patch('builtins.print')
    def test_handle_view_saved_empty(self, mock_print):
        """Тест просмотра сохраненных вакансий когда данных нет"""
        self.app._handle_view_saved()
        
        # Проверяем что показали сообщение об отсутствии вакансий
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Сохраненные вакансии не найдены" in call for call in print_calls)
    
    @patch('builtins.print')
    def test_handle_company_stats_with_sql_filter_service(self, mock_print):
        """Тест статистики компаний с SQL фильтром"""
        # Мокаем processor как SQLFilterService
        mock_processor = Mock()
        mock_processor.get_companies_vacancy_count.return_value = [("Test Company", 5), ("Another Company", 3)]
        self.app.processor = mock_processor
        
        with patch('src.interfaces.main_application_interface.SQLFilterService', mock_processor.__class__):
            self.app._handle_company_stats()
        
        # Проверяем что статистика была выведена
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Статистика по целевым компаниям" in call for call in print_calls)
        assert any("Test Company: 5 вакансий" in call for call in print_calls)
    
    @patch('builtins.print')
    def test_handle_company_stats_without_sql_filter_service(self, mock_print):
        """Тест статистики компаний без SQL фильтра"""
        self.app._handle_company_stats()
        
        # Проверяем что показали сообщение о неподдерживаемой статистике
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("не поддерживается" in call for call in print_calls)
    
    @patch('builtins.print')
    def test_handle_company_stats_exception(self, mock_print):
        """Тест обработки ошибки при получении статистики"""
        mock_processor = Mock()
        mock_processor.get_companies_vacancy_count.side_effect = Exception("Test error")
        self.app.processor = mock_processor
        
        with patch('src.interfaces.main_application_interface.SQLFilterService', mock_processor.__class__):
            self.app._handle_company_stats()
        
        # Проверяем что показали сообщение об ошибке
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Ошибка получения статистики" in call for call in print_calls)
    
    @patch('builtins.print')
    def test_display_vacancy_summary_basic(self, mock_print):
        """Тест отображения краткой информации о вакансиях"""
        # Создаем тестовые вакансии
        vacancy1 = Mock()
        vacancy1.title = "Python Developer"
        vacancy1.employer = Mock(name="Test Company")
        vacancy1.salary = Mock(get_formatted_string=lambda: "100000 RUR")
        vacancy1.url = "http://test1.com"
        
        vacancy2 = Mock()
        vacancy2.title = "Java Developer"
        vacancy2.employer = None
        vacancy2.salary = None
        vacancy2.url = None
        
        self.app._display_vacancy_summary([vacancy1, vacancy2])
        
        # Проверяем что информация была выведена
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Python Developer" in call for call in print_calls)
        assert any("Java Developer" in call for call in print_calls)
        assert any("Test Company" in call for call in print_calls)
        assert any("Не указана" in call for call in print_calls)  # для пустых полей
    
    @patch('builtins.print')
    def test_display_vacancy_summary_salary_variations(self, mock_print):
        """Тест отображения различных вариантов зарплаты"""
        # Вакансия с salary_info
        vacancy1 = Mock()
        vacancy1.title = "Test 1"
        vacancy1.employer = Mock(name="Company 1")
        vacancy1.salary = Mock(salary_info="120000 RUR")
        vacancy1.url = "http://test1.com"
        # Убираем get_formatted_string чтобы проверить fallback
        del vacancy1.salary.get_formatted_string
        
        # Вакансия с salary_from и salary_to
        vacancy2 = Mock()
        vacancy2.title = "Test 2"
        vacancy2.employer = Mock(name="Company 2")
        vacancy2.salary = Mock(salary_from=100000, salary_to=150000)
        vacancy2.url = "http://test2.com"
        # Убираем все методы форматирования
        del vacancy2.salary.get_formatted_string
        del vacancy2.salary.salary_info
        
        # Вакансия только с salary_from
        vacancy3 = Mock()
        vacancy3.title = "Test 3"
        vacancy3.employer = Mock(name="Company 3")
        vacancy3.salary = Mock(salary_from=80000, salary_to=None)
        vacancy3.url = "http://test3.com"
        # Убираем все методы форматирования
        del vacancy3.salary.get_formatted_string
        del vacancy3.salary.salary_info
        
        # Вакансия только с salary_to
        vacancy4 = Mock()
        vacancy4.title = "Test 4"
        vacancy4.employer = Mock(name="Company 4")
        vacancy4.salary = Mock(salary_from=None, salary_to=200000)
        vacancy4.url = "http://test4.com"
        # Убираем все методы форматирования
        del vacancy4.salary.get_formatted_string
        del vacancy4.salary.salary_info
        
        self.app._display_vacancy_summary([vacancy1, vacancy2, vacancy3, vacancy4])
        
        # Проверяем различные форматы зарплаты
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("120000 RUR" in call for call in print_calls)
        assert any("100000 - 150000 RUR" in call for call in print_calls)
        assert any("от 80000 RUR" in call for call in print_calls)
        assert any("до 200000 RUR" in call for call in print_calls)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_application_menu_loop(self, mock_print, mock_input):
        """Тест основного цикла приложения"""
        # Симулируем выбор пользователя: поиск вакансий, затем выход
        mock_input.side_effect = ["1", "Python", "0"]
        
        self.app.run_application()
        
        # Проверяем что меню было показано
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Приложение поиска вакансий" in call for call in print_calls)
        assert any("1. Поиск вакансий" in call for call in print_calls)
        assert any("Завершение работы" in call for call in print_calls)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_application_view_saved(self, mock_print, mock_input):
        """Тест просмотра сохраненных вакансий через меню"""
        mock_input.side_effect = ["2", "0"]
        
        self.app.run_application()
        
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Сохраненные вакансии не найдены" in call for call in print_calls)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_application_company_stats(self, mock_print, mock_input):
        """Тест статистики компаний через меню"""
        mock_input.side_effect = ["3", "0"]
        
        self.app.run_application()
        
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("не поддерживается" in call for call in print_calls)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_application_invalid_choice(self, mock_print, mock_input):
        """Тест неверного выбора в меню"""
        mock_input.side_effect = ["999", "0"]
        
        self.app.run_application()
        
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Неверный выбор" in call for call in print_calls)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_application_keyboard_interrupt(self, mock_print, mock_input):
        """Тест прерывания приложения"""
        mock_input.side_effect = KeyboardInterrupt()
        
        self.app.run_application()
        
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("прервана пользователем" in call for call in print_calls)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_application_exception_handling(self, mock_print, mock_input):
        """Тест обработки исключений в приложении"""
        mock_input.side_effect = Exception("Test error")
        
        self.app.run_application()
        
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Ошибка: Test error" in call for call in print_calls)


class TestAdvancedApplicationInterface:
    """Тесты продвинутого интерфейса"""
    
    def test_advanced_application_interface_creation(self):
        """Тест создания продвинутого интерфейса"""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = MockVacancyStorage()
        analytics = Mock()
        
        app = AdvancedApplicationInterface(provider, processor, storage, analytics)
        
        assert app.provider == provider
        assert app.processor == processor
        assert app.storage == storage
        assert app.analytics == analytics
    
    def test_get_advanced_analytics_with_analytics(self):
        """Тест получения аналитики когда аналитика доступна"""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = MockVacancyStorage()
        analytics = Mock()
        analytics.generate_report.return_value = {"total_vacancies": 100, "avg_salary": 150000}
        
        app = AdvancedApplicationInterface(provider, processor, storage, analytics)
        
        result = app.get_advanced_analytics()
        
        assert result == {"total_vacancies": 100, "avg_salary": 150000}
    
    def test_get_advanced_analytics_without_analytics(self):
        """Тест получения аналитики когда аналитика недоступна"""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = MockVacancyStorage()
        
        app = AdvancedApplicationInterface(provider, processor, storage)
        
        result = app.get_advanced_analytics()
        
        assert result == {}


class TestProtocols:
    """Тесты протоколов интерфейсов"""
    
    def test_vacancy_provider_protocol(self):
        """Тест соответствия протоколу VacancyProvider"""
        provider = MockVacancyProvider()
        
        assert isinstance(provider, VacancyProvider)
        assert hasattr(provider, 'get_vacancies')
        assert hasattr(provider, 'get_source_name')
    
    def test_vacancy_processor_protocol(self):
        """Тест соответствия протоколу VacancyProcessor"""
        processor = MockVacancyProcessor()
        
        assert isinstance(processor, VacancyProcessor)
        assert hasattr(processor, 'process_vacancies')
    
    def test_vacancy_storage_protocol(self):
        """Тест соответствия протоколу VacancyStorage"""
        storage = MockVacancyStorage()
        
        assert isinstance(storage, VacancyStorage)
        assert hasattr(storage, 'save_vacancies')
        assert hasattr(storage, 'load_vacancies')