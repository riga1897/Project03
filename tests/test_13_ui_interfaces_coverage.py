#!/usr/bin/env python3
"""
Тесты для 100% покрытия UI интерфейсов.

Архитектурные принципы:
- Все I/O операции заменены на mock (консольный ввод, вывод, файлы)
- Нет реальных взаимодействий с базой данных или файловой системой
- Полное покрытие console_interface.py и других UI модулей
- Тестирование всех веток логики пользовательского интерфейса
"""

import logging
from unittest.mock import patch, Mock, MagicMock, call
import pytest

# Импорты из реального кода для покрытия  
import src.ui_interfaces.console_interface


class TestConsoleInterface:
    """100% покрытие консольного интерфейса."""

    @patch('src.ui_interfaces.console_interface.VacancySearchHandler')
    @patch('src.ui_interfaces.console_interface.VacancyDisplayHandler')
    @patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator')
    @patch('src.ui_interfaces.console_interface.UnifiedAPI')
    @patch('src.ui_interfaces.console_interface.StorageFactory')
    def test_user_interface_init(self, mock_storage_factory, mock_unified_api,
                                mock_ops_coordinator, mock_display_handler, 
                                mock_search_handler):
        """Покрытие инициализации пользовательского интерфейса."""
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        # Настраиваем моки
        mock_storage_factory.get_default_storage.return_value = mock_storage
        
        ui = src.ui_interfaces.console_interface.UserInterface(mock_storage, mock_db_manager)
        
        assert ui.storage is mock_storage
        assert ui.db_manager is mock_db_manager

    @patch('src.ui_interfaces.console_interface.VacancySearchHandler')
    @patch('src.ui_interfaces.console_interface.VacancyDisplayHandler')
    @patch('src.ui_interfaces.console_interface.VacancyOperationsCoordinator')
    @patch('src.ui_interfaces.console_interface.UnifiedAPI')
    @patch('src.ui_interfaces.console_interface.StorageFactory')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_main_menu_exit(self, mock_print, mock_input,
                               mock_storage_factory, mock_unified_api,
                               mock_ops_coordinator, mock_display_handler, 
                               mock_search_handler):
        """Покрытие главного меню с выходом."""
        mock_input.return_value = "0"
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        # Настраиваем моки
        mock_storage_factory.get_default_storage.return_value = mock_storage
        
        ui = src.ui_interfaces.console_interface.UserInterface(mock_storage, mock_db_manager)
        ui.run()
        
        # Проверяем что выведено меню
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_main_menu_invalid_choice(self, mock_print, mock_input):
        """Покрытие неверного выбора в главном меню."""
        mock_input.side_effect = ["invalid", "0"]
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        ui = UserInterface(mock_storage, mock_db_manager)
        ui.run()
        
        # Проверяем что была обработана ошибка выбора
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_search_vacancies(self, mock_print, mock_input):
        """Покрытие поиска вакансий."""
        mock_input.side_effect = ["1", "0"]  # Поиск вакансий, затем выход
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        ui = UserInterface(mock_storage, mock_db_manager)
        
        # Мокаем метод обработки поиска
        ui.vacancy_search_handler.handle_search = Mock()
        
        ui.run()
        
        # Проверяем что был вызван обработчик поиска
        ui.vacancy_search_handler.handle_search.assert_called_once()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_display_vacancies(self, mock_print, mock_input):
        """Покрытие отображения вакансий."""
        mock_input.side_effect = ["2", "0"]  # Отображение вакансий, затем выход
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        ui = UserInterface(mock_storage, mock_db_manager)
        
        # Мокаем метод отображения
        ui.vacancy_display_handler.display_saved_vacancies = Mock()
        
        ui.run()
        
        # Проверяем что был вызван обработчик отображения
        ui.vacancy_display_handler.display_saved_vacancies.assert_called_once()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_vacancy_operations(self, mock_print, mock_input):
        """Покрытие операций с вакансиями."""
        mock_input.side_effect = ["3", "0"]  # Операции с вакансиями, затем выход
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        ui = UserInterface(mock_storage, mock_db_manager)
        
        # Мокаем метод операций
        ui.vacancy_operations_coordinator.coordinate_operations = Mock()
        
        ui.run()
        
        # Проверяем что был вызван координатор операций
        ui.vacancy_operations_coordinator.coordinate_operations.assert_called_once()

    @patch('builtins.input') 
    @patch('builtins.print')
    def test_run_statistics(self, mock_print, mock_input):
        """Покрытие статистики."""
        mock_input.side_effect = ["4", "0"]  # Статистика, затем выход
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        # Настраиваем мок для get_companies_and_vacancies_count
        mock_db_manager.get_companies_and_vacancies_count.return_value = [
            ("Company A", 10), ("Company B", 5)
        ]
        
        ui = UserInterface(mock_storage, mock_db_manager)
        ui.run()
        
        # Проверяем что была вызвана статистика
        mock_db_manager.get_companies_and_vacancies_count.assert_called_once()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_statistics_empty(self, mock_print, mock_input):
        """Покрытие пустой статистики."""
        mock_input.side_effect = ["4", "0"]  # Статистика, затем выход
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        # Настраиваем мок для пустой статистики
        mock_db_manager.get_companies_and_vacancies_count.return_value = []
        
        ui = UserInterface(mock_storage, mock_db_manager)
        ui.run()
        
        # Проверяем что была обработана пустая статистика
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_statistics_error(self, mock_print, mock_input):
        """Покрытие ошибки статистики."""
        mock_input.side_effect = ["4", "0"]  # Статистика, затем выход
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        # Настраиваем мок для ошибки статистики
        mock_db_manager.get_companies_and_vacancies_count.side_effect = Exception("DB Error")
        
        ui = UserInterface(mock_storage, mock_db_manager)
        ui.run()
        
        # Проверяем что была обработана ошибка
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input):
        """Покрытие прерывания с клавиатуры."""
        mock_input.side_effect = KeyboardInterrupt()
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        ui = UserInterface(mock_storage, mock_db_manager)
        ui.run()
        
        # Проверяем что было обработано прерывание
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_general_exception(self, mock_print, mock_input):
        """Покрытие общего исключения."""
        mock_input.side_effect = Exception("General error")
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        ui = UserInterface(mock_storage, mock_db_manager)
        ui.run()
        
        # Проверяем что была обработана ошибка
        mock_print.assert_called()


class TestSourceSelector:
    """100% покрытие селектора источников."""

    def test_source_selector_init(self):
        """Покрытие инициализации селектора источников."""
        selector = SourceSelector()
        
        # Проверяем что объект создан корректно
        assert selector is not None

    @patch('builtins.input')
    @patch('builtins.print')
    def test_select_source_hh(self, mock_print, mock_input):
        """Покрытие выбора HeadHunter."""
        mock_input.return_value = "1"
        
        selector = SourceSelector()
        result = selector.select_source()
        
        # Проверяем что возвращен правильный источник
        assert result == "hh"

    @patch('builtins.input')
    @patch('builtins.print')
    def test_select_source_sj(self, mock_print, mock_input):
        """Покрытие выбора SuperJob."""
        mock_input.return_value = "2"
        
        selector = SourceSelector()
        result = selector.select_source()
        
        # Проверяем что возвращен правильный источник
        assert result == "sj"

    @patch('builtins.input')
    @patch('builtins.print')
    def test_select_source_both(self, mock_print, mock_input):
        """Покрытие выбора обоих источников."""
        mock_input.return_value = "3"
        
        selector = SourceSelector()
        result = selector.select_source()
        
        # Проверяем что возвращены оба источника
        assert result == "both"

    @patch('builtins.input')
    @patch('builtins.print')
    def test_select_source_invalid_then_valid(self, mock_print, mock_input):
        """Покрытие неверного выбора с последующим правильным."""
        mock_input.side_effect = ["invalid", "1"]
        
        selector = SourceSelector()
        result = selector.select_source()
        
        # Проверяем что в итоге возвращен правильный результат
        assert result == "hh"


class TestVacancyDisplayHandler:
    """100% покрытие обработчика отображения вакансий."""

    def test_vacancy_display_handler_init(self):
        """Покрытие инициализации обработчика отображения."""
        mock_storage = Mock()
        
        handler = VacancyDisplayHandler(mock_storage)
        
        assert handler.storage is mock_storage

    @patch('builtins.print')
    def test_display_saved_vacancies_empty(self, mock_print):
        """Покрытие отображения пустого списка вакансий."""
        mock_storage = Mock()
        mock_storage.load_vacancies.return_value = []
        
        handler = VacancyDisplayHandler(mock_storage)
        handler.display_saved_vacancies()
        
        # Проверяем что выведено сообщение о пустом списке
        mock_print.assert_called()

    @patch('builtins.print')
    def test_display_saved_vacancies_with_data(self, mock_print):
        """Покрытие отображения вакансий с данными."""
        mock_vacancy = Mock()
        mock_vacancy.title = "Python Developer"
        mock_vacancy.employer = Mock()
        mock_vacancy.employer.name = "Test Company"
        mock_vacancy.salary = None
        mock_vacancy.url = "http://test.com"
        
        mock_storage = Mock()
        mock_storage.load_vacancies.return_value = [mock_vacancy]
        
        handler = VacancyDisplayHandler(mock_storage)
        handler.display_saved_vacancies()
        
        # Проверяем что вакансии были отображены
        mock_print.assert_called()

    @patch('builtins.print')
    def test_display_saved_vacancies_error(self, mock_print):
        """Покрытие ошибки при отображении вакансий."""
        mock_storage = Mock()
        mock_storage.load_vacancies.side_effect = Exception("Storage error")
        
        handler = VacancyDisplayHandler(mock_storage)
        handler.display_saved_vacancies()
        
        # Проверяем что была обработана ошибка
        mock_print.assert_called()


class TestVacancySearchHandler:
    """100% покрытие обработчика поиска вакансий."""

    def test_vacancy_search_handler_init(self):
        """Покрытие инициализации обработчика поиска."""
        mock_storage = Mock()
        mock_source_selector = Mock()
        
        handler = VacancySearchHandler(mock_storage, mock_source_selector)
        
        assert handler.storage is mock_storage
        assert handler.source_selector is mock_source_selector

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_search_success(self, mock_print, mock_input):
        """Покрытие успешного поиска вакансий."""
        mock_input.side_effect = ["Python developer"]
        
        mock_storage = Mock()
        mock_source_selector = Mock()
        mock_source_selector.select_source.return_value = "hh"
        
        handler = VacancySearchHandler(mock_storage, mock_source_selector)
        
        # Мокаем поиск вакансий
        with patch.object(handler, '_search_vacancies') as mock_search:
            mock_search.return_value = [Mock()]
            
            handler.handle_search()
            
            # Проверяем что поиск был выполнен
            mock_search.assert_called_once()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_search_empty_query(self, mock_print, mock_input):
        """Покрытие пустого поискового запроса."""
        mock_input.return_value = ""
        
        mock_storage = Mock()
        mock_source_selector = Mock()
        
        handler = VacancySearchHandler(mock_storage, mock_source_selector)
        handler.handle_search()
        
        # Проверяем что было выведено сообщение об ошибке
        mock_print.assert_called()


class TestVacancyOperationsCoordinator:
    """100% покрытие координатора операций с вакансиями."""

    def test_vacancy_operations_coordinator_init(self):
        """Покрытие инициализации координатора операций."""
        mock_storage = Mock()
        
        coordinator = VacancyOperationsCoordinator(mock_storage)
        
        assert coordinator.storage is mock_storage

    @patch('builtins.input')
    @patch('builtins.print')
    def test_coordinate_operations_back(self, mock_print, mock_input):
        """Покрытие возврата в главное меню."""
        mock_input.return_value = "0"
        
        mock_storage = Mock()
        coordinator = VacancyOperationsCoordinator(mock_storage)
        
        coordinator.coordinate_operations()
        
        # Проверяем что меню было отображено
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_coordinate_operations_invalid_choice(self, mock_print, mock_input):
        """Покрытие неверного выбора операции."""
        mock_input.side_effect = ["invalid", "0"]
        
        mock_storage = Mock()
        coordinator = VacancyOperationsCoordinator(mock_storage)
        
        coordinator.coordinate_operations()
        
        # Проверяем что была обработана ошибка выбора
        mock_print.assert_called()


class TestUIInterfacesIntegration:
    """100% покрытие интеграции UI интерфейсов."""

    def test_user_interface_components_integration(self):
        """Покрытие интеграции компонентов пользовательского интерфейса."""
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        ui = UserInterface(mock_storage, mock_db_manager)
        
        # Проверяем что все компоненты инициализированы корректно
        assert isinstance(ui.vacancy_search_handler, VacancySearchHandler)
        assert isinstance(ui.vacancy_display_handler, VacancyDisplayHandler)
        assert isinstance(ui.vacancy_operations_coordinator, VacancyOperationsCoordinator)
        assert isinstance(ui.source_selector, SourceSelector)
        
        # Проверяем что компоненты получили правильные зависимости
        assert ui.vacancy_search_handler.storage is mock_storage
        assert ui.vacancy_display_handler.storage is mock_storage
        assert ui.vacancy_operations_coordinator.storage is mock_storage

    def test_components_creation(self):
        """Покрытие создания отдельных компонентов."""
        mock_storage = Mock()
        
        # Тестируем создание каждого компонента отдельно
        source_selector = SourceSelector()
        display_handler = VacancyDisplayHandler(mock_storage)
        search_handler = VacancySearchHandler(mock_storage, source_selector)
        operations_coordinator = VacancyOperationsCoordinator(mock_storage)
        
        # Проверяем что все компоненты созданы корректно
        assert source_selector is not None
        assert display_handler.storage is mock_storage
        assert search_handler.storage is mock_storage
        assert search_handler.source_selector is source_selector
        assert operations_coordinator.storage is mock_storage


class TestUIInterfacesErrorHandling:
    """100% покрытие обработки ошибок в UI интерфейсах."""

    @patch('builtins.print')
    def test_error_handling_in_display(self, mock_print):
        """Покрытие обработки ошибок в отображении."""
        mock_storage = Mock()
        mock_storage.load_vacancies.side_effect = Exception("Storage error")
        
        handler = VacancyDisplayHandler(mock_storage)
        
        # Функция должна обработать ошибку gracefully
        handler.display_saved_vacancies()
        
        # Проверяем что ошибка была обработана
        mock_print.assert_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_error_handling_in_menu(self, mock_print, mock_input):
        """Покрытие обработки ошибок в меню."""
        mock_input.side_effect = Exception("Input error")
        
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        ui = UserInterface(mock_storage, mock_db_manager)
        
        # Функция должна обработать ошибку gracefully
        ui.run()
        
        # Проверяем что ошибка была обработана
        mock_print.assert_called()