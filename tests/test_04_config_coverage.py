"""
Тесты конфигурационных модулей для 100% покрытия.

Покрывает все строки кода в src/config/ с использованием моков для I/O операций.
"""

from pathlib import Path
from unittest.mock import patch
from typing import Any

from src.config.api_config import APIConfig
from src.config.hh_api_config import HHAPIConfig
from src.config.sj_api_config import SJAPIConfig
from src.config.target_companies import TargetCompanies


class TestAPIConfig:
    """100% покрытие APIConfig."""

    def test_init_default(self) -> None:
        """Покрытие инициализации с параметрами по умолчанию."""
        config = APIConfig()
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20

    def test_init_custom(self) -> None:
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

    def test_get_pagination_params_default(self) -> None:
        """Покрытие get_pagination_params без переопределения."""
        config = APIConfig()
        params = config.get_pagination_params()
        assert params == {"max_pages": 20}

    def test_get_pagination_params_override(self) -> None:
        """Покрытие get_pagination_params с переопределением."""
        config = APIConfig()
        params = config.get_pagination_params(max_pages=100)
        assert params == {"max_pages": 100}


class TestHHAPIConfig:
    """100% покрытие HHAPIConfig."""

    def test_init_default(self) -> None:
        """Покрытие инициализации HH конфигурации."""
        config = HHAPIConfig()
        assert config.area == 113
        assert config.per_page == 50
        assert config.period == 15

    def test_get_params_basic(self) -> None:
        """Покрытие get_params с базовыми параметрами."""
        config = HHAPIConfig()
        params = config.get_params()

        assert "area" in params
        assert params["area"] == 113
        assert "per_page" in params
        assert params["per_page"] == 50

    def test_get_params_with_kwargs(self) -> None:
        """Покрытие get_params с дополнительными параметрами."""
        config = HHAPIConfig()
        params = config.get_params(text="python", salary=100000)

        assert params["text"] == "python"
        assert params["salary"] == 100000
        assert params["area"] == 113


class TestSJAPIConfig:
    """100% покрытие SJAPIConfig."""

    def test_init_default(self) -> None:
        """Покрытие инициализации SJ конфигурации."""
        config = SJAPIConfig()
        assert hasattr(config, 'count')
        assert hasattr(config, 'only_with_salary')
        assert hasattr(config, 'published')

    def test_get_params_basic(self) -> None:
        """Покрытие get_params с базовыми параметрами."""
        config = SJAPIConfig()
        params = config.get_params()

        assert "count" in params
        assert "order_field" in params
        assert "order_direction" in params
        assert "published" in params

    def test_get_params_with_kwargs(self) -> None:
        """Покрытие get_params с дополнительными параметрами."""
        config = SJAPIConfig()
        params = config.get_params(keyword="python", payment_from=50000, page=1)

        assert params["keyword"] == "python"
        assert params["payment_from"] == 50000
        assert params["page"] == 1

    @patch('src.utils.file_handlers.json_handler.write_json')
    @patch('src.utils.file_handlers.json_handler.read_json')
    def test_save_load_token(self, mock_read_json: Any, mock_write_json: Any) -> None:
        """Покрытие save_token и load_token."""
        config = SJAPIConfig(token_file=Path("test_token.json"))

        # Тест save_token
        config.save_token("test_token")
        mock_write_json.assert_called_once()

        # Тест load_token
        mock_read_json.return_value = [{"superjob_api_key": "test_token"}]
        loaded_token = config.load_token()
        assert loaded_token == "test_token"


class TestTargetCompanies:
    """100% покрытие TargetCompanies."""

    def test_get_all_companies(self) -> None:
        """Покрытие get_all_companies."""
        companies = TargetCompanies.get_all_companies()
        assert isinstance(companies, list)
        assert len(companies) > 0

    def test_get_hh_ids(self) -> None:
        """Покрытие get_hh_ids."""
        hh_ids = TargetCompanies.get_hh_ids()
        assert isinstance(hh_ids, list)
        assert len(hh_ids) > 0

    def test_is_target_company_valid(self) -> None:
        """Покрытие is_target_company с валидной компанией."""
        # Используем первый ID из списка
        hh_ids = TargetCompanies.get_hh_ids()
        if hh_ids:
            first_id = hh_ids[0]
            assert TargetCompanies.is_target_company(first_id) is True

    def test_is_target_company_invalid(self) -> None:
        """Покрытие is_target_company с невалидной компанией."""
        assert TargetCompanies.is_target_company("99999") is False

    def test_get_company_by_hh_id_found(self) -> None:
        """Покрытие get_company_by_hh_id с найденной компанией."""
        # Используем первый реальный ID
        hh_ids = TargetCompanies.get_hh_ids()
        if hh_ids:
            result = TargetCompanies.get_company_by_hh_id(hh_ids[0])
            assert result is not None

    def test_get_company_by_hh_id_not_found(self) -> None:
        """Покрытие get_company_by_hh_id с ненайденной компанией."""
        result = TargetCompanies.get_company_by_hh_id("99999")
        assert result is None

    def test_get_company_by_sj_id_found(self) -> None:
        """Покрытие get_company_by_sj_id с найденной компанией."""
        # Используем первый реальный SJ ID
        sj_ids = TargetCompanies.get_sj_ids()
        if sj_ids:
            result = TargetCompanies.get_company_by_sj_id(sj_ids[0])
            assert result is not None

    def test_get_company_by_sj_id_not_found(self) -> None:
        """Покрытие get_company_by_sj_id с ненайденной компанией."""
        result = TargetCompanies.get_company_by_sj_id("99999")
        assert result is None

    def test_get_company_count(self) -> None:
        """Покрытие get_company_count."""
        count = TargetCompanies.get_company_count()
        assert isinstance(count, int)
        assert count > 0
