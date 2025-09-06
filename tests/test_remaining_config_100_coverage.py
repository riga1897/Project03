"""
100% покрытие оставшихся config модулей: sj_api_config, target_companies
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pytest
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.config.sj_api_config import SJAPIConfig
from src.config.target_companies import TargetCompanies, CompanyInfo


class TestSJAPIConfig:
    """100% покрытие SJAPIConfig"""

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_init_default(self, mock_get_env):
        """Тест инициализации с дефолтными параметрами"""
        mock_get_env.return_value = "false"
        
        config = SJAPIConfig()
        
        assert config.count == 500
        assert config.published == 15
        assert config.only_with_salary is False
        assert config.per_page == 100
        assert config.max_total_pages == 20
        assert config.filter_by_target_companies is True
        mock_get_env.assert_called_once_with("FILTER_ONLY_WITH_SALARY", "false")

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_init_with_custom_token_file(self, mock_get_env):
        """Тест инициализации с кастомным файлом токена"""
        mock_get_env.return_value = "false"
        custom_path = Path("custom_token.json")
        
        config = SJAPIConfig(token_file=custom_path)
        
        assert config.token_file == custom_path

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_init_with_kwargs(self, mock_get_env):
        """Тест инициализации с дополнительными параметрами"""
        mock_get_env.return_value = "false"
        
        config = SJAPIConfig(count=100, published=7, custom_attr="test")
        
        assert config.count == 100
        assert config.published == 7
        assert hasattr(config, 'custom_attr')
        assert config.custom_attr == "test"

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_init_env_only_with_salary_true_variations(self, mock_get_env):
        """Тест различных вариантов true для only_with_salary"""
        test_cases = ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"]
        
        for env_value in test_cases:
            mock_get_env.return_value = env_value
            config = SJAPIConfig()
            assert config.only_with_salary is True, f"Failed for env_value: {env_value}"
            mock_get_env.reset_mock()

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_init_env_only_with_salary_false_variations(self, mock_get_env):
        """Тест различных вариантов false для only_with_salary"""
        test_cases = ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF", "random_value"]
        
        for env_value in test_cases:
            mock_get_env.return_value = env_value
            config = SJAPIConfig()
            assert config.only_with_salary is False, f"Failed for env_value: {env_value}"
            mock_get_env.reset_mock()

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_get_params_default(self, mock_get_env):
        """Тест получения дефолтных параметров"""
        mock_get_env.return_value = "false"
        config = SJAPIConfig()
        
        params = config.get_params()
        
        expected = {
            "count": 500,
            "order_field": "date",
            "order_direction": "desc",
            "published": 15,
            "no_agreement": 0
        }
        
        for key, value in expected.items():
            assert params[key] == value

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_get_params_with_kwargs_override(self, mock_get_env):
        """Тест переопределения параметров через kwargs"""
        mock_get_env.return_value = "false"
        config = SJAPIConfig()
        
        params = config.get_params(
            count=200,
            order_field="salary",
            order_direction="asc",
            published=30,
            only_with_salary=True
        )
        
        assert params["count"] == 200
        assert params["order_field"] == "salary"
        assert params["order_direction"] == "asc"
        assert params["published"] == 30
        assert params["no_agreement"] == 1

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_get_params_with_page(self, mock_get_env):
        """Тест добавления параметра page"""
        mock_get_env.return_value = "false"
        config = SJAPIConfig()
        
        params = config.get_params(page=5)
        
        assert params["page"] == 5

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_get_params_with_town(self, mock_get_env):
        """Тест добавления параметра town"""
        mock_get_env.return_value = "false"
        config = SJAPIConfig()
        
        params = config.get_params(town="Москва")
        
        assert params["town"] == "Москва"

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_get_params_with_custom_params(self, mock_get_env):
        """Тест с кастомными параметрами"""
        mock_get_env.return_value = "false"
        config = SJAPIConfig()
        config.custom_params = {"profession": "1", "catalogues": "48"}
        
        params = config.get_params()
        
        assert params["profession"] == "1"
        assert params["catalogues"] == "48"

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_get_params_kwargs_update(self, mock_get_env):
        """Тест обновления параметров из kwargs"""
        mock_get_env.return_value = "false"
        config = SJAPIConfig()
        
        params = config.get_params(extra_param="extra_value", another_param=42)
        
        assert params["extra_param"] == "extra_value"
        assert params["another_param"] == 42

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    @patch('src.utils.file_handlers.json_handler.write_json')
    def test_save_token_success(self, mock_write_json, mock_get_env):
        """Тест успешного сохранения токена"""
        mock_get_env.return_value = "false"
        config = SJAPIConfig()
        
        with patch('src.config.sj_api_config.logger') as mock_logger:
            config.save_token("test_token_123")
        
        expected_data = [{"superjob_api_key": "test_token_123"}]
        mock_write_json.assert_called_once_with(config.token_file, expected_data)
        mock_logger.info.assert_called_once()

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    @patch('src.utils.file_handlers.json_handler.write_json')
    def test_save_token_failure(self, mock_write_json, mock_get_env):
        """Тест обработки ошибки сохранения токена"""
        mock_get_env.return_value = "false"
        mock_write_json.side_effect = IOError("Write failed")
        
        config = SJAPIConfig()
        
        with patch('src.config.sj_api_config.logger') as mock_logger:
            with pytest.raises(IOError):
                config.save_token("test_token")
        
        mock_logger.error.assert_called_once()

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    @patch('src.utils.file_handlers.json_handler.read_json')
    def test_load_token_success(self, mock_read_json, mock_get_env):
        """Тест успешной загрузки токена"""
        mock_get_env.return_value = "false"
        mock_read_json.return_value = [{"superjob_api_key": "loaded_token_456"}]
        
        config = SJAPIConfig()
        token = config.load_token()
        
        assert token == "loaded_token_456"
        mock_read_json.assert_called_once_with(config.token_file)

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    @patch('src.utils.file_handlers.json_handler.read_json')
    def test_load_token_empty_data(self, mock_read_json, mock_get_env):
        """Тест загрузки токена из пустого файла"""
        mock_get_env.return_value = "false"
        mock_read_json.return_value = []
        
        config = SJAPIConfig()
        token = config.load_token()
        
        assert token is None

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    @patch('src.utils.file_handlers.json_handler.read_json')
    def test_load_token_none_data(self, mock_read_json, mock_get_env):
        """Тест загрузки токена когда данные None"""
        mock_get_env.return_value = "false"
        mock_read_json.return_value = None
        
        config = SJAPIConfig()
        token = config.load_token()
        
        assert token is None

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    @patch('src.utils.file_handlers.json_handler.read_json')
    def test_load_token_missing_key(self, mock_read_json, mock_get_env):
        """Тест загрузки токена когда ключ отсутствует"""
        mock_get_env.return_value = "false"
        mock_read_json.return_value = [{"other_key": "value"}]
        
        config = SJAPIConfig()
        token = config.load_token()
        
        assert token is None

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    @patch('src.utils.file_handlers.json_handler.read_json')
    def test_load_token_exception(self, mock_read_json, mock_get_env):
        """Тест обработки исключения при загрузке токена"""
        mock_get_env.return_value = "false"
        mock_read_json.side_effect = Exception("Read failed")
        
        config = SJAPIConfig()
        
        with patch('src.config.sj_api_config.logger') as mock_logger:
            token = config.load_token()
        
        assert token is None
        mock_logger.error.assert_called_once()


class TestCompanyInfo:
    """100% покрытие CompanyInfo"""

    def test_init_required_fields(self):
        """Тест инициализации с обязательными полями"""
        company = CompanyInfo(name="Test Company", hh_id="123")
        
        assert company.name == "Test Company"
        assert company.hh_id == "123"
        assert company.sj_id is None
        assert company.description == ""

    def test_init_all_fields(self):
        """Тест инициализации со всеми полями"""
        company = CompanyInfo(
            name="Full Company",
            hh_id="456",
            sj_id="789",
            description="Company description"
        )
        
        assert company.name == "Full Company"
        assert company.hh_id == "456"
        assert company.sj_id == "789"
        assert company.description == "Company description"

    def test_dataclass_equality(self):
        """Тест сравнения CompanyInfo объектов"""
        company1 = CompanyInfo(name="Company", hh_id="123")
        company2 = CompanyInfo(name="Company", hh_id="123")
        company3 = CompanyInfo(name="Other", hh_id="123")
        
        assert company1 == company2
        assert company1 != company3

    def test_dataclass_representation(self):
        """Тест строкового представления CompanyInfo"""
        company = CompanyInfo(name="Test", hh_id="123")
        repr_str = repr(company)
        
        assert "CompanyInfo" in repr_str
        assert "Test" in repr_str
        assert "123" in repr_str


class TestTargetCompanies:
    """100% покрытие TargetCompanies"""

    def test_companies_list_not_empty(self):
        """Тест что список компаний не пустой"""
        assert len(TargetCompanies.COMPANIES) > 0
        assert len(TargetCompanies.COMPANIES) == 12  # Должно быть 12 компаний

    def test_companies_have_required_fields(self):
        """Тест что все компании имеют обязательные поля"""
        for company in TargetCompanies.COMPANIES:
            assert isinstance(company, CompanyInfo)
            assert company.name is not None and company.name != ""
            assert company.hh_id is not None and company.hh_id != ""

    def test_specific_companies_present(self):
        """Тест наличия конкретных известных компаний"""
        company_names = {c.name for c in TargetCompanies.COMPANIES}
        
        expected_companies = {"Яндекс", "Тинькофф", "СБЕР", "VK", "OZON"}
        
        for expected in expected_companies:
            assert expected in company_names, f"Company {expected} not found"

    def test_get_all_companies_returns_copy(self):
        """Тест что get_all_companies возвращает копию"""
        companies1 = TargetCompanies.get_all_companies()
        companies2 = TargetCompanies.get_all_companies()
        
        # Должны иметь одинаковый контент но быть разными объектами
        assert companies1 == companies2
        assert companies1 is not companies2
        
        # Изменение копии не должно влиять на оригинал
        companies1.pop()
        assert len(companies1) != len(companies2)
        assert len(TargetCompanies.COMPANIES) == len(companies2)

    def test_get_all_companies_content(self):
        """Тест содержимого get_all_companies"""
        companies = TargetCompanies.get_all_companies()
        
        assert isinstance(companies, list)
        assert len(companies) == 12
        
        for company in companies:
            assert isinstance(company, CompanyInfo)

    def test_companies_have_valid_ids(self):
        """Тест что компании имеют валидные ID"""
        for company in TargetCompanies.COMPANIES:
            # hh_id должен быть строкой с числом
            assert company.hh_id.isdigit(), f"Invalid hh_id for {company.name}: {company.hh_id}"
            
            # sj_id может быть None или строкой с числом
            if company.sj_id is not None:
                assert company.sj_id.isdigit(), f"Invalid sj_id for {company.name}: {company.sj_id}"

    def test_companies_have_descriptions(self):
        """Тест что компании имеют описания"""
        for company in TargetCompanies.COMPANIES:
            # description может быть пустой строкой, но не должен быть None
            assert isinstance(company.description, str)
            # Большинство компаний должны иметь непустые описания
            if company.name in ["Яндекс", "Тинькофф", "СБЕР"]:
                assert len(company.description) > 10

    def test_get_hh_ids(self):
        """Тест получения списка HH ID"""
        companies = TargetCompanies.get_all_companies()
        hh_ids = [c.hh_id for c in companies]
        
        # Все ID должны быть уникальными
        assert len(hh_ids) == len(set(hh_ids))
        
        # Должны содержать известные ID
        assert "1740" in hh_ids  # Яндекс
        assert "78638" in hh_ids  # Тинькофф

    def test_get_sj_ids(self):
        """Тест получения списка SuperJob ID"""
        companies = TargetCompanies.get_all_companies()
        sj_ids = [c.sj_id for c in companies if c.sj_id is not None]
        
        # Все непустые ID должны быть уникальными
        assert len(sj_ids) == len(set(sj_ids))
        
        # Должны содержать известные ID
        assert "19421" in sj_ids  # Яндекс
        assert "2324" in sj_ids   # Тинькофф

    def test_company_info_list_copy(self):
        """Тест что get_all_companies возвращает список-копию"""
        original_count = len(TargetCompanies.COMPANIES)
        companies = TargetCompanies.get_all_companies()
        
        # Изменяем полученный список (добавляем элемент)
        companies.append(CompanyInfo(name="New Company", hh_id="999"))
        
        # Оригинальный список не должен измениться в размере
        assert len(TargetCompanies.COMPANIES) == original_count
        assert len(companies) == original_count + 1

    def test_first_company_details(self):
        """Тест деталей первой компании в списке"""
        companies = TargetCompanies.get_all_companies()
        assert len(companies) > 0
        
        first_company = companies[0]
        assert first_company.name is not None
        assert first_company.hh_id is not None
        assert first_company.hh_id.isdigit()
        
        # Проверяем что у первой компании есть описание
        assert isinstance(first_company.description, str)


class TestConfigIntegration:
    """Интеграционные тесты config модулей"""

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_sj_config_with_target_companies(self, mock_get_env):
        """Тест интеграции SJAPIConfig с TargetCompanies"""
        mock_get_env.return_value = "true"
        
        # Создаем конфигурацию
        config = SJAPIConfig()
        assert config.filter_by_target_companies is True
        
        # Получаем целевые компании
        companies = TargetCompanies.get_all_companies()
        
        # Создаем параметры запроса для первой компании с SJ ID
        company_with_sj = next((c for c in companies if c.sj_id is not None), None)
        
        if company_with_sj:
            params = config.get_params(firm_id=company_with_sj.sj_id)
            assert params["firm_id"] == company_with_sj.sj_id
            assert params["no_agreement"] == 1  # only_with_salary=True
        else:
            # Если нет компаний с SJ ID, просто проверим базовые параметры
            params = config.get_params()
            assert params["no_agreement"] == 1

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    @patch('src.utils.file_handlers.json_handler.write_json')
    @patch('src.utils.file_handlers.json_handler.read_json')
    def test_token_save_load_cycle(self, mock_read_json, mock_write_json, mock_get_env):
        """Тест полного цикла сохранения и загрузки токена"""
        mock_get_env.return_value = "false"
        
        # Симулируем сохранение токена
        config = SJAPIConfig()
        test_token = "test_superjob_token_12345"
        
        config.save_token(test_token)
        
        # Проверяем что токен был записан
        expected_data = [{"superjob_api_key": test_token}]
        mock_write_json.assert_called_once_with(config.token_file, expected_data)
        
        # Симулируем загрузку токена
        mock_read_json.return_value = expected_data
        loaded_token = config.load_token()
        
        assert loaded_token == test_token
        mock_read_json.assert_called_once_with(config.token_file)

    def test_company_info_in_api_params(self):
        """Тест использования CompanyInfo в параметрах API"""
        companies = TargetCompanies.get_all_companies()
        
        # Проверяем что можем использовать данные компаний для API
        for company in companies[:3]:  # Проверяем первые 3 компании
            assert company.hh_id is not None
            assert company.hh_id.isdigit()
            
            # Если есть SJ ID, тоже должен быть числовым
            if company.sj_id:
                assert company.sj_id.isdigit()

    @patch('src.utils.env_loader.EnvLoader.get_env_var')
    def test_config_environment_integration(self, mock_get_env):
        """Тест интеграции с переменными окружения"""
        # Тест что конфигурация корректно читает переменные окружения
        test_cases = [
            ("true", True),
            ("false", False),
            ("1", True),
            ("0", False)
        ]
        
        for env_value, expected in test_cases:
            mock_get_env.return_value = env_value
            config = SJAPIConfig()
            
            assert config.only_with_salary == expected
            
            # Проверяем что это отражается в параметрах
            params = config.get_params()
            expected_no_agreement = 1 if expected else 0
            assert params["no_agreement"] == expected_no_agreement
            
            mock_get_env.reset_mock()