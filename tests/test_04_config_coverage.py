"""
Тесты конфигурационных модулей для 100% покрытия.

Покрывает все строки кода в src/config/ с использованием моков для I/O операций.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.config.api_config import APIConfig
from src.config.hh_api_config import HHAPIConfig
from src.config.sj_api_config import SJAPIConfig
from src.config.target_companies import TargetCompanies


class TestAPIConfig:
    """100% покрытие APIConfig."""

    def test_init_default(self):
        """Покрытие инициализации с параметрами по умолчанию."""
        config = APIConfig()
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20

    def test_init_custom(self):
        """Покрытие инициализации с кастомными параметрами."""
        hh_config = HHAPIConfig()
        config = APIConfig(
            user_agent="CustomApp/2.0",
            timeout=30,
            request_delay=1.0,
            hh_config=hh_config,
            max_pages=50
        )
        assert config.user_agent == "CustomApp/2.0"
        assert config.timeout == 30
        assert config.request_delay == 1.0
        assert config.hh_config == hh_config
        assert config.max_pages == 50

    def test_get_pagination_params_default(self):
        """Покрытие get_pagination_params без переопределения."""
        config = APIConfig()
        params = config.get_pagination_params()
        assert params == {"max_pages": 20}

    def test_get_pagination_params_override(self):
        """Покрытие get_pagination_params с переопределением."""
        config = APIConfig()
        params = config.get_pagination_params(max_pages=100)
        assert params == {"max_pages": 100}


class TestHHAPIConfig:
    """100% покрытие HHAPIConfig."""

    def test_init_default(self):
        """Покрытие инициализации HH конфигурации."""
        config = HHAPIConfig()
        assert config.base_url == "https://api.hh.ru/vacancies"
        assert config.per_page == 100

    def test_get_search_params_basic(self):
        """Покрытие get_search_params с базовыми параметрами."""
        config = HHAPIConfig()
        params = config.get_search_params("python")
        
        assert "text" in params
        assert params["text"] == "python"
        assert "per_page" in params
        assert params["per_page"] == 100

    def test_get_search_params_with_kwargs(self):
        """Покрытие get_search_params с дополнительными параметрами."""
        config = HHAPIConfig()
        params = config.get_search_params("python", salary=100000, experience="between1And3")
        
        assert params["text"] == "python"
        assert "salary" in params
        assert "experience" in params


class TestSJAPIConfig:
    """100% покрытие SJAPIConfig."""

    def test_init_default(self):
        """Покрытие инициализации SJ конфигурации."""
        config = SJAPIConfig()
        assert config.base_url == "https://api.superjob.ru/2.0/vacancies"
        assert config.count == 100

    def test_get_search_params_basic(self):
        """Покрытие get_search_params с базовыми параметрами."""
        config = SJAPIConfig()
        params = config.get_search_params("python")
        
        assert "keyword" in params
        assert params["keyword"] == "python"
        assert "count" in params
        assert params["count"] == 100

    def test_get_search_params_with_kwargs(self):
        """Покрытие get_search_params с дополнительными параметрами."""
        config = SJAPIConfig()
        params = config.get_search_params("python", payment_from=50000, no_agreement=1)
        
        assert params["keyword"] == "python"
        assert "payment_from" in params
        assert "no_agreement" in params

    def test_map_period_parameter(self):
        """Покрытие map_period_parameter."""
        config = SJAPIConfig()
        mapped = config.map_period_parameter(30)
        assert mapped == 30

    def test_validate_api_key_present(self):
        """Покрытие validate_api_key с ключом."""
        config = SJAPIConfig()
        assert config.validate_api_key("test_key") is True

    def test_validate_api_key_empty(self):
        """Покрытие validate_api_key с пустым ключом."""
        config = SJAPIConfig()
        assert config.validate_api_key("") is False
        assert config.validate_api_key(None) is False

    def test_get_headers_with_key(self):
        """Покрытие get_headers с API ключом."""
        config = SJAPIConfig()
        headers = config.get_headers("test_api_key")
        
        assert "X-Api-App-Id" in headers
        assert headers["X-Api-App-Id"] == "test_api_key"

    def test_get_headers_without_key(self):
        """Покрытие get_headers без API ключа."""
        config = SJAPIConfig()
        headers = config.get_headers()
        
        assert "X-Api-App-Id" in headers
        # Возвращает дефолтный ключ


class TestTargetCompanies:
    """100% покрытие TargetCompanies."""

    def test_get_companies_list(self):
        """Покрытие get_companies_list."""
        companies = TargetCompanies.get_companies_list()
        assert isinstance(companies, list)
        assert len(companies) > 0

    def test_get_companies_dict(self):
        """Покрытие get_companies_dict."""
        companies_dict = TargetCompanies.get_companies_dict()
        assert isinstance(companies_dict, dict)
        assert len(companies_dict) > 0

    def test_is_target_company_valid(self):
        """Покрытие is_target_company с валидной компанией."""
        # Используем первую компанию из списка
        companies = TargetCompanies.get_companies_list()
        if companies:
            first_company = companies[0]
            assert TargetCompanies.is_target_company(first_company) is True

    def test_is_target_company_invalid(self):
        """Покрытие is_target_company с невалидной компанией."""
        assert TargetCompanies.is_target_company("Несуществующая компания") is False

    def test_get_company_by_hh_id_found(self):
        """Покрытие get_company_by_hh_id с найденной компанией."""
        # Тестируем с моком поскольку не знаем реальные ID
        with patch.object(TargetCompanies, 'get_companies_dict') as mock_dict:
            mock_dict.return_value = {"1": "Test Company"}
            result = TargetCompanies.get_company_by_hh_id("1")
            assert result == "Test Company"

    def test_get_company_by_hh_id_not_found(self):
        """Покрытие get_company_by_hh_id с ненайденной компанией."""
        result = TargetCompanies.get_company_by_hh_id("99999")
        assert result is None

    def test_get_company_by_sj_id_found(self):
        """Покрытие get_company_by_sj_id с найденной компанией."""
        with patch.object(TargetCompanies, '_get_sj_mapping') as mock_mapping:
            mock_mapping.return_value = {"100": "SJ Test Company"}
            result = TargetCompanies.get_company_by_sj_id("100")
            assert result == "SJ Test Company"

    def test_get_company_by_sj_id_not_found(self):
        """Покрытие get_company_by_sj_id с ненайденной компанией."""
        result = TargetCompanies.get_company_by_sj_id("99999")
        assert result is None

    def test_get_total_count(self):
        """Покрытие get_total_count."""
        count = TargetCompanies.get_total_count()
        assert isinstance(count, int)
        assert count > 0

    def test_private_get_sj_mapping(self):
        """Покрытие приватного метода _get_sj_mapping."""
        mapping = TargetCompanies._get_sj_mapping()
        assert isinstance(mapping, dict)