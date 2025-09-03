"""
Тесты для главного модуля пользовательского интерфейса
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch
import pytest

# Мокаем psycopg2 перед импортом
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.sql'] = MagicMock()

# Добавляем путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import user_interface


class TestUserInterface:
    """Тесты модуля user_interface"""
    
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.DBManager')
    def test_main_success(self, mock_db_manager_class, mock_app_config_class, 
                         mock_storage_factory, mock_user_interface_class):
        """Тест успешного запуска основной функции"""
        # Настройка моков
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [('Test Company', 5)]
        mock_db_manager_class.return_value = mock_db_manager
        
        mock_app_config = Mock()
        mock_app_config.default_storage_type = 'postgres'
        mock_app_config_class.return_value = mock_app_config
        
        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage
        
        mock_ui = Mock()
        mock_user_interface_class.return_value = mock_ui
        
        # Тестируем
        user_interface.main()
        
        # Проверяем вызовы
        mock_db_manager.check_connection.assert_called_once()
        mock_db_manager.create_tables.assert_called_once()
        mock_db_manager.populate_companies_table.assert_called_once()
        mock_db_manager.get_companies_and_vacancies_count.assert_called_once()
        mock_storage_factory.create_storage.assert_called_once_with('postgres')
        mock_user_interface_class.assert_called_once_with(mock_storage, db_manager=mock_db_manager)
        mock_ui.run.assert_called_once()
    
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.DBManager')
    def test_main_db_connection_fails(self, mock_db_manager_class, mock_app_config_class, 
                                     mock_storage_factory, mock_user_interface_class):
        """Тест обработки ошибки подключения к БД"""
        # Настройка моков
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = False
        mock_db_manager_class.return_value = mock_db_manager
        
        # Тестируем
        user_interface.main()
        
        # Проверяем что подключение проверялось, но дальше не шли
        mock_db_manager.check_connection.assert_called_once()
        mock_db_manager.create_tables.assert_not_called()
        mock_user_interface_class.assert_not_called()
    
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.DBManager')
    def test_main_create_tables_fails(self, mock_db_manager_class, mock_app_config_class, 
                                     mock_storage_factory, mock_user_interface_class):
        """Тест обработки ошибки создания таблиц"""
        # Настройка моков
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.side_effect = Exception("Table creation failed")
        mock_db_manager_class.return_value = mock_db_manager
        
        # Тестируем
        user_interface.main()
        
        # Проверяем что попытались создать таблицы, но дальше не шли
        mock_db_manager.check_connection.assert_called_once()
        mock_db_manager.create_tables.assert_called_once()
        mock_user_interface_class.assert_not_called()
    
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.DBManager')
    def test_main_populate_companies_fails(self, mock_db_manager_class, mock_app_config_class, 
                                          mock_storage_factory, mock_user_interface_class):
        """Тест обработки ошибки заполнения таблицы компаний"""
        # Настройка моков
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.side_effect = Exception("Population failed")
        mock_db_manager_class.return_value = mock_db_manager
        
        # Тестируем
        user_interface.main()
        
        # Проверяем что попытались заполнить таблицы, но дальше не шли
        mock_db_manager.check_connection.assert_called_once()
        mock_db_manager.create_tables.assert_called_once()
        mock_db_manager.populate_companies_table.assert_called_once()
        mock_user_interface_class.assert_not_called()
    
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.DBManager')
    def test_main_initialization_check_fails(self, mock_db_manager_class, mock_app_config_class, 
                                            mock_storage_factory, mock_user_interface_class):
        """Тест обработки ошибки проверки инициализации БД"""
        # Настройка моков
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.side_effect = Exception("Check failed")
        mock_db_manager_class.return_value = mock_db_manager
        
        # Тестируем
        user_interface.main()
        
        # Проверяем что попытались проверить инициализацию, но дальше не шли
        mock_db_manager.check_connection.assert_called_once()
        mock_db_manager.create_tables.assert_called_once()
        mock_db_manager.populate_companies_table.assert_called_once()
        mock_db_manager.get_companies_and_vacancies_count.assert_called_once()
        mock_user_interface_class.assert_not_called()
    
    @patch('builtins.print')
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.DBManager')
    def test_main_keyboard_interrupt(self, mock_db_manager_class, mock_app_config_class, 
                                    mock_storage_factory, mock_user_interface_class, mock_print):
        """Тест обработки прерывания пользователем"""
        # Настройка моков
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [('Test Company', 5)]
        mock_db_manager_class.return_value = mock_db_manager
        
        mock_app_config = Mock()
        mock_app_config.default_storage_type = 'postgres'
        mock_app_config_class.return_value = mock_app_config
        
        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage
        
        mock_ui = Mock()
        mock_ui.run.side_effect = KeyboardInterrupt()
        mock_user_interface_class.return_value = mock_ui
        
        # Тестируем
        user_interface.main()
        
        # Проверяем что напечатали сообщение о прерывании
        mock_print.assert_called_with("\\n\\nРабота прервана пользователем. До свидания!")
    
    @patch('builtins.print')
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.DBManager')
    def test_main_database_error_handling(self, mock_db_manager_class, mock_app_config_class, 
                                         mock_storage_factory, mock_user_interface_class, mock_print):
        """Тест обработки ошибок базы данных"""
        # Настройка моков
        mock_db_manager = Mock()
        mock_db_manager.check_connection.side_effect = Exception("Ошибка подключения к базе данных")
        mock_db_manager_class.return_value = mock_db_manager
        
        # Тестируем
        user_interface.main()
        
        # Проверяем что напечатали информацию об ошибке БД
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("базы данных" in call.lower() or "database" in call.lower() for call in print_calls)
    
    @patch('builtins.print')
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    @patch('src.user_interface.DBManager')
    def test_main_general_error_handling(self, mock_db_manager_class, mock_app_config_class, 
                                        mock_storage_factory, mock_user_interface_class, mock_print):
        """Тест обработки общих ошибок"""
        # Настройка моков
        mock_db_manager = Mock()
        mock_db_manager.check_connection.side_effect = Exception("General error")
        mock_db_manager_class.return_value = mock_db_manager
        
        # Тестируем
        user_interface.main()
        
        # Проверяем что напечатали общее сообщение об ошибке
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("разработчику" in call.lower() for call in print_calls)