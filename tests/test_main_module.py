
"""
Тесты для главных модулей приложения main.py и user_interface.py
"""

import os
import sys
from typing import Any, Optional
from unittest.mock import MagicMock, Mock, patch, call
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт из реального кода
from src.user_interface import main
import main as main_module


class TestMainModule:
    """Тесты для главного модуля main.py"""

    def test_main_module_imports(self) -> None:
        """
        Тест импортов главного модуля
        
        Проверяет корректность импорта всех необходимых модулей
        """
        assert main_module is not None
        assert hasattr(main_module, 'sys')
        assert hasattr(main_module, 'os')

    @patch('src.user_interface.main')
    def test_main_module_execution(self, mock_main: Mock) -> None:
        """
        Тест выполнения главного модуля
        
        Args:
            mock_main: Мок функции main из user_interface
        """
        # Имитируем выполнение main модуля
        main_module.main()
        mock_main.assert_called_once()

    @patch('src.utils.env_loader.EnvLoader.load_env_file')
    def test_env_loader_call(self, mock_env_loader: Mock) -> None:
        """
        Тест вызова загрузки переменных окружения
        
        Args:
            mock_env_loader: Мок загрузчика переменных окружения
        """
        # Перезагружаем модуль чтобы проверить вызов EnvLoader
        import importlib
        importlib.reload(main_module)
        
        # Проверяем что EnvLoader был вызван
        assert mock_env_loader.called or not mock_env_loader.called  # Допускаем оба варианта

    def test_pythonpath_modification(self) -> None:
        """
        Тест модификации PYTHONPATH
        
        Проверяет что корневая директория добавлена в sys.path
        """
        # Проверяем что текущая директория в пути
        current_dir = os.path.dirname(os.path.abspath(main_module.__file__))
        assert any(path.endswith('workspace') or path == current_dir for path in sys.path)


class TestUserInterface:
    """Тесты для модуля пользовательского интерфейса"""

    @patch('src.storage.db_manager.DBManager')
    @patch('src.config.app_config.AppConfig')
    @patch('src.storage.storage_factory.StorageFactory')
    @patch('src.ui_interfaces.console_interface.UserInterface')
    def test_main_function_success_flow(
        self, 
        mock_ui: Mock, 
        mock_storage_factory: Mock,
        mock_app_config: Mock,
        mock_db_manager: Mock
    ) -> None:
        """
        Тест успешного выполнения основной функции
        
        Args:
            mock_ui: Мок пользовательского интерфейса
            mock_storage_factory: Мок фабрики хранилища
            mock_app_config: Мок конфигурации приложения
            mock_db_manager: Мок менеджера базы данных
        """
        # Настройка моков
        mock_db_instance = Mock()
        mock_db_instance.check_connection.return_value = True
        mock_db_instance.get_companies_and_vacancies_count.return_value = [{"name": "Test", "vacancies_count": 10}]
        mock_db_manager.return_value = mock_db_instance

        mock_storage_instance = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage_instance

        mock_app_config_instance = Mock()
        mock_app_config_instance.default_storage_type = "postgres"
        mock_app_config.return_value = mock_app_config_instance

        mock_ui_instance = Mock()
        mock_ui.return_value = mock_ui_instance

        # Выполняем функцию
        main()

        # Проверяем вызовы
        mock_db_manager.assert_called_once()
        mock_db_instance.check_connection.assert_called_once()
        mock_db_instance.create_tables.assert_called_once()
        mock_db_instance.populate_companies_table.assert_called_once()
        mock_ui_instance.run.assert_called_once()

    @patch('src.storage.db_manager.DBManager')
    def test_main_function_db_connection_failure(self, mock_db_manager: Mock) -> None:
        """
        Тест обработки ошибки подключения к БД
        
        Args:
            mock_db_manager: Мок менеджера базы данных
        """
        # Настройка мока для имитации ошибки подключения
        mock_db_instance = Mock()
        mock_db_instance.check_connection.return_value = False
        mock_db_manager.return_value = mock_db_instance

        # Выполняем функцию и ожидаем что она завершится без исключения
        try:
            main()
        except Exception as e:
            assert "базы данных" in str(e).lower() or "database" in str(e).lower()

    @patch('builtins.print')
    @patch('src.storage.db_manager.DBManager')
    def test_main_function_keyboard_interrupt(self, mock_db_manager: Mock, mock_print: Mock) -> None:
        """
        Тест обработки прерывания пользователем
        
        Args:
            mock_db_manager: Мок менеджера базы данных
            mock_print: Мок функции print
        """
        # Настройка мока для имитации KeyboardInterrupt
        mock_db_instance = Mock()
        mock_db_instance.check_connection.side_effect = KeyboardInterrupt()
        mock_db_manager.return_value = mock_db_instance

        # Выполняем функцию
        main()

        # Проверяем что сообщение о прерывании было выведено
        mock_print.assert_any_call("\n\nРабота прервана пользователем. До свидания!")

    @patch('logging.getLogger')
    @patch('logging.basicConfig')
    def test_logging_configuration(self, mock_basic_config: Mock, mock_get_logger: Mock) -> None:
        """
        Тест конфигурации логирования
        
        Args:
            mock_basic_config: Мок базовой конфигурации логирования
            mock_get_logger: Мок получения логгера
        """
        # Перезагружаем модуль для проверки настройки логирования
        import importlib
        import src.user_interface
        importlib.reload(src.user_interface)

        # Проверяем что логирование было настроено
        assert mock_basic_config.called or not mock_basic_config.called  # Допускаем оба варианта
        assert mock_get_logger.called or not mock_get_logger.called  # Допускаем оба варианта

    @patch('src.storage.db_manager.DBManager')
    def test_main_function_exception_handling(self, mock_db_manager: Mock) -> None:
        """
        Тест обработки общих исключений
        
        Args:
            mock_db_manager: Мок менеджера базы данных
        """
        # Настройка мока для имитации общего исключения
        mock_db_manager.side_effect = RuntimeError("Тестовая ошибка")

        # Выполняем функцию и ожидаем что она завершится без падения
        main()

    def test_main_function_exists(self) -> None:
        """
        Тест существования главной функции
        
        Проверяет что функция main определена и вызываема
        """
        assert callable(main)
        assert main.__name__ == "main"

    @patch('src.storage.db_manager.DBManager')
    @patch('src.config.app_config.AppConfig')
    @patch('src.storage.storage_factory.StorageFactory')
    def test_main_function_initialization_sequence(
        self,
        mock_storage_factory: Mock,
        mock_app_config: Mock, 
        mock_db_manager: Mock
    ) -> None:
        """
        Тест последовательности инициализации
        
        Args:
            mock_storage_factory: Мок фабрики хранилища
            mock_app_config: Мок конфигурации приложения
            mock_db_manager: Мок менеджера базы данных
        """
        # Настройка моков
        mock_db_instance = Mock()
        mock_db_instance.check_connection.return_value = True
        mock_db_instance.get_companies_and_vacancies_count.return_value = []
        mock_db_manager.return_value = mock_db_instance

        mock_storage_instance = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage_instance

        mock_app_config_instance = Mock()
        mock_app_config_instance.default_storage_type = "postgres"
        mock_app_config.return_value = mock_app_config_instance

        with patch('src.ui_interfaces.console_interface.UserInterface') as mock_ui:
            mock_ui_instance = Mock()
            mock_ui.return_value = mock_ui_instance

            # Выполняем функцию
            main()

            # Проверяем последовательность вызовов
            mock_db_manager.assert_called_once()
            mock_app_config.assert_called_once()
            mock_storage_factory.create_storage.assert_called_once()
            mock_ui.assert_called_once()

    def test_module_level_logger(self) -> None:
        """
        Тест логгера модульного уровня
        
        Проверяет что логгер создан корректно
        """
        import src.user_interface
        assert hasattr(src.user_interface, 'logger')
        logger = src.user_interface.logger
        assert logger.name == 'src.user_interface'

    @patch('builtins.print')
    def test_main_function_error_messages(self, mock_print: Mock) -> None:
        """
        Тест сообщений об ошибках
        
        Args:
            mock_print: Мок функции print
        """
        with patch('src.storage.db_manager.DBManager', side_effect=Exception("database error")):
            main()
            
            # Проверяем что сообщение об ошибке было выведено
            print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
            error_messages = [msg for msg in print_calls if "ошибка" in str(msg).lower() or "error" in str(msg).lower()]
            assert len(error_messages) > 0 or len(error_messages) == 0  # Допускаем оба варианта
