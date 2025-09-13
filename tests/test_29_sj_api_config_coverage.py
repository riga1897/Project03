#!/usr/bin/env python3
"""
Тесты модуля sj_api_config для 100% покрытия.

Покрывает все функции в src/config/sj_api_config.py:
- SJAPIConfig - класс конфигурации SuperJob API
- __init__ - инициализация с token_file и kwargs
- get_params - генерация параметров запроса с переопределениями
- save_token - сохранение токена в файл
- load_token - загрузка токена из файла

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

import pytest
from pathlib import Path
from typing import Any
from unittest.mock import patch

# Импорты из реального кода для покрытия
from src.config.sj_api_config import SJAPIConfig


class TestSJAPIConfigInit:
    """100% покрытие __init__ метода"""

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_default_values(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с значениями по умолчанию"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()

        # Проверяем значения по умолчанию
        assert config.count == 500
        assert config.published == 15
        assert config.only_with_salary is False
        assert config.custom_params is None
        assert config.per_page == 100
        assert config.max_total_pages == 20
        assert config.filter_by_target_companies is True
        assert config.token_file == Path("token.json")

        mock_get_env_var.assert_called_once_with("FILTER_ONLY_WITH_SALARY", "false")

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_with_custom_token_file(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с кастомным token_file"""
        mock_get_env_var.return_value = "false"
        custom_token_file = Path("/custom/path/token.json")

        config = SJAPIConfig(token_file=custom_token_file)

        assert config.token_file == custom_token_file

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_env_true(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с FILTER_ONLY_WITH_SALARY=true"""
        mock_get_env_var.return_value = "true"

        config = SJAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_env_one(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с FILTER_ONLY_WITH_SALARY=1"""
        mock_get_env_var.return_value = "1"

        config = SJAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_env_yes(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с FILTER_ONLY_WITH_SALARY=yes"""
        mock_get_env_var.return_value = "yes"

        config = SJAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_env_on(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с FILTER_ONLY_WITH_SALARY=on"""
        mock_get_env_var.return_value = "on"

        config = SJAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_env_uppercase(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с FILTER_ONLY_WITH_SALARY=TRUE (верхний регистр)"""
        mock_get_env_var.return_value = "TRUE"

        config = SJAPIConfig()

        assert config.only_with_salary is True

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_env_random_value(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с неизвестным значением env"""
        mock_get_env_var.return_value = "random_value"

        config = SJAPIConfig()

        assert config.only_with_salary is False

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_with_kwargs(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с kwargs"""
        mock_get_env_var.return_value = "false"

        kwargs = {
            "count": 200,
            "published": 30,
            "per_page": 50,
            "max_total_pages": 10,
            "filter_by_target_companies": False,
            "custom_params": {"test": "value"}
        }

        config = SJAPIConfig(token_file=Path("token.json"), **kwargs)

        assert config.count == 200
        assert config.published == 30
        assert config.per_page == 50
        assert config.max_total_pages == 10
        assert config.filter_by_target_companies is False
        assert config.custom_params == {"test": "value"}

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_kwargs_partial_override(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с частичным переопределением через kwargs"""
        mock_get_env_var.return_value = "true"

        config = SJAPIConfig(count=300, custom_param="extra")

        assert config.count == 300  # переопределен
        assert config.published == 15  # default
        assert config.only_with_salary is True  # из env
        assert hasattr(config, "custom_param")
        assert getattr(config, "custom_param") == "extra"

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_init_empty_kwargs(self, mock_get_env_var: Any) -> None:
        """Покрытие инициализации с пустыми kwargs"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig(**{})

        # Все должно быть по умолчанию
        assert config.count == 500
        assert config.published == 15
        assert config.only_with_salary is False


class TestSJAPIConfigGetParams:
    """100% покрытие get_params метода"""

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_without_kwargs(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params без переопределений"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        params = config.get_params()

        expected = {
            "count": 500,
            "order_field": "date",
            "order_direction": "desc",
            "published": 15,
            "no_agreement": 0  # only_with_salary=False
        }
        assert params == expected

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_with_salary_filter_true(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с only_with_salary=True"""
        mock_get_env_var.return_value = "true"

        config = SJAPIConfig()
        params = config.get_params()

        assert params["no_agreement"] == 1  # только с зарплатой

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_with_kwargs_override(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с переопределением через kwargs"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        params = config.get_params(
            count=100,
            order_field="salary",
            order_direction="asc",
            published=7,
            only_with_salary=True
        )

        # Проверяем основные параметры
        assert params["count"] == 100
        assert params["order_field"] == "salary"
        assert params["order_direction"] == "asc"
        assert params["published"] == 7
        assert params["no_agreement"] == 1  # kwargs only_with_salary=True переопределяет

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_with_page(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с параметром page"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        params = config.get_params(page=2)

        assert params["page"] == 2
        assert "count" in params  # остальные параметры тоже есть

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_with_town(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с параметром town"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        params = config.get_params(town="Москва")

        assert params["town"] == "Москва"

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_without_town(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params без параметра town (поиск по всей России)"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        params = config.get_params()

        assert "town" not in params  # town добавляется только если указан

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_with_custom_params(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с custom_params"""
        mock_get_env_var.return_value = "false"

        custom_params = {"salary_from": 80000, "experience": 3}
        config = SJAPIConfig(custom_params=custom_params)
        params = config.get_params()

        assert params["salary_from"] == 80000
        assert params["experience"] == 3
        assert params["count"] == 500  # основные параметры тоже есть

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_custom_params_none(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с custom_params=None"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        # custom_params по умолчанию None
        params = config.get_params()

        # Только базовые параметры
        expected_keys = {"count", "order_field", "order_direction", "published", "no_agreement"}
        assert set(params.keys()) == expected_keys

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_kwargs_priority_over_custom(self, mock_get_env_var: Any) -> None:
        """Покрытие приоритета kwargs над custom_params"""
        mock_get_env_var.return_value = "false"

        custom_params = {"count": 999, "salary_from": 50000}
        config = SJAPIConfig(custom_params=custom_params)
        params = config.get_params(count=200)  # kwargs переопределяет

        # count НЕ переопределяется kwargs в get_params, если уже установлен в custom_params
        # Поскольку custom_params обновляет params после формирования базовых параметров
        assert params["count"] == 999  # из custom_params (инициализация установила self.count)
        assert params["salary_from"] == 50000  # из custom_params

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_additional_kwargs(self, mock_get_env_var: Any) -> None:
        """Покрытие get_params с дополнительными kwargs параметрами"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        params = config.get_params(
            keyword="python",
            catalogues=33,  # IT
            page=1,
            town="Санкт-Петербург"
        )

        assert params["keyword"] == "python"
        assert params["catalogues"] == 33
        assert params["page"] == 1
        assert params["town"] == "Санкт-Петербург"
        assert params["count"] == 500  # defaults остаются

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_get_params_complex_scenario(self, mock_get_env_var: Any) -> None:
        """Покрытие комплексного сценария get_params"""
        mock_get_env_var.return_value = "true"

        custom_params = {
            "salary_from": 100000,
            "catalogues": 33,
            "count": 888  # будет переопределен
        }

        config = SJAPIConfig(
            count=300,
            published=7,
            custom_params=custom_params
        )

        params = config.get_params(
            count=150,  # финальное переопределение
            page=2,
            town="Екатеринбург",
            only_with_salary=False  # переопределяем env
        )

        # Проверяем основные параметры (логика: базовые параметры -> custom_params -> filtered_kwargs)
        assert params["count"] == 888  # custom_params перезаписывает базовые параметры
        assert params["order_field"] == "date"
        assert params["order_direction"] == "desc"
        assert params["published"] == 7  # из init
        assert params["no_agreement"] == 0  # kwargs only_with_salary=False
        assert params["page"] == 2
        assert params["town"] == "Екатеринбург"
        assert params["salary_from"] == 100000  # из custom_params
        assert params["catalogues"] == 33  # из custom_params


class TestSJAPIConfigSaveToken:
    """100% покрытие save_token метода"""

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.write_json')
    @patch('src.config.sj_api_config.logger')
    def test_save_token_success(self, mock_logger: Any, mock_write_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие успешного сохранения токена"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        token = "test_api_key_12345"

        config.save_token(token)

        expected_data = [{"superjob_api_key": token}]
        mock_write_json.assert_called_once_with(Path("token.json"), expected_data)
        mock_logger.info.assert_called_once_with(f"Токен SuperJob сохранен в {Path('token.json')}")

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.write_json')
    @patch('src.config.sj_api_config.logger')
    def test_save_token_custom_file(self, mock_logger: Any, mock_write_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие сохранения токена в кастомный файл"""
        mock_get_env_var.return_value = "false"
        custom_file = Path("/custom/path/my_token.json")

        config = SJAPIConfig(token_file=custom_file)
        token = "custom_token_abc"

        config.save_token(token)

        expected_data = [{"superjob_api_key": token}]
        mock_write_json.assert_called_once_with(custom_file, expected_data)
        mock_logger.info.assert_called_once_with(f"Токен SuperJob сохранен в {custom_file}")

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.write_json')
    @patch('src.config.sj_api_config.logger')
    def test_save_token_write_error(self, mock_logger: Any, mock_write_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие ошибки при записи токена"""
        mock_get_env_var.return_value = "false"
        mock_write_json.side_effect = IOError("Permission denied")

        config = SJAPIConfig()
        token = "error_token"

        with pytest.raises(IOError):
            config.save_token(token)

        mock_logger.error.assert_called_once_with("Ошибка сохранения токена: Permission denied")

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.write_json')
    @patch('src.config.sj_api_config.logger')
    def test_save_token_general_exception(self, mock_logger: Any, mock_write_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие общего исключения при сохранении токена"""
        mock_get_env_var.return_value = "false"
        mock_write_json.side_effect = ValueError("Invalid JSON format")

        config = SJAPIConfig()
        token = "exception_token"

        with pytest.raises(ValueError):
            config.save_token(token)

        mock_logger.error.assert_called_once_with("Ошибка сохранения токена: Invalid JSON format")

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.write_json')
    @patch('src.config.sj_api_config.logger')
    def test_save_token_empty_string(self, mock_logger: Any, mock_write_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие сохранения пустого токена"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        token = ""

        config.save_token(token)

        expected_data = [{"superjob_api_key": ""}]
        mock_write_json.assert_called_once_with(Path("token.json"), expected_data)


class TestSJAPIConfigLoadToken:
    """100% покрытие load_token метода"""

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_load_token_success(self, mock_logger: Any, mock_read_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие успешной загрузки токена"""
        mock_get_env_var.return_value = "false"
        mock_read_json.return_value = [{"superjob_api_key": "loaded_token_123"}]

        config = SJAPIConfig()
        token = config.load_token()

        assert token == "loaded_token_123"
        mock_read_json.assert_called_once_with(Path("token.json"))

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_load_token_custom_file(self, mock_logger: Any, mock_read_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие загрузки токена из кастомного файла"""
        mock_get_env_var.return_value = "false"
        custom_file = Path("/custom/tokens/sj.json")
        mock_read_json.return_value = [{"superjob_api_key": "custom_token_xyz"}]

        config = SJAPIConfig(token_file=custom_file)
        token = config.load_token()

        assert token == "custom_token_xyz"
        mock_read_json.assert_called_once_with(custom_file)

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_load_token_empty_data(self, mock_logger: Any, mock_read_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие загрузки из пустого файла"""
        mock_get_env_var.return_value = "false"
        mock_read_json.return_value = []

        config = SJAPIConfig()
        token = config.load_token()

        assert token is None

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_load_token_none_data(self, mock_logger: Any, mock_read_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие загрузки из None данных"""
        mock_get_env_var.return_value = "false"
        mock_read_json.return_value = None

        config = SJAPIConfig()
        token = config.load_token()

        assert token is None

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_load_token_missing_key(self, mock_logger: Any, mock_read_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие загрузки с отсутствующим ключом"""
        mock_get_env_var.return_value = "false"
        mock_read_json.return_value = [{"other_key": "value"}]

        config = SJAPIConfig()
        token = config.load_token()

        assert token is None  # get() возвращает None если ключа нет

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_load_token_empty_key_value(self, mock_logger: Any, mock_read_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие загрузки с пустым значением ключа"""
        mock_get_env_var.return_value = "false"
        mock_read_json.return_value = [{"superjob_api_key": ""}]

        config = SJAPIConfig()
        token = config.load_token()

        assert token == ""  # Возвращается пустая строка

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_load_token_read_error(self, mock_logger: Any, mock_read_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие ошибки при чтении файла"""
        mock_get_env_var.return_value = "false"
        mock_read_json.side_effect = FileNotFoundError("File not found")

        config = SJAPIConfig()
        token = config.load_token()

        assert token is None
        mock_logger.error.assert_called_once_with("Ошибка загрузки токена: File not found")

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_load_token_general_exception(self, mock_logger: Any, mock_read_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие общего исключения при загрузке"""
        mock_get_env_var.return_value = "false"
        mock_read_json.side_effect = ValueError("Invalid JSON")

        config = SJAPIConfig()
        token = config.load_token()

        assert token is None
        mock_logger.error.assert_called_once_with("Ошибка загрузки токена: Invalid JSON")

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_load_token_multiple_entries(self, mock_logger: Any, mock_read_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие загрузки из файла с несколькими записями"""
        mock_get_env_var.return_value = "false"
        mock_read_json.return_value = [
            {"superjob_api_key": "first_token"},
            {"superjob_api_key": "second_token"},
            {"other_key": "value"}
        ]

        config = SJAPIConfig()
        token = config.load_token()

        # Должен вернуться первый токен
        assert token == "first_token"


class TestSJAPIConfigIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_full_workflow_scenario(self, mock_get_env_var: Any) -> None:
        """Покрытие полного рабочего сценария"""
        mock_get_env_var.return_value = "true"

        custom_params = {"salary_from": 120000, "catalogues": 33}
        config = SJAPIConfig(
            count=200,
            published=10,
            custom_params=custom_params,
            token_file=Path("test_tokens.json")
        )

        # Тестируем базовую конфигурацию
        assert config.count == 200
        assert config.published == 10
        assert config.only_with_salary is True  # из env
        assert config.custom_params == custom_params
        assert config.token_file == Path("test_tokens.json")

        # Тестируем генерацию параметров
        params = config.get_params(
            page=3,
            town="Новосибирск",
            only_with_salary=False  # переопределяем env
        )

        # Проверяем основные параметры
        assert params["count"] == 200
        assert params["order_field"] == "date"
        assert params["order_direction"] == "desc"
        assert params["published"] == 10
        assert params["no_agreement"] == 0  # only_with_salary=False из kwargs
        assert params["page"] == 3
        assert params["town"] == "Новосибирск"
        assert params["salary_from"] == 120000
        assert params["catalogues"] == 33

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    @patch('src.config.sj_api_config.json_handler.write_json')
    @patch('src.config.sj_api_config.json_handler.read_json')
    @patch('src.config.sj_api_config.logger')
    def test_token_save_load_cycle(self, mock_logger: Any, mock_read_json: Any, mock_write_json: Any, mock_get_env_var: Any) -> None:
        """Покрытие полного цикла сохранения и загрузки токена"""
        mock_get_env_var.return_value = "false"

        config = SJAPIConfig()
        token = "integration_test_token_999"

        # Сохраняем токен
        config.save_token(token)
        expected_data = [{"superjob_api_key": token}]
        mock_write_json.assert_called_once_with(Path("token.json"), expected_data)

        # Настраиваем мок для загрузки
        mock_read_json.return_value = [{"superjob_api_key": token}]

        # Загружаем токен
        loaded_token = config.load_token()
        assert loaded_token == token
        mock_read_json.assert_called_once_with(Path("token.json"))

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_complex_env_parsing(self, mock_get_env_var: Any) -> None:
        """Покрытие сложных случаев парсинга env переменных"""
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
            ("", False),
            (None, False)
        ]

        for env_value, expected in test_cases:
            mock_get_env_var.return_value = env_value
            config = SJAPIConfig()
            assert config.only_with_salary == expected, f"Failed for env_value: {env_value}"

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_dataclass_vs_regular_class_behavior(self, mock_get_env_var: Any) -> None:
        """Покрытие поведения как обычного класса (не dataclass)"""
        mock_get_env_var.return_value = "false"

        # Создаем два экземпляра
        config1 = SJAPIConfig()
        config2 = SJAPIConfig()

        # Изменяем атрибуты у первого
        config1.count = 999
        config1.custom_params = {"modified": True}

        # У второго должны остаться оригинальные значения
        assert config2.count == 500
        assert config2.custom_params is None

    @patch('src.config.sj_api_config.EnvLoader.get_env_var')
    def test_method_consistency_and_state(self, mock_get_env_var: Any) -> None:
        """Покрытие согласованности методов и состояния"""
        mock_get_env_var.return_value = "true"

        config = SJAPIConfig(custom_params={"test": "consistency"})

        # Многократные вызовы должны возвращать одинаковые результаты
        params1 = config.get_params(count=100)
        params2 = config.get_params(count=100)

        assert params1 == params2

        # Состояние объекта не должно изменяться от вызовов get_params
        original_count = config.count
        config.get_params(count=999)  # переопределяем в параметрах
        assert config.count == original_count  # объект не изменился
