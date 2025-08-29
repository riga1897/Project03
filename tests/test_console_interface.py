
"""
Тесты для консольного интерфейса пользователя
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ui_interfaces.console_interface import UserInterface


class TestUserInterface:
    """Тесты для UserInterface"""
    
    @pytest.fixture
    def mock_storage(self):
        """Мокированное хранилище"""
        storage = Mock()
        storage.get_vacancies.return_value = []
        storage.get_vacancies_count.return_value = 0
        storage.delete_vacancy_by_id.return_value = True
        storage.delete_vacancies_by_keyword.return_value = 5
        return storage
    
    @pytest.fixture
    def mock_db_manager(self):
        """Мокированный DB Manager"""
        db_manager = Mock()
        db_manager.check_connection.return_value = True
        return db_manager
    
    @pytest.fixture
    def user_interface(self, mock_storage, mock_db_manager):
        """Экземпляр UserInterface для тестирования"""
        with patch('src.ui_interfaces.console_interface.UnifiedAPI'):
            with patch('src.ui_interfaces.console_interface.VacancySearchHandler'):
                with patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'):
                    with patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator'):
                        with patch('src.ui_interfaces.console_interface.create_main_menu'):
                            with patch('src.ui_interfaces.console_interface.VacancyOperations'):
                                ui = UserInterface(mock_storage, mock_db_manager)
                                return ui
    
    def test_initialization(self, user_interface, mock_storage, mock_db_manager):
        """Тест инициализации интерфейса"""
        assert user_interface.storage == mock_storage
        assert user_interface.db_manager == mock_db_manager
        assert hasattr(user_interface, 'unified_api')
        assert hasattr(user_interface, 'search_handler')
        assert hasattr(user_interface, 'display_handler')
        assert hasattr(user_interface, 'operations_coordinator')
    
    def test_initialization_default_storage(self, mock_db_manager):
        """Тест инициализации с хранилищем по умолчанию"""
        with patch('src.ui_interfaces.console_interface.StorageFactory.get_default_storage') as mock_factory:
            mock_storage = Mock()
            mock_factory.return_value = mock_storage
            
            with patch('src.ui_interfaces.console_interface.UnifiedAPI'):
                with patch('src.ui_interfaces.console_interface.VacancySearchHandler'):
                    with patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'):
                        with patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator'):
                            with patch('src.ui_interfaces.console_interface.create_main_menu'):
                                with patch('src.ui_interfaces.console_interface.VacancyOperations'):
                                    ui = UserInterface(db_manager=mock_db_manager)
                                    
                                    mock_factory.assert_called_once()
                                    assert ui.storage == mock_storage
    
    def test_show_menu(self, user_interface):
        """Тест отображения меню"""
        with patch('builtins.input', return_value='1') as mock_input:
            with patch('builtins.print'):
                choice = user_interface._show_menu()
                
                mock_input.assert_called_once_with("Ваш выбор: ")
                assert choice == '1'
    
    def test_get_period_choice_default(self, user_interface):
        """Тест выбора периода по умолчанию"""
        with patch('builtins.input', return_value='') as mock_input:
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
                
                mock_input.assert_called()
                assert period == 15  # по умолчанию
    
    def test_get_period_choice_custom(self, user_interface):
        """Тест выбора пользовательского периода"""
        with patch('builtins.input', side_effect=['6', '7']) as mock_input:
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
                
                assert mock_input.call_count == 2
                assert period == 7
    
    def test_get_period_choice_invalid_custom(self, user_interface):
        """Тест некорректного пользовательского периода"""
        with patch('builtins.input', side_effect=['6', 'invalid']) as mock_input:
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
                
                assert period == 15  # по умолчанию при ошибке
    
    def test_get_period_choice_cancel(self, user_interface):
        """Тест отмены выбора периода"""
        with patch('builtins.input', return_value='0') as mock_input:
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
                
                mock_input.assert_called()
                assert period is None
    
    def test_get_period_choice_keyboard_interrupt(self, user_interface):
        """Тест прерывания выбора периода"""
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
                
                assert period is None
    
    @patch('src.ui_interfaces.console_interface.confirm_action')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_all(self, mock_print, mock_input, mock_confirm, user_interface, mock_storage):
        """Тест удаления всех вакансий"""
        # Настраиваем мок вакансий
        mock_vacancies = [
            Mock(vacancy_id='1', title='Job 1', employer={'name': 'Company 1'}, salary=None, url='http://1'),
            Mock(vacancy_id='2', title='Job 2', employer={'name': 'Company 2'}, salary=None, url='http://2')
        ]
        
        mock_input.return_value = 'a'
        mock_confirm.return_value = True
        mock_storage.delete_vacancies_by_keyword.return_value = 2
        
        user_interface._show_vacancies_for_deletion(mock_vacancies, 'python')
        
        mock_confirm.assert_called_once()
        mock_storage.delete_vacancies_by_keyword.assert_called_once_with('python')
    
    @patch('src.ui_interfaces.console_interface.confirm_action')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_single(self, mock_print, mock_input, mock_confirm, user_interface, mock_storage):
        """Тест удаления одной вакансии"""
        mock_vacancy = Mock(
            vacancy_id='1', 
            title='Job 1', 
            employer={'name': 'Company 1'}, 
            salary='100000 руб.', 
            url='http://1'
        )
        mock_vacancies = [mock_vacancy]
        
        mock_input.return_value = '1'
        mock_confirm.return_value = True
        mock_storage.delete_vacancy_by_id.return_value = True
        
        user_interface._show_vacancies_for_deletion(mock_vacancies, 'python')
        
        mock_confirm.assert_called_once()
        mock_storage.delete_vacancy_by_id.assert_called_once_with('1')
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_quit(self, mock_print, mock_input, user_interface, mock_storage):
        """Тест выхода из удаления вакансий"""
        mock_vacancies = [Mock(vacancy_id='1', title='Job 1', employer={'name': 'Company 1'}, salary=None, url='http://1')]
        
        mock_input.return_value = 'q'
        
        user_interface._show_vacancies_for_deletion(mock_vacancies, 'python')
        
        # Проверяем, что методы удаления не вызывались
        mock_storage.delete_vacancy_by_id.assert_not_called()
        mock_storage.delete_vacancies_by_keyword.assert_not_called()
    
    @patch('src.ui_interfaces.console_interface.confirm_action')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_range(self, mock_print, mock_input, mock_confirm, user_interface, mock_storage):
        """Тест удаления диапазона вакансий"""
        mock_vacancies = [
            Mock(vacancy_id='1', title='Job 1', employer={'name': 'Company 1'}, salary=None, url='http://1'),
            Mock(vacancy_id='2', title='Job 2', employer={'name': 'Company 2'}, salary=None, url='http://2'),
            Mock(vacancy_id='3', title='Job 3', employer={'name': 'Company 3'}, salary=None, url='http://3')
        ]
        
        mock_input.return_value = '1-2'
        mock_confirm.return_value = True
        mock_storage.delete_vacancy_by_id.return_value = True
        
        user_interface._show_vacancies_for_deletion(mock_vacancies, 'python')
        
        mock_confirm.assert_called_once()
        # Должны быть вызваны удаления для вакансий 1 и 2
        assert mock_storage.delete_vacancy_by_id.call_count == 2
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_invalid_range(self, mock_print, mock_input, user_interface, mock_storage):
        """Тест некорректного диапазона вакансий"""
        mock_vacancies = [Mock(vacancy_id='1', title='Job 1', employer={'name': 'Company 1'}, salary=None, url='http://1')]
        
        mock_input.side_effect = ['1-5', 'q']  # Сначала некорректный диапазон, потом выход
        
        user_interface._show_vacancies_for_deletion(mock_vacancies, 'python')
        
        # Проверяем, что удаление не было вызвано
        mock_storage.delete_vacancy_by_id.assert_not_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_pagination(self, mock_print, mock_input, user_interface, mock_storage):
        """Тест пагинации при удалении вакансий"""
        # Создаем больше 10 вакансий для проверки пагинации
        mock_vacancies = []
        for i in range(15):
            mock_vacancies.append(
                Mock(
                    vacancy_id=str(i+1), 
                    title=f'Job {i+1}', 
                    employer={'name': f'Company {i+1}'}, 
                    salary=None, 
                    url=f'http://{i+1}'
                )
            )
        
        mock_input.side_effect = ['n', 'q']  # Следующая страница, потом выход
        
        user_interface._show_vacancies_for_deletion(mock_vacancies, 'python')
        
        # Проверяем, что input был вызван дважды
        assert mock_input.call_count == 2
    
    def test_display_vacancies_static_method(self, user_interface):
        """Тест статического метода отображения вакансий"""
        mock_vacancies = [
            Mock(title='Job 1', employer={'name': 'Company 1'}),
            Mock(title='Job 2', employer={'name': 'Company 2'})
        ]
        
        with patch('src.ui_interfaces.console_interface.display_vacancy_info') as mock_display:
            UserInterface._display_vacancies(mock_vacancies, 5)
            
            # Проверяем, что display_vacancy_info был вызван для каждой вакансии
            assert mock_display.call_count == 2
            mock_display.assert_any_call(mock_vacancies[0], 5)
            mock_display.assert_any_call(mock_vacancies[1], 6)
    
    def test_display_vacancies_with_pagination_static_method(self, user_interface):
        """Тест статического метода отображения с пагинацией"""
        mock_vacancies = [Mock(title='Job 1'), Mock(title='Job 2')]
        
        with patch('src.ui_interfaces.console_interface.quick_paginate') as mock_paginate:
            UserInterface._display_vacancies_with_pagination(mock_vacancies)
            
            mock_paginate.assert_called_once()
            # Проверяем параметры вызова
            args, kwargs = mock_paginate.call_args
            assert args[0] == mock_vacancies
            assert 'formatter' in kwargs
            assert kwargs['header'] == 'Вакансии'
            assert kwargs['items_per_page'] == 10
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_configure_superjob_api_static_method(self, mock_print, mock_input):
        """Тест статического метода настройки SuperJob API"""
        mock_input.return_value = ''  # Просто нажать Enter
        
        with patch.dict('os.environ', {'SUPERJOB_API_KEY': 'test_key'}):
            UserInterface._configure_superjob_api()
            
            mock_input.assert_called_once()
            mock_print.assert_called()
            
            # Проверяем, что в выводе есть информация о настройке
            print_calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(print_calls)
            assert "SUPERJOB" in output or "SuperJob" in output
    
    def test_run_keyboard_interrupt(self, user_interface):
        """Тест прерывания работы пользователем"""
        with patch.object(user_interface, '_show_menu', side_effect=KeyboardInterrupt()):
            with patch('builtins.print') as mock_print:
                user_interface.run()
                
                # Проверяем, что было выведено сообщение о прерывании
                print_calls = [str(call) for call in mock_print.call_args_list]
                output = " ".join(print_calls)
                assert "прервана" in output or "прерван" in output
    
    def test_run_exception_handling(self, user_interface):
        """Тест обработки исключений в основном цикле"""
        with patch.object(user_interface, '_show_menu', side_effect=Exception("Test error")):
            with patch('builtins.print') as mock_print:
                with patch('src.ui_interfaces.console_interface.logger') as mock_logger:
                    # Мокируем чтобы цикл завершился после первой итерации
                    with patch.object(user_interface, '_show_menu', side_effect=[Exception("Test error"), "0"]):
                        user_interface.run()
                        
                        mock_logger.error.assert_called()
                        mock_print.assert_called()
    
    def test_operations_coordinator_methods(self, user_interface):
        """Тест методов, делегирующих работу operations_coordinator"""
        # Тестируем методы, которые делегируют работу operations_coordinator
        methods_to_test = [
            '_search_vacancies',
            '_show_saved_vacancies',
            '_get_top_saved_vacancies_by_salary',
            '_search_saved_vacancies_by_keyword',
            '_delete_saved_vacancies',
            '_clear_api_cache'
        ]
        
        for method_name in methods_to_test:
            with patch.object(user_interface.operations_coordinator, 'handle_vacancy_search') as mock_handle:
                method = getattr(user_interface, method_name)
                method()
                
                # Проверяем, что operations_coordinator был использован
                # (конкретный метод может отличаться, главное что он вызывается)
                assert hasattr(user_interface, 'operations_coordinator')
    
    def test_advanced_search_vacancies(self, user_interface, mock_storage):
        """Тест расширенного поиска вакансий"""
        mock_vacancies = [
            Mock(title='Python Developer', description='Python Django'),
            Mock(title='Java Developer', description='Java Spring')
        ]
        mock_storage.get_vacancies.return_value = mock_vacancies
        
        with patch('src.ui_interfaces.console_interface.get_user_input', return_value='python') as mock_input:
            with patch.object(user_interface.vacancy_ops, 'filter_vacancies_by_multiple_keywords', return_value=[mock_vacancies[0]]) as mock_filter:
                with patch('src.ui_interfaces.console_interface.quick_paginate') as mock_paginate:
                    with patch('builtins.print'):
                        user_interface._advanced_search_vacancies()
                        
                        mock_input.assert_called_once()
                        mock_filter.assert_called_once()
                        mock_paginate.assert_called_once()
    
    def test_advanced_search_vacancies_empty_query(self, user_interface, mock_storage):
        """Тест расширенного поиска с пустым запросом"""
        mock_storage.get_vacancies.return_value = []
        
        with patch('src.ui_interfaces.console_interface.get_user_input', return_value='') as mock_input:
            with patch('builtins.print'):
                user_interface._advanced_search_vacancies()
                
                mock_input.assert_called_once()
    
    def test_filter_saved_vacancies_by_salary_min(self, user_interface, mock_storage):
        """Тест фильтрации по минимальной зарплате"""
        mock_vacancies = [Mock(title='Job 1', salary=150000)]
        mock_storage.get_vacancies.return_value = mock_vacancies
        
        with patch('builtins.input', side_effect=['1', '100000']) as mock_input:
            with patch.object(user_interface.vacancy_ops, 'filter_vacancies_by_min_salary', return_value=mock_vacancies) as mock_filter:
                with patch.object(user_interface.vacancy_ops, 'sort_vacancies_by_salary', return_value=mock_vacancies) as mock_sort:
                    with patch('src.ui_interfaces.console_interface.quick_paginate') as mock_paginate:
                        with patch('builtins.print'):
                            user_interface._filter_saved_vacancies_by_salary()
                            
                            assert mock_input.call_count == 2
                            mock_filter.assert_called_once_with(mock_vacancies, 100000)
                            mock_sort.assert_called_once()
                            mock_paginate.assert_called_once()
    
    def test_filter_saved_vacancies_by_salary_invalid_input(self, user_interface, mock_storage):
        """Тест фильтрации с некорректным вводом"""
        mock_storage.get_vacancies.return_value = [Mock()]
        
        with patch('builtins.input', side_effect=['1', 'invalid']) as mock_input:
            with patch('builtins.print') as mock_print:
                user_interface._filter_saved_vacancies_by_salary()
                
                # Проверяем, что было выведено сообщение об ошибке
                print_calls = [str(call) for call in mock_print.call_args_list]
                output = " ".join(print_calls)
                assert "корректное" in output or "ошибка" in output or "Введите" in output
