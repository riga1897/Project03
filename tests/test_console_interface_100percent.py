#!/usr/bin/env python3
"""
Финальные тесты для достижения 100% покрытия console_interface.py

УПРОЩЕННЫЙ ПОДХОД: Покрываем только критические непокрытые строки без зависания
Цель: Довести покрытие с 58% до максимально возможного процента
"""

from unittest.mock import MagicMock, patch
import pytest
from src.ui_interfaces.console_interface import UserInterface


class TestConsoleInterface100Percent:
    """Упрощенные тесты для максимального покрытия"""
    
    def test_init_with_db_manager_creates_demo(self):
        """Покрытие строк 68-71: создание demo при наличии db_manager"""
        mock_db = MagicMock()
        
        with patch('src.storage.storage_factory.StorageFactory') as mock_sf:
            with patch('src.api_modules.unified_api.UnifiedAPI'):
                with patch('src.utils.menu_manager.create_main_menu'):
                    with patch('src.utils.vacancy_operations.VacancyOperations'):
                        with patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler'):
                            with patch('src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyOperationsCoordinator'):
                                    with patch('src.ui_interfaces.console_interface.DBManagerDemo') as mock_demo:
                                        mock_sf.get_default_storage.return_value = MagicMock()
                                        mock_demo.return_value = MagicMock()
                                        
                                        ui = UserInterface(db_manager=mock_db)
                                        
                                        # Покрываем строки создания demo
                                        assert ui.db_manager == mock_db
                                        assert ui.demo is not None
    
    @patch('src.ui_interfaces.console_interface.DBManager', None)
    @patch('src.ui_interfaces.console_interface.DBManagerDemo', None)  
    def test_init_without_db_imports(self):
        """Покрытие строк 23-25: когда DBManager не импортируется"""
        with patch('src.storage.storage_factory.StorageFactory') as mock_sf:
            with patch('src.api_modules.unified_api.UnifiedAPI'):
                with patch('src.utils.menu_manager.create_main_menu'):
                    with patch('src.utils.vacancy_operations.VacancyOperations'):
                        with patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler'):
                            with patch('src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    
                                    ui = UserInterface()
                                    
                                    # Покрываем except блок импорта
                                    assert ui.db_manager is None
                                    assert ui.demo is None
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['10', '0'])  # DB demo choice, затем выход
    @patch('builtins.print')
    def test_dbmanager_demo_branch(self, mock_print, mock_input, mock_header):
        """Покрытие строк 103-107: запуск DB Manager demo"""
        ui = self._create_ui()
        ui.db_manager = MagicMock()  
        ui.demo = MagicMock()
        
        ui.run()
        
        # Покрываем ветку демонстрации DBManager
        ui.demo.run_full_demo.assert_called_once()
        mock_print.assert_any_call("ДЕМОНСТРАЦИЯ DBMANAGER")
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('src.ui_interfaces.console_interface.logger')
    @patch('time.sleep', return_value=None)
    @patch('builtins.print')
    def test_run_exception_handler(self, mock_print, mock_sleep, mock_logger, mock_header):
        """Покрытие строк 121-127: exception handler в run()"""
        ui = self._create_ui()
        
        # Мокируем _show_menu чтобы сначала генерировать исключение, потом выйти
        ui._show_menu = MagicMock(side_effect=[Exception("Test error"), "0"])
        
        ui.run()
        
        # Покрываем exception handling
        mock_logger.error.assert_called()
        mock_print.assert_any_call("Произошла ошибка: Test error")
        mock_sleep.assert_called_with(0.1)
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="test AND keyword")
    @patch('src.ui_interfaces.console_interface.quick_paginate') 
    @patch('src.ui_interfaces.console_interface.VacancyFormatter')
    @patch('builtins.print')
    def test_advanced_search_and_operator(self, mock_print, mock_formatter, mock_paginate, mock_input):
        """Покрытие строк 202-203: advanced search с AND"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        ui.vacancy_ops.search_vacancies_advanced = MagicMock(return_value=[MagicMock()])
        
        ui._advanced_search_vacancies()
        
        # Основная цель - покрытие кода, проверяем что поиск был выполнен
        ui.vacancy_ops.search_vacancies_advanced.assert_called_once()
        assert mock_paginate.called
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="nosuchkeyword")
    @patch('builtins.print')
    def test_advanced_search_no_results(self, mock_print, mock_input):
        """Покрытие строк 206-207: нет результатов поиска"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        ui.vacancy_ops.search_vacancies_advanced = MagicMock(return_value=[])
        
        ui._advanced_search_vacancies()
        
        mock_print.assert_any_call("Вакансии по указанным критериям не найдены.")
    
    @patch('builtins.print')  
    def test_salary_filter_no_vacancies(self, mock_print):
        """Покрытие строк 233-234: нет сохраненных вакансий"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = []
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Нет сохраненных вакансий.")
    
    @patch('builtins.input', side_effect=['2', 'not_a_number'])
    @patch('builtins.print')
    def test_salary_filter_max_value_error(self, mock_print, mock_input):
        """Покрытие строк 259-261: ValueError в max salary"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Введите корректное число!")
    
    @patch('builtins.input', side_effect=['3', ''])
    @patch('src.ui_interfaces.console_interface.parse_salary_range', return_value=None)
    def test_salary_filter_range_parse_fail(self, mock_parse, mock_input):
        """Покрытие строки 273: return при неудачном parse"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        
        ui._filter_saved_vacancies_by_salary()
        
        # Покрываем return при неудачном парсинге
        mock_parse.assert_called_once()
    
    @patch('builtins.input', side_effect=['1', '999999'])
    @patch('builtins.print')
    def test_salary_filter_no_matching_results(self, mock_print, mock_input):
        """Покрытие строк 280-281: нет подходящих вакансий"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        ui.vacancy_ops.filter_vacancies_by_min_salary = MagicMock(return_value=[])
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Вакансии с указанными критериями зарплаты не найдены.")
    
    @patch('builtins.input', side_effect=['6', '0'])  # Неверный период -> 0 дней
    @patch('builtins.print')
    def test_period_choice_out_of_range(self, mock_print, mock_input):
        """Покрытие строк 344-348: период вне диапазона"""
        result = UserInterface._get_period_choice()
        
        assert result == 15
        mock_print.assert_any_call("Некорректный период. Используется 15 дней по умолчанию.")
    
    @patch('builtins.input', side_effect=['6', 'abc'])
    @patch('builtins.print') 
    def test_period_choice_value_error(self, mock_print, mock_input):
        """Покрытие строк 346-348: ValueError при вводе"""
        result = UserInterface._get_period_choice()
        
        assert result == 15
        mock_print.assert_any_call("Некорректный ввод. Используется 15 дней по умолчанию.")
    
    @patch('builtins.input', return_value='invalid_choice')
    @patch('builtins.print')
    def test_period_choice_else_branch(self, mock_print, mock_input):
        """Покрытие строк 350-351: else ветка"""
        result = UserInterface._get_period_choice()
        
        assert result == 15
        mock_print.assert_any_call("Некорректный выбор. Используется 15 дней по умолчанию.")
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_period_choice_keyboard_interrupt(self, mock_print, mock_input):
        """Покрытие строк 353-355: KeyboardInterrupt"""
        result = UserInterface._get_period_choice()
        
        assert result is None
        mock_print.assert_any_call("\nВыбор периода отменен.")
    
    def _create_ui(self):
        """Создает UI с замоканными зависимостями"""
        with patch('src.storage.storage_factory.StorageFactory') as mock_sf:
            with patch('src.api_modules.unified_api.UnifiedAPI'):
                with patch('src.utils.menu_manager.create_main_menu'):
                    with patch('src.utils.vacancy_operations.VacancyOperations'):
                        with patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler'):
                            with patch('src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    return UserInterface()


class TestConsoleInterfaceMenuChoices:
    """Простые тесты для покрытия всех menu choices (строки 82-100)"""
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['1', '0'])
    def test_menu_choice_1(self, mock_input, mock_header):
        """Покрытие строки 82"""
        ui = self._create_ui()
        ui.run()
        ui.operations_coordinator.handle_vacancy_search.assert_called_once()
    
    @patch('src.ui_interfaces.console_interface.print_section_header') 
    @patch('builtins.input', side_effect=['2', '0'])
    def test_menu_choice_2(self, mock_input, mock_header):
        """Покрытие строки 84"""
        ui = self._create_ui()
        ui.run()
        ui.operations_coordinator.handle_show_saved_vacancies.assert_called_once()
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['3', '0'])
    def test_menu_choice_3(self, mock_input, mock_header):
        """Покрытие строки 86"""  
        ui = self._create_ui()
        ui.run()
        ui.operations_coordinator.handle_top_vacancies_by_salary.assert_called_once()
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['4', '0'])
    def test_menu_choice_4(self, mock_input, mock_header):
        """Покрытие строки 88"""
        ui = self._create_ui()
        ui.run()
        ui.operations_coordinator.handle_search_saved_by_keyword.assert_called_once()
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['7', '0'])  
    def test_menu_choice_7(self, mock_input, mock_header):
        """Покрытие строки 94"""
        ui = self._create_ui()
        ui.run()
        ui.operations_coordinator.handle_delete_vacancies.assert_called_once()
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['8', '0'])
    def test_menu_choice_8(self, mock_input, mock_header):
        """Покрытие строки 97"""
        ui = self._create_ui()
        ui.run()
        ui.operations_coordinator.handle_cache_cleanup.assert_called_once()
    
    def _create_ui(self):
        """Создает UI с замоканными зависимостями"""
        with patch('src.storage.storage_factory.StorageFactory') as mock_sf:
            with patch('src.api_modules.unified_api.UnifiedAPI'):
                with patch('src.utils.menu_manager.create_main_menu'):
                    with patch('src.utils.vacancy_operations.VacancyOperations'):
                        with patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler'):
                            with patch('src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    return UserInterface()