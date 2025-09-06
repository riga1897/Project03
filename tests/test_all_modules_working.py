"""
Рабочие тесты для всех модулей src/ с максимальным покрытием
Исправлены импорты и зависимости
"""

import os
import sys
import tempfile
import time
from unittest.mock import Mock, patch, mock_open, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Config модули
from src.config.api_config import APIConfig
from src.config.app_config import AppConfig
from src.config.target_companies import TargetCompanies, CompanyInfo

# Utils модули
from src.utils.env_loader import EnvLoader

# API модули
from src.api_modules.base_api import BaseJobAPI


class TestAPIConfig:
    """Тесты для APIConfig - основного конфиг модуля"""

    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        config = APIConfig()
        
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20

    def test_init_custom_values(self):
        """Тест инициализации с пользовательскими значениями"""
        config = APIConfig(
            user_agent="CustomApp/2.0",
            timeout=30,
            request_delay=1.0,
            max_pages=50
        )
        
        assert config.user_agent == "CustomApp/2.0"
        assert config.timeout == 30
        assert config.request_delay == 1.0
        assert config.max_pages == 50

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
    """Тесты для AppConfig"""

    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        config = AppConfig()
        
        assert config.default_storage_type == "postgres"
        assert config.storage_type == "postgres"

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
        """Тест получения конфигурации БД"""
        config = AppConfig()
        db_config = config.get_db_config()
        
        assert isinstance(db_config, dict)
        assert "host" in db_config
        assert "port" in db_config

    def test_set_db_config(self):
        """Тест обновления конфигурации БД"""
        config = AppConfig()
        new_config = {"host": "new_host", "port": "9999"}
        
        config.set_db_config(new_config)
        
        assert config.db_config["host"] == "new_host"
        assert config.db_config["port"] == "9999"


class TestCompanyInfo:
    """Тесты для класса CompanyInfo"""

    def test_init_minimal(self):
        """Тест минимальной инициализации"""
        company = CompanyInfo(name="Test Company", hh_id="123")
        
        assert company.name == "Test Company"
        assert company.hh_id == "123"
        assert company.sj_id is None

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
    """Тесты для класса TargetCompanies"""

    def test_companies_list_exists(self):
        """Тест существования списка компаний"""
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
        """Тест поиска компании по имени (найдена)"""
        # Используем первую компанию из списка
        first_company = TargetCompanies.COMPANIES[0]
        found_company = TargetCompanies.get_company_by_name(first_company.name)
        
        assert found_company is not None
        assert found_company.name == first_company.name

    def test_get_company_by_name_not_found(self):
        """Тест поиска компании по имени (не найдена)"""
        found_company = TargetCompanies.get_company_by_name("Несуществующая компания")
        
        assert found_company is None

    def test_get_company_ids_hh(self):
        """Тест получения ID компаний для HH"""
        ids = TargetCompanies.get_company_ids("hh")
        
        assert isinstance(ids, list)
        assert len(ids) > 0
        assert all(isinstance(company_id, str) for company_id in ids)

    def test_get_company_ids_sj(self):
        """Тест получения ID компаний для SuperJob"""
        ids = TargetCompanies.get_company_ids("sj")
        
        assert isinstance(ids, list)
        # Некоторые компании могут не иметь SJ ID
        assert all(company_id is None or isinstance(company_id, str) for company_id in ids)

    def test_get_companies_for_source_hh(self):
        """Тест получения компаний для HH"""
        companies = TargetCompanies.get_companies_for_source("hh")
        
        assert isinstance(companies, list)
        assert len(companies) > 0

    def test_get_companies_for_source_sj(self):
        """Тест получения компаний для SuperJob"""
        companies = TargetCompanies.get_companies_for_source("sj")
        
        assert isinstance(companies, list)
        # Может быть меньше компаний, так как не все имеют SJ ID


class TestEnvLoader:
    """Тесты для EnvLoader"""

    def setup_method(self):
        """Сброс состояния перед каждым тестом"""
        EnvLoader._loaded = False

    def test_load_env_file_not_found(self):
        """Тест загрузки несуществующего .env файла"""
        with patch('os.path.exists', return_value=False):
            EnvLoader.load_env_file("nonexistent.env")
            assert EnvLoader._loaded == True

    def test_load_env_file_already_loaded(self):
        """Тест повторной загрузки когда уже загружено"""
        EnvLoader._loaded = True
        
        with patch('builtins.open', mock_open()) as mock_file:
            EnvLoader.load_env_file(".env")
            mock_file.assert_not_called()

    def test_load_env_file_success(self):
        """Тест успешной загрузки .env файла"""
        env_content = """
KEY1=value1
KEY2="value2"
KEY3='value3'
# Комментарий
KEY4=value4
        """.strip()
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch.dict(os.environ, {}, clear=True):
                    EnvLoader.load_env_file(".env")
                    
                    assert os.environ["KEY1"] == "value1"
                    assert os.environ["KEY2"] == "value2"
                    assert os.environ["KEY3"] == "value3"
                    assert os.environ["KEY4"] == "value4"

    def test_load_env_file_exception(self):
        """Тест обработки исключения при чтении файла"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("File error")):
                # Не должно падать
                EnvLoader.load_env_file(".env")

    def test_get_env_var_str_existing(self):
        """Тест получения существующей строковой переменной"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = EnvLoader.get_env_var_str("TEST_VAR", "default")
            assert result == "test_value"

    def test_get_env_var_str_default(self):
        """Тест получения дефолтного значения строковой переменной"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_env_var_str("MISSING_VAR", "default_value")
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

    def test_get_env_var_bool_true_values(self):
        """Тест получения булевых значений true"""
        true_values = ["true", "True", "TRUE", "1", "yes"]
        
        for value in true_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                result = EnvLoader.get_env_var_bool("BOOL_VAR", False)
                assert result == True

    def test_get_env_var_bool_false_values(self):
        """Тест получения булевых значений false"""
        false_values = ["false", "False", "FALSE", "0", "no"]
        
        for value in false_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                result = EnvLoader.get_env_var_bool("BOOL_VAR", True)
                assert result == False


class TestBaseJobAPI:
    """Тесты для BaseJobAPI"""

    def test_is_abstract_class(self):
        """Тест что BaseJobAPI - абстрактный класс"""
        with pytest.raises(TypeError):
            BaseJobAPI()

    def test_clear_cache_not_implemented(self):
        """Тест что clear_cache имеет дефолтную реализацию"""
        # Создаем конкретную реализацию для тестирования
        class TestAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return []
            def _validate_vacancy(self, vacancy):
                return True
        
        api = TestAPI()
        # Не должно падать
        api.clear_cache("test")


# Дополнительные тесты для модулей, которые можно безопасно импортировать
class TestModuleImports:
    """Тесты импорта всех основных модулей"""

    def test_config_modules_import(self):
        """Тест импорта config модулей"""
        from src.config.api_config import APIConfig
        from src.config.app_config import AppConfig
        from src.config.target_companies import TargetCompanies
        
        assert APIConfig is not None
        assert AppConfig is not None
        assert TargetCompanies is not None

    def test_utils_modules_import(self):
        """Тест импорта utils модулей"""
        from src.utils.env_loader import EnvLoader
        
        assert EnvLoader is not None

    def test_api_modules_import(self):
        """Тест импорта API модулей"""
        from src.api_modules.base_api import BaseJobAPI
        
        assert BaseJobAPI is not None

    def test_all_init_files_exist(self):
        """Тест существования всех __init__.py файлов"""
        init_files = [
            "src/__init__.py",
            "src/config/__init__.py",
            "src/api_modules/__init__.py",
            "src/utils/__init__.py"
        ]
        
        for init_file in init_files:
            assert os.path.exists(init_file), f"Отсутствует файл {init_file}"


# Интеграционные тесты для проверки взаимодействия модулей
class TestModuleIntegration:
    """Тесты интеграции между модулями"""

    def test_api_config_with_target_companies(self):
        """Тест интеграции APIConfig с TargetCompanies"""
        config = APIConfig()
        companies = TargetCompanies.get_all_companies()
        
        # Проверяем что конфигурация может использоваться с компаниями
        assert len(companies) > 0
        assert config.max_pages > 0

    def test_env_loader_with_app_config(self):
        """Тест интеграции EnvLoader с AppConfig"""
        # Загружаем env переменные
        EnvLoader.load_env_file(".env")  # Будет использовать системные переменные
        
        # Создаем конфигурацию приложения
        config = AppConfig()
        
        # Проверяем что конфигурация работает
        assert config.get_storage_type() == "postgres"

    def test_full_workflow_simulation(self):
        """Тест симуляции полного рабочего процесса"""
        # 1. Загружаем переменные окружения
        EnvLoader.load_env_file(".env")
        
        # 2. Создаем конфигурации
        api_config = APIConfig()
        app_config = AppConfig()
        
        # 3. Получаем список компаний
        companies = TargetCompanies.get_all_companies()
        
        # 4. Проверяем что все работает вместе
        assert api_config is not None
        assert app_config is not None
        assert len(companies) > 0
        
        # 5. Симулируем настройку параметров поиска
        search_params = api_config.get_pagination_params()
        company_ids = TargetCompanies.get_company_ids("hh")
        
        assert "max_pages" in search_params
        assert len(company_ids) > 0