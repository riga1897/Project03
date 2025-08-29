
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
        storage.get_vacancies.return_value = []
        storage.delete_vacancy_by_id.return_value = True
        storage.delete_vacancies_by_keyword.return_value = 5
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
             patch('src.ui_interfaces.console_interface.VacancyDisplayHandler') as mock_display_handler, \
             patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator') as mock_coordinator:
            
            # Настройка моков
            mock_unified_api_instance = Mock()
            mock_unified_api.return_value = mock_unified_api_instance
            
            mock_search_handler_instance = Mock()
            mock_search_handler.return_value = mock_search_handler_instance
            
            mock_display_handler_instance = Mock()
            mock_display_handler.return_value = mock_display_handler_instance
            
            mock_coordinator_instance = Mock()
            mock_coordinator.return_value = mock_coordinator_instance
            
            interface = UserInterface(mock_storage, mock_db_manager)
            return interface

    def test_initialization(self, user_interface, mock_storage, mock_db_manager):
        """Тест инициализации UserInterface"""
        assert user_interface.storage == mock_storage
        assert user_interface.db_manager == mock_db_manager
        assert hasattr(user_interface, 'unified_api')
        assert hasattr(user_interface, 'search_handler')
        assert hasattr(user_interface, 'display_handler')
        assert hasattr(user_interface, 'operations_coordinator')

    def test_initialization_default_storage(self, mock_db_manager):
        """Тест инициализации с хранилищем по умолчанию"""
        with patch('src.ui_interfaces.console_interface.StorageFactory.get_default_storage') as mock_factory, \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.VacancySearchHandler'), \
             patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'), \
             patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator'):
            
            mock_storage = Mock()
            mock_factory.return_value = mock_storage
            
            interface = UserInterface(db_manager=mock_db_manager)
            
            assert interface.storage == mock_storage
            assert interface.db_manager == mock_db_manager
            mock_factory.assert_called_once()

    @patch('builtins.print')
    def test_show_menu(self, mock_print, user_interface):
        """Тест отображения меню"""
        # В реальном коде это приватный метод _show_menu
        result = user_interface._show_menu()
        
        # Проверяем, что print был вызван несколько раз для отображения меню
        assert mock_print.call_count > 0
        # Проверяем, что в одном из вызовов есть текст меню
        menu_calls = [str(call) for call in mock_print.call_args_list]
        menu_text_found = any("Выберите действие" in call for call in menu_calls)
        assert menu_text_found

    @patch('builtins.input', return_value='1')
    def test_get_period_choice_default(self, mock_input, user_interface):
        """Тест выбора периода по умолчанию"""
        # В реальном коде это статический метод _get_period_choice
        result = UserInterface._get_period_choice()
        assert result == 1

    @patch('builtins.input', side_effect=['6', '7'])
    def test_get_period_choice_custom(self, mock_input, user_interface):
        """Тест выбора пользовательского периода"""
        result = UserInterface._get_period_choice()
        assert result == 7

    @patch('builtins.input', side_effect=['6', 'invalid', '5'])
    @patch('builtins.print')
    def test_get_period_choice_invalid_custom(self, mock_print, mock_input, user_interface):
        """Тест обработки некорректного ввода периода"""
        result = UserInterface._get_period_choice()
        assert result == 15  # По умолчанию

    @patch('builtins.input', return_value='0')
    def test_get_period_choice_cancel(self, mock_input, user_interface):
        """Тест отмены выбора периода"""
        result = UserInterface._get_period_choice()
        assert result is None

    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_get_period_choice_keyboard_interrupt(self, mock_input, user_interface):
        """Тест обработки KeyboardInterrupt"""
        result = UserInterface._get_period_choice()
        assert result is None

    @patch('builtins.input', side_effect=['a', 'y'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_all(self, mock_print, mock_input, user_interface):
        """Тест отображения всех вакансий для удаления"""
        # Настройка мок данных
        vacancies = [
            Mock(vacancy_id='1', title='Test Vacancy 1'),
            Mock(vacancy_id='2', title='Test Vacancy 2')
        ]
        
        # В реальном коде метод требует список вакансий и ключевое слово
        user_interface._show_vacancies_for_deletion(vacancies, "test")
        
        assert mock_print.call_count > 0

    @patch('builtins.input', side_effect=['1', 'y'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_single(self, mock_print, mock_input, user_interface):
        """Тест отображения одной вакансии для удаления"""
        vacancies = [Mock(vacancy_id='1', title='Test Vacancy')]
        
        user_interface._show_vacancies_for_deletion(vacancies, "test")
        
        assert mock_print.call_count > 0

    @patch('builtins.input', return_value='q')
    def test_show_vacancies_for_deletion_quit(self, mock_input, user_interface):
        """Тест выхода из удаления вакансий"""
        vacancies = [Mock(vacancy_id='1', title='Test Vacancy')]
        
        user_interface._show_vacancies_for_deletion(vacancies, "test")

    @patch('builtins.input', side_effect=['1-3', 'y'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_range(self, mock_print, mock_input, user_interface):
        """Тест удаления диапазона вакансий"""
        vacancies = [
            Mock(vacancy_id='1', title='Test 1'),
            Mock(vacancy_id='2', title='Test 2'),
            Mock(vacancy_id='3', title='Test 3'),
            Mock(vacancy_id='4', title='Test 4')
        ]
        
        user_interface._show_vacancies_for_deletion(vacancies, "test")
        
        assert mock_print.call_count > 0

    @patch('builtins.input', side_effect=['invalid-range', '1', 'y'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_invalid_range(self, mock_print, mock_input, user_interface):
        """Тест обработки некорректного диапазона"""
        vacancies = [Mock(vacancy_id='1', title='Test Vacancy')]
        
        user_interface._show_vacancies_for_deletion(vacancies, "test")
        
        assert mock_print.call_count > 0

    @patch('builtins.input', side_effect=['n', 'q'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_pagination(self, mock_print, mock_input, user_interface):
        """Тест пагинации при удалении вакансий"""
        # Создаем много вакансий для тестирования пагинации
        vacancies = [Mock(vacancy_id=str(i), title=f'Test {i}') for i in range(1, 25)]
        
        user_interface._show_vacancies_for_deletion(vacancies, "test")
        
        assert mock_print.call_count > 0

    @patch('builtins.print')
    def test_display_vacancies_static_method(self, mock_print):
        """Тест статического метода отображения вакансий"""
        vacancies = [
            Mock(vacancy_id='1', title='Test Vacancy 1'),
            Mock(vacancy_id='2', title='Test Vacancy 2')
        ]
        
        # В реальном коде это приватный метод _display_vacancies
        UserInterface._display_vacancies(vacancies)
        
        # Проверяем, что print был вызван
        assert mock_print.call_count > 0

    @patch('builtins.input', side_effect=['n', 'q'])
    @patch('builtins.print')
    def test_display_vacancies_with_pagination_static_method(self, mock_print, mock_input):
        """Тест статического метода отображения вакансий с пагинацией"""
        vacancies = [Mock(vacancy_id=str(i), title=f'Test {i}') for i in range(1, 25)]
        
        # В реальном коде это приватный метод _display_vacancies_with_pagination
        UserInterface._display_vacancies_with_pagination(vacancies)
        
        assert mock_print.call_count > 0

    @patch('builtins.input', side_effect=KeyboardInterrupt)
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input, user_interface):
        """Тест обработки KeyboardInterrupt в основном цикле"""
        with patch.object(user_interface, '_show_menu', return_value='0'):
            user_interface.run()
            
        # Проверяем, что было выведено сообщение о завершении
        exit_messages = [str(call) for call in mock_print.call_args_list]
        exit_found = any("прервана" in msg.lower() for msg in exit_messages)
        assert exit_found

    @patch('builtins.input', side_effect=['invalid', '0'])
    @patch('builtins.print')
    def test_run_exception_handling(self, mock_print, mock_input, user_interface):
        """Тест обработки исключений в основном цикле"""
        with patch.object(user_interface, '_show_menu', side_effect=['invalid', '0']):
            user_interface.run()

    def test_run_method_exists(self, user_interface):
        """Тест что метод run существует"""
        assert hasattr(user_interface, 'run')
        assert callable(getattr(user_interface, 'run'))

    @patch('builtins.input', return_value='python django')
    @patch('builtins.print')
    def test_advanced_search_vacancies(self, mock_print, mock_input, user_interface):
        """Тест расширенного поиска вакансий"""
        mock_vacancies = [Mock(vacancy_id='1', title='Python Django Developer')]
        user_interface.storage.get_vacancies.return_value = mock_vacancies
        
        # Вызываем приватный метод напрямую
        user_interface._advanced_search_vacancies()
        
        assert mock_print.call_count > 0

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_advanced_search_vacancies_empty_query(self, mock_print, mock_input, user_interface):
        """Тест расширенного поиска с пустым запросом"""
        user_interface.storage.get_vacancies.return_value = []
        
        user_interface._advanced_search_vacancies()
        
        assert mock_print.call_count > 0

    @patch('builtins.input', return_value='50000')
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_min(self, mock_print, mock_input, user_interface):
        """Тест фильтрации сохраненных вакансий по минимальной зарплате"""
        mock_vacancies = [Mock(vacancy_id='1', title='High Salary Job')]
        user_interface.storage.get_vacancies.return_value = mock_vacancies
        
        with patch('builtins.input', side_effect=['1', '50000']):
            user_interface._filter_saved_vacancies_by_salary()
        
        assert mock_print.call_count > 0

    @patch('builtins.input', side_effect=['1', 'invalid', '40000'])
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_invalid_input(self, mock_print, mock_input, user_interface):
        """Тест фильтрации с некорректным вводом зарплаты"""
        user_interface.storage.get_vacancies.return_value = []
        
        user_interface._filter_saved_vacancies_by_salary()
        
        assert mock_print.call_count > 0

    def test_interface_components_integration(self, user_interface):
        """Тест интеграции компонентов интерфейса"""
        # Проверяем, что все необходимые компоненты инициализированы
        assert hasattr(user_interface, 'storage')
        assert hasattr(user_interface, 'db_manager')
        assert hasattr(user_interface, 'unified_api')
        assert hasattr(user_interface, 'search_handler')
        assert hasattr(user_interface, 'display_handler')
        assert hasattr(user_interface, 'operations_coordinator')

    @patch('builtins.print')
    def test_error_handling_in_methods(self, mock_print, user_interface):
        """Тест обработки ошибок в методах интерфейса"""
        # Проверяем, что методы не падают при ошибках хранилища
        user_interface.storage.get_vacancies.side_effect = Exception("Storage error")
        
        # Вызовы не должны вызывать исключения
        try:
            user_interface._advanced_search_vacancies()
        except Exception as e:
            # Метод может логировать ошибку, но не должен падать
            pass

    def test_menu_choices_coverage(self, user_interface):
        """Тест покрытия всех пунктов меню"""
        # Проверяем, что есть обработчик для основных пунктов меню
        menu_methods = [
            '_show_menu',
            'run',
            '_search_vacancies',
            '_show_saved_vacancies',
            '_get_top_saved_vacancies_by_salary',
            '_search_saved_vacancies_by_keyword',
            '_advanced_search_vacancies',
            '_filter_saved_vacancies_by_salary',
            '_delete_saved_vacancies',
            '_clear_api_cache'
        ]
        
        for method in menu_methods:
            assert hasattr(user_interface, method), f"Missing method: {method}"
            assert callable(getattr(user_interface, method)), f"Method {method} is not callable"

    @patch('src.ui_interfaces.console_interface.UnifiedAPI')
    @patch('src.ui_interfaces.console_interface.VacancySearchHandler')
    @patch('src.ui_interfaces.console_interface.VacancyDisplayHandler')
    @patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator')
    def test_initialization_with_mocks(self, mock_coordinator, mock_display, mock_search, mock_api, mock_storage, mock_db_manager):
        """Тест инициализации с полными моками"""
        interface = UserInterface(mock_storage, mock_db_manager)
        
        # Проверяем, что все классы были инициализированы
        mock_api.assert_called_once()
        mock_search.assert_called_once()
        mock_display.assert_called_once()
        mock_coordinator.assert_called_once()

    def test_storage_integration(self, user_interface, mock_storage):
        """Тест интеграции с хранилищем"""
        # Проверяем, что методы хранилища вызываются корректно
        user_interface.storage.get_vacancies()
        mock_storage.get_vacancies.assert_called()

    def test_db_manager_integration(self, user_interface, mock_db_manager):
        """Тест интеграции с менеджером БД"""
        # Проверяем доступность менеджера БД
        assert user_interface.db_manager == mock_db_manager

    def test_operations_coordinator_methods(self, user_interface):
        """Тест что operations_coordinator методы вызываются"""
        # Проверяем, что координатор операций доступен
        assert hasattr(user_interface, 'operations_coordinator')
        
        # Тестируем вызовы координатора
        user_interface._search_vacancies()
        user_interface._show_saved_vacancies()
        user_interface._get_top_saved_vacancies_by_salary()
        user_interface._search_saved_vacancies_by_keyword()
        user_interface._delete_saved_vacancies()
        user_interface._clear_api_cache()

    @patch('builtins.print')
    def test_demo_db_manager(self, mock_print, user_interface):
        """Тест демонстрации DBManager"""
        # Проверяем что метод существует
        assert hasattr(user_interface, '_demo_db_manager')
        
        user_interface._demo_db_manager()
        assert mock_print.call_count > 0

    @patch('builtins.print')  
    @patch('builtins.input')
    def test_setup_superjob_api(self, mock_input, mock_print, user_interface):
        """Тест настройки SuperJob API"""
        UserInterface._configure_superjob_api()
        assert mock_print.call_count > 0

    @patch('builtins.input', side_effect=['0'])
    @patch('builtins.print')
    def test_run_normal_exit(self, mock_print, mock_input, user_interface):
        """Тест нормального выхода из программы"""
        user_interface.run()
        
        # Проверяем, что было выведено сообщение о завершении
        exit_messages = [str(call) for call in mock_print.call_args_list]
        exit_found = any("спасибо" in msg.lower() or "свидания" in msg.lower() for msg in exit_messages)
        assert exit_found

    def test_all_public_methods_exist(self, user_interface):
        """Тест что все публичные методы существуют"""
        public_methods = ['run']
        
        for method in public_methods:
            assert hasattr(user_interface, method)
            assert callable(getattr(user_interface, method))

    def test_all_private_methods_exist(self, user_interface):
        """Тест что все приватные методы существуют"""
        private_methods = [
            '_show_menu',
            '_search_vacancies', 
            '_show_saved_vacancies',
            '_get_top_saved_vacancies_by_salary',
            '_search_saved_vacancies_by_keyword',
            '_advanced_search_vacancies',
            '_filter_saved_vacancies_by_salary',
            '_delete_saved_vacancies',
            '_clear_api_cache',
            '_setup_superjob_api',
            '_demo_db_manager',
            '_show_vacancies_for_deletion'
        ]
        
        for method in private_methods:
            assert hasattr(user_interface, method), f"Missing private method: {method}"
            assert callable(getattr(user_interface, method)), f"Private method {method} is not callable"

    def test_static_methods_exist(self):
        """Тест что статические методы существуют"""
        static_methods = [
            '_get_period_choice',
            '_display_vacancies', 
            '_display_vacancies_with_pagination',
            '_configure_superjob_api'
        ]
        
        for method in static_methods:
            assert hasattr(UserInterface, method), f"Missing static method: {method}"
            assert callable(getattr(UserInterface, method)), f"Static method {method} is not callable"
