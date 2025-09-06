"""
100% покрытие всех config модулей
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.config.hh_api_config import HHAPIConfig
from src.config.sj_api_config import SJAPIConfig  
from src.config.db_config import DatabaseConfig
from src.config.ui_config import UIConfig, UIPaginationConfig


class TestHHAPIConfig:
    """100% покрытие HHAPIConfig"""

    def test_init_default_values(self):
        """Тест дефолтной инициализации"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            config = HHAPIConfig()
            assert config.area == 113
            assert config.per_page == 50
            assert config.only_with_salary == False
            assert config.period == 15
            assert config.custom_params == {}

    def test_post_init_env_loading(self):
        """Тест загрузки настроек из env переменных"""
        # Тест true значений
        true_values = ["true", "1", "yes", "on", "TRUE", "Yes", "ON"]
        for value in true_values:
            with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": value}):
                config = HHAPIConfig()
                assert config.only_with_salary == True

        # Тест false значений
        false_values = ["false", "0", "no", "off", "FALSE"]
        for value in false_values:
            with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": value}):
                config = HHAPIConfig()
                assert config.only_with_salary == False

    def test_get_params_default(self):
        """Тест получения дефолтных параметров"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            config = HHAPIConfig()
            params = config.get_params()
            
            expected = {
                "area": 113,
                "per_page": 50, 
                "only_with_salary": False,
                "period": 15
            }
            assert params == expected

    def test_get_params_with_overrides(self):
        """Тест переопределения параметров"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            config = HHAPIConfig()
            params = config.get_params(
                area=1,
                per_page=100,
                only_with_salary=True,
                period=30,
                extra_param="test"
            )
            
            assert params["area"] == 1
            assert params["per_page"] == 100
            assert params["only_with_salary"] == True
            assert params["period"] == 30
            assert params["extra_param"] == "test"

    def test_get_params_with_custom_params(self):
        """Тест с пользовательскими параметрами"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            config = HHAPIConfig()
            config.custom_params = {"custom1": "value1", "custom2": "value2"}
            
            params = config.get_params(custom2="overridden")
            
            assert params["custom1"] == "value1"
            assert params["custom2"] == "overridden"

    def test_get_hh_params_compatibility(self):
        """Тест совместимости метода get_hh_params"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            config = HHAPIConfig()
            
            params1 = config.get_params(area=1)
            params2 = config.get_hh_params(area=1)
            
            assert params1 == params2


class TestSJAPIConfig:
    """100% покрытие SJAPIConfig"""

    def test_init_default_values(self):
        """Тест дефолтной инициализации"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            config = SJAPIConfig()
            assert config.count == 500
            assert config.published == 15
            assert config.only_with_salary == False
            assert config.custom_params is None
            assert config.per_page == 100
            assert config.max_total_pages == 20
            assert config.filter_by_target_companies == True
            assert config.token_file == Path("token.json")

    def test_init_with_custom_token_file(self):
        """Тест инициализации с пользовательским файлом токена"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            custom_path = Path("custom_token.json")
            config = SJAPIConfig(token_file=custom_path)
            assert config.token_file == custom_path

    def test_init_with_kwargs(self):
        """Тест инициализации с дополнительными параметрами"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "true"}):
            config = SJAPIConfig(
                count=100,
                published=30,
                per_page=50,
                custom_attr="test_value"
            )
            assert config.count == 100
            assert config.published == 30
            assert config.per_page == 50
            assert config.custom_attr == "test_value"
            assert config.only_with_salary == True

    def test_env_loading_in_init(self):
        """Тест загрузки переменных окружения в __init__"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "yes"}):
            config = SJAPIConfig()
            assert config.only_with_salary == True

        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "no"}):
            config = SJAPIConfig()
            assert config.only_with_salary == False

    def test_get_params_default(self):
        """Тест получения дефолтных параметров"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            config = SJAPIConfig()
            params = config.get_params()
            
            expected = {
                "count": 500,
                "order_field": "date",
                "order_direction": "desc",
                "published": 15,
                "no_agreement": 0
            }
            assert params == expected

    def test_get_params_with_overrides(self):
        """Тест переопределения параметров"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            config = SJAPIConfig()
            params = config.get_params(
                count=100,
                order_field="salary",
                order_direction="asc",
                published=30,
                only_with_salary=True,
                page=2,
                town="Moscow"
            )
            
            assert params["count"] == 100
            assert params["order_field"] == "salary"
            assert params["order_direction"] == "asc"
            assert params["published"] == 30
            assert params["no_agreement"] == 1
            assert params["page"] == 2
            assert params["town"] == "Moscow"

    def test_get_params_with_custom_params(self):
        """Тест с пользовательскими параметрами"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            config = SJAPIConfig()
            config.custom_params = {"custom1": "value1", "custom2": "value2"}
            
            params = config.get_params(custom2="overridden")
            
            assert params["custom1"] == "value1"
            assert params["custom2"] == "overridden"

    @patch('src.utils.file_handlers.json_handler.write_json')
    def test_save_token_success(self, mock_write_json):
        """Тест успешного сохранения токена"""
        config = SJAPIConfig()
        test_token = "test_token_123"
        
        config.save_token(test_token)
        
        mock_write_json.assert_called_once_with(
            config.token_file,
            [{"superjob_api_key": test_token}]
        )

    @patch('src.utils.file_handlers.json_handler.write_json')
    def test_save_token_error(self, mock_write_json):
        """Тест обработки ошибки при сохранении токена"""
        mock_write_json.side_effect = Exception("Write error")
        
        config = SJAPIConfig()
        
        with pytest.raises(Exception, match="Write error"):
            config.save_token("test_token")


class TestDatabaseConfig:
    """100% покрытие DatabaseConfig"""

    def test_init_creates_default_config(self):
        """Тест создания дефолтной конфигурации"""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig()
            assert config.default_config is not None
            assert isinstance(config.default_config, dict)

    def test_get_default_config_with_database_url(self):
        """Тест получения конфигурации из DATABASE_URL"""
        database_url = "postgresql://user:pass@host:5432/dbname"
        
        with patch.dict(os.environ, {"DATABASE_URL": database_url}):
            with patch.object(DatabaseConfig, '_parse_database_url') as mock_parse:
                mock_parse.return_value = {"parsed": "config"}
                
                config = DatabaseConfig()
                mock_parse.assert_called_once_with(database_url)

    def test_get_default_config_with_separate_vars(self):
        """Тест получения конфигурации из отдельных переменных"""
        env_vars = {
            "PGHOST": "test_host",
            "PGPORT": "5433", 
            "PGDATABASE": "test_db",
            "PGUSER": "test_user",
            "PGPASSWORD": "test_pass",
            "PGCONNECT_TIMEOUT": "20",
            "PGCOMMAND_TIMEOUT": "60"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            
            assert config.default_config["host"] == "test_host"
            assert config.default_config["port"] == "5433"
            assert config.default_config["database"] == "test_db"
            assert config.default_config["username"] == "test_user"
            assert config.default_config["password"] == "test_pass"
            assert config.default_config["connect_timeout"] == "20"
            assert config.default_config["command_timeout"] == "60"

    def test_get_default_config_fallback_values(self):
        """Тест дефолтных значений при отсутствии переменных"""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig()
            
            assert config.default_config["host"] == "localhost"
            assert config.default_config["port"] == "5432"
            assert config.default_config["database"] == "job_search_app"
            assert config.default_config["username"] == "postgres"
            assert config.default_config["password"] == ""
            assert config.default_config["connect_timeout"] == "10"
            assert config.default_config["command_timeout"] == "30"

    def test_get_config_without_custom(self):
        """Тест получения конфигурации без пользовательских параметров"""
        with patch.dict(os.environ, {"PGHOST": "test_host", "DATABASE_URL": ""}):
            config = DatabaseConfig()
            result = config.get_config()
            
            assert result is config.default_config
            assert result["host"] == "test_host"

    def test_get_config_with_custom(self):
        """Тест получения конфигурации с пользовательскими параметрами"""
        with patch.dict(os.environ, {"PGHOST": "original_host", "DATABASE_URL": "", "PGDATABASE": "job_search_app"}):
            config = DatabaseConfig()
            
            custom_config = {"host": "custom_host", "port": "9999"}
            result = config.get_config(custom_config)
            
            assert result["host"] == "custom_host"
            assert result["port"] == "9999"
            assert result["database"] == "job_search_app"  # Остальные дефолтные
            
            # Проверяем что оригинальная конфигурация не изменилась
            assert config.default_config["host"] == "original_host"

    def test_get_connection_params_basic(self):
        """Тест получения параметров подключения"""
        env_vars = {
            "PGHOST": "conn_host",
            "PGPORT": "5433",
            "PGDATABASE": "conn_db", 
            "PGUSER": "conn_user",
            "PGPASSWORD": "conn_pass"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            params = config.get_connection_params()
            
            expected = {
                "host": "conn_host",
                "port": "5433",
                "database": "conn_db",
                "user": "conn_user",
                "password": "conn_pass"
            }
            assert params == expected

    def test_get_connection_params_with_ssl(self):
        """Тест получения параметров подключения с SSL"""
        with patch.dict(os.environ, {"PGHOST": "ssl_host"}):
            config = DatabaseConfig()
            config.default_config["sslmode"] = "require"
            
            params = config.get_connection_params()
            assert params["sslmode"] == "require"

    def test_parse_database_url_complete(self):
        """Тест парсинга полного DATABASE_URL"""
        config = DatabaseConfig()
        
        # Тест полного URL без моков
        url = "postgresql://user:pass@host:5432/dbname"
        result = config._parse_database_url(url)
        
        assert result["host"] == "host"
        assert result["port"] == "5432"
        assert result["database"] == "dbname"
        assert result["username"] == "user"
        assert result["password"] == "pass"

    def test_parse_database_url_minimal(self):
        """Тест парсинга минимального DATABASE_URL"""
        config = DatabaseConfig()
        
        # Тест реального парсинга без моков
        url = "postgresql://host/dbname"
        result = config._parse_database_url(url)
        
        assert result["host"] == "host"
        assert result["port"] == "5432"
        assert result["database"] == "dbname"
        assert result["username"] == ""  # пустая строка если не указано
        assert result["password"] == ""

    def test_parse_database_url_with_query_params(self):
        """Тест парсинга DATABASE_URL с query параметрами"""
        config = DatabaseConfig()
        
        # Тест с SSL параметром
        url = "postgresql://user:pass@host:5432/dbname?sslmode=require"
        result = config._parse_database_url(url)
        
        assert result["host"] == "host"
        assert result["database"] == "dbname"
        assert result["sslmode"] == "require"

    def test_parse_database_url_error_handling(self):
        """Тест обработки ошибок парсинга URL"""
        config = DatabaseConfig()
        
        # Невалидный URL должен вернуть дефолтные значения
        invalid_url = "invalid://malformed/url"
        with patch('builtins.print'):  # Подавляем вывод ошибки
            result = config._parse_database_url(invalid_url)
            
        assert result["host"] == "localhost"
        assert result["port"] == "5432"
        assert result["database"] == "job_search_app"


class TestUIConfig:
    """100% покрытие UIConfig"""

    def test_init_default_values(self):
        """Тест дефолтной инициализации"""
        config = UIConfig()
        assert config.items_per_page == 5
        assert config.max_display_items == 20

    def test_init_custom_values(self):
        """Тест инициализации с пользовательскими значениями"""
        config = UIConfig(items_per_page=15, max_display_items=50)
        assert config.items_per_page == 15
        assert config.max_display_items == 50

    def test_get_pagination_settings_default(self):
        """Тест получения дефолтных настроек пагинации"""
        config = UIConfig()
        settings = config.get_pagination_settings()
        
        expected = {
            "items_per_page": 5,
            "max_display_items": 20
        }
        assert settings == expected

    def test_get_pagination_settings_with_overrides(self):
        """Тест получения настроек пагинации с переопределениями"""
        config = UIConfig(items_per_page=10, max_display_items=30)
        settings = config.get_pagination_settings(
            items_per_page=25,
            max_display_items=100
        )
        
        expected = {
            "items_per_page": 25,
            "max_display_items": 100
        }
        assert settings == expected


class TestUIPaginationConfig:
    """100% покрытие UIPaginationConfig"""

    def test_init_default_values(self):
        """Тест дефолтной инициализации"""
        config = UIPaginationConfig()
        assert config.default_items_per_page == 10
        assert config.search_results_per_page == 5
        assert config.saved_vacancies_per_page == 10
        assert config.top_vacancies_per_page == 10
        assert config.max_items_per_page == 50
        assert config.min_items_per_page == 1

    def test_get_items_per_page_default(self):
        """Тест получения количества элементов по умолчанию"""
        config = UIPaginationConfig()
        result = config.get_items_per_page()
        assert result == 10

    def test_get_items_per_page_search_context(self):
        """Тест для контекста поиска"""
        config = UIPaginationConfig()
        result = config.get_items_per_page("search")
        assert result == 5

    def test_get_items_per_page_saved_context(self):
        """Тест для контекста сохраненных вакансий"""
        config = UIPaginationConfig()
        result = config.get_items_per_page("saved")
        assert result == 10

    def test_get_items_per_page_top_context(self):
        """Тест для контекста топ-списков"""
        config = UIPaginationConfig()
        result = config.get_items_per_page("top")
        assert result == 10

    def test_get_items_per_page_unknown_context(self):
        """Тест для неизвестного контекста"""
        config = UIPaginationConfig()
        result = config.get_items_per_page("unknown")
        assert result == 10  # должен вернуть default

    def test_validate_items_per_page_normal(self):
        """Тест валидации нормального значения"""
        config = UIPaginationConfig()
        result = config.validate_items_per_page(25)
        assert result == 25

    def test_validate_items_per_page_too_small(self):
        """Тест валидации слишком маленького значения"""
        config = UIPaginationConfig()
        result = config.validate_items_per_page(0)
        assert result == 1

    def test_validate_items_per_page_too_large(self):
        """Тест валидации слишком большого значения"""
        config = UIPaginationConfig()
        result = config.validate_items_per_page(100)
        assert result == 50


class TestConfigModulesIntegration:
    """Интеграционные тесты config модулей"""

    def test_all_configs_work_together(self):
        """Тест что все конфигурации работают вместе"""
        with patch.dict(os.environ, {
            "FILTER_ONLY_WITH_SALARY": "true",
            "PGHOST": "test_host",
            "DATABASE_URL": ""
        }):
            # Создаем все конфигурации
            hh_config = HHAPIConfig()
            sj_config = SJAPIConfig()
            db_config = DatabaseConfig()
            ui_config = UIConfig()
            
            # Проверяем что они корректно инициализированы
            assert hh_config.only_with_salary == True
            assert sj_config.only_with_salary == True
            assert db_config.default_config["host"] == "test_host"
            assert ui_config.items_per_page == 5

    def test_configs_env_isolation(self):
        """Тест изоляции конфигураций от переменных окружения"""
        # Каждая конфигурация должна работать независимо
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            hh_config = HHAPIConfig()
            
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "true"}):
            sj_config = SJAPIConfig()
            
        # Конфигурации должны отражать свое окружение
        assert hh_config.only_with_salary == False
        assert sj_config.only_with_salary == True

    @patch('psycopg2.connect')
    def test_database_test_connection_success(self, mock_connect):
        """Тест успешного тестирования подключения к БД"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        config = DatabaseConfig()
        result = config.test_connection()
        
        assert result == True
        mock_connection.close.assert_called_once()

    @patch('psycopg2.connect')
    def test_database_test_connection_failure(self, mock_connect):
        """Тест неуспешного тестирования подключения к БД"""
        mock_connect.side_effect = Exception("Connection failed")
        
        config = DatabaseConfig()
        with patch('builtins.print'):  # Подавляем вывод ошибки
            result = config.test_connection()
        
        assert result == False

    def test_error_handling(self):
        """Тест обработки ошибок в конфигурациях"""
        # Тест обработки ошибки в SJAPIConfig при сохранении токена
        with patch('src.utils.file_handlers.json_handler.write_json') as mock_write:
            mock_write.side_effect = IOError("Permission denied")
            
            config = SJAPIConfig()
            with pytest.raises(IOError):
                config.save_token("test_token")

    def test_parameter_override_consistency(self):
        """Тест консистентности переопределения параметров"""
        with patch.dict(os.environ, {"FILTER_ONLY_WITH_SALARY": "false"}):
            hh_config = HHAPIConfig()
            sj_config = SJAPIConfig()
            
            # Оба API должны поддерживать переопределение только_с_зарплатой
            hh_params = hh_config.get_params(only_with_salary=True)
            sj_params = sj_config.get_params(only_with_salary=True)
            
            assert hh_params["only_with_salary"] == True
            assert sj_params["no_agreement"] == 1  # SuperJob использует no_agreement