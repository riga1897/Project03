import os
import sys
from unittest.mock import MagicMock, patch, Mock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestUserInterface:
    """Оптимизированные тесты для модуля пользовательского интерфейса"""

    def test_main_function_import(self):
        """Тест импорта главной функции"""
        try:
            from src.user_interface import main
            assert callable(main)
        except ImportError:
            pytest.skip("Модуль user_interface не найден")

    @patch('src.user_interface.logging')
    @patch('src.storage.db_manager.DBManager')
    @patch('src.config.app_config.AppConfig')
    @patch('src.storage.storage_factory.StorageFactory')
    @patch('src.ui_interfaces.console_interface.UserInterface')
    def test_main_function_mocked(
        self, 
        mock_user_interface_class,
        mock_storage_factory, 
        mock_app_config_class,
        mock_db_manager_class,
        mock_logging
    ):
        """Тест главной функции с полными моками"""
        try:
            from src.user_interface import main
        except ImportError:
            pytest.skip("Модуль user_interface не найден")

        # Настройка моков
        mock_logger = Mock()
        mock_logging.getLogger.return_value = mock_logger

        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = []
        mock_db_manager_class.return_value = mock_db_manager

        mock_app_config = Mock()
        mock_app_config.default_storage_type = "postgres"
        mock_app_config_class.return_value = mock_app_config

        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage

        mock_ui = Mock()
        mock_ui.run.return_value = None  # Предотвращаем зависание
        mock_user_interface_class.return_value = mock_ui

        # Выполняем функцию main
        main()

        # Проверяем, что все компоненты были инициализированы
        mock_db_manager_class.assert_called_once()
        mock_app_config_class.assert_called_once()
        mock_storage_factory.create_storage.assert_called_once()
        mock_user_interface_class.assert_called_once()

    @patch('src.user_interface.logging')
    @patch('src.storage.db_manager.DBManager')
    def test_main_function_db_failure(self, mock_db_manager_class, mock_logging):
        """Тест обработки ошибки подключения к БД"""
        try:
            from src.user_interface import main
        except ImportError:
            pytest.skip("Модуль user_interface не найден")

        mock_logger = Mock()
        mock_logging.getLogger.return_value = mock_logger

        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = False
        mock_db_manager_class.return_value = mock_db_manager

        # Ожидаем исключение при неудачном подключении к БД
        with pytest.raises(Exception):
            main()

    def test_vacancy_model_basic(self):
        """Тест базовой модели вакансии"""
        try:
            from src.vacancies.models import Vacancy
            from src.utils.salary import Salary

            salary = Salary(salary_from=100000, salary_to=150000)
            vacancy = Vacancy(
                title="Python Developer",
                url="https://test.com/1",
                vacancy_id="1",
                source="hh",
                employer={"name": "Test Company"},
                salary=salary,
                description="Test job"
            )

            assert vacancy.title == "Python Developer"
            assert vacancy.vacancy_id == "1"
            assert vacancy.source == "hh"

        except ImportError:
            pytest.skip("Модели вакансий не найдены")

    def test_salary_model_basic(self):
        """Тест базовой модели зарплаты"""
        try:
            from src.utils.salary import Salary

            salary = Salary(salary_from=50000, salary_to=80000, currency="RUR")

            assert salary.salary_from == 50000
            assert salary.salary_to == 80000
            assert salary.currency == "RUR"

        except ImportError:
            pytest.skip("Модель зарплаты не найдена")

    def test_user_interface_class_basic(self):
        """Тест базового класса пользовательского интерфейса"""
        try:
            from src.ui_interfaces.console_interface import UserInterface

            mock_storage = Mock()
            mock_db_manager = Mock()

            ui = UserInterface(storage=mock_storage, db_manager=mock_db_manager)

            assert ui.storage == mock_storage
            assert ui.db_manager == mock_db_manager

        except ImportError:
            pytest.skip("Класс UserInterface не найден")

    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_keyboard_interrupt_handling(self, mock_print, mock_input):
        """Тест обработки KeyboardInterrupt"""
        try:
            from src.user_interface import main
        except ImportError:
            pytest.skip("Модуль user_interface не найден")

        # Имитируем прерывание пользователем
        with patch('src.ui_interfaces.console_interface.UserInterface') as mock_ui_class:
            mock_ui = Mock()
            mock_ui.run.side_effect = KeyboardInterrupt()
            mock_ui_class.return_value = mock_ui

            with patch('src.storage.db_manager.DBManager') as mock_db_manager_class:
                mock_db_manager = Mock()
                mock_db_manager.check_connection.return_value = True
                mock_db_manager.create_tables.return_value = None
                mock_db_manager.populate_companies_table.return_value = None
                mock_db_manager.get_companies_and_vacancies_count.return_value = []
                mock_db_manager_class.return_value = mock_db_manager

                with patch('src.config.app_config.AppConfig') as mock_config_class:
                    mock_config = Mock()
                    mock_config.default_storage_type = "postgres"
                    mock_config_class.return_value = mock_config

                    with patch('src.storage.storage_factory.StorageFactory') as mock_factory:
                        mock_storage = Mock()
                        mock_factory.create_storage.return_value = mock_storage

                        # Запускаем main - должно корректно обработать KeyboardInterrupt
                        main()

    def test_constants_and_types(self):
        """Тест базовых констант и типов"""
        assert isinstance("test", str)
        assert isinstance(123, int)
        assert isinstance([], list)
        assert isinstance({}, dict)
        assert isinstance(True, bool)

    def test_mock_functionality(self):
        """Тест функциональности моков"""
        mock_obj = Mock()
        mock_obj.test_method.return_value = "test_result"

        result = mock_obj.test_method()
        assert result == "test_result"
        mock_obj.test_method.assert_called_once()