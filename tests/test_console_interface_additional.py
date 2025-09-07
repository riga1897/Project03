#!/usr/bin/env python3
"""
Дополнительные тесты для повышения покрытия console_interface.py до максимума

Покрывает оставшиеся сложные сценарии и edge cases для достижения 90%+ покрытия.
Фокус на покрытии условных блоков, exception handling и сложных методов.
"""

from unittest.mock import MagicMock, patch
import pytest
from src.ui_interfaces.console_interface import UserInterface


class TestUserInterfaceComplexScenarios:
    """Сложные сценарии для максимального покрытия"""
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['3', '4', '5', '6', '7', '8', '9', '0'])
    @patch('builtins.print')
    def test_run_all_menu_choices(self, mock_print, mock_input, mock_header):
        """Тест всех пунктов меню для максимального покрытия"""
        ui = self._create_ui()
        
        ui.run()
        
        # Проверяем что все обработчики были вызваны
        ui.operations_coordinator.handle_top_vacancies_by_salary.assert_called_once()
        ui.operations_coordinator.handle_search_saved_by_keyword.assert_called_once()
        ui.operations_coordinator.handle_delete_vacancies.assert_called_once()
        ui.operations_coordinator.handle_cache_cleanup.assert_called_once()
        ui.operations_coordinator.handle_superjob_setup.assert_called()
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['10', '0'])  # DB demo с доступным db_manager
    @patch('builtins.print')
    def test_run_db_manager_demo_available(self, mock_print, mock_input, mock_header):
        """Тест DBManager demo когда доступен"""
        ui = self._create_ui()
        # Устанавливаем db_manager и demo
        ui.db_manager = MagicMock()
        ui.demo = MagicMock()
        
        ui.run()
        
        ui.demo.run_full_demo.assert_called_once()
        mock_print.assert_any_call("ДЕМОНСТРАЦИЯ DBMANAGER")
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="python AND django")
    @patch('src.ui_interfaces.console_interface.quick_paginate')
    @patch('src.ui_interfaces.console_interface.VacancyFormatter')
    @patch('builtins.print')
    def test_advanced_search_with_and_operator(self, mock_print, mock_formatter, 
                                              mock_paginate, mock_input):
        """Тест расширенного поиска с AND оператором"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        ui.vacancy_ops.search_vacancies_advanced.return_value = [MagicMock()]
        
        ui._advanced_search_vacancies()
        
        # Проверяем что был вызван advanced search (не multiple keywords)
        ui.vacancy_ops.search_vacancies_advanced.assert_called_once()
        mock_print.assert_any_call("Результаты поиска по запросу: 'python AND django'")
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="python OR java")
    @patch('builtins.print')
    def test_advanced_search_no_results(self, mock_print, mock_input):
        """Тест расширенного поиска без результатов"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        ui.vacancy_ops.search_vacancies_advanced.return_value = []  # Нет результатов
        
        ui._advanced_search_vacancies()
        
        mock_print.assert_any_call("Вакансии по указанным критериям не найдены.")
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="test")
    @patch('src.ui_interfaces.console_interface.logger')
    @patch('builtins.print')
    def test_advanced_search_exception_handling(self, mock_print, mock_logger, mock_input):
        """Тест обработки исключений в advanced search"""
        ui = self._create_ui()
        ui.storage.get_vacancies.side_effect = Exception("Test error")
        
        ui._advanced_search_vacancies()
        
        mock_logger.error.assert_called_once()
        mock_print.assert_any_call("Ошибка при поиске: Test error")
    
    @patch('builtins.input', side_effect=['2', '200000'])  # Максимальная зарплата
    @patch('builtins.print')
    def test_filter_salary_maximum_success(self, mock_print, mock_input):
        """Тест фильтрации по максимальной зарплате"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        ui.vacancy_ops.filter_vacancies_by_max_salary.return_value = [MagicMock()]
        ui.vacancy_ops.sort_vacancies_by_salary.return_value = [MagicMock()]
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Вакансии с зарплатой до 200000 руб.:")
        ui.vacancy_ops.filter_vacancies_by_max_salary.assert_called_once_with([mock_input], 200000)
    
    @patch('builtins.input', side_effect=['3', 'invalid range'])  # Неверный диапазон
    @patch('src.ui_interfaces.console_interface.parse_salary_range', return_value=None)
    @patch('builtins.print')
    def test_filter_salary_invalid_range(self, mock_print, mock_parse, mock_input):
        """Тест фильтрации с неверным диапазоном зарплат"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        
        ui._filter_saved_vacancies_by_salary()
        
        # Метод должен завершиться из-за неверного диапазона
        mock_parse.assert_called_once()
    
    @patch('builtins.input', side_effect=['1', 'abc'])  # Некорректный ввод зарплаты
    @patch('builtins.print')
    def test_filter_salary_value_error(self, mock_print, mock_input):
        """Тест обработки ValueError при вводе зарплаты"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Введите корректное число!")
    
    @patch('builtins.input', side_effect=['1', '50000'])
    @patch('builtins.print')
    def test_filter_salary_no_results(self, mock_print, mock_input):
        """Тест фильтрации зарплат без результатов"""
        ui = self._create_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        ui.vacancy_ops.filter_vacancies_by_min_salary.return_value = []  # Нет результатов
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Вакансии с указанными критериями зарплаты не найдены.")
    
    @patch('src.ui_interfaces.console_interface.logger')
    @patch('builtins.print')
    def test_filter_salary_exception_handling(self, mock_print, mock_logger):
        """Тест обработки исключений в фильтре зарплат"""
        ui = self._create_ui()
        ui.storage.get_vacancies.side_effect = Exception("Storage error")
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_logger.error.assert_called_once()
        mock_print.assert_any_call("Ошибка при фильтрации: Storage error")
    
    def _create_ui(self):
        """Создает UI с полными моками"""
        with patch('src.storage.storage_factory.StorageFactory') as mock_sf:
            with patch('src.api_modules.unified_api.UnifiedAPI'):
                with patch('src.utils.menu_manager.create_main_menu'):
                    with patch('src.utils.vacancy_operations.VacancyOperations'):
                        with patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler'):
                            with patch('src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    return UserInterface()


class TestUserInterfaceVacancyDeletion:
    """Тесты сложного метода удаления вакансий"""
    
    @patch('builtins.input', side_effect=['a'])  # Удалить все
    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=True)
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_delete_all(self, mock_print, mock_confirm, mock_input):
        """Тест удаления всех вакансий по ключевому слову"""
        ui = self._create_ui()
        ui.storage.delete_vacancies_by_keyword.return_value = 5
        
        mock_vacancy = MagicMock()
        mock_vacancy.id = "test1"
        mock_vacancy.title = "Python Developer"
        mock_vacancy.url = "http://test.com"
        mock_vacancy.employer = {"name": "Test Co"}
        mock_vacancy.salary = None
        
        ui._show_vacancies_for_deletion([mock_vacancy], "python")
        
        ui.storage.delete_vacancies_by_keyword.assert_called_once_with("python")
        mock_print.assert_any_call("Удалено 5 вакансий.")
    
    @patch('builtins.input', side_effect=['1-3'])  # Удалить диапазон 1-3
    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=True)
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_range(self, mock_print, mock_confirm, mock_input):
        """Тест удаления диапазона вакансий"""
        ui = self._create_ui()
        ui.storage.delete_vacancy.return_value = True
        
        mock_vacancies = []
        for i in range(5):
            vacancy = MagicMock()
            vacancy.id = f"test{i}"
            vacancy.title = f"Job {i}"
            vacancy.url = f"http://test{i}.com"
            vacancy.employer = {"name": f"Company {i}"}
            vacancy.salary = None
            mock_vacancies.append(vacancy)
        
        ui._show_vacancies_for_deletion(mock_vacancies, "test")
        
        # Проверяем что были попытки удаления
        assert ui.storage.delete_vacancy.call_count >= 1
    
    @patch('builtins.input', side_effect=['1-3'])  # Диапазон
    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=False)  # Отмена
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_range_cancelled(self, mock_print, mock_confirm, mock_input):
        """Тест отмены удаления диапазона"""
        ui = self._create_ui()
        
        mock_vacancies = [MagicMock() for _ in range(5)]
        for i, v in enumerate(mock_vacancies):
            v.id = f"test{i}"
            v.title = f"Job {i}"
            v.url = f"http://test{i}.com"
            v.employer = {"name": f"Company {i}"}
            v.salary = None
        
        ui._show_vacancies_for_deletion(mock_vacancies, "test")
        
        # Не должно быть удалений
        ui.storage.delete_vacancy.assert_not_called()
    
    @patch('builtins.input', side_effect=['n', 'q'])  # Следующая страница, затем выход
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_navigation(self, mock_print, mock_input):
        """Тест навигации по страницам при удалении"""
        ui = self._create_ui()
        
        # Создаем больше 10 вакансий для тестирования пагинации
        mock_vacancies = []
        for i in range(15):
            vacancy = MagicMock()
            vacancy.id = f"test{i}"
            vacancy.title = f"Job {i}"
            vacancy.url = f"http://test{i}.com"
            vacancy.employer = {"name": f"Company {i}"}
            vacancy.salary = "100000 руб." if i % 2 == 0 else None
            mock_vacancies.append(vacancy)
        
        ui._show_vacancies_for_deletion(mock_vacancies, "test")
        
        # Проверяем что отображались страницы
        mock_print.assert_any_call("--- Страница 1 из 2 ---")
    
    @patch('builtins.input', side_effect=['5'])  # Удалить конкретную вакансию по номеру
    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=True)
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_single_vacancy(self, mock_print, mock_confirm, mock_input):
        """Тест удаления одной вакансии по номеру"""
        ui = self._create_ui()
        ui.storage.delete_vacancy.return_value = True
        
        mock_vacancies = []
        for i in range(10):
            vacancy = MagicMock()
            vacancy.id = f"test{i}"
            vacancy.title = f"Job {i}"
            vacancy.url = f"http://test{i}.com"
            vacancy.employer = {"name": f"Company {i}"}
            vacancy.salary = None
            mock_vacancies.append(vacancy)
        
        ui._show_vacancies_for_deletion(mock_vacancies, "test")
        
        # Проверяем удаление одной вакансии
        ui.storage.delete_vacancy.assert_called()
    
    def _create_ui(self):
        """Создает UI с полными моками"""
        with patch('src.storage.storage_factory.StorageFactory') as mock_sf:
            with patch('src.api_modules.unified_api.UnifiedAPI'):
                with patch('src.utils.menu_manager.create_main_menu'):
                    with patch('src.utils.vacancy_operations.VacancyOperations'):
                        with patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler'):
                            with patch('src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    return UserInterface()


class TestUserInterfaceStaticMethodsAdvanced:
    """Расширенные тесты статических методов"""
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_get_period_choice_keyboard_interrupt(self, mock_print, mock_input):
        """Тест прерывания выбора периода"""
        result = UserInterface._get_period_choice()
        
        assert result is None
        mock_print.assert_any_call("\nВыбор периода отменен.")
    
    @patch('builtins.input', side_effect=['6', 'abc'])  # Пользовательский период с неверным вводом
    @patch('builtins.print')
    def test_get_period_choice_custom_value_error(self, mock_print, mock_input):
        """Тест ValueError при пользовательском периоде"""
        result = UserInterface._get_period_choice()
        
        assert result == 15  # По умолчанию
        mock_print.assert_any_call("Некорректный ввод. Используется 15 дней по умолчанию.")
    
    @patch('builtins.input', return_value='99')  # Некорректный выбор
    @patch('builtins.print')
    def test_get_period_choice_invalid_choice(self, mock_print, mock_input):
        """Тест некорректного выбора периода"""
        result = UserInterface._get_period_choice()
        
        assert result == 15  # По умолчанию
        mock_print.assert_any_call("Некорректный выбор. Используется 15 дней по умолчанию.")
    
    @patch('src.ui_interfaces.console_interface.display_vacancy_info')
    def test_display_vacancies_with_custom_start_number(self, mock_display):
        """Тест отображения вакансий с пользовательским начальным номером"""
        mock_vacancies = [MagicMock(), MagicMock(), MagicMock()]
        
        UserInterface._display_vacancies(mock_vacancies, start_number=10)
        
        # Проверяем правильную нумерацию с 10
        mock_display.assert_any_call(mock_vacancies[0], 10)
        mock_display.assert_any_call(mock_vacancies[1], 11)
        mock_display.assert_any_call(mock_vacancies[2], 12)
    
    def test_display_vacancies_empty_list(self):
        """Тест отображения пустого списка вакансий"""
        with patch('src.ui_interfaces.console_interface.display_vacancy_info') as mock_display:
            UserInterface._display_vacancies([])
            
            # Не должно быть вызовов display_vacancy_info
            mock_display.assert_not_called()