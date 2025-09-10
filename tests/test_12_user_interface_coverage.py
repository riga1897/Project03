#!/usr/bin/env python3
"""
Тесты для 100% покрытия модуля пользовательского интерфейса.

Архитектурные принципы:
- Все I/O операции заменены на mock (база данных, логирование, файлы)
- Нет реальных подключений к БД, создания файлов или консольного ввода
- Полное покрытие main() функции и всех веток выполнения
- Тестирование всех сценариев инициализации приложения
"""

import logging
from unittest.mock import patch, Mock, MagicMock
import pytest

# Импорты из реального кода для покрытия
import src.user_interface


class TestUserInterface:
    """100% покрытие модуля пользовательского интерфейса."""

    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.storage.db_manager.DBManager')
    def test_main_success(self, mock_db_manager_class, mock_app_config, 
                         mock_storage_factory, mock_ui):
        """Покрытие успешного выполнения main()."""
        # Настраиваем мок БД с контекстным менеджером
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True  
        mock_db_manager.initialize_database.return_value = True
        mock_db_manager.get_companies_and_vacancies_count.return_value = [("Company1", 10)]

        # Настраиваем контекстный менеджер для _get_connection()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [5]  # count результат 
        mock_connection.cursor.return_value = mock_cursor
        mock_db_manager._get_connection.return_value = mock_connection

        mock_db_manager_class.return_value = mock_db_manager

        # Настраиваем мок конфигурации
        mock_config = Mock()
        mock_config.default_storage_type = "postgres"
        mock_app_config.return_value = mock_config

        # Настраиваем мок хранилища
        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage

        # Настраиваем мок UI
        mock_ui_instance = Mock()
        mock_ui.return_value = mock_ui_instance

        # Выполняем функцию
        src.user_interface.main()

        # Проверяем что компоненты инициализированы согласно реальному коду
        mock_db_manager_class.assert_called_once()
        mock_db_manager.check_connection.assert_called_once()
        mock_db_manager.initialize_database.assert_called_once()
        mock_ui.assert_called_once()
        mock_ui_instance.run.assert_called_once()

    @patch('src.storage.db_manager.DBManager')
    @patch('builtins.print')
    def test_main_database_creation_error(self, mock_print, mock_db_manager_class):
        """Покрытие ошибки создания базы данных."""
        # Настраиваем мок для ошибки создания БД
        mock_db_manager = Mock()
        mock_db_manager._ensure_database_exists.side_effect = Exception("DB Creation Error")
        mock_db_manager_class.return_value = mock_db_manager

        # Выполняем функцию (она не должна вызывать исключение, а обработать его)
        result = src.user_interface.main()

        # Проверяем что функция завершилась gracefully (return None)
        assert result is None
        # Проверяем что была выведена ошибка
        mock_print.assert_called()

    @patch('src.storage.db_manager.DBManager')
    @patch('builtins.print')
    def test_main_connection_error(self, mock_print, mock_db_manager_class):
        """Покрытие ошибки подключения к базе данных."""
        # Настраиваем мок для ошибки подключения
        mock_db_manager = Mock()
        mock_db_manager._ensure_database_exists.return_value = None
        mock_db_manager.check_connection.return_value = False
        mock_db_manager_class.return_value = mock_db_manager

        # Выполняем функцию (она обрабатывает ошибку gracefully)
        result = src.user_interface.main()

        # Проверяем что функция завершилась gracefully
        assert result is None
        # Проверяем что попытка подключения была сделана
        mock_db_manager.check_connection.assert_called_once()
        # Проверяем что была выведена ошибка
        mock_print.assert_called()

    @patch('src.storage.db_manager.DBManager')
    @patch('builtins.print')
    def test_main_table_creation_error(self, mock_print, mock_db_manager_class):
        """Покрытие ошибки создания таблиц."""
        # Настраиваем мок для ошибки создания таблиц
        mock_db_manager = Mock()
        mock_db_manager._ensure_database_exists.return_value = None
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.side_effect = Exception("Table Creation Error")
        mock_db_manager_class.return_value = mock_db_manager

        # Выполняем функцию (она обрабатывает ошибку gracefully)
        result = src.user_interface.main()

        # Проверяем что функция завершилась gracefully
        assert result is None
        # Проверяем что была выведена ошибка
        mock_print.assert_called()

    @patch('src.storage.db_manager.DBManager')
    @patch('builtins.print')
    def test_main_populate_companies_error(self, mock_print, mock_db_manager_class):
        """Покрытие ошибки заполнения таблицы компаний."""
        # Настраиваем мок для ошибки заполнения компаний
        mock_db_manager = Mock()
        mock_db_manager._ensure_database_exists.return_value = None
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.side_effect = Exception("Populate Error")
        mock_db_manager_class.return_value = mock_db_manager

        # Выполняем функцию (она обрабатывает ошибку gracefully)
        result = src.user_interface.main()

        # Проверяем что функция завершилась gracefully
        assert result is None
        # Проверяем что была выведена ошибка
        mock_print.assert_called()

    @patch('src.storage.db_manager.DBManager')
    @patch('builtins.print')
    def test_main_validation_error(self, mock_print, mock_db_manager_class):
        """Покрытие ошибки валидации инициализации БД."""
        # Настраиваем мок для ошибки валидации
        mock_db_manager = Mock()
        mock_db_manager._ensure_database_exists.return_value = None
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.side_effect = Exception("Validation Error")
        mock_db_manager_class.return_value = mock_db_manager

        # Выполняем функцию (она обрабатывает ошибку gracefully)
        result = src.user_interface.main()

        # Проверяем что функция завершилась gracefully
        assert result is None
        # Проверяем что была выведена ошибка
        mock_print.assert_called()

    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')  
    @patch('src.user_interface.AppConfig')
    @patch('src.storage.db_manager.DBManager')
    @patch('builtins.print')
    def test_main_storage_error(self, mock_print, mock_db_manager_class, mock_app_config, 
                               mock_storage_factory, mock_ui):
        """Покрытие ошибки создания хранилища."""
        # Настраиваем мок БД для успешного выполнения
        mock_db_manager = Mock()
        mock_db_manager._ensure_database_exists.return_value = None
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [("Company1", 10)]
        mock_db_manager_class.return_value = mock_db_manager

        mock_config = Mock()
        mock_app_config.return_value = mock_config

        # Настраиваем мок хранилища для ошибки
        mock_storage_factory.create_storage.side_effect = Exception("Storage Error")

        # Выполняем функцию (она обрабатывает ошибку gracefully)
        result = src.user_interface.main()

        # Проверяем что функция завершилась gracefully
        assert result is None
        # Проверяем что была выведена ошибка
        mock_print.assert_called()

    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.storage.db_manager.DBManager')
    @patch('builtins.print')
    def test_main_ui_error(self, mock_print, mock_db_manager_class, mock_app_config, 
                          mock_storage_factory, mock_ui):
        """Покрытие ошибки создания пользовательского интерфейса."""
        # Настраиваем моки для успешного выполнения до UI
        mock_db_manager = Mock()
        mock_db_manager._ensure_database_exists.return_value = None
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [("Company1", 10)]
        mock_db_manager_class.return_value = mock_db_manager

        mock_config = Mock()
        mock_app_config.return_value = mock_config

        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage

        # Настраиваем мок UI для ошибки
        mock_ui.side_effect = Exception("UI Error")

        # Выполняем функцию (она обрабатывает ошибку gracefully)
        result = src.user_interface.main()

        # Проверяем что функция завершилась gracefully
        assert result is None
        # Проверяем что была выведена ошибка
        mock_print.assert_called()

    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.storage.db_manager.DBManager')
    @patch('builtins.print')
    def test_main_ui_run_error(self, mock_print, mock_db_manager_class, mock_app_config,
                              mock_storage_factory, mock_ui):
        """Покрытие ошибки запуска пользовательского интерфейса."""
        # Настраиваем моки для успешного выполнения до запуска UI
        mock_db_manager = Mock()
        mock_db_manager._ensure_database_exists.return_value = None
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [("Company1", 10)]
        mock_db_manager_class.return_value = mock_db_manager

        mock_config = Mock()
        mock_config.default_storage_type = "postgres"
        mock_app_config.return_value = mock_config

        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage

        mock_ui_instance = Mock()
        mock_ui_instance.run.side_effect = Exception("UI Run Error")
        mock_ui.return_value = mock_ui_instance

        # Выполняем функцию (она обрабатывает ошибку gracefully)
        result = src.user_interface.main()

        # Проверяем что функция завершилась gracefully
        assert result is None
        # Проверяем что была выведена ошибка
        mock_print.assert_called()

    def test_logging_configuration(self) -> None:
        """Покрытие конфигурации логирования."""
        # Проверяем что модуль содержит правильную настройку логирования
        assert hasattr(src.user_interface, 'logger')
        assert isinstance(src.user_interface.logger, logging.Logger)
        assert src.user_interface.logger.name == 'src.user_interface'

    @patch('src.storage.db_manager.DBManager')
    @patch('builtins.print')
    def test_main_general_exception(self, mock_print, mock_db_manager):
        """Покрытие общего исключения в try-except блоке main()."""
        # Мокаем чтобы вызвать общее исключение в начале функции
        mock_db_manager.side_effect = Exception("General Error")

        # Выполняем функцию (она обрабатывает ошибку gracefully)
        result = src.user_interface.main()

        # Проверяем что функция завершилась gracefully
        assert result is None
        # Проверяем что была выведена ошибка
        mock_print.assert_called()


class TestUserInterfaceImports:
    """Покрытие импортов модуля."""

    def test_imports_exist(self) -> None:
        """Покрытие всех импортов модуля."""
        # Проверяем что все необходимые импорты доступны
        assert hasattr(src.user_interface, 'logging')
        assert hasattr(src.user_interface, 'AppConfig')
        assert hasattr(src.user_interface, 'StorageFactory')  
        assert hasattr(src.user_interface, 'UserInterface')
        assert hasattr(src.user_interface, 'main')
        assert hasattr(src.user_interface, 'logger')

    def test_main_function_exists(self) -> None:
        """Покрытие существования главной функции."""
        assert callable(src.user_interface.main)

        # Проверяем docstring функции
        assert src.user_interface.main.__doc__ is not None
        assert "Основная функция" in src.user_interface.main.__doc__


class TestUserInterfaceIntegration:
    """Покрытие интеграционных аспектов."""

    @patch('src.user_interface.logging.basicConfig')
    @patch('src.storage.db_manager.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.logger')
    def test_full_integration_flow(self, mock_logger, mock_ui, mock_storage_factory,
                                  mock_app_config, mock_db_manager_class, mock_logging_config):
        """Покрытие полного потока интеграции компонентов."""
        # Настраиваем все моки для успешного сценария
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.initialize_database.return_value = True
        mock_db_manager.get_companies_and_vacancies_count.return_value = [
            ("Company1", 10), ("Company2", 5), ("Company3", 3)
        ]

        # Настраиваем контекстный менеджер для _get_connection()
        from unittest.mock import MagicMock
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [3]  # count результат 
        mock_connection.cursor.return_value = mock_cursor
        mock_db_manager._get_connection.return_value = mock_connection

        mock_db_manager_class.return_value = mock_db_manager

        mock_config = Mock()
        mock_config.storage_type = "postgres"
        mock_app_config.return_value = mock_config

        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage

        mock_ui_instance = Mock()
        mock_ui.return_value = mock_ui_instance

        # Выполняем функцию
        src.user_interface.main()

        # Проверяем порядок вызовов
        mock_logger.info.assert_called()
        mock_db_manager.check_connection.assert_called_once()
        mock_db_manager.initialize_database.assert_called_once()
        mock_db_manager.get_companies_and_vacancies_count.assert_called_once()
        mock_storage_factory.create_storage.assert_called_once_with(mock_config.default_storage_type)
        mock_ui.assert_called_once_with(mock_storage, db_manager=mock_db_manager)
        mock_ui_instance.run.assert_called_once()

    def test_module_level_configuration(self) -> None:
        """Покрытие настроек на уровне модуля."""
        # Проверяем что логирование настроено на уровне модуля
        assert src.user_interface.logger is not None

        # Проверяем что есть docstring модуля
        assert src.user_interface.__doc__ is not None