#!/usr/bin/env python3
"""
Тесты модуля api_config для 100% покрытия.

Покрывает все функции в src/config/api_config.py:
- APIConfig - основная конфигурация API
- __init__ - инициализация с параметрами и зависимостями
- get_pagination_params - получение параметров пагинации

Все I/O операции и зависимости заменены на mock для соблюдения принципа нулевого I/O.
"""

import pytest
from typing import Any, Dict, Optional
from unittest.mock import patch, MagicMock

# Импорты из реального кода для покрытия
from src.config.api_config import APIConfig


class TestAPIConfig:
    """100% покрытие APIConfig класса"""

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_init_with_defaults(self, mock_sj_config, mock_hh_config):
        """Покрытие инициализации с параметрами по умолчанию"""
        # Настраиваем моки
        mock_hh_instance = MagicMock()
        mock_sj_instance = MagicMock()
        mock_hh_config.return_value = mock_hh_instance
        mock_sj_config.return_value = mock_sj_instance
        
        config = APIConfig()
        
        # Проверяем значения по умолчанию
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20
        
        # Проверяем что создались конфигурации для HH и SJ
        assert config.hh_config == mock_hh_instance
        assert config.sj_config == mock_sj_instance
        mock_hh_config.assert_called_once()
        mock_sj_config.assert_called_once()

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_init_with_custom_parameters(self, mock_sj_config, mock_hh_config):
        """Покрытие инициализации с кастомными параметрами"""
        # Настраиваем моки
        mock_hh_instance = MagicMock()
        mock_sj_instance = MagicMock()
        mock_hh_config.return_value = mock_hh_instance
        mock_sj_config.return_value = mock_sj_instance
        
        config = APIConfig(
            user_agent="CustomApp/2.0",
            timeout=30,
            request_delay=1.0,
            max_pages=50
        )
        
        # Проверяем кастомные значения
        assert config.user_agent == "CustomApp/2.0"
        assert config.timeout == 30
        assert config.request_delay == 1.0
        assert config.max_pages == 50
        
        # Проверяем что создались конфигурации
        assert config.hh_config == mock_hh_instance
        assert config.sj_config == mock_sj_instance

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_init_with_custom_hh_config(self, mock_sj_config, mock_hh_config):
        """Покрытие инициализации с кастомной конфигурацией HH"""
        # Создаем кастомную конфигурацию HH
        custom_hh_config = MagicMock()
        mock_sj_instance = MagicMock()
        mock_sj_config.return_value = mock_sj_instance
        
        config = APIConfig(hh_config=custom_hh_config)
        
        # Проверяем что используется переданная конфигурация HH
        assert config.hh_config == custom_hh_config
        assert config.sj_config == mock_sj_instance
        
        # HHAPIConfig не должен был вызываться (используется переданный)
        mock_hh_config.assert_not_called()
        mock_sj_config.assert_called_once()

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_init_with_none_hh_config(self, mock_sj_config, mock_hh_config):
        """Покрытие инициализации с None конфигурацией HH"""
        # Настраиваем моки
        mock_hh_instance = MagicMock()
        mock_sj_instance = MagicMock()
        mock_hh_config.return_value = mock_hh_instance
        mock_sj_config.return_value = mock_sj_instance
        
        config = APIConfig(hh_config=None)
        
        # При None должен создаться новый экземпляр HHAPIConfig
        assert config.hh_config == mock_hh_instance
        assert config.sj_config == mock_sj_instance
        mock_hh_config.assert_called_once()
        mock_sj_config.assert_called_once()

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_init_all_parameters_custom(self, mock_sj_config, mock_hh_config):
        """Покрытие инициализации со всеми кастомными параметрами"""
        custom_hh_config = MagicMock()
        mock_sj_instance = MagicMock()
        mock_sj_config.return_value = mock_sj_instance
        
        config = APIConfig(
            user_agent="FullCustomApp/3.0",
            timeout=60,
            request_delay=2.5,
            hh_config=custom_hh_config,
            max_pages=100
        )
        
        # Проверяем все параметры
        assert config.user_agent == "FullCustomApp/3.0"
        assert config.timeout == 60
        assert config.request_delay == 2.5
        assert config.hh_config == custom_hh_config
        assert config.sj_config == mock_sj_instance
        assert config.max_pages == 100

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_get_pagination_params_defaults(self, mock_sj_config, mock_hh_config):
        """Покрытие получения параметров пагинации по умолчанию"""
        config = APIConfig()
        
        params = config.get_pagination_params()
        
        expected = {"max_pages": 20}  # Значение по умолчанию
        assert params == expected

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_get_pagination_params_with_override(self, mock_sj_config, mock_hh_config):
        """Покрытие получения параметров пагинации с переопределением"""
        config = APIConfig(max_pages=30)
        
        # Переопределяем через kwargs
        params = config.get_pagination_params(max_pages=50)
        
        expected = {"max_pages": 50}  # Переопределенное значение
        assert params == expected

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_get_pagination_params_no_override(self, mock_sj_config, mock_hh_config):
        """Покрытие получения параметров пагинации без переопределения"""
        config = APIConfig(max_pages=75)
        
        params = config.get_pagination_params()
        
        expected = {"max_pages": 75}  # Значение из конфигурации
        assert params == expected

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_get_pagination_params_with_extra_kwargs(self, mock_sj_config, mock_hh_config):
        """Покрытие получения параметров пагинации с дополнительными kwargs"""
        config = APIConfig()
        
        # Передаем дополнительные параметры, но функция должна возвращать только max_pages
        params = config.get_pagination_params(
            max_pages=40,
            extra_param="ignored",
            another_param=123
        )
        
        expected = {"max_pages": 40}
        assert params == expected

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_get_pagination_params_zero_max_pages(self, mock_sj_config, mock_hh_config):
        """Покрытие получения параметров пагинации с нулевым max_pages"""
        config = APIConfig()
        
        params = config.get_pagination_params(max_pages=0)
        
        expected = {"max_pages": 0}
        assert params == expected

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_get_pagination_params_negative_max_pages(self, mock_sj_config, mock_hh_config):
        """Покрытие получения параметров пагинации с отрицательным max_pages"""
        config = APIConfig()
        
        params = config.get_pagination_params(max_pages=-5)
        
        expected = {"max_pages": -5}
        assert params == expected


class TestAPIConfigEdgeCases:
    """Покрытие граничных случаев и особых сценариев"""

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_init_with_zero_timeout(self, mock_sj_config, mock_hh_config):
        """Покрытие инициализации с нулевым таймаутом"""
        config = APIConfig(timeout=0)
        
        assert config.timeout == 0

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_init_with_zero_request_delay(self, mock_sj_config, mock_hh_config):
        """Покрытие инициализации с нулевой задержкой запросов"""
        config = APIConfig(request_delay=0.0)
        
        assert config.request_delay == 0.0

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_init_with_empty_user_agent(self, mock_sj_config, mock_hh_config):
        """Покрытие инициализации с пустым user agent"""
        config = APIConfig(user_agent="")
        
        assert config.user_agent == ""

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_init_with_negative_values(self, mock_sj_config, mock_hh_config):
        """Покрытие инициализации с отрицательными значениями"""
        config = APIConfig(
            timeout=-10,
            request_delay=-1.5,
            max_pages=-5
        )
        
        assert config.timeout == -10
        assert config.request_delay == -1.5
        assert config.max_pages == -5

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_multiple_instances_independence(self, mock_sj_config, mock_hh_config):
        """Покрытие независимости множественных экземпляров"""
        # Создаем разные моки для каждого вызова
        mock_hh_config.side_effect = [MagicMock(), MagicMock()]
        mock_sj_config.side_effect = [MagicMock(), MagicMock()]
        
        config1 = APIConfig(user_agent="App1", timeout=10)
        config2 = APIConfig(user_agent="App2", timeout=20)
        
        # Экземпляры должны быть независимыми
        assert config1.user_agent != config2.user_agent
        assert config1.timeout != config2.timeout
        assert config1.hh_config != config2.hh_config
        assert config1.sj_config != config2.sj_config


class TestAPIConfigDependencies:
    """Покрытие взаимодействия с зависимостями"""

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_hh_config_creation_called_correctly(self, mock_sj_config, mock_hh_config):
        """Покрытие корректного вызова создания HH конфигурации"""
        config = APIConfig()
        
        # HHAPIConfig должен вызываться без параметров
        mock_hh_config.assert_called_once_with()

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_sj_config_creation_called_correctly(self, mock_sj_config, mock_hh_config):
        """Покрытие корректного вызова создания SJ конфигурации"""
        config = APIConfig()
        
        # SJAPIConfig должен вызываться без параметров
        mock_sj_config.assert_called_once_with()

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_config_objects_stored_correctly(self, mock_sj_config, mock_hh_config):
        """Покрытие корректного сохранения объектов конфигурации"""
        mock_hh_instance = MagicMock()
        mock_sj_instance = MagicMock()
        mock_hh_config.return_value = mock_hh_instance
        mock_sj_config.return_value = mock_sj_instance
        
        config = APIConfig()
        
        # Объекты должны быть сохранены как атрибуты
        assert hasattr(config, 'hh_config')
        assert hasattr(config, 'sj_config')
        assert config.hh_config is mock_hh_instance
        assert config.sj_config is mock_sj_instance

    @patch('src.config.api_config.HHAPIConfig', side_effect=Exception("HH Config Error"))
    @patch('src.config.api_config.SJAPIConfig')
    def test_hh_config_creation_exception_propagated(self, mock_sj_config, mock_hh_config):
        """Покрытие распространения исключений при создании HH конфигурации"""
        with pytest.raises(Exception, match="HH Config Error"):
            APIConfig()

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig', side_effect=Exception("SJ Config Error"))
    def test_sj_config_creation_exception_propagated(self, mock_sj_config, mock_hh_config):
        """Покрытие распространения исключений при создании SJ конфигурации"""
        mock_hh_config.return_value = MagicMock()
        
        with pytest.raises(Exception, match="SJ Config Error"):
            APIConfig()


class TestAPIConfigIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_full_configuration_workflow(self, mock_sj_config, mock_hh_config):
        """Покрытие полного рабочего процесса конфигурации"""
        mock_hh_instance = MagicMock()
        mock_sj_instance = MagicMock()
        mock_hh_config.return_value = mock_hh_instance
        mock_sj_config.return_value = mock_sj_instance
        
        # Создаем конфигурацию с кастомными параметрами
        config = APIConfig(
            user_agent="IntegrationTestApp/1.0",
            timeout=45,
            request_delay=1.5,
            max_pages=25
        )
        
        # Проверяем базовые параметры
        assert config.user_agent == "IntegrationTestApp/1.0"
        assert config.timeout == 45
        assert config.request_delay == 1.5
        assert config.max_pages == 25
        
        # Проверяем что созданы зависимые конфигурации
        assert config.hh_config is mock_hh_instance
        assert config.sj_config is mock_sj_instance
        
        # Тестируем пагинацию
        pagination_params = config.get_pagination_params()
        assert pagination_params == {"max_pages": 25}
        
        # Тестируем переопределение пагинации
        custom_pagination = config.get_pagination_params(max_pages=100)
        assert custom_pagination == {"max_pages": 100}

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_state_consistency_after_operations(self, mock_sj_config, mock_hh_config):
        """Покрытие согласованности состояния после операций"""
        config = APIConfig(max_pages=15)
        
        # Многократные вызовы get_pagination_params не должны изменять состояние
        params1 = config.get_pagination_params()
        params2 = config.get_pagination_params()
        params3 = config.get_pagination_params(max_pages=30)
        params4 = config.get_pagination_params()
        
        # Состояние объекта не должно изменяться
        assert config.max_pages == 15
        assert params1 == params2 == params4
        assert params1 == {"max_pages": 15}
        assert params3 == {"max_pages": 30}

    @patch('src.config.api_config.HHAPIConfig')
    @patch('src.config.api_config.SJAPIConfig')
    def test_parameter_types_preserved(self, mock_sj_config, mock_hh_config):
        """Покрытие сохранения типов параметров"""
        config = APIConfig(
            user_agent="TypeTest",
            timeout=30,
            request_delay=2.5,
            max_pages=50
        )
        
        # Проверяем типы параметров
        assert isinstance(config.user_agent, str)
        assert isinstance(config.timeout, int)
        assert isinstance(config.request_delay, float)
        assert isinstance(config.max_pages, int)
        
        # Проверяем типы в результатах функций
        params = config.get_pagination_params()
        assert isinstance(params, dict)
        assert isinstance(params["max_pages"], int)