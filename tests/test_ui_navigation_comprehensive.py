
"""
Комплексные тесты для модуля ui_navigation с максимальным покрытием кода.
Включает тестирование навигации, пагинации и управления состоянием UI.

Все тесты используют консолидированные моки без внешних запросов.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import List, Dict, Any, Optional

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.ui_navigation import UINavigation, ui_navigation, quick_paginate


class ConsolidatedUINavigationMocks:
    """Консолидированная система моков для UI Navigation"""
    
    def __init__(self):
        """Инициализация всех моков"""
        self.input_mock = Mock()
        self.print_mock = Mock()
        self.formatter_mock = Mock()
        
        # Настройка поведения моков
        self.input_mock.return_value = "q"  # По умолчанию выход
        self.formatter_mock.return_value = "formatted_item"


# Глобальный экземпляр моков
nav_mocks = ConsolidatedUINavigationMocks()


class TestUINavigation:
    """Комплексное тестирование класса UINavigation"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.ui_nav = UINavigation(items_per_page=5)
        self.test_items = [f"item_{i}" for i in range(25)]
        
        def test_formatter(item, number=None):
            """Тестовый форматер элементов"""
            if number:
                return f"{number}. {item}"
            return str(item)
        
        self.formatter = test_formatter
    
    def test_ui_navigation_initialization(self):
        """Тестирование инициализации UINavigation"""
        nav = UINavigation()
        assert nav.items_per_page == 10  # Значение по умолчанию
        
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
        assert pagination_info["has_prev"] is False
        assert pagination_info["has_next"] is True
        assert pagination_info["start_idx"] == 1
        assert pagination_info["end_idx"] == 5
    
    def test_get_page_data_middle_page(self):
        """Тестирование получения данных средней страницы"""
        page_items, pagination_info = self.ui_nav.get_page_data(self.test_items, page=3)
        
        assert len(page_items) == 5
        assert page_items == ["item_10", "item_11", "item_12", "item_13", "item_14"]
        assert pagination_info["current_page"] == 3
        assert pagination_info["has_prev"] is True
        assert pagination_info["has_next"] is True
    
    def test_get_page_data_last_page(self):
        """Тестирование получения данных последней страницы"""
        page_items, pagination_info = self.ui_nav.get_page_data(self.test_items, page=5)
        
        assert len(page_items) == 5
        assert page_items == ["item_20", "item_21", "item_22", "item_23", "item_24"]
        assert pagination_info["current_page"] == 5
        assert pagination_info["has_prev"] is True
        assert pagination_info["has_next"] is False
    
    def test_get_page_data_empty_items(self):
        """Тестирование с пустым списком элементов"""
        page_items, pagination_info = self.ui_nav.get_page_data([], page=1)
        
        assert len(page_items) == 0
        assert pagination_info["total_items"] == 0
        assert pagination_info["total_pages"] == 0
        assert pagination_info["current_page"] == 1
        assert pagination_info["has_prev"] is False
        assert pagination_info["has_next"] is False
    
    def test_get_page_data_invalid_page_low(self):
        """Тестирование с некорректным номером страницы (слишком низким)"""
        page_items, pagination_info = self.ui_nav.get_page_data(self.test_items, page=0)
        
        # Должно быть исправлено на страницу 1
        assert pagination_info["current_page"] == 1
    
    def test_get_page_data_invalid_page_high(self):
        """Тестирование с некорректным номером страницы (слишком высоким)"""
        page_items, pagination_info = self.ui_nav.get_page_data(self.test_items, page=10)
        
        # Должно быть исправлено на последнюю страницу
        assert pagination_info["current_page"] == 5
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_single_page(self, mock_print, mock_input):
        """Тестирование отображения с одной страницей"""
        mock_input.return_value = ""  # Enter для продолжения
        
        short_items = ["item_1", "item_2", "item_3"]
        self.ui_nav.paginate_display(short_items, self.formatter, "Test Data")
        
        # Проверяем, что print был вызван для отображения данных
        assert mock_print.call_count > 0
        
        # Должен быть вызван input для продолжения
        mock_input.assert_called_once()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_navigation_next(self, mock_print, mock_input):
        """Тестирование навигации на следующую страницу"""
        mock_input.side_effect = ["n", "q"]  # Следующая страница, затем выход
        
        self.ui_nav.paginate_display(self.test_items, self.formatter, "Test Data")
        
        # Проверяем, что input был вызван дважды
        assert mock_input.call_count == 2
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_navigation_previous(self, mock_print, mock_input):
        """Тестирование навигации на предыдущую страницу"""
        mock_input.side_effect = ["n", "p", "q"]  # Вперед, назад, выход
        
        self.ui_nav.paginate_display(self.test_items, self.formatter, "Test Data")
        
        assert mock_input.call_count == 3
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_direct_page_navigation(self, mock_print, mock_input):
        """Тестирование прямого перехода к странице"""
        mock_input.side_effect = ["3", "q"]  # Переход на страницу 3, затем выход
        
        self.ui_nav.paginate_display(self.test_items, self.formatter, "Test Data")
        
        assert mock_input.call_count == 2
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_invalid_page_number(self, mock_print, mock_input):
        """Тестирование некорректного номера страницы"""
        mock_input.side_effect = ["100", "", "q"]  # Неверная страница, Enter, выход
        
        self.ui_nav.paginate_display(self.test_items, self.formatter, "Test Data")
        
        # Должно быть сообщение об ошибке
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Некорректный номер страницы" in call for call in print_calls)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_custom_actions(self, mock_print, mock_input):
        """Тестирование пользовательских действий"""
        custom_action_called = False
        
        def custom_action():
            nonlocal custom_action_called
            custom_action_called = True
            custom_action.called = True
        
        custom_action.called = False
        custom_actions = {"c": custom_action}
        
        mock_input.side_effect = ["c", "q"]  # Пользовательское действие, выход
        
        self.ui_nav.paginate_display(
            self.test_items, 
            self.formatter, 
            "Test Data", 
            custom_actions=custom_actions
        )
        
        assert custom_action.called is True
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_empty_items(self, mock_print, mock_input):
        """Тестирование с пустым списком элементов"""
        self.ui_nav.paginate_display([], self.formatter, "Empty Data")
        
        # Должно быть сообщение о том, что нет данных
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Нет данных для отображения" in call for call in print_calls)
    
    def test_handle_navigation_choice_quit(self):
        """Тестирование выбора выхода"""
        result = self.ui_nav._handle_navigation_choice("q", 1, 5)
        assert result == -1
        
        result = self.ui_nav._handle_navigation_choice("quit", 1, 5)
        assert result == -1
    
    def test_handle_navigation_choice_next(self):
        """Тестирование перехода вперед"""
        result = self.ui_nav._handle_navigation_choice("n", 2, 5)
        assert result == 3
        
        result = self.ui_nav._handle_navigation_choice("next", 2, 5)
        assert result == 3
        
        # На последней странице не должно быть перехода вперед
        result = self.ui_nav._handle_navigation_choice("n", 5, 5)
        assert result == -2  # Некорректный ввод
    
    def test_handle_navigation_choice_previous(self):
        """Тестирование перехода назад"""
        result = self.ui_nav._handle_navigation_choice("p", 3, 5)
        assert result == 2
        
        result = self.ui_nav._handle_navigation_choice("prev", 3, 5)
        assert result == 2
        
        # На первой странице не должно быть перехода назад
        result = self.ui_nav._handle_navigation_choice("p", 1, 5)
        assert result == -2  # Некорректный ввод
    
    def test_handle_navigation_choice_page_number(self):
        """Тестирование прямого указания номера страницы"""
        result = self.ui_nav._handle_navigation_choice("3", 1, 5)
        assert result == 3
        
        # Некорректный номер страницы
        result = self.ui_nav._handle_navigation_choice("10", 1, 5)
        assert result == 1  # Остается на текущей странице
    
    def test_display_navigation_menu(self):
        """Тестирование отображения навигационного меню"""
        with patch('builtins.print') as mock_print:
            # Меню для средней страницы
            self.ui_nav._display_navigation_menu(3, 5)
            
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("'p' или 'prev' - предыдущая страница" in call for call in print_calls)
            assert any("'n' или 'next' - следующая страница" in call for call in print_calls)
            assert any("'q' или 'quit' - выход" in call for call in print_calls)
    
    def test_display_navigation_menu_first_page(self):
        """Тестирование меню для первой страницы"""
        with patch('builtins.print') as mock_print:
            self.ui_nav._display_navigation_menu(1, 5)
            
            print_calls = [str(call) for call in mock_print.call_args_list]
            # Не должно быть опции "предыдущая страница"
            assert not any("'p' или 'prev'" in call for call in print_calls)
            assert any("'n' или 'next'" in call for call in print_calls)
    
    def test_display_navigation_menu_last_page(self):
        """Тестирование меню для последней страницы"""
        with patch('builtins.print') as mock_print:
            self.ui_nav._display_navigation_menu(5, 5)
            
            print_calls = [str(call) for call in mock_print.call_args_list]
            # Не должно быть опции "следующая страница"
            assert any("'p' или 'prev'" in call for call in print_calls)
            assert not any("'n' или 'next'" in call for call in print_calls)


class TestGlobalUINavigation:
    """Тестирование глобального экземпляра навигации"""
    
    def test_global_ui_navigation_exists(self):
        """Тестирование существования глобального экземпляра"""
        assert ui_navigation is not None
        assert isinstance(ui_navigation, UINavigation)
        assert ui_navigation.items_per_page == 10


class TestQuickPaginate:
    """Тестирование функции быстрой пагинации"""
    
    def test_formatter(self, item, number=None):
        """Тестовый форматер"""
        if number:
            return f"{number}. {item}"
        return str(item)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_quick_paginate_basic(self, mock_print, mock_input):
        """Базовое тестирование quick_paginate"""
        mock_input.return_value = "q"
        
        items = ["item1", "item2", "item3"]
        quick_paginate(items, self.test_formatter, "Quick Test", items_per_page=2)
        
        # Проверяем, что функции были вызваны
        assert mock_print.call_count > 0
        assert mock_input.call_count >= 1
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_quick_paginate_with_custom_actions(self, mock_print, mock_input):
        """Тестирование quick_paginate с пользовательскими действиями"""
        mock_input.side_effect = ["c", "q"]
        
        action_called = False
        def custom_action():
            nonlocal action_called
            action_called = True
        
        custom_actions = {"c": custom_action}
        items = ["item1", "item2", "item3"]
        
        quick_paginate(
            items, 
            self.test_formatter, 
            "Quick Test", 
            custom_actions=custom_actions
        )
        
        assert action_called is True


class TestUINavigationIntegration:
    """Интеграционные тесты для UI Navigation"""
    
    def create_test_data(self, count=50):
        """Создание тестовых данных"""
        return [{"id": i, "name": f"Item {i}", "value": i * 10} for i in range(count)]
    
    def complex_formatter(self, item, number=None):
        """Сложный форматер для тестирования"""
        prefix = f"{number}. " if number else ""
        return f"{prefix}ID: {item['id']}, Name: {item['name']}, Value: {item['value']}"
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_full_navigation_workflow(self, mock_print, mock_input):
        """Тестирование полного рабочего процесса навигации"""
        # Симулируем сложный сценарий навигации
        mock_input.side_effect = [
            "2",    # Переход на страницу 2
            "next", # Следующая страница (3)
            "prev", # Предыдущая страница (2)
            "5",    # Переход на страницу 5
            "1",    # Возврат к первой странице
            "q"     # Выход
        ]
        
        test_data = self.create_test_data(50)
        navigator = UINavigation(items_per_page=10)
        
        navigator.paginate_display(
            test_data, 
            self.complex_formatter, 
            "Complex Navigation Test",
            show_numbers=True
        )
        
        # Проверяем, что все команды навигации были обработаны
        assert mock_input.call_count == 6
    
    def test_pagination_math_correctness(self):
        """Тестирование корректности математики пагинации"""
        navigator = UINavigation(items_per_page=7)
        test_cases = [
            (50, 7, 8),  # 50 элементов по 7 на странице = 8 страниц
            (49, 7, 7),  # 49 элементов по 7 на странице = 7 страниц
            (7, 7, 1),   # 7 элементов по 7 на странице = 1 страница
            (0, 7, 0),   # 0 элементов = 0 страниц
            (1, 10, 1),  # 1 элемент по 10 на странице = 1 страница
        ]
        
        for total_items, items_per_page, expected_pages in test_cases:
            navigator.items_per_page = items_per_page
            test_data = [f"item_{i}" for i in range(total_items)]
            
            _, pagination_info = navigator.get_page_data(test_data, page=1)
            assert pagination_info["total_pages"] == expected_pages, \
                f"Failed for {total_items} items with {items_per_page} per page"
    
    def test_edge_cases_handling(self):
        """Тестирование обработки граничных случаев"""
        navigator = UINavigation()
        
        # Тест с None в качестве элементов
        try:
            _, info = navigator.get_page_data(None, page=1)
            # Должно обрабатываться корректно или вызывать исключение
        except (TypeError, AttributeError):
            pass  # Ожидаемое поведение
        
        # Тест с очень большим номером страницы
        test_data = ["item1", "item2", "item3"]
        _, info = navigator.get_page_data(test_data, page=9999)
        assert info["current_page"] == 1  # Должно быть исправлено
        
        # Тест с отрицательным номером страницы
        _, info = navigator.get_page_data(test_data, page=-5)
        assert info["current_page"] == 1  # Должно быть исправлено
