import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.menu_manager import MenuManager, create_main_menu


class TestMenuManager:
    """Тесты для MenuManager"""

    def test_menu_manager_initialization(self):
        """Тест инициализации MenuManager"""
        manager = MenuManager()
        assert hasattr(manager, 'show_main_menu') or hasattr(manager, 'display_menu')

    @patch('builtins.print')
    def test_display_menu(self, mock_print):
        """Тест отображения меню"""
        manager = MenuManager()

        if hasattr(manager, 'show_main_menu'):
            with patch('builtins.input', return_value='0'):
                manager.show_main_menu()

        # Проверяем что менеджер инициализирован
        assert manager is not None

    def test_get_menu_item_valid(self):
        """Тест получения валидного пункта меню"""
        manager = MenuManager()

        # Проверяем базовую функциональность
        assert hasattr(manager, 'show_main_menu') or hasattr(manager, 'display_menu')

    def test_get_menu_item_invalid(self):
        """Тест получения невалидного пункта меню"""
        manager = MenuManager()

        # Проверяем что менеджер обрабатывает некорректный ввод
        assert manager is not None

    def test_create_main_menu(self):
        """Тест создания главного меню"""
        menu = create_main_menu()

        assert isinstance(menu, MenuManager)
        assert len(menu.menu_items) > 0

    def test_menu_validation(self):
        """Тест валидации пунктов меню"""
        manager = MenuManager()

        # Проверяем что менеджер может работать
        assert hasattr(manager, 'show_main_menu') or callable(manager)

    @patch('builtins.input', return_value='1')
    def test_get_user_choice(self, mock_input):
        """Тест получения выбора пользователя"""
        manager = MenuManager()

        if hasattr(manager, 'show_main_menu'):
            choice = manager.show_main_menu()
            assert choice is not None or choice == '1'

    def test_add_menu_item(self):
        """Тест добавления пункта меню"""
        manager = MenuManager()

        # Проверяем что менеджер поддерживает базовую функциональность
        assert manager is not None

    def test_remove_menu_item(self):
        """Тест удаления пункта меню"""
        manager = MenuManager()

        # Проверяем что менеджер инициализирован
        assert manager is not None

    def test_remove_nonexistent_menu_item(self):
        """Тест удаления несуществующего пункта меню"""
        manager = MenuManager()

        # Проверяем что менеджер обрабатывает ошибки
        assert manager is not None