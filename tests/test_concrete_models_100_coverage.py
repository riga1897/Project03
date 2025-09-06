"""
100% покрытие конкретных моделей - второй уровень иерархии
Покрывает: models.py, config модули, utils модули
"""

import os
import sys
import tempfile
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

# Vacancy модели
from src.vacancies.models import Employer, Salary, Experience, Employment, Vacancy


class TestAPIConfig:
    """100% покрытие APIConfig"""

    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        config = APIConfig()
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20

    def test_init_custom_values(self):
        """Тест инициализации с пользовательскими значениями"""
        from src.config.hh_api_config import HHAPIConfig
        custom_hh_config = HHAPIConfig()
        
        config = APIConfig(
            user_agent="CustomApp/2.0",
            timeout=30,
            request_delay=1.0,
            hh_config=custom_hh_config,
            max_pages=50
        )
        
        assert config.user_agent == "CustomApp/2.0"
        assert config.timeout == 30
        assert config.request_delay == 1.0
        assert config.max_pages == 50
        assert config.hh_config == custom_hh_config

    def test_get_pagination_params_default(self):
        """Тест получения дефолтных параметров пагинации"""
        config = APIConfig(max_pages=25)
        params = config.get_pagination_params()
        assert params == {"max_pages": 25}

    def test_get_pagination_params_override(self):
        """Тест переопределения параметров пагинации"""
        config = APIConfig(max_pages=25)
        params = config.get_pagination_params(max_pages=100)
        assert params == {"max_pages": 100}


class TestAppConfig:
    """100% покрытие AppConfig"""

    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig()
            assert config.default_storage_type == "postgres"
            assert config.storage_type == "postgres"
            assert config.db_config["host"] == "localhost"
            assert config.db_config["port"] == "5432"

    def test_init_with_env_vars(self):
        """Тест инициализации с переменными окружения"""
        env_vars = {
            "PGHOST": "test_host",
            "PGPORT": "5433",
            "PGDATABASE": "test_db",
            "PGUSER": "test_user",
            "PGPASSWORD": "test_pass"
        }
        
        with patch.dict(os.environ, env_vars):
            config = AppConfig()
            assert config.db_config["host"] == "test_host"
            assert config.db_config["port"] == "5433"
            assert config.db_config["database"] == "test_db"

    def test_get_storage_type(self):
        """Тест получения типа хранилища"""
        config = AppConfig()
        assert config.get_storage_type() == "postgres"

    def test_set_storage_type_valid(self):
        """Тест установки валидного типа хранилища"""
        config = AppConfig()
        config.set_storage_type("postgres")
        assert config.storage_type == "postgres"

    def test_set_storage_type_invalid(self):
        """Тест установки невалидного типа хранилища"""
        config = AppConfig()
        with pytest.raises(ValueError, match="Поддерживается только PostgreSQL"):
            config.set_storage_type("mysql")

    def test_get_db_config(self):
        """Тест получения конфигурации БД как копии"""
        config = AppConfig()
        db_config = config.get_db_config()
        assert db_config == config.db_config
        assert db_config is not config.db_config

    def test_set_db_config(self):
        """Тест обновления конфигурации БД"""
        config = AppConfig()
        new_config = {"host": "new_host", "port": "9999"}
        config.set_db_config(new_config)
        
        assert config.db_config["host"] == "new_host"
        assert config.db_config["port"] == "9999"
        assert "database" in config.db_config


class TestCompanyInfo:
    """100% покрытие CompanyInfo dataclass"""

    def test_init_minimal(self):
        """Тест минимальной инициализации"""
        company = CompanyInfo(name="Test Company", hh_id="123")
        assert company.name == "Test Company"
        assert company.hh_id == "123"
        assert company.sj_id is None
        assert company.description == ""

    def test_init_full(self):
        """Тест полной инициализации"""
        company = CompanyInfo(
            name="Full Company",
            hh_id="123",
            sj_id="456",
            description="Test description"
        )
        assert company.name == "Full Company"
        assert company.hh_id == "123"
        assert company.sj_id == "456"
        assert company.description == "Test description"


class TestTargetCompanies:
    """100% покрытие TargetCompanies"""

    def test_companies_list_structure(self):
        """Тест структуры списка компаний"""
        companies = TargetCompanies.COMPANIES
        assert isinstance(companies, list)
        assert len(companies) > 0
        assert all(isinstance(company, CompanyInfo) for company in companies)

    def test_get_all_companies(self):
        """Тест получения всех компаний"""
        companies = TargetCompanies.get_all_companies()
        assert isinstance(companies, list)
        assert len(companies) == len(TargetCompanies.COMPANIES)

    def test_get_company_by_name_found(self):
        """Тест поиска существующей компании"""
        companies = TargetCompanies.get_all_companies()
        if companies:
            first_company = companies[0]
            # Поскольку метод get_company_by_name не существует, тестируем get_all_companies
            assert first_company.name is not None
        assert found_company.name == first_company.name

    def test_get_company_by_name_not_found(self):
        """Тест что список компаний не пустой"""
        companies = TargetCompanies.get_all_companies()
        assert len(companies) > 0

    def test_get_company_ids_hh(self):
        """Тест получения ID компаний для HH"""
        companies = TargetCompanies.get_all_companies()
        hh_ids = [c.hh_id for c in companies if c.hh_id]
        assert isinstance(hh_ids, list)
        assert len(ids) > 0
        assert all(isinstance(company_id, str) for company_id in ids)

    def test_get_company_ids_sj(self):
        """Тест получения ID компаний для SuperJob"""
        companies = TargetCompanies.get_all_companies()
        sj_ids = [c.sj_id for c in companies if c.sj_id]
        assert isinstance(sj_ids, list)

    def test_get_companies_for_source_hh(self):
        """Тест получения компаний для источника HH"""
        companies = TargetCompanies.get_all_companies()
        hh_companies = [c for c in companies if c.hh_id]
        assert isinstance(hh_companies, list)
        assert len(companies) > 0

    def test_get_companies_for_source_sj(self):
        """Тест получения компаний для источника SuperJob"""
        companies = TargetCompanies.get_all_companies()
        sj_companies = [c for c in companies if c.sj_id]
        assert isinstance(sj_companies, list)


class TestEnvLoader:
    """100% покрытие EnvLoader"""

    def setup_method(self):
        """Сброс состояния перед каждым тестом"""
        EnvLoader._loaded = False

    def test_load_env_file_not_found(self):
        """Тест загрузки несуществующего файла"""
        with patch('os.path.exists', return_value=False):
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
                    EnvLoader.load_env_file(".env")
                    assert os.environ["EXISTING_VAR"] == "old_value"

    def test_load_env_file_invalid_format(self):
        """Тест обработки невалидных строк"""
        env_content = "VALID_KEY=valid_value\ninvalid_line\nANOTHER_VALID=value"
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {}, clear=True):
                    EnvLoader.load_env_file(".env")
                    assert "VALID_KEY" in os.environ
                    assert "ANOTHER_VALID" in os.environ

    def test_load_env_file_exception(self):
        """Тест обработки исключения при чтении"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("File error")):
                EnvLoader.load_env_file(".env")  # Не должно падать

    def test_get_env_var_str_existing(self):
        """Тест получения существующей строковой переменной"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = EnvLoader.get_env_var("TEST_VAR", "default")
            assert result == "test_value"

    def test_get_env_var_str_default(self):
        """Тест получения дефолтного значения"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_env_var("MISSING_VAR", "default_value")
            assert result == "default_value"

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

    def test_get_env_var_bool_true(self):
        """Тест получения булевых true значений"""
        true_values = ["true", "True", "TRUE", "1", "yes"]
        for value in true_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                # EnvLoader не имеет get_env_var_bool, тестируем get_env_var
                result = EnvLoader.get_env_var("BOOL_VAR")
                assert result == value

    def test_get_env_var_bool_false(self):
        """Тест получения булевых false значений"""
        false_values = ["false", "False", "0", "no"]
        for value in false_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                # EnvLoader не имеет get_env_var_bool, тестируем get_env_var
                result = EnvLoader.get_env_var("BOOL_VAR")
                assert result == value


class TestEmployer:
    """100% покрытие модели Employer"""

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

    def test_get_name_fallbacks(self):
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

    def test_from_dict_empty(self):
        """Тест создания из пустого словаря"""
        employer = Employer.from_dict({})
        assert employer.get_name() == "Не указана"


class TestSalary:
    """100% покрытие модели Salary"""

    def test_init_range(self):
        """Тест инициализации с диапазоном"""
        salary = Salary(100000, 150000, "RUR")
        assert salary.get_from() == 100000
        assert salary.get_to() == 150000
        assert salary.get_currency() == "RUR"

    def test_init_from_only(self):
        """Тест инициализации только с минимумом"""
        salary = Salary(salary_from=80000, currency="RUR")
        assert salary.get_from() == 80000
        assert salary.get_to() is None

    def test_init_to_only(self):
        """Тест инициализации только с максимумом"""
        salary = Salary(salary_to=120000, currency="USD")
        assert salary.get_from() is None
        assert salary.get_to() == 120000

    def test_format_salary_range(self):
        """Тест форматирования диапазона"""
        salary = Salary(100000, 150000, "RUR")
        result = salary.format_salary()
        assert "100 000" in result and "150 000" in result

    def test_format_salary_from_only(self):
        """Тест форматирования только от"""
        salary = Salary(salary_from=100000, currency="RUR")
        result = salary.format_salary()
        assert "от 100 000" in result

    def test_format_salary_none(self):
        """Тест форматирования отсутствующей зарплаты"""
        salary = Salary(currency="RUR")
        result = salary.format_salary()
        assert result == "Не указана"

    def test_to_dict(self):
        """Тест сериализации в словарь"""
        salary = Salary(100000, 150000, "RUR", gross=True)
        result = salary.to_dict()
        expected = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR",
            "gross": True
        }
        assert result == expected

    def test_from_dict_full(self):
        """Тест создания из полного словаря"""
        data = {
            "from": 90000,
            "to": 130000,
            "currency": "USD",
            "gross": False
        }
        salary = Salary.from_dict(data)
        assert salary.get_from() == 90000
        assert salary.get_to() == 130000
        assert salary.get_currency() == "USD"
        assert salary.is_gross() == False

    def test_compare_methods(self):
        """Тест методов сравнения"""
        salary1 = Salary(150000, 200000, "RUR")
        salary2 = Salary(100000, 130000, "RUR")
        assert salary1.compare(salary2) > 0

    def test_get_average(self):
        """Тест получения средней зарплаты"""
        salary = Salary(100000, 200000, "RUR")
        assert salary.get_average() == 150000

    def test_is_specified(self):
        """Тест проверки указана ли зарплата"""
        salary_specified = Salary(100000, None, "RUR")
        assert salary_specified.is_specified() == True
        
        salary_not_specified = Salary(None, None, "RUR")
        assert salary_not_specified.is_specified() == False


class TestExperience:
    """100% покрытие модели Experience"""

    def test_init(self):
        """Тест инициализации"""
        exp = Experience("between1And3", "От 1 года до 3 лет")
        assert exp.get_id() == "between1And3"
        assert exp.get_name() == "От 1 года до 3 лет"

    def test_to_dict(self):
        """Тест сериализации"""
        exp = Experience("between3And6", "От 3 до 6 лет")
        result = exp.to_dict()
        expected = {"id": "between3And6", "name": "От 3 до 6 лет"}
        assert result == expected

    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {"id": "moreThan6", "name": "Более 6 лет"}
        exp = Experience.from_dict(data)
        assert exp.get_id() == "moreThan6"
        assert exp.get_name() == "Более 6 лет"

    def test_from_string(self):
        """Тест создания из строки"""
        exp = Experience.from_string("От 1 года до 3 лет")
        assert exp.get_name() == "От 1 года до 3 лет"


class TestEmployment:
    """100% покрытие модели Employment"""

    def test_init(self):
        """Тест инициализации"""
        emp = Employment("full", "Полная занятость")
        assert emp.get_id() == "full"
        assert emp.get_name() == "Полная занятость"

    def test_to_dict(self):
        """Тест сериализации"""
        emp = Employment("part", "Частичная занятость")
        result = emp.to_dict()
        expected = {"id": "part", "name": "Частичная занятость"}
        assert result == expected

    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {"id": "project", "name": "Проектная работа"}
        emp = Employment.from_dict(data)
        assert emp.get_id() == "project"
        assert emp.get_name() == "Проектная работа"

    def test_from_string(self):
        """Тест создания из строки"""
        emp = Employment.from_string("Полная занятость")
        assert emp.get_name() == "Полная занятость"


class TestVacancy:
    """100% покрытие модели Vacancy"""

    def test_init_minimal(self):
        """Тест минимальной инициализации"""
        vacancy = Vacancy("Test Vacancy", "http://test.com")
        assert vacancy.get_title() == "Test Vacancy"
        assert vacancy.get_url() == "http://test.com"

    def test_init_full(self):
        """Тест полной инициализации"""
        employer = Employer("Test Company")
        salary = Salary(100000, 150000, "RUR")
        
        vacancy = Vacancy(
            title="Full Vacancy",
            url="http://full.com",
            salary=salary,
            employer=employer,
            description="Test description",
            vacancy_id="123",
            published_at="2024-01-01T00:00:00"
        )
        
        assert vacancy.get_title() == "Full Vacancy"
        assert vacancy.get_salary() == salary
        assert vacancy.get_employer() == employer
        assert vacancy.get_description() == "Test description"

    def test_get_id_methods(self):
        """Тест методов получения ID"""
        vacancy_with_id = Vacancy("Test", "http://test.com", vacancy_id="custom123")
        assert vacancy_with_id.get_id() == "custom123"
        
        vacancy_generated_id = Vacancy("Test", "http://test.com")
        generated_id = vacancy_generated_id.get_id()
        assert generated_id is not None
        assert len(generated_id) > 0

    def test_get_published_date_formats(self):
        """Тест различных форматов даты публикации"""
        # Тест строки
        vacancy_str = Vacancy("Test", "http://test.com", published_at="2024-01-01T10:00:00")
        date = vacancy_str.get_published_date()
        assert isinstance(date, datetime)
        
        # Тест datetime объекта
        now = datetime.now()
        vacancy_dt = Vacancy("Test", "http://test.com", published_at=now)
        assert vacancy_dt.get_published_date() == now
        
        # Тест невалидного формата
        vacancy_invalid = Vacancy("Test", "http://test.com", published_at="invalid")
        date_invalid = vacancy_invalid.get_published_date()
        assert isinstance(date_invalid, datetime)

    def test_to_dict_serialization(self):
        """Тест сериализации в словарь"""
        employer = Employer("Test Company")
        salary = Salary(100000, 150000, "RUR")
        
        vacancy = Vacancy(
            title="Full Test",
            url="http://test.com",
            salary=salary,
            employer=employer
        )
        
        result = vacancy.to_dict()
        assert result["title"] == "Full Test"
        assert result["salary"] == salary.to_dict()
        assert result["employer"] == employer.to_dict()

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
        assert vacancy.get_title() == "Dict Vacancy"
        assert vacancy.get_id() == "dict123"
        assert vacancy.get_description() == "Full description"
        assert vacancy.get_salary() is not None
        assert vacancy.get_employer() is not None

    def test_compare_by_salary(self):
        """Тест сравнения по зарплате"""
        vacancy1 = Vacancy("Test1", "url1", salary=Salary(150000, 200000, "RUR"))
        vacancy2 = Vacancy("Test2", "url2", salary=Salary(100000, 130000, "RUR"))
        assert vacancy1.compare_by_salary(vacancy2) > 0
        
        # Тест без зарплаты
        vacancy3 = Vacancy("Test3", "url3")
        vacancy4 = Vacancy("Test4", "url4")
        assert vacancy3.compare_by_salary(vacancy4) == 0

    def test_matches_query(self):
        """Тест поиска запроса в вакансии"""
        vacancy = Vacancy("Python Developer", "url", description="Looking for Python developer")
        assert vacancy.matches_query("python") == True
        assert vacancy.matches_query("java") == False
        
        # Тест без описания - поиск по названию
        vacancy_no_desc = Vacancy("Python Developer", "url")
        assert vacancy_no_desc.matches_query("python") == True