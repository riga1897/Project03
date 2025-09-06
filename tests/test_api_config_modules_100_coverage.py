"""
100% покрытие config API модулей: api_config.py, hh_api_config.py, sj_api_config.py
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest
from typing import Any, Dict, Optional
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.config.api_config import APIConfig
from src.config.hh_api_config import HHAPIConfig  
from src.config.sj_api_config import SJAPIConfig


class TestAPIConfig:
    """100% покрытие APIConfig"""

    @patch('src.utils.env_loader.EnvLoader')
    def test_api_config_init_defaults(self, mock_env):
        """Тест инициализации APIConfig с дефолтными параметрами - покрывает строки 33-38"""
        mock_env.get_env_var.return_value = "false"
        
        config = APIConfig()
        
        # Проверяем дефолтные значения
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20
        assert isinstance(config.hh_config, HHAPIConfig)
        assert isinstance(config.sj_config, SJAPIConfig)

    @patch('src.utils.env_loader.EnvLoader')
    def test_api_config_init_custom_params(self, mock_env):
        """Тест инициализации APIConfig с кастомными параметрами"""
        mock_env.get_env_var.return_value = "false"
        
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
        assert config.hh_config is custom_hh_config

    @patch('src.utils.env_loader.EnvLoader')
    def test_api_config_get_pagination_params_defaults(self, mock_env):
        """Тест метода get_pagination_params с дефолтными значениями - покрывает строку 50"""
        mock_env.get_env_var.return_value = "false"
        
        config = APIConfig(max_pages=25)
        result = config.get_pagination_params()
        
        assert result == {"max_pages": 25}

    @patch('src.utils.env_loader.EnvLoader')
    def test_api_config_get_pagination_params_override(self, mock_env):
        """Тест метода get_pagination_params с переопределением параметров"""
        mock_env.get_env_var.return_value = "false"
        
        config = APIConfig(max_pages=10)
        result = config.get_pagination_params(max_pages=100)
        
        assert result == {"max_pages": 100}


class TestHHAPIConfig:
    """100% покрытие HHAPIConfig"""

    @patch('src.utils.env_loader.EnvLoader')
    def test_hh_api_config_init_defaults(self, mock_env):
        """Тест инициализации HHAPIConfig с дефолтными значениями - покрывает строки 11-15"""
        mock_env.get_env_var.return_value = "false"
        
        config = HHAPIConfig()
        
        assert config.area == 113
        assert config.per_page == 50
        assert config.only_with_salary is False
        assert config.period == 15
        assert config.custom_params == {}

    @patch.dict('os.environ', {'FILTER_ONLY_WITH_SALARY': 'true'}, clear=False)
    def test_hh_api_config_post_init_true_values(self):
        """Тест __post_init__ с различными true значениями - покрывает строки 19-20"""
        config = HHAPIConfig()
        assert config.only_with_salary is True

    @patch.dict('os.environ', {'FILTER_ONLY_WITH_SALARY': 'false'}, clear=False)
    def test_hh_api_config_post_init_false_values(self):
        """Тест __post_init__ с различными false значениями"""
        config = HHAPIConfig()
        assert config.only_with_salary is False

    @patch('src.utils.env_loader.EnvLoader')
    def test_hh_api_config_get_params_defaults(self, mock_env):
        """Тест метода get_params без переопределений - покрывает строки 24-33"""
        mock_env.get_env_var.return_value = "false"
        
        config = HHAPIConfig()
        config.custom_params = {"test_param": "test_value"}
        
        result = config.get_params()
        
        expected = {
            "area": 113,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15,
            "test_param": "test_value"
        }
        assert result == expected

    @patch('src.utils.env_loader.EnvLoader')
    def test_hh_api_config_get_params_with_overrides(self, mock_env):
        """Тест метода get_params с переопределениями"""
        mock_env.get_env_var.return_value = "false"
        
        config = HHAPIConfig()
        result = config.get_params(
            area=1,
            per_page=100,
            only_with_salary=True,
            period=30,
            custom_override="override_value"
        )
        
        expected = {
            "area": 1,
            "per_page": 100,
            "only_with_salary": True,
            "period": 30,
            "custom_override": "override_value"
        }
        assert result == expected

    @patch('src.utils.env_loader.EnvLoader')
    def test_hh_api_config_get_params_no_custom_params(self, mock_env):
        """Тест get_params когда custom_params пустой - покрывает строку 30 (if self.custom_params)"""
        mock_env.get_env_var.return_value = "false"
        
        config = HHAPIConfig()
        config.custom_params = {}  # Пустой словарь
        
        result = config.get_params()
        
        expected = {
            "area": 113,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15
        }
        assert result == expected

    @patch('src.utils.env_loader.EnvLoader')
    def test_hh_api_config_get_hh_params_compatibility(self, mock_env):
        """Тест метода get_hh_params для обратной совместимости - покрывает строку 37"""
        mock_env.get_env_var.return_value = "false"
        
        config = HHAPIConfig()
        
        # Должен вызывать get_params
        result1 = config.get_hh_params(area=2)
        result2 = config.get_params(area=2)
        
        assert result1 == result2


class TestSJAPIConfig:
    """100% покрытие SJAPIConfig"""

    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_init_defaults(self, mock_env):
        """Тест инициализации SJAPIConfig с дефолтными значениями - покрывает строки 28-39"""
        mock_env.get_env_var.return_value = "false"
        
        config = SJAPIConfig()
        
        # Проверяем дефолтные значения из dataclass
        assert config.count == 500
        assert config.published == 15
        assert config.only_with_salary is False
        assert config.custom_params is None
        assert config.per_page == 100
        assert config.max_total_pages == 20
        assert config.filter_by_target_companies is True
        assert config.token_file == Path("token.json")

    @patch.dict('os.environ', {'FILTER_ONLY_WITH_SALARY': 'true'}, clear=False)
    def test_sj_api_config_init_with_env_true(self):
        """Тест инициализации с FILTER_ONLY_WITH_SALARY=true - покрывает строки 34-35"""
        config = SJAPIConfig()
        assert config.only_with_salary is True

    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_init_with_kwargs(self, mock_env):
        """Тест инициализации с kwargs - покрывает строки 37-39"""
        mock_env.get_env_var.return_value = "false"
        
        config = SJAPIConfig(
            token_file=Path("custom_token.json"),
            count=200,
            custom_param="custom_value"
        )
        
        assert config.token_file == Path("custom_token.json")
        assert config.count == 200
        assert config.custom_param == "custom_value"

    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_get_params_defaults(self, mock_env):
        """Тест метода get_params без переопределений - покрывает строки 43-64"""
        mock_env.get_env_var.return_value = "false"
        
        config = SJAPIConfig()
        result = config.get_params()
        
        expected = {
            "count": 500,
            "order_field": "date",
            "order_direction": "desc",
            "published": 15,
            "no_agreement": 0  # False для only_with_salary
        }
        assert result == expected

    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_get_params_with_page(self, mock_env):
        """Тест get_params с параметром page - покрывает строки 54-55"""
        mock_env.get_env_var.return_value = "false"
        
        config = SJAPIConfig()
        result = config.get_params(page=5)
        
        assert result["page"] == 5

    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_get_params_with_town(self, mock_env):
        """Тест get_params с параметром town - покрывает строки 58-59"""
        mock_env.get_env_var.return_value = "false"
        
        config = SJAPIConfig()
        result = config.get_params(town="Москва")
        
        assert result["town"] == "Москва"

    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_get_params_with_custom_params(self, mock_env):
        """Тест get_params с custom_params - покрывает строки 61-63"""
        mock_env.get_env_var.return_value = "false"
        
        config = SJAPIConfig()
        config.custom_params = {"custom_field": "custom_value"}
        
        result = config.get_params(override_param="override_value")
        
        assert result["custom_field"] == "custom_value"
        assert result["override_param"] == "override_value"

    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_get_params_no_custom_params(self, mock_env):
        """Тест get_params когда custom_params None - покрывает строку 61 (if self.custom_params)"""
        mock_env.get_env_var.return_value = "false"
        
        config = SJAPIConfig()
        config.custom_params = None
        
        result = config.get_params()
        
        # Проверяем что custom_params не добавились
        assert "custom_field" not in result

    @patch('src.utils.file_handlers.json_handler.write_json')
    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_save_token_success(self, mock_env, mock_write_json):
        """Тест успешного сохранения токена - покрывает строки 69-71"""
        mock_env.get_env_var.return_value = "false"
        
        config = SJAPIConfig()
        config.save_token("test_token_123")
        
        # Проверяем что токен был сохранен
        mock_write_json.assert_called_once_with(
            config.token_file,
            [{"superjob_api_key": "test_token_123"}]
        )

    @patch('src.utils.file_handlers.json_handler.write_json')
    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_save_token_failure(self, mock_env, mock_write_json):
        """Тест ошибки при сохранении токена - покрывает строки 73-75"""
        mock_env.get_env_var.return_value = "false"
        mock_write_json.side_effect = Exception("Write failed")
        
        config = SJAPIConfig()
        
        with pytest.raises(Exception) as exc_info:
            config.save_token("test_token")
        
        assert "Write failed" in str(exc_info.value)

    @patch('src.utils.file_handlers.json_handler.read_json')
    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_load_token_success(self, mock_env, mock_read_json):
        """Тест успешной загрузки токена - покрывает строки 80-82"""
        mock_env.get_env_var.return_value = "false"
        mock_read_json.return_value = [{"superjob_api_key": "loaded_token"}]
        
        config = SJAPIConfig()
        token = config.load_token()
        
        assert token == "loaded_token"

    @patch('src.utils.file_handlers.json_handler.read_json')
    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_load_token_empty_data(self, mock_env, mock_read_json):
        """Тест загрузки токена из пустых данных - покрывает строку 83"""
        mock_env.get_env_var.return_value = "false"
        mock_read_json.return_value = []
        
        config = SJAPIConfig()
        token = config.load_token()
        
        assert token is None

    @patch('src.utils.file_handlers.json_handler.read_json')
    @patch('src.utils.env_loader.EnvLoader')
    def test_sj_api_config_load_token_failure(self, mock_env, mock_read_json):
        """Тест ошибки при загрузке токена - покрывает строки 85-87"""
        mock_env.get_env_var.return_value = "false"
        mock_read_json.side_effect = Exception("Read failed")
        
        config = SJAPIConfig()
        token = config.load_token()
        
        assert token is None

    def test_sj_api_config_salary_filter_logic(self):
        """Тест логики фильтрации по зарплате - проверяем строки 48-50"""
        # Тест когда only_with_salary = True
        with patch.dict('os.environ', {'FILTER_ONLY_WITH_SALARY': 'true'}, clear=False):
            config_true = SJAPIConfig()
            result_true = config_true.get_params()
            assert result_true["no_agreement"] == 1
        
        # Тест когда only_with_salary = False
        with patch.dict('os.environ', {'FILTER_ONLY_WITH_SALARY': 'false'}, clear=False):
            config_false = SJAPIConfig()
            result_false = config_false.get_params()
            assert result_false["no_agreement"] == 0
            
            # Тест переопределения в kwargs
            result_override = config_false.get_params(only_with_salary=True)
            assert result_override["no_agreement"] == 1

    @patch.dict('os.environ', {'FILTER_ONLY_WITH_SALARY': 'false'}, clear=False)
    def test_sj_api_config_comprehensive_params(self):
        """Comprehensive тест всех параметров get_params"""
        config = SJAPIConfig()
        config.custom_params = {"profession": 48, "catalogues": 33}
        
        result = config.get_params(
            count=250,
            order_field="payment",
            order_direction="asc",
            published=7,
            only_with_salary=True,
            page=3,
            town="СПб",
            keywords="python django"
        )
        
        expected = {
            "count": 250,
            "order_field": "payment",
            "order_direction": "asc", 
            "published": 7,
            "no_agreement": 1,
            "page": 3,
            "town": "СПб",
            "profession": 48,
            "catalogues": 33,
            "keywords": "python django",
            "only_with_salary": True  # kwargs добавляется в конце
        }
        
        assert result == expected


class TestAPIConfigIntegration:
    """Интеграционные тесты для всех API config модулей"""

    @patch.dict('os.environ', {'FILTER_ONLY_WITH_SALARY': 'true'}, clear=False)
    def test_api_configs_integration(self):
        """Тест интеграции всех API конфигураций"""
        # Создаем основной API config
        api_config = APIConfig(
            user_agent="IntegrationTest/1.0",
            timeout=20,
            request_delay=0.3,
            max_pages=15
        )
        
        # Проверяем что все конфигурации созданы
        assert isinstance(api_config.hh_config, HHAPIConfig)
        assert isinstance(api_config.sj_config, SJAPIConfig)
        
        # Проверяем параметры HH
        hh_params = api_config.hh_config.get_params()
        assert hh_params["only_with_salary"] is True
        
        # Проверяем параметры SJ  
        sj_params = api_config.sj_config.get_params()
        assert sj_params["no_agreement"] == 1
        
        # Проверяем пагинацию
        pagination = api_config.get_pagination_params()
        assert pagination["max_pages"] == 15