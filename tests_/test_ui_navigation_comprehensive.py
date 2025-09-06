"""
Комплексные тесты для модуля ui_navigation с максимальным покрытием кода.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.ui_navigation import UINavigation, ui_navigation, quick_paginate


class TestUINavigation:
    """Комплексное тестирование класса UINavigation"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.ui_nav = UINavigation(items_per_page=5)
        self.test_items = [f"item_{i}" for i in range(25)]

    def _test_formatter(self, item, number=None):
        """Тестовый форматер элементов"""
        if number:
            return f"{number}. {item}"
        return str(item)

    def test_ui_navigation_initialization(self):
        """Тестирование инициализации UINavigation"""
        nav = UINavigation()
        assert nav.items_per_page == 10

        nav_custom = UINavigation(items_per_page=20)
        assert nav_custom.items_per_page == 20

    def test_get_page_data_first_page(self):
        """Тестирование получения данных первой страницы"""
        page_items, pagination_info = self.ui_nav.get_page_data(self.test_items, page=1)

        assert len(page_items) == 5
        assert page_items == ["item_0", "item_1", "item_2", "item_3", "item_4"]
        assert pagination_info["current_page"] == 1
        assert pagination_info["total_pages"] == 5
        assert pagination_info["total_items"] == 25

    @patch('builtins.input', return_value="q")
    @patch('builtins.print')
    def test_paginate_display_single_page(self, mock_print, mock_input):
        """Тестирование отображения с одной страницей"""
        short_items = ["item_1", "item_2", "item_3"]
        self.ui_nav.paginate_display(short_items, self._test_formatter, "Test Data")

        assert mock_print.call_count > 0

    def test_handle_navigation_choice_quit(self):
        """Тестирование выбора выхода"""
        result = self.ui_nav._handle_navigation_choice("q", 1, 5)
        assert result == -1


class TestQuickPaginate:
    """Тестирование функции быстрой пагинации"""

    def _test_formatter(self, item, number=None):
        """Простой форматтер для тестов"""
        if number is not None:
            return f"{number}: Formatted: {item}"
        return f"Formatted: {item}"

    @patch('builtins.input', return_value="q")
    @patch('builtins.print')
    def test_quick_paginate_basic(self, mock_print, mock_input):
        """Базовое тестирование quick_paginate"""
        items = ["item1", "item2", "item3"]
        quick_paginate(items, self._test_formatter, "Quick Test", items_per_page=2)

        assert mock_print.call_count > 0
        assert mock_input.call_count >= 1

    @patch('builtins.input', side_effect=["q"])
    @patch('builtins.print')
    def test_quick_paginate_with_custom_actions(self, mock_print, mock_input):
        """Тестирование quick_paginate с пользовательскими действиями"""
        action_called = False

        def custom_action():
            nonlocal action_called
            action_called = True

        custom_actions = {"c": custom_action}
        items = ["item1", "item2", "item3"]

        quick_paginate(
            items, 
            self._test_formatter, 
            "Quick Test", 
            custom_actions=custom_actions
        )

        # Проверяем, что функция выполнилась без ошибок
        assert mock_print.called