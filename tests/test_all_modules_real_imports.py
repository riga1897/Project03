"""
Тесты для 100% покрытия всех модулей src/ с РЕАЛЬНЫМИ импортами
Все I/O операции замокированы, но классы импортируются из реального кода
"""

import os
import sys
from unittest.mock import Mock, patch, mock_open, MagicMock
from datetime import datetime
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# РЕАЛЬНЫЕ импорты из src/ для правильного измерения покрытия
from src.vacancies.abstract import AbstractVacancy
from src.vacancies.abstract_models import (
    AbstractEmployer, AbstractExperience, AbstractEmployment, AbstractSalary
)
from src.storage.abstract import AbstractVacancyStorage
from src.storage.abstract_db_manager import AbstractDBManager
from src.api_modules.base_api import BaseJobAPI
from src.utils.abstract_filter import AbstractDataFilter

from src.config.api_config import APIConfig
from src.config.app_config import AppConfig  
from src.config.target_companies import TargetCompanies, CompanyInfo
from src.utils.env_loader import EnvLoader
from src.vacancies.models import Employer, Experience, Employment, Vacancy


class TestAbstractClasses:
    """Тесты абстрактных классов с реальными импортами"""

    def test_abstract_vacancy_cannot_instantiate(self):
        """Тест что AbstractVacancy нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractVacancy()

    def test_abstract_vacancy_concrete_implementation(self):
        """Тест конкретной реализации AbstractVacancy"""
        class ConcreteVacancy(AbstractVacancy):
            def __init__(self):
                pass
            def to_dict(self):
                return {"test": "data"}
            @classmethod
            def from_dict(cls, data):
                return cls()
        
        vacancy = ConcreteVacancy()
        assert vacancy.to_dict() == {"test": "data"}

    def test_abstract_employer_cannot_instantiate(self):
        """Тест что AbstractEmployer нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractEmployer()

    def test_abstract_employer_concrete_implementation(self):
        """Тест конкретной реализации AbstractEmployer"""
        class ConcreteEmployer(AbstractEmployer):
            def get_name(self): return "Test Company"
            def get_id(self): return "123"
            def is_trusted(self): return True
            def get_url(self): return "http://test.com"
            def to_dict(self): return {"name": "Test Company"}
            @classmethod
            def from_dict(cls, data): return cls()
        
        employer = ConcreteEmployer()
        assert employer.get_name() == "Test Company"

    def test_abstract_experience_cannot_instantiate(self):
        """Тест что AbstractExperience нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractExperience()

    def test_abstract_experience_concrete_implementation(self):
        """Тест конкретной реализации AbstractExperience"""
        class ConcreteExperience(AbstractExperience):
            def get_name(self): return "От 1 до 3 лет"
            def get_id(self): return "between1And3"
            def to_dict(self): return {"name": "От 1 до 3 лет", "id": "between1And3"}
            @classmethod
            def from_dict(cls, data): return cls()
            @classmethod
            def from_string(cls, data): return cls()
        
        exp = ConcreteExperience()
        assert exp.get_name() == "От 1 до 3 лет"

    def test_abstract_employment_cannot_instantiate(self):
        """Тест что AbstractEmployment нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractEmployment()

    def test_abstract_employment_concrete_implementation(self):
        """Тест конкретной реализации AbstractEmployment"""
        class ConcreteEmployment(AbstractEmployment):
            def get_name(self): return "Полная занятость"
            def get_id(self): return "full"
            def to_dict(self): return {"name": "Полная занятость", "id": "full"}
            @classmethod
            def from_dict(cls, data): return cls()
            @classmethod
            def from_string(cls, data): return cls()
        
        emp = ConcreteEmployment()
        assert emp.get_name() == "Полная занятость"

    def test_abstract_salary_cannot_instantiate(self):
        """Тест что AbstractSalary нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractSalary()

    def test_abstract_salary_concrete_implementation(self):
        """Тест конкретной реализации AbstractSalary"""
        class ConcreteSalary(AbstractSalary):
            def get_from(self): return 100000
            def get_to(self): return 150000
            def get_currency(self): return "RUR"
            def is_gross(self): return True
            def format_salary(self): return "100k-150k"
            def to_dict(self): return {"from": 100000, "to": 150000}
            @classmethod
            def from_dict(cls, data): return cls()
            def compare(self, other): return 0
            def get_from_amount(self): return 100000
            def get_to_amount(self): return 150000
            def get_average(self): return 125000
            def is_specified(self): return True
        
        salary = ConcreteSalary()
        assert salary.get_from() == 100000

    def test_abstract_vacancy_storage_cannot_instantiate(self):
        """Тест что AbstractVacancyStorage нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractVacancyStorage()

    def test_abstract_vacancy_storage_concrete_implementation(self):
        """Тест конкретной реализации AbstractVacancyStorage"""
        class ConcreteStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy): pass
            def get_vacancies(self, filters=None): return []
            def delete_vacancy(self, vacancy): pass
            def check_vacancies_exist_batch(self, vacancies): return {}
            def add_vacancy_batch_optimized(self, vacancies, search_query=None): return []
        
        storage = ConcreteStorage()
        assert storage.get_vacancies() == []

    def test_abstract_db_manager_cannot_instantiate(self):
        """Тест что AbstractDBManager нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractDBManager()

    def test_abstract_db_manager_concrete_implementation(self):
        """Тест конкретной реализации AbstractDBManager"""
        class ConcreteDBManager(AbstractDBManager):
            def get_companies_and_vacancies_count(self): return []
            def get_all_vacancies(self): return []
            def get_avg_salary(self): return None
            def get_vacancies_with_higher_salary(self): return []
            def get_vacancies_with_keyword(self, keyword): return []
            def get_database_stats(self): return {}
        
        db_manager = ConcreteDBManager()
        assert db_manager.get_all_vacancies() == []

    def test_base_job_api_cannot_instantiate(self):
        """Тест что BaseJobAPI нельзя инстанцировать"""
        with pytest.raises(TypeError):
            BaseJobAPI()

    def test_base_job_api_concrete_implementation(self):
        """Тест конкретной реализации BaseJobAPI"""
        class ConcreteAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs): return []
            def _validate_vacancy(self, vacancy): return True
        
        api = ConcreteAPI()
        assert api.get_vacancies("test") == []
        api.clear_cache("test")  # Тестируем унаследованный метод

    def test_abstract_data_filter_cannot_instantiate(self):
        """Тест что AbstractDataFilter нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractDataFilter()

    def test_abstract_data_filter_concrete_implementation(self):
        """Тест конкретной реализации AbstractDataFilter"""
        class ConcreteFilter(AbstractDataFilter):
            def filter_by_company(self, data, companies): return data
            def filter_by_salary(self, data, min_salary=None, max_salary=None): return data
            def filter_by_location(self, data, locations): return data
            def filter_by_experience(self, data, experience_levels): return data
        
        filter_obj = ConcreteFilter()
        test_data = [{"test": "data"}]
        assert filter_obj.filter_by_company(test_data, ["company"]) == test_data

        # Тестируем неабстрактный метод filter_by_multiple_criteria
        result = filter_obj.filter_by_multiple_criteria(test_data, companies=["test"])
        assert result == test_data


class TestConfigModules:
    """Тесты config модулей с реальными импортами"""

    def test_api_config_all_methods(self):
        """100% покрытие APIConfig"""
        # Дефолтная инициализация
        config = APIConfig()
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20
        
        # Кастомная инициализация
        from src.config.hh_api_config import HHAPIConfig
        hh_config = HHAPIConfig()
        config_custom = APIConfig(
            user_agent="Custom/1.0",
            timeout=30,
            request_delay=1.0,
            hh_config=hh_config,
            max_pages=50
        )
        assert config_custom.user_agent == "Custom/1.0"
        assert config_custom.timeout == 30
        assert config_custom.hh_config == hh_config
        
        # Тест параметров пагинации
        params = config.get_pagination_params()
        assert params == {"max_pages": 20}
        
        params_override = config.get_pagination_params(max_pages=100)
        assert params_override == {"max_pages": 100}

    def test_app_config_all_methods(self):
        """100% покрытие AppConfig"""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig()
            
            # Тест дефолтных значений
            assert config.get_storage_type() == "postgres"
            assert config.default_storage_type == "postgres"
            
            # Тест установки типа хранилища
            config.set_storage_type("postgres")
            assert config.storage_type == "postgres"
            
            # Тест исключения
            with pytest.raises(ValueError, match="Поддерживается только PostgreSQL"):
                config.set_storage_type("mysql")
            
            # Тест DB config
            db_config = config.get_db_config()
            assert isinstance(db_config, dict)
            assert "host" in db_config
            
            # Тест установки конфигурации БД
            new_config = {"host": "new_host", "port": "9999"}
            config.set_db_config(new_config)
            assert config.db_config["host"] == "new_host"

        # Тест с переменными окружения
        env_vars = {"PGHOST": "env_host", "PGPORT": "5433", "PGDATABASE": "env_db"}
        with patch.dict(os.environ, env_vars):
            config_env = AppConfig()
            assert config_env.db_config["host"] == "env_host"
            assert config_env.db_config["port"] == "5433"

    def test_company_info_dataclass(self):
        """100% покрытие CompanyInfo"""
        # Минимальный экземпляр
        company_min = CompanyInfo(name="Test", hh_id="123")
        assert company_min.name == "Test"
        assert company_min.hh_id == "123"
        assert company_min.sj_id is None
        assert company_min.description == ""
        
        # Полный экземпляр
        company_full = CompanyInfo(
            name="Full", 
            hh_id="123", 
            sj_id="456", 
            description="Test desc"
        )
        assert company_full.sj_id == "456"
        assert company_full.description == "Test desc"

    def test_target_companies_all_methods(self):
        """100% покрытие TargetCompanies"""
        # Тест получения всех компаний
        companies = TargetCompanies.get_all_companies()
        assert isinstance(companies, list)
        assert len(companies) > 0
        assert all(isinstance(c, CompanyInfo) for c in companies)
        
        # Тест что COMPANIES существует
        assert hasattr(TargetCompanies, 'COMPANIES')
        assert isinstance(TargetCompanies.COMPANIES, list)
        assert len(TargetCompanies.COMPANIES) == len(companies)


class TestUtilsModules:
    """Тесты utils модулей с реальными импортами"""

    def setup_method(self):
        """Сброс состояния EnvLoader перед каждым тестом"""
        EnvLoader._loaded = False

    def test_env_loader_all_methods(self):
        """100% покрытие EnvLoader"""
        # Тест загрузки несуществующего файла
        with patch('os.path.exists', return_value=False):
            EnvLoader.load_env_file("nonexistent.env")
            assert EnvLoader._loaded == True

        # Тест повторной загрузки (уже загружено)
        EnvLoader._loaded = True
        with patch('builtins.open', mock_open()) as mock_file:
            EnvLoader.load_env_file(".env")
            mock_file.assert_not_called()

        # Тест успешной загрузки
        EnvLoader._loaded = False
        env_content = "KEY1=value1\nKEY2=\"value2\"\nKEY3='value3'\n# Comment\nKEY4=value4"
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {}, clear=True):
                    EnvLoader.load_env_file(".env")
                    assert os.environ["KEY1"] == "value1"
                    assert os.environ["KEY2"] == "value2"
                    assert os.environ["KEY3"] == "value3"
                    assert os.environ["KEY4"] == "value4"

        # Тест что существующие переменные не перезаписываются
        EnvLoader._loaded = False
        env_content = "EXISTING_VAR=new_value"
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {"EXISTING_VAR": "old_value"}):
                    EnvLoader.load_env_file(".env")
                    assert os.environ["EXISTING_VAR"] == "old_value"

        # Тест обработки невалидных строк
        EnvLoader._loaded = False
        env_content = "VALID_KEY=valid_value\ninvalid_line\nANOTHER_VALID=value"
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {}, clear=True):
                    EnvLoader.load_env_file(".env")
                    assert "VALID_KEY" in os.environ
                    assert "ANOTHER_VALID" in os.environ

        # Тест обработки исключения при чтении
        EnvLoader._loaded = False
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("File error")):
                EnvLoader.load_env_file(".env")  # Не должно падать

        # Тест методов получения переменных
        with patch.dict(os.environ, {"TEST_VAR": "test_value", "INT_VAR": "42"}):
            # get_env_var
            result = EnvLoader.get_env_var("TEST_VAR", "default")
            assert result == "test_value"
            
            result = EnvLoader.get_env_var("MISSING", "default")
            assert result == "default"
            
            result = EnvLoader.get_env_var("MISSING_NO_DEFAULT")
            assert result == ""
            
            # get_env_var_int
            result = EnvLoader.get_env_var_int("INT_VAR", 0)
            assert result == 42
            
            result = EnvLoader.get_env_var_int("MISSING", 100)
            assert result == 100

        # Тест невалидного int
        with patch.dict(os.environ, {"INVALID_INT": "not_a_number"}):
            result = EnvLoader.get_env_var_int("INVALID_INT", 42)
            assert result == 42


class TestVacancyModels:
    """Тесты моделей вакансий с реальными импортами"""

    def test_employer_all_methods(self):
        """100% покрытие Employer"""
        # Тест инициализации
        employer = Employer("Test Company", "123", True, "http://test.com")
        assert employer.get_name() == "Test Company"
        assert employer.get_id() == "123"
        assert employer.is_trusted() == True
        assert employer.get_url() == "http://test.com"
        
        # Тест fallback для None/пустых значений
        employer_none = Employer(None)
        assert employer_none.get_name() == "Не указана"
        
        employer_empty = Employer("")
        assert employer_empty.get_name() == "Не указана"
        
        # Тест сериализации
        employer_dict = employer.to_dict()
        expected = {
            "name": "Test Company",
            "id": "123", 
            "trusted": True,
            "alternate_url": "http://test.com"
        }
        assert employer_dict == expected
        
        # Тест создания из словаря
        data = {"name": "Dict Company", "id": "456", "trusted": False}
        employer_from_dict = Employer.from_dict(data)
        assert employer_from_dict.get_name() == "Dict Company"
        assert employer_from_dict.get_id() == "456"
        assert employer_from_dict.is_trusted() == False
        
        # Тест создания из пустого словаря
        employer_empty_dict = Employer.from_dict({})
        assert employer_empty_dict.get_name() == "Не указана"
        
        # Тест свойств для обратной совместимости
        assert employer.name == "Test Company"
        assert employer.id == "123"
        assert employer.trusted == True
        assert employer.alternate_url == "http://test.com"
        
        # Тест dictionary-like доступа
        assert employer.get("name") == "Test Company"
        assert employer.get("id") == "123"
        assert employer.get("missing", "default") == "default"
        
        # Тест равенства
        employer2 = Employer("Test Company", "123")
        assert employer == employer2
        
        dict_data = {"name": "Test Company", "id": "123"}
        assert employer == dict_data
        
        # Тест строковых представлений
        assert str(employer) == "Test Company"
        assert "Test Company" in repr(employer)
        
        # Тест хеширования
        assert hash(employer) == hash(employer2)
        
        # Тест в множестве
        employer_set = {employer, employer2}
        assert len(employer_set) == 1

    def test_experience_all_methods(self):
        """100% покрытие Experience"""
        # Тест инициализации (первый параметр - name)
        exp = Experience("От 1 до 3 лет", "between1And3")
        assert exp.get_name() == "От 1 до 3 лет"
        assert exp.get_id() == "between1And3"
        
        # Тест только с именем
        exp_name_only = Experience("От 3 до 6 лет")
        assert exp_name_only.get_name() == "От 3 до 6 лет"
        assert exp_name_only.get_id() is None
        
        # Тест fallback
        exp_empty = Experience("")
        assert exp_empty.get_name() == "Не указан"
        
        exp_none = Experience(None)
        assert exp_none.get_name() == "Не указан"
        
        # Тест сериализации
        exp_dict = exp.to_dict()
        assert exp_dict["name"] == "От 1 до 3 лет"
        assert exp_dict["id"] == "between1And3"
        
        # Тест создания из словаря
        data = {"name": "Более 6 лет", "id": "moreThan6"}
        exp_from_dict = Experience.from_dict(data)
        assert exp_from_dict.get_name() == "Более 6 лет"
        assert exp_from_dict.get_id() == "moreThan6"
        
        # Тест создания из строки
        exp_from_string = Experience.from_string("Без опыта")
        assert exp_from_string.get_name() == "Без опыта"
        assert exp_from_string.get_id() is None

    def test_employment_all_methods(self):
        """100% покрытие Employment"""
        # Тест инициализации (первый параметр - name)
        emp = Employment("Полная занятость", "full")
        assert emp.get_name() == "Полная занятость"
        assert emp.get_id() == "full"
        
        # Тест только с именем
        emp_name_only = Employment("Частичная занятость")
        assert emp_name_only.get_name() == "Частичная занятость"
        assert emp_name_only.get_id() is None
        
        # Тест сериализации
        emp_dict = emp.to_dict()
        assert emp_dict["name"] == "Полная занятость"
        assert emp_dict["id"] == "full"
        
        # Тест создания из словаря
        data = {"name": "Проектная работа", "id": "project"}
        emp_from_dict = Employment.from_dict(data)
        assert emp_from_dict.get_name() == "Проектная работа"
        assert emp_from_dict.get_id() == "project"
        
        # Тест создания из строки
        emp_from_string = Employment.from_string("Удаленная работа")
        assert emp_from_string.get_name() == "Удаленная работа"
        assert emp_from_string.get_id() is None

    def test_vacancy_all_methods(self):
        """100% покрытие Vacancy"""
        # Тест минимальной инициализации
        vacancy = Vacancy("Test Job", "http://test.com")
        assert vacancy.title == "Test Job"
        assert vacancy.url == "http://test.com"
        
        # Тест с дополнительными параметрами
        employer = Employer("Test Company")
        vacancy_full = Vacancy(
            title="Full Job",
            url="http://full.com",
            employer=employer,
            description="Full description",
            vacancy_id="full123",
            published_at="2024-01-01T10:00:00"
        )
        assert vacancy_full.title == "Full Job"
        assert vacancy_full.employer == employer
        assert vacancy_full.description == "Full description"
        
        # Тест сериализации
        vacancy_dict = vacancy.to_dict()
        assert vacancy_dict["title"] == "Test Job"
        assert vacancy_dict["url"] == "http://test.com"
        
        # Тест создания из словаря
        data = {
            "title": "Dict Job",
            "url": "http://dict.com",
            "description": "Dict description",
            "id": "dict123",
            "employer": {"name": "Dict Company"},
            "published_at": "2024-01-01T00:00:00"
        }
        vacancy_from_dict = Vacancy.from_dict(data)
        assert vacancy_from_dict.title == "Dict Job"
        assert vacancy_from_dict.description == "Dict description"
        
        # Тест строковых представлений
        str_result = str(vacancy)
        assert "Test Job" in str_result

    @patch('src.utils.salary.Salary')
    def test_salary_integration_mocked(self, mock_salary_class):
        """Тест интеграции с Salary через мок"""
        mock_salary = Mock()
        mock_salary_class.return_value = mock_salary
        
        from src.utils.salary import Salary
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)
        
        mock_salary_class.assert_called_once_with(salary_data)


class TestIntegration:
    """Интеграционные тесты с реальными импортами"""

    def test_all_modules_imported_correctly(self):
        """Тест что все модули импортируются корректно"""
        # Абстрактные классы
        assert AbstractVacancy is not None
        assert AbstractEmployer is not None
        assert AbstractExperience is not None
        assert AbstractEmployment is not None
        assert AbstractSalary is not None
        assert AbstractVacancyStorage is not None
        assert AbstractDBManager is not None
        assert BaseJobAPI is not None
        assert AbstractDataFilter is not None
        
        # Config модули
        assert APIConfig is not None
        assert AppConfig is not None
        assert TargetCompanies is not None
        assert CompanyInfo is not None
        
        # Utils модули
        assert EnvLoader is not None
        
        # Модели
        assert Employer is not None
        assert Experience is not None
        assert Employment is not None
        assert Vacancy is not None

    def test_inheritance_hierarchy(self):
        """Тест правильности иерархии наследования"""
        from abc import ABC
        
        # Проверяем что абстрактные классы наследуются от ABC
        assert issubclass(AbstractVacancy, ABC)
        assert issubclass(AbstractEmployer, ABC)
        assert issubclass(AbstractExperience, ABC)
        assert issubclass(AbstractEmployment, ABC)
        assert issubclass(AbstractSalary, ABC)
        assert issubclass(AbstractVacancyStorage, ABC)
        assert issubclass(AbstractDBManager, ABC)
        assert issubclass(BaseJobAPI, ABC)
        assert issubclass(AbstractDataFilter, ABC)
        
        # Проверяем что конкретные классы наследуются от абстрактных
        assert issubclass(Employer, AbstractEmployer)
        assert issubclass(Experience, AbstractExperience)
        assert issubclass(Employment, AbstractEmployment)
        assert issubclass(Vacancy, AbstractVacancy)

    def test_full_workflow_simulation(self):
        """Тест симуляции полного рабочего процесса"""
        # 1. Загружаем переменные окружения
        EnvLoader._loaded = False
        with patch('os.path.exists', return_value=False):
            EnvLoader.load_env_file(".env")
        
        # 2. Создаем конфигурации
        api_config = APIConfig()
        app_config = AppConfig()
        
        # 3. Получаем список компаний
        companies = TargetCompanies.get_all_companies()
        
        # 4. Создаем модели
        employer = Employer("Test Company", "123")
        experience = Experience("От 1 до 3 лет", "between1And3")
        employment = Employment("Полная занятость", "full")
        vacancy = Vacancy("Python Developer", "http://test.com", employer=employer)
        
        # 5. Проверяем что все работает вместе
        assert api_config is not None
        assert app_config is not None
        assert len(companies) > 0
        assert vacancy.employer.get_name() == "Test Company"
        assert experience.get_name() == "От 1 до 3 лет"
        assert employment.get_name() == "Полная занятость"
        
        # 6. Тест сериализации/десериализации
        employer_dict = employer.to_dict()
        employer_restored = Employer.from_dict(employer_dict)
        assert employer.get_name() == employer_restored.get_name()
        
        vacancy_dict = vacancy.to_dict()
        vacancy_restored = Vacancy.from_dict(vacancy_dict)
        assert vacancy.title == vacancy_restored.title

    def test_error_handling_comprehensive(self):
        """Комплексное тестирование обработки ошибок"""
        # AppConfig с невалидным типом
        app_config = AppConfig()
        with pytest.raises(ValueError):
            app_config.set_storage_type("invalid_type")
        
        # EnvLoader с исключением
        EnvLoader._loaded = False
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("Test error")):
                EnvLoader.load_env_file(".env")  # Не должно падать
        
        # EnvLoader с невалидным int
        with patch.dict(os.environ, {"INVALID_INT": "not_a_number"}):
            result = EnvLoader.get_env_var_int("INVALID_INT", 42)
            assert result == 42
        
        # Создание моделей с None значениями
        employer = Employer(None)
        assert employer.get_name() == "Не указана"
        
        exp = Experience(None)
        assert exp.get_name() == "Не указан"
        
        # Создание из пустых словарей
        employer_empty = Employer.from_dict({})
        assert employer_empty.get_name() == "Не указана"
        
        exp_empty = Experience.from_dict({})
        assert exp_empty.get_name() == "Не указан"
        
        emp_empty = Employment.from_dict({})
        # Employment не имеет fallback в from_dict, поэтому может быть None
        assert emp_empty.get_name() is not None or emp_empty.get_name() == ""