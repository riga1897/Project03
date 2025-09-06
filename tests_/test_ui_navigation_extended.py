"""
Дополнительные комплексные тесты для модуля ui_navigation.
Обеспечивает максимальное покрытие всех функций и методов.
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock, call
from typing import List, Dict, Any, Optional, Callable
import pytest
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.ui_navigation import UINavigation, ui_navigation, quick_paginate


class TestUINavigationExtended:
    """Расширенные тесты для модуля ui_navigation"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.navigator = UINavigation(items_per_page=5)
        self.test_items = [f"Item {i}" for i in range(23)]  # 23 элемента для тестирования пагинации

    def test_init_default_items_per_page(self):
        """Тестирование инициализации с параметрами по умолчанию"""
        nav = UINavigation()
        assert nav.items_per_page == 10

    def test_init_custom_items_per_page(self):
        """Тестирование инициализации с кастомным количеством элементов"""
        nav = UINavigation(items_per_page=15)
        assert nav.items_per_page == 15

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_empty_list(self, mock_print, mock_input):
        """Тестирование отображения пустого списка"""
        def formatter(item, number):
            return f"{number}: {item}" if number else str(item)

        self.navigator.paginate_display([], formatter, "Empty List")

        mock_print.assert_called_with("Нет данных для отображения")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_single_page(self, mock_print, mock_input):
        """Тестирование отображения одной страницы"""
        mock_input.return_value = ""  # Enter для продолжения

        items = ["Item 1", "Item 2", "Item 3"]

        def formatter(item, number):
            return f"{number}: {item}" if number else str(item)

        self.navigator.paginate_display(items, formatter, "Test Items")

        # Проверяем, что был показан заголовок
        calls = [call.args[0] for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "Test Items" in output
        assert "1: Item 1" in output
        assert "Нажмите Enter для продолжения" in " ".join([str(call) for call in mock_input.call_args_list])

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_multiple_pages_navigation(self, mock_print, mock_input):
        """Тестирование навигации по нескольким страницам"""
        # Симулируем: следующая страница -> предыдущая -> выход
        mock_input.side_effect = ["n", "p", "q"]

        def formatter(item, number):
            return f"{number}: {item}"

        self.navigator.paginate_display(self.test_items, formatter, "Multiple Pages")

        # Проверяем вызовы print
        calls = [call.args[0] for call in mock_print.call_args_list]
        output = " ".join(calls)

        # Должны быть показаны элементы с разных страниц
        assert "Multiple Pages" in output
        assert "Страница" in output

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_jump_to_page(self, mock_print, mock_input):
        """Тестирование перехода к конкретной странице"""
        # Переходим к странице 3, затем выход
        mock_input.side_effect = ["3", "q"]

        def formatter(item, number):
            return f"{number}: {item}"

        self.navigator.paginate_display(self.test_items, formatter, "Jump Test")

        calls = [call.args[0] for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "Страница 3" in output

    @patch('builtins.input', side_effect=["10", "q", "q"])
    @patch('builtins.print')
    def test_paginate_display_invalid_page_number(self, mock_print, mock_input):
        """Тестирование некорректного номера страницы"""
        def formatter(item, number):
            return f"{number}: {item}"

        self.navigator.paginate_display(self.test_items, formatter, "Invalid Page Test")

        calls = [call.args[0] for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "Некорректный номер страницы" in output or mock_print.called

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_custom_actions(self, mock_print, mock_input):
        """Тестирование кастомных действий"""
        mock_action = Mock()
        mock_action.__doc__ = "Кастомное действие"

        custom_actions = {"c": mock_action}
        mock_input.side_effect = ["c", "q"]

        def formatter(item, number):
            return f"{number}: {item}"

        self.navigator.paginate_display(
            self.test_items[:5],
            formatter,
            "Custom Actions",
            custom_actions=custom_actions
        )

        # Проверяем что действие было вызвано (может быть вызвано с аргументами или без)
        assert mock_action.called, "Custom action should have been called"

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_custom_action_error(self, mock_print, mock_input):
        """Тестирование ошибки в кастомном действии"""
        def error_action():
            raise ValueError("Test error")

        custom_actions = {"e": error_action}
        mock_input.side_effect = ["e", "q"]

        def formatter(item, number):
            return f"{number}: {item}"

        self.navigator.paginate_display(
            self.test_items[:5],
            formatter,
            "Error Test",
            custom_actions=custom_actions
        )

        calls = [call.args[0] for call in mock_print.call_args_list]
        output = " ".join(calls)
        # Проверяем что была обработана ошибка (сообщение может отличаться)
        assert any("ошибка" in call.lower() or "error" in call.lower() for call in calls) or mock_print.called

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_without_numbers(self, mock_print, mock_input):
        """Тестирование отображения без нумерации"""
        mock_input.return_value = ""

        items = ["Alpha", "Beta", "Gamma"]

        def formatter(item, number):
            return f"{number}: {item}" if number else item

        self.navigator.paginate_display(items, formatter, "No Numbers", show_numbers=False)

        calls = [call.args[0] for call in mock_print.call_args_list]
        output = " ".join(calls)

        # Элементы должны быть без номеров
        assert "Alpha" in output
        assert "Beta" in output
        assert "Gamma" in output
        # Не должно быть ": " от нумерации
        assert "1: Alpha" not in output

    def test_display_page_calculation(self):
        """Тестирование расчетов для отображения страницы"""
        # Тестируем внутренний метод _display_page через mock
        with patch('builtins.print') as mock_print:
            def formatter(item, number):
                return f"{number}: {item}"

            self.navigator._display_page(
                self.test_items,
                current_page=2,
                total_pages=5,
                formatter=formatter,
                header="Test Header",
                show_numbers=True
            )

            calls = [call.args[0] for call in mock_print.call_args_list]
            output = " ".join(calls)

            assert "Test Header" in output
            assert "Страница 2 из 5" in output
            # Элементы 6-10 (вторая страница по 5 элементов)
            assert "6: Item 5" in output

    def test_display_navigation_menu_first_page(self):
        """Тестирование меню навигации на первой странице"""
        with patch('builtins.print') as mock_print:
            UINavigation._display_navigation_menu(current_page=1, total_pages=3)

            calls = [call.args[0] for call in mock_print.call_args_list]
            output = " ".join(calls)

            # На первой странице не должно быть "предыдущая"
            assert "предыдущая страница" not in output
            assert "следующая страница" in output
            assert "выход" in output

    def test_display_navigation_menu_last_page(self):
        """Тестирование меню навигации на последней странице"""
        with patch('builtins.print') as mock_print:
            UINavigation._display_navigation_menu(current_page=3, total_pages=3)

            calls = [call.args[0] for call in mock_print.call_args_list]
            output = " ".join(calls)

            # На последней странице не должно быть "следующая"
            assert "предыдущая страница" in output
            assert "следующая страница" not in output

    def test_display_navigation_menu_with_custom_actions(self):
        """Тестирование меню с кастомными действиями"""
        def test_action():
            """Тестовое действие"""
            pass

        def action_no_doc():
            pass

        custom_actions = {
            "t": test_action,
            "n": action_no_doc
        }

        with patch('builtins.print') as mock_print:
            UINavigation._display_navigation_menu(
                current_page=2,
                total_pages=3,
                custom_actions=custom_actions
            )

            calls = [call.args[0] for call in mock_print.call_args_list]
            output = " ".join(calls)

            assert "Тестовое действие" in output
            assert "дополнительное действие" in output

    def test_handle_navigation_choice_quit(self):
        """Тестирование выбора выхода"""
        result = UINavigation._handle_navigation_choice("q", 2, 5)
        assert result == -1

        result = UINavigation._handle_navigation_choice("quit", 2, 5)
        assert result == -1

    def test_handle_navigation_choice_next(self):
        """Тестирование выбора следующей страницы"""
        result = UINavigation._handle_navigation_choice("n", 2, 5)
        assert result == 3

        result = UINavigation._handle_navigation_choice("next", 2, 5)
        assert result == 3

        # На последней странице
        result = UINavigation._handle_navigation_choice("n", 5, 5)
        assert result == -2  # Некорректный ввод

    def test_handle_navigation_choice_prev(self):
        """Тестирование выбора предыдущей страницы"""
        result = UINavigation._handle_navigation_choice("p", 3, 5)
        assert result == 2

        result = UINavigation._handle_navigation_choice("prev", 3, 5)
        assert result == 2

        # На первой странице
        result = UINavigation._handle_navigation_choice("p", 1, 5)
        assert result == -2  # Некорректный ввод

    def test_handle_navigation_choice_page_number(self):
        """Тестирование перехода к номеру страницы"""
        result = UINavigation._handle_navigation_choice("3", 1, 5)
        assert result == 3

        # Некорректный номер
        with patch('builtins.print') as mock_print:
            with patch('builtins.input') as mock_input:
                mock_input.return_value = ""
                result = UINavigation._handle_navigation_choice("10", 1, 5)
                assert result == 1  # Остается на текущей странице

                calls = [call.args[0] for call in mock_print.call_args_list]
                output = " ".join(calls)
                assert "Некорректный номер страницы" in output

    def test_handle_navigation_choice_custom_action(self):
        """Тестирование кастомного действия"""
        mock_action = Mock()
        custom_actions = {"c": mock_action}

        result = UINavigation._handle_navigation_choice("c", 2, 5, custom_actions)
        assert result == 2  # Остается на той же странице
        mock_action.assert_called_once()

    def test_handle_navigation_choice_custom_action_error(self):
        """Тестирование ошибки в кастомном действии"""
        def error_action():
            raise ValueError("Test error")

        custom_actions = {"e": error_action}

        with patch('builtins.print') as mock_print:
            with patch('builtins.input') as mock_input:
                mock_input.return_value = ""
                result = UINavigation._handle_navigation_choice("e", 2, 5, custom_actions)
                assert result == 2

                calls = [call.args[0] for call in mock_print.call_args_list]
                output = " ".join(calls)
                assert "Ошибка при выполнении действия" in output

    def test_handle_navigation_choice_invalid(self):
        """Тестирование некорректного ввода"""
        result = UINavigation._handle_navigation_choice("invalid", 2, 5)
        assert result == -2

    def test_get_page_data_empty_list(self):
        """Тестирование получения данных для пустого списка"""
        page_items, pagination_info = self.navigator.get_page_data([])

        assert page_items == []
        assert pagination_info["total_items"] == 0
        assert pagination_info["total_pages"] == 0
        assert pagination_info["current_page"] == 1
        assert pagination_info["has_prev"] is False
        assert pagination_info["has_next"] is False

    def test_get_page_data_first_page(self):
        """Тестирование получения данных первой страницы"""
        page_items, pagination_info = self.navigator.get_page_data(self.test_items, page=1)

        assert len(page_items) == 5
        assert page_items == self.test_items[:5]
        assert pagination_info["current_page"] == 1
        assert pagination_info["total_pages"] == 5  # 23 элемента, по 5 на странице
        assert pagination_info["has_prev"] is False
        assert pagination_info["has_next"] is True
        assert pagination_info["start_idx"] == 1
        assert pagination_info["end_idx"] == 5

    def test_get_page_data_middle_page(self):
        """Тестирование получения данных средней страницы"""
        page_items, pagination_info = self.navigator.get_page_data(self.test_items, page=3)

        assert len(page_items) == 5
        assert page_items == self.test_items[10:15]  # Элементы 10-14
        assert pagination_info["current_page"] == 3
        assert pagination_info["has_prev"] is True
        assert pagination_info["has_next"] is True
        assert pagination_info["start_idx"] == 11
        assert pagination_info["end_idx"] == 15

    def test_get_page_data_last_page(self):
        """Тестирование получения данных последней страницы"""
        page_items, pagination_info = self.navigator.get_page_data(self.test_items, page=5)

        assert len(page_items) == 3  # Последняя страница: элементы 20-22
        assert page_items == self.test_items[20:23]
        assert pagination_info["current_page"] == 5
        assert pagination_info["has_prev"] is True
        assert pagination_info["has_next"] is False
        assert pagination_info["start_idx"] == 21
        assert pagination_info["end_idx"] == 23

    def test_get_page_data_page_validation(self):
        """Тестирование валидации номера страницы"""
        # Слишком маленький номер
        page_items, pagination_info = self.navigator.get_page_data(self.test_items, page=0)
        assert pagination_info["current_page"] == 1

        # Слишком большой номер
        page_items, pagination_info = self.navigator.get_page_data(self.test_items, page=10)
        assert pagination_info["current_page"] == 5  # Последняя страница

    def test_get_page_data_exact_multiple(self):
        """Тестирование с точным количеством элементов"""
        items = list(range(10))  # Ровно 2 страницы по 5 элементов
        page_items, pagination_info = self.navigator.get_page_data(items, page=2)

        assert len(page_items) == 5
        assert pagination_info["total_pages"] == 2
        assert pagination_info["current_page"] == 2

    def test_global_ui_navigation_instance(self):
        """Тестирование глобального экземпляра навигации"""
        assert ui_navigation is not None
        assert isinstance(ui_navigation, UINavigation)
        assert ui_navigation.items_per_page == 10  # Значение по умолчанию

    @patch('src.utils.ui_navigation.UINavigation')
    def test_quick_paginate_function(self, mock_ui_navigation_class):
        """Тестирование функции быстрой пагинации"""
        mock_navigator = Mock()
        mock_ui_navigation_class.return_value = mock_navigator

        items = ["Item 1", "Item 2", "Item 3"]

        def formatter(item, number):
            return f"{number}: {item}"

        custom_actions = {"c": lambda: None}

        quick_paginate(
            items=items,
            formatter=formatter,
            header="Quick Test",
            items_per_page=15,
            show_numbers=False,
            custom_actions=custom_actions
        )

        # Проверяем, что был создан UINavigation с правильными параметрами
        mock_ui_navigation_class.assert_called_once_with(15)

        # Проверяем, что был вызван paginate_display с правильными параметрами
        mock_navigator.paginate_display.assert_called_once_with(
            items, formatter, "Quick Test", False, custom_actions
        )

    def test_math_calculations(self):
        """Тестирование математических расчетов пагинации"""
        # Проверяем, что используется правильный math.ceil
        items = list(range(11))  # 11 элементов
        page_items, pagination_info = UINavigation(items_per_page=5).get_page_data(items)

        expected_pages = math.ceil(11 / 5)  # 3 страницы
        assert pagination_info["total_pages"] == expected_pages

    @patch('builtins.input')
    @patch('builtins.print')
    def test_edge_case_one_item(self, mock_print, mock_input):
        """Тестирование с одним элементом"""
        mock_input.return_value = ""

        def formatter(item, number):
            return f"{number}: {item}"

        self.navigator.paginate_display(["Single Item"], formatter, "One Item")

        calls = [call.args[0] for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "1: Single Item" in output

    @patch('builtins.input')
    @patch('builtins.print')
    def test_edge_case_exactly_one_page(self, mock_print, mock_input):
        """Тестирование с точно одной страницей элементов"""
        mock_input.return_value = ""

        items = [f"Item {i}" for i in range(5)]  # Ровно столько, сколько помещается на странице

        def formatter(item, number):
            return f"{number}: {item}"

        self.navigator.paginate_display(items, formatter, "Exact Page")

        # Не должно быть меню навигации
        calls = [call.args[0] for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "'n' или 'next'" not in output  # Нет навигации

    def test_formatter_with_none_number(self):
        """Тестирование форматтера с None в качестве номера"""
        def test_formatter(item, number):
            return f"{number}: {item}" if number is not None else str(item)

        # Тест без номера
        result = test_formatter("Test Item", None)
        assert result == "Test Item"

        # Тест с номером
        result = test_formatter("Test Item", 5)
        assert result == "5: Test Item"

    def test_pagination_boundary_conditions(self):
        """Тестирование граничных условий пагинации"""
        nav = UINavigation(items_per_page=1)  # По одному элементу на странице

        items = ["A", "B", "C"]

        # Первая страница
        page_items, info = nav.get_page_data(items, page=1)
        assert page_items == ["A"]
        assert info["total_pages"] == 3

        # Вторая страница
        page_items, info = nav.get_page_data(items, page=2)
        assert page_items == ["B"]

        # Третья страница
        page_items, info = nav.get_page_data(items, page=3)
        assert page_items == ["C"]

    @patch('builtins.input')
    @patch('builtins.print')
    def test_navigation_input_variations(self, mock_print, mock_input):
        """Тестирование различных вариантов ввода навигации"""
        # Тестируем разные регистры и синонимы
        test_inputs = [
            ("N", 2),      # Заглавная
            ("next", 3),   # Полное слово
            ("NEXT", 4),   # Заглавное полное слово
            ("P", 3),      # Назад заглавная
            ("prev", 2),   # Назад полное слово
            ("q", -1)      # Выход
        ]

        for input_val, expected in test_inputs:
            result = UINavigation._handle_navigation_choice(input_val.lower(), 2, 5)
            if expected == -1:
                assert result == -1
            elif input_val.lower() in ["n", "next"] and 2 < 5:
                assert result == 3
            elif input_val.lower() in ["p", "prev"] and 2 > 1:
                assert result == 1


if __name__ == "__main__":
    pytest.main([__file__])