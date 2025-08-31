
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
        menu_items = [
            {"id": "1", "title": "Option 1", "description": "First option"},
            {"id": "2", "title": "Option 2", "description": "Second option"}
        ]
        
        manager = MenuManager(menu_items)
        assert manager.menu_items == menu_items

    @patch('builtins.print')
    def test_display_menu(self, mock_print):
        """Тест отображения меню"""
        menu_items = [
            {"id": "1", "title": "Option 1", "description": "First option"},
            {"id": "2", "title": "Option 2", "description": "Second option"}
        ]
        
        manager = MenuManager(menu_items)
        manager.display_menu()
        
        # Проверяем, что меню было выведено
        mock_print.assert_called()

    def test_get_menu_item_valid(self):
        """Тест получения валидного пункта меню"""
        menu_items = [
            {"id": "1", "title": "Option 1", "description": "First option"},
            {"id": "2", "title": "Option 2", "description": "Second option"}
        ]
        
        manager = MenuManager(menu_items)
        item = manager.get_menu_item("1")
        
        assert item == menu_items[0]

    def test_get_menu_item_invalid(self):
        """Тест получения невалидного пункта меню"""
        menu_items = [
            {"id": "1", "title": "Option 1", "description": "First option"}
        ]
        
        manager = MenuManager(menu_items)
        item = manager.get_menu_item("999")
        
        assert item is None

    def test_create_main_menu(self):
        """Тест создания главного меню"""
        menu = create_main_menu()
        
        assert isinstance(menu, MenuManager)
        assert len(menu.menu_items) > 0

    def test_menu_validation(self):
        """Тест валидации пунктов меню"""
        manager = MenuManager([])
        
        # Проверяем валидацию пустого меню
        assert len(manager.menu_items) == 0

    @patch('builtins.input', return_value='1')
    def test_get_user_choice(self, mock_input):
        """Тест получения выбора пользователя"""
        menu_items = [
            {"id": "1", "title": "Option 1", "description": "First option"}
        ]
        
        manager = MenuManager(menu_items)
        
        with patch('builtins.print'):
            choice = manager.get_user_choice()
        
        assert choice == "1"
        mock_input.assert_called()

    def test_add_menu_item(self):
        """Тест добавления пункта меню"""
        manager = MenuManager([])
        
        new_item = {"id": "1", "title": "New Option", "description": "New option"}
        manager.add_menu_item(new_item)
        
        assert len(manager.menu_items) == 1
        assert manager.menu_items[0] == new_item

    def test_remove_menu_item(self):
        """Тест удаления пункта меню"""
        menu_items = [
            {"id": "1", "title": "Option 1", "description": "First option"},
            {"id": "2", "title": "Option 2", "description": "Second option"}
        ]
        
        manager = MenuManager(menu_items)
        success = manager.remove_menu_item("1")
        
        assert success is True
        assert len(manager.menu_items) == 1
        assert manager.menu_items[0]["id"] == "2"

    def test_remove_nonexistent_menu_item(self):
        """Тест удаления несуществующего пункта меню"""
        menu_items = [
            {"id": "1", "title": "Option 1", "description": "First option"}
        ]
        
        manager = MenuManager(menu_items)
        success = manager.remove_menu_item("999")
        
        assert success is False
        assert len(manager.menu_items) == 1
