#!/usr/bin/env python3
"""
Тесты для модуля user_interface.py
"""

import logging
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.config.app_config import AppConfig
from src.storage.storage_factory import StorageFactory
from src.storage.db_manager import DBManager
from src.ui_interfaces.console_interface import UserInterface


class TestUserInterface:
    """Тесты для модуля user_interface.py"""
    
    @pytest.fixture(autouse=True)
    def setup_logging(self):
        """Настройка логирования для тестов"""
        # Сбрасываем настройки логирования
        logging.getLogger().handlers.clear()
        yield
        # Восстанавливаем
        logging.getLogger().handlers.clear()
    
    @patch('src.user_interface.logging.basicConfig')
    @patch('src.user_interface.logging.FileHandler')
    @patch('src.user_interface.logging.StreamHandler')
    def test_logging_setup(self, mock_stream_handler, mock_file_handler, mock_basic_config):
        """Тест настройки логирования"""
        mock_file_handler.return_value = Mock()
        mock_stream_handler.return_value = Mock()
        
        # Импортируем модуль заново для проверки настройки логирования
        import importlib
        import src.user_interface
        importlib.reload(src.user_interface)
        
        # Проверяем, что логирование настроено
        mock_basic_config.assert_called_once()
        mock_file_handler.assert_called_once_with("app.log")
        mock_stream_handler.assert_called_once()
    
    @patch('src.user_interface.logging.getLogger')
    def test_logger_creation(self, mock_get_logger):
        """Тест создания логгера"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        import importlib
        import src.user_interface
        importlib.reload(src.user_interface)
        
        mock_get_logger.assert_called_with(__name__)
    
    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    def test_main_function_success_flow(self, mock_user_interface, mock_storage_factory, 
                                      mock_app_config, mock_db_manager_class):
        """Тест успешного выполнения main функции"""
        # Мокаем DBManager
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [{"name": "Test Company"}]
        mock_db_manager_class.return_value = mock_db_manager
        
        # Мокаем AppConfig
        mock_config = Mock()
        mock_config.default_storage_type = "postgres"
        mock_app_config.return_value = mock_config
        
        # Мокаем StorageFactory
        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage
        
        # Мокаем UserInterface
        mock_ui = Mock()
        mock_user_interface.return_value = mock_ui
        
        # Импортируем и вызываем main функцию
        from src.user_interface import main
        
        main()
        
        # Проверяем, что все методы были вызваны
        mock_db_manager.check_connection.assert_called_once()
        mock_db_manager.create_tables.assert_called_once()
        mock_db_manager.populate_companies_table.assert_called_once()
        mock_db_manager.get_companies_and_vacancies_count.assert_called_once()
        mock_app_config.assert_called_once()
        mock_storage_factory.create_storage.assert_called_once_with("postgres")
        mock_user_interface.assert_called_once_with(mock_storage, db_manager=mock_db_manager)
        mock_ui.run.assert_called_once()
    
    @patch('src.user_interface.DBManager')
    def test_main_function_db_connection_failure(self, mock_db_manager_class):
        """Тест обработки ошибки подключения к БД"""
        # Мокаем DBManager с ошибкой подключения
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = False
        mock_db_manager_class.return_value = mock_db_manager
        
        # Мокаем print для проверки вывода
        with patch('builtins.print') as mock_print:
            with patch('src.user_interface.logger.error') as mock_logger_error:
                from src.user_interface import main
                
                with pytest.raises(Exception, match="Не удается подключиться к базе данных"):
                    main()
                
                mock_logger_error.assert_called()
    
    @patch('src.user_interface.DBManager')
    def test_main_function_db_init_failure(self, mock_db_manager_class):
        """Тест обработки ошибки инициализации БД"""
        # Мокаем DBManager с ошибкой инициализации
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.side_effect = Exception("DB init error")
        mock_db_manager_class.return_value = mock_db_manager
        
        with patch('builtins.print') as mock_print:
            with patch('src.user_interface.logger.error') as mock_logger_error:
                from src.user_interface import main
                
                with pytest.raises(Exception, match="Не удалось инициализировать структуру базы данных"):
                    main()
                
                mock_logger_error.assert_called()
    
    @patch('src.user_interface.DBManager')
    def test_main_function_db_verification_failure(self, mock_db_manager_class):
        """Тест обработки ошибки проверки инициализации БД"""
        # Мокаем DBManager с ошибкой проверки
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.side_effect = Exception("Verification error")
        mock_db_manager_class.return_value = mock_db_manager
        
        with patch('builtins.print') as mock_print:
            with patch('src.user_interface.logger.error') as mock_logger_error:
                from src.user_interface import main
                
                with pytest.raises(Exception, match="База данных не была корректно инициализирована"):
                    main()
                
                mock_logger_error.assert_called()
    
    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    def test_main_function_keyboard_interrupt(self, mock_user_interface, mock_storage_factory,
                                           mock_app_config, mock_db_manager_class):
        """Тест обработки KeyboardInterrupt"""
        # Мокаем DBManager
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [{"name": "Test Company"}]
        mock_db_manager_class.return_value = mock_db_manager
        
        # Мокаем AppConfig
        mock_config = Mock()
        mock_config.default_storage_type = "postgres"
        mock_app_config.return_value = mock_config
        
        # Мокаем StorageFactory
        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage
        
        # Мокаем UserInterface с KeyboardInterrupt
        mock_ui = Mock()
        mock_ui.run.side_effect = KeyboardInterrupt()
        mock_user_interface.return_value = mock_ui
        
        with patch('builtins.print') as mock_print:
            with patch('src.user_interface.logger.info') as mock_logger_info:
                from src.user_interface import main
                
                main()
                
                # Проверяем, что выведено сообщение о прерывании
                mock_print.assert_called_with("\n\nРабота прервана пользователем. До свидания!")
                mock_logger_info.assert_called_with("Приложение завершено пользователем")
    
    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    def test_main_function_database_error(self, mock_user_interface, mock_storage_factory,
                                        mock_app_config, mock_db_manager_class):
        """Тест обработки ошибки базы данных"""
        # Мокаем DBManager с ошибкой БД
        mock_db_manager = Mock()
        mock_db_manager.check_connection.side_effect = Exception("Database connection error")
        mock_db_manager_class.return_value = mock_db_manager
        
        with patch('builtins.print') as mock_print:
            with patch('src.user_interface.logger.error') as mock_logger_error:
                from src.user_interface import main
                
                main()
                
                # Проверяем, что выведены сообщения об ошибке БД
                mock_print.assert_any_call("Программа не может работать без базы данных. Завершение работы.")
                mock_print.assert_any_call("1. Настройки подключения в файле .env")
                mock_print.assert_any_call("2. Что PostgreSQL сервер запущен и доступен")
                mock_print.assert_any_call("3. Правильность параметров подключения")
                mock_logger_error.assert_called()
    
    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    def test_main_function_general_error(self, mock_user_interface, mock_storage_factory,
                                       mock_app_config, mock_db_manager_class):
        """Тест обработки общей ошибки"""
        # Мокаем DBManager с общей ошибкой
        mock_db_manager = Mock()
        mock_db_manager.check_connection.side_effect = Exception("General error")
        mock_db_manager_class.return_value = mock_db_manager
        
        with patch('builtins.print') as mock_print:
            with patch('src.user_interface.logger.error') as mock_logger_error:
                from src.user_interface import main
                
                main()
                
                # Проверяем, что выведено сообщение об общей ошибке
                mock_print.assert_any_call("Обратитесь к разработчику для решения проблемы.")
                mock_logger_error.assert_called()
    
    def test_main_function_return_on_error(self):
        """Тест возврата из функции при ошибке"""
        with patch('src.user_interface.DBManager') as mock_db_manager_class:
            mock_db_manager = Mock()
            mock_db_manager.check_connection.side_effect = Exception("Test error")
            mock_db_manager_class.return_value = mock_db_manager
            
            with patch('builtins.print'):
                with patch('src.user_interface.logger.error'):
                    from src.user_interface import main
                    
                    # Функция должна завершиться без исключения
                    result = main()
                    assert result is None
    
    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    def test_main_function_storage_creation(self, mock_user_interface, mock_storage_factory,
                                          mock_app_config, mock_db_manager_class):
        """Тест создания хранилища"""
        # Мокаем DBManager
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [{"name": "Test Company"}]
        mock_db_manager_class.return_value = mock_db_manager
        
        # Мокаем AppConfig
        mock_config = Mock()
        mock_config.default_storage_type = "memory"
        mock_app_config.return_value = mock_config
        
        # Мокаем StorageFactory
        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage
        
        # Мокаем UserInterface
        mock_ui = Mock()
        mock_user_interface.return_value = mock_ui
        
        with patch('src.user_interface.logger.info') as mock_logger_info:
            from src.user_interface import main
            
            main()
            
            # Проверяем создание хранилища
            mock_storage_factory.create_storage.assert_called_once_with("memory")
            mock_logger_info.assert_any_call("Используется хранилище: Mock")
    
    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.UserInterface')
    def test_main_function_user_interface_creation(self, mock_user_interface, mock_storage_factory,
                                                 mock_app_config, mock_db_manager_class):
        """Тест создания пользовательского интерфейса"""
        # Мокаем DBManager
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [{"name": "Test Company"}]
        mock_db_manager_class.return_value = mock_db_manager
        
        # Мокаем AppConfig
        mock_config = Mock()
        mock_config.default_storage_type = "postgres"
        mock_app_config.return_value = mock_config
        
        # Мокаем StorageFactory
        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage
        
        # Мокаем UserInterface
        mock_ui = Mock()
        mock_user_interface.return_value = mock_ui
        
        from src.user_interface import main
        
        main()
        
        # Проверяем создание UserInterface с правильными параметрами
        mock_user_interface.assert_called_once_with(mock_storage, db_manager=mock_db_manager)