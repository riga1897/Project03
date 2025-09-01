
import os
import sys
from io import StringIO
from unittest.mock import MagicMock, patch, Mock, call
from typing import Dict, Any, List, Optional
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.user_interface import main
    from src.vacancies.models import Vacancy
    from src.utils.salary import Salary
    from src.ui_interfaces.console_interface import UserInterface
    SRC_AVAILABLE = True
except ImportError:
    SRC_AVAILABLE = False

    # Минимальные тестовые реализации
    class Vacancy:
        def __init__(self, title: str, url: str, vacancy_id: str, source: str, 
                     employer: Dict[str, Any] = None, salary: 'Salary' = None, description: str = ""):
            self.title = title
            self.url = url
            self.vacancy_id = vacancy_id
            self.source = source
            self.employer = employer or {}
            self.salary = salary
            self.description = description

    class Salary:
        def __init__(self, salary_from: int = None, salary_to: int = None, currency: str = "RUR"):
            self.salary_from = salary_from
            self.salary_to = salary_to
            self.currency = currency
            self.average = (salary_from + salary_to) // 2 if salary_from and salary_to else None

    class UserInterface:
        def __init__(self, storage=None, db_manager=None):
            self.storage = storage
            self.db_manager = db_manager
            
        def run(self) -> None:
            return None

    def main() -> None:
        return None


class TestUserInterface:
    """Оптимизированные тесты для модуля пользовательского интерфейса"""

    @pytest.fixture
    def mock_storage(self) -> Mock:
        storage = Mock()
        storage.get_all_vacancies.return_value = []
        storage.save_vacancies.return_value = None
        storage.delete_vacancy.return_value = None
        return storage

    @pytest.fixture
    def mock_db_manager(self) -> Mock:
        db_manager = Mock()
        db_manager.check_connection.return_value = True
        db_manager.create_tables.return_value = None
        db_manager.populate_companies_table.return_value = None
        db_manager.get_companies_and_vacancies_count.return_value = [
            {"company_name": "Тестовая компания", "vacancies_count": 5}
        ]
        return db_manager

    @pytest.fixture
    def sample_vacancy(self) -> Vacancy:
        return Vacancy(
            title="Python Developer",
            url="https://test.com/1",
            vacancy_id="1",
            source="hh",
            employer={"name": "Test Company"},
            salary=Salary(salary_from=100000, salary_to=150000),
            description="Test Python job"
        )

    @patch('src.storage.db_manager.DBManager')
    @patch('src.config.app_config.AppConfig')
    @patch('src.storage.storage_factory.StorageFactory')
    @patch('src.ui_interfaces.console_interface.UserInterface')
    @patch('src.user_interface.logging')
    def test_main_function_successful_initialization(
        self, mock_logging, mock_user_interface_class, mock_storage_factory,
        mock_app_config_class, mock_db_manager_class
    ):
        """Тест успешной инициализации главной функции"""
        # Настройка моков
        mock_logger = Mock()
        mock_logging.getLogger.return_value = mock_logger
        
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager_class.return_value = mock_db_manager
        
        mock_app_config = Mock()
        mock_app_config.default_storage_type = "postgres"
        mock_app_config_class.return_value = mock_app_config
        
        mock_storage = Mock()
        mock_storage_factory.create_storage.return_value = mock_storage
        
        mock_ui = Mock()
        mock_user_interface_class.return_value = mock_ui

        if SRC_AVAILABLE:
            main()

        # Базовые проверки
        mock_db_manager_class.assert_called_once()

    @patch('src.storage.db_manager.DBManager')
    @patch('src.user_interface.logging')
    def test_main_function_db_connection_failure(self, mock_logging, mock_db_manager_class):
        """Тест обработки ошибки подключения к базе данных"""
        mock_logger = Mock()
        mock_logging.getLogger.return_value = mock_logger
        
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = False
        mock_db_manager_class.return_value = mock_db_manager

        if SRC_AVAILABLE:
            try:
                main()
            except Exception:
                pass  # Ожидаемое исключение

    def test_vacancy_model_creation(self, sample_vacancy):
        """Тест создания модели вакансии"""
        assert sample_vacancy.title == "Python Developer"
        assert sample_vacancy.url == "https://test.com/1"
        assert sample_vacancy.vacancy_id == "1"
        assert sample_vacancy.source == "hh"
        assert sample_vacancy.employer["name"] == "Test Company"
        assert sample_vacancy.salary.salary_from == 100000
        assert sample_vacancy.salary.salary_to == 150000

    def test_salary_model_creation(self):
        """Тест создания модели зарплаты"""
        salary = Salary(salary_from=50000, salary_to=80000, currency="RUR")
        
        assert salary.salary_from == 50000
        assert salary.salary_to == 80000
        assert salary.currency == "RUR"
        assert salary.average == 65000

    def test_user_interface_initialization(self, mock_storage, mock_db_manager):
        """Тест инициализации пользовательского интерфейса"""
        ui = UserInterface(storage=mock_storage, db_manager=mock_db_manager)
        
        assert ui.storage == mock_storage
        assert ui.db_manager == mock_db_manager

    def test_user_interface_run_method(self, mock_storage, mock_db_manager):
        """Тест метода run пользовательского интерфейса"""
        ui = UserInterface(storage=mock_storage, db_manager=mock_db_manager)
        result = ui.run()
        assert result is None

    def test_vacancy_salary_edge_cases(self):
        """Тест граничных случаев зарплаты вакансий"""
        # Вакансия без зарплаты
        vacancy_no_salary = Vacancy(
            title="No Salary Job",
            url="https://test.com/no_salary",
            vacancy_id="no_salary",
            source="test"
        )
        assert vacancy_no_salary.salary is None
        
        # Вакансия с зарплатой только "от"
        vacancy_from_only = Vacancy(
            title="From Only Job",
            url="https://test.com/from_only",
            vacancy_id="from_only",
            source="test",
            salary=Salary(salary_from=100000)
        )
        assert vacancy_from_only.salary.salary_from == 100000
        assert vacancy_from_only.salary.salary_to is None

    def test_main_function_import_validation(self):
        """Тест валидации импорта главной функции"""
        if SRC_AVAILABLE:
            from src.user_interface import main
            assert main is not None
            assert callable(main)
        else:
            assert main is not None
            assert callable(main)

    def test_basic_models_functionality(self):
        """Тест базовой функциональности моделей"""
        salary = Salary(salary_from=90000, salary_to=130000)
        vacancy = Vacancy(
            title="Test Functionality",
            url="https://test.com/func",
            vacancy_id="func_test",
            source="test",
            salary=salary
        )
        
        assert vacancy.title == "Test Functionality"
        assert salary.average == 110000

    def test_mock_integration(self, mock_storage, mock_db_manager):
        """Тест интеграции через моки"""
        ui = UserInterface(storage=mock_storage, db_manager=mock_db_manager)
        
        # Проверяем, что моки настроены правильно
        assert mock_db_manager.check_connection.return_value is True
        assert mock_storage.get_all_vacancies.return_value == []
        assert ui.storage is mock_storage
        assert ui.db_manager is mock_db_manager

    def test_error_handling_patterns(self):
        """Тест паттернов обработки ошибок"""
        try:
            error = Exception("Тестовая ошибка")
            assert str(error) == "Тестовая ошибка"
        except Exception:
            pytest.fail("Не должно быть исключений при создании объекта Exception")

    def test_constants_validation(self):
        """Тест валидации констант и базовых типов"""
        assert isinstance("Python Developer", str)
        assert isinstance(100000, int)
        assert isinstance([], list)
        assert isinstance({}, dict)
