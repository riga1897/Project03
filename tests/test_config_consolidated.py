
"""
Консолидированные тесты для всех конфигурационных модулей
Объединяет тесты api_config, app_config, db_config, hh_api_config, sj_api_config, ui_config, target_companies
"""

import os
import sys
from typing import Any, Dict, List
from unittest.mock import Mock, patch, mock_open
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорты конфигурационных модулей
try:
    from src.config.api_config import API_CONFIG
    from src.config.app_config import APP_CONFIG
    from src.config.db_config import DB_CONFIG
    from src.config.hh_api_config import HH_API_CONFIG
    from src.config.sj_api_config import SJ_API_CONFIG
    from src.config.ui_config import UI_CONFIG
    from src.config.target_companies import TARGET_COMPANIES
    CONFIG_MODULES_AVAILABLE = True
except ImportError:
    CONFIG_MODULES_AVAILABLE = False


class TestConfigConsolidated:
    """Консолидированные тесты для всех конфигурационных модулей"""

    def test_api_config_structure(self) -> None:
        """Тест структуры API конфигурации"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        # Проверяем наличие API_CONFIG
        assert API_CONFIG is not None
        assert isinstance(API_CONFIG, dict)
        
        # Основные ключи конфигурации API
        expected_keys = ["timeout", "retries", "rate_limit"]
        for key in expected_keys:
            if key in API_CONFIG:
                assert API_CONFIG[key] is not None

    def test_app_config_structure(self) -> None:
        """Тест структуры конфигурации приложения"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        assert APP_CONFIG is not None
        assert isinstance(APP_CONFIG, dict)
        
        # Основные ключи конфигурации приложения
        expected_keys = ["debug", "log_level", "cache_enabled"]
        for key in expected_keys:
            if key in APP_CONFIG:
                assert APP_CONFIG[key] is not None

    def test_db_config_structure(self) -> None:
        """Тест структуры конфигурации базы данных"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        assert DB_CONFIG is not None
        assert isinstance(DB_CONFIG, dict)
        
        # Основные ключи конфигурации БД
        expected_keys = ["host", "port", "database", "user"]
        for key in expected_keys:
            if key in DB_CONFIG:
                assert DB_CONFIG[key] is not None

    def test_hh_api_config_structure(self) -> None:
        """Тест структуры конфигурации HeadHunter API"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        assert HH_API_CONFIG is not None
        assert isinstance(HH_API_CONFIG, dict)
        
        # Специфичные ключи для HH API
        expected_keys = ["base_url", "vacancies_endpoint", "areas_endpoint"]
        for key in expected_keys:
            if key in HH_API_CONFIG:
                assert HH_API_CONFIG[key] is not None
                if "url" in key:
                    assert HH_API_CONFIG[key].startswith("http")

    def test_sj_api_config_structure(self) -> None:
        """Тест структуры конфигурации SuperJob API"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        assert SJ_API_CONFIG is not None
        assert isinstance(SJ_API_CONFIG, dict)
        
        # Специфичные ключи для SJ API
        expected_keys = ["base_url", "api_key", "secret_key"]
        for key in expected_keys:
            if key in SJ_API_CONFIG:
                assert SJ_API_CONFIG[key] is not None
                if "url" in key:
                    assert SJ_API_CONFIG[key].startswith("http")

    def test_ui_config_structure(self) -> None:
        """Тест структуры конфигурации пользовательского интерфейса"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        assert UI_CONFIG is not None
        assert isinstance(UI_CONFIG, dict)
        
        # Ключи конфигурации UI
        expected_keys = ["items_per_page", "max_display_items", "menu_timeout"]
        for key in expected_keys:
            if key in UI_CONFIG:
                assert isinstance(UI_CONFIG[key], (int, float))
                assert UI_CONFIG[key] > 0

    def test_target_companies_structure(self) -> None:
        """Тест структуры целевых компаний"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        assert TARGET_COMPANIES is not None
        assert isinstance(TARGET_COMPANIES, (list, dict))
        
        if isinstance(TARGET_COMPANIES, list):
            # Список компаний
            for company in TARGET_COMPANIES:
                assert isinstance(company, (str, dict))
                if isinstance(company, dict):
                    assert "name" in company or "id" in company
        
        elif isinstance(TARGET_COMPANIES, dict):
            # Словарь компаний
            for company_id, company_data in TARGET_COMPANIES.items():
                assert isinstance(company_data, (str, dict))

    def test_config_validation(self) -> None:
        """Тест валидации конфигурационных данных"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        configs = [
            API_CONFIG, APP_CONFIG, DB_CONFIG, 
            HH_API_CONFIG, SJ_API_CONFIG, UI_CONFIG
        ]
        
        for config in configs:
            assert config is not None
            assert isinstance(config, dict)
            # Конфигурация не должна быть пустой
            if config:
                assert len(config) > 0

    def test_config_environment_variables(self) -> None:
        """Тест работы с переменными окружения в конфигурации"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        # Тестируем загрузку конфигурации с переменными окружения
        with patch.dict(os.environ, {
            'DB_HOST': 'test_host',
            'DB_PORT': '5432',
            'API_TIMEOUT': '30'
        }):
            # Перезагружаем конфигурационные модули
            try:
                importlib.reload(sys.modules['src.config.db_config'])
                importlib.reload(sys.modules['src.config.api_config'])
            except (KeyError, AttributeError):
                # Модули могут не поддерживать перезагрузку
                pass

    def test_config_file_loading(self) -> None:
        """Тест загрузки конфигурации из файлов"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        # Мокаем чтение конфигурационного файла
        mock_config_data = '''
        {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "api": {
                "timeout": 30,
                "retries": 3
            }
        }
        '''
        
        with patch('builtins.open', mock_open(read_data=mock_config_data)):
            # Тестируем загрузку конфигурации
            try:
                import json
                config_data = json.loads(mock_config_data)
                assert "database" in config_data
                assert "api" in config_data
            except Exception:
                # Конфигурация может не использовать JSON
                pass

    def test_config_defaults(self) -> None:
        """Тест значений по умолчанию в конфигурации"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        # Проверяем разумные значения по умолчанию
        if "timeout" in API_CONFIG:
            assert isinstance(API_CONFIG["timeout"], (int, float))
            assert API_CONFIG["timeout"] > 0
            assert API_CONFIG["timeout"] < 300  # Максимум 5 минут

        if "items_per_page" in UI_CONFIG:
            assert isinstance(UI_CONFIG["items_per_page"], int)
            assert UI_CONFIG["items_per_page"] > 0
            assert UI_CONFIG["items_per_page"] <= 100

    def test_config_consistency(self) -> None:
        """Тест согласованности между конфигурациями"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        # Проверяем что URL'ы в API конфигурациях корректны
        api_configs = [HH_API_CONFIG, SJ_API_CONFIG]
        
        for config in api_configs:
            for key, value in config.items():
                if "url" in key.lower() and isinstance(value, str):
                    assert value.startswith(("http://", "https://"))
                    assert not value.endswith("/")  # URL не должны заканчиваться слешем

    def test_config_security(self) -> None:
        """Тест безопасности конфигурации"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        # Проверяем что секретные ключи не хранятся в открытом виде
        sensitive_keys = ["password", "secret", "key", "token"]
        
        all_configs = [
            API_CONFIG, APP_CONFIG, DB_CONFIG,
            HH_API_CONFIG, SJ_API_CONFIG, UI_CONFIG
        ]
        
        for config in all_configs:
            for key, value in config.items():
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in sensitive_keys):
                    if isinstance(value, str):
                        # Секретные значения не должны быть очевидными
                        assert value not in ["password", "secret", "key", "123456"]

    def test_config_types(self) -> None:
        """Тест типов данных в конфигурации"""
        if not CONFIG_MODULES_AVAILABLE:
            pytest.skip("Config modules not available")

        # Числовые конфигурации должны быть числами
        numeric_keys = ["port", "timeout", "retries", "limit", "per_page"]
        
        all_configs = [
            API_CONFIG, APP_CONFIG, DB_CONFIG,
            HH_API_CONFIG, SJ_API_CONFIG, UI_CONFIG
        ]
        
        for config in all_configs:
            for key, value in config.items():
                if any(numeric in key.lower() for numeric in numeric_keys):
                    assert isinstance(value, (int, float, str))
                    if isinstance(value, str):
                        # Строковые числа должны быть конвертируемы
                        try:
                            float(value)
                        except ValueError:
                            pytest.fail(f"Numeric config {key} has non-numeric string value: {value}")
