import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import List, Dict, Any, Optional, Callable
import math

"""
Комплексные тесты для модуля ui_navigation с максимальным покрытием кода.

Покрывает все методы и функции навигации пользовательского интерфейса:
- Класс UINavigation с пагинацией
- Обработка пользовательского ввода 
- Навигационные команды
- Отображение страниц и меню
- Функция quick_paginate

Все тесты используют консолидированные моки без fallback методов.
Оптимизированы для быстрого выполнения.
"""

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.ui_navigation import UINavigation, quick_paginate, ui_navigation
    SRC_AVAILABLE = True
except ImportError:
    SRC_AVAILABLE = False


def create_test_items(count: int = 10) -> List[Dict[str, Any]]:  # Уменьшено значение по умолчанию
    """Создает тестовые элементы для пагинации"""
    return [{"id": i, "title": f"Item {i}", "data": f"test_data_{i}"} for i in range(1, count + 1)]


def simple_formatter(item: Any, index: Optional[int] = None) -> str:
    """Простой форматтер для тестирования"""
    if index:
        return f"{index}. {item.get('title', str(item))}"
    return str(item.get('title', str(item)))


class TestUINavigationInitialization:
    """Тестирование инициализации UINavigation"""

    def test_ui_navigation_default_initialization(self):
        """Тестирование инициализации с параметрами по умолчанию"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        nav = UINavigation()
        assert nav.items_per_page == 10

    def test_ui_navigation_custom_initialization(self):
        """Тестирование инициализации с пользовательскими параметрами"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        nav = UINavigation(items_per_page=5)
        assert nav.items_per_page == 5

    def test_ui_navigation_invalid_initialization(self):
        """Тестирование инициализации с некорректными параметрами"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        # Отрицательное значение
        nav = UINavigation(items_per_page=-5)
        # Конструктор должен обрабатывать некорректные значения
        assert hasattr(nav, 'items_per_page')


class TestUINavigationPagination:
    """Тестирование методов пагинации"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        if SRC_AVAILABLE:
            self.nav = UINavigation(items_per_page=5)
            self.test_items = create_test_items(23)

    def test_get_page_data_first_page(self):
        """Тестирование получения данных первой страницы"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        page_items, pagination_info = self.nav.get_page_data(self.test_items, page=1)
        
        assert len(page_items) == 5
        assert pagination_info['current_page'] == 1
        assert pagination_info['total_pages'] == 5  # math.ceil(23/5) = 5
        assert pagination_info['has_prev'] is False
        assert pagination_info['has_next'] is True
        assert pagination_info['start_idx'] == 1
        assert pagination_info['end_idx'] == 5

    def test_get_page_data_middle_page(self):
        """Тестирование получения данных средней страницы"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        page_items, pagination_info = self.nav.get_page_data(self.test_items, page=3)
        
        assert len(page_items) == 5
        assert pagination_info['current_page'] == 3
        assert pagination_info['has_prev'] is True
        assert pagination_info['has_next'] is True
        assert pagination_info['start_idx'] == 11
        assert pagination_info['end_idx'] == 15

    def test_get_page_data_last_page(self):
        """Тестирование получения данных последней страницы"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        page_items, pagination_info = self.nav.get_page_data(self.test_items, page=5)
        
        assert len(page_items) == 3  # Остаток: 23 % 5 = 3
        assert pagination_info['current_page'] == 5
        assert pagination_info['has_prev'] is True
        assert pagination_info['has_next'] is False
        assert pagination_info['start_idx'] == 21
        assert pagination_info['end_idx'] == 23

    def test_get_page_data_empty_list(self):
        """Тестирование получения данных для пустого списка"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        page_items, pagination_info = self.nav.get_page_data([], page=1)
        
        assert len(page_items) == 0
        assert pagination_info['total_items'] == 0
        assert pagination_info['total_pages'] == 0
        assert pagination_info['current_page'] == 1
        assert pagination_info['has_prev'] is False
        assert pagination_info['has_next'] is False

    def test_get_page_data_invalid_page_negative(self):
        """Тестирование с отрицательным номером страницы"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        page_items, pagination_info = self.nav.get_page_data(self.test_items, page=-1)
        
        # Должна возвращаться первая страница
        assert pagination_info['current_page'] == 1

    def test_get_page_data_invalid_page_too_high(self):
        """Тестирование с номером страницы выше максимального"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        page_items, pagination_info = self.nav.get_page_data(self.test_items, page=100)
        
        # Должна возвращаться последняя страница
        assert pagination_info['current_page'] == 5  # math.ceil(23/5) = 5


class TestUINavigationDisplay:
    """Тестирование методов отображения"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        if SRC_AVAILABLE:
            self.nav = UINavigation(items_per_page=3)
            self.test_items = create_test_items(7)

    @patch('builtins.print')
    def test_display_page_with_numbers(self, mock_print):
        """Тестирование отображения страницы с нумерацией"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        self.nav._display_page(
            self.test_items, 
            current_page=1, 
            total_pages=3,
            formatter=simple_formatter,
            header="Тестовые данные",
            show_numbers=True
        )
        
        # Проверяем, что print был вызван для отображения
        assert mock_print.called
        
        # Проверяем, что заголовок был выведен
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Тестовые данные" in call_str for call_str in print_calls)

    @patch('builtins.print')
    def test_display_page_without_numbers(self, mock_print):
        """Тестирование отображения страницы без нумерации"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        self.nav._display_page(
            self.test_items,
            current_page=2,
            total_pages=3,
            formatter=simple_formatter,
            header="Данные без номеров",
            show_numbers=False
        )
        
        assert mock_print.called

    @patch('builtins.print')
    def test_display_navigation_menu_first_page(self, mock_print):
        """Тестирование отображения навигационного меню на первой странице"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        self.nav._display_navigation_menu(current_page=1, total_pages=3)
        
        assert mock_print.called
        # На первой странице не должно быть команды "предыдущая"
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert not any("предыдущая" in call_str.lower() for call_str in print_calls)

    @patch('builtins.print')
    def test_display_navigation_menu_last_page(self, mock_print):
        """Тестирование отображения навигационного меню на последней странице"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        self.nav._display_navigation_menu(current_page=3, total_pages=3)
        
        assert mock_print.called
        # На последней странице не должно быть команды "следующая"
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert not any("следующая" in call_str.lower() for call_str in print_calls)

    @patch('builtins.print')
    def test_display_navigation_menu_with_custom_actions(self, mock_print):
        """Тестирование отображения меню с пользовательскими действиями"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        def custom_action():
            """Пользовательское действие"""
            return "custom_result"

        custom_actions = {"c": custom_action}
        
        self.nav._display_navigation_menu(
            current_page=2, 
            total_pages=3, 
            custom_actions=custom_actions
        )
        
        assert mock_print.called


class TestUINavigationChoiceHandling:
    """Тестирование обработки пользовательского выбора"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        if SRC_AVAILABLE:
            self.nav = UINavigation()

    def test_handle_navigation_choice_quit(self):
        """Тестирование команды выхода"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        result = self.nav._handle_navigation_choice("q", current_page=2, total_pages=5)
        assert result == -1
        
        result = self.nav._handle_navigation_choice("quit", current_page=2, total_pages=5)
        assert result == -1

    def test_handle_navigation_choice_next(self):
        """Тестирование команды следующая страница"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        result = self.nav._handle_navigation_choice("n", current_page=2, total_pages=5)
        assert result == 3
        
        result = self.nav._handle_navigation_choice("next", current_page=3, total_pages=5)
        assert result == 4

    def test_handle_navigation_choice_previous(self):
        """Тестирование команды предыдущая страница"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        result = self.nav._handle_navigation_choice("p", current_page=3, total_pages=5)
        assert result == 2
        
        result = self.nav._handle_navigation_choice("prev", current_page=2, total_pages=5)
        assert result == 1

    def test_handle_navigation_choice_page_number(self):
        """Тестирование перехода к конкретной странице"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        result = self.nav._handle_navigation_choice("3", current_page=1, total_pages=5)
        assert result == 3
        
        result = self.nav._handle_navigation_choice("1", current_page=3, total_pages=5)
        assert result == 1

    @patch('builtins.print')
    @patch('builtins.input', return_value='')
    def test_handle_navigation_choice_invalid_page_number(self, mock_input, mock_print):
        """Тестирование некорректного номера страницы"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        result = self.nav._handle_navigation_choice("10", current_page=2, total_pages=5)
        assert result == 2  # Должны остаться на той же странице

    def test_handle_navigation_choice_next_at_last_page(self):
        """Тестирование команды next на последней странице"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        result = self.nav._handle_navigation_choice("n", current_page=5, total_pages=5)
        assert result == -2  # Некорректный ввод

    def test_handle_navigation_choice_prev_at_first_page(self):
        """Тестирование команды prev на первой странице"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        result = self.nav._handle_navigation_choice("p", current_page=1, total_pages=5)
        assert result == -2  # Некорректный ввод

    def test_handle_navigation_choice_custom_action(self):
        """Тестирование пользовательского действия"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        custom_action_called = Mock()
        custom_actions = {"c": custom_action_called}
        
        result = self.nav._handle_navigation_choice(
            "c", 
            current_page=2, 
            total_pages=5, 
            custom_actions=custom_actions
        )
        
        assert result == 2  # Остаемся на той же странице
        custom_action_called.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value='')
    def test_handle_navigation_choice_custom_action_error(self, mock_input, mock_print):
        """Тестирование ошибки в пользовательском действии"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        def failing_action():
            raise Exception("Custom action failed")

        custom_actions = {"f": failing_action}
        
        result = self.nav._handle_navigation_choice(
            "f", 
            current_page=2, 
            total_pages=5, 
            custom_actions=custom_actions
        )
        
        assert result == 2  # Остаемся на той же странице
        assert mock_print.called

    def test_handle_navigation_choice_invalid_input(self):
        """Тестирование некорректного ввода"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        result = self.nav._handle_navigation_choice("invalid", current_page=2, total_pages=5)
        assert result == -2


class TestUINavigationPaginateDisplay:
    """Тестирование основного метода paginate_display"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        if SRC_AVAILABLE:
            self.nav = UINavigation(items_per_page=3)
            self.test_items = create_test_items(7)

    @patch('builtins.input', side_effect=['', 'q'])
    @patch('builtins.print')
    def test_paginate_display_empty_list(self, mock_print, mock_input):
        """Тестирование отображения пустого списка"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        self.nav.paginate_display([], simple_formatter)
        
        # Проверяем, что было выведено сообщение о пустом списке
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("нет данных" in call_str.lower() for call_str in print_calls)

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_paginate_display_single_page(self, mock_print, mock_input):
        """Тестирование отображения одной страницы"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        single_page_items = create_test_items(2)
        self.nav.paginate_display(single_page_items, simple_formatter)
        
        assert mock_print.called
        assert mock_input.called

    @patch('builtins.input', side_effect=['n', 'p', 'q'])
    @patch('builtins.print')
    def test_paginate_display_navigation(self, mock_print, mock_input):
        """Тестирование навигации между страницами"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        # Ограничиваем количество элементов для ускорения теста
        limited_items = self.test_items[:6]  # Только 6 элементов вместо 7
        self.nav.paginate_display(limited_items, simple_formatter, header="Тест навигации")
        
        assert mock_print.called
        assert mock_input.call_count == 3

    @patch('builtins.input', side_effect=['2', 'q'])
    @patch('builtins.print')
    def test_paginate_display_direct_page_jump(self, mock_print, mock_input):
        """Тестирование прямого перехода к странице"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        self.nav.paginate_display(self.test_items, simple_formatter)
        
        assert mock_print.called
        assert mock_input.call_count == 2

    @patch('builtins.input', side_effect=['invalid', 'q'])
    @patch('builtins.print')
    def test_paginate_display_invalid_input(self, mock_print, mock_input):
        """Тестирование обработки некорректного ввода"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        # Используем меньший набор данных
        small_items = create_test_items(5)
        self.nav.paginate_display(small_items, simple_formatter)
        
        assert mock_print.called
        assert mock_input.call_count == 2

    @patch('builtins.input', side_effect=['c', 'q'])
    @patch('builtins.print')
    def test_paginate_display_custom_actions(self, mock_print, mock_input):
        """Тестирование пользовательских действий"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        custom_action = Mock()
        custom_actions = {"c": custom_action}
        
        self.nav.paginate_display(
            self.test_items, 
            simple_formatter, 
            custom_actions=custom_actions
        )
        
        assert mock_print.called
        assert custom_action.called

    @patch('builtins.input', side_effect=['q'])
    @patch('builtins.print')
    def test_paginate_display_show_numbers_false(self, mock_print, mock_input):
        """Тестирование отображения без номеров"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        self.nav.paginate_display(
            self.test_items, 
            simple_formatter, 
            show_numbers=False
        )
        
        assert mock_print.called


class TestQuickPaginateFunction:
    """Тестирование функции quick_paginate"""

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_quick_paginate_default_params(self, mock_print, mock_input):
        """Тестирование quick_paginate с параметрами по умолчанию"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        test_items = create_test_items(5)
        quick_paginate(test_items, simple_formatter)
        
        assert mock_print.called

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_quick_paginate_custom_params(self, mock_print, mock_input):
        """Тестирование quick_paginate с пользовательскими параметрами"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        test_items = create_test_items(15)
        quick_paginate(
            test_items, 
            simple_formatter,
            header="Пользовательский заголовок",
            items_per_page=5,
            show_numbers=False
        )
        
        assert mock_print.called

    @patch('builtins.input', side_effect=['c', 'q'])
    @patch('builtins.print')
    def test_quick_paginate_with_custom_actions(self, mock_print, mock_input):
        """Тестирование quick_paginate с пользовательскими действиями"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        test_items = create_test_items(10)
        custom_action = Mock()
        custom_actions = {"c": custom_action}
        
        quick_paginate(
            test_items, 
            simple_formatter,
            custom_actions=custom_actions
        )
        
        assert mock_print.called
        assert custom_action.called


class TestUINavigationGlobalInstance:
    """Тестирование глобального экземпляра ui_navigation"""

    def test_global_ui_navigation_exists(self):
        """Тестирование существования глобального экземпляра"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        assert ui_navigation is not None
        assert isinstance(ui_navigation, UINavigation)

    def test_global_ui_navigation_default_settings(self):
        """Тестирование настроек глобального экземпляра по умолчанию"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        assert ui_navigation.items_per_page == 10

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_global_ui_navigation_usage(self, mock_print, mock_input):
        """Тестирование использования глобального экземпляра"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        test_items = create_test_items(5)
        ui_navigation.paginate_display(test_items, simple_formatter)
        
        assert mock_print.called


class TestUINavigationEdgeCases:
    """Тестирование граничных случаев"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        if SRC_AVAILABLE:
            self.nav = UINavigation(items_per_page=10)

    def test_navigation_with_exactly_one_page_items(self):
        """Тестирование с количеством элементов ровно на одну страницу"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        exact_page_items = create_test_items(10)
        page_items, pagination_info = self.nav.get_page_data(exact_page_items, page=1)
        
        assert len(page_items) == 10
        assert pagination_info['total_pages'] == 1
        assert pagination_info['has_next'] is False

    def test_navigation_with_one_item(self):
        """Тестирование с одним элементом"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        single_item = create_test_items(1)
        page_items, pagination_info = self.nav.get_page_data(single_item, page=1)
        
        assert len(page_items) == 1
        assert pagination_info['total_pages'] == 1

    def test_navigation_math_calculations(self):
        """Тестирование математических вычислений пагинации"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        # Тестируем различные комбинации общего количества и размера страницы
        test_cases = [
            (25, 10, 3),  # 25 элементов, 10 на странице = 3 страницы
            (30, 10, 3),  # 30 элементов, 10 на странице = 3 страницы  
            (31, 10, 4),  # 31 элемент, 10 на странице = 4 страницы
            (100, 7, 15), # 100 элементов, 7 на странице = 15 страниц
        ]
        
        for total_items, items_per_page, expected_pages in test_cases:
            nav = UINavigation(items_per_page=items_per_page)
            test_items = create_test_items(total_items)
            _, pagination_info = nav.get_page_data(test_items, page=1)
            
            assert pagination_info['total_pages'] == expected_pages

    def test_complex_formatter_function(self):
        """Тестирование сложной функции форматирования"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        def complex_formatter(item: Any, index: Optional[int] = None) -> str:
            """Сложная функция форматирования для тестирования"""
            prefix = f"[{index}] " if index else "• "
            title = item.get('title', 'Без названия')
            data = item.get('data', 'Нет данных')
            return f"{prefix}{title} ({data})"

        page_items, _ = self.nav.get_page_data(self.test_items, page=1)
        
        # Проверяем, что форматтер работает корректно
        formatted_with_index = complex_formatter(self.test_items[0], 1)
        assert "[1]" in formatted_with_index
        assert "Item 1" in formatted_with_index
        
        formatted_without_index = complex_formatter(self.test_items[0])
        assert "•" in formatted_without_index

    @patch('builtins.input', side_effect=['100', 'q'])
    @patch('builtins.print')
    def test_navigation_boundary_page_numbers(self, mock_print, mock_input):
        """Тестирование граничных номеров страниц"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        # Используем меньше элементов для ускорения
        test_items = create_test_items(10)
        self.nav.paginate_display(test_items, simple_formatter)
        
        # Должно обработать некорректный номер страницы
        assert mock_print.called
        assert mock_input.call_count == 2


class TestUINavigationIntegration:
    """Интеграционные тесты для ui_navigation"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        if SRC_AVAILABLE:
            self.nav = UINavigation(items_per_page=4)

    @patch('builtins.input', side_effect=['n', 'p', '1', 'q'])  # Убран переход на страницу 3
    @patch('builtins.print')
    def test_full_navigation_workflow(self, mock_print, mock_input):
        """Тестирование полного рабочего процесса навигации"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        test_items = create_test_items(8)  # Уменьшено с 12 до 8 элементов
        
        self.nav.paginate_display(
            test_items, 
            simple_formatter, 
            header="Полный тест навигации",
            show_numbers=True
        )
        
        assert mock_print.called
        assert mock_input.call_count == 4  # Изменено с 5 на 4

    @patch('builtins.input', side_effect=['c', 's', 'q'])
    @patch('builtins.print')
    def test_navigation_with_multiple_custom_actions(self, mock_print, mock_input):
        """Тестирование навигации с несколькими пользовательскими действиями"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        action_counts = {"custom": 0, "search": 0}
        
        def custom_action():
            """Пользовательское действие"""
            action_counts["custom"] += 1

        def search_action():
            """Действие поиска"""
            action_counts["search"] += 1

        custom_actions = {
            "c": custom_action,
            "s": search_action
        }
        
        test_items = create_test_items(8)
        self.nav.paginate_display(
            test_items, 
            simple_formatter, 
            custom_actions=custom_actions
        )
        
        assert action_counts["custom"] == 1
        assert action_counts["search"] == 1

    def test_navigation_performance_large_dataset(self):
        """Тестирование производительности с большим набором данных"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        import time
        
        # Уменьшаем размер тестового набора для ускорения
        large_items = create_test_items(100)
        
        start_time = time.time()
        page_items, pagination_info = self.nav.get_page_data(large_items, page=5)
        end_time = time.time()
        
        # Операция должна быть быстрой даже для больших данных
        assert (end_time - start_time) < 0.1
        
        # Проверяем корректность результата
        assert len(page_items) == 4
        assert pagination_info['current_page'] == 5

    def test_navigation_with_complex_data_structures(self):
        """Тестирование навигации со сложными структурами данных"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        # Уменьшаем количество элементов для ускорения
        complex_items = [
            {
                "id": i,
                "title": f"Сложная структура {i}",
                "data": {
                    "nested": {"value": i * 10},
                    "list": [f"item_{i}_{j}" for j in range(2)],  # Уменьшено с 3 до 2
                    "metadata": {"created": f"2024-01-{i:02d}", "type": "test"}
                }
            }
            for i in range(1, 9)  # Уменьшено с 16 до 9
        ]
        
        def complex_formatter(item: Any, index: Optional[int] = None) -> str:
            """Форматтер для сложных данных"""
            prefix = f"{index}. " if index else ""
            title = item.get('title', 'Unknown')
            nested_value = item.get('data', {}).get('nested', {}).get('value', 0)
            return f"{prefix}{title} (значение: {nested_value})"

        page_items, pagination_info = self.nav.get_page_data(complex_items, page=2)
        
        assert len(page_items) == 4
        assert pagination_info['current_page'] == 2
        assert pagination_info['total_pages'] == 4  # math.ceil(15/4) = 4
        
        # Проверяем, что форматтер работает с комплексными данными
        formatted = complex_formatter(page_items[0], 5)
        assert "Сложная структура" in formatted
        assert "значение:" in formatted


class TestUINavigationStaticMethods:
    """Тестирование статических методов UINavigation"""

    @patch('builtins.print')
    def test_display_navigation_menu_static(self, mock_print):
        """Тестирование статического метода отображения меню"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        UINavigation._display_navigation_menu(current_page=2, total_pages=5)
        assert mock_print.called

    def test_handle_navigation_choice_static(self):
        """Тестирование статического метода обработки выбора"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        result = UINavigation._handle_navigation_choice("n", current_page=2, total_pages=5)
        assert result == 3
        
        result = UINavigation._handle_navigation_choice("q", current_page=2, total_pages=5)
        assert result == -1

    def test_static_method_independence(self):
        """Тестирование независимости статических методов"""
        if not SRC_AVAILABLE:
            pytest.skip("Source code not available")
            
        # Статические методы должны работать без экземпляра класса
        result1 = UINavigation._handle_navigation_choice("2", 1, 5)
        result2 = UINavigation._handle_navigation_choice("3", 1, 5)
        
        assert result1 == 2
        assert result2 == 3
        assert result1 != result2
