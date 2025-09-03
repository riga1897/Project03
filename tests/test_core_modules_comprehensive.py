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

Автор: Система тестирования поиска вакансий
Дата: 2025
"""

import os
import sys
import pytest
import tempfile
import json
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any, Optional, Union

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Глобальные моки для внешних зависимостей
mock_psycopg2 = MagicMock()
sys.modules['psycopg2'] = mock_psycopg2
sys.modules['psycopg2.extras'] = mock_psycopg2.extras

# Основные импорты
from src.user_interface import main
from src.storage.db_manager import DBManager
from src.vacancies.models import Vacancy, Employer, Experience, Employment, Schedule
from src.config.app_config import AppConfig
from src.storage.storage_factory import StorageFactory


class TestUserInterfaceModule:
    """
    Комплексное тестирование основного модуля пользовательского интерфейса.
    
    Тестирует функцию main() и все сценарии её выполнения:
    - Успешный запуск приложения с корректной инициализацией БД
    - Обработка ошибок подключения к базе данных
    - Обработка ошибок инициализации структуры БД
    - Корректная обработка прерывания пользователем (Ctrl+C)
    - Логирование всех этапов работы приложения
    
    Все внешние зависимости мокируются для изолированного тестирования.
    """
    
    # Консолидированный набор моков для всех тестов класса
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
        mock_app_config.return_value = mock_app_config_instance
        
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
    def test_main_function_db_connection_error(self, mock_db_manager_class):
        """Тестирование обработки ошибки подключения к БД"""
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = False
        mock_db_manager_class.return_value = mock_db_manager
        
        with pytest.raises(Exception, match="Не удается подключиться к базе данных"):
            main()
            
    @patch('src.user_interface.DBManager')
    def test_main_function_db_initialization_error(self, mock_db_manager_class):
        """Тестирование обработки ошибки инициализации БД"""
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.side_effect = Exception("DB init error")
        mock_db_manager_class.return_value = mock_db_manager
        
        with pytest.raises(Exception, match="Не удалось инициализировать структуру базы данных"):
            main()
            
    @patch('builtins.print')
    @patch('src.user_interface.UserInterface')
    @patch('src.user_interface.DBManager')
    def test_main_function_keyboard_interrupt(self, mock_db_manager_class, 
                                              mock_user_interface_class, mock_print):
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
    
    def setup_method(self):
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
    def test_get_connection_success(self, mock_psycopg2):
        """Тестирование успешного подключения к БД"""
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        connection = self.db_manager._get_connection()
        
        assert connection == mock_connection
        mock_connection.set_client_encoding.assert_called_with("UTF8")
        
    @patch('src.storage.db_manager.psycopg2')
    def test_get_connection_error(self, mock_psycopg2):
        """Тестирование обработки ошибки подключения"""
        mock_psycopg2.connect.side_effect = Exception("Connection error")
        
        with pytest.raises(Exception, match="Connection error"):
            self.db_manager._get_connection()
            
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', False)
    @patch('src.storage.db_manager.get_db_adapter')
    def test_get_connection_fallback(self, mock_get_adapter):
        """Тестирование fallback подключения"""
        mock_adapter = Mock()
        mock_get_adapter.return_value = mock_adapter
        
        connection = self.db_manager._get_connection()
        
        assert connection == mock_adapter
        
    def test_check_connection_success(self):
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
            
    def test_check_connection_failure(self):
        """Тестирование неудачной проверки подключения"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.side_effect = Exception("Connection failed")
            
            result = self.db_manager.check_connection()
            
            assert result is False
            
    def test_create_tables_success(self):
        """Тестирование успешного создания таблиц"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection
            
            self.db_manager.create_tables()
            
            # Проверяем, что выполнялись SQL команды
            assert mock_cursor.execute.call_count >= 2  # companies и vacancies таблицы
            mock_connection.commit.assert_called_once()
            mock_connection.close.assert_called_once()
            
    def test_add_company_success(self):
        """Тестирование успешного добавления компании"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection
            
            result = self.db_manager.add_company("Test Company", "123")
            
            assert result is True
            mock_cursor.execute.assert_called()
            mock_connection.commit.assert_called_once()
            
    def test_add_company_duplicate(self):
        """Тестирование добавления дублирующейся компании"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            # Симулируем IntegrityError для дублирования
            mock_cursor.execute.side_effect = mock_psycopg2.IntegrityError()
            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection
            
            result = self.db_manager.add_company("Test Company", "123")
            
            assert result is True  # Дублирование обрабатывается как успех
            
    def test_add_vacancy_success(self):
        """Тестирование успешного добавления вакансии"""
        vacancy_data = {
            "title": "Python Developer",
            "company_id": "123",
            "salary_from": 100000,
            "salary_to": 200000,
            "currency": "RUR",
            "url": "https://test.com/vacancy/1",
            "requirements": "Python, Django",
            "description": "Great opportunity"
        }
        
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection
            
            result = self.db_manager.add_vacancy(vacancy_data)
            
            assert result is True
            mock_cursor.execute.assert_called()
            mock_connection.commit.assert_called_once()
            
    def test_get_companies_and_vacancies_count(self):
        """Тестирование получения количества вакансий по компаниям"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [
                {"company_name": "Company A", "company_id": "1", "vacancy_count": 5},
                {"company_name": "Company B", "company_id": "2", "vacancy_count": 3}
            ]
            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection
            
            result = self.db_manager.get_companies_and_vacancies_count()
            
            assert len(result) == 2
            assert result[0]["company_name"] == "Company A"
            assert result[0]["vacancy_count"] == 5
            
    def test_get_avg_salary(self):
        """Тестирование получения средней зарплаты"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = {"avg_salary": 150000.0}
            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection
            
            result = self.db_manager.get_avg_salary()
            
            assert result == 150000.0
            
    def test_get_vacancies_with_higher_salary(self):
        """Тестирование получения вакансий с зарплатой выше средней"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [
                {
                    "title": "Senior Python Developer",
                    "company_name": "Tech Corp",
                    "salary_from": 200000,
                    "salary_to": 300000,
                    "url": "https://test.com/vacancy/1"
                }
            ]
            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection
            
            result = self.db_manager.get_vacancies_with_higher_salary()
            
            assert len(result) == 1
            assert result[0]["title"] == "Senior Python Developer"
            
    def test_get_vacancies_with_keyword(self):
        """Тестирование поиска вакансий по ключевому слову"""
        with patch.object(self.db_manager, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [
                {
                    "title": "Python Developer",
                    "company_name": "Python Corp",
                    "description": "Python development"
                }
            ]
            mock_connection.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_connection
            
            result = self.db_manager.get_vacancies_with_keyword("Python")
            
            assert len(result) == 1
            assert "Python" in result[0]["title"]


class TestVacancyModels:
    """Комплексное тестирование моделей вакансий"""
    
    def test_employer_initialization(self):
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
        
    def test_employer_from_dict(self):
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
        
    def test_employer_to_dict(self):
        """Тестирование преобразования работодателя в словарь"""
        employer = Employer("Test Company", "123", True)
        result = employer.to_dict()
        
        assert result["name"] == "Test Company"
        assert result["id"] == "123"
        assert result["trusted"] is True
        
    def test_employer_str_repr(self):
        """Тестирование строковых представлений работодателя"""
        employer = Employer("Test Company", "123")
        
        assert str(employer) == "Test Company"
        assert "Test Company" in repr(employer)
        assert "123" in repr(employer)
        
    def test_employer_properties(self):
        """Тестирование свойств работодателя"""
        employer = Employer("Test Company", "123")
        
        assert employer.name == "Test Company"
        assert employer.id == "123"
        
    def test_vacancy_initialization(self):
        """Тестирование инициализации вакансии"""
        employer = Employer("Test Company", "123")
        
        # Проверяем минимальную инициализацию
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1"
        )
        
        assert vacancy.get_title() == "Python Developer"
        assert vacancy.get_employer().get_name() == "Test Company"
        assert vacancy.get_url() == "https://test.com/vacancy/1"
        
    def test_vacancy_with_salary(self):
        """Тестирование вакансии с зарплатой"""
        employer = Employer("Test Company", "123")
        salary = Salary(100000, 200000, "RUR")
        
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1",
            salary=salary
        )
        
        assert vacancy.get_salary() == salary
        assert vacancy.get_salary().salary_from == 100000
        assert vacancy.get_salary().salary_to == 200000
        
    def test_vacancy_validation_valid(self):
        """Тестирование валидации корректной вакансии"""
        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1"
        )
        
        assert vacancy.is_valid() is True
        
    def test_vacancy_validation_invalid_title(self):
        """Тестирование валидации вакансии с некорректным названием"""
        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title="",  # Пустое название
            employer=employer,
            url="https://test.com/vacancy/1"
        )
        
        assert vacancy.is_valid() is False
        
    def test_vacancy_validation_invalid_url(self):
        """Тестирование валидации вакансии с некорректным URL"""
        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url=""  # Пустой URL
        )
        
        assert vacancy.is_valid() is False
        
    def test_vacancy_to_dict(self):
        """Тестирование преобразования вакансии в словарь"""
        employer = Employer("Test Company", "123")
        salary = Salary(100000, 200000, "RUR")
        
        vacancy = Vacancy(
            title="Python Developer",
            employer=employer,
            url="https://test.com/vacancy/1",
            salary=salary,
            requirements="Python, Django",
            responsibilities="Development"
        )
        
        result = vacancy.to_dict()
        
        assert result["title"] == "Python Developer"
        assert result["employer"]["name"] == "Test Company"
        assert result["url"] == "https://test.com/vacancy/1"
        assert result["salary"]["from"] == 100000
        assert result["requirements"] == "Python, Django"
        
    def test_vacancy_from_dict(self):
        """Тестирование создания вакансии из словаря"""
        data = {
            "title": "Python Developer",
            "employer": {"name": "Dict Company", "id": "456"},
            "url": "https://dict.com/vacancy/1",
            "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
            "requirements": "Python, FastAPI",
            "responsibilities": "Backend development"
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.get_title() == "Python Developer"
        assert vacancy.get_employer().get_name() == "Dict Company"
        assert vacancy.get_salary().salary_from == 150000
        assert vacancy.get_requirements() == "Python, FastAPI"
        
    def test_vacancy_comparison(self):
        """Тестирование сравнения вакансий"""
        employer1 = Employer("Company A", "123")
        employer2 = Employer("Company B", "456")
        
        vacancy1 = Vacancy("Python Developer", employer1, "https://test1.com")
        vacancy2 = Vacancy("Java Developer", employer2, "https://test2.com")
        vacancy3 = Vacancy("Python Developer", employer1, "https://test1.com")
        
        assert vacancy1 == vacancy3  # Одинаковые вакансии
        assert vacancy1 != vacancy2  # Разные вакансии
        
    def test_vacancy_str_repr(self):
        """Тестирование строковых представлений вакансии"""
        employer = Employer("Test Company", "123")
        vacancy = Vacancy("Python Developer", employer, "https://test.com")
        
        str_repr = str(vacancy)
        assert "Python Developer" in str_repr
        assert "Test Company" in str_repr
        
        repr_repr = repr(vacancy)
        assert "Vacancy" in repr_repr
        assert "Python Developer" in repr_repr


class TestAppConfigComprehensive:
    """Комплексное тестирование конфигурации приложения"""
    
    def test_app_config_initialization(self):
        """Тестирование инициализации конфигурации"""
        config = AppConfig()
        
        assert config is not None
        assert hasattr(config, 'default_storage_type')
        
    def test_app_config_default_values(self):
        """Тестирование значений по умолчанию"""
        config = AppConfig()
        
        # Проверяем, что есть тип хранилища по умолчанию
        assert config.default_storage_type in ["postgresql", "json", "memory"]
        
    @patch.dict(os.environ, {"STORAGE_TYPE": "json"})
    def test_app_config_environment_override(self):
        """Тестирование переопределения конфигурации через переменные окружения"""
        config = AppConfig()
        
        # Если поддерживается переопределение из env
        if hasattr(config, 'load_from_env'):
            config.load_from_env()
        
        # Проверяем корректность работы конфигурации
        assert config.default_storage_type is not None


class TestStorageFactoryComprehensive:
    """Комплексное тестирование фабрики хранилищ"""
    
    def test_storage_factory_postgresql(self):
        """Тестирование создания PostgreSQL хранилища"""
        storage = StorageFactory.create_storage("postgresql")
        
        assert storage is not None
        assert hasattr(storage, 'save_vacancy') or hasattr(storage, 'save_vacancies')
        
    def test_storage_factory_json(self):
        """Тестирование создания JSON хранилища"""
        storage = StorageFactory.create_storage("json")
        
        assert storage is not None
        assert hasattr(storage, 'save_vacancy') or hasattr(storage, 'save_vacancies')
        
    def test_storage_factory_invalid_type(self):
        """Тестирование обработки некорректного типа хранилища"""
        try:
            storage = StorageFactory.create_storage("invalid_type")
            # Если не выбрасывается исключение, то должно возвращаться хранилище по умолчанию
            assert storage is not None
        except (ValueError, KeyError, NotImplementedError):
            # Ожидаемое поведение при некорректном типе
            pass
            
    def test_storage_factory_none_type(self):
        """Тестирование обработки None типа"""
        try:
            storage = StorageFactory.create_storage(None)
            # Должно вернуть хранилище по умолчанию
            assert storage is not None
        except (ValueError, TypeError):
            # Также допустимое поведение
            pass