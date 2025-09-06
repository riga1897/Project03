"""
100% покрытие конкретных моделей с правильными сигнатурами
Основано на реальной структуре кода
"""

import os
import sys
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Config модули
from src.config.api_config import APIConfig
from src.config.app_config import AppConfig  
from src.config.target_companies import TargetCompanies, CompanyInfo

# Utils модули  
from src.utils.env_loader import EnvLoader
from src.utils.salary import Salary

# Vacancy модели
from src.vacancies.models import Employer, Experience, Employment, Vacancy


class TestEnvLoader:
    """100% покрытие EnvLoader с правильными методами"""

    def setup_method(self):
        """Сброс состояния перед каждым тестом"""
        EnvLoader._loaded = False

    def test_load_env_file_not_found(self):
        """Тест загрузки несуществующего файла"""
        with patch('os.path.exists', return_value=False):
            with patch.object(EnvLoader, '_loaded', False):
                EnvLoader.load_env_file("nonexistent.env")
                assert EnvLoader._loaded == True

    def test_load_env_file_already_loaded(self):
        """Тест повторной загрузки"""
        EnvLoader._loaded = True
        with patch('builtins.open', mock_open()) as mock_file:
            EnvLoader.load_env_file(".env")
            mock_file.assert_not_called()

    def test_load_env_file_success(self):
        """Тест успешной загрузки файла"""
        env_content = """KEY1=value1\nKEY2="value2"\nKEY3='value3'\n# Comment\nKEY4=value4"""
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {}, clear=True):
                    with patch.object(EnvLoader, '_loaded', False):
                        EnvLoader.load_env_file(".env")
                        assert os.environ["KEY1"] == "value1"
                        assert os.environ["KEY2"] == "value2"
                        assert os.environ["KEY3"] == "value3"

    def test_load_env_file_existing_env_var(self):
        """Тест что существующие переменные не перезаписываются"""
        env_content = "EXISTING_VAR=new_value"
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {"EXISTING_VAR": "old_value"}):
                    with patch.object(EnvLoader, '_loaded', False):
                        EnvLoader.load_env_file(".env")
                        assert os.environ["EXISTING_VAR"] == "old_value"

    def test_load_env_file_invalid_format(self):
        """Тест обработки невалидных строк"""
        env_content = "VALID_KEY=valid_value\ninvalid_line\nANOTHER_VALID=value"
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {}, clear=True):
                    with patch.object(EnvLoader, '_loaded', False):
                        EnvLoader.load_env_file(".env")
                        assert "VALID_KEY" in os.environ
                        assert "ANOTHER_VALID" in os.environ

    def test_load_env_file_exception(self):
        """Тест обработки исключения при чтении"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("File error")):
                with patch.object(EnvLoader, '_loaded', False):
                    EnvLoader.load_env_file(".env")  # Не должно падать

    def test_get_env_var_existing(self):
        """Тест получения существующей переменной"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = EnvLoader.get_env_var("TEST_VAR", "default")
            assert result == "test_value"

    def test_get_env_var_default(self):
        """Тест получения дефолтного значения"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_env_var("MISSING_VAR", "default_value")
            assert result == "default_value"

    def test_get_env_var_no_default(self):
        """Тест без дефолтного значения"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_env_var("MISSING_VAR")
            assert result == ""

    def test_get_env_var_int_existing(self):
        """Тест получения существующей числовой переменной"""
        with patch.dict(os.environ, {"INT_VAR": "42"}):
            result = EnvLoader.get_env_var_int("INT_VAR", 0)
            assert result == 42

    def test_get_env_var_int_invalid(self):
        """Тест получения невалидной числовой переменной"""
        with patch.dict(os.environ, {"INT_VAR": "not_a_number"}):
            result = EnvLoader.get_env_var_int("INT_VAR", 100)
            assert result == 100

    def test_get_env_var_int_missing(self):
        """Тест получения отсутствующей числовой переменной"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_env_var_int("MISSING_INT_VAR", 50)
            assert result == 50


class TestSalary:
    """100% покрытие utils.salary.Salary с правильной сигнатурой"""

    def test_init_empty(self):
        """Тест инициализации без данных"""
        salary = Salary()
        assert salary.get_from_amount() is None
        assert salary.get_to_amount() is None

    def test_init_with_data(self):
        """Тест инициализации с данными"""
        salary_data = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR",
            "gross": True
        }
        salary = Salary(salary_data)
        assert salary.get_from_amount() == 100000
        assert salary.get_to_amount() == 150000
        assert salary.get_currency() == "RUR"
        assert salary.is_gross() == True

    def test_init_partial_data(self):
        """Тест инициализации с частичными данными"""
        salary_data = {"from": 80000, "currency": "USD"}
        salary = Salary(salary_data)
        assert salary.get_from_amount() == 80000
        assert salary.get_to_amount() is None
        assert salary.get_currency() == "USD"

    def test_format_salary_full_range(self):
        """Тест форматирования полного диапазона"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)
        formatted = salary.format_salary()
        assert "100 000" in formatted and "150 000" in formatted

    def test_format_salary_from_only(self):
        """Тест форматирования только от"""
        salary_data = {"from": 100000, "currency": "RUR"}
        salary = Salary(salary_data)
        formatted = salary.format_salary()
        assert "от 100 000" in formatted.lower()

    def test_format_salary_to_only(self):
        """Тест форматирования только до"""
        salary_data = {"to": 100000, "currency": "RUR"}
        salary = Salary(salary_data)
        formatted = salary.format_salary()
        assert "до 100 000" in formatted.lower()

    def test_format_salary_none(self):
        """Тест форматирования отсутствующей зарплаты"""
        salary = Salary()
        formatted = salary.format_salary()
        assert formatted == "Не указана"

    def test_is_specified_true(self):
        """Тест проверки что зарплата указана"""
        salary_data = {"from": 100000}
        salary = Salary(salary_data)
        assert salary.is_specified() == True

    def test_is_specified_false(self):
        """Тест проверки что зарплата не указана"""
        salary = Salary()
        assert salary.is_specified() == False

    def test_get_average_with_range(self):
        """Тест получения средней зарплаты с диапазоном"""
        salary_data = {"from": 100000, "to": 200000}
        salary = Salary(salary_data)
        assert salary.get_average() == 150000

    def test_get_average_from_only(self):
        """Тест получения средней зарплаты только с from"""
        salary_data = {"from": 100000}
        salary = Salary(salary_data)
        assert salary.get_average() == 100000

    def test_get_average_to_only(self):
        """Тест получения средней зарплаты только с to"""
        salary_data = {"to": 150000}
        salary = Salary(salary_data)
        assert salary.get_average() == 150000

    def test_compare_salaries(self):
        """Тест сравнения зарплат"""
        salary1_data = {"from": 150000, "to": 200000}
        salary2_data = {"from": 100000, "to": 130000}
        
        salary1 = Salary(salary1_data)
        salary2 = Salary(salary2_data)
        
        assert salary1.compare(salary2) > 0
        assert salary2.compare(salary1) < 0

    def test_to_dict(self):
        """Тест сериализации в словарь"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR", "gross": True}
        salary = Salary(salary_data)
        result = salary.to_dict()
        assert result == salary_data

    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {"from": 90000, "to": 130000, "currency": "USD"}
        salary = Salary.from_dict(data)
        assert salary.get_from_amount() == 90000
        assert salary.get_to_amount() == 130000


class TestEmployer:
    """100% покрытие models.Employer"""

    def test_init_minimal(self):
        """Тест минимальной инициализации"""
        employer = Employer("Test Company")
        assert employer.get_name() == "Test Company"
        assert employer.get_id() is None

    def test_init_full(self):
        """Тест полной инициализации"""
        employer = Employer(
            name="Full Company",
            employer_id="123",
            trusted=True,
            alternate_url="http://company.com"
        )
        assert employer.get_name() == "Full Company"
        assert employer.get_id() == "123"
        assert employer.is_trusted() == True
        assert employer.get_url() == "http://company.com"

    def test_get_name_fallback(self):
        """Тест fallback для имени"""
        employer_empty = Employer("")
        assert employer_empty.get_name() == "Не указана"
        
        employer_none = Employer(None)
        assert employer_none.get_name() == "Не указана"

    def test_to_dict(self):
        """Тест сериализации в словарь"""
        employer = Employer("Test", "123", True, "http://test.com")
        result = employer.to_dict()
        expected = {
            "name": "Test",
            "id": "123", 
            "trusted": True,
            "alternate_url": "http://test.com"
        }
        assert result == expected

    def test_from_dict_full(self):
        """Тест создания из полного словаря"""
        data = {
            "name": "Dict Company",
            "id": "456",
            "trusted": False,
            "alternate_url": "http://dict.com"
        }
        employer = Employer.from_dict(data)
        assert employer.get_name() == "Dict Company"
        assert employer.get_id() == "456"
        assert employer.is_trusted() == False

    def test_from_dict_minimal(self):
        """Тест создания из минимального словаря"""
        data = {"name": "Minimal Company"}
        employer = Employer.from_dict(data)
        assert employer.get_name() == "Minimal Company"
        assert employer.get_id() is None

    def test_properties(self):
        """Тест свойств для обратной совместимости"""
        employer = Employer("Prop Company", "prop123", True, "http://prop.com")
        assert employer.name == "Prop Company"
        assert employer.id == "prop123"
        assert employer.trusted == True
        assert employer.alternate_url == "http://prop.com"

    def test_get_method(self):
        """Тест dictionary-like доступа"""
        employer = Employer("Dict Access", "dict456")
        assert employer.get("name") == "Dict Access"
        assert employer.get("id") == "dict456"
        assert employer.get("nonexistent", "default") == "default"

    def test_equality(self):
        """Тест сравнения"""
        employer1 = Employer("Same Company", "123")
        employer2 = Employer("Same Company", "123")
        employer3 = Employer("Different Company", "123")
        
        assert employer1 == employer2
        assert employer1 != employer3
        
        # Тест сравнения со словарем
        dict_data = {"name": "Same Company", "id": "123"}
        assert employer1 == dict_data

    def test_str_repr(self):
        """Тест строковых представлений"""
        employer = Employer("String Company", "str123")
        assert str(employer) == "String Company"
        assert repr(employer) == "Employer(name='String Company', id='str123')"

    def test_hash(self):
        """Тест хеширования"""
        employer1 = Employer("Hash Company", "hash123")
        employer2 = Employer("Hash Company", "hash123")
        assert hash(employer1) == hash(employer2)
        
        # Тест использования в множествах
        employer_set = {employer1, employer2}
        assert len(employer_set) == 1


class TestExperience:
    """100% покрытие models.Experience с правильными параметрами"""

    def test_init(self):
        """Тест инициализации - первый параметр name"""
        exp = Experience("От 1 года до 3 лет", "between1And3")
        assert exp.get_name() == "От 1 года до 3 лет"
        assert exp.get_id() == "between1And3"

    def test_init_name_only(self):
        """Тест инициализации только с именем"""
        exp = Experience("От 3 до 6 лет")
        assert exp.get_name() == "От 3 до 6 лет"
        assert exp.get_id() is None

    def test_get_name_fallback(self):
        """Тест fallback для имени"""
        exp_empty = Experience("")
        assert exp_empty.get_name() == "Не указан"
        
        exp_none = Experience(None)
        assert exp_none.get_name() == "Не указан"

    def test_to_dict(self):
        """Тест сериализации"""
        exp = Experience("От 3 до 6 лет", "between3And6")
        result = exp.to_dict()
        expected = {"name": "От 3 до 6 лет", "id": "between3And6"}
        assert result == expected

    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {"name": "Более 6 лет", "id": "moreThan6"}
        exp = Experience.from_dict(data)
        assert exp.get_name() == "Более 6 лет"
        assert exp.get_id() == "moreThan6"

    def test_from_string(self):
        """Тест создания из строки"""
        exp = Experience.from_string("От 1 года до 3 лет")
        assert exp.get_name() == "От 1 года до 3 лет"
        assert exp.get_id() is None


class TestEmployment:
    """100% покрытие models.Employment с правильными параметрами"""

    def test_init(self):
        """Тест инициализации - первый параметр name"""
        emp = Employment("Полная занятость", "full")
        assert emp.get_name() == "Полная занятость"
        assert emp.get_id() == "full"

    def test_init_name_only(self):
        """Тест инициализации только с именем"""
        emp = Employment("Частичная занятость")
        assert emp.get_name() == "Частичная занятость"
        assert emp.get_id() is None

    def test_to_dict(self):
        """Тест сериализации"""
        emp = Employment("Частичная занятость", "part")
        result = emp.to_dict()
        expected = {"name": "Частичная занятость", "id": "part"}
        assert result == expected

    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {"name": "Проектная работа", "id": "project"}
        emp = Employment.from_dict(data)
        assert emp.get_name() == "Проектная работа"
        assert emp.get_id() == "project"

    def test_from_string(self):
        """Тест создания из строки"""
        emp = Employment.from_string("Полная занятость")
        assert emp.get_name() == "Полная занятость"
        assert emp.get_id() is None


class TestVacancy:
    """100% покрытие models.Vacancy с реальными методами"""

    def test_init_minimal(self):
        """Тест минимальной инициализации"""
        vacancy = Vacancy("Test Vacancy", "http://test.com")
        assert vacancy.title == "Test Vacancy"
        assert vacancy.url == "http://test.com"

    def test_init_full(self):
        """Тест полной инициализации"""
        employer = Employer("Test Company")
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)
        
        vacancy = Vacancy(
            title="Full Vacancy",
            url="http://full.com",
            salary=salary,
            employer=employer,
            description="Test description",
            vacancy_id="123",
            published_at="2024-01-01T00:00:00"
        )
        
        assert vacancy.title == "Full Vacancy"
        assert vacancy.salary == salary
        assert vacancy.employer == employer
        assert vacancy.description == "Test description"

    def test_properties(self):
        """Тест свойств вакансии"""
        employer = Employer("Prop Company")
        vacancy = Vacancy("Prop Vacancy", "http://prop.com", employer=employer)
        
        # Проверяем доступ к свойствам
        assert vacancy.title == "Prop Vacancy"
        assert vacancy.url == "http://prop.com" 
        assert vacancy.employer == employer

    def test_to_dict_serialization(self):
        """Тест сериализации в словарь"""
        employer = Employer("Test Company")
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)
        
        vacancy = Vacancy(
            title="Full Test",
            url="http://test.com",
            salary=salary,
            employer=employer,
            vacancy_id="test123"
        )
        
        result = vacancy.to_dict()
        assert result["title"] == "Full Test"
        assert "salary" in result
        assert "employer" in result
        assert result["id"] == "test123"

    def test_from_dict_deserialization(self):
        """Тест создания из словаря"""
        data = {
            "title": "Dict Vacancy",
            "url": "http://dict.com",
            "id": "dict123",
            "description": "Full description",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "employer": {"name": "Dict Company"},
            "published_at": "2024-01-01T00:00:00"
        }
        
        vacancy = Vacancy.from_dict(data)
        assert vacancy.title == "Dict Vacancy"
        assert vacancy.id == "dict123"
        assert vacancy.description == "Full description"
        assert vacancy.salary is not None
        assert vacancy.employer is not None

    def test_str_repr(self):
        """Тест строковых представлений"""
        vacancy = Vacancy("String Vacancy", "http://string.com")
        str_result = str(vacancy)
        repr_result = repr(vacancy)
        
        assert "String Vacancy" in str_result
        assert "String Vacancy" in repr_result


class TestConfigModulesIntegration:
    """Интеграционные тесты config модулей"""

    def test_api_config_all_methods(self):
        """Тест всех методов APIConfig"""
        config = APIConfig()
        
        # Тест дефолтных значений
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20
        
        # Тест параметров пагинации
        params = config.get_pagination_params()
        assert params == {"max_pages": 20}
        
        params_override = config.get_pagination_params(max_pages=100)
        assert params_override == {"max_pages": 100}

    def test_app_config_all_methods(self):
        """Тест всех методов AppConfig"""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig()
            
            # Тест дефолтных значений
            assert config.get_storage_type() == "postgres"
            
            # Тест установки типа хранилища
            config.set_storage_type("postgres")
            assert config.storage_type == "postgres"
            
            # Тест исключения для невалидного типа
            with pytest.raises(ValueError):
                config.set_storage_type("mysql")
            
            # Тест получения конфигурации БД
            db_config = config.get_db_config()
            assert isinstance(db_config, dict)
            assert "host" in db_config
            
            # Тест установки конфигурации БД
            new_config = {"host": "new_host", "port": "9999"}
            config.set_db_config(new_config)
            assert config.db_config["host"] == "new_host"

    def test_target_companies_all_methods(self):
        """Тест всех методов TargetCompanies"""
        # Тест получения всех компаний
        companies = TargetCompanies.get_all_companies()
        assert isinstance(companies, list)
        assert len(companies) > 0
        
        # Тест поиска компании (используем первую из списка)
        first_company = companies[0]
        found_company = TargetCompanies.get_company_by_name(first_company.name)
        assert found_company is not None
        
        # Тест поиска несуществующей компании
        not_found = TargetCompanies.get_company_by_name("Несуществующая компания")
        assert not_found is None
        
        # Тест получения ID для HH
        hh_ids = TargetCompanies.get_company_ids("hh")
        assert isinstance(hh_ids, list)
        
        # Тест получения компаний для источника
        hh_companies = TargetCompanies.get_companies_for_source("hh")
        assert isinstance(hh_companies, list)

    def test_company_info_dataclass(self):
        """Тест dataclass CompanyInfo"""
        # Минимальный экземпляр
        company_min = CompanyInfo(name="Test", hh_id="123")
        assert company_min.name == "Test"
        assert company_min.hh_id == "123"
        
        # Полный экземпляр
        company_full = CompanyInfo(
            name="Full", 
            hh_id="123", 
            sj_id="456", 
            description="Test desc"
        )
        assert company_full.sj_id == "456"
        assert company_full.description == "Test desc"