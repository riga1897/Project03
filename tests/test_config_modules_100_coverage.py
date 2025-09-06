"""
Тесты для всех модулей конфигурации с 100% покрытием
Покрывает: api_config, app_config, db_config, target_companies, ui_config, hh_api_config, sj_api_config
"""

import os
import sys
import tempfile
from unittest.mock import Mock, patch, mock_open

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config.api_config import APIConfig
from src.config.app_config import AppConfig
from src.config.db_config import DBConfig
from src.config.target_companies import TargetCompanies
from src.config.ui_config import UIConfig
from src.config.hh_api_config import HHAPIConfig
from src.config.sj_api_config import SJAPIConfig


class TestAPIConfig:
    """Тесты для APIConfig"""

    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        config = APIConfig()
        
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20
        assert config.hh_config is not None
        assert config.sj_config is not None

    def test_init_custom_values(self):
        """Тест инициализации с пользовательскими значениями"""
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
    """Тесты для AppConfig"""

    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig()
            
            assert config.default_storage_type == "postgres"
            assert config.storage_type == "postgres"
            assert config.db_config["host"] == "localhost"
            assert config.db_config["port"] == "5432"
            assert config.db_config["database"] == "Project03"

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
            assert config.db_config["username"] == "test_user"
            assert config.db_config["password"] == "test_pass"

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
        
        # Проверяем, что возвращается копия
        assert db_config == config.db_config
        assert db_config is not config.db_config

    def test_set_db_config(self):
        """Тест обновления конфигурации БД"""
        config = AppConfig()
        new_config = {"host": "new_host", "port": "9999"}
        
        config.set_db_config(new_config)
        
        assert config.db_config["host"] == "new_host"
        assert config.db_config["port"] == "9999"
        # Остальные параметры должны остаться
        assert "database" in config.db_config


class TestDBConfig:
    """Тесты для DBConfig"""

    @patch.dict(os.environ, {}, clear=True)
    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        config = DBConfig()
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "Project03"
        assert config.username == "postgres"
        assert config.password == ""

    def test_init_with_env_vars(self):
        """Тест инициализации с переменными окружения"""
        env_vars = {
            "PGHOST": "env_host",
            "PGPORT": "5433",
            "PGDATABASE": "env_db",
            "PGUSER": "env_user",
            "PGPASSWORD": "env_pass"
        }
        
        with patch.dict(os.environ, env_vars):
            config = DBConfig()
            
            assert config.host == "env_host"
            assert config.port == 5433
            assert config.database == "env_db"
            assert config.username == "env_user"
            assert config.password == "env_pass"

    def test_get_connection_string(self):
        """Тест получения строки подключения"""
        config = DBConfig()
        config.host = "test_host"
        config.port = 5432
        config.database = "test_db"
        config.username = "test_user"
        config.password = "test_pass"
        
        conn_str = config.get_connection_string()
        expected = "postgresql://test_user:test_pass@test_host:5432/test_db"
        assert conn_str == expected

    def test_get_connection_string_no_password(self):
        """Тест получения строки подключения без пароля"""
        config = DBConfig()
        config.host = "test_host"
        config.port = 5432
        config.database = "test_db"
        config.username = "test_user"
        config.password = ""
        
        conn_str = config.get_connection_string()
        expected = "postgresql://test_user:@test_host:5432/test_db"
        assert conn_str == expected


class TestTargetCompanies:
    """Тесты для TargetCompanies"""

    def test_init_default(self):
        """Тест инициализации по умолчанию"""
        companies = TargetCompanies()
        
        assert isinstance(companies.companies, list)
        assert len(companies.companies) > 0
        # Проверяем наличие известных компаний
        company_names = [comp["name"] for comp in companies.companies]
        assert any("Яндекс" in name for name in company_names)

    def test_get_all_companies(self):
        """Тест получения всех компаний"""
        companies = TargetCompanies()
        all_companies = companies.get_all_companies()
        
        assert isinstance(all_companies, list)
        assert len(all_companies) == len(companies.companies)

    def test_get_company_by_name_found(self):
        """Тест поиска компании по имени (найдена)"""
        companies = TargetCompanies()
        
        # Берем первую компанию
        first_company = companies.companies[0]
        found_company = companies.get_company_by_name(first_company["name"])
        
        assert found_company == first_company

    def test_get_company_by_name_not_found(self):
        """Тест поиска компании по имени (не найдена)"""
        companies = TargetCompanies()
        found_company = companies.get_company_by_name("Несуществующая компания")
        
        assert found_company is None

    def test_get_company_ids(self):
        """Тест получения списка ID компаний"""
        companies = TargetCompanies()
        ids = companies.get_company_ids()
        
        assert isinstance(ids, list)
        assert len(ids) == len(companies.companies)
        # Все элементы должны быть строками или числами
        assert all(isinstance(comp_id, (str, int)) for comp_id in ids)


class TestUIConfig:
    """Тесты для UIConfig"""

    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        config = UIConfig()
        
        assert config.items_per_page == 10
        assert config.max_description_length == 500
        assert config.show_salary == True
        assert config.show_experience == True
        assert config.date_format == "%Y-%m-%d"

    def test_init_custom_values(self):
        """Тест инициализации с пользовательскими значениями"""
        config = UIConfig(
            items_per_page=25,
            max_description_length=1000,
            show_salary=False,
            show_experience=False,
            date_format="%d.%m.%Y"
        )
        
        assert config.items_per_page == 25
        assert config.max_description_length == 1000
        assert config.show_salary == False
        assert config.show_experience == False
        assert config.date_format == "%d.%m.%Y"

    def test_get_pagination_config(self):
        """Тест получения конфигурации пагинации"""
        config = UIConfig(items_per_page=20)
        pagination = config.get_pagination_config()
        
        assert pagination == {"items_per_page": 20}

    def test_get_display_config(self):
        """Тест получения конфигурации отображения"""
        config = UIConfig(
            max_description_length=800,
            show_salary=False,
            show_experience=True,
            date_format="%Y/%m/%d"
        )
        
        display = config.get_display_config()
        expected = {
            "max_description_length": 800,
            "show_salary": False,
            "show_experience": True,
            "date_format": "%Y/%m/%d"
        }
        assert display == expected


class TestHHAPIConfig:
    """Тесты для HHAPIConfig"""

    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        config = HHAPIConfig()
        
        assert config.base_url == "https://api.hh.ru"
        assert config.per_page == 100
        assert config.timeout == 10
        assert config.user_agent == "VacancySearchApp/1.0"

    def test_init_custom_values(self):
        """Тест инициализации с пользовательскими значениями"""
        config = HHAPIConfig(
            base_url="https://custom.api.hh.ru",
            per_page=50,
            timeout=30,
            user_agent="CustomApp/2.0"
        )
        
        assert config.base_url == "https://custom.api.hh.ru"
        assert config.per_page == 50
        assert config.timeout == 30
        assert config.user_agent == "CustomApp/2.0"

    def test_get_vacancies_url(self):
        """Тест получения URL для вакансий"""
        config = HHAPIConfig()
        url = config.get_vacancies_url()
        
        assert url == "https://api.hh.ru/vacancies"

    def test_get_default_params(self):
        """Тест получения дефолтных параметров"""
        config = HHAPIConfig(per_page=75)
        params = config.get_default_params()
        
        assert params["per_page"] == 75
        assert "order_by" in params
        assert "search_field" in params


class TestSJAPIConfig:
    """Тесты для SJAPIConfig"""

    def test_init_default_values(self):
        """Тест инициализации с дефолтными значениями"""
        config = SJAPIConfig()
        
        assert config.base_url == "https://api.superjob.ru/2.0"
        assert config.per_page == 100
        assert config.timeout == 10
        assert config.api_key is None

    def test_init_with_api_key(self):
        """Тест инициализации с API ключом"""
        with patch.dict(os.environ, {"SUPERJOB_API_KEY": "test_key"}):
            config = SJAPIConfig()
            assert config.api_key == "test_key"

    def test_init_custom_values(self):
        """Тест инициализации с пользовательскими значениями"""
        config = SJAPIConfig(
            base_url="https://custom.superjob.ru/2.0",
            per_page=50,
            timeout=20,
            api_key="custom_key"
        )
        
        assert config.base_url == "https://custom.superjob.ru/2.0"
        assert config.per_page == 50
        assert config.timeout == 20
        assert config.api_key == "custom_key"

    def test_get_vacancies_url(self):
        """Тест получения URL для вакансий"""
        config = SJAPIConfig()
        url = config.get_vacancies_url()
        
        assert url == "https://api.superjob.ru/2.0/vacancies/"

    def test_get_headers_with_key(self):
        """Тест получения заголовков с API ключом"""
        config = SJAPIConfig(api_key="test_key_123")
        headers = config.get_headers()
        
        assert headers["X-Api-App-Id"] == "test_key_123"
        assert "User-Agent" in headers

    def test_get_headers_without_key(self):
        """Тест получения заголовков без API ключа"""
        config = SJAPIConfig(api_key=None)
        headers = config.get_headers()
        
        assert "X-Api-App-Id" not in headers
        assert "User-Agent" in headers

    def test_get_default_params(self):
        """Тест получения дефолтных параметров"""
        config = SJAPIConfig(per_page=80)
        params = config.get_default_params()
        
        assert params["count"] == 80
        assert "published" in params