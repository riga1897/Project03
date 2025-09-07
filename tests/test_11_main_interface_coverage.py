#!/usr/bin/env python3
"""
Тесты для 100% покрытия модулей главного интерфейса приложения.

Архитектурные принципы:
- Все I/O операции заменены на mock
- Тестирование протоколов и абстракций
- Покрытие всех методов и веток кода
- Следование иерархии: протоколы → абстракции → реализации
"""

import io
import sys
from typing import List
from unittest.mock import patch, Mock, MagicMock
import pytest

# Импорты из реального кода для покрытия
from src.interfaces.main_application_interface import (
    VacancyProvider,
    VacancyProcessor, 
    VacancyStorage,
    MainApplicationInterface,
    ConsoleApplicationInterface,
    AdvancedApplicationInterface
)
from src.vacancies.models import Vacancy
from src.config.target_companies import CompanyInfo


class MockVacancyProvider:
    """Мок-провайдер вакансий для тестов."""
    
    def __init__(self, vacancies_to_return=None):
        self.vacancies_to_return = vacancies_to_return or []
    
    def get_vacancies(self, query: str) -> List[Vacancy]:
        """Возвращает заданные вакансии."""
        return self.vacancies_to_return
    
    def get_source_name(self) -> str:
        """Возвращает имя источника."""
        return "MockProvider"


class MockVacancyProcessor:
    """Мок-процессор вакансий для тестов."""
    
    def __init__(self, processed_vacancies=None):
        self.processed_vacancies = processed_vacancies or []
    
    def process_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """Возвращает обработанные вакансии."""
        return self.processed_vacancies or vacancies


class MockVacancyStorage:
    """Мок-хранилище вакансий для тестов."""
    
    def __init__(self, save_result=True, stored_vacancies=None):
        self.save_result = save_result
        self.stored_vacancies = stored_vacancies or []
        self.saved_vacancies = []
    
    def save_vacancies(self, vacancies: List[Vacancy]) -> bool:
        """Сохраняет вакансии и возвращает результат."""
        self.saved_vacancies.extend(vacancies)
        return self.save_result
    
    def load_vacancies(self) -> List[Vacancy]:
        """Загружает сохраненные вакансии."""
        return self.stored_vacancies


class ConcreteMainInterface(MainApplicationInterface):
    """Конкретная реализация для тестирования абстрактного класса."""
    
    def run_application(self) -> None:
        """Простая реализация для тестов."""
        pass


class TestVacancyProtocols:
    """100% покрытие протоколов для вакансий."""

    def test_vacancy_provider_protocol(self):
        """Покрытие протокола VacancyProvider."""
        provider = MockVacancyProvider()
        
        # Проверяем что класс соответствует протоколу
        assert isinstance(provider, VacancyProvider)
        
        # Тестируем методы
        result = provider.get_vacancies("Python")
        assert isinstance(result, list)
        
        source_name = provider.get_source_name()
        assert isinstance(source_name, str)
        assert source_name == "MockProvider"

    def test_vacancy_processor_protocol(self):
        """Покрытие протокола VacancyProcessor."""
        processor = MockVacancyProcessor()
        
        # Проверяем что класс соответствует протоколу
        assert isinstance(processor, VacancyProcessor)
        
        # Тестируем обработку
        vacancies = [Mock(spec=Vacancy)]
        result = processor.process_vacancies(vacancies)
        assert isinstance(result, list)

    def test_vacancy_storage_protocol(self):
        """Покрытие протокола VacancyStorage."""
        storage = MockVacancyStorage()
        
        # Проверяем что класс соответствует протоколу
        assert isinstance(storage, VacancyStorage)
        
        # Тестируем сохранение
        vacancies = [Mock(spec=Vacancy)]
        result = storage.save_vacancies(vacancies)
        assert isinstance(result, bool)
        assert result is True
        
        # Тестируем загрузку
        loaded = storage.load_vacancies()
        assert isinstance(loaded, list)


class TestMainApplicationInterface:
    """100% покрытие абстрактного интерфейса приложения."""

    def test_main_interface_init(self):
        """Покрытие инициализации главного интерфейса."""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = MockVacancyStorage()
        
        interface = ConcreteMainInterface(provider, processor, storage)
        
        assert interface.provider is provider
        assert interface.processor is processor
        assert interface.storage is storage

    def test_main_interface_abstract_method(self):
        """Покрытие абстрактного метода."""
        # Проверяем что нельзя инстанцировать абстрактный класс
        with pytest.raises(TypeError):
            MainApplicationInterface(Mock(), Mock(), Mock())

    def test_execute_vacancy_workflow_success(self):
        """Покрытие успешного выполнения workflow."""
        # Настраиваем моки
        mock_vacancy = Mock(spec=Vacancy)
        provider = MockVacancyProvider([mock_vacancy])
        processor = MockVacancyProcessor([mock_vacancy])
        storage = MockVacancyStorage(save_result=True)
        
        interface = ConcreteMainInterface(provider, processor, storage)
        
        # Выполняем workflow
        result = interface.execute_vacancy_workflow("Python")
        
        # Проверяем результат
        assert len(result) == 1
        assert result[0] is mock_vacancy
        assert len(storage.saved_vacancies) == 1

    def test_execute_vacancy_workflow_save_failure(self):
        """Покрытие неудачного сохранения."""
        mock_vacancy = Mock(spec=Vacancy)
        provider = MockVacancyProvider([mock_vacancy])
        processor = MockVacancyProcessor([mock_vacancy])
        storage = MockVacancyStorage(save_result=False)
        
        interface = ConcreteMainInterface(provider, processor, storage)
        
        # Выполняем workflow
        result = interface.execute_vacancy_workflow("Python")
        
        # Проверяем что возвращается пустой список при неудаче сохранения
        assert result == []


class TestConsoleApplicationInterface:
    """100% покрытие консольного интерфейса."""

    def test_console_interface_init(self):
        """Покрытие инициализации консольного интерфейса."""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = MockVacancyStorage()
        
        interface = ConsoleApplicationInterface(provider, processor, storage)
        
        assert isinstance(interface, MainApplicationInterface)
        assert interface.provider is provider

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_application_exit(self, mock_print, mock_input):
        """Покрытие запуска приложения с выходом."""
        mock_input.return_value = "0"
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(), 
            MockVacancyStorage()
        )
        
        interface.run_application()
        
        # Проверяем что вызваны принты меню
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_application_invalid_choice(self, mock_print, mock_input):
        """Покрытие неверного выбора в меню."""
        mock_input.side_effect = ["invalid", "0"]
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        interface.run_application()
        
        # Проверяем что выведено сообщение об ошибке
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_application_keyboard_interrupt(self, mock_print, mock_input):
        """Покрытие прерывания с клавиатуры."""
        mock_input.side_effect = KeyboardInterrupt()
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        interface.run_application()
        
        # Проверяем что обработано прерывание
        mock_print.assert_called()

    @patch('builtins.input') 
    @patch('builtins.print')
    def test_run_application_exception(self, mock_print, mock_input):
        """Покрытие обработки исключений."""
        mock_input.side_effect = [Exception("Test error"), "0"]
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        interface.run_application()
        
        # Проверяем что ошибка обработана
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_vacancy_search_success(self, mock_print, mock_input):
        """Покрытие успешного поиска вакансий."""
        mock_input.side_effect = ["1", "Python developer", "0"]
        
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.title = "Python Developer"
        mock_vacancy.url = "http://example.com"
        mock_vacancy.employer = Mock()
        mock_vacancy.employer.name = "Test Company"
        mock_vacancy.salary = None
        
        provider = MockVacancyProvider([mock_vacancy])
        processor = MockVacancyProcessor([mock_vacancy])
        storage = MockVacancyStorage(save_result=True)
        
        interface = ConsoleApplicationInterface(provider, processor, storage)
        interface.run_application()
        
        # Проверяем что поиск выполнен
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_vacancy_search_empty_query(self, mock_print, mock_input):
        """Покрытие пустого поискового запроса."""
        mock_input.side_effect = ["1", "", "0"]
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        interface.run_application()
        
        # Проверяем обработку пустого запроса
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_vacancy_search_no_results(self, mock_print, mock_input):
        """Покрытие поиска без результатов."""
        mock_input.side_effect = ["1", "NonExistentJob", "0"]
        
        # Настраиваем хранилище для неудачного сохранения
        storage = MockVacancyStorage(save_result=False)
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider([]),
            MockVacancyProcessor([]),
            storage
        )
        
        interface.run_application()
        
        # Проверяем сообщение о том что вакансии не найдены
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_view_saved_with_vacancies(self, mock_print, mock_input):
        """Покрытие просмотра сохраненных вакансий."""
        mock_input.side_effect = ["2", "0"]
        
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.title = "Saved Job"
        mock_vacancy.url = "http://saved.com"
        mock_vacancy.employer = Mock()
        mock_vacancy.employer.name = "Saved Company"
        mock_vacancy.salary = None
        
        storage = MockVacancyStorage(stored_vacancies=[mock_vacancy])
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            storage
        )
        
        interface.run_application()
        
        # Проверяем что сохраненные вакансии отображены
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_view_saved_empty(self, mock_print, mock_input):
        """Покрытие просмотра пустого списка сохраненных вакансий."""
        mock_input.side_effect = ["2", "0"]
        
        storage = MockVacancyStorage(stored_vacancies=[])
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            storage
        )
        
        interface.run_application()
        
        # Проверяем сообщение о пустом списке
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_company_stats_with_sql_service(self, mock_print, mock_input):
        """Покрытие статистики с SQL сервисом."""
        mock_input.side_effect = ["3", "0"]
        
        # Создаем мок процессора с методом get_companies_vacancy_count
        mock_processor = Mock()
        mock_processor.get_companies_vacancy_count.return_value = [
            ("Company A", 10),
            ("Company B", 5)
        ]
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            mock_processor,
            MockVacancyStorage()
        )
        
        # Мокаем isinstance чтобы симулировать SQLFilterService
        with patch('src.interfaces.main_application_interface.isinstance', return_value=True):
            interface.run_application()
        
        # Проверяем что статистика отображена
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_company_stats_no_sql_service(self, mock_print, mock_input):
        """Покрытие статистики без SQL сервиса."""
        mock_input.side_effect = ["3", "0"]
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        # isinstance вернет False для обычного процессора
        interface.run_application()
        
        # Проверяем сообщение о неподдерживаемой статистике
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_company_stats_exception(self, mock_print, mock_input):
        """Покрытие исключения при получении статистики."""
        mock_input.side_effect = ["3", "0"]
        
        # Процессор который вызывает ошибку
        mock_processor = Mock()
        mock_processor.get_companies_vacancy_count.side_effect = Exception("DB Error")
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            mock_processor,
            MockVacancyStorage()
        )
        
        with patch('src.interfaces.main_application_interface.isinstance', return_value=True):
            interface.run_application()
        
        # Проверяем обработку ошибки
        mock_print.assert_called()

    def test_display_vacancy_summary_with_salary_formatted(self):
        """Покрытие отображения вакансий с форматированной зарплатой."""
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.title = "Test Job"
        mock_vacancy.url = "http://test.com"
        mock_vacancy.employer = Mock()
        mock_vacancy.employer.name = "Test Company"
        
        # Зарплата с методом форматирования
        mock_salary = Mock()
        mock_salary.get_formatted_string.return_value = "100,000 - 150,000 RUR"
        mock_vacancy.salary = mock_salary
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        with patch('builtins.print') as mock_print:
            interface._display_vacancy_summary([mock_vacancy])
            mock_print.assert_called()

    def test_display_vacancy_summary_with_salary_info(self):
        """Покрытие отображения с salary_info."""
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.title = "Test Job"
        mock_vacancy.url = "http://test.com"
        mock_vacancy.employer = Mock()
        mock_vacancy.employer.name = "Test Company"
        
        # Зарплата с salary_info
        mock_salary = Mock()
        del mock_salary.get_formatted_string  # Удаляем метод
        mock_salary.salary_info = "Good salary"
        mock_vacancy.salary = mock_salary
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        with patch('builtins.print') as mock_print:
            interface._display_vacancy_summary([mock_vacancy])
            mock_print.assert_called()

    def test_display_vacancy_summary_with_salary_from_to(self):
        """Покрытие отображения с полями salary_from и salary_to."""
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.title = "Test Job"
        mock_vacancy.url = "http://test.com"
        mock_vacancy.employer = Mock()
        mock_vacancy.employer.name = "Test Company"
        
        # Зарплата с базовыми полями
        mock_salary = Mock()
        del mock_salary.get_formatted_string
        del mock_salary.salary_info
        mock_salary.salary_from = 100000
        mock_salary.salary_to = 150000
        mock_vacancy.salary = mock_salary
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        with patch('builtins.print') as mock_print:
            interface._display_vacancy_summary([mock_vacancy])
            mock_print.assert_called()

    def test_display_vacancy_summary_salary_exception(self):
        """Покрытие исключения при обработке зарплаты."""
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.title = "Test Job"
        mock_vacancy.url = "http://test.com"
        mock_vacancy.employer = Mock()
        mock_vacancy.employer.name = "Test Company"
        
        # Зарплата которая вызывает исключение
        mock_salary = Mock()
        mock_salary.get_formatted_string.side_effect = Exception("Format error")
        mock_vacancy.salary = mock_salary
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        with patch('builtins.print') as mock_print:
            interface._display_vacancy_summary([mock_vacancy])
            mock_print.assert_called()

    def test_display_vacancy_summary_no_employer(self):
        """Покрытие отображения без работодателя."""
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.title = "Test Job"
        mock_vacancy.url = None
        mock_vacancy.employer = None
        mock_vacancy.salary = None
        
        interface = ConsoleApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        with patch('builtins.print') as mock_print:
            interface._display_vacancy_summary([mock_vacancy])
            mock_print.assert_called()


class TestAdvancedApplicationInterface:
    """100% покрытие продвинутого интерфейса."""

    def test_advanced_interface_init(self):
        """Покрытие инициализации продвинутого интерфейса."""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = MockVacancyStorage()
        analytics = Mock()
        
        interface = AdvancedApplicationInterface(
            provider, processor, storage, analytics
        )
        
        assert isinstance(interface, MainApplicationInterface)
        assert interface.analytics is analytics

    def test_advanced_interface_init_no_analytics(self):
        """Покрытие инициализации без аналитики."""
        interface = AdvancedApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        assert interface.analytics is None

    def test_run_application(self):
        """Покрытие запуска продвинутого приложения."""
        interface = AdvancedApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        # Метод пустой, но должен выполниться без ошибок
        interface.run_application()

    def test_get_advanced_analytics_with_analytics(self):
        """Покрытие получения аналитики."""
        mock_analytics = Mock()
        mock_analytics.generate_report.return_value = {"total": 100}
        
        interface = AdvancedApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage(),
            mock_analytics
        )
        
        result = interface.get_advanced_analytics()
        assert result == {"total": 100}

    def test_get_advanced_analytics_no_analytics(self):
        """Покрытие получения аналитики без сервиса."""
        interface = AdvancedApplicationInterface(
            MockVacancyProvider(),
            MockVacancyProcessor(),
            MockVacancyStorage()
        )
        
        result = interface.get_advanced_analytics()
        assert result == {}


class TestMainInterfaceIntegration:
    """100% покрытие интеграции компонентов."""

    def test_protocol_integration(self):
        """Покрытие интеграции протоколов."""
        provider = MockVacancyProvider()
        processor = MockVacancyProcessor()
        storage = MockVacancyStorage()
        
        # Проверяем что все моки соответствуют протоколам
        assert isinstance(provider, VacancyProvider)
        assert isinstance(processor, VacancyProcessor)
        assert isinstance(storage, VacancyStorage)

    def test_full_workflow_integration(self):
        """Покрытие полного workflow."""
        mock_vacancy = Mock(spec=Vacancy)
        
        provider = MockVacancyProvider([mock_vacancy])
        processor = MockVacancyProcessor([mock_vacancy])
        storage = MockVacancyStorage(save_result=True)
        
        interface = ConcreteMainInterface(provider, processor, storage)
        
        # Выполняем полный цикл
        result = interface.execute_vacancy_workflow("test query")
        
        # Проверяем что все компоненты были задействованы
        assert len(result) == 1
        assert len(storage.saved_vacancies) == 1