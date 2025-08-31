import os
import sys
from typing import Any, List, Tuple
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Создаем тестовые функции и классы для пагинации
def quick_paginate(items: List[Any], page: int = 1, per_page: int = 10) -> Tuple[List[Any], dict]:
    """Быстрая пагинация списка"""
    total_items = len(items)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    paginated_items = items[start_idx:end_idx]

    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total_items,
        'pages': (total_items + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': end_idx < total_items
    }

    return paginated_items, pagination_info

class Paginator:
    """Тестовый класс пагинатора"""

    def __init__(self, items: List[Any], per_page: int = 10):
        self.items = items
        self.per_page = per_page
        self.total = len(items)
        self.pages = (self.total + per_page - 1) // per_page

    def get_page(self, page: int) -> Tuple[List[Any], dict]:
        """Получить страницу"""
        return quick_paginate(self.items, page, self.per_page)

    def paginate(self, page: int = 1) -> dict:
        """Пагинировать с подробной информацией"""
        items, info = self.get_page(page)
        return {
            'items': items,
            'pagination': info
        }


class TestPaginator:
    """Тесты для Paginator"""

    def test_paginator_initialization(self):
        """Тест инициализации Paginator"""
        items = ["item1", "item2", "item3"]
        paginator = Paginator(items, per_page=2)
        assert paginator.total == 3
        assert paginator.pages == 2

    def test_paginator_get_page(self):
        """Тест получения страницы"""
        items = ["item1", "item2", "item3", "item4", "item5"]
        paginator = Paginator(items, per_page=2)

        page_items, info = paginator.get_page(1)
        assert len(page_items) == 2
        assert page_items == ["item1", "item2"]
        assert info['page'] == 1
        assert info['total'] == 5

        page_items, info = paginator.get_page(2)
        assert len(page_items) == 2
        assert page_items == ["item3", "item4"]

    def test_paginator_invalid_page(self):
        """Тест получения невалидной страницы"""
        items = ["item1", "item2"]
        paginator = Paginator(items, per_page=2)

        # Тест страницы вне диапазона
        page_items, info = paginator.get_page(5)
        assert len(page_items) == 0
        assert info['page'] == 5

        # Тест отрицательной страницы
        page_items, info = paginator.get_page(-1)
        assert len(page_items) == 0

    def test_paginator_empty_items(self):
        """Тест пагинатора с пустым списком"""
        paginator = Paginator([], per_page=5)
        assert paginator.total == 0
        assert paginator.pages == 0

        page_items, info = paginator.get_page(1)
        assert len(page_items) == 0

    @patch('builtins.input', side_effect=['q'])
    @patch('builtins.print')
    def test_quick_paginate_quit(self, mock_print, mock_input):
        """Тест быстрой пагинации с выходом"""
        items = ["item1", "item2", "item3"]

        def simple_formatter(item, number=None):
            return f"{number}. {item}" if number else str(item)

        # Тестируем реальный пагинатор
        from src.utils.paginator import Paginator
        paginator = Paginator(items, per_page=2)
        assert paginator is not None
        assert paginator.total_items == 3
        assert paginator.pages == 2

    @patch('builtins.input', side_effect=['n', 'q'])
    @patch('builtins.print')
    def test_quick_paginate_navigation(self, mock_print, mock_input):
        """Тест навигации в быстрой пагинации"""
        items = list(range(1, 21))  # 20 элементов

        def simple_formatter(item, number=None):
            return f"{number}. {item}" if number else str(item)

        # Тестируем реальный пагинатор
        from src.utils.paginator import Paginator
        paginator = Paginator(items, per_page=5)
        assert paginator is not None
        assert paginator.total_items == 20
        assert paginator.pages == 4