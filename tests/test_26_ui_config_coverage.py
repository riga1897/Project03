#!/usr/bin/env python3
"""
Тесты модуля ui_config для 100% покрытия.

Покрывает все классы и функции в src/config/ui_config.py:
- UIPaginationConfig - конфигурация пагинации в UI
- UIConfig - основная конфигурация UI
- ui_pagination_config - глобальный экземпляр пагинации
- ui_config - глобальный экземпляр конфигурации

Модуль содержит dataclass конфигурации без I/O операций.
"""


# Импорты из реального кода для покрытия
from src.config.ui_config import (
    UIPaginationConfig,
    UIConfig,
    ui_pagination_config,
    ui_config
)


class TestUIPaginationConfig:
    """100% покрытие UIPaginationConfig dataclass"""

    def test_default_initialization(self)  -> None:
        """Покрытие инициализации с настройками по умолчанию"""
        config = UIPaginationConfig()

        # Проверяем все атрибуты по умолчанию
        assert config.default_items_per_page == 10
        assert config.search_results_per_page == 5
        assert config.saved_vacancies_per_page == 10
        assert config.top_vacancies_per_page == 10
        assert config.max_items_per_page == 50
        assert config.min_items_per_page == 1

    def test_custom_initialization(self)  -> None:
        """Покрытие инициализации с кастомными значениями"""
        config = UIPaginationConfig(
            default_items_per_page=15,
            search_results_per_page=8,
            saved_vacancies_per_page=12,
            top_vacancies_per_page=20,
            max_items_per_page=100,
            min_items_per_page=5
        )

        assert config.default_items_per_page == 15
        assert config.search_results_per_page == 8
        assert config.saved_vacancies_per_page == 12
        assert config.top_vacancies_per_page == 20
        assert config.max_items_per_page == 100
        assert config.min_items_per_page == 5

    def test_get_items_per_page_search_context(self)  -> None:
        """Покрытие получения элементов на странице для контекста 'search'"""
        config = UIPaginationConfig()

        result = config.get_items_per_page("search")

        assert result == 5  # search_results_per_page
        assert result == config.search_results_per_page

    def test_get_items_per_page_saved_context(self)  -> None:
        """Покрытие получения элементов на странице для контекста 'saved'"""
        config = UIPaginationConfig()

        result = config.get_items_per_page("saved")

        assert result == 10  # saved_vacancies_per_page
        assert result == config.saved_vacancies_per_page

    def test_get_items_per_page_top_context(self)  -> None:
        """Покрытие получения элементов на странице для контекста 'top'"""
        config = UIPaginationConfig()

        result = config.get_items_per_page("top")

        assert result == 10  # top_vacancies_per_page
        assert result == config.top_vacancies_per_page

    def test_get_items_per_page_none_context(self)  -> None:
        """Покрытие получения элементов на странице для None контекста"""
        config = UIPaginationConfig()

        result = config.get_items_per_page(None)

        assert result == 10  # default_items_per_page
        assert result == config.default_items_per_page

    def test_get_items_per_page_unknown_context(self)  -> None:
        """Покрытие получения элементов на странице для неизвестного контекста"""
        config = UIPaginationConfig()

        result = config.get_items_per_page("unknown_context")

        assert result == 10  # default_items_per_page
        assert result == config.default_items_per_page

    def test_get_items_per_page_empty_string_context(self)  -> None:
        """Покрытие получения элементов на странице для пустого контекста"""
        config = UIPaginationConfig()

        result = config.get_items_per_page("")

        assert result == 10  # default_items_per_page
        assert result == config.default_items_per_page

    def test_get_items_per_page_custom_values(self)  -> None:
        """Покрытие получения элементов с кастомными значениями"""
        config = UIPaginationConfig(
            search_results_per_page=7,
            saved_vacancies_per_page=15,
            top_vacancies_per_page=25,
            default_items_per_page=20
        )

        assert config.get_items_per_page("search") == 7
        assert config.get_items_per_page("saved") == 15
        assert config.get_items_per_page("top") == 25
        assert config.get_items_per_page("unknown") == 20

    def test_validate_items_per_page_valid_value(self)  -> None:
        """Покрытие валидации корректного значения"""
        config = UIPaginationConfig()

        result = config.validate_items_per_page(25)

        assert result == 25  # Значение в допустимых пределах

    def test_validate_items_per_page_below_minimum(self)  -> None:
        """Покрытие валидации значения ниже минимума"""
        config = UIPaginationConfig()

        result = config.validate_items_per_page(0)

        assert result == 1  # min_items_per_page
        assert result == config.min_items_per_page

    def test_validate_items_per_page_negative_value(self)  -> None:
        """Покрытие валидации отрицательного значения"""
        config = UIPaginationConfig()

        result = config.validate_items_per_page(-10)

        assert result == 1  # min_items_per_page
        assert result == config.min_items_per_page

    def test_validate_items_per_page_above_maximum(self)  -> None:
        """Покрытие валидации значения выше максимума"""
        config = UIPaginationConfig()

        result = config.validate_items_per_page(100)

        assert result == 50  # max_items_per_page
        assert result == config.max_items_per_page

    def test_validate_items_per_page_at_boundaries(self)  -> None:
        """Покрытие валидации граничных значений"""
        config = UIPaginationConfig()

        # Проверяем минимальное значение
        assert config.validate_items_per_page(1) == 1

        # Проверяем максимальное значение
        assert config.validate_items_per_page(50) == 50

    def test_validate_items_per_page_custom_limits(self)  -> None:
        """Покрытие валидации с кастомными лимитами"""
        config = UIPaginationConfig(
            min_items_per_page=5,
            max_items_per_page=100
        )

        # Ниже минимума
        assert config.validate_items_per_page(3) == 5

        # В пределах нормы
        assert config.validate_items_per_page(50) == 50

        # Выше максимума
        assert config.validate_items_per_page(150) == 100


class TestUIConfig:
    """100% покрытие UIConfig dataclass"""

    def test_default_initialization(self)  -> None:
        """Покрытие инициализации с настройками по умолчанию"""
        config = UIConfig()

        assert config.items_per_page == 5
        assert config.max_display_items == 20

    def test_custom_initialization(self)  -> None:
        """Покрытие инициализации с кастомными значениями"""
        config = UIConfig(
            items_per_page=10,
            max_display_items=50
        )

        assert config.items_per_page == 10
        assert config.max_display_items == 50

    def test_get_pagination_settings_defaults(self)  -> None:
        """Покрытие получения настроек пагинации по умолчанию"""
        config = UIConfig()

        settings = config.get_pagination_settings()

        expected = {
            "items_per_page": 5,
            "max_display_items": 20
        }
        assert settings == expected

    def test_get_pagination_settings_with_overrides(self)  -> None:
        """Покрытие получения настроек пагинации с переопределением"""
        config = UIConfig()

        settings = config.get_pagination_settings(
            items_per_page=15,
            max_display_items=30
        )

        expected = {
            "items_per_page": 15,
            "max_display_items": 30
        }
        assert settings == expected

    def test_get_pagination_settings_partial_override(self)  -> None:
        """Покрытие получения настроек с частичным переопределением"""
        config = UIConfig()

        settings = config.get_pagination_settings(items_per_page=12)

        expected = {
            "items_per_page": 12,
            "max_display_items": 20  # Значение по умолчанию
        }
        assert settings == expected

    def test_get_pagination_settings_custom_config(self)  -> None:
        """Покрытие получения настроек с кастомной конфигурацией"""
        config = UIConfig(items_per_page=8, max_display_items=25)

        settings = config.get_pagination_settings()

        expected = {
            "items_per_page": 8,
            "max_display_items": 25
        }
        assert settings == expected

    def test_get_pagination_settings_extra_kwargs(self)  -> None:
        """Покрытие получения настроек с дополнительными kwargs"""
        config = UIConfig()

        settings = config.get_pagination_settings(
            items_per_page=7,
            max_display_items=35,
            extra_param="ignored"  # Должен игнорироваться
        )

        expected = {
            "items_per_page": 7,
            "max_display_items": 35
        }
        assert settings == expected

    def test_get_pagination_settings_zero_values(self)  -> None:
        """Покрытие получения настроек с нулевыми значениями"""
        config = UIConfig()

        settings = config.get_pagination_settings(
            items_per_page=0,
            max_display_items=0
        )

        expected = {
            "items_per_page": 0,
            "max_display_items": 0
        }
        assert settings == expected

    def test_get_pagination_settings_negative_values(self)  -> None:
        """Покрытие получения настроек с отрицательными значениями"""
        config = UIConfig()

        settings = config.get_pagination_settings(
            items_per_page=-5,
            max_display_items=-10
        )

        expected = {
            "items_per_page": -5,
            "max_display_items": -10
        }
        assert settings == expected


class TestGlobalInstances:
    """Покрытие глобальных экземпляров конфигурации"""

    def test_ui_pagination_config_instance(self)  -> None:
        """Покрытие глобального экземпляра ui_pagination_config"""
        # Проверяем что экземпляр создан
        assert ui_pagination_config is not None
        assert isinstance(ui_pagination_config, UIPaginationConfig)

        # Проверяем значения по умолчанию
        assert ui_pagination_config.default_items_per_page == 10
        assert ui_pagination_config.search_results_per_page == 5
        assert ui_pagination_config.saved_vacancies_per_page == 10
        assert ui_pagination_config.top_vacancies_per_page == 10
        assert ui_pagination_config.max_items_per_page == 50
        assert ui_pagination_config.min_items_per_page == 1

    def test_ui_config_instance(self)  -> None:
        """Покрытие глобального экземпляра ui_config"""
        # Проверяем что экземпляр создан
        assert ui_config is not None
        assert isinstance(ui_config, UIConfig)

        # Проверяем значения по умолчанию
        assert ui_config.items_per_page == 5
        assert ui_config.max_display_items == 20

    def test_global_instances_functionality(self)  -> None:
        """Покрытие функциональности глобальных экземпляров"""
        # Тестируем методы глобального экземпляра пагинации
        search_items = ui_pagination_config.get_items_per_page("search")
        assert search_items == 5

        validated_value = ui_pagination_config.validate_items_per_page(100)
        assert validated_value == 50

        # Тестируем методы глобального экземпляра UI
        pagination_settings = ui_config.get_pagination_settings()
        expected = {"items_per_page": 5, "max_display_items": 20}
        assert pagination_settings == expected

    def test_global_instances_independence(self)  -> None:
        """Покрытие независимости глобальных экземпляров"""
        # Создаем новые экземпляры
        new_pagination_config = UIPaginationConfig()
        new_ui_config = UIConfig()

        # Они должны быть разными объектами от глобальных
        assert new_pagination_config is not ui_pagination_config
        assert new_ui_config is not ui_config

        # Но иметь одинаковые значения
        assert new_pagination_config.default_items_per_page == ui_pagination_config.default_items_per_page
        assert new_ui_config.items_per_page == ui_config.items_per_page


class TestUIConfigEdgeCases:
    """Покрытие граничных случаев и особых сценариев"""

    def test_pagination_config_extreme_values(self)  -> None:
        """Покрытие экстремальных значений в UIPaginationConfig"""
        config = UIPaginationConfig(
            default_items_per_page=0,
            search_results_per_page=-5,
            saved_vacancies_per_page=1000,
            top_vacancies_per_page=1,
            max_items_per_page=1000000,
            min_items_per_page=0
        )

        # Значения должны сохраняться как есть (без валидации в конструкторе)
        assert config.default_items_per_page == 0
        assert config.search_results_per_page == -5
        assert config.saved_vacancies_per_page == 1000
        assert config.top_vacancies_per_page == 1
        assert config.max_items_per_page == 1000000
        assert config.min_items_per_page == 0

    def test_ui_config_extreme_values(self)  -> None:
        """Покрытие экстремальных значений в UIConfig"""
        config = UIConfig(
            items_per_page=0,
            max_display_items=-100
        )

        assert config.items_per_page == 0
        assert config.max_display_items == -100

    def test_context_mapping_coverage(self)  -> None:
        """Покрытие всех веток в context_mapping"""
        config = UIPaginationConfig(
            search_results_per_page=1,
            saved_vacancies_per_page=2,
            top_vacancies_per_page=3,
            default_items_per_page=4
        )

        # Проверяем все известные контексты
        assert config.get_items_per_page("search") == 1
        assert config.get_items_per_page("saved") == 2
        assert config.get_items_per_page("top") == 3

        # Неизвестные контексты возвращают default
        assert config.get_items_per_page("unknown") == 4
        assert config.get_items_per_page(None) == 4

    def test_validate_boundary_conditions(self)  -> None:
        """Покрытие граничных условий валидации"""
        config = UIPaginationConfig(min_items_per_page=10, max_items_per_page=20)

        # Ровно на границах
        assert config.validate_items_per_page(10) == 10
        assert config.validate_items_per_page(20) == 20

        # За границами
        assert config.validate_items_per_page(9) == 10
        assert config.validate_items_per_page(21) == 20

    def test_equal_min_max_limits(self)  -> None:
        """Покрытие случая когда min == max"""
        config = UIPaginationConfig(min_items_per_page=15, max_items_per_page=15)

        # Все значения должны приводиться к 15
        assert config.validate_items_per_page(10) == 15
        assert config.validate_items_per_page(15) == 15
        assert config.validate_items_per_page(20) == 15


class TestUIConfigIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    def test_pagination_config_workflow(self)  -> None:
        """Покрытие полного рабочего процесса UIPaginationConfig"""
        config = UIPaginationConfig(
            search_results_per_page=3,
            max_items_per_page=30,
            min_items_per_page=2
        )

        # Получаем элементы для поиска
        search_items = config.get_items_per_page("search")
        assert search_items == 3

        # Валидируем значение выше максимума
        validated = config.validate_items_per_page(50)
        assert validated == 30

        # Валидируем корректное значение
        validated = config.validate_items_per_page(search_items)
        assert validated == 3

    def test_ui_config_workflow(self)  -> None:
        """Покрытие полного рабочего процесса UIConfig"""
        config = UIConfig(items_per_page=7, max_display_items=35)

        # Получаем настройки по умолчанию
        default_settings = config.get_pagination_settings()
        assert default_settings["items_per_page"] == 7
        assert default_settings["max_display_items"] == 35

        # Переопределяем настройки
        custom_settings = config.get_pagination_settings(items_per_page=14)
        assert custom_settings["items_per_page"] == 14
        assert custom_settings["max_display_items"] == 35

    def test_cross_class_compatibility(self)  -> None:
        """Покрытие совместимости между классами"""
        pagination_config = UIPaginationConfig()
        ui_config = UIConfig()

        # Значения могут использоваться совместно
        search_items = pagination_config.get_items_per_page("search")
        settings = ui_config.get_pagination_settings(items_per_page=search_items)

        assert settings["items_per_page"] == search_items

        # Валидация может применяться к настройкам UI
        validated_max = pagination_config.validate_items_per_page(ui_config.max_display_items)
        assert validated_max <= pagination_config.max_items_per_page

    def test_dataclass_behavior(self)  -> None:
        """Покрытие поведения dataclass"""
        config1 = UIPaginationConfig(default_items_per_page=10)
        config2 = UIPaginationConfig(default_items_per_page=10)
        config3 = UIPaginationConfig(default_items_per_page=15)

        # Dataclass обеспечивает равенство по значениям
        assert config1 == config2
        assert config1 != config3

        # Проверяем строковое представление
        config_str = str(config1)
        assert "UIPaginationConfig" in config_str
        assert "default_items_per_page=10" in config_str