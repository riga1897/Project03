"""
100% покрытие ui_config.py модуля
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.config.ui_config import UIPaginationConfig, UIConfig


class TestUIPaginationConfig:
    """100% покрытие UIPaginationConfig"""

    def test_ui_pagination_config_defaults(self):
        """Тест инициализации UIPaginationConfig с дефолтными значениями - покрывает строки 15-24"""
        config = UIPaginationConfig()
        
        assert config.default_items_per_page == 10
        assert config.search_results_per_page == 5
        assert config.saved_vacancies_per_page == 10
        assert config.top_vacancies_per_page == 10
        assert config.max_items_per_page == 50
        assert config.min_items_per_page == 1

    def test_ui_pagination_config_custom_values(self):
        """Тест инициализации UIPaginationConfig с кастомными значениями"""
        config = UIPaginationConfig(
            default_items_per_page=15,
            search_results_per_page=8,
            saved_vacancies_per_page=12,
            top_vacancies_per_page=20,
            max_items_per_page=100,
            min_items_per_page=2
        )
        
        assert config.default_items_per_page == 15
        assert config.search_results_per_page == 8
        assert config.saved_vacancies_per_page == 12
        assert config.top_vacancies_per_page == 20
        assert config.max_items_per_page == 100
        assert config.min_items_per_page == 2

    def test_get_items_per_page_search_context(self):
        """Тест метода get_items_per_page для контекста 'search' - покрывает строки 36-42"""
        config = UIPaginationConfig()
        
        result = config.get_items_per_page("search")
        
        assert result == 5  # search_results_per_page

    def test_get_items_per_page_saved_context(self):
        """Тест метода get_items_per_page для контекста 'saved'"""
        config = UIPaginationConfig()
        
        result = config.get_items_per_page("saved")
        
        assert result == 10  # saved_vacancies_per_page

    def test_get_items_per_page_top_context(self):
        """Тест метода get_items_per_page для контекста 'top'"""
        config = UIPaginationConfig()
        
        result = config.get_items_per_page("top")
        
        assert result == 10  # top_vacancies_per_page

    def test_get_items_per_page_default_context(self):
        """Тест метода get_items_per_page для дефолтного контекста"""
        config = UIPaginationConfig()
        
        result = config.get_items_per_page(None)
        
        assert result == 10  # default_items_per_page

    def test_get_items_per_page_unknown_context(self):
        """Тест метода get_items_per_page для неизвестного контекста"""
        config = UIPaginationConfig()
        
        result = config.get_items_per_page("unknown_context")
        
        assert result == 10  # default_items_per_page

    def test_validate_items_per_page_valid_value(self):
        """Тест валидации нормального значения - покрывает строку 58"""
        config = UIPaginationConfig()
        
        result = config.validate_items_per_page(25)
        
        assert result == 25

    def test_validate_items_per_page_below_minimum(self):
        """Тест валидации значения ниже минимума - покрывает строки 54-55"""
        config = UIPaginationConfig()
        
        result = config.validate_items_per_page(0)
        
        assert result == 1  # min_items_per_page

    def test_validate_items_per_page_above_maximum(self):
        """Тест валидации значения выше максимума - покрывает строки 56-57"""
        config = UIPaginationConfig()
        
        result = config.validate_items_per_page(100)
        
        assert result == 50  # max_items_per_page

    def test_validate_items_per_page_custom_limits(self):
        """Тест валидации с кастомными лимитами"""
        config = UIPaginationConfig(min_items_per_page=5, max_items_per_page=30)
        
        # Ниже минимума
        assert config.validate_items_per_page(2) == 5
        
        # Выше максимума
        assert config.validate_items_per_page(50) == 30
        
        # В пределах нормы
        assert config.validate_items_per_page(15) == 15

    def test_get_items_per_page_with_custom_values(self):
        """Тест get_items_per_page с кастомными значениями"""
        config = UIPaginationConfig(
            search_results_per_page=3,
            saved_vacancies_per_page=7,
            top_vacancies_per_page=15,
            default_items_per_page=12
        )
        
        assert config.get_items_per_page("search") == 3
        assert config.get_items_per_page("saved") == 7
        assert config.get_items_per_page("top") == 15
        assert config.get_items_per_page("default") == 12
        assert config.get_items_per_page(None) == 12


class TestUIConfig:
    """100% покрытие UIConfig"""

    def test_ui_config_defaults(self):
        """Тест инициализации UIConfig с дефолтными значениями - покрывает строки 69-70"""
        config = UIConfig()
        
        assert config.items_per_page == 5
        assert config.max_display_items == 20

    def test_ui_config_custom_values(self):
        """Тест инициализации UIConfig с кастомными значениями"""
        config = UIConfig(items_per_page=15, max_display_items=50)
        
        assert config.items_per_page == 15
        assert config.max_display_items == 50

    def test_get_pagination_settings_defaults(self):
        """Тест метода get_pagination_settings без параметров - покрывает строки 78-84"""
        config = UIConfig()
        
        result = config.get_pagination_settings()
        
        expected = {
            "items_per_page": 5,
            "max_display_items": 20
        }
        assert result == expected

    def test_get_pagination_settings_with_overrides(self):
        """Тест метода get_pagination_settings с переопределениями - только предусмотренные параметры"""
        config = UIConfig()
        
        result = config.get_pagination_settings(
            items_per_page=10,
            max_display_items=30
        )
        
        expected = {
            "items_per_page": 10,
            "max_display_items": 30
        }
        assert result == expected

    def test_get_pagination_settings_partial_overrides(self):
        """Тест метода get_pagination_settings с частичными переопределениями"""
        config = UIConfig(items_per_page=8, max_display_items=25)
        
        result = config.get_pagination_settings(items_per_page=12)
        
        expected = {
            "items_per_page": 12,  # Переопределено
            "max_display_items": 25  # Значение из config
        }
        assert result == expected


class TestUIConfigIntegration:
    """Интеграционные тесты UI конфигураций"""

    def test_pagination_config_integration_with_ui_config(self):
        """Тест интеграции UIPaginationConfig и UIConfig"""
        pagination_config = UIPaginationConfig(
            default_items_per_page=8,
            search_results_per_page=3
        )
        ui_config = UIConfig(items_per_page=pagination_config.default_items_per_page)
        
        # Проверяем что значения согласованы
        assert ui_config.items_per_page == 8
        assert pagination_config.get_items_per_page("search") == 3
        assert pagination_config.get_items_per_page(None) == 8

    def test_pagination_validation_edge_cases(self):
        """Тест граничных случаев валидации"""
        config = UIPaginationConfig(min_items_per_page=1, max_items_per_page=50)
        
        # Граничные значения
        assert config.validate_items_per_page(1) == 1  # Минимум
        assert config.validate_items_per_page(50) == 50  # Максимум
        
        # Отрицательные значения
        assert config.validate_items_per_page(-5) == 1
        
        # Очень большие значения
        assert config.validate_items_per_page(1000) == 50

    def test_all_context_mappings(self):
        """Тест всех возможных контекстов"""
        config = UIPaginationConfig(
            search_results_per_page=5,
            saved_vacancies_per_page=10,
            top_vacancies_per_page=15,
            default_items_per_page=20
        )
        
        contexts_and_expected = [
            ("search", 5),
            ("saved", 10),
            ("top", 15),
            (None, 20),
            ("", 20),  # Пустая строка
            ("nonexistent", 20),  # Несуществующий контекст
        ]
        
        for context, expected in contexts_and_expected:
            assert config.get_items_per_page(context) == expected

    def test_ui_config_comprehensive_settings(self):
        """Comprehensive тест всех настроек UI конфигурации"""
        config = UIConfig(items_per_page=7, max_display_items=35)
        
        # Без переопределений
        settings1 = config.get_pagination_settings()
        assert settings1["items_per_page"] == 7
        assert settings1["max_display_items"] == 35
        
        # С переопределениями
        settings2 = config.get_pagination_settings(
            items_per_page=12,
            max_display_items=40
        )
        assert settings2["items_per_page"] == 12
        assert settings2["max_display_items"] == 40

    def test_config_consistency(self):
        """Тест консистентности конфигураций"""
        pagination = UIPaginationConfig()
        ui = UIConfig()
        
        # Проверяем что основные значения логически согласованы
        assert pagination.min_items_per_page <= pagination.default_items_per_page
        assert pagination.default_items_per_page <= pagination.max_items_per_page
        assert ui.items_per_page <= ui.max_display_items
        
        # Проверяем валидацию
        validated_min = pagination.validate_items_per_page(pagination.min_items_per_page)
        validated_max = pagination.validate_items_per_page(pagination.max_items_per_page)
        
        assert validated_min == pagination.min_items_per_page
        assert validated_max == pagination.max_items_per_page