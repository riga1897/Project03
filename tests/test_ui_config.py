import pytest

from src.config.ui_config import UIConfig


class TestUIConfig:
    def test_ui_config_initialization(self):
        """Тест инициализации UI конфигурации"""
        config = UIConfig()
        assert hasattr(config, "items_per_page") or hasattr(config, "max_display_items")

    def test_ui_config_pagination(self):
        """Тест настроек пагинации"""
        config = UIConfig()
        assert config.items_per_page > 0
        assert config.max_display_items > 0

    def test_ui_config_display_settings(self):
        """Тест настроек отображения"""
        config = UIConfig()
        if hasattr(config, "SHOW_SALARY"):
            assert isinstance(config.SHOW_SALARY, bool)
        if hasattr(config, "SHOW_EXPERIENCE"):
            assert isinstance(config.SHOW_EXPERIENCE, bool)

    def test_ui_config_menu_settings(self):
        """Тест настроек меню"""
        config = UIConfig()
        if hasattr(config, "MENU_ITEMS"):
            assert isinstance(config.MENU_ITEMS, (list, dict))
        if hasattr(config, "MENU_TITLE"):
            assert isinstance(config.MENU_TITLE, str)

    def test_ui_config_colors(self):
        """Тест настроек цветов"""
        config = UIConfig()
        if hasattr(config, "COLORS"):
            assert isinstance(config.COLORS, dict)
        if hasattr(config, "USE_COLORS"):
            assert isinstance(config.USE_COLORS, bool)
