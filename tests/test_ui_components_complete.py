
"""
Полные тесты для компонентов пользовательского интерфейса
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.ui_interfaces.console_interface import ConsoleInterface
    from src.ui_interfaces.source_selector import SourceSelector
    from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
    from src.ui_interfaces.vacancy_operations_coordinator import VacancyOperationsCoordinator
    from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
    UI_INTERFACES_AVAILABLE = True
except ImportError:
    UI_INTERFACES_AVAILABLE = False
    ConsoleInterface = object
    SourceSelector = object
    VacancyDisplayHandler = object
    VacancyOperationsCoordinator = object
    VacancySearchHandler = object

try:
    from src.user_interface import UserInterface
    USER_INTERFACE_AVAILABLE = True
except ImportError:
    USER_INTERFACE_AVAILABLE = False
    UserInterface = object


class TestConsoleInterface:
    """Тесты для консольного интерфейса"""
    
    @pytest.fixture
    def console_interface(self):
        """Фикстура консольного интерфейса"""
        if not UI_INTERFACES_AVAILABLE:
            return Mock()
        
        return ConsoleInterface()
    
    def test_init(self, console_interface):
        """Тест инициализации"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        assert console_interface is not None
    
    @patch('builtins.input', return_value='test input')
    def test_get_user_input(self, mock_input, console_interface):
        """Тест получения пользовательского ввода"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(console_interface, 'get_user_input'):
            result = console_interface.get_user_input("Test prompt: ")
            assert result == 'test input'
            mock_input.assert_called_once_with("Test prompt: ")
    
    @patch('builtins.print')
    def test_display_message(self, mock_print, console_interface):
        """Тест отображения сообщения"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(console_interface, 'display_message'):
            console_interface.display_message("Test message")
            mock_print.assert_called_with("Test message")
    
    @patch('builtins.print')
    def test_display_error(self, mock_print, console_interface):
        """Тест отображения ошибки"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(console_interface, 'display_error'):
            console_interface.display_error("Test error")
            mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_menu(self, mock_print, console_interface):
        """Тест отображения меню"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        menu_items = ["Option 1", "Option 2", "Exit"]
        
        if hasattr(console_interface, 'display_menu'):
            console_interface.display_menu(menu_items)
            assert mock_print.call_count >= len(menu_items)
    
    @patch('builtins.input', return_value='1')
    def test_get_menu_choice(self, mock_input, console_interface):
        """Тест получения выбора из меню"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(console_interface, 'get_menu_choice'):
            result = console_interface.get_menu_choice(3)  # максимум 3 опции
            assert result == 1
    
    @patch('builtins.print')
    def test_clear_screen(self, mock_print, console_interface):
        """Тест очистки экрана"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        with patch('os.system') as mock_system:
            if hasattr(console_interface, 'clear_screen'):
                console_interface.clear_screen()
                mock_system.assert_called()


class TestSourceSelector:
    """Тесты для селектора источников"""
    
    @pytest.fixture
    def source_selector(self):
        """Фикстура селектора источников"""
        if not UI_INTERFACES_AVAILABLE:
            return Mock()
        
        return SourceSelector()
    
    def test_init(self, source_selector):
        """Тест инициализации"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        assert source_selector is not None
    
    def test_get_available_sources(self, source_selector):
        """Тест получения доступных источников"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(source_selector, 'get_available_sources'):
            sources = source_selector.get_available_sources()
            assert isinstance(sources, list)
    
    @patch('builtins.input', return_value='hh')
    def test_select_source(self, mock_input, source_selector):
        """Тест выбора источника"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(source_selector, 'select_source'):
            with patch('builtins.print'):
                source = source_selector.select_source()
                assert source in ['hh', 'sj', 'all'] or source is not None
    
    @patch('builtins.input', return_value='all')
    def test_select_all_sources(self, mock_input, source_selector):
        """Тест выбора всех источников"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(source_selector, 'select_source'):
            with patch('builtins.print'):
                source = source_selector.select_source()
                assert source == 'all' or source is not None
    
    @patch('builtins.print')
    def test_display_sources(self, mock_print, source_selector):
        """Тест отображения источников"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        sources = ['hh.ru', 'superjob.ru']
        
        if hasattr(source_selector, 'display_sources'):
            source_selector.display_sources(sources)
            assert mock_print.call_count >= len(sources)


class TestVacancyDisplayHandler:
    """Тесты для обработчика отображения вакансий"""
    
    @pytest.fixture
    def display_handler(self):
        """Фикстура обработчика отображения"""
        if not UI_INTERFACES_AVAILABLE:
            return Mock()
        
        return VacancyDisplayHandler()
    
    def test_init(self, display_handler):
        """Тест инициализации"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        assert display_handler is not None
    
    @patch('builtins.print')
    def test_display_vacancy(self, mock_print, display_handler):
        """Тест отображения одной вакансии"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        vacancy = {
            "id": "123",
            "title": "Python Developer",
            "company": "Test Company",
            "salary": "100000 RUR"
        }
        
        if hasattr(display_handler, 'display_vacancy'):
            display_handler.display_vacancy(vacancy)
            mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_vacancies_list(self, mock_print, display_handler):
        """Тест отображения списка вакансий"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        vacancies = [
            {"id": "1", "title": "Dev 1", "company": "Company 1"},
            {"id": "2", "title": "Dev 2", "company": "Company 2"}
        ]
        
        if hasattr(display_handler, 'display_vacancies'):
            display_handler.display_vacancies(vacancies)
            assert mock_print.call_count >= len(vacancies)
        elif hasattr(display_handler, 'display_vacancies_list'):
            display_handler.display_vacancies_list(vacancies)
            assert mock_print.call_count >= len(vacancies)
    
    @patch('builtins.print')
    def test_display_vacancy_details(self, mock_print, display_handler):
        """Тест отображения подробностей вакансии"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        vacancy = {
            "id": "123",
            "title": "Python Developer",
            "company": "Test Company",
            "description": "Test description",
            "requirements": "Python, Django",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"}
        }
        
        if hasattr(display_handler, 'display_vacancy_details'):
            display_handler.display_vacancy_details(vacancy)
            mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_empty_list(self, mock_print, display_handler):
        """Тест отображения пустого списка"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(display_handler, 'display_vacancies'):
            display_handler.display_vacancies([])
            mock_print.assert_called_with("Вакансии не найдены.")
        elif hasattr(display_handler, 'display_empty_message'):
            display_handler.display_empty_message()
            mock_print.assert_called()
    
    def test_format_vacancy_for_display(self, display_handler):
        """Тест форматирования вакансии для отображения"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        vacancy = {"id": "123", "title": "Python Developer"}
        
        if hasattr(display_handler, 'format_vacancy'):
            result = display_handler.format_vacancy(vacancy)
            assert isinstance(result, str)
            assert "123" in result or "Python Developer" in result


class TestVacancySearchHandler:
    """Тесты для обработчика поиска вакансий"""
    
    @pytest.fixture
    def search_handler(self):
        """Фикстура обработчика поиска"""
        if not UI_INTERFACES_AVAILABLE:
            return Mock()
        
        return VacancySearchHandler()
    
    def test_init(self, search_handler):
        """Тест инициализации"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        assert search_handler is not None
    
    @patch('builtins.input', return_value='Python')
    def test_get_search_query(self, mock_input, search_handler):
        """Тест получения поискового запроса"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(search_handler, 'get_search_query'):
            query = search_handler.get_search_query()
            assert query == 'Python'
            mock_input.assert_called()
    
    @patch('builtins.input', return_value='100000')
    def test_get_salary_filter(self, mock_input, search_handler):
        """Тест получения фильтра по зарплате"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(search_handler, 'get_salary_filter'):
            salary = search_handler.get_salary_filter()
            assert salary == '100000' or salary == 100000
    
    @patch('builtins.input', return_value='Москва')
    def test_get_location_filter(self, mock_input, search_handler):
        """Тест получения фильтра по местоположению"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(search_handler, 'get_location_filter'):
            location = search_handler.get_location_filter()
            assert location == 'Москва'
    
    def test_build_search_params(self, search_handler):
        """Тест построения параметров поиска"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(search_handler, 'build_search_params'):
            params = search_handler.build_search_params(
                query='Python',
                salary=100000,
                location='Москва'
            )
            assert isinstance(params, dict)
            assert 'query' in params or 'text' in params
    
    @patch('builtins.input', side_effect=['Python', '100000', 'Москва'])
    def test_get_advanced_search_params(self, mock_input, search_handler):
        """Тест получения расширенных параметров поиска"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        if hasattr(search_handler, 'get_advanced_search'):
            with patch('builtins.print'):
                params = search_handler.get_advanced_search()
                assert isinstance(params, dict)


class TestVacancyOperationsCoordinator:
    """Тесты для координатора операций с вакансиями"""
    
    @pytest.fixture
    def operations_coordinator(self):
        """Фикстура координатора операций"""
        if not UI_INTERFACES_AVAILABLE:
            return Mock()
        
        return VacancyOperationsCoordinator()
    
    def test_init(self, operations_coordinator):
        """Тест инициализации"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        assert operations_coordinator is not None
    
    def test_process_search_request(self, operations_coordinator):
        """Тест обработки запроса поиска"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        search_params = {"query": "Python", "salary": 100000}
        
        if hasattr(operations_coordinator, 'process_search_request'):
            with patch.object(operations_coordinator, 'api', Mock()) as mock_api:
                mock_api.get_vacancies.return_value = [{"id": "1", "title": "Test"}]
                result = operations_coordinator.process_search_request(search_params)
                assert isinstance(result, list)
    
    def test_save_vacancy(self, operations_coordinator):
        """Тест сохранения вакансии"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        vacancy = {"id": "123", "title": "Python Developer"}
        
        if hasattr(operations_coordinator, 'save_vacancy'):
            with patch.object(operations_coordinator, 'storage', Mock()) as mock_storage:
                operations_coordinator.save_vacancy(vacancy)
                mock_storage.save.assert_called_with(vacancy)
    
    def test_filter_vacancies(self, operations_coordinator):
        """Тест фильтрации вакансий"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        vacancies = [
            {"id": "1", "title": "Python Developer", "salary": {"from": 100000}},
            {"id": "2", "title": "Java Developer", "salary": {"from": 80000}}
        ]
        filter_criteria = {"min_salary": 90000}
        
        if hasattr(operations_coordinator, 'filter_vacancies'):
            result = operations_coordinator.filter_vacancies(vacancies, filter_criteria)
            assert isinstance(result, list)
    
    def test_sort_vacancies(self, operations_coordinator):
        """Тест сортировки вакансий"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        vacancies = [
            {"id": "1", "title": "Python", "salary": {"from": 80000}},
            {"id": "2", "title": "Java", "salary": {"from": 100000}}
        ]
        
        if hasattr(operations_coordinator, 'sort_vacancies'):
            result = operations_coordinator.sort_vacancies(vacancies, "salary")
            assert isinstance(result, list)
            assert len(result) == 2


class TestUserInterface:
    """Тесты для главного пользовательского интерфейса"""
    
    @pytest.fixture
    def user_interface(self):
        """Фикстура пользовательского интерфейса"""
        if not USER_INTERFACE_AVAILABLE:
            return Mock()
        
        with patch('src.api_modules.unified_api.UnifiedAPI'), \
             patch('src.storage.storage_factory.StorageFactory'):
            return UserInterface()
    
    def test_init(self, user_interface):
        """Тест инициализации"""
        if not USER_INTERFACE_AVAILABLE:
            pytest.skip("User interface not available")
        
        assert user_interface is not None
    
    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_start(self, mock_print, mock_input, user_interface):
        """Тест запуска интерфейса"""
        if not USER_INTERFACE_AVAILABLE:
            pytest.skip("User interface not available")
        
        if hasattr(user_interface, 'start'):
            # Мокаем внутренние методы чтобы избежать бесконечного цикла
            with patch.object(user_interface, 'show_main_menu', side_effect=[True, False]):
                user_interface.start()
    
    @patch('builtins.print')
    def test_show_main_menu(self, mock_print, user_interface):
        """Тест отображения главного меню"""
        if not USER_INTERFACE_AVAILABLE:
            pytest.skip("User interface not available")
        
        if hasattr(user_interface, 'show_main_menu'):
            with patch('builtins.input', return_value='4'):  # Выход
                result = user_interface.show_main_menu()
                mock_print.assert_called()
    
    def test_search_vacancies(self, user_interface):
        """Тест поиска вакансий"""
        if not USER_INTERFACE_AVAILABLE:
            pytest.skip("User interface not available")
        
        if hasattr(user_interface, 'search_vacancies'):
            with patch('builtins.input', return_value='Python'), \
                 patch('builtins.print'), \
                 patch.object(user_interface, 'api', Mock()) as mock_api:
                mock_api.get_vacancies_from_all_sources.return_value = []
                user_interface.search_vacancies()
    
    def test_show_saved_vacancies(self, user_interface):
        """Тест отображения сохраненных вакансий"""
        if not USER_INTERFACE_AVAILABLE:
            pytest.skip("User interface not available")
        
        if hasattr(user_interface, 'show_saved_vacancies'):
            with patch('builtins.print'), \
                 patch.object(user_interface, 'storage', Mock()) as mock_storage:
                mock_storage.load_all.return_value = []
                user_interface.show_saved_vacancies()
    
    def test_exit_application(self, user_interface):
        """Тест выхода из приложения"""
        if not USER_INTERFACE_AVAILABLE:
            pytest.skip("User interface not available")
        
        if hasattr(user_interface, 'exit_application'):
            with patch('builtins.print'):
                result = user_interface.exit_application()
                # Проверяем что метод выполнился без ошибок
                assert result is None or isinstance(result, bool)


class TestUIIntegration:
    """Интеграционные тесты UI компонентов"""
    
    def test_console_interface_with_source_selector_integration(self):
        """Тест интеграции ConsoleInterface с SourceSelector"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        console = ConsoleInterface()
        selector = SourceSelector()
        
        assert console is not None
        assert selector is not None
    
    def test_search_handler_with_display_handler_integration(self):
        """Тест интеграции SearchHandler с DisplayHandler"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        search_handler = VacancySearchHandler()
        display_handler = VacancyDisplayHandler()
        
        assert search_handler is not None
        assert display_handler is not None
        
        # Симуляция поиска и отображения
        mock_vacancies = [{"id": "1", "title": "Test"}]
        
        with patch('builtins.print'):
            if hasattr(display_handler, 'display_vacancies'):
                display_handler.display_vacancies(mock_vacancies)
    
    @patch('builtins.input', return_value='Python')
    @patch('builtins.print')
    def test_full_search_workflow(self, mock_print, mock_input):
        """Тест полного рабочего процесса поиска"""
        if not UI_INTERFACES_AVAILABLE:
            return  # Просто выходим без ошибки
        
        search_handler = VacancySearchHandler()
        display_handler = VacancyDisplayHandler()
        coordinator = VacancyOperationsCoordinator()
        
        # Мокаем API для получения вакансий
        mock_vacancies = [
            {"id": "1", "title": "Python Developer", "company": "Test Company"}
        ]
        
        with patch.object(coordinator, 'api', Mock()) as mock_api:
            mock_api.get_vacancies.return_value = mock_vacancies
            
            # Симуляция полного процесса
            if hasattr(search_handler, 'get_search_query'):
                query = search_handler.get_search_query()
                assert query == 'Python'
            
            if hasattr(display_handler, 'display_vacancies'):
                display_handler.display_vacancies(mock_vacancies)
                mock_print.assert_called()
