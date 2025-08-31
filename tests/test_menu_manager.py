"""
Тесты для MenuManager

Содержит тесты для проверки корректности работы менеджера меню.
"""

from unittest.mock import Mock, patch

import pytest

from src.utils.menu_manager import MenuManager


class TestMenuManager:
    """Тесты для MenuManager"""

    @pytest.fixture
    def menu_manager(self):
        """Фикстура менеджера меню"""
        return MenuManager()

    def test_menu_manager_initialization(self, menu_manager):
        """Тест инициализации менеджера меню"""
        assert menu_manager is not None
        assert hasattr(menu_manager, "display_menu")

    @patch("builtins.print")
    def test_display_menu(self, mock_print, menu_manager):
        """Тест отображения меню"""
        menu_manager.display_menu()
        mock_print.assert_called()

    def test_menu_manager_methods_exist(self, menu_manager):
        """Тест существования основных методов"""
        assert hasattr(menu_manager, "display_menu")
        assert callable(getattr(menu_manager, "display_menu"))

    @patch("builtins.print")
    def test_display_menu_content(self, mock_print, menu_manager):
        """Тест содержимого отображаемого меню"""
        menu_manager.display_menu()

        # Проверяем, что print вызывался
        assert mock_print.called

        # Получаем все вызовы print
        calls = mock_print.call_args_list
        printed_content = [str(call[0][0]) if call[0] else "" for call in calls]

        # Проверяем наличие основных элементов меню
        full_output = " ".join(printed_content)
        assert "поиск" in full_output.lower() or "выберите" in full_output.lower()
