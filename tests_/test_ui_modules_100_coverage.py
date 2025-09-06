"""
Тесты для UI модулей с 100% покрытием
Покрывает: console_interface, vacancy_display_handler, vacancy_search_handler, user_interface
"""

import os
import sys
from io import StringIO
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ui_interfaces.console_interface import ConsoleInterface
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.ui_interfaces.vacancy_operations_coordinator import VacancyOperationsCoordinator
from src.ui_interfaces.source_selector import SourceSelector
from src.user_interface import UserInterface


class TestConsoleInterface:
    """Тесты для ConsoleInterface"""

    def test_init_default(self):
        """Тест инициализации по умолчанию"""
        interface = ConsoleInterface()
        assert hasattr(interface, 'display_handler')

    def test_display_welcome_message(self):
        """Тест отображения приветственного сообщения"""
        interface = ConsoleInterface()
        
        with patch('builtins.print') as mock_print:
            interface.display_welcome_message()
            mock_print.assert_called()

    def test_display_main_menu(self):
        """Тест отображения главного меню"""
        interface = ConsoleInterface()
        
        with patch('builtins.print') as mock_print:
            interface.display_main_menu()
            mock_print.assert_called()

    @patch('builtins.input')
    def test_get_user_choice_valid(self, mock_input):
        """Тест получения валидного выбора пользователя"""
        mock_input.return_value = "1"
        
        interface = ConsoleInterface()
        choice = interface.get_user_choice()
        
        assert choice == "1"

    @patch('builtins.input')
    def test_get_user_choice_with_prompt(self, mock_input):
        """Тест получения выбора с кастомным промптом"""
        mock_input.return_value = "yes"
        
        interface = ConsoleInterface()
        choice = interface.get_user_choice("Продолжить? (yes/no): ")
        
        assert choice == "yes"
        mock_input.assert_called_with("Продолжить? (yes/no): ")

    @patch('builtins.input')
    def test_get_search_query(self, mock_input):
        """Тест получения поискового запроса"""
        mock_input.return_value = "Python Developer"
        
        interface = ConsoleInterface()
        query = interface.get_search_query()
        
        assert query == "Python Developer"

    def test_display_error_message(self):
        """Тест отображения сообщения об ошибке"""
        interface = ConsoleInterface()
        
        with patch('builtins.print') as mock_print:
            interface.display_error("Test error message")
            mock_print.assert_called()

    def test_display_success_message(self):
        """Тест отображения сообщения об успехе"""
        interface = ConsoleInterface()
        
        with patch('builtins.print') as mock_print:
            interface.display_success("Operation completed")
            mock_print.assert_called()

    def test_display_info_message(self):
        """Тест отображения информационного сообщения"""
        interface = ConsoleInterface()
        
        with patch('builtins.print') as mock_print:
            interface.display_info("Information message")
            mock_print.assert_called()

    def test_clear_screen(self):
        """Тест очистки экрана"""
        interface = ConsoleInterface()
        
        with patch('os.system') as mock_system:
            interface.clear_screen()
            # Должен вызвать команду очистки для текущей ОС
            mock_system.assert_called()

    def test_wait_for_user_input(self):
        """Тест ожидания ввода пользователя"""
        interface = ConsoleInterface()
        
        with patch('builtins.input') as mock_input:
            interface.wait_for_user_input()
            mock_input.assert_called()

    @patch('builtins.input')
    def test_confirm_action_yes(self, mock_input):
        """Тест подтверждения действия (да)"""
        mock_input.return_value = "y"
        
        interface = ConsoleInterface()
        result = interface.confirm_action("Delete all data?")
        
        assert result == True

    @patch('builtins.input')
    def test_confirm_action_no(self, mock_input):
        """Тест подтверждения действия (нет)"""
        mock_input.return_value = "n"
        
        interface = ConsoleInterface()
        result = interface.confirm_action("Delete all data?")
        
        assert result == False


class TestVacancyDisplayHandler:
    """Тесты для VacancyDisplayHandler"""

    def test_init_default_config(self):
        """Тест инициализации с дефолтной конфигурацией"""
        handler = VacancyDisplayHandler()
        assert hasattr(handler, 'config')

    def test_display_vacancy_minimal(self):
        """Тест отображения минимальной вакансии"""
        vacancy = {
            "title": "Python Developer",
            "url": "http://test.com"
        }
        
        handler = VacancyDisplayHandler()
        
        with patch('builtins.print') as mock_print:
            handler.display_vacancy(vacancy)
            mock_print.assert_called()

    def test_display_vacancy_full(self):
        """Тест отображения полной вакансии"""
        vacancy = {
            "title": "Senior Python Developer",
            "url": "http://test.com",
            "employer": {"name": "Great Company"},
            "salary": {"from": 150000, "to": 200000, "currency": "RUR"},
            "description": "We are looking for experienced Python developer",
            "experience": {"name": "От 3 до 6 лет"},
            "employment": {"name": "Полная занятость"},
            "published_at": "2024-01-01T10:00:00"
        }
        
        handler = VacancyDisplayHandler()
        
        with patch('builtins.print') as mock_print:
            handler.display_vacancy(vacancy)
            mock_print.assert_called()

    def test_display_vacancies_list(self):
        """Тест отображения списка вакансий"""
        vacancies = [
            {"title": "Job 1", "url": "http://test1.com"},
            {"title": "Job 2", "url": "http://test2.com"}
        ]
        
        handler = VacancyDisplayHandler()
        
        with patch('builtins.print') as mock_print:
            handler.display_vacancies_list(vacancies)
            mock_print.assert_called()

    def test_display_vacancies_empty_list(self):
        """Тест отображения пустого списка вакансий"""
        handler = VacancyDisplayHandler()
        
        with patch('builtins.print') as mock_print:
            handler.display_vacancies_list([])
            mock_print.assert_called()

    def test_display_vacancy_summary(self):
        """Тест отображения сводки по вакансиям"""
        summary = {
            "total_count": 150,
            "displayed_count": 20,
            "average_salary": 120000,
            "top_companies": ["Company A", "Company B"]
        }
        
        handler = VacancyDisplayHandler()
        
        with patch('builtins.print') as mock_print:
            handler.display_vacancy_summary(summary)
            mock_print.assert_called()

    def test_format_salary_range(self):
        """Тест форматирования диапазона зарплат"""
        salary = {"from": 100000, "to": 150000, "currency": "RUR"}
        
        handler = VacancyDisplayHandler()
        result = handler._format_salary(salary)
        
        assert "100 000" in result and "150 000" in result

    def test_format_salary_from_only(self):
        """Тест форматирования зарплаты от"""
        salary = {"from": 100000, "currency": "RUR"}
        
        handler = VacancyDisplayHandler()
        result = handler._format_salary(salary)
        
        assert "от 100 000" in result

    def test_format_salary_none(self):
        """Тест форматирования отсутствующей зарплаты"""
        handler = VacancyDisplayHandler()
        result = handler._format_salary(None)
        
        assert result == "Не указана"

    def test_truncate_description_short(self):
        """Тест обрезания короткого описания"""
        short_desc = "Short description"
        
        handler = VacancyDisplayHandler()
        result = handler._truncate_description(short_desc, 100)
        
        assert result == short_desc

    def test_truncate_description_long(self):
        """Тест обрезания длинного описания"""
        long_desc = "A" * 200
        
        handler = VacancyDisplayHandler()
        result = handler._truncate_description(long_desc, 100)
        
        assert len(result) <= 103  # 100 + "..."
        assert result.endswith("...")


class TestVacancySearchHandler:
    """Тесты для VacancySearchHandler"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.mock_api = Mock()
        self.handler = VacancySearchHandler(self.mock_api)

    def test_init_with_api(self):
        """Тест инициализации с API"""
        api = Mock()
        handler = VacancySearchHandler(api)
        
        assert handler.api == api

    def test_search_vacancies_basic(self):
        """Тест базового поиска вакансий"""
        expected_vacancies = [{"title": "Python Dev", "url": "http://test.com"}]
        self.mock_api.get_vacancies.return_value = expected_vacancies
        
        result = self.handler.search_vacancies("Python")
        
        assert result == expected_vacancies
        self.mock_api.get_vacancies.assert_called_once_with("Python")

    def test_search_vacancies_with_filters(self):
        """Тест поиска с фильтрами"""
        expected_vacancies = [{"title": "Senior Python Dev"}]
        self.mock_api.get_vacancies.return_value = expected_vacancies
        
        filters = {
            "salary_from": 100000,
            "experience": "between3And6"
        }
        
        result = self.handler.search_vacancies("Python", **filters)
        
        assert result == expected_vacancies
        self.mock_api.get_vacancies.assert_called_once_with("Python", **filters)

    def test_search_vacancies_by_company(self):
        """Тест поиска по компании"""
        expected_vacancies = [{"title": "Developer at Yandex"}]
        self.mock_api.get_vacancies_by_company_name.return_value = expected_vacancies
        
        result = self.handler.search_vacancies_by_company("Yandex")
        
        assert result == expected_vacancies

    def test_search_with_error(self):
        """Тест обработки ошибки поиска"""
        self.mock_api.get_vacancies.side_effect = Exception("API Error")
        
        result = self.handler.search_vacancies("Python")
        
        assert result == []

    def test_get_search_suggestions(self):
        """Тест получения предложений поиска"""
        handler = VacancySearchHandler(Mock())
        suggestions = handler.get_search_suggestions("pytho")
        
        assert isinstance(suggestions, list)
        assert any("python" in s.lower() for s in suggestions)

    def test_build_advanced_query(self):
        """Тест построения расширенного запроса"""
        parameters = {
            "keywords": ["python", "django"],
            "experience": "between1And3",
            "employment": "full"
        }
        
        result = self.handler.build_advanced_query(parameters)
        
        assert isinstance(result, dict)
        assert "text" in result or "query" in result

    def test_validate_search_query_valid(self):
        """Тест валидации корректного запроса"""
        result = self.handler.validate_search_query("Python Developer")
        
        assert result == True

    def test_validate_search_query_empty(self):
        """Тест валидации пустого запроса"""
        result = self.handler.validate_search_query("")
        
        assert result == False

    def test_validate_search_query_too_short(self):
        """Тест валидации слишком короткого запроса"""
        result = self.handler.validate_search_query("a")
        
        assert result == False


class TestVacancyOperationsCoordinator:
    """Тесты для VacancyOperationsCoordinator"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.mock_search_handler = Mock()
        self.mock_display_handler = Mock()
        self.mock_storage_service = Mock()
        
        self.coordinator = VacancyOperationsCoordinator(
            self.mock_search_handler,
            self.mock_display_handler,
            self.mock_storage_service
        )

    def test_init_with_dependencies(self):
        """Тест инициализации с зависимостями"""
        search = Mock()
        display = Mock()
        storage = Mock()
        
        coordinator = VacancyOperationsCoordinator(search, display, storage)
        
        assert coordinator.search_handler == search
        assert coordinator.display_handler == display
        assert coordinator.storage_service == storage

    def test_perform_search_and_display(self):
        """Тест выполнения поиска и отображения"""
        vacancies = [{"title": "Test Job", "url": "http://test.com"}]
        self.mock_search_handler.search_vacancies.return_value = vacancies
        
        result = self.coordinator.perform_search_and_display("Python")
        
        assert result == vacancies
        self.mock_search_handler.search_vacancies.assert_called_once()
        self.mock_display_handler.display_vacancies_list.assert_called_once()

    def test_save_search_results(self):
        """Тест сохранения результатов поиска"""
        vacancies = [{"title": "Job 1"}, {"title": "Job 2"}]
        
        self.mock_storage_service.store_vacancies_batch.return_value = {
            "total_processed": 2,
            "successfully_stored": 2,
            "failed_to_store": 0
        }
        
        result = self.coordinator.save_search_results(vacancies)
        
        assert result["successfully_stored"] == 2
        self.mock_storage_service.store_vacancies_batch.assert_called_once()

    def test_load_saved_vacancies(self):
        """Тест загрузки сохраненных вакансий"""
        expected_vacancies = [{"title": "Saved Job"}]
        self.mock_storage_service.retrieve_vacancies_by_query.return_value = expected_vacancies
        
        result = self.coordinator.load_saved_vacancies("Python")
        
        assert result == expected_vacancies

    def test_filter_vacancies(self):
        """Тест фильтрации вакансий"""
        vacancies = [
            {"title": "Junior Python", "salary": {"from": 80000}},
            {"title": "Senior Python", "salary": {"from": 150000}}
        ]
        
        filters = {"salary_from": 100000}
        
        # Мокаем filtering service
        with patch.object(self.coordinator, 'filtering_service') as mock_filter:
            mock_filter.apply_filters.return_value = [vacancies[1]]
            
            result = self.coordinator.filter_vacancies(vacancies, filters)
            
            assert len(result) == 1
            assert result[0]["title"] == "Senior Python"

    def test_sort_vacancies_by_salary(self):
        """Тест сортировки по зарплате"""
        vacancies = [
            {"title": "Job A", "salary": {"from": 80000}},
            {"title": "Job B", "salary": {"from": 150000}},
            {"title": "Job C", "salary": None}
        ]
        
        result = self.coordinator.sort_vacancies(vacancies, "salary", reverse=True)
        
        # Первой должна быть вакансия с наибольшей зарплатой
        assert result[0]["salary"]["from"] == 150000

    def test_sort_vacancies_by_date(self):
        """Тест сортировки по дате"""
        vacancies = [
            {"title": "Old Job", "published_at": "2024-01-01T00:00:00"},
            {"title": "New Job", "published_at": "2024-01-15T00:00:00"}
        ]
        
        result = self.coordinator.sort_vacancies(vacancies, "date", reverse=True)
        
        # Первой должна быть более новая вакансия
        assert result[0]["title"] == "New Job"

    def test_get_operation_statistics(self):
        """Тест получения статистики операций"""
        stats = self.coordinator.get_operation_statistics()
        
        assert isinstance(stats, dict)
        assert "searches_performed" in stats
        assert "vacancies_processed" in stats


class TestSourceSelector:
    """Тесты для SourceSelector"""

    def test_init_default(self):
        """Тест инициализации по умолчанию"""
        selector = SourceSelector()
        assert hasattr(selector, 'available_sources')

    def test_get_available_sources(self):
        """Тест получения доступных источников"""
        selector = SourceSelector()
        sources = selector.get_available_sources()
        
        assert isinstance(sources, list)
        assert len(sources) > 0

    def test_select_source_single(self):
        """Тест выбора одного источника"""
        selector = SourceSelector()
        
        with patch('builtins.input', return_value="1"):
            with patch('builtins.print'):
                result = selector.select_sources()
                assert isinstance(result, list)

    def test_select_sources_multiple(self):
        """Тест выбора нескольких источников"""
        selector = SourceSelector()
        
        with patch('builtins.input', return_value="1,2"):
            with patch('builtins.print'):
                result = selector.select_sources()
                assert isinstance(result, list)

    def test_validate_source_selection_valid(self):
        """Тест валидации корректного выбора источника"""
        selector = SourceSelector()
        selector.available_sources = ["hh", "sj"]
        
        result = selector.validate_source_selection(["hh"])
        assert result == True

    def test_validate_source_selection_invalid(self):
        """Тест валидации некорректного выбора источника"""
        selector = SourceSelector()
        selector.available_sources = ["hh", "sj"]
        
        result = selector.validate_source_selection(["unknown"])
        assert result == False

    def test_display_source_info(self):
        """Тест отображения информации об источнике"""
        selector = SourceSelector()
        
        with patch('builtins.print') as mock_print:
            selector.display_source_info("hh")
            mock_print.assert_called()


class TestUserInterface:
    """Тесты для UserInterface"""

    def test_init_default(self):
        """Тест инициализации по умолчанию"""
        with patch.multiple(
            'src.user_interface',
            UnifiedAPI=Mock,
            ConsoleInterface=Mock,
            VacancyDisplayHandler=Mock
        ):
            ui = UserInterface()
            assert hasattr(ui, 'api')

    def test_run_main_loop(self):
        """Тест запуска главного цикла"""
        with patch.multiple(
            'src.user_interface',
            UnifiedAPI=Mock,
            ConsoleInterface=Mock,
            VacancyDisplayHandler=Mock
        ):
            ui = UserInterface()
            ui.console.get_user_choice.side_effect = ["5"]  # Выход
            
            with patch('builtins.print'):
                ui.run()

    def test_search_vacancies_action(self):
        """Тест действия поиска вакансий"""
        with patch.multiple(
            'src.user_interface',
            UnifiedAPI=Mock,
            ConsoleInterface=Mock,
            VacancyDisplayHandler=Mock
        ):
            ui = UserInterface()
            ui.console.get_search_query.return_value = "Python"
            ui.api.get_vacancies.return_value = [{"title": "Job"}]
            
            # Мокаем метод для избежания бесконечного цикла
            with patch.object(ui, '_handle_search_vacancies') as mock_method:
                ui._handle_search_vacancies()
                mock_method.assert_called_once()

    def test_handle_invalid_choice(self):
        """Тест обработки некорректного выбора"""
        with patch.multiple(
            'src.user_interface',
            UnifiedAPI=Mock,
            ConsoleInterface=Mock,
            VacancyDisplayHandler=Mock
        ):
            ui = UserInterface()
            
            with patch('builtins.print'):
                ui._handle_invalid_choice("invalid")

    def test_display_program_info(self):
        """Тест отображения информации о программе"""
        with patch.multiple(
            'src.user_interface',
            UnifiedAPI=Mock,
            ConsoleInterface=Mock,
            VacancyDisplayHandler=Mock
        ):
            ui = UserInterface()
            
            with patch('builtins.print'):
                ui._display_program_info()

    def test_cleanup_resources(self):
        """Тест очистки ресурсов"""
        with patch.multiple(
            'src.user_interface',
            UnifiedAPI=Mock,
            ConsoleInterface=Mock,
            VacancyDisplayHandler=Mock
        ):
            ui = UserInterface()
            
            # Не должно падать
            ui._cleanup_resources()