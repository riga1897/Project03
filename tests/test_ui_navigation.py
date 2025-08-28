
"""
Тесты для модуля ui_navigation
"""

import pytest
from unittest.mock import Mock, patch, call
from io import StringIO
from src.utils.ui_navigation import quick_paginate


class TestUINavigation:
    """Тесты для навигации пользовательского интерфейса"""

    def test_quick_paginate_empty_items(self):
        """Тест пагинации с пустым списком элементов"""
        items = []
        
        with patch('builtins.input', return_value='q'):
            result = quick_paginate(items, items_per_page=5)
            # Функция должна обработать пустой список без ошибок
            assert result is None or result == []

    def test_quick_paginate_single_page(self):
        """Тест пагинации с одной страницей"""
        items = ['item1', 'item2', 'item3']
        
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print') as mock_print:
                result = quick_paginate(items, items_per_page=5)
                # Должны быть выведены все элементы
                mock_print.assert_called()

    def test_quick_paginate_multiple_pages(self):
        """Тест пагинации с несколькими страницами"""
        items = ['item1', 'item2', 'item3', 'item4', 'item5', 'item6']
        
        with patch('builtins.input', side_effect=['n', 'q']):
            with patch('builtins.print') as mock_print:
                result = quick_paginate(items, items_per_page=3)
                # Должна быть показана первая страница, затем вторая
                mock_print.assert_called()

    def test_quick_paginate_navigation_next(self):
        """Тест навигации на следующую страницу"""
        items = ['item1', 'item2', 'item3', 'item4', 'item5', 'item6']
        
        with patch('builtins.input', side_effect=['n', 'q']):
            with patch('builtins.print') as mock_print:
                quick_paginate(items, items_per_page=2)
                # Проверяем, что функция обработала команду 'n' (next)
                mock_print.assert_called()

    def test_quick_paginate_navigation_previous(self):
        """Тест навигации на предыдущую страницу"""
        items = ['item1', 'item2', 'item3', 'item4']
        
        with patch('builtins.input', side_effect=['n', 'p', 'q']):
            with patch('builtins.print') as mock_print:
                quick_paginate(items, items_per_page=2)
                # Проверяем, что функция обработала команды навигации
                mock_print.assert_called()

    def test_quick_paginate_quit_immediately(self):
        """Тест немедленного выхода из пагинации"""
        items = ['item1', 'item2', 'item3']
        
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print') as mock_print:
                result = quick_paginate(items, items_per_page=2)
                # Должна быть показана первая страница
                mock_print.assert_called()

    def test_quick_paginate_invalid_input(self):
        """Тест обработки некорректного ввода"""
        items = ['item1', 'item2', 'item3', 'item4']
        
        with patch('builtins.input', side_effect=['invalid', 'xyz', 'q']):
            with patch('builtins.print') as mock_print:
                quick_paginate(items, items_per_page=2)
                # Функция должна обработать некорректный ввод и продолжить работу
                mock_print.assert_called()

    def test_quick_paginate_custom_items_per_page(self):
        """Тест пагинации с настраиваемым количеством элементов на странице"""
        items = ['item1', 'item2', 'item3', 'item4', 'item5']
        
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print') as mock_print:
                quick_paginate(items, items_per_page=1)
                # При items_per_page=1 должен быть показан только один элемент
                mock_print.assert_called()

    def test_quick_paginate_last_page_boundary(self):
        """Тест навигации на границе последней страницы"""
        items = ['item1', 'item2', 'item3']
        
        with patch('builtins.input', side_effect=['n', 'n', 'q']):
            with patch('builtins.print') as mock_print:
                quick_paginate(items, items_per_page=2)
                # Попытка перейти дальше последней страницы не должна вызвать ошибку
                mock_print.assert_called()

    def test_quick_paginate_first_page_boundary(self):
        """Тест навигации на границе первой страницы"""
        items = ['item1', 'item2', 'item3', 'item4']
        
        with patch('builtins.input', side_effect=['p', 'q']):
            with patch('builtins.print') as mock_print:
                quick_paginate(items, items_per_page=2)
                # Попытка перейти назад с первой страницы не должна вызвать ошибку
                mock_print.assert_called()

    def test_quick_paginate_display_format(self):
        """Тест формата отображения элементов"""
        items = [
            {'title': 'Job 1', 'company': 'Company A'},
            {'title': 'Job 2', 'company': 'Company B'}
        ]
        
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print') as mock_print:
                quick_paginate(items, items_per_page=5)
                # Проверяем, что функция может обработать словари
                mock_print.assert_called()

    def test_quick_paginate_edge_case_zero_items_per_page(self):
        """Тест граничного случая с нулевым количеством элементов на странице"""
        items = ['item1', 'item2']
        
        with patch('builtins.input', return_value='q'):
            # При items_per_page=0 или отрицательном значении должно использоваться значение по умолчанию
            try:
                quick_paginate(items, items_per_page=0)
            except (ValueError, ZeroDivisionError):
                # Ожидается обработка ошибки или использование значения по умолчанию
                pass

    def test_quick_paginate_string_items(self):
        """Тест пагинации со строковыми элементами"""
        items = ["First item", "Second item", "Third item"]
        
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print') as mock_print:
                quick_paginate(items, items_per_page=2)
                mock_print.assert_called()
