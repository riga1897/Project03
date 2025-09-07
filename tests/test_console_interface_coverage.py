#!/usr/bin/env python3
"""
Комплексные тесты для 100% покрытия src/ui_interfaces/console_interface.py

Покрывает все методы класса UserInterface, включая:
- Инициализацию и зависимости
- Основной цикл run() со всеми menu choices
- Все операции с вакансиями (поиск, отображение, фильтрация, удаление)
- Static методы для отображения и навигации
- Exception handling и edge cases

ЦЕЛЬ: 100% coverage для 600 строк сложного UI кода

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- Нулевых реальных I/O операций (UI, файлы, API, БД)
- Полное мокирование всех зависимостей
- Покрытие всех условных блоков и exception handlers
"""

import logging
from typing import List, Optional
from unittest.mock import MagicMock, patch, Mock, call
from io import StringIO
import sys

import pytest

from src.ui_interfaces.console_interface import UserInterface


class TestUserInterfaceInit:
    """Тесты инициализации UserInterface"""
    
    @patch('src.storage.storage_factory.StorageFactory')
    @patch('src.api_modules.unified_api.UnifiedAPI')
    @patch('src.utils.menu_manager.create_main_menu')
    @patch('src.utils.vacancy_operations.VacancyOperations')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyOperationsCoordinator')
    def test_init_with_default_storage(self, mock_coordinator, mock_display_handler, 
                                      mock_search_handler, mock_vacancy_ops, mock_menu,
                                      mock_unified_api, mock_storage_factory):
        """Тест инициализации без предоставленного storage"""
        mock_storage = MagicMock()
        mock_storage_factory.get_default_storage.return_value = mock_storage
        mock_unified_api.return_value = MagicMock()
        
        ui = UserInterface()
        
        # Проверяем что storage был получен через StorageFactory
        mock_storage_factory.get_default_storage.assert_called_once()
        assert ui.storage == mock_storage
        assert ui.db_storage == mock_storage
        
        # Проверяем инициализацию других компонентов
        mock_unified_api.assert_called_once()
        mock_menu.assert_called_once()
        mock_vacancy_ops.assert_called_once()
        mock_search_handler.assert_called_once()
        mock_display_handler.assert_called_once()
    
    @patch('src.ui_interfaces.console_interface.UnifiedAPI')
    @patch('src.ui_interfaces.console_interface.create_main_menu')
    @patch('src.ui_interfaces.console_interface.VacancyOperations')
    @patch('src.ui_interfaces.console_interface.VacancySearchHandler')
    @patch('src.ui_interfaces.console_interface.VacancyDisplayHandler')
    @patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator')
    def test_init_with_provided_storage_and_db_manager(self, mock_coordinator, mock_display_handler,
                                                      mock_search_handler, mock_vacancy_ops,
                                                      mock_menu, mock_unified_api):
        """Тест инициализации с предоставленным storage и db_manager"""
        mock_storage = MagicMock()
        mock_db_manager = MagicMock()
        
        # Мокируем DBManagerDemo для инициализации demo
        with patch('src.ui_interfaces.console_interface.DBManagerDemo') as mock_demo:
            ui = UserInterface(storage=mock_storage, db_manager=mock_db_manager)
        
        assert ui.storage == mock_storage
        assert ui.db_manager == mock_db_manager
        assert ui.demo is not None  # Demo должен быть создан
    
    @patch('src.ui_interfaces.console_interface.UnifiedAPI')
    @patch('src.ui_interfaces.console_interface.create_main_menu')
    @patch('src.ui_interfaces.console_interface.VacancyOperations')
    @patch('src.ui_interfaces.console_interface.VacancySearchHandler')
    @patch('src.ui_interfaces.console_interface.VacancyDisplayHandler')
    @patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator')
    def test_init_with_db_manager_none(self, mock_coordinator, mock_display_handler,
                                      mock_search_handler, mock_vacancy_ops,
                                      mock_menu, mock_unified_api):
        """Тест инициализации когда DBManager недоступен"""
        # Мокируем DBManager как None
        with patch('src.ui_interfaces.console_interface.DBManager', None):
            with patch('src.ui_interfaces.console_interface.DBManagerDemo', None):
                ui = UserInterface(db_manager=None)
        
        assert ui.db_manager is None
        assert ui.demo is None


class TestUserInterfaceRun:
    """Тесты основного цикла run()"""
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['0'])  # Выход сразу
    @patch('builtins.print')
    def test_run_basic_exit(self, mock_print, mock_input, mock_header):
        """Тест базового выполнения с немедленным выходом"""
        ui = self._create_mock_ui()
        
        ui.run()
        
        mock_header.assert_called_with("Добро пожаловать в поисковик вакансий!")
        mock_print.assert_any_call("Спасибо за использование! До свидания!")
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['1', '0'])  # Выбор поиска, затем выход
    @patch('builtins.print')
    def test_run_search_vacancies_menu_choice(self, mock_print, mock_input, mock_header):
        """Тест выполнения пункта меню 1 - Поиск вакансий"""
        ui = self._create_mock_ui()
        
        ui.run()
        
        # Проверяем что метод поиска был вызван
        ui.operations_coordinator.handle_vacancy_search.assert_called_once()
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['2', '0'])  # Показ сохраненных, затем выход
    @patch('builtins.print')
    def test_run_show_saved_vacancies_menu_choice(self, mock_print, mock_input, mock_header):
        """Тест выполнения пункта меню 2 - Показ сохраненных вакансий"""
        ui = self._create_mock_ui()
        
        ui.run()
        
        ui.operations_coordinator.handle_show_saved_vacancies.assert_called_once()
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['10', '0'])  # DBManager demo, затем выход
    @patch('builtins.print')
    def test_run_db_manager_demo_available(self, mock_print, mock_input, mock_header):
        """Тест демонстрации DBManager когда она доступна"""
        ui = self._create_mock_ui()
        # Устанавливаем db_manager и demo
        ui.db_manager = MagicMock()
        ui.demo = MagicMock()
        
        ui.run()
        
        # Проверяем что demo был вызван
        ui.demo.run_full_demo.assert_called_once()
        mock_print.assert_any_call("=" * 60)
        mock_print.assert_any_call("ДЕМОНСТРАЦИЯ DBMANAGER")
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['10', '0'])  # DBManager demo, затем выход
    @patch('builtins.print')
    def test_run_db_manager_demo_unavailable(self, mock_print, mock_input, mock_header):
        """Тест когда DBManager недоступен"""
        ui = self._create_mock_ui()
        # db_manager и demo остаются None
        
        ui.run()
        
        mock_print.assert_any_call("\nБаза данных недоступна. Демонстрация DBManager невозможна.")
        mock_print.assert_any_call("Проверьте подключение к PostgreSQL и перезапустите приложение.")
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['99', '0'])  # Неверный выбор, затем выход
    @patch('builtins.print')
    def test_run_invalid_menu_choice(self, mock_print, mock_input, mock_header):
        """Тест неверного выбора меню"""
        ui = self._create_mock_ui()
        
        ui.run()
        
        mock_print.assert_any_call("Неверный выбор. Попробуйте снова.")
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=KeyboardInterrupt())  # Прерывание пользователем
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input, mock_header):
        """Тест прерывания выполнения пользователем"""
        ui = self._create_mock_ui()
        
        ui.run()
        
        mock_print.assert_any_call("\n\nРабота прервана пользователем. До свидания!")
    
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('src.ui_interfaces.console_interface.logger')
    @patch('builtins.input', side_effect=[Exception("Test error"), '0'])  # Ошибка, затем выход
    @patch('builtins.print')
    @patch('time.sleep', return_value=None)  # Мокируем sleep
    def test_run_exception_handling(self, mock_sleep, mock_print, mock_input, mock_logger, mock_header):
        """Тест обработки исключений в основном цикле"""
        ui = self._create_mock_ui()
        
        # Настраиваем _show_menu для генерации исключения
        ui._show_menu = MagicMock(side_effect=[Exception("Test error"), "0"])
        
        ui.run()
        
        # Проверяем логирование ошибки
        mock_logger.error.assert_called_once()
        mock_print.assert_any_call("Произошла ошибка: Test error")
        mock_sleep.assert_called_with(0.1)  # Задержка для избежания цикла
    
    def _create_mock_ui(self):
        """Создает UI с замоканными зависимостями"""
        with patch('src.storage.storage_factory.StorageFactory') as mock_sf:
            with patch('src.api_modules.unified_api.UnifiedAPI') as mock_api:
                with patch('src.utils.menu_manager.create_main_menu'):
                    with patch('src.utils.vacancy_operations.VacancyOperations'):
                        with patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler'):
                            with patch('src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyOperationsCoordinator') as mock_coord:
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    ui = UserInterface()
                                    # Мокируем _show_menu для контроля flow
                                    ui._show_menu = MagicMock(side_effect=['0'])  # По умолчанию выход
                                    return ui


class TestUserInterfaceMenuMethods:
    """Тесты методов меню"""
    
    @patch('src.ui_interfaces.console_interface.print_menu_separator')
    @patch('builtins.input', return_value='5')
    @patch('builtins.print')
    def test_show_menu_basic(self, mock_print, mock_input, mock_separator):
        """Тест отображения основного меню"""
        ui = self._create_mock_ui()
        
        result = ui._show_menu()
        
        assert result == '5'
        mock_separator.assert_called()
        mock_print.assert_any_call("Выберите действие:")
        mock_print.assert_any_call("1. Поиск вакансий по запросу (выбор источника + запрос к API)")
    
    @patch('src.ui_interfaces.console_interface.print_menu_separator')
    @patch('builtins.input', return_value='3')
    @patch('builtins.print')
    def test_show_menu_with_dbmanager_available(self, mock_print, mock_input, mock_separator):
        """Тест отображения меню когда DBManager доступен"""
        with patch('src.ui_interfaces.console_interface.DBManager', MagicMock()):
            with patch('src.ui_interfaces.console_interface.DBManagerDemo', MagicMock()):
                ui = self._create_mock_ui()
                
                result = ui._show_menu()
                
                assert result == '3'
                mock_print.assert_any_call("10. Демонстрация DBManager (анализ данных в БД)")
    
    def _create_mock_ui(self):
        """Создает UI с замоканными зависимостями"""
        with patch('src.ui_interfaces.console_interface.StorageFactory') as mock_sf:
            with patch('src.ui_interfaces.console_interface.UnifiedAPI'):
                with patch('src.ui_interfaces.console_interface.create_main_menu'):
                    with patch('src.ui_interfaces.console_interface.VacancyOperations'):
                        with patch('src.ui_interfaces.console_interface.VacancySearchHandler'):
                            with patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    return UserInterface()


class TestUserInterfaceVacancyMethods:
    """Тесты методов для работы с вакансиями"""
    
    def test_search_vacancies_delegates_to_coordinator(self):
        """Тест делегирования поиска вакансий координатору"""
        ui = self._create_mock_ui()
        
        ui._search_vacancies()
        
        ui.operations_coordinator.handle_vacancy_search.assert_called_once()
    
    def test_show_saved_vacancies_delegates_to_coordinator(self):
        """Тест делегирования показа сохраненных вакансий координатору"""
        ui = self._create_mock_ui()
        
        ui._show_saved_vacancies()
        
        ui.operations_coordinator.handle_show_saved_vacancies.assert_called_once()
    
    def test_get_top_saved_vacancies_by_salary_delegates_to_coordinator(self):
        """Тест делегирования получения топ вакансий координатору"""
        ui = self._create_mock_ui()
        
        ui._get_top_saved_vacancies_by_salary()
        
        ui.operations_coordinator.handle_top_vacancies_by_salary.assert_called_once()
    
    def test_search_saved_vacancies_by_keyword_delegates_to_coordinator(self):
        """Тест делегирования поиска по ключевому слову координатору"""
        ui = self._create_mock_ui()
        
        ui._search_saved_vacancies_by_keyword()
        
        ui.operations_coordinator.handle_search_saved_by_keyword.assert_called_once()
    
    def test_delete_saved_vacancies_delegates_to_coordinator(self):
        """Тест делегирования удаления вакансий координатору"""
        ui = self._create_mock_ui()
        
        ui._delete_saved_vacancies()
        
        ui.operations_coordinator.handle_delete_vacancies.assert_called_once()
    
    def test_clear_api_cache_delegates_to_coordinator(self):
        """Тест делегирования очистки кэша координатору"""
        ui = self._create_mock_ui()
        
        ui._clear_api_cache()
        
        ui.operations_coordinator.handle_cache_cleanup.assert_called_once()
    
    def test_setup_superjob_api_delegates_to_coordinator(self):
        """Тест делегирования настройки SuperJob API координатору"""
        ui = self._create_mock_ui()
        
        ui._setup_superjob_api()
        
        ui.operations_coordinator.handle_superjob_setup.assert_called_once()
    
    def _create_mock_ui(self):
        """Создает UI с замоканными зависимостями"""
        with patch('src.ui_interfaces.console_interface.StorageFactory') as mock_sf:
            with patch('src.ui_interfaces.console_interface.UnifiedAPI'):
                with patch('src.ui_interfaces.console_interface.create_main_menu'):
                    with patch('src.ui_interfaces.console_interface.VacancyOperations'):
                        with patch('src.ui_interfaces.console_interface.VacancySearchHandler'):
                            with patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    return UserInterface()


class TestUserInterfaceAdvancedSearch:
    """Тесты расширенного поиска"""
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="")
    @patch('builtins.print')
    def test_advanced_search_empty_query(self, mock_print, mock_input):
        """Тест расширенного поиска с пустым запросом"""
        ui = self._create_mock_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]  # Есть вакансии
        
        ui._advanced_search_vacancies()
        
        # Метод должен завершиться без дальнейшей обработки
        ui.vacancy_ops.filter_vacancies_by_multiple_keywords.assert_not_called()
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="python, django, rest")
    @patch('src.ui_interfaces.console_interface.quick_paginate')
    @patch('src.ui_interfaces.console_interface.VacancyFormatter')
    @patch('builtins.print')
    def test_advanced_search_comma_separated_keywords(self, mock_print, mock_formatter, 
                                                     mock_paginate, mock_input):
        """Тест расширенного поиска с ключевыми словами через запятую"""
        ui = self._create_mock_ui()
        mock_vacancies = [MagicMock(), MagicMock()]
        ui.storage.get_vacancies.return_value = mock_vacancies
        
        filtered_vacancies = [MagicMock()]
        ui.vacancy_ops.filter_vacancies_by_multiple_keywords.return_value = filtered_vacancies
        
        ui._advanced_search_vacancies()
        
        # Проверяем что был вызван правильный метод фильтрации
        ui.vacancy_ops.filter_vacancies_by_multiple_keywords.assert_called_once_with(
            mock_vacancies, ['python', 'django', 'rest']
        )
        mock_paginate.assert_called_once()
        mock_print.assert_any_call(f"Найдено {len(filtered_vacancies)} вакансий:")
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="python AND django")
    @patch('src.ui_interfaces.console_interface.quick_paginate')
    @patch('src.ui_interfaces.console_interface.VacancyFormatter')
    @patch('builtins.print')
    def test_advanced_search_with_and_operator(self, mock_print, mock_formatter, 
                                              mock_paginate, mock_input):
        """Тест расширенного поиска с AND оператором"""
        ui = self._create_mock_ui()
        mock_vacancies = [MagicMock(), MagicMock()]
        ui.storage.get_vacancies.return_value = mock_vacancies
        
        filtered_vacancies = [MagicMock()]
        ui.vacancy_ops.search_vacancies_advanced.return_value = filtered_vacancies
        
        ui._advanced_search_vacancies()
        
        # Проверяем продвинутый поиск
        ui.vacancy_ops.search_vacancies_advanced.assert_called_once_with(
            mock_vacancies, "python AND django"
        )
        mock_print.assert_any_call("Результаты поиска по запросу: 'python AND django'")
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="nonexistent")
    @patch('builtins.print')
    def test_advanced_search_no_results(self, mock_print, mock_input):
        """Тест расширенного поиска без результатов"""
        ui = self._create_mock_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        
        # Возвращаем пустой результат
        ui.vacancy_ops.search_vacancies_advanced.return_value = []
        
        ui._advanced_search_vacancies()
        
        mock_print.assert_any_call("Вакансии по указанным критериям не найдены.")
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="test")
    @patch('builtins.print')
    def test_advanced_search_no_saved_vacancies(self, mock_print, mock_input):
        """Тест расширенного поиска когда нет сохраненных вакансий"""
        ui = self._create_mock_ui()
        ui.storage.get_vacancies.return_value = []  # Нет вакансий
        
        ui._advanced_search_vacancies()
        
        mock_print.assert_any_call("Нет сохраненных вакансий.")
    
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value="test")
    @patch('src.ui_interfaces.console_interface.logger')
    @patch('builtins.print')
    def test_advanced_search_exception_handling(self, mock_print, mock_logger, mock_input):
        """Тест обработки исключений в расширенном поиске"""
        ui = self._create_mock_ui()
        ui.storage.get_vacancies.side_effect = Exception("Storage error")
        
        ui._advanced_search_vacancies()
        
        mock_logger.error.assert_called_once()
        mock_print.assert_any_call("Ошибка при поиске: Storage error")
    
    def _create_mock_ui(self):
        """Создает UI с замоканными зависимостями"""
        with patch('src.ui_interfaces.console_interface.StorageFactory') as mock_sf:
            with patch('src.ui_interfaces.console_interface.UnifiedAPI'):
                with patch('src.ui_interfaces.console_interface.create_main_menu'):
                    with patch('src.ui_interfaces.console_interface.VacancyOperations'):
                        with patch('src.ui_interfaces.console_interface.VacancySearchHandler'):
                            with patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    return UserInterface()


class TestUserInterfaceSalaryFilter:
    """Тесты фильтрации по зарплате"""
    
    @patch('builtins.input', side_effect=['1', '100000'])  # Минимальная зарплата
    @patch('src.ui_interfaces.console_interface.quick_paginate')
    @patch('src.ui_interfaces.console_interface.VacancyFormatter')
    @patch('builtins.print')
    def test_filter_by_minimum_salary_success(self, mock_print, mock_formatter, 
                                             mock_paginate, mock_input):
        """Тест фильтрации по минимальной зарплате"""
        ui = self._create_mock_ui()
        mock_vacancies = [MagicMock(), MagicMock()]
        ui.storage.get_vacancies.return_value = mock_vacancies
        
        filtered_vacancies = [MagicMock()]
        ui.vacancy_ops.filter_vacancies_by_min_salary.return_value = filtered_vacancies
        ui.vacancy_ops.sort_vacancies_by_salary.return_value = filtered_vacancies
        
        ui._filter_saved_vacancies_by_salary()
        
        ui.vacancy_ops.filter_vacancies_by_min_salary.assert_called_once_with(
            mock_vacancies, 100000
        )
        mock_print.assert_any_call("Вакансии с зарплатой от 100000 руб.:")
        mock_paginate.assert_called_once()
    
    @patch('builtins.input', side_effect=['2', '150000'])  # Максимальная зарплата
    @patch('src.ui_interfaces.console_interface.quick_paginate')
    @patch('src.ui_interfaces.console_interface.VacancyFormatter')
    @patch('builtins.print')
    def test_filter_by_maximum_salary_success(self, mock_print, mock_formatter,
                                             mock_paginate, mock_input):
        """Тест фильтрации по максимальной зарплате"""
        ui = self._create_mock_ui()
        mock_vacancies = [MagicMock(), MagicMock()]
        ui.storage.get_vacancies.return_value = mock_vacancies
        
        filtered_vacancies = [MagicMock()]
        ui.vacancy_ops.filter_vacancies_by_max_salary.return_value = filtered_vacancies
        ui.vacancy_ops.sort_vacancies_by_salary.return_value = filtered_vacancies
        
        ui._filter_saved_vacancies_by_salary()
        
        ui.vacancy_ops.filter_vacancies_by_max_salary.assert_called_once_with(
            mock_vacancies, 150000
        )
        mock_print.assert_any_call("Вакансии с зарплатой до 150000 руб.:")
    
    @patch('builtins.input', side_effect=['3', '100000 - 150000'])  # Диапазон
    @patch('src.ui_interfaces.console_interface.parse_salary_range', return_value=(100000, 150000))
    @patch('src.ui_interfaces.console_interface.quick_paginate')
    @patch('src.ui_interfaces.console_interface.VacancyFormatter')
    @patch('builtins.print')
    def test_filter_by_salary_range_success(self, mock_print, mock_formatter, mock_paginate, 
                                           mock_parse, mock_input):
        """Тест фильтрации по диапазону зарплат"""
        ui = self._create_mock_ui()
        mock_vacancies = [MagicMock(), MagicMock()]
        ui.storage.get_vacancies.return_value = mock_vacancies
        
        filtered_vacancies = [MagicMock()]
        ui.vacancy_ops.filter_vacancies_by_salary_range.return_value = filtered_vacancies
        ui.vacancy_ops.sort_vacancies_by_salary.return_value = filtered_vacancies
        
        ui._filter_saved_vacancies_by_salary()
        
        ui.vacancy_ops.filter_vacancies_by_salary_range.assert_called_once_with(
            mock_vacancies, 100000, 150000
        )
        mock_print.assert_any_call("Вакансии с зарплатой в диапазоне 100000 - 150000 руб.:")
    
    @patch('builtins.input', side_effect=['1', 'invalid'])  # Некорректный ввод
    @patch('builtins.print')
    def test_filter_by_salary_invalid_input(self, mock_print, mock_input):
        """Тест фильтрации с некорректным вводом зарплаты"""
        ui = self._create_mock_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Введите корректное число!")
    
    @patch('builtins.input', return_value='4')  # Неверный выбор
    @patch('builtins.print')
    def test_filter_by_salary_invalid_choice(self, mock_print, mock_input):
        """Тест фильтрации с неверным выбором типа фильтра"""
        ui = self._create_mock_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Неверный выбор.")
    
    @patch('builtins.input', side_effect=['1', '100000'])
    @patch('builtins.print')
    def test_filter_by_salary_no_results(self, mock_print, mock_input):
        """Тест фильтрации без результатов"""
        ui = self._create_mock_ui()
        ui.storage.get_vacancies.return_value = [MagicMock()]
        ui.vacancy_ops.filter_vacancies_by_min_salary.return_value = []  # Нет результатов
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Вакансии с указанными критериями зарплаты не найдены.")
    
    @patch('builtins.print')
    def test_filter_by_salary_no_saved_vacancies(self, mock_print):
        """Тест фильтрации когда нет сохраненных вакансий"""
        ui = self._create_mock_ui()
        ui.storage.get_vacancies.return_value = []  # Нет вакансий
        
        ui._filter_saved_vacancies_by_salary()
        
        mock_print.assert_any_call("Нет сохраненных вакансий.")
    
    def _create_mock_ui(self):
        """Создает UI с замоканными зависимостями"""
        with patch('src.ui_interfaces.console_interface.StorageFactory') as mock_sf:
            with patch('src.ui_interfaces.console_interface.UnifiedAPI'):
                with patch('src.ui_interfaces.console_interface.create_main_menu'):
                    with patch('src.ui_interfaces.console_interface.VacancyOperations'):
                        with patch('src.ui_interfaces.console_interface.VacancySearchHandler'):
                            with patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    return UserInterface()


class TestUserInterfaceStaticMethods:
    """Тесты статических методов"""
    
    @patch('src.ui_interfaces.console_interface.display_vacancy_info')
    def test_display_vacancies_basic(self, mock_display_info):
        """Тест базового отображения вакансий"""
        mock_vacancies = [MagicMock(), MagicMock(), MagicMock()]
        
        UserInterface._display_vacancies(mock_vacancies, start_number=5)
        
        # Проверяем что display_vacancy_info был вызван для каждой вакансии
        assert mock_display_info.call_count == 3
        # Проверяем правильную нумерацию
        mock_display_info.assert_any_call(mock_vacancies[0], 5)
        mock_display_info.assert_any_call(mock_vacancies[1], 6)
        mock_display_info.assert_any_call(mock_vacancies[2], 7)
    
    @patch('src.ui_interfaces.console_interface.quick_paginate')
    @patch('src.ui_interfaces.console_interface.VacancyFormatter')
    def test_display_vacancies_with_pagination(self, mock_formatter, mock_paginate):
        """Тест отображения вакансий с постраничным просмотром"""
        mock_vacancies = [MagicMock(), MagicMock()]
        
        UserInterface._display_vacancies_with_pagination(mock_vacancies)
        
        mock_paginate.assert_called_once_with(
            mock_vacancies,
            formatter=mock_paginate.call_args[1]['formatter'],
            header="Вакансии",
            items_per_page=10
        )
    
    @patch('builtins.input', side_effect=['1', '100'])  # Выбор периода 1 день
    @patch('builtins.print')
    def test_get_period_choice_predefined(self, mock_print, mock_input):
        """Тест выбора предопределенного периода"""
        result = UserInterface._get_period_choice()
        
        assert result == 1
        mock_print.assert_any_call("\nВыберите период публикации вакансий:")
    
    @patch('builtins.input', return_value='')  # Пустой ввод (по умолчанию)
    def test_get_period_choice_default(self, mock_input):
        """Тест выбора периода по умолчанию"""
        result = UserInterface._get_period_choice()
        
        assert result == 15  # По умолчанию 15 дней
    
    @patch('builtins.input', side_effect=['6', '30'])  # Пользовательский период
    @patch('builtins.print')
    def test_get_period_choice_custom(self, mock_print, mock_input):
        """Тест выбора пользовательского периода"""
        result = UserInterface._get_period_choice()
        
        assert result == 30
    
    @patch('builtins.input', side_effect=['6', '500'])  # Период вне диапазона
    @patch('builtins.print')
    def test_get_period_choice_custom_out_of_range(self, mock_print, mock_input):
        """Тест пользовательского периода вне допустимого диапазона"""
        result = UserInterface._get_period_choice()
        
        assert result == 15  # По умолчанию
        mock_print.assert_any_call("Некорректный период. Используется 15 дней по умолчанию.")
    
    @patch('builtins.input', side_effect=['6', 'invalid'])  # Некорректный ввод
    @patch('builtins.print')
    def test_get_period_choice_custom_invalid(self, mock_print, mock_input):
        """Тест некорректного пользовательского периода"""
        result = UserInterface._get_period_choice()
        
        assert result == 15  # По умолчанию
        mock_print.assert_any_call("Некорректный ввод. Используется 15 дней по умолчанию.")
    
    @patch('builtins.input', return_value='0')  # Отмена
    @patch('builtins.print')
    def test_get_period_choice_cancel(self, mock_print, mock_input):
        """Тест отмены выбора периода"""
        result = UserInterface._get_period_choice()
        
        assert result is None
        mock_print.assert_any_call("Выбор периода отменен.")
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_get_period_choice_keyboard_interrupt(self, mock_print, mock_input):
        """Тест прерывания выбора периода"""
        result = UserInterface._get_period_choice()
        
        assert result is None
        mock_print.assert_any_call("\nВыбор периода отменен.")


class TestUserInterfaceConfigureMethods:
    """Тесты методов настройки"""
    
    def test_configure_superjob_api_delegates_to_coordinator(self):
        """Тест делегирования настройки SuperJob API координатору"""
        ui = self._create_mock_ui()
        
        # Покрываем метод _configure_superjob_api()
        ui._configure_superjob_api()
        
        # Должен вызвать handle_superjob_setup через operations_coordinator
        ui.operations_coordinator.handle_superjob_setup.assert_called_once()
    
    def _create_mock_ui(self):
        """Создает UI с замоканными зависимостями"""
        with patch('src.ui_interfaces.console_interface.StorageFactory') as mock_sf:
            with patch('src.ui_interfaces.console_interface.UnifiedAPI'):
                with patch('src.ui_interfaces.console_interface.create_main_menu'):
                    with patch('src.ui_interfaces.console_interface.VacancyOperations'):
                        with patch('src.ui_interfaces.console_interface.VacancySearchHandler'):
                            with patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'):
                                with patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator'):
                                    mock_sf.get_default_storage.return_value = MagicMock()
                                    return UserInterface()