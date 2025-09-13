#!/usr/bin/env python3
"""
Тесты модуля hh_api_config для 100% покрытия.

Покрывает все функции в src/config/hh_api_config.py:
- HHAPIConfig - dataclass конфигурации HH API
- __post_init__ - загрузка настроек из .env
- get_params - генерация параметров запроса с переопределениями
- get_hh_params - совместимость со старым интерфейсом

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

from unittest.mock import patch
from typing import Any

# Импорты из реального кода для покрытия
from src.config.hh_api_config import HHAPIConfig


class TestHHAPIConfig:
    """100% покрытие HHAPIConfig dataclass"""

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_init_default_values(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с значениями по умолчанию"""
        mock_get_env_var.return_value = "false"

        config = HHAPIConfig()

        # Проверяем значения по умолчанию
        assert config.area == 113
        assert config.per_page == 50
        assert config.only_with_salary is False
        assert config.period == 15
        assert config.custom_params == {}

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_init_with_custom_values(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с кастомными значениями"""
        mock_get_env_var.return_value = "true"

        config = HHAPIConfig(
            area=1,
            per_page=100,
            period=30,
            custom_params={"test": "value"}
        )

        assert config.area == 1
        assert config.per_page == 100
        assert config.only_with_salary is True  # Из env
        assert config.period == 30
        assert config.custom_params == {"test": "value"}

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_post_init_env_false(self, mock_get_env_var: Any) -> None:
        """Покрытие __post_init__ с FILTER_ONLY_WITH_SALARY=false"""
        mock_get_env_var.return_value = "false"

        config = HHAPIConfig()

        mock_get_env_var.assert_called_once_with("FILTER_ONLY_WITH_SALARY", "false")
        assert config.only_with_salary is False

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_post_init_env_true(self, mock_get_env_var: Any) -> None:
        """Покрытие __post_init__ с FILTER_ONLY_WITH_SALARY=true"""
        mock_get_env_var.return_value = "true"

        config = HHAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_post_init_env_one(self, mock_get_env_var: Any) -> None:
        """Покрытие __post_init__ с FILTER_ONLY_WITH_SALARY=1"""
        mock_get_env_var.return_value = "1"

        config = HHAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_post_init_env_yes(self, mock_get_env_var: Any) -> None:
        """Покрытие __post_init__ с FILTER_ONLY_WITH_SALARY=yes"""
        mock_get_env_var.return_value = "yes"

        config = HHAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_post_init_env_on(self, mock_get_env_var: Any) -> None:
        """Покрытие __post_init__ с FILTER_ONLY_WITH_SALARY=on"""
        mock_get_env_var.return_value = "on"

        config = HHAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_post_init_env_uppercase_true(self, mock_get_env_var: Any) -> None:
        """Покрытие __post_init__ с FILTER_ONLY_WITH_SALARY=TRUE (верхний регистр)"""
        mock_get_env_var.return_value = "TRUE"

        config = HHAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_post_init_env_random_string(self, mock_get_env_var: Any) -> None:
        """Покрытие __post_init__ с неизвестным значением"""
        mock_get_env_var.return_value = "random_value"

        config = HHAPIConfig()

        assert config.only_with_salary is False

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_post_init_env_none(self, mock_get_env_var: Any) -> None:
        """Покрытие __post_init__ с None значением"""
        mock_get_env_var.return_value = None

        config = HHAPIConfig()

        assert config.only_with_salary is False


class TestHHAPIConfigGetParams:
    """100% покрытие get_params метода"""

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_params_without_kwargs(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params без переопределений"""
        mock_get_env_var.return_value = "false"

        config = HHAPIConfig()
        params = config.get_params()

        expected = {
            "area": 113,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15
        }
        assert params == expected

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_params_with_kwargs_override(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с переопределением через kwargs"""
        mock_get_env_var.return_value = "false"

        config = HHAPIConfig()
        params = config.get_params(
            area=1,
            per_page=100,
            only_with_salary=True,
            period=30
        )

        expected = {
            "area": 1,
            "per_page": 100,
            "only_with_salary": True,
            "period": 30
        }
        assert params == expected

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_params_partial_override(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с частичным переопределением"""
        mock_get_env_var.return_value = "true"

        config = HHAPIConfig()
        params = config.get_params(area=2, period=7)

        expected = {
            "area": 2,
            "per_page": 50,  # default
            "only_with_salary": True,  # from env
            "period": 7
        }
        assert params == expected

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_params_with_custom_params(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с custom_params"""
        mock_get_env_var.return_value = "false"

        custom_params = {"salary_from": 50000, "experience": "between1And3"}
        config = HHAPIConfig(custom_params=custom_params)
        params = config.get_params()

        expected = {
            "area": 113,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15,
            "salary_from": 50000,
            "experience": "between1And3"
        }
        assert params == expected

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_params_custom_params_with_kwargs(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с custom_params и kwargs"""
        mock_get_env_var.return_value = "false"

        custom_params = {"salary_from": 50000, "area": 999}  # area будет переопределена
        config = HHAPIConfig(custom_params=custom_params)
        params = config.get_params(area=1, new_param="test")

        expected = {
            "area": 1,  # из kwargs
            "per_page": 50,
            "only_with_salary": False,
            "period": 15,
            "salary_from": 50000,  # из custom_params
            "new_param": "test"  # из kwargs
        }
        assert params == expected

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_params_empty_custom_params(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с пустыми custom_params"""
        mock_get_env_var.return_value = "false"

        config = HHAPIConfig(custom_params={})
        params = config.get_params()

        expected = {
            "area": 113,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15
        }
        assert params == expected

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_params_none_custom_params_default_factory(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с default_factory для custom_params"""
        mock_get_env_var.return_value = "false"

        # Не передаем custom_params, используется default_factory=dict
        config = HHAPIConfig()
        params = config.get_params()

        expected = {
            "area": 113,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15
        }
        assert params == expected

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_params_kwargs_priority_over_custom(self, mock_get_env_var: Any) -> None:
        """Покрытие приоритета kwargs над custom_params"""
        mock_get_env_var.return_value = "false"

        custom_params = {"area": 999, "salary_from": 100000}
        config = HHAPIConfig(custom_params=custom_params)
        params = config.get_params(area=1)  # kwargs переопределяет custom_params

        expected = {
            "area": 1,  # kwargs побеждает
            "per_page": 50,
            "only_with_salary": False,
            "period": 15,
            "salary_from": 100000  # из custom_params
        }
        assert params == expected

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_params_additional_kwargs(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с дополнительными kwargs параметрами"""
        mock_get_env_var.return_value = "false"

        config = HHAPIConfig()
        params = config.get_params(
            text="python developer",
            salary_from=80000,
            employment="full"
        )

        assert params["area"] == 113  # default
        assert params["text"] == "python developer"  # дополнительный
        assert params["salary_from"] == 80000  # дополнительный
        assert params["employment"] == "full"  # дополнительный


class TestHHAPIConfigGetHHParams:
    """100% покрытие get_hh_params метода (legacy compatibility)"""

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_hh_params_compatibility(self, mock_get_env_var: Any) -> None:
        """Покрытие get_hh_params как алиаса для get_params"""
        mock_get_env_var.return_value = "true"

        config = HHAPIConfig()

        # Вызываем оба метода с одинаковыми параметрами
        params1 = config.get_params(area=2, per_page=25)
        params2 = config.get_hh_params(area=2, per_page=25)

        # Результаты должны быть идентичными
        assert params1 == params2

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_hh_params_without_args(self, mock_get_env_var: Any) -> None:
        """Покрытие get_hh_params без аргументов"""
        mock_get_env_var.return_value = "false"

        config = HHAPIConfig()
        params = config.get_hh_params()

        expected = {
            "area": 113,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15
        }
        assert params == expected

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_get_hh_params_with_kwargs(self, mock_get_env_var: Any) -> None:
        """Покрытие get_hh_params с kwargs"""
        mock_get_env_var.return_value = "false"

        config = HHAPIConfig(custom_params={"test": "value"})
        params = config.get_hh_params(area=5, new_param="legacy_test")

        expected = {
            "area": 5,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15,
            "test": "value",  # из custom_params
            "new_param": "legacy_test"  # из kwargs
        }
        assert params == expected


class TestHHAPIConfigIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_full_workflow_scenario(self, mock_get_env_var: Any) -> None:
        """Покрытие полного рабочего сценария"""
        mock_get_env_var.return_value = "true"

        # Создаем конфигурацию с кастомными параметрами
        custom_params = {
            "salary_from": 100000,
            "salary_to": 200000,
            "experience": "between3And6"
        }

        config = HHAPIConfig(
            area=1,  # Москва
            per_page=100,
            period=7,
            custom_params=custom_params
        )

        # Тестируем получение параметров
        params = config.get_params()

        assert params["area"] == 1
        assert params["per_page"] == 100
        assert params["only_with_salary"] is True  # из env
        assert params["period"] == 7
        assert params["salary_from"] == 100000
        assert params["salary_to"] == 200000
        assert params["experience"] == "between3And6"

        # Тестируем переопределение
        override_params = config.get_params(
            area=2,  # СПб
            text="senior python developer"
        )

        assert override_params["area"] == 2  # переопределен
        assert override_params["text"] == "senior python developer"
        assert override_params["salary_from"] == 100000  # остается из custom_params

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_dataclass_field_defaults(self, mock_get_env_var: Any) -> None:
        """Покрытие правильной работы default_factory для dataclass полей"""
        mock_get_env_var.return_value = "false"

        # Создаем два экземпляра, чтобы убедиться что custom_params не разделяются
        config1 = HHAPIConfig()
        config2 = HHAPIConfig()

        # Изменяем custom_params у первого
        config1.custom_params["test"] = "value1"

        # У второго не должно быть этого значения
        assert "test" not in config2.custom_params
        assert config1.custom_params != config2.custom_params

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_complex_env_parsing(self, mock_get_env_var: Any) -> None:
        """Покрытие сложных случаев парсинга env переменных"""
        # Тестируем обработку различных строковых представлений
        test_cases = [
            ("True", True),
            ("False", False),
            ("1", True),
            ("0", False),
            ("YES", True),
            ("no", False),
            ("ON", True),
            ("off", False),
            ("random", False),
            ("", False)
        ]

        for env_value, expected in test_cases:
            mock_get_env_var.return_value = env_value
            config = HHAPIConfig()
            assert config.only_with_salary == expected, f"Failed for env_value: {env_value}"

    @patch('src.config.hh_api_config.EnvLoader.get_env_var')
    def test_method_consistency(self, mock_get_env_var: Any) -> None:
        """Покрытие согласованности методов get_params и get_hh_params"""
        mock_get_env_var.return_value = "true"

        config = HHAPIConfig(custom_params={"test": "consistency"})

        # Многократные вызовы должны возвращать одинаковые результаты
        params1 = config.get_params(area=1)
        params2 = config.get_params(area=1)
        hh_params1 = config.get_hh_params(area=1)
        hh_params2 = config.get_hh_params(area=1)

        assert params1 == params2
        assert hh_params1 == hh_params2
        assert params1 == hh_params1  # Методы должны возвращать идентичные результаты
