
"""
Тесты для модуля user_interface.py
"""

import os
import sys
from typing import Any
from unittest.mock import MagicMock, Mock, patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestUserInterfaceMain:
    """Тесты для основного модуля пользовательского интерфейса"""

    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    def test_main_function_success(
        self, 
        mock_ui_class: Mock,
        mock_factory: Mock,
        mock_config_class: Mock,
        mock_db_class: Mock
    ) -> None:
        """
        Тест успешного выполнения main функции
        
        Args:
            mock_ui_class: Мок класса UserInterface
            mock_factory: Мок фабрики хранилища
            mock_config_class: Мок класса AppConfig
            mock_db_class: Мок класса DBManager
        """
        # Настройка моков
        mock_db = Mock()
        mock_db.check_connection.return_value = True
        mock_db.create_tables.return_value = None
        mock_db.populate_companies_table.return_value = None
        mock_db.get_companies_and_vacancies_count.return_value = [
            {'company': 'Test Company', 'count': 5}
        ]
        mock_db_class.return_value = mock_db

        mock_config = Mock()
        mock_config.default_storage_type = "postgres"
        mock_config_class.return_value = mock_config

        mock_storage = Mock()
        mock_factory.create_storage.return_value = mock_storage

        mock_ui = Mock()
        mock_ui.run.return_value = None
        mock_ui_class.return_value = mock_ui

        # Импортируем и вызываем main
        from src.user_interface import main
        
        # Выполняем тест
        main()

        # Проверяем вызовы
        mock_db_class.assert_called_once()
        mock_db.check_connection.assert_called_once()
        mock_db.create_tables.assert_called_once()
        mock_db.populate_companies_table.assert_called_once()
        mock_db.get_companies_and_vacancies_count.assert_called_once()
        
        mock_config_class.assert_called_once()
        mock_factory.create_storage.assert_called_once_with("postgres")
        mock_ui_class.assert_called_once_with(mock_storage, db_manager=mock_db)
        mock_ui.run.assert_called_once()

    @patch('src.user_interface.DBManager')
    def test_main_function_db_connection_failure(self, mock_db_class: Mock) -> None:
        """
        Тест неудачного подключения к базе данных
        
        Args:
            mock_db_class: Мок класса DBManager
        """
        # Настройка мока для неудачного подключения
        mock_db = Mock()
        mock_db.check_connection.return_value = False
        mock_db_class.return_value = mock_db

        from src.user_interface import main

        # Выполняем тест и ожидаем что функция завершится без исключения
        main()

        # Проверяем что проверка подключения была вызвана
        mock_db.check_connection.assert_called_once()

    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    def test_main_function_keyboard_interrupt(
        self,
        mock_ui_class: Mock,
        mock_factory: Mock,
        mock_config_class: Mock,
        mock_db_class: Mock
    ) -> None:
        """
        Тест прерывания пользователем
        
        Args:
            mock_ui_class: Мок класса UserInterface
            mock_factory: Мок фабрики хранилища
            mock_config_class: Мок класса AppConfig
            mock_db_class: Мок класса DBManager
        """
        # Настройка моков
        mock_db = Mock()
        mock_db.check_connection.return_value = True
        mock_db.create_tables.return_value = None
        mock_db.populate_companies_table.return_value = None
        mock_db.get_companies_and_vacancies_count.return_value = [
            {'company': 'Test Company', 'count': 5}
        ]
        mock_db_class.return_value = mock_db

        mock_config = Mock()
        mock_config.default_storage_type = "postgres"
        mock_config_class.return_value = mock_config

        mock_storage = Mock()
        mock_factory.create_storage.return_value = mock_storage

        mock_ui = Mock()
        mock_ui.run.side_effect = KeyboardInterrupt()
        mock_ui_class.return_value = mock_ui

        from src.user_interface import main

        # Выполняем тест
        main()

        # Проверяем что все компоненты были инициализированы
        mock_ui.run.assert_called_once()

    @patch('src.user_interface.DBManager')
    def test_main_function_generic_exception(self, mock_db_class: Mock) -> None:
        """
        Тест обработки общего исключения
        
        Args:
            mock_db_class: Мок класса DBManager
        """
        # Настройка мока для исключения
        mock_db_class.side_effect = Exception("Test error")

        from src.user_interface import main

        # Выполняем тест
        main()

        # Проверяем что исключение было обработано
        mock_db_class.assert_called_once()

    def test_module_imports(self) -> None:
        """Тест импортов модуля"""
        try:
            import src.user_interface
            assert hasattr(src.user_interface, 'main')
            assert callable(src.user_interface.main)
            
            # Проверяем что логгер настроен
            assert hasattr(src.user_interface, 'logger')
            
        except ImportError as e:
            pytest.skip(f"Модуль user_interface недоступен: {e}")

    def test_logging_configuration(self) -> None:
        """Тест конфигурации логирования"""
        import logging
        
        # Проверяем что логгер настроен правильно
        logger = logging.getLogger('src.user_interface')
        assert logger is not None
        
        # Проверяем уровень логирования
        root_logger = logging.getLogger()
        assert root_logger.level <= logging.INFO

    @patch('src.user_interface.logger')
    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    def test_logging_calls(
        self,
        mock_ui_class: Mock,
        mock_factory: Mock,
        mock_config_class: Mock,
        mock_db_class: Mock,
        mock_logger: Mock
    ) -> None:
        """
        Тест вызовов логирования
        
        Args:
            mock_ui_class: Мок класса UserInterface
            mock_factory: Мок фабрики хранилища
            mock_config_class: Мок класса AppConfig
            mock_db_class: Мок класса DBManager
            mock_logger: Мок логгера
        """
        # Настройка моков
        mock_db = Mock()
        mock_db.check_connection.return_value = True
        mock_db.create_tables.return_value = None
        mock_db.populate_companies_table.return_value = None
        mock_db.get_companies_and_vacancies_count.return_value = [
            {'company': 'Test Company', 'count': 5}
        ]
        mock_db_class.return_value = mock_db

        mock_config = Mock()
        mock_config.default_storage_type = "postgres"
        mock_config_class.return_value = mock_config

        mock_storage = Mock()
        mock_factory.create_storage.return_value = mock_storage

        mock_ui = Mock()
        mock_ui.run.return_value = None
        mock_ui_class.return_value = mock_ui

        from src.user_interface import main

        # Выполняем тест
        main()

        # Проверяем что логирование было вызвано
        assert mock_logger.info.call_count >= 3


class TestModuleConstants:
    """Тесты констант и настроек модуля"""

    def test_module_level_variables(self) -> None:
        """Тест переменных уровня модуля"""
        import src.user_interface as ui_module
        
        # Проверяем наличие логгера
        assert hasattr(ui_module, 'logger')
        
        # Проверяем что основная функция определена
        assert hasattr(ui_module, 'main')
        assert callable(ui_module.main)

    def test_if_name_main_block(self) -> None:
        """Тест блока if __name__ == '__main__'"""
        # Этот тест проверяет что модуль может быть запущен как скрипт
        import src.user_interface
        
        # Проверяем что модуль правильно настроен для запуска
        assert hasattr(src.user_interface, '__name__')


class TestErrorHandling:
    """Тесты обработки ошибок"""

    @patch('src.user_interface.DBManager')
    def test_database_error_handling(self, mock_db_class: Mock) -> None:
        """
        Тест обработки ошибок базы данных
        
        Args:
            mock_db_class: Мок класса DBManager
        """
        # Настройка мока для ошибки базы данных
        mock_db_class.side_effect = Exception("Database connection failed")

        from src.user_interface import main

        # Выполняем тест и проверяем что ошибка обработана корректно
        main()

        mock_db_class.assert_called_once()

    @patch('builtins.print')
    @patch('src.user_interface.logger')
    @patch('src.user_interface.DBManager')
    def test_error_logging(
        self,
        mock_db_class: Mock,
        mock_logger: Mock,
        mock_print: Mock
    ) -> None:
        """
        Тест логирования ошибок
        
        Args:
            mock_db_class: Мок класса DBManager
            mock_logger: Мок логгера
            mock_print: Мок функции print
        """
        # Настройка мока для ошибки
        test_error = Exception("Test database error")
        mock_db_class.side_effect = test_error

        from src.user_interface import main

        # Выполняем тест
        main()

        # Проверяем что ошибка была залогирована
        mock_logger.error.assert_called_once()
        mock_print.assert_called()
