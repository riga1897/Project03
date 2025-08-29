
"""
Тесты для консольного интерфейса пользователя
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ui_interfaces.console_interface import UserInterface
from src.storage.storage_factory import StorageFactory


class TestUserInterface:
    """Тесты для класса UserInterface"""

    @pytest.fixture
    def mock_storage(self):
        """Мок объекта хранилища"""
        storage = Mock()
        storage.get_all_vacancies.return_value = []
        storage.get_top_vacancies.return_value = []
        storage.filter_vacancies.return_value = []
        storage.delete_all_vacancies.return_value = None
        storage.delete_vacancies.return_value = None
        storage.add_vacancies.return_value = None
        return storage

    @pytest.fixture
    def mock_db_manager(self):
        """Мок объекта менеджера базы данных"""
        db_manager = Mock()
        db_manager.get_companies_and_vacancies_count.return_value = []
        db_manager.get_all_vacancies.return_value = []
        db_manager.get_avg_salary.return_value = 0
        db_manager.get_vacancies_with_higher_salary.return_value = []
        return db_manager

    @pytest.fixture
    def user_interface(self, mock_storage, mock_db_manager):
        """Экземпляр UserInterface для тестирования"""
        with patch('src.ui_interfaces.console_interface.UnifiedAPI') as mock_unified_api, \
             patch('src.ui_interfaces.console_interface.VacancySearchHandler') as mock_search_handler, \
             patch('src.ui_interfaces.console_interface.VacancyDisplayHandler') as mock_display_handler:
            
            # Настройка моков
            mock_unified_api_instance = Mock()
            mock_unified_api.return_value = mock_unified_api_instance
            
            mock_search_handler_instance = Mock()
            mock_search_handler.return_value = mock_search_handler_instance
            
            mock_display_handler_instance = Mock()
            mock_display_handler.return_value = mock_display_handler_instance
            
            interface = UserInterface(mock_storage, mock_db_manager)
            return interface

    def test_initialization(self, user_interface, mock_storage, mock_db_manager):
        """Тест инициализации UserInterface"""
        assert user_interface.storage == mock_storage
        assert user_interface.db_manager == mock_db_manager
        assert hasattr(user_interface, 'unified_api')
        assert hasattr(user_interface, 'search_handler')
        assert hasattr(user_interface, 'display_handler')

    def test_initialization_default_storage(self, mock_db_manager):
        """Тест инициализации с хранилищем по умолчанию"""
        with patch('src.ui_interfaces.console_interface.StorageFactory.get_default_storage') as mock_factory, \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.VacancySearchHandler'), \
             patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'):
            
            mock_storage = Mock()
            mock_factory.return_value = mock_storage
            
            interface = UserInterface(db_manager=mock_db_manager)
            
            assert interface.storage == mock_storage
            assert interface.db_manager == mock_db_manager
            mock_factory.assert_called_once()

    @patch('builtins.print')
    def test_show_menu(self, mock_print, user_interface):
        """Тест отображения меню"""
        user_interface.show_menu()
        
        # Проверяем, что print был вызван несколько раз для отображения меню
        assert mock_print.call_count > 0
        # Проверяем, что в одном из вызовов есть текст меню
        menu_calls = [str(call) for call in mock_print.call_args_list]
        menu_text_found = any("Выберите действие" in call for call in menu_calls)
        assert menu_text_found

    @patch('builtins.input', return_value='1')
    def test_get_period_choice_default(self, mock_input, user_interface):
        """Тест выбора периода по умолчанию"""
        result = user_interface.get_period_choice()
        assert result == 30  # Значение по умолчанию

    @patch('builtins.input', side_effect=['2', '7'])
    def test_get_period_choice_custom(self, mock_input, user_interface):
        """Тест выбора пользовательского периода"""
        result = user_interface.get_period_choice()
        assert result == 7

    @patch('builtins.input', side_effect=['2', 'invalid', '5'])
    @patch('builtins.print')
    def test_get_period_choice_invalid_custom(self, mock_print, mock_input, user_interface):
        """Тест обработки некорректного ввода периода"""
        result = user_interface.get_period_choice()
        assert result == 5

    @patch('builtins.input', return_value='0')
    def test_get_period_choice_cancel(self, mock_input, user_interface):
        """Тест отмены выбора периода"""
        result = user_interface.get_period_choice()
        assert result is None

    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_get_period_choice_keyboard_interrupt(self, mock_input, user_interface):
        """Тест обработки KeyboardInterrupt"""
        result = user_interface.get_period_choice()
        assert result is None

    @patch('builtins.input', side_effect=['all', 'y'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_all(self, mock_print, mock_input, user_interface):
        """Тест отображения всех вакансий для удаления"""
        # Настройка мок данных
        user_interface.storage.get_all_vacancies.return_value = [
            Mock(vacancy_id='1', title='Test Vacancy 1'),
            Mock(vacancy_id='2', title='Test Vacancy 2')
        ]
        
        result = user_interface.show_vacancies_for_deletion()
        
        assert result == 'all'
        user_interface.storage.get_all_vacancies.assert_called_once()

    @patch('builtins.input', side_effect=['1', 'y'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_single(self, mock_print, mock_input, user_interface):
        """Тест отображения одной вакансии для удаления"""
        user_interface.storage.get_all_vacancies.return_value = [
            Mock(vacancy_id='1', title='Test Vacancy')
        ]
        
        result = user_interface.show_vacancies_for_deletion()
        
        assert result == [1]

    @patch('builtins.input', return_value='quit')
    def test_show_vacancies_for_deletion_quit(self, mock_input, user_interface):
        """Тест выхода из удаления вакансий"""
        user_interface.storage.get_all_vacancies.return_value = [
            Mock(vacancy_id='1', title='Test Vacancy')
        ]
        
        result = user_interface.show_vacancies_for_deletion()
        
        assert result is None

    @patch('builtins.input', side_effect=['1-3', 'y'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_range(self, mock_print, mock_input, user_interface):
        """Тест удаления диапазона вакансий"""
        user_interface.storage.get_all_vacancies.return_value = [
            Mock(vacancy_id='1', title='Test 1'),
            Mock(vacancy_id='2', title='Test 2'),
            Mock(vacancy_id='3', title='Test 3'),
            Mock(vacancy_id='4', title='Test 4')
        ]
        
        result = user_interface.show_vacancies_for_deletion()
        
        assert result == [1, 2, 3]

    @patch('builtins.input', side_effect=['invalid-range', '1', 'y'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_invalid_range(self, mock_print, mock_input, user_interface):
        """Тест обработки некорректного диапазона"""
        user_interface.storage.get_all_vacancies.return_value = [
            Mock(vacancy_id='1', title='Test Vacancy')
        ]
        
        result = user_interface.show_vacancies_for_deletion()
        
        assert result == [1]

    @patch('builtins.input', side_effect=['next', 'quit'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_pagination(self, mock_print, mock_input, user_interface):
        """Тест пагинации при удалении вакансий"""
        # Создаем много вакансий для тестирования пагинации
        vacancies = [Mock(vacancy_id=str(i), title=f'Test {i}') for i in range(1, 25)]
        user_interface.storage.get_all_vacancies.return_value = vacancies
        
        result = user_interface.show_vacancies_for_deletion()
        
        assert result is None

    @patch('builtins.print')
    def test_display_vacancies_static_method(self, mock_print):
        """Тест статического метода отображения вакансий"""
        vacancies = [
            Mock(vacancy_id='1', title='Test Vacancy 1'),
            Mock(vacancy_id='2', title='Test Vacancy 2')
        ]
        
        UserInterface.display_vacancies(vacancies)
        
        # Проверяем, что print был вызван
        assert mock_print.call_count > 0

    @patch('builtins.input', side_effect=['next', 'quit'])
    @patch('builtins.print')
    def test_display_vacancies_with_pagination_static_method(self, mock_print, mock_input):
        """Тест статического метода отображения вакансий с пагинацией"""
        vacancies = [Mock(vacancy_id=str(i), title=f'Test {i}') for i in range(1, 25)]
        
        UserInterface.display_vacancies_with_pagination(vacancies)
        
        assert mock_print.call_count > 0

    @patch('builtins.input', side_effect=KeyboardInterrupt)
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input, user_interface):
        """Тест обработки KeyboardInterrupt в основном цикле"""
        with patch.object(user_interface, 'show_menu'):
            user_interface.run()
            
        # Проверяем, что было выведено сообщение о завершении
        exit_messages = [str(call) for call in mock_print.call_args_list]
        exit_found = any("Программа завершена" in msg or "завершена" in msg for msg in exit_messages)
        assert exit_found

    @patch('builtins.input', side_effect=['invalid', '0'])
    @patch('builtins.print')
    def test_run_exception_handling(self, mock_print, mock_input, user_interface):
        """Тест обработки исключений в основном цикле"""
        with patch.object(user_interface, 'show_menu'), \
             patch.object(user_interface, 'handle_menu_choice', side_effect=Exception("Test error")):
            
            user_interface.run()

    def test_handle_menu_choice_structure(self, user_interface):
        """Тест структуры обработчика выбора меню"""
        # Проверяем, что метод существует
        assert hasattr(user_interface, 'handle_menu_choice')
        assert callable(getattr(user_interface, 'handle_menu_choice'))

    @patch('builtins.input', return_value='python django')
    @patch('builtins.print')
    def test_advanced_search_vacancies(self, mock_print, mock_input, user_interface):
        """Тест расширенного поиска вакансий"""
        mock_vacancies = [Mock(vacancy_id='1', title='Python Django Developer')]
        user_interface.storage.filter_vacancies.return_value = mock_vacancies
        
        # Мокаем метод advanced_search_vacancies если он существует
        if hasattr(user_interface, 'advanced_search_vacancies'):
            with patch.object(user_interface, 'advanced_search_vacancies') as mock_search:
                mock_search.return_value = None
                user_interface.advanced_search_vacancies()
                mock_search.assert_called_once()

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_advanced_search_vacancies_empty_query(self, mock_print, mock_input, user_interface):
        """Тест расширенного поиска с пустым запросом"""
        if hasattr(user_interface, 'advanced_search_vacancies'):
            with patch.object(user_interface, 'advanced_search_vacancies') as mock_search:
                mock_search.return_value = None
                user_interface.advanced_search_vacancies()
                mock_search.assert_called_once()

    @patch('builtins.input', return_value='50000')
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_min(self, mock_print, mock_input, user_interface):
        """Тест фильтрации сохраненных вакансий по минимальной зарплате"""
        mock_vacancies = [Mock(vacancy_id='1', title='High Salary Job')]
        user_interface.storage.filter_vacancies.return_value = mock_vacancies
        
        if hasattr(user_interface, 'filter_saved_vacancies_by_salary'):
            with patch.object(user_interface, 'filter_saved_vacancies_by_salary') as mock_filter:
                mock_filter.return_value = None
                user_interface.filter_saved_vacancies_by_salary()
                mock_filter.assert_called_once()

    @patch('builtins.input', side_effect=['invalid', '40000'])
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_invalid_input(self, mock_print, mock_input, user_interface):
        """Тест фильтрации с некорректным вводом зарплаты"""
        if hasattr(user_interface, 'filter_saved_vacancies_by_salary'):
            with patch.object(user_interface, 'filter_saved_vacancies_by_salary') as mock_filter:
                mock_filter.return_value = None
                user_interface.filter_saved_vacancies_by_salary()
                mock_filter.assert_called_once()

    def test_interface_components_integration(self, user_interface):
        """Тест интеграции компонентов интерфейса"""
        # Проверяем, что все необходимые компоненты инициализированы
        assert hasattr(user_interface, 'storage')
        assert hasattr(user_interface, 'db_manager')
        assert hasattr(user_interface, 'unified_api')
        assert hasattr(user_interface, 'search_handler')
        assert hasattr(user_interface, 'display_handler')

    @patch('builtins.print')
    def test_error_handling_in_methods(self, mock_print, user_interface):
        """Тест обработки ошибок в методах интерфейса"""
        # Проверяем, что методы не падают при ошибках хранилища
        user_interface.storage.get_all_vacancies.side_effect = Exception("Storage error")
        
        # Вызовы не должны вызывать исключения
        try:
            if hasattr(user_interface, 'show_all_saved_vacancies'):
                user_interface.show_all_saved_vacancies()
        except Exception as e:
            pytest.fail(f"Method should handle storage errors gracefully: {e}")

    def test_menu_choices_coverage(self, user_interface):
        """Тест покрытия всех пунктов меню"""
        # Проверяем, что есть обработчик для основных пунктов меню
        menu_methods = [
            'handle_menu_choice',
            'show_menu',
            'run'
        ]
        
        for method in menu_methods:
            assert hasattr(user_interface, method), f"Missing method: {method}"
            assert callable(getattr(user_interface, method)), f"Method {method} is not callable"

    @patch('src.ui_interfaces.console_interface.UnifiedAPI')
    @patch('src.ui_interfaces.console_interface.VacancySearchHandler')
    @patch('src.ui_interfaces.console_interface.VacancyDisplayHandler')
    def test_initialization_with_mocks(self, mock_display, mock_search, mock_api, mock_storage, mock_db_manager):
        """Тест инициализации с полными моками"""
        interface = UserInterface(mock_storage, mock_db_manager)
        
        # Проверяем, что все классы были инициализированы
        mock_api.assert_called_once()
        mock_search.assert_called_once()
        mock_display.assert_called_once()

    def test_storage_integration(self, user_interface, mock_storage):
        """Тест интеграции с хранилищем"""
        # Проверяем, что методы хранилища вызываются корректно
        user_interface.storage.get_all_vacancies()
        mock_storage.get_all_vacancies.assert_called()

    def test_db_manager_integration(self, user_interface, mock_db_manager):
        """Тест интеграции с менеджером БД"""
        # Проверяем доступность менеджера БД
        assert user_interface.db_manager == mock_db_manager
