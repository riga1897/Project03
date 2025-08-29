"""
Тесты для модуля MenuManager
"""

from unittest.mock import Mock, patch

import pytest

from src.utils.menu_manager import MenuManager


class TestMenuManager:
    """Тесты для класса MenuManager"""

    @pytest.fixture
    def menu_manager(self):
        """Фикстура MenuManager"""
        return MenuManager()

    def test_menu_manager_initialization(self, menu_manager):
        """Тест инициализации MenuManager"""
        assert menu_manager is not None
        assert hasattr(menu_manager, "menu_items")

    @patch("builtins.input", return_value="1")
    def test_get_user_choice_valid(self, mock_input, menu_manager):
        """Тест получения корректного выбора пользователя"""
        menu_items = ["Item 1", "Item 2", "Exit"]
        choice = menu_manager.get_user_choice(menu_items)
        assert choice == "1"

    @patch("builtins.input", side_effect=["invalid", "2"])
    @patch("builtins.print")
    def test_get_user_choice_invalid_then_valid(self, mock_print, mock_input, menu_manager):
        """Тест обработки некорректного, а затем корректного выбора"""
        menu_items = ["Item 1", "Item 2"]
        choice = menu_manager.get_user_choice(menu_items)
        assert choice == "2"

    def test_display_menu_items(self, menu_manager):
        """Тест отображения элементов меню"""
        menu_items = ["Search", "View", "Exit"]
        with patch("builtins.print") as mock_print:
            menu_manager.display_menu(menu_items)
            # Проверяем, что print был вызван для каждого элемента
            assert mock_print.call_count >= len(menu_items)

    @patch("builtins.input", return_value="0")
    def test_get_user_choice_exit(self, mock_input, menu_manager):
        """Тест выбора выхода из меню"""
        menu_items = ["Item 1", "Exit"]
        choice = menu_manager.get_user_choice(menu_items)
        assert choice == "0"
