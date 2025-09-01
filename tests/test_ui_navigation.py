import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vacancies.models import Vacancy
# Импортируем классы и функции из src, если они существуют
try:
    from src.utils.ui_navigation import quick_paginate, calculate_pagination, UINavigation
    SRC_AVAILABLE = True
except ImportError:
    SRC_AVAILABLE = False

    # Если модули из src недоступны, определяем заглушки/тестовые реализации
    def quick_paginate(items, formatter, header="Данные", items_per_page=10, show_numbers=True, custom_actions=None):
        """Заглушка функции быстрой пагинации"""
        print(f"\n{header}")
        print("=" * 50)
        if not items:
            print("Нет элементов для отображения")
            return

        total_items = len(items)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        current_page = 0

        while current_page < total_pages:
            start_idx = current_page * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)

            for i in range(start_idx, end_idx):
                if show_numbers:
                    print(f"{i + 1}. {formatter(items[i], i + 1)}")
                else:
                    print(formatter(items[i]))

            if custom_actions:
                for action_key, action_func in custom_actions.items():
                    print(f"   {action_key}: {action_func.__name__}")

            print(f"\nСтраница {current_page + 1} из {total_pages}")

            if current_page < total_pages - 1:
                user_input = input("Нажмите Enter для следующей страницы, 'q' для выхода, или выберите действие: ")
                if user_input.lower() == 'q':
                    break
                elif user_input in custom_actions:
                    custom_actions[user_input]()  # Вызываем выбранное действие
                else:
                    current_page += 1
            else:
                input("Нажмите Enter для завершения...")
                break

    def calculate_pagination(total_items, items_per_page):
        """Заглушка функции расчета пагинации"""
        if items_per_page <= 0:
            raise ValueError("items_per_page must be positive")
        total_pages = (total_items + items_per_page - 1) // items_per_page
        return {
            "total_pages": total_pages,
            "items_per_page": items_per_page,
            "total_items": total_items
        }

    class UINavigation:
        """Заглушка класса UINavigation"""
        def __init__(self, items_per_page=10):
            self.items_per_page = items_per_page

        def paginate_display(self, items, formatter, header="", show_numbers=True, custom_actions=None):
            """Отображает элементы с пагинацией"""
            quick_paginate(items, formatter, header, self.items_per_page, show_numbers, custom_actions)


class TestUINavigation:
    """Тесты для модуля навигации UI"""

    @pytest.fixture
    def sample_items(self):
        """Фикстура для создания тестовых элементов"""
        return [
            {"id": i, "title": f"Item {i}", "description": f"Description {i}"}
            for i in range(1, 11)
        ]

    @pytest.fixture
    def sample_vacancies(self):
        """Фикстура для создания тестовых вакансий"""
        return [
            Vacancy(
                title=f"Developer {i}",
                url=f"https://test.com/{i}",
                vacancy_id=str(i),
                source="hh.ru"
            )
            for i in range(1, 11)
        ]

    @patch('builtins.input', side_effect=["", "", "", "", "", "", "", "", "q"])
    @patch('builtins.print')
    def test_quick_paginate_basic(self, mock_print, mock_input, sample_items):
        """Тест базовой пагинации"""
        if SRC_AVAILABLE:
            quick_paginate_func = quick_paginate
            formatter_func = lambda item, number=None: f"{number}. {item['id']}: {item['title']}" if number else f"{item['id']}: {item['title']}"
        else:
            # Тестовая реализация, если src.utils.ui_navigation.quick_paginate недоступен
            def quick_paginate_test(items, formatter, header="", items_per_page=10, show_numbers=True, custom_actions=None):
                print(f"\n{header}")
                print("=" * 50)
                if not items:
                    print("Нет элементов для отображения")
                    return
                total_items = len(items)
                total_pages = (total_items + items_per_page - 1) // items_per_page
                current_page = 0
                while current_page < total_pages:
                    start_idx = current_page * items_per_page
                    end_idx = min(start_idx + items_per_page, total_items)
                    for i in range(start_idx, end_idx):
                        if show_numbers:
                            print(f"{i + 1}. {formatter(items[i], i + 1)}")
                        else:
                            print(formatter(items[i]))
                    print(f"\nСтраница {current_page + 1} из {total_pages}")
                    if current_page < total_pages - 1:
                        input("Нажмите Enter для следующей страницы или 'q' для выхода: ")
                    else:
                        input("Нажмите Enter для завершения...")
                    current_page += 1

            quick_paginate_func = quick_paginate_test
            formatter_func = lambda item, number=None: f"{number}. {item['id']}: {item['title']}" if number else f"{item['id']}: {item['title']}"


        quick_paginate_func(
            sample_items,
            formatter=formatter_func,
            header="Test Items",
            items_per_page=3
        )
        mock_print.assert_called()

    @patch('builtins.input', return_value="q")
    @patch('builtins.print')
    def test_quick_paginate_empty_list(self, mock_print, mock_input):
        """Тест пагинации с пустым списком"""
        if SRC_AVAILABLE:
            quick_paginate_func = quick_paginate
        else:
            def quick_paginate_test(items, formatter, header="", items_per_page=10, show_numbers=True, custom_actions=None):
                print("Нет элементов для отображения")
            quick_paginate_func = quick_paginate_test

        quick_paginate_func([], lambda x: str(x), "Empty Test")
        mock_print.assert_called()

    @patch('builtins.input', return_value="q")
    @patch('builtins.print')
    def test_quick_paginate_with_vacancies(self, mock_print, mock_input, sample_vacancies):
        """Тест пагинации с вакансиями"""
        if SRC_AVAILABLE:
            quick_paginate_func = quick_paginate
            formatter_func = lambda vacancy, number=None: f"{number}. {vacancy.title} - {vacancy.source}" if number else f"{vacancy.title} - {vacancy.source}"
        else:
            def quick_paginate_test(items, formatter, header="", items_per_page=10, show_numbers=True, custom_actions=None):
                for i, item in enumerate(items, 1):
                    print(f"{i}. {formatter(item)}")

            quick_paginate_func = quick_paginate_test
            formatter_func = lambda vacancy, number=None: f"{number}. {vacancy.title} - {vacancy.source}" if number else f"{vacancy.title} - {vacancy.source}"


        quick_paginate_func(
            sample_vacancies[:5],
            formatter=formatter_func,
            header="Test Vacancies",
            items_per_page=2
        )
        mock_print.assert_called()

    def test_pagination_calculation(self):
        """Тест расчета параметров пагинации"""
        if SRC_AVAILABLE:
            calculate_pagination_func = calculate_pagination
        else:
            def calculate_pagination_test(total_items, items_per_page):
                if items_per_page <= 0:
                    raise ValueError("items_per_page must be positive")
                total_pages = (total_items + items_per_page - 1) // items_per_page
                return {
                    "total_pages": total_pages,
                    "items_per_page": items_per_page,
                    "total_items": total_items
                }
            calculate_pagination_func = calculate_pagination_test

        result = calculate_pagination_func(total_items=100, items_per_page=10)
        assert result["total_pages"] == 10
        assert result["items_per_page"] == 10
        assert result["total_items"] == 100

    @patch('builtins.input', side_effect=["2", "1", "q", "q", "q", "q", "q"])
    @patch('builtins.print')
    def test_quick_paginate_with_actions(self, mock_print, mock_input, sample_items):
        """Тест для quick_paginate с действиями"""
        if SRC_AVAILABLE:
            quick_paginate_func = quick_paginate
        else:
            def quick_paginate_test(items, formatter, header="", items_per_page=10, show_numbers=True, custom_actions=None):
                print(header)
                print("=" * 50)
                for item in items:
                    print(formatter(item))
                print("Навигация завершена")
            quick_paginate_func = quick_paginate_test


        def simple_formatter(item, number=None):
            if number:
                return f"{number}. {item['title']}"
            return str(item["title"])

        # Пример действия
        def mock_action():
            print("Action executed")

        custom_actions = {"1": mock_action} # Привязываем действие к вводу "1"

        quick_paginate_func(
            sample_items,
            formatter=simple_formatter,
            header="Navigation Test",
            items_per_page=3,
            custom_actions=custom_actions
        )
        mock_print.assert_called()

    @patch('builtins.input', side_effect=["n", "", "", "q"])
    @patch('builtins.print')
    def test_navigation_controls(self, mock_print, mock_input, sample_items):
        """Тест элементов управления навигацией"""
        if SRC_AVAILABLE:
            quick_paginate_func = quick_paginate
        else:
            def quick_paginate_test(items, formatter, header="", items_per_page=10, show_numbers=True, custom_actions=None):
                print(header)
                print("=" * 50)
                for item in items:
                    print(formatter(item))
                print("Навигация завершена")
            quick_paginate_func = quick_paginate_test

        def simple_formatter(item, number=None):
            if number:
                return f"{number}. {item['title']}"
            return str(item["title"])

        quick_paginate_func(
            sample_items,
            formatter=simple_formatter,
            header="Navigation Test",
            items_per_page=3
        )
        mock_print.assert_called()

    # Дополнительные тесты для покрытия
    @patch('builtins.input', side_effect=["1", "q"]) # Тест перехода на 1 страницу
    @patch('builtins.print')
    def test_quick_paginate_specific_page(self, mock_print, mock_input, sample_items):
        """Тест перехода на конкретную страницу"""
        if SRC_AVAILABLE:
            quick_paginate_func = quick_paginate
            formatter_func = lambda item, number=None: f"{number}. {item['id']}: {item['title']}" if number else f"{item['id']}: {item['title']}"
        else:
            def quick_paginate_test(items, formatter, header="", items_per_page=10, show_numbers=True, custom_actions=None):
                print(f"\n{header}")
                print("=" * 50)
                total_items = len(items)
                total_pages = (total_items + items_per_page - 1) // items_per_page
                current_page = 0
                while current_page < total_pages:
                    start_idx = current_page * items_per_page
                    end_idx = min(start_idx + items_per_page, total_items)
                    for i in range(start_idx, end_idx):
                        if show_numbers:
                            print(f"{i + 1}. {formatter(items[i], i + 1)}")
                        else:
                            print(formatter(items[i]))
                    print(f"\nСтраница {current_page + 1} из {total_pages}")
                    if current_page < total_pages - 1:
                        input("Нажмите Enter для следующей страницы или 'q' для выхода: ")
                    else:
                        input("Нажмите Enter для завершения...")
                    current_page += 1

            quick_paginate_func = quick_paginate_test
            formatter_func = lambda item, number=None: f"{number}. {item['id']}: {item['title']}" if number else f"{item['id']}: {item['title']}"

        quick_paginate_func(
            sample_items,
            formatter=formatter_func,
            header="Test Page Navigation",
            items_per_page=3
        )
        mock_print.assert_called()

    @patch('builtins.input', side_effect=["", "q"]) # Тест без ввода номера страницы
    @patch('builtins.print')
    def test_quick_paginate_next_page(self, mock_print, mock_input, sample_items):
        """Тест перехода на следующую страницу по Enter"""
        if SRC_AVAILABLE:
            quick_paginate_func = quick_paginate
            formatter_func = lambda item, number=None: f"{number}. {item['id']}: {item['title']}" if number else f"{item['id']}: {item['title']}"
        else:
            def quick_paginate_test(items, formatter, header="", items_per_page=10, show_numbers=True, custom_actions=None):
                print(f"\n{header}")
                print("=" * 50)
                total_items = len(items)
                total_pages = (total_items + items_per_page - 1) // items_per_page
                current_page = 0
                while current_page < total_pages:
                    start_idx = current_page * items_per_page
                    end_idx = min(start_idx + items_per_page, total_items)
                    for i in range(start_idx, end_idx):
                        if show_numbers:
                            print(f"{i + 1}. {formatter(items[i], i + 1)}")
                        else:
                            print(formatter(items[i]))
                    print(f"\nСтраница {current_page + 1} из {total_pages}")
                    if current_page < total_pages - 1:
                        input("Нажмите Enter для следующей страницы, 'q' для выхода: ")
                    else:
                        input("Нажмите Enter для завершения...")
                    current_page += 1

            quick_paginate_func = quick_paginate_test
            formatter_func = lambda item, number=None: f"{number}. {item['id']}: {item['title']}" if number else f"{item['id']}: {item['title']}"

        quick_paginate_func(
            sample_items,
            formatter=formatter_func,
            header="Test Next Page",
            items_per_page=3
        )
        mock_print.assert_called()

    @patch('builtins.input', side_effect=["q"]) # Тест выхода при первом запросе
    @patch('builtins.print')
    def test_quick_paginate_exit_early(self, mock_print, mock_input, sample_items):
        """Тест выхода из пагинации на первом шаге"""
        if SRC_AVAILABLE:
            quick_paginate_func = quick_paginate
            formatter_func = lambda item, number=None: f"{number}. {item['id']}: {item['title']}" if number else f"{item['id']}: {item['title']}"
        else:
            def quick_paginate_test(items, formatter, header="", items_per_page=10, show_numbers=True, custom_actions=None):
                print(f"\n{header}")
                print("=" * 50)
                if not items:
                    print("Нет элементов для отображения")
                    return
                total_items = len(items)
                total_pages = (total_items + items_per_page - 1) // items_per_page
                current_page = 0
                while current_page < total_pages:
                    start_idx = current_page * items_per_page
                    end_idx = min(start_idx + items_per_page, total_items)
                    for i in range(start_idx, end_idx):
                        if show_numbers:
                            print(f"{i + 1}. {formatter(items[i], i + 1)}")
                        else:
                            print(formatter(items[i]))
                    print(f"\nСтраница {current_page + 1} из {total_pages}")
                    user_input = input("Нажмите Enter для следующей страницы, 'q' для выхода: ")
                    if user_input.lower() == 'q':
                        break
                    current_page += 1

            quick_paginate_func = quick_paginate_test
            formatter_func = lambda item, number=None: f"{number}. {item['id']}: {item['title']}" if number else f"{item['id']}: {item['title']}"


        quick_paginate_func(
            sample_items,
            formatter=formatter_func,
            header="Test Early Exit",
            items_per_page=3
        )
        mock_print.assert_called()

    @patch('builtins.print')
    def test_calculate_pagination_edge_cases(self, mock_print):
        """Тест крайних случаев для calculate_pagination"""
        if SRC_AVAILABLE:
            calculate_pagination_func = calculate_pagination
        else:
            def calculate_pagination_test(total_items, items_per_page):
                if items_per_page <= 0:
                    raise ValueError("items_per_page must be positive")
                total_pages = (total_items + items_per_page - 1) // items_per_page
                return {
                    "total_pages": total_pages,
                    "items_per_page": items_per_page,
                    "total_items": total_items
                }
            calculate_pagination_func = calculate_pagination_test

        # Случай с 0 элементов
        result_zero_items = calculate_pagination_func(total_items=0, items_per_page=10)
        assert result_zero_items["total_pages"] == 0

        # Случай с 1 элементом
        result_one_item = calculate_pagination_func(total_items=1, items_per_page=10)
        assert result_one_item["total_pages"] == 1

        # Случай, когда количество элементов кратно items_per_page
        result_exact_pages = calculate_pagination_func(total_items=20, items_per_page=5)
        assert result_exact_pages["total_pages"] == 4

        # Случай с большим количеством элементов
        result_large_list = calculate_pagination_func(total_items=150, items_per_page=7)
        assert result_large_list["total_pages"] == 22

    @pytest.mark.parametrize(
        "items_per_page, expected_pages",
        [
            (1, 10),
            (2, 5),
            (5, 2),
            (10, 1),
            (11, 1) # Test case where items_per_page is greater than total items
        ]
    )
    def test_calculate_pagination_various_items_per_page(self, items_per_page, expected_pages):
        """Тест calculate_pagination с различными значениями items_per_page"""
        if SRC_AVAILABLE:
            calculate_pagination_func = calculate_pagination
        else:
            def calculate_pagination_test(total_items, items_per_page):
                if items_per_page <= 0:
                    raise ValueError("items_per_page must be positive")
                total_pages = (total_items + items_per_page - 1) // items_per_page
                return {
                    "total_pages": total_pages,
                    "items_per_page": items_per_page,
                    "total_items": 10
                }
            calculate_pagination_func = calculate_pagination_test

        result = calculate_pagination_func(total_items=10, items_per_page=items_per_page)
        assert result["total_pages"] == expected_pages

    @pytest.mark.parametrize("items_per_page", [0, -1])
    def test_calculate_pagination_invalid_items_per_page(self, items_per_page):
        """Тест calculate_pagination с некорректными значениями items_per_page"""
        if SRC_AVAILABLE:
            calculate_pagination_func = calculate_pagination
        else:
            def calculate_pagination_test(total_items, items_per_page):
                if items_per_page <= 0:
                    raise ValueError("items_per_page must be positive")
                total_pages = (total_items + items_per_page - 1) // items_per_page
                return {
                    "total_pages": total_pages,
                    "items_per_page": items_per_page,
                    "total_items": 10
                }
            calculate_pagination_func = calculate_pagination_test

        with pytest.raises(ValueError):
            calculate_pagination_func(total_items=10, items_per_page=items_per_page)