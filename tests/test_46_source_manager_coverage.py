#!/usr/bin/env python3
"""
Тесты модуля source_manager.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций 
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Мокирование всех API конфигураций

Модуль содержит:
- Класс SourceManager для управления источниками API
- Методы для получения конфигурации, валидации, приоритетов
- Класс DataSource для представления источника
- Глобальный экземпляр source_manager
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Any, Dict, List, Optional

from src.utils.source_manager import (
    SourceManager,
    DataSource,
    source_manager
)


class TestSourceManagerInit:
    """100% покрытие инициализации SourceManager"""

    def test_init_sources_config(self):
        """Покрытие: инициализация с предустановленной конфигурацией"""
        sm = SourceManager()
        
        # Проверяем структуру конфигурации
        assert "hh.ru" in sm._sources_config
        assert "superjob.ru" in sm._sources_config
        
        # Проверяем конфигурацию HeadHunter
        hh_config = sm._sources_config["hh.ru"]
        assert hh_config["name"] == "HeadHunter"
        assert hh_config["display_name"] == "HeadHunter"
        assert hh_config["priority"] == 1
        assert "free_access" in hh_config["features"]
        
        # Проверяем конфигурацию SuperJob
        sj_config = sm._sources_config["superjob.ru"]
        assert sj_config["name"] == "SuperJob"
        assert sj_config["priority"] == 2
        assert "api_key_required" in sj_config["features"]

    def test_global_instance_exists(self):
        """Покрытие: глобальный экземпляр создан"""
        from src.utils.source_manager import source_manager
        
        assert isinstance(source_manager, SourceManager)
        assert "hh.ru" in source_manager._sources_config


class TestGetAvailableSources:
    """100% покрытие метода get_available_sources"""

    def test_get_available_sources(self):
        """Покрытие: получение списка доступных источников"""
        sm = SourceManager()
        
        sources = sm.get_available_sources()
        
        assert isinstance(sources, list)
        assert "hh.ru" in sources
        assert "superjob.ru" in sources
        assert len(sources) == 2


class TestGetSourceConfig:
    """100% покрытие метода get_source_config"""

    def test_get_source_config_existing_hh(self):
        """Покрытие: получение конфигурации HeadHunter"""
        sm = SourceManager()
        
        config = sm.get_source_config("hh.ru")
        
        assert config is not None
        assert config["name"] == "HeadHunter"
        assert config["priority"] == 1
        assert "api_limits" in config
        assert config["api_limits"]["requests_per_second"] == 5

    def test_get_source_config_existing_sj(self):
        """Покрытие: получение конфигурации SuperJob"""
        sm = SourceManager()
        
        config = sm.get_source_config("superjob.ru")
        
        assert config is not None
        assert config["name"] == "SuperJob"
        assert config["priority"] == 2
        assert config["api_limits"]["max_pages"] == 50

    def test_get_source_config_nonexistent(self):
        """Покрытие: получение конфигурации несуществующего источника"""
        sm = SourceManager()
        
        config = sm.get_source_config("unknown.source")
        
        assert config is None


class TestIsSourceAvailable:
    """100% покрытие метода is_source_available"""

    def test_is_source_available_hh(self):
        """Покрытие: проверка доступности HeadHunter"""
        sm = SourceManager()
        
        assert sm.is_source_available("hh.ru") is True

    def test_is_source_available_sj(self):
        """Покрытие: проверка доступности SuperJob"""
        sm = SourceManager()
        
        assert sm.is_source_available("superjob.ru") is True

    def test_is_source_available_unknown(self):
        """Покрытие: проверка доступности неизвестного источника"""
        sm = SourceManager()
        
        assert sm.is_source_available("unknown.source") is False


class TestGetSourceDisplayName:
    """100% покрытие метода get_source_display_name"""

    def test_get_source_display_name_existing(self):
        """Покрытие: получение display_name для существующего источника"""
        sm = SourceManager()
        
        name = sm.get_source_display_name("hh.ru")
        
        assert name == "HeadHunter"

    def test_get_source_display_name_nonexistent(self):
        """Покрытие: получение display_name для несуществующего источника"""
        sm = SourceManager()
        
        name = sm.get_source_display_name("unknown.source")
        
        assert name == "unknown.source"  # Возвращает исходное имя

    def test_get_source_display_name_config_without_display_name(self):
        """Покрытие: конфигурация без display_name"""
        sm = SourceManager()
        
        # Мокируем конфигурацию без display_name
        original_config = sm._sources_config["hh.ru"].copy()
        sm._sources_config["test.source"] = {"name": "Test"}  # Без display_name
        
        name = sm.get_source_display_name("test.source")
        
        assert name == "test.source"  # Возвращает исходный ключ
        
        # Восстанавливаем конфигурацию
        del sm._sources_config["test.source"]


class TestGetSourceApiLimits:
    """100% покрытие метода get_source_api_limits"""

    def test_get_source_api_limits_hh(self):
        """Покрытие: получение API лимитов HeadHunter"""
        sm = SourceManager()
        
        limits = sm.get_source_api_limits("hh.ru")
        
        assert limits is not None
        assert limits["requests_per_second"] == 5
        assert limits["max_pages"] == 20
        assert limits["max_per_page"] == 100

    def test_get_source_api_limits_sj(self):
        """Покрытие: получение API лимитов SuperJob"""
        sm = SourceManager()
        
        limits = sm.get_source_api_limits("superjob.ru")
        
        assert limits is not None
        assert limits["requests_per_second"] == 3
        assert limits["max_pages"] == 50

    def test_get_source_api_limits_nonexistent(self):
        """Покрытие: получение лимитов несуществующего источника"""
        sm = SourceManager()
        
        limits = sm.get_source_api_limits("unknown.source")
        
        assert limits is None

    def test_get_source_api_limits_config_without_limits(self):
        """Покрытие: конфигурация без api_limits"""
        sm = SourceManager()
        
        # Мокируем конфигурацию без api_limits
        sm._sources_config["test.source"] = {"name": "Test"}
        
        limits = sm.get_source_api_limits("test.source")
        
        assert limits is None
        
        # Очистка
        del sm._sources_config["test.source"]


class TestValidateSourceCredentials:
    """100% покрытие метода validate_source_credentials"""

    def test_validate_source_credentials_hh(self):
        """Покрытие: валидация учетных данных HeadHunter"""
        sm = SourceManager()
        
        # HH.ru не требует API ключа - всегда True
        result = sm.validate_source_credentials("hh.ru", {})
        assert result is True
        
        result = sm.validate_source_credentials("hh.ru", {"some": "data"})
        assert result is True

    @patch('src.utils.source_manager.SJAPIConfig')
    def test_validate_source_credentials_sj_with_api_key(self, mock_sj_config):
        """Покрытие: валидация SuperJob с API ключом"""
        sm = SourceManager()
        
        credentials = {"api_key": "test_key"}
        result = sm.validate_source_credentials("superjob.ru", credentials)
        
        assert result is True

    @patch('src.utils.source_manager.SJAPIConfig')
    def test_validate_source_credentials_sj_without_api_key_configured(self, mock_sj_config):
        """Покрытие: валидация SuperJob без API ключа, но с конфигурацией"""
        mock_config_instance = MagicMock()
        mock_config_instance.is_configured.return_value = True
        mock_sj_config.return_value = mock_config_instance
        
        sm = SourceManager()
        
        credentials = {}  # Нет API ключа
        result = sm.validate_source_credentials("superjob.ru", credentials)
        
        assert result is True
        mock_sj_config.assert_called_once()
        mock_config_instance.is_configured.assert_called_once()

    @patch('src.utils.source_manager.SJAPIConfig')
    def test_validate_source_credentials_sj_without_api_key_not_configured(self, mock_sj_config):
        """Покрытие: валидация SuperJob без API ключа и без конфигурации"""
        mock_config_instance = MagicMock()
        mock_config_instance.is_configured.return_value = False
        mock_sj_config.return_value = mock_config_instance
        
        sm = SourceManager()
        
        credentials = {}  # Нет API ключа
        result = sm.validate_source_credentials("superjob.ru", credentials)
        
        assert result is False

    @patch('src.utils.source_manager.SJAPIConfig')
    def test_validate_source_credentials_sj_with_empty_api_key(self, mock_sj_config):
        """Покрытие: валидация SuperJob с пустым API ключом"""
        mock_config_instance = MagicMock()
        mock_config_instance.is_configured.return_value = False
        mock_sj_config.return_value = mock_config_instance
        
        sm = SourceManager()
        
        credentials = {"api_key": ""}  # Пустой API ключ
        result = sm.validate_source_credentials("superjob.ru", credentials)
        
        assert result is False

    def test_validate_source_credentials_unknown_source(self):
        """Покрытие: валидация неизвестного источника"""
        sm = SourceManager()
        
        result = sm.validate_source_credentials("unknown.source", {"key": "value"})
        
        assert result is False


class TestGetSourcePriority:
    """100% покрытие метода get_source_priority"""

    def test_get_source_priority_hh(self):
        """Покрытие: получение приоритета HeadHunter"""
        sm = SourceManager()
        
        priority = sm.get_source_priority("hh.ru")
        
        assert priority == 1

    def test_get_source_priority_sj(self):
        """Покрытие: получение приоритета SuperJob"""
        sm = SourceManager()
        
        priority = sm.get_source_priority("superjob.ru")
        
        assert priority == 2

    def test_get_source_priority_nonexistent(self):
        """Покрытие: получение приоритета несуществующего источника"""
        sm = SourceManager()
        
        priority = sm.get_source_priority("unknown.source")
        
        assert priority == 999  # Значение по умолчанию

    def test_get_source_priority_config_without_priority(self):
        """Покрытие: конфигурация без priority"""
        sm = SourceManager()
        
        # Мокируем конфигурацию без priority
        sm._sources_config["test.source"] = {"name": "Test"}
        
        priority = sm.get_source_priority("test.source")
        
        assert priority == 999  # Значение по умолчанию
        
        # Очистка
        del sm._sources_config["test.source"]


class TestSortSourcesByPriority:
    """100% покрытие метода sort_sources_by_priority"""

    def test_sort_sources_by_priority_normal_order(self):
        """Покрытие: сортировка в правильном порядке"""
        sm = SourceManager()
        
        sources = ["superjob.ru", "hh.ru"]  # Неправильный порядок
        sorted_sources = sm.sort_sources_by_priority(sources)
        
        assert sorted_sources == ["hh.ru", "superjob.ru"]  # Правильный порядок

    def test_sort_sources_by_priority_already_sorted(self):
        """Покрытие: сортировка уже отсортированного списка"""
        sm = SourceManager()
        
        sources = ["hh.ru", "superjob.ru"]  # Уже правильный порядок
        sorted_sources = sm.sort_sources_by_priority(sources)
        
        assert sorted_sources == ["hh.ru", "superjob.ru"]

    def test_sort_sources_by_priority_with_unknown(self):
        """Покрытие: сортировка с неизвестными источниками"""
        sm = SourceManager()
        
        sources = ["unknown1.source", "hh.ru", "unknown2.source", "superjob.ru"]
        sorted_sources = sm.sort_sources_by_priority(sources)
        
        # HH должен быть первым, SJ вторым, неизвестные в конце
        assert sorted_sources[0] == "hh.ru"
        assert sorted_sources[1] == "superjob.ru"
        assert "unknown1.source" in sorted_sources[2:]
        assert "unknown2.source" in sorted_sources[2:]

    def test_sort_sources_by_priority_empty_list(self):
        """Покрытие: сортировка пустого списка"""
        sm = SourceManager()
        
        sources = []
        sorted_sources = sm.sort_sources_by_priority(sources)
        
        assert sorted_sources == []


class TestGetSourceFeatures:
    """100% покрытие метода get_source_features"""

    def test_get_source_features_hh(self):
        """Покрытие: получение функций HeadHunter"""
        sm = SourceManager()
        
        features = sm.get_source_features("hh.ru")
        
        assert isinstance(features, list)
        assert "free_access" in features
        assert "large_database" in features
        assert "detailed_info" in features

    def test_get_source_features_sj(self):
        """Покрытие: получение функций SuperJob"""
        sm = SourceManager()
        
        features = sm.get_source_features("superjob.ru")
        
        assert isinstance(features, list)
        assert "api_key_required" in features
        assert "salary_details" in features
        assert "contact_info" in features

    def test_get_source_features_nonexistent(self):
        """Покрытие: получение функций несуществующего источника"""
        sm = SourceManager()
        
        features = sm.get_source_features("unknown.source")
        
        assert features == []

    def test_get_source_features_config_without_features(self):
        """Покрытие: конфигурация без features"""
        sm = SourceManager()
        
        # Мокируем конфигурацию без features
        sm._sources_config["test.source"] = {"name": "Test"}
        
        features = sm.get_source_features("test.source")
        
        assert features == []
        
        # Очистка
        del sm._sources_config["test.source"]


class TestGetSourceConfigClass:
    """100% покрытие метода get_source_config_class"""

    def test_get_source_config_class_hh(self):
        """Покрытие: получение класса конфигурации HeadHunter"""
        sm = SourceManager()
        
        config_class = sm.get_source_config_class("hh.ru")
        
        # Проверяем, что это правильный класс
        from src.config.hh_api_config import HHAPIConfig
        assert config_class == HHAPIConfig

    def test_get_source_config_class_sj(self):
        """Покрытие: получение класса конфигурации SuperJob"""
        sm = SourceManager()
        
        config_class = sm.get_source_config_class("superjob.ru")
        
        # Проверяем, что это правильный класс
        from src.config.sj_api_config import SJAPIConfig
        assert config_class == SJAPIConfig

    def test_get_source_config_class_nonexistent(self):
        """Покрытие: получение класса конфигурации несуществующего источника"""
        sm = SourceManager()
        
        config_class = sm.get_source_config_class("unknown.source")
        
        assert config_class is None

    def test_get_source_config_class_config_without_class(self):
        """Покрытие: конфигурация без config_class"""
        sm = SourceManager()
        
        # Мокируем конфигурацию без config_class
        sm._sources_config["test.source"] = {"name": "Test"}
        
        config_class = sm.get_source_config_class("test.source")
        
        assert config_class is None
        
        # Очистка
        del sm._sources_config["test.source"]


class TestCreateSourceInstance:
    """100% покрытие метода create_source_instance"""

    def test_create_source_instance_hh(self):
        """Покрытие: создание экземпляра HeadHunter API"""
        sm = SourceManager()
        
        result = sm.create_source_instance("hh.ru")
        
        # Проверяем, что возвращается экземпляр правильного класса
        from src.config.hh_api_config import HHAPIConfig
        assert isinstance(result, HHAPIConfig)

    def test_create_source_instance_sj(self):
        """Покрытие: создание экземпляра SuperJob API"""
        sm = SourceManager()
        
        result = sm.create_source_instance("superjob.ru")
        
        # Проверяем, что возвращается экземпляр правильного класса
        from src.config.sj_api_config import SJAPIConfig
        assert isinstance(result, SJAPIConfig)

    def test_create_source_instance_nonexistent(self):
        """Покрытие: создание экземпляра несуществующего источника"""
        sm = SourceManager()
        
        result = sm.create_source_instance("unknown.source")
        
        assert result is None

    def test_create_source_instance_config_without_class(self):
        """Покрытие: создание экземпляра для конфигурации без класса"""
        sm = SourceManager()
        
        # Мокируем конфигурацию без config_class
        sm._sources_config["test.source"] = {"name": "Test"}
        
        result = sm.create_source_instance("test.source")
        
        assert result is None
        
        # Очистка
        del sm._sources_config["test.source"]


class TestDataSourceClass:
    """100% покрытие класса DataSource"""

    def test_data_source_init(self):
        """Покрытие: инициализация DataSource"""
        ds = DataSource("hh.ru", "HeadHunter", "HeadHunter API")
        
        assert ds.key == "hh.ru"
        assert ds.name == "HeadHunter"
        assert ds.display_name == "HeadHunter API"

    def test_data_source_init_different_values(self):
        """Покрытие: инициализация DataSource с разными значениями"""
        ds = DataSource("custom.api", "Custom API", "My Custom API")
        
        assert ds.key == "custom.api"
        assert ds.name == "Custom API"
        assert ds.display_name == "My Custom API"

    def test_data_source_attributes_accessible(self):
        """Покрытие: доступ к атрибутам DataSource"""
        ds = DataSource("test", "Test Name", "Test Display")
        
        # Проверяем, что атрибуты можно менять
        ds.key = "new_test"
        ds.name = "New Test Name"
        ds.display_name = "New Test Display"
        
        assert ds.key == "new_test"
        assert ds.name == "New Test Name"
        assert ds.display_name == "New Test Display"


class TestIntegrationScenarios:
    """Интеграционные тесты для проверки совместной работы методов"""

    def test_full_source_management_flow(self):
        """Покрытие: полный цикл управления источниками"""
        sm = SourceManager()
        
        # Получаем все источники
        sources = sm.get_available_sources()
        assert len(sources) == 2
        
        # Сортируем по приоритету
        sorted_sources = sm.sort_sources_by_priority(sources)
        assert sorted_sources[0] == "hh.ru"  # Первый приоритет
        
        # Проверяем конфигурацию первого источника
        config = sm.get_source_config(sorted_sources[0])
        assert config is not None
        assert config["priority"] == 1
        
        # Получаем лимиты API
        limits = sm.get_source_api_limits(sorted_sources[0])
        assert limits["requests_per_second"] == 5

    @patch('src.utils.source_manager.SJAPIConfig')
    def test_credentials_validation_flow(self, mock_sj_config):
        """Покрытие: поток валидации учетных данных"""
        mock_config_instance = MagicMock()
        mock_config_instance.is_configured.return_value = True
        mock_sj_config.return_value = mock_config_instance
        
        sm = SourceManager()
        
        # Валидация HH (всегда True)
        assert sm.validate_source_credentials("hh.ru", {}) is True
        
        # Валидация SJ с API ключом
        assert sm.validate_source_credentials("superjob.ru", {"api_key": "test"}) is True
        
        # Валидация SJ без API ключа, но с конфигурацией
        assert sm.validate_source_credentials("superjob.ru", {}) is True

    def test_source_features_and_config_integration(self):
        """Покрытие: интеграция функций источников и конфигурации"""
        sm = SourceManager()
        
        # Проверяем функции обоих источников
        hh_features = sm.get_source_features("hh.ru")
        sj_features = sm.get_source_features("superjob.ru")
        
        assert "free_access" in hh_features
        assert "api_key_required" in sj_features
        
        # Проверяем отображаемые имена
        hh_display = sm.get_source_display_name("hh.ru")
        sj_display = sm.get_source_display_name("superjob.ru")
        
        assert hh_display == "HeadHunter"
        assert sj_display == "SuperJob"

    def test_error_handling_edge_cases(self):
        """Покрытие: граничные случаи и обработка ошибок"""
        sm = SourceManager()
        
        # Тестируем все методы с несуществующим источником
        assert sm.get_source_config("fake") is None
        assert sm.is_source_available("fake") is False
        assert sm.get_source_display_name("fake") == "fake"
        assert sm.get_source_api_limits("fake") is None
        assert sm.validate_source_credentials("fake", {}) is False
        assert sm.get_source_priority("fake") == 999
        assert sm.get_source_features("fake") == []
        assert sm.get_source_config_class("fake") is None
        assert sm.create_source_instance("fake") is None

    def test_data_source_with_source_manager_integration(self):
        """Покрытие: интеграция DataSource с SourceManager"""
        sm = SourceManager()
        
        # Создаем DataSource на основе данных из SourceManager
        hh_config = sm.get_source_config("hh.ru")
        ds = DataSource(
            key="hh.ru",
            name=hh_config["name"],
            display_name=hh_config["display_name"]
        )
        
        assert ds.key == "hh.ru"
        assert ds.name == "HeadHunter"
        assert ds.display_name == "HeadHunter"