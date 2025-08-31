
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.paginator import quick_paginate, Paginator


class TestPaginator:
    """Тесты для Paginator"""

    def test_paginator_initialization(self):
        """Тест инициализации Paginator"""
        items = ["item1", "item2", "item3"]
        paginator = Paginator(items, items_per_page=2)
        
        assert paginator.items == items
        assert paginator.items_per_page == 2
        assert paginator.total_items == 3
        assert paginator.total_pages == 2

    def test_paginator_get_page(self):
        """Тест получения страницы"""
        items = ["item1", "item2", "item3", "item4", "item5"]
        paginator = Paginator(items, items_per_page=2)
        
        page1 = paginator.get_page(1)
        assert page1 == ["item1", "item2"]
        
        page2 = paginator.get_page(2)
        assert page2 == ["item3", "item4"]
        
        page3 = paginator.get_page(3)
        assert page3 == ["item5"]

    def test_paginator_invalid_page(self):
        """Тест получения невалидной страницы"""
        items = ["item1", "item2"]
        paginator = Paginator(items, items_per_page=2)
        
        # Страница 0 или отрицательная
        assert paginator.get_page(0) == []
        assert paginator.get_page(-1) == []
        
        # Страница больше общего количества
        assert paginator.get_page(10) == []

    def test_paginator_empty_items(self):
        """Тест пагинатора с пустым списком"""
        paginator = Paginator([], items_per_page=5)
        
        assert paginator.total_items == 0
        assert paginator.total_pages == 0
        assert paginator.get_page(1) == []

    @patch('builtins.input', side_effect=['q'])
    @patch('builtins.print')
    def test_quick_paginate_quit(self, mock_print, mock_input):
        """Тест быстрой пагинации с выходом"""
        items = ["item1", "item2", "item3"]
        
        def simple_formatter(item, number=None):
            return f"{number}. {item}" if number else str(item)
        
        quick_paginate(items, formatter=simple_formatter)
        
        # Проверяем, что функция завершилась без ошибок
        mock_input.assert_called()

    @patch('builtins.input', side_effect=['n', 'q'])
    @patch('builtins.print')
    def test_quick_paginate_navigation(self, mock_print, mock_input):
        """Тест навигации в быстрой пагинации"""
        items = list(range(1, 21))  # 20 элементов
        
        def simple_formatter(item, number=None):
            return f"{number}. {item}" if number else str(item)
        
        quick_paginate(items, formatter=simple_formatter, items_per_page=5)
        
        # Проверяем, что навигация работает
        assert mock_input.call_count >= 2
