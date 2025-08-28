
"""
Тесты для модуля ui_navigation
"""

import pytest
from unittest.mock import patch, Mock
from src.utils.ui_navigation import quick_paginate, navigate_pages, confirm_navigation


class TestUINavigation:
    """Тесты для функций навигации UI"""

    @pytest.fixture
    def sample_items(self):
        """Фикстура с тестовыми элементами"""
        return [f"Item {i}" for i in range(1, 26)]  # 25 элементов

    def test_quick_paginate_basic(self, sample_items):
        """Тест базовой пагинации"""
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print') as mock_print:
                quick_paginate(sample_items, items_per_page=10)
                # Проверяем, что элементы были выведены
                mock_print.assert_called()

    @patch('builtins.input', side_effect=['n', 'q'])
    @patch('builtins.print')
    def test_quick_paginate_next_page(self, mock_print, mock_input, sample_items):
        """Тест перехода к следующей странице"""
        quick_paginate(sample_items, items_per_page=10)
        # Проверяем, что функция выполнилась без ошибок
        assert mock_print.called

    @patch('builtins.input', side_effect=['n', 'p', 'q'])
    @patch('builtins.print')
    def test_quick_paginate_previous_page(self, mock_print, mock_input, sample_items):
        """Тест перехода к предыдущей странице"""
        quick_paginate(sample_items, items_per_page=10)
        assert mock_print.called

    def test_quick_paginate_empty_items(self):
        """Тест пагинации с пустым списком"""
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print') as mock_print:
                quick_paginate([], items_per_page=10)
                mock_print.assert_called()

    def test_quick_paginate_single_page(self):
        """Тест пагинации с элементами на одну страницу"""
        items = ["Item 1", "Item 2", "Item 3"]
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print') as mock_print:
                quick_paginate(items, items_per_page=10)
                mock_print.assert_called()

    @patch('builtins.input', return_value='2')
    @patch('builtins.print')
    def test_navigate_pages_go_to_page(self, mock_print, mock_input, sample_items):
        """Тест перехода к конкретной странице"""
        result = navigate_pages(sample_items, current_page=1, items_per_page=10)
        assert result == 2

    @patch('builtins.input', return_value='next')
    @patch('builtins.print')
    def test_navigate_pages_next_command(self, mock_print, mock_input, sample_items):
        """Тест команды 'next'"""
        result = navigate_pages(sample_items, current_page=1, items_per_page=10)
        assert result == 2

    @patch('builtins.input', return_value='prev')
    @patch('builtins.print')
    def test_navigate_pages_previous_command(self, mock_print, mock_input, sample_items):
        """Тест команды 'prev'"""
        result = navigate_pages(sample_items, current_page=2, items_per_page=10)
        assert result == 1

    @patch('builtins.input', return_value='exit')
    @patch('builtins.print')
    def test_navigate_pages_exit_command(self, mock_print, mock_input, sample_items):
        """Тест команды 'exit'"""
        result = navigate_pages(sample_items, current_page=1, items_per_page=10)
        assert result == -1

    @patch('builtins.input', return_value='y')
    def test_confirm_navigation_yes(self, mock_input):
        """Тест подтверждения навигации - да"""
        result = confirm_navigation("Continue to next page?")
        assert result is True

    @patch('builtins.input', return_value='n')
    def test_confirm_navigation_no(self, mock_input):
        """Тест подтверждения навигации - нет"""
        result = confirm_navigation("Continue to next page?")
        assert result is False

    @patch('builtins.input', side_effect=['maybe', 'y'])
    @patch('builtins.print')
    def test_confirm_navigation_invalid_then_valid(self, mock_print, mock_input):
        """Тест некорректного, затем корректного ответа"""
        result = confirm_navigation("Continue?")
        assert result is True
        mock_print.assert_called()  # Должно быть сообщение об ошибке

    def test_quick_paginate_custom_formatter(self, sample_items):
        """Тест пагинации с пользовательским форматтером"""
        def custom_formatter(item, index):
            return f"[{index}] {item.upper()}"

        with patch('builtins.input', return_value='q'):
            with patch('builtins.print') as mock_print:
                quick_paginate(sample_items[:5], items_per_page=10, formatter=custom_formatter)
                mock_print.assert_called()
