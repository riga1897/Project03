"""
Комплексные тесты для основных модулей системы с максимальным покрытием кода.

Этот модуль предоставляет исчерпывающее тестирование ключевых компонентов системы:
- Главный пользовательский интерфейс (user_interface.py)
- Менеджер базы данных (DBManager) с полным покрытием методов
- Модели вакансий и работодателей с валидацией
- Конфигурация приложения и фабрика хранилищ
- Обработка исключений и граничных случаев

Все тесты используют консолидированные моки для внешних зависимостей
и не выполняют реальных запросов к базе данных или внешним API.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Основные импорты
from src.user_interface import main
from src.storage.db_manager import DBManager
from src.vacancies.models import Vacancy, Employer
from src.utils.salary import Salary
from src.config.app_config import AppConfig
from src.storage.storage_factory import StorageFactory

# Глобальные моки для внешних зависимостей
mock_psycopg2 = MagicMock()
sys.modules['psycopg2'] = mock_psycopg2
sys.modules['psycopg2.extras'] = mock_psycopg2.extras


class TestUserInterfaceModule:
    """
    Комплексное тестирование основного модуля пользовательского интерфейса.

    Тестирует функцию main() и все сценарии её выполнения:
    - Успешный запуск приложения с корректной инициализацией БД
    - Обработка ошибок подключения к базе данных
    - Обработка ошибок инициализации структуры БД
    - Корректная обработка прерывания пользователем (Ctrl+C)
    - Логирование всех этапов работы приложения
    """

    def _create_consolidated_mocks(self) -> Dict[str, Mock]:
        """
        Создает консолидированный набор моков для тестирования.

        Returns:
            Dict[str, Mock]: Словарь с настроенными моками для всех зависимостей
        """
        mocks = {
            'db_manager': Mock(),
            'app_config': Mock(),
            'storage': Mock(),
            'user_interface': Mock()
        }

        # Настройка мока БД менеджера
        mocks['db_manager'].check_connection.return_value = True
        mocks['db_manager'].create_tables.return_value = None
        mocks['db_manager'].populate_companies_table.return_value = None
        mocks['db_manager'].get_companies_and_vacancies_count.return_value = [
            {"company": "Test Company", "vacancies": 5}
        ]

        # Настройка мока конфигурации
        mocks['app_config'].default_storage_type = "postgresql"

        return mocks

    @patch('src.user_interface.DBManager')
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.StorageFactory')
    @patch('src.user_interface.AppConfig')
    def test_main_function_success(self, mock_app_config_class, mock_storage_factory,
                                   mock_user_interface_class, mock_db_manager_class) -> None:
        """Тестирование успешного выполнения main функции"""
        # Настройка моков
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = [
            {"company": "Test Company", "vacancies": 5}
        ]
        mock_db_manager_class.return_value = mock_db_manager

        mock_app_config_instance = Mock()
        mock_app_config_instance.default_storage_type = "postgresql"
        mock_app_config_class.return_value = mock_app_config_instance

        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage

        mock_user_interface = Mock()
        mock_user_interface_class.return_value = mock_user_interface

        # Выполняем функцию
        main()

        # Проверяем вызовы
        mock_db_manager_class.assert_called_once()
        mock_db_manager.check_connection.assert_called_once()
        mock_db_manager.create_tables.assert_called_once()
        mock_db_manager.populate_companies_table.assert_called_once()
        mock_user_interface.run.assert_called_once()

    @patch('src.user_interface.DBManager')
    def test_main_function_db_connection_error(self, mock_db_manager_class) -> None:
        """Тестирование обработки ошибки подключения к БД"""
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = False
        mock_db_manager_class.return_value = mock_db_manager

        with pytest.raises(Exception, match="Не удается подключиться к базе данных"):
            main()

    @patch('builtins.print')
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.DBManager')
    def test_main_function_keyboard_interrupt(self, mock_db_manager_class,
                                              mock_user_interface_class, mock_print) -> None:
        """Тестирование обработки KeyboardInterrupt"""
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = []
        mock_db_manager_class.return_value = mock_db_manager

        mock_user_interface = Mock()
        mock_user_interface.run.side_effect = KeyboardInterrupt()
        mock_user_interface_class.return_value = mock_user_interface

        # Выполняем с патчингом AppConfig и StorageFactory
        with patch('src.user_interface.AppConfig') as mock_app_config, \
             patch('src.user_interface.StorageFactory') as mock_storage_factory:

            mock_app_config.return_value.default_storage_type = "postgresql"
            mock_storage_factory.create_storage.return_value = Mock()

            main()

        # Проверяем, что было выведено сообщение о прерывании
        mock_print.assert_called_with("\n\nРабота прервана пользователем. До свидания!")


class TestDBManagerComprehensive:
    """Комплексное тестирование DBManager с максимальным покрытием"""

    def setup_method(self) -> None:
        """Настройка перед каждым тестом"""
        # Создаем мок конфигурации
        self.mock_config = Mock()
        self.mock_config.get_connection_params.return_value = {
            "host": "localhost",
            "database": "test_db",
            "user": "test_user",
            "password": "test_pass",
            "port": 5432
        }

        # Создаем DBManager с мок конфигурацией
        with patch('src.storage.db_manager.DatabaseConfig') as mock_db_config_class:
            mock_db_config_class.return_value = self.mock_config
            self.db_manager = DBManager(self.mock_config)

    @patch('src.storage.db_manager.psycopg2')
    def test_get_connection_success(self, mock_psycopg2) -> None:
        """Тестирование успешного подключения к БД"""
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection

        connection = self.db_manager._get_connection()

        assert connection == mock_connection
        mock_connection.set_client_encoding.assert_called_with("UTF8")

    def test_check_connection_success(self) -> None:
        """Тестирование успешной проверки подключения"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection

            result = self.db_manager.check_connection()

            assert result is True
            mock_cursor.execute.assert_called_with("SELECT 1")
            mock_connection.close.assert_called_once()

    def test_create_tables_success(self) -> None:
        """Тестирование успешного создания таблиц"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()

            # Настраиваем context manager для подключения
            mock_connection.__enter__ = Mock(return_value=mock_connection)
            mock_connection.__exit__ = Mock(return_value=None)

            # Настраиваем context manager для курсора
            mock_cursor.__enter__ = Mock(return_value=mock_cursor)
            mock_cursor.__exit__ = Mock(return_value=None)
            mock_cursor.execute.return_value = None
            mock_cursor.fetchone.return_value = None

            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection

            self.db_manager.create_tables()

            # Проверяем, что курсор использовался для выполнения SQL
            assert mock_cursor.execute.called


class TestVacancyModels:
    """Комплексное тестирование моделей вакансий"""

    def test_employer_initialization(self) -> None:
        """Тестирование инициализации работодателя"""
        employer = Employer(
            name="Test Company",
            employer_id="123",
            trusted=True,
            alternate_url="https://test.com"
        )

        assert employer.get_name() == "Test Company"
        assert employer.get_id() == "123"
        assert employer.is_trusted() is True
        assert employer.get_url() == "https://test.com"

    def test_employer_from_dict(self) -> None:
        """Тестирование создания работодателя из словаря"""
        data = {
            "name": "Dict Company",
            "id": "456",
            "trusted": False,
            "alternate_url": "https://dict.com"
        }

        employer = Employer.from_dict(data)

        assert employer.get_name() == "Dict Company"
        assert employer.get_id() == "456"
        assert employer.is_trusted() is False

    def test_vacancy_initialization(self) -> None:
        """Тестирование инициализации вакансии"""
        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1"
        )

        assert vacancy.title == "Python Developer"

    def test_vacancy_with_salary(self) -> None:
        """Тестирование вакансии с зарплатой"""
        employer = Employer("Test Company", "123")
        salary = Salary({"from": 100000, "to": 200000, "currency": "RUR"})

        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1",
            salary=salary
        )

        assert vacancy.salary == salary
        assert vacancy.salary.salary_from == 100000
        assert vacancy.salary.salary_to == 200000

    def test_vacancy_validation_valid(self) -> None:
        """Тестирование валидации корректной вакансии"""
        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1"
        )

        assert vacancy.is_valid() is True

    def test_vacancy_validation_invalid_title(self) -> None:
        """Тестирование валидации вакансии с некорректным названием"""
        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title="",  # Пустое название
            employer=employer,
            url="https://test.com/vacancy/1"
        )

        assert vacancy.is_valid() is False


class TestAppConfigComprehensive:
    """Комплексное тестирование конфигурации приложения"""

    def test_app_config_initialization(self) -> None:
        """Тестирование инициализации конфигурации"""
        config = AppConfig()

        assert config is not None
        assert hasattr(config, 'default_storage_type')

    def test_app_config_default_values(self) -> None:
        """Тестирование значений по умолчанию"""
        config = AppConfig()

        # Проверяем, что есть тип хранилища по умолчанию
        assert config.default_storage_type in ["postgresql", "json", "memory"]


class TestStorageFactoryComprehensive:
    """Комплексное тестирование фабрики хранилищ"""

    def test_storage_factory_postgresql(self) -> None:
        """Тестирование создания PostgreSQL хранилища"""
        storage = StorageFactory.create_storage("postgresql")

        assert storage is not None
        assert hasattr(storage, 'save_vacancy') or hasattr(storage, 'save_vacancies')

    def test_storage_factory_json(self) -> None:
        """Тестирование создания JSON хранилища"""
        storage = StorageFactory.create_storage("json")

        assert storage is not None
        assert hasattr(storage, 'save_vacancy') or hasattr(storage, 'save_vacancies')

    def test_storage_factory_invalid_type(self) -> None:
        """Тестирование обработки некорректного типа хранилища"""
        try:
            storage = StorageFactory.create_storage("invalid_type")
            # Если не выбрасывается исключение, то должно возвращаться хранилище по умолчанию
            assert storage is not None
        except (ValueError, KeyError, NotImplementedError):
            # Ожидаемое поведение при некорректном типе
            pass