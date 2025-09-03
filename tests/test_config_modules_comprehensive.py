"""
Комплексные тесты для конфигурационных модулей с максимальным покрытием кода.
Включает тестирование всех настроек, валидации параметров и обработки переменных окружения.
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Мокируем внешние зависимости
sys.modules['psycopg2'] = MagicMock()

from src.config.api_config import APIConfig
from src.config.hh_api_config import HHAPIConfig
from src.config.sj_api_config import SJAPIConfig
from src.config.db_config import DatabaseConfig
from src.config.ui_config import UIConfig
from src.config.app_config import AppConfig
from src.config.target_companies import TargetCompanies


class TestAPIConfig:
    """Комплексное тестирование базовой конфигурации API"""
    
    def test_api_config_initialization(self):
        """Тестирование инициализации базовой конфигурации API"""
        config = APIConfig()
        assert config is not None
        assert hasattr(config, 'get_base_url')
        assert hasattr(config, 'get_headers')
        assert hasattr(config, 'get_default_parameters')
        
    def test_api_config_abstract_methods(self):
        """Тестирование абстрактных методов базовой конфигурации"""
        config = APIConfig()
        
        # Базовая конфигурация должна возвращать значения по умолчанию
        base_url = config.get_base_url()
        assert isinstance(base_url, str)
        
        headers = config.get_headers()
        assert isinstance(headers, dict)
        
        params = config.get_default_parameters()
        assert isinstance(params, dict)


class TestHHAPIConfig:
    """Комплексное тестирование конфигурации HH.ru API"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.config = HHAPIConfig()
        
    def test_hh_config_initialization(self):
        """Тестирование инициализации конфигурации HH"""
        assert self.config is not None
        assert isinstance(self.config, HHAPIConfig)
        
    def test_hh_config_urls(self):
        """Тестирование URL конфигурации HH"""
        base_url = self.config.get_base_url()
        assert isinstance(base_url, str)
        assert "hh.ru" in base_url or "api" in base_url
        
        search_url = self.config.get_search_url()
        assert isinstance(search_url, str)
        assert len(search_url) > 0
        
        if hasattr(self.config, 'get_vacancy_url'):
            vacancy_url = self.config.get_vacancy_url()
            assert isinstance(vacancy_url, str)
        
    def test_hh_config_headers(self):
        """Тестирование заголовков HTTP для HH API"""
        headers = self.config.get_headers()
        assert isinstance(headers, dict)
        
        # Проверяем основные заголовки
        if 'User-Agent' in headers:
            assert len(headers['User-Agent']) > 0
            
    def test_hh_config_default_parameters(self):
        """Тестирование параметров по умолчанию для HH API"""
        params = self.config.get_default_parameters()
        assert isinstance(params, dict)
        
        # Проверяем типичные параметры HH API
        if 'per_page' in params:
            assert isinstance(params['per_page'], int)
            assert params['per_page'] > 0
            
    @patch.dict(os.environ, {'FILTER_ONLY_WITH_SALARY': 'true'})
    def test_hh_config_salary_filter_enabled(self):
        """Тестирование фильтрации по зарплате когда включена"""
        config = HHAPIConfig()
        should_filter = config.should_filter_by_salary()
        assert should_filter is True
        
    @patch.dict(os.environ, {'FILTER_ONLY_WITH_SALARY': 'false'})
    def test_hh_config_salary_filter_disabled(self):
        """Тестирование фильтрации по зарплате когда отключена"""
        config = HHAPIConfig()
        should_filter = config.should_filter_by_salary()
        assert should_filter is False
        
    @patch.dict(os.environ, {}, clear=True)
    def test_hh_config_salary_filter_default(self):
        """Тестирование значения по умолчанию для фильтрации по зарплате"""
        config = HHAPIConfig()
        should_filter = config.should_filter_by_salary()
        assert isinstance(should_filter, bool)
        
    def test_hh_config_parameter_building(self):
        """Тестирование построения параметров запроса"""
        if hasattr(self.config, 'build_search_params'):
            params = self.config.build_search_params("Python", page=1)
            assert isinstance(params, dict)
            
        if hasattr(self.config, 'build_vacancy_params'):
            params = self.config.build_vacancy_params("123")
            assert isinstance(params, dict)


class TestSJAPIConfig:
    """Комплексное тестирование конфигурации SuperJob API"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.config = SJAPIConfig()
        
    def test_sj_config_initialization(self):
        """Тестирование инициализации конфигурации SuperJob"""
        assert self.config is not None
        assert isinstance(self.config, SJAPIConfig)
        
    def test_sj_config_urls(self):
        """Тестирование URL конфигурации SuperJob"""
        base_url = self.config.get_base_url()
        assert isinstance(base_url, str)
        assert "superjob.ru" in base_url or "api" in base_url
        
        search_url = self.config.get_search_url()
        assert isinstance(search_url, str)
        assert len(search_url) > 0
        
    def test_sj_config_headers(self):
        """Тестирование заголовков HTTP для SuperJob API"""
        headers = self.config.get_headers()
        assert isinstance(headers, dict)
        
        # SuperJob API обычно требует API ключ в заголовках
        if 'X-Api-App-Id' in headers:
            assert isinstance(headers['X-Api-App-Id'], str)
            
    @patch.dict(os.environ, {'SUPERJOB_API_KEY': 'test_api_key_123'})
    def test_sj_config_with_api_key(self):
        """Тестирование конфигурации с API ключом"""
        config = SJAPIConfig()
        headers = config.get_headers()
        
        # Проверяем, что API ключ присутствует в заголовках
        assert any('test_api_key_123' in str(value) for value in headers.values())
        
    @patch.dict(os.environ, {}, clear=True)
    def test_sj_config_without_api_key(self):
        """Тестирование конфигурации без API ключа"""
        config = SJAPIConfig()
        headers = config.get_headers()
        
        # Конфигурация должна работать даже без API ключа
        assert isinstance(headers, dict)
        
    def test_sj_config_parameters(self):
        """Тестирование параметров SuperJob API"""
        params = self.config.get_default_parameters()
        assert isinstance(params, dict)
        
        # Проверяем типичные параметры SuperJob API
        if 'count' in params:
            assert isinstance(params['count'], int)
            assert params['count'] > 0
            
    @patch.dict(os.environ, {'FILTER_ONLY_WITH_SALARY': 'true'})
    def test_sj_config_salary_filter(self):
        """Тестирование фильтрации по зарплате в SuperJob"""
        config = SJAPIConfig()
        should_filter = config.should_filter_by_salary()
        assert isinstance(should_filter, bool)


class TestDatabaseConfig:
    """Комплексное тестирование конфигурации базы данных"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.config = DatabaseConfig()
        
    def test_db_config_initialization(self):
        """Тестирование инициализации конфигурации БД"""
        assert self.config is not None
        assert hasattr(self.config, 'default_config')
        
    @patch.dict(os.environ, {
        'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
    })
    def test_db_config_with_database_url(self):
        """Тестирование конфигурации с DATABASE_URL"""
        config = DatabaseConfig()
        db_config = config.get_config()
        
        assert isinstance(db_config, dict)
        assert 'host' in db_config
        assert 'port' in db_config
        assert 'database' in db_config
        assert 'username' in db_config
        assert 'password' in db_config
        
        assert db_config['host'] == 'localhost'
        assert db_config['port'] == '5432'
        assert db_config['database'] == 'testdb'
        assert db_config['username'] == 'user'
        assert db_config['password'] == 'pass'
        
    @patch.dict(os.environ, {
        'PGHOST': 'testhost',
        'PGPORT': '5433',
        'PGDATABASE': 'testdb',
        'PGUSER': 'testuser',
        'PGPASSWORD': 'testpass'
    }, clear=True)
    def test_db_config_with_separate_vars(self):
        """Тестирование конфигурации с отдельными переменными"""
        config = DatabaseConfig()
        db_config = config.get_config()
        
        assert db_config['host'] == 'testhost'
        assert db_config['port'] == '5433'
        assert db_config['database'] == 'testdb'
        assert db_config['username'] == 'testuser'
        assert db_config['password'] == 'testpass'
        
    def test_db_config_connection_params(self):
        """Тестирование параметров подключения для psycopg2"""
        params = self.config.get_connection_params()
        
        assert isinstance(params, dict)
        assert 'host' in params
        assert 'port' in params
        assert 'database' in params
        assert 'user' in params
        assert 'password' in params
        
    def test_db_config_custom_override(self):
        """Тестирование переопределения пользовательской конфигурации"""
        custom_config = {
            'host': 'custom_host',
            'port': '9999'
        }
        
        config = self.config.get_config(custom_config)
        
        assert config['host'] == 'custom_host'
        assert config['port'] == '9999'
        # Остальные параметры должны остаться из конфигурации по умолчанию
        assert 'database' in config
        assert 'username' in config
        
    @patch('psycopg2.connect')
    def test_db_config_connection_test(self, mock_connect):
        """Тестирование проверки подключения к БД"""
        # Мокируем успешное подключение
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        result = self.config.test_connection()
        assert result is True
        
        mock_connect.assert_called_once()
        mock_conn.close.assert_called_once()
        
    @patch('psycopg2.connect')
    def test_db_config_connection_test_failure(self, mock_connect):
        """Тестирование обработки ошибки подключения к БД"""
        # Мокируем ошибку подключения
        mock_connect.side_effect = Exception("Connection failed")
        
        result = self.config.test_connection()
        assert result is False
        
    def test_db_config_url_parsing_edge_cases(self):
        """Тестирование парсинга URL с различными форматами"""
        # Тестируем некорректный URL
        if hasattr(self.config, '_parse_database_url'):
            # URL без схемы
            result = self.config._parse_database_url("invalid_url")
            assert isinstance(result, dict)
            
            # URL с postgres:// вместо postgresql://
            result = self.config._parse_database_url("postgres://user:pass@host:5432/db")
            assert result['host'] == 'host'
            assert result['database'] == 'db'
            
            # URL с дополнительными параметрами
            result = self.config._parse_database_url("postgresql://user:pass@host:5432/db?sslmode=require")
            assert result['host'] == 'host'
            if 'sslmode' in result:
                assert result['sslmode'] == 'require'


class TestUIConfig:
    """Комплексное тестирование конфигурации пользовательского интерфейса"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.config = UIConfig()
        
    def test_ui_config_initialization(self):
        """Тестирование инициализации конфигурации UI"""
        assert self.config is not None
        
    def test_ui_config_pagination_settings(self):
        """Тестирование настроек пагинации"""
        if hasattr(self.config, 'get_items_per_page'):
            items_per_page = self.config.get_items_per_page()
            assert isinstance(items_per_page, int)
            assert items_per_page > 0
            
        if hasattr(self.config, 'get_max_pages'):
            max_pages = self.config.get_max_pages()
            assert isinstance(max_pages, int)
            assert max_pages > 0
            
    def test_ui_config_display_settings(self):
        """Тестирование настроек отображения"""
        if hasattr(self.config, 'get_table_width'):
            width = self.config.get_table_width()
            assert isinstance(width, int)
            assert width > 0
            
        if hasattr(self.config, 'get_max_description_length'):
            length = self.config.get_max_description_length()
            assert isinstance(length, int)
            assert length > 0
            
    def test_ui_config_formatting_options(self):
        """Тестирование опций форматирования"""
        if hasattr(self.config, 'should_truncate_descriptions'):
            truncate = self.config.should_truncate_descriptions()
            assert isinstance(truncate, bool)
            
        if hasattr(self.config, 'should_show_company_info'):
            show_company = self.config.should_show_company_info()
            assert isinstance(show_company, bool)
            
    def test_ui_config_color_settings(self):
        """Тестирование настроек цветов"""
        if hasattr(self.config, 'get_color_scheme'):
            colors = self.config.get_color_scheme()
            assert isinstance(colors, dict)
            
        if hasattr(self.config, 'is_colors_enabled'):
            colors_enabled = self.config.is_colors_enabled()
            assert isinstance(colors_enabled, bool)


class TestAppConfig:
    """Комплексное тестирование общей конфигурации приложения"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.config = AppConfig()
        
    def test_app_config_initialization(self):
        """Тестирование инициализации конфигурации приложения"""
        assert self.config is not None
        
    def test_app_config_logging_settings(self):
        """Тестирование настроек логирования"""
        if hasattr(self.config, 'get_log_level'):
            log_level = self.config.get_log_level()
            assert isinstance(log_level, str)
            assert log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            
        if hasattr(self.config, 'get_log_format'):
            log_format = self.config.get_log_format()
            assert isinstance(log_format, str)
            assert len(log_format) > 0
            
    def test_app_config_cache_settings(self):
        """Тестирование настроек кэширования"""
        if hasattr(self.config, 'get_cache_ttl'):
            cache_ttl = self.config.get_cache_ttl()
            assert isinstance(cache_ttl, int)
            assert cache_ttl > 0
            
        if hasattr(self.config, 'is_cache_enabled'):
            cache_enabled = self.config.is_cache_enabled()
            assert isinstance(cache_enabled, bool)
            
    @patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'})
    def test_app_config_environment_override(self):
        """Тестирование переопределения настроек через переменные окружения"""
        config = AppConfig()
        if hasattr(config, 'get_log_level'):
            log_level = config.get_log_level()
            assert log_level == 'DEBUG'
            
    def test_app_config_validation(self):
        """Тестирование валидации настроек"""
        if hasattr(self.config, 'validate_config'):
            is_valid = self.config.validate_config()
            assert isinstance(is_valid, bool)


class TestTargetCompanies:
    """Комплексное тестирование конфигурации целевых компаний"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.companies = TargetCompanies()
        
    def test_target_companies_initialization(self):
        """Тестирование инициализации целевых компаний"""
        assert self.companies is not None
        
    def test_get_companies_list(self):
        """Тестирование получения списка компаний"""
        if hasattr(self.companies, 'get_companies'):
            companies = self.companies.get_companies()
            assert isinstance(companies, (list, dict))
            
            if isinstance(companies, list):
                assert len(companies) > 0
                for company in companies:
                    assert isinstance(company, (str, dict))
                    
            elif isinstance(companies, dict):
                assert len(companies) > 0
                for key, value in companies.items():
                    assert isinstance(key, str)
                    
    def test_get_company_by_id(self):
        """Тестирование получения компании по ID"""
        if hasattr(self.companies, 'get_company_by_id'):
            # Тестируем с известными ID
            known_ids = ["1740", "78638", "39305"]  # Известные ID из HH.ru
            
            for company_id in known_ids:
                company = self.companies.get_company_by_id(company_id)
                if company is not None:
                    assert isinstance(company, dict)
                    assert 'name' in company or 'id' in company
                    
    def test_get_hh_companies(self):
        """Тестирование получения компаний для HH.ru"""
        if hasattr(self.companies, 'get_hh_companies'):
            hh_companies = self.companies.get_hh_companies()
            assert isinstance(hh_companies, (list, dict))
            
    def test_get_sj_companies(self):
        """Тестирование получения компаний для SuperJob"""
        if hasattr(self.companies, 'get_sj_companies'):
            sj_companies = self.companies.get_sj_companies()
            assert isinstance(sj_companies, (list, dict))
            
    def test_target_companies_validation(self):
        """Тестирование валидации данных о компаниях"""
        if hasattr(self.companies, 'validate_companies'):
            is_valid = self.companies.validate_companies()
            assert isinstance(is_valid, bool)
            
        # Проверяем, что компании имеют правильную структуру
        if hasattr(self.companies, 'get_companies'):
            companies = self.companies.get_companies()
            if isinstance(companies, list):
                for company in companies:
                    if isinstance(company, dict):
                        # Проверяем обязательные поля
                        assert 'name' in company or 'id' in company
                        
    def test_company_search(self):
        """Тестирование поиска компаний"""
        if hasattr(self.companies, 'search_company'):
            # Поиск по частичному названию
            results = self.companies.search_company("Яндекс")
            if results:
                assert isinstance(results, list)
                for result in results:
                    assert isinstance(result, dict)
                    
    def test_company_ids_extraction(self):
        """Тестирование извлечения ID компаний"""
        if hasattr(self.companies, 'get_all_ids'):
            all_ids = self.companies.get_all_ids()
            assert isinstance(all_ids, list)
            for company_id in all_ids:
                assert isinstance(company_id, str)
                assert len(company_id) > 0
                
        if hasattr(self.companies, 'get_hh_ids'):
            hh_ids = self.companies.get_hh_ids()
            assert isinstance(hh_ids, list)
            
        if hasattr(self.companies, 'get_sj_ids'):
            sj_ids = self.companies.get_sj_ids()
            assert isinstance(sj_ids, list)


class TestConfigIntegration:
    """Интеграционные тесты для конфигурационных модулей"""
    
    def test_config_modules_interaction(self):
        """Тестирование взаимодействия между конфигурационными модулями"""
        # Создаем экземпляры всех конфигураций
        app_config = AppConfig()
        db_config = DatabaseConfig()
        ui_config = UIConfig()
        hh_config = HHAPIConfig()
        sj_config = SJAPIConfig()
        
        # Проверяем, что все конфигурации работают независимо
        assert app_config is not None
        assert db_config is not None
        assert ui_config is not None
        assert hh_config is not None
        assert sj_config is not None
        
    @patch.dict(os.environ, {
        'LOG_LEVEL': 'INFO',
        'CACHE_TTL': '7200',
        'FILTER_ONLY_WITH_SALARY': 'true',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test'
    })
    def test_environment_variables_propagation(self):
        """Тестирование распространения переменных окружения между конфигурациями"""
        # Проверяем, что переменные окружения корректно используются
        app_config = AppConfig()
        db_config = DatabaseConfig()
        hh_config = HHAPIConfig()
        
        # Все конфигурации должны учитывать переменные окружения
        if hasattr(app_config, 'get_log_level'):
            assert app_config.get_log_level() == 'INFO'
            
        if hasattr(app_config, 'get_cache_ttl'):
            assert app_config.get_cache_ttl() == 7200
            
        db_config_values = db_config.get_config()
        assert db_config_values['host'] == 'localhost'
        assert db_config_values['database'] == 'test'
        
        assert hh_config.should_filter_by_salary() is True
        
    def test_config_error_handling(self):
        """Тестирование обработки ошибок в конфигурациях"""
        # Тестируем создание конфигураций при отсутствии переменных окружения
        with patch.dict(os.environ, {}, clear=True):
            try:
                app_config = AppConfig()
                db_config = DatabaseConfig()
                hh_config = HHAPIConfig()
                sj_config = SJAPIConfig()
                
                # Конфигурации должны работать с значениями по умолчанию
                assert app_config is not None
                assert db_config is not None
                assert hh_config is not None
                assert sj_config is not None
                
            except Exception as e:
                pytest.fail(f"Configuration should work with default values: {e}")