#!/usr/bin/env python3
"""
Тесты модуля menu_manager.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций 
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Мокирование всех print() вызовов

Модуль содержит:
- Класс MenuManager для управления интерактивными меню
- Методы для добавления, удаления, отображения пунктов меню
- Функции для создания главного меню и печати разделителей
- Логику позиционирования и обработчиков пунктов меню
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Callable, Dict, List, Tuple, Any

from src.utils.menu_manager import (
    MenuManager,
    create_main_menu,
    print_menu_separator,
    print_section_header
)


class TestMenuManagerInit:
    """100% покрытие инициализации MenuManager"""

    def test_init(self) -> None:
        """Покрытие: инициализация MenuManager"""
        menu = MenuManager()
        
        # Проверяем инициализацию атрибутов
        assert isinstance(menu.menu_items, dict)
        assert isinstance(menu.menu_order, list)
        assert len(menu.menu_items) == 0
        assert len(menu.menu_order) == 0

    def test_multiple_instances_independence(self) -> None:
        """Покрытие: независимость нескольких экземпляров"""
        menu1 = MenuManager()
        menu2 = MenuManager()
        
        # Добавляем элемент в первое меню
        menu1.add_menu_item("1", "Test Item 1", lambda: None)
        
        # Проверяем, что второе меню остается пустым
        assert len(menu1.menu_items) == 1
        assert len(menu2.menu_items) == 0
        assert menu1.menu_items is not menu2.menu_items
        assert menu1.menu_order is not menu2.menu_order


class TestAddMenuItem:
    """100% покрытие метода add_menu_item"""

    def test_add_menu_item_basic(self) -> None:
        """Покрытие: базовое добавление пункта меню"""
        menu = MenuManager()
        handler = lambda: "test_handler"
        
        menu.add_menu_item("1", "Test Item", handler)
        
        assert "1" in menu.menu_items
        assert menu.menu_items["1"] == ("Test Item", handler)
        assert menu.menu_order == ["1"]

    def test_add_menu_item_multiple(self) -> None:
        """Покрытие: добавление нескольких пунктов"""
        menu = MenuManager()
        handler1 = lambda: "handler1"
        handler2 = lambda: "handler2"
        handler3 = lambda: "handler3"
        
        menu.add_menu_item("1", "Item 1", handler1)
        menu.add_menu_item("2", "Item 2", handler2)
        menu.add_menu_item("3", "Item 3", handler3)
        
        assert len(menu.menu_items) == 3
        assert menu.menu_order == ["1", "2", "3"]
        assert menu.menu_items["2"] == ("Item 2", handler2)

    def test_add_menu_item_with_none_handler(self) -> None:
        """Покрытие: добавление пункта с None обработчиком"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "Test Item", None)
        
        assert menu.menu_items["1"] == ("Test Item", None)
        assert menu.menu_order == ["1"]

    def test_add_menu_item_with_position_beginning(self) -> None:
        """Покрытие: добавление в начало (position=0)"""
        menu = MenuManager()
        
        # Добавляем первый элемент
        menu.add_menu_item("1", "First", lambda: None)
        menu.add_menu_item("2", "Second", lambda: None)
        
        # Добавляем в начало
        handler = lambda: None
        menu.add_menu_item("0", "New First", handler, position=0)
        
        assert menu.menu_order == ["0", "1", "2"]
        assert menu.menu_items["0"][0] == "New First"
        assert menu.menu_items["0"][1] is handler

    def test_add_menu_item_with_position_middle(self) -> None:
        """Покрытие: добавление в середину"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "First", lambda: None)
        menu.add_menu_item("2", "Second", lambda: None)
        menu.add_menu_item("3", "Third", lambda: None)
        
        # Добавляем в позицию 1 (между первым и вторым)
        menu.add_menu_item("1.5", "Middle", lambda: None, position=1)
        
        assert menu.menu_order == ["1", "1.5", "2", "3"]

    def test_add_menu_item_with_position_end(self) -> None:
        """Покрытие: добавление в конец через position"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "First", lambda: None)
        menu.add_menu_item("2", "Second", lambda: None)
        
        # Добавляем в последнюю позицию
        menu.add_menu_item("3", "Last", lambda: None, position=2)
        
        assert menu.menu_order == ["1", "2", "3"]

    def test_add_menu_item_with_position_out_of_bounds(self) -> None:
        """Покрытие: position больше длины списка"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "First", lambda: None)
        
        # Позиция больше длины списка - должно добавиться в конец
        menu.add_menu_item("2", "Second", lambda: None, position=10)
        
        assert menu.menu_order == ["1", "2"]

    def test_add_menu_item_with_negative_position(self) -> None:
        """Покрытие: отрицательная position"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "First", lambda: None)
        
        # Отрицательная позиция - должно добавиться в конец
        menu.add_menu_item("2", "Second", lambda: None, position=-1)
        
        assert menu.menu_order == ["1", "2"]

    def test_add_menu_item_replace_existing_key(self) -> None:
        """Покрытие: замена существующего ключа"""
        menu = MenuManager()
        
        original_handler = lambda: "original"
        replaced_handler = lambda: "replaced"
        
        menu.add_menu_item("1", "Original", original_handler)
        menu.add_menu_item("1", "Replaced", replaced_handler)
        
        # Ключ должен быть заменен, но порядок остаться
        assert menu.menu_items["1"][0] == "Replaced"
        assert menu.menu_items["1"][1] is replaced_handler
        assert menu.menu_order == ["1", "1"]  # Ключ добавляется дважды в order


class TestRemoveMenuItem:
    """100% покрытие метода remove_menu_item"""

    def test_remove_menu_item_existing(self) -> None:
        """Покрытие: удаление существующего пункта"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "Item 1", lambda: None)
        menu.add_menu_item("2", "Item 2", lambda: None)
        menu.add_menu_item("3", "Item 3", lambda: None)
        
        result = menu.remove_menu_item("2")
        
        assert result is True
        assert "2" not in menu.menu_items
        assert menu.menu_order == ["1", "3"]
        assert len(menu.menu_items) == 2

    def test_remove_menu_item_nonexistent(self) -> None:
        """Покрытие: удаление несуществующего пункта"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "Item 1", lambda: None)
        
        result = menu.remove_menu_item("999")
        
        assert result is False
        assert len(menu.menu_items) == 1
        assert menu.menu_order == ["1"]

    def test_remove_menu_item_empty_menu(self) -> None:
        """Покрытие: удаление из пустого меню"""
        menu = MenuManager()
        
        result = menu.remove_menu_item("1")
        
        assert result is False
        assert len(menu.menu_items) == 0
        assert len(menu.menu_order) == 0

    def test_remove_menu_item_single_item(self) -> None:
        """Покрытие: удаление единственного пункта"""
        menu = MenuManager()
        
        menu.add_menu_item("only", "Only Item", lambda: None)
        result = menu.remove_menu_item("only")
        
        assert result is True
        assert len(menu.menu_items) == 0
        assert len(menu.menu_order) == 0

    def test_remove_menu_item_all_items(self) -> None:
        """Покрытие: удаление всех пунктов последовательно"""
        menu = MenuManager()
        
        keys = ["1", "2", "3", "4"]
        for key in keys:
            menu.add_menu_item(key, f"Item {key}", lambda: None)
        
        # Удаляем все пункты
        for key in keys:
            result = menu.remove_menu_item(key)
            assert result is True
        
        assert len(menu.menu_items) == 0
        assert len(menu.menu_order) == 0


class TestGetMenuItems:
    """100% покрытие метода get_menu_items"""

    def test_get_menu_items_empty(self) -> None:
        """Покрытие: получение пунктов пустого меню"""
        menu = MenuManager()
        
        items = menu.get_menu_items()
        
        assert items == []

    def test_get_menu_items_single(self) -> None:
        """Покрытие: получение одного пункта"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "Single Item", lambda: None)
        items = menu.get_menu_items()
        
        assert items == [("1", "Single Item")]

    def test_get_menu_items_multiple_ordered(self) -> None:
        """Покрытие: получение множественных пунктов в правильном порядке"""
        menu = MenuManager()
        
        menu.add_menu_item("3", "Third", lambda: None)
        menu.add_menu_item("1", "First", lambda: None)
        menu.add_menu_item("2", "Second", lambda: None)
        
        items = menu.get_menu_items()
        
        # Должен вернуть в порядке добавления
        assert items == [("3", "Third"), ("1", "First"), ("2", "Second")]

    def test_get_menu_items_with_positions(self) -> None:
        """Покрытие: получение пунктов с учетом позиций"""
        menu = MenuManager()
        
        menu.add_menu_item("2", "Second", lambda: None)
        menu.add_menu_item("1", "First", lambda: None, position=0)
        menu.add_menu_item("3", "Third", lambda: None)
        
        items = menu.get_menu_items()
        
        assert items == [("1", "First"), ("2", "Second"), ("3", "Third")]

    def test_get_menu_items_with_inconsistent_order(self) -> None:
        """Покрытие: получение пунктов когда order содержит несуществующие ключи"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "Item 1", lambda: None)
        menu.add_menu_item("2", "Item 2", lambda: None)
        
        # Вручную добавляем несуществующий ключ в order
        menu.menu_order.append("999")
        
        items = menu.get_menu_items()
        
        # Должен фильтровать только существующие ключи
        assert items == [("1", "Item 1"), ("2", "Item 2")]

    def test_get_menu_items_after_removal(self) -> None:
        """Покрытие: получение пунктов после удаления"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "Item 1", lambda: None)
        menu.add_menu_item("2", "Item 2", lambda: None)
        menu.add_menu_item("3", "Item 3", lambda: None)
        
        menu.remove_menu_item("2")
        items = menu.get_menu_items()
        
        assert items == [("1", "Item 1"), ("3", "Item 3")]


class TestGetHandler:
    """100% покрытие метода get_handler"""

    def test_get_handler_existing(self) -> None:
        """Покрытие: получение существующего обработчика"""
        menu = MenuManager()
        handler = lambda: "test_result"
        
        menu.add_menu_item("1", "Test Item", handler)
        retrieved_handler = menu.get_handler("1")
        
        assert retrieved_handler is handler
        assert retrieved_handler() == "test_result"

    def test_get_handler_nonexistent(self) -> None:
        """Покрытие: получение несуществующего обработчика"""
        menu = MenuManager()
        
        retrieved_handler = menu.get_handler("999")
        
        assert retrieved_handler is None

    def test_get_handler_none_handler(self) -> None:
        """Покрытие: получение None обработчика"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "Test Item", None)
        retrieved_handler = menu.get_handler("1")
        
        assert retrieved_handler is None

    def test_get_handler_empty_menu(self) -> None:
        """Покрытие: получение обработчика из пустого меню"""
        menu = MenuManager()
        
        retrieved_handler = menu.get_handler("1")
        
        assert retrieved_handler is None

    def test_get_handler_multiple_items(self) -> None:
        """Покрытие: получение разных обработчиков"""
        menu = MenuManager()
        
        handler1 = lambda: "result1"
        handler2 = lambda: "result2"
        handler3 = None
        
        menu.add_menu_item("1", "Item 1", handler1)
        menu.add_menu_item("2", "Item 2", handler2)
        menu.add_menu_item("3", "Item 3", handler3)
        
        assert menu.get_handler("1") is handler1
        assert menu.get_handler("2") is handler2
        assert menu.get_handler("3") is None
        assert menu.get_handler("999") is None


class TestDisplayMenu:
    """100% покрытие метода display_menu"""

    @patch('builtins.print')
    @patch('src.utils.menu_manager.print_menu_separator')
    def test_display_menu_empty(self, mock_separator: Any, mock_print: Any) -> None:
        """Покрытие: отображение пустого меню"""
        menu = MenuManager()
        
        menu.display_menu()
        
        # Проверяем вызовы print
        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        
        # Ищем конкретные строки
        assert any("\n" in call for call in print_calls)  # Проверяем перенос строки
        assert any("Выберите действие:" in call for call in print_calls)
        assert any("0. Выход" in call for call in print_calls)
        
        # Проверяем вызовы разделителя
        assert mock_separator.call_count == 2

    @patch('builtins.print')
    @patch('src.utils.menu_manager.print_menu_separator')
    def test_display_menu_with_items(self, mock_separator: Any, mock_print: Any) -> None:
        """Покрытие: отображение меню с пунктами"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "First Item", lambda: None)
        menu.add_menu_item("2", "Second Item", lambda: None)
        menu.add_menu_item("3", "Third Item", lambda: None)
        
        menu.display_menu()
        
        # Проверяем, что все пункты отображены
        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("1. First Item" in call for call in print_calls)
        assert any("2. Second Item" in call for call in print_calls)
        assert any("3. Third Item" in call for call in print_calls)
        assert any("0. Выход" in call for call in print_calls)

    @patch('builtins.print')
    @patch('src.utils.menu_manager.print_menu_separator')
    def test_display_menu_with_complex_titles(self, mock_separator: Any, mock_print: Any) -> None:
        """Покрытие: отображение меню со сложными заголовками"""
        menu = MenuManager()
        
        menu.add_menu_item("1", "Поиск вакансий по запросу (запрос к API)", lambda: None)
        menu.add_menu_item("10", "Демонстрация DBManager (анализ данных в БД)", lambda: None)
        
        menu.display_menu()
        
        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("1. Поиск вакансий по запросу (запрос к API)" in call for call in print_calls)
        assert any("10. Демонстрация DBManager (анализ данных в БД)" in call for call in print_calls)


class TestCreateMainMenu:
    """100% покрытие функции create_main_menu"""

    def test_create_main_menu_structure(self) -> None:
        """Покрытие: создание главного меню"""
        menu = create_main_menu()
        
        # Проверяем тип
        assert isinstance(menu, MenuManager)
        
        # Проверяем количество пунктов
        items = menu.get_menu_items()
        assert len(items) == 10
        
        # Проверяем ключи
        expected_keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        actual_keys = [item[0] for item in items]
        assert actual_keys == expected_keys

    def test_create_main_menu_items_content(self) -> None:
        """Покрытие: содержимое пунктов главного меню"""
        menu = create_main_menu()
        items = menu.get_menu_items()
        
        # Проверяем конкретные пункты
        items_dict = dict(items)
        assert "Поиск вакансий по запросу" in items_dict["1"]
        assert "Показать все сохраненные вакансии" in items_dict["2"]
        assert "Топ N сохраненных вакансий" in items_dict["3"]
        assert "Поиск в сохраненных вакансиях" in items_dict["4"]
        assert "Расширенный поиск" in items_dict["5"]
        assert "Фильтр сохраненных вакансий" in items_dict["6"]
        assert "Удалить сохраненные вакансии" in items_dict["7"]
        assert "Очистить кэш API" in items_dict["8"]
        assert "Настройка SuperJob API" in items_dict["9"]
        assert "Демонстрация DBManager" in items_dict["10"]

    def test_create_main_menu_handlers_are_none(self) -> None:
        """Покрытие: все обработчики главного меню None"""
        menu = create_main_menu()
        
        for i in range(1, 11):
            handler = menu.get_handler(str(i))
            assert handler is None

    def test_create_main_menu_independence(self) -> None:
        """Покрытие: независимость множественных вызовов"""
        menu1 = create_main_menu()
        menu2 = create_main_menu()
        
        assert menu1 is not menu2
        assert menu1.menu_items is not menu2.menu_items
        assert len(menu1.get_menu_items()) == len(menu2.get_menu_items())


class TestPrintMenuSeparator:
    """100% покрытие функции print_menu_separator"""

    @patch('builtins.print')
    def test_print_menu_separator_default_width(self, mock_print: Any) -> None:
        """Покрытие: разделитель с шириной по умолчанию"""
        print_menu_separator()
        
        mock_print.assert_called_once_with("-" * 40)

    @patch('builtins.print')
    def test_print_menu_separator_custom_width(self, mock_print: Any) -> None:
        """Покрытие: разделитель с заданной шириной"""
        print_menu_separator(20)
        
        mock_print.assert_called_once_with("-" * 20)

    @patch('builtins.print')
    def test_print_menu_separator_zero_width(self, mock_print: Any) -> None:
        """Покрытие: разделитель нулевой ширины"""
        print_menu_separator(0)
        
        mock_print.assert_called_once_with("")

    @patch('builtins.print')
    def test_print_menu_separator_large_width(self, mock_print: Any) -> None:
        """Покрытие: разделитель большой ширины"""
        print_menu_separator(100)
        
        mock_print.assert_called_once_with("-" * 100)

    @patch('builtins.print')
    def test_print_menu_separator_multiple_calls(self, mock_print: Any) -> None:
        """Покрытие: множественные вызовы разделителя"""
        print_menu_separator(10)
        print_menu_separator(15)
        print_menu_separator(5)
        
        expected_calls = [
            ("-" * 10,),
            ("-" * 15,),
            ("-" * 5,)
        ]
        
        assert mock_print.call_count == 3
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls


class TestPrintSectionHeader:
    """100% покрытие функции print_section_header"""

    @patch('builtins.print')
    def test_print_section_header_default_width(self, mock_print: Any) -> None:
        """Покрытие: заголовок секции с шириной по умолчанию"""
        print_section_header("Test Header")
        
        expected_calls = [
            ("=" * 50,),
            ("Test Header",),
            ("=" * 50,)
        ]
        
        assert mock_print.call_count == 3
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

    @patch('builtins.print')
    def test_print_section_header_custom_width(self, mock_print: Any) -> None:
        """Покрытие: заголовок секции с заданной шириной"""
        print_section_header("Custom Header", 30)
        
        expected_calls = [
            ("=" * 30,),
            ("Custom Header",),
            ("=" * 30,)
        ]
        
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

    @patch('builtins.print')
    def test_print_section_header_empty_title(self, mock_print: Any) -> None:
        """Покрытие: заголовок секции с пустым заголовком"""
        print_section_header("", 25)
        
        expected_calls = [
            ("=" * 25,),
            ("",),
            ("=" * 25,)
        ]
        
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

    @patch('builtins.print')
    def test_print_section_header_long_title(self, mock_print: Any) -> None:
        """Покрытие: заголовок секции с длинным заголовком"""
        long_title = "Very Long Section Header That Exceeds Normal Width"
        print_section_header(long_title, 20)
        
        expected_calls = [
            ("=" * 20,),
            (long_title,),
            ("=" * 20,)
        ]
        
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

    @patch('builtins.print')
    def test_print_section_header_unicode_title(self, mock_print: Any) -> None:
        """Покрытие: заголовок секции с Unicode символами"""
        unicode_title = "Заголовок Секции с Unicode 🚀"
        print_section_header(unicode_title, 35)
        
        expected_calls = [
            ("=" * 35,),
            (unicode_title,),
            ("=" * 35,)
        ]
        
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

    @patch('builtins.print')
    def test_print_section_header_zero_width(self, mock_print: Any) -> None:
        """Покрытие: заголовок секции с нулевой шириной"""
        print_section_header("Test", 0)
        
        expected_calls = [
            ("",),
            ("Test",),
            ("",)
        ]
        
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls


class TestIntegrationScenarios:
    """Интеграционные тесты для проверки совместной работы методов"""

    def test_full_menu_lifecycle(self) -> None:
        """Покрытие: полный жизненный цикл меню"""
        menu = MenuManager()
        
        # Добавляем пункты
        menu.add_menu_item("1", "First", lambda: "first")
        menu.add_menu_item("2", "Second", lambda: "second")
        menu.add_menu_item("3", "Third", lambda: "third")
        
        # Проверяем добавление
        assert len(menu.get_menu_items()) == 3
        
        # Проверяем обработчики
        assert menu.get_handler("1")() == "first"
        assert menu.get_handler("2")() == "second"
        
        # Удаляем пункт
        assert menu.remove_menu_item("2") is True
        assert len(menu.get_menu_items()) == 2
        assert menu.get_handler("2") is None
        
        # Добавляем новый пункт в позицию
        menu.add_menu_item("1.5", "Between", lambda: "between", position=1)
        items = menu.get_menu_items()
        assert items[1] == ("1.5", "Between")

    @patch('builtins.print')
    @patch('src.utils.menu_manager.print_menu_separator')
    def test_menu_display_integration(self, mock_separator: Any, mock_print: Any) -> None:
        """Покрытие: интеграция отображения меню"""
        menu = MenuManager()
        
        # Создаем меню с различными типами пунктов
        menu.add_menu_item("a", "Alpha", lambda: None)
        menu.add_menu_item("b", "Beta", None)
        menu.add_menu_item("c", "Gamma", lambda x: x)
        
        menu.display_menu()
        
        # Проверяем, что все элементы отображены
        print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("a. Alpha" in call for call in print_calls)
        assert any("b. Beta" in call for call in print_calls)
        assert any("c. Gamma" in call for call in print_calls)
        assert any("0. Выход" in call for call in print_calls)

    def test_create_main_menu_integration(self) -> None:
        """Покрытие: интеграция создания главного меню"""
        menu = create_main_menu()
        
        # Проверяем, что можем работать с созданным меню
        original_count = len(menu.get_menu_items())
        
        # Добавляем новый пункт
        menu.add_menu_item("11", "Custom Item", lambda: "custom")
        assert len(menu.get_menu_items()) == original_count + 1
        
        # Удаляем существующий пункт
        assert menu.remove_menu_item("5") is True
        assert len(menu.get_menu_items()) == original_count
        
        # Проверяем, что обработчик работает
        assert menu.get_handler("11")() == "custom"

    @patch('builtins.print')
    def test_print_functions_integration(self, mock_print: Any) -> None:
        """Покрытие: интеграция функций печати"""
        # Печатаем заголовок секции
        print_section_header("Test Section", 30)
        
        # Печатаем разделитель
        print_menu_separator(30)
        
        # Проверяем правильную последовательность вызовов
        expected_calls = [
            ("=" * 30,),
            ("Test Section",),
            ("=" * 30,),
            ("-" * 30,)
        ]
        
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

    def test_menu_edge_cases_integration(self) -> None:
        """Покрытие: граничные случаи работы с меню"""
        menu = MenuManager()
        
        # Пустое меню
        assert menu.get_menu_items() == []
        assert menu.get_handler("any") is None
        assert menu.remove_menu_item("any") is False
        
        # Добавление и удаление одного и того же пункта
        menu.add_menu_item("test", "Test", lambda: None)
        assert menu.remove_menu_item("test") is True
        assert menu.remove_menu_item("test") is False  # Второе удаление
        
        # Добавление пункта с тем же ключом
        menu.add_menu_item("dup", "Original", lambda: "original")
        menu.add_menu_item("dup", "Duplicate", lambda: "duplicate")
        
        # Проверяем, что значение заменилось
        handler = menu.get_handler("dup")
        assert handler() == "duplicate"


class TestErrorHandlingAndEdgeCases:
    """Тесты для обработки ошибок и граничных случаев"""

    def test_menu_with_complex_handlers(self) -> None:
        """Покрытие: меню со сложными обработчиками"""
        menu = MenuManager()
        
        # Различные типы обработчиков
        def complex_handler(x, y=5):
            return x + y
        
        class HandlerClass:
            def __call__(self):
                return "class_handler"
        
        menu.add_menu_item("1", "Function", complex_handler)
        menu.add_menu_item("2", "Lambda", lambda: "lambda_result")
        menu.add_menu_item("3", "Class", HandlerClass())
        menu.add_menu_item("4", "None", None)
        
        # Проверяем все типы
        assert callable(menu.get_handler("1"))
        assert menu.get_handler("2")() == "lambda_result"
        assert menu.get_handler("3")() == "class_handler"
        assert menu.get_handler("4") is None

    def test_menu_order_consistency(self) -> None:
        """Покрытие: консистентность порядка меню"""
        menu = MenuManager()
        
        # Добавляем элементы в случайном порядке с позициями
        menu.add_menu_item("z", "Last", None)
        menu.add_menu_item("a", "First", None, position=0)
        menu.add_menu_item("m", "Middle", None, position=1)
        
        items = menu.get_menu_items()
        keys = [item[0] for item in items]
        
        assert keys == ["a", "m", "z"]

    def test_menu_with_special_characters(self) -> None:
        """Покрытие: меню со специальными символами"""
        menu = MenuManager()
        
        special_items = [
            ("@", "Символ @", None),
            ("🚀", "Ракета", None),
            ("key with spaces", "Ключ с пробелами", None),
            ("", "Пустой ключ", None),
        ]
        
        for key, title, handler in special_items:
            menu.add_menu_item(key, title, handler)
        
        items = menu.get_menu_items()
        assert len(items) == 4
        
        # Проверяем, что все добавились
        keys = [item[0] for item in items]
        assert "@" in keys
        assert "🚀" in keys
        assert "key with spaces" in keys
        assert "" in keys