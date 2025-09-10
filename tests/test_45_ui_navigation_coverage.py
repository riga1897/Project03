#!/usr/bin/env python3
"""
Тесты модуля ui_navigation.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Мокирование всех input(), print() и logger операций

Модуль содержит:
- Класс UINavigation для пагинации и навигации
- Методы отображения страниц и меню
- Обработка пользовательского ввода
- Функцию quick_paginate для быстрого использования
"""

import math
from typing import Any
from unittest.mock import patch

from src.utils.ui_navigation import (
    UINavigation,
    ui_navigation,
    quick_paginate
)


def simple_formatter(item: Any, number: Any=None) -> str:
    """Простой форматтер для тестов"""
    if number:
        return f"{number}. {item}"
    return str(item)


def custom_action_success() -> str:
    """Успешное пользовательское действие"""
    return "success"


def custom_action_with_exception() -> None:
    """Пользовательское действие с исключением"""
    raise ValueError("Test error")


class TestUINavigationInit:
    """100% покрытие инициализации UINavigation"""

    def test_init_default_items_per_page(self) -> None:
        """Покрытие: инициализация с параметрами по умолчанию"""
        nav = UINavigation()

        assert nav.items_per_page == 10

    def test_init_custom_items_per_page(self) -> None:
        """Покрытие: инициализация с кастомным количеством элементов"""
        nav = UINavigation(items_per_page=5)

        assert nav.items_per_page == 5

    def test_global_instance_exists(self) -> None:
        """Покрытие: глобальный экземпляр создан"""

        assert isinstance(ui_navigation, UINavigation)
        assert ui_navigation.items_per_page == 10


class TestPaginateDisplay:
    """100% покрытие метода paginate_display"""

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_empty_items(self, mock_print: Any, mock_input: Any) -> None:
        """Покрытие: пагинация пустого списка"""
        nav = UINavigation()

        nav.paginate_display([], simple_formatter)

        mock_print.assert_called_once_with("Нет данных для отображения")
        mock_input.assert_not_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_single_page(self, mock_print: Any, mock_input: Any) -> None:
        """Покрытие: пагинация с одной страницей"""
        nav = UINavigation(items_per_page=10)
        items = ["item1", "item2", "item3"]
        mock_input.return_value = ""  # Enter для продолжения

        nav.paginate_display(items, simple_formatter, header="Test Items")

        # Проверяем, что отобразилось содержимое и затем ждало Enter
        mock_input.assert_called_once_with("\nНажмите Enter для продолжения...")

        # Проверяем содержимое вывода
        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        assert "Test Items" in combined_output
        assert "1. item1" in combined_output
        assert "Страница 1 из 1" in combined_output

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_multiple_pages_quit(self, mock_print: Any, mock_input: Any) -> None:
        """Покрытие: пагинация с несколькими страницами, выход по q"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4", "item5"]
        mock_input.return_value = "q"  # Выход

        nav.paginate_display(items, simple_formatter)

        # Проверяем, что показалось меню и обработался выход
        mock_input.assert_called_once_with("\nВыберите действие: ")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_navigation_next(self, mock_print: Any, mock_input: Any) -> None:
        """Покрытие: навигация на следующую страницу"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4"]
        mock_input.side_effect = ["n", "q"]  # Следующая страница, затем выход

        nav.paginate_display(items, simple_formatter)

        assert mock_input.call_count == 2

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_invalid_input(self, mock_print: Any, mock_input: Any) -> None:
        """Покрытие: некорректный ввод пользователя"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3"]
        mock_input.side_effect = ["invalid", "", "q"]  # Некорректный ввод, Enter, затем выход

        nav.paginate_display(items, simple_formatter)

        # Должно быть сообщение об ошибке
        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert "Некорректный ввод" in " ".join(print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_custom_actions(self, mock_print: Any, mock_input: Any) -> None:
        """Покрытие: пользовательские действия"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3"]

        custom_actions = {"s": custom_action_success}
        mock_input.side_effect = ["s", "q"]  # Пользовательское действие, затем выход

        nav.paginate_display(items, simple_formatter, custom_actions=custom_actions)

        # Проверяем, что действие выполнилось (остались на той же странице)
        assert mock_input.call_count == 2

    @patch('builtins.input')
    @patch('builtins.print')
    def test_paginate_display_show_numbers_false(self, mock_print: Any, mock_input: Any) -> None:
        """Покрытие: отображение без нумерации"""
        nav = UINavigation(items_per_page=10)
        items = ["item1", "item2"]
        mock_input.return_value = ""  # Enter

        nav.paginate_display(items, simple_formatter, show_numbers=False)

        # Должны быть элементы без номеров
        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        assert "1. item1" not in combined_output  # Нет нумерации
        assert "item1" in combined_output  # Но сами элементы есть


class TestDisplayPage:
    """100% покрытие метода _display_page"""

    @patch('builtins.print')
    def test_display_page_first_page(self, mock_print: Any) -> None:
        """Покрытие: отображение первой страницы"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4"]

        nav._display_page(items, 1, 2, simple_formatter, "Test Header", True)

        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)

        assert "Test Header" in combined_output
        assert "1. item1" in combined_output
        assert "2. item2" in combined_output
        assert "Страница 1 из 2" in combined_output
        assert "Показано элементов: 1-2 из 4" in combined_output

    @patch('builtins.print')
    def test_display_page_last_page(self, mock_print: Any) -> None:
        """Покрытие: отображение последней страницы"""
        nav = UINavigation(items_per_page=3)
        items = ["item1", "item2", "item3", "item4", "item5"]

        nav._display_page(items, 2, 2, simple_formatter, "Last Page", True)

        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)

        assert "4. item4" in combined_output
        assert "5. item5" in combined_output
        assert "Страница 2 из 2" in combined_output
        assert "Показано элементов: 4-5 из 5" in combined_output

    @patch('builtins.print')
    def test_display_page_without_numbers(self, mock_print: Any) -> None:
        """Покрытие: отображение без нумерации"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2"]

        nav._display_page(items, 1, 1, simple_formatter, "No Numbers", False)

        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)

        # Элементы без номеров (форматер получает None)
        assert "item1" in combined_output
        assert "item2" in combined_output


class TestDisplayNavigationMenu:
    """100% покрытие статического метода _display_navigation_menu"""

    @patch('builtins.print')
    def test_display_navigation_menu_first_page(self, mock_print: Any) -> None:
        """Покрытие: меню на первой странице"""
        UINavigation._display_navigation_menu(1, 3)

        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)

        assert "предыдущая страница" not in combined_output  # Нет кнопки "назад"
        assert "'n' или 'next' - следующая страница" in combined_output
        assert "'q' или 'quit' - выход" in combined_output
        assert "Номер страницы - переход к странице" in combined_output

    @patch('builtins.print')
    def test_display_navigation_menu_middle_page(self, mock_print: Any) -> None:
        """Покрытие: меню на средней странице"""
        UINavigation._display_navigation_menu(2, 3)

        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)

        assert "'p' или 'prev' - предыдущая страница" in combined_output
        assert "'n' или 'next' - следующая страница" in combined_output

    @patch('builtins.print')
    def test_display_navigation_menu_last_page(self, mock_print: Any) -> None:
        """Покрытие: меню на последней странице"""
        UINavigation._display_navigation_menu(3, 3)

        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)

        assert "'p' или 'prev' - предыдущая страница" in combined_output
        assert "следующая страница" not in combined_output  # Нет кнопки "вперед"

    @patch('builtins.print')
    def test_display_navigation_menu_single_page(self, mock_print: Any) -> None:
        """Покрытие: меню для одной страницы"""
        UINavigation._display_navigation_menu(1, 1)

        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)

        assert "предыдущая страница" not in combined_output
        assert "следующая страница" not in combined_output
        assert "'q' или 'quit' - выход" in combined_output

    @patch('builtins.print')
    def test_display_navigation_menu_with_custom_actions(self, mock_print: Any) -> None:
        """Покрытие: меню с пользовательскими действиями"""
        def documented_action() -> None:
            """Документированное действие"""
            pass

        def undocumented_action() -> None:
            pass

        custom_actions = {
            "d": documented_action,
            "u": undocumented_action
        }

        UINavigation._display_navigation_menu(1, 2, custom_actions)

        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)

        assert "'d' - Документированное действие" in combined_output
        assert "'u' - дополнительное действие" in combined_output


class TestHandleNavigationChoice:
    """100% покрытие статического метода _handle_navigation_choice"""

    def test_handle_navigation_choice_quit_q(self) -> None:
        """Покрытие: выход по 'q'"""
        result = UINavigation._handle_navigation_choice("q", 1, 3)
        assert result == -1

    def test_handle_navigation_choice_quit_full(self) -> None:
        """Покрытие: выход по 'quit'"""
        result = UINavigation._handle_navigation_choice("quit", 2, 3)
        assert result == -1

    def test_handle_navigation_choice_next_n(self) -> None:
        """Покрытие: следующая страница по 'n'"""
        result = UINavigation._handle_navigation_choice("n", 1, 3)
        assert result == 2

    def test_handle_navigation_choice_next_full(self) -> None:
        """Покрытие: следующая страница по 'next'"""
        result = UINavigation._handle_navigation_choice("next", 2, 3)
        assert result == 3

    def test_handle_navigation_choice_next_on_last_page(self) -> None:
        """Покрытие: попытка следующей страницы на последней странице"""
        result = UINavigation._handle_navigation_choice("n", 3, 3)
        assert result == -2  # Некорректный ввод

    def test_handle_navigation_choice_prev_p(self) -> None:
        """Покрытие: предыдущая страница по 'p'"""
        result = UINavigation._handle_navigation_choice("p", 2, 3)
        assert result == 1

    def test_handle_navigation_choice_prev_full(self) -> None:
        """Покрытие: предыдущая страница по 'prev'"""
        result = UINavigation._handle_navigation_choice("prev", 3, 3)
        assert result == 2

    def test_handle_navigation_choice_prev_on_first_page(self) -> None:
        """Покрытие: попытка предыдущей страницы на первой странице"""
        result = UINavigation._handle_navigation_choice("p", 1, 3)
        assert result == -2  # Некорректный ввод

    def test_handle_navigation_choice_valid_page_number(self) -> None:
        """Покрытие: переход к валидной странице по номеру"""
        result = UINavigation._handle_navigation_choice("2", 1, 3)
        assert result == 2

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_navigation_choice_invalid_page_number(self, mock_print: Any, mock_input: Any):
        """Покрытие: некорректный номер страницы"""
        mock_input.return_value = ""  # Enter для продолжения

        result = UINavigation._handle_navigation_choice("5", 1, 3)

        assert result == 1  # Остались на текущей странице
        mock_print.assert_called_with("Некорректный номер страницы. Доступно: 1-3")
        mock_input.assert_called_once_with("Нажмите Enter для продолжения...")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_navigation_choice_zero_page(self, mock_print: Any, mock_input: Any):
        """Покрытие: номер страницы 0"""
        mock_input.return_value = ""

        result = UINavigation._handle_navigation_choice("0", 2, 3)

        assert result == 2  # Остались на текущей
        mock_print.assert_called_with("Некорректный номер страницы. Доступно: 1-3")

    def test_handle_navigation_choice_custom_action_success(self) -> None:
        """Покрытие: успешное выполнение пользовательского действия"""
        custom_actions = {"s": custom_action_success}

        result = UINavigation._handle_navigation_choice("s", 2, 3, custom_actions)

        assert result == 2  # Остались на той же странице

    @patch('src.utils.ui_navigation.logger')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_navigation_choice_custom_action_exception(self, mock_print: Any, mock_input: Any, mock_logger: Any):
        """Покрытие: исключение в пользовательском действии"""
        custom_actions = {"e": custom_action_with_exception}
        mock_input.return_value = ""

        result = UINavigation._handle_navigation_choice("e", 2, 3, custom_actions)

        assert result == 2  # Остались на той же странице
        mock_logger.error.assert_called_once()
        mock_print.assert_called_with("Ошибка при выполнении действия: Test error")
        mock_input.assert_called_once_with("Нажмите Enter для продолжения...")

    def test_handle_navigation_choice_unknown_custom_action(self) -> None:
        """Покрытие: неизвестное пользовательское действие"""
        custom_actions = {"s": custom_action_success}

        result = UINavigation._handle_navigation_choice("unknown", 2, 3, custom_actions)

        assert result == -2  # Некорректный ввод

    def test_handle_navigation_choice_invalid_input(self) -> None:
        """Покрытие: полностью некорректный ввод"""
        result = UINavigation._handle_navigation_choice("invalid", 2, 3)
        assert result == -2

    def test_handle_navigation_choice_non_digit(self) -> None:
        """Покрытие: нецифровой ввод"""
        result = UINavigation._handle_navigation_choice("abc", 1, 3)
        assert result == -2


class TestGetPageData:
    """100% покрытие метода get_page_data"""

    def test_get_page_data_empty_items(self) -> None:
        """Покрытие: получение данных для пустого списка"""
        nav = UINavigation(items_per_page=10)

        page_items, pagination_info = nav.get_page_data([])

        assert page_items == []
        assert pagination_info == {
            "total_items": 0,
            "total_pages": 0,
            "current_page": 1,
            "items_per_page": 10,
            "has_prev": False,
            "has_next": False,
        }

    def test_get_page_data_first_page(self) -> None:
        """Покрытие: получение данных первой страницы"""
        nav = UINavigation(items_per_page=3)
        items = ["item1", "item2", "item3", "item4", "item5"]

        page_items, pagination_info = nav.get_page_data(items, page=1)

        assert page_items == ["item1", "item2", "item3"]
        assert pagination_info["total_items"] == 5
        assert pagination_info["total_pages"] == 2
        assert pagination_info["current_page"] == 1
        assert pagination_info["has_prev"] == False
        assert pagination_info["has_next"] == True
        assert pagination_info["start_idx"] == 1
        assert pagination_info["end_idx"] == 3

    def test_get_page_data_last_page(self) -> None:
        """Покрытие: получение данных последней страницы"""
        nav = UINavigation(items_per_page=3)
        items = ["item1", "item2", "item3", "item4", "item5"]

        page_items, pagination_info = nav.get_page_data(items, page=2)

        assert page_items == ["item4", "item5"]
        assert pagination_info["current_page"] == 2
        assert pagination_info["has_prev"] == True
        assert pagination_info["has_next"] == False
        assert pagination_info["start_idx"] == 4
        assert pagination_info["end_idx"] == 5

    def test_get_page_data_page_too_low(self) -> None:
        """Покрытие: номер страницы меньше 1"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3"]

        page_items, pagination_info = nav.get_page_data(items, page=-1)

        # Должно скорректироваться на страницу 1
        assert pagination_info["current_page"] == 1
        assert page_items == ["item1", "item2"]

    def test_get_page_data_page_too_high(self) -> None:
        """Покрытие: номер страницы больше максимального"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3"]  # 2 страницы

        page_items, pagination_info = nav.get_page_data(items, page=5)

        # Должно скорректироваться на последнюю страницу (2)
        assert pagination_info["current_page"] == 2
        assert page_items == ["item3"]

    def test_get_page_data_single_page(self) -> None:
        """Покрытие: данные помещаются на одну страницу"""
        nav = UINavigation(items_per_page=10)
        items = ["item1", "item2", "item3"]

        page_items, pagination_info = nav.get_page_data(items, page=1)

        assert page_items == items
        assert pagination_info["total_pages"] == 1
        assert pagination_info["has_prev"] == False
        assert pagination_info["has_next"] == False

    def test_get_page_data_exact_fit(self) -> None:
        """Покрытие: данные точно заполняют страницы"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4"]  # Ровно 2 страницы

        # Первая страница
        page_items1, info1 = nav.get_page_data(items, page=1)
        assert page_items1 == ["item1", "item2"]
        assert info1["total_pages"] == 2

        # Вторая страница
        page_items2, info2 = nav.get_page_data(items, page=2)
        assert page_items2 == ["item3", "item4"]
        assert info2["total_pages"] == 2


class TestQuickPaginateFunction:
    """100% покрытие функции quick_paginate"""

    @patch('builtins.input')
    @patch('builtins.print')
    def test_quick_paginate_default_params(self, mock_print: Any, mock_input: Any):
        """Покрытие: quick_paginate с параметрами по умолчанию"""
        items = ["item1", "item2"]
        mock_input.return_value = ""  # Enter для одной страницы

        quick_paginate(items, simple_formatter)

        # Проверяем, что создался новый UINavigation и вызвался paginate_display
        mock_input.assert_called_once_with("\nНажмите Enter для продолжения...")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_quick_paginate_custom_params(self, mock_print: Any, mock_input: Any):
        """Покрытие: quick_paginate с кастомными параметрами"""
        items = ["item1", "item2", "item3"]
        custom_actions = {"t": custom_action_success}
        mock_input.return_value = ""

        quick_paginate(
            items,
            simple_formatter,
            header="Custom Header",
            items_per_page=5,
            show_numbers=False,
            custom_actions=custom_actions
        )

        # Проверяем содержимое вывода
        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        assert "Custom Header" in combined_output

    @patch('builtins.input')
    @patch('builtins.print')
    def test_quick_paginate_multiple_pages(self, mock_print: Any, mock_input: Any):
        """Покрытие: quick_paginate с несколькими страницами"""
        items = ["item1", "item2", "item3", "item4", "item5"]
        mock_input.return_value = "q"  # Выход

        quick_paginate(items, simple_formatter, items_per_page=2)

        # Должно быть меню навигации
        mock_input.assert_called_once_with("\nВыберите действие: ")


class TestIntegrationScenarios:
    """Интеграционные тесты для сложных сценариев"""

    @patch('builtins.input')
    @patch('builtins.print')
    def test_full_navigation_flow(self, mock_print: Any, mock_input: Any):
        """Покрытие: полный цикл навигации"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4", "item5", "item6"]

        # Симуляция: next -> page 3 -> prev -> quit
        mock_input.side_effect = ["n", "3", "p", "q"]

        nav.paginate_display(items, simple_formatter, header="Full Flow Test")

        assert mock_input.call_count == 4

    @patch('builtins.input')
    @patch('builtins.print')
    def test_error_recovery_flow(self, mock_print: Any, mock_input: Any):
        """Покрытие: восстановление после ошибок"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3"]

        # Симуляция: invalid -> invalid page number -> quit
        mock_input.side_effect = ["invalid", "", "10", "", "q"]

        nav.paginate_display(items, simple_formatter)

        # Должны быть сообщения об ошибках
        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        assert "Некорректный ввод" in combined_output
        assert "Некорректный номер страницы" in combined_output

    def test_math_edge_cases(self) -> None:
        """Покрытие: математические граничные случаи"""
        nav = UINavigation(items_per_page=3)

        # Тест math.ceil для пагинации
        items_7 = ["i"] * 7  # 7/3 = 2.33 -> ceil = 3 страницы
        _, info = nav.get_page_data(items_7, 1)
        assert info["total_pages"] == math.ceil(7/3) == 3

        # Тест точного деления
        items_6 = ["i"] * 6  # 6/3 = 2.0 -> ceil = 2 страницы
        _, info2 = nav.get_page_data(items_6, 1)
        assert info2["total_pages"] == 2

    @patch('builtins.input')
    @patch('builtins.print')
    def test_custom_formatter_integration(self, mock_print: Any, mock_input: Any):
        """Покрытие: интеграция с кастомным форматтером"""
        def complex_formatter(item: Any, number: Any=None):
            if number:
                return f"[{number:03d}] >>> {item.upper()} <<<"
            return f">>> {item.upper()} <<<"

        nav = UINavigation(items_per_page=2)
        items = ["test", "item"]
        mock_input.return_value = ""

        nav.paginate_display(items, complex_formatter, show_numbers=True)

        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        assert "[001] >>> TEST <<<" in combined_output
        assert "[002] >>> ITEM <<<" in combined_output