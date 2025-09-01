
"""
Тесты для модуля базового форматирования
"""

import os
import sys
from unittest.mock import Mock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class BaseFormatter:
    """Базовый класс для форматирования данных"""
    
    def format_item(self, item: any, index: int = None) -> str:
        """
        Форматирование элемента
        
        Args:
            item: Элемент для форматирования
            index: Индекс элемента
            
        Returns:
            str: Отформатированная строка
        """
        if index is not None:
            return f"{index}. {str(item)}"
        return str(item)
    
    def format_list(self, items: list, start_index: int = 1) -> list:
        """
        Форматирование списка элементов
        
        Args:
            items: Список элементов
            start_index: Начальный индекс
            
        Returns:
            list: Список отформатированных строк
        """
        formatted = []
        for i, item in enumerate(items, start_index):
            formatted.append(self.format_item(item, i))
        return formatted
    
    def format_table_row(self, data: dict, columns: list) -> str:
        """
        Форматирование строки таблицы
        
        Args:
            data: Словарь с данными
            columns: Список колонок
            
        Returns:
            str: Отформатированная строка
        """
        values = []
        for col in columns:
            value = data.get(col, "")
            values.append(str(value))
        return " | ".join(values)


class TestBaseFormatter:
    """Тесты для базового форматтера"""
    
    @pytest.fixture
    def formatter(self):
        """Фикстура форматтера"""
        return BaseFormatter()
    
    def test_format_item_with_index(self, formatter):
        """Тест форматирования элемента с индексом"""
        result = formatter.format_item("test", 1)
        assert result == "1. test"
    
    def test_format_item_without_index(self, formatter):
        """Тест форматирования элемента без индекса"""
        result = formatter.format_item("test")
        assert result == "test"
    
    def test_format_item_none_index(self, formatter):
        """Тест форматирования элемента с None индексом"""
        result = formatter.format_item("test", None)
        assert result == "test"
    
    def test_format_list_basic(self, formatter):
        """Тест базового форматирования списка"""
        items = ["item1", "item2", "item3"]
        result = formatter.format_list(items)
        expected = ["1. item1", "2. item2", "3. item3"]
        assert result == expected
    
    def test_format_list_custom_start_index(self, formatter):
        """Тест форматирования списка с кастомным начальным индексом"""
        items = ["item1", "item2"]
        result = formatter.format_list(items, start_index=5)
        expected = ["5. item1", "6. item2"]
        assert result == expected
    
    def test_format_list_empty(self, formatter):
        """Тест форматирования пустого списка"""
        result = formatter.format_list([])
        assert result == []
    
    def test_format_table_row_basic(self, formatter):
        """Тест форматирования строки таблицы"""
        data = {"name": "Test", "age": 25, "city": "Moscow"}
        columns = ["name", "age", "city"]
        result = formatter.format_table_row(data, columns)
        assert result == "Test | 25 | Moscow"
    
    def test_format_table_row_missing_column(self, formatter):
        """Тест форматирования строки таблицы с отсутствующей колонкой"""
        data = {"name": "Test", "age": 25}
        columns = ["name", "age", "city"]
        result = formatter.format_table_row(data, columns)
        assert result == "Test | 25 | "
    
    def test_format_table_row_empty_columns(self, formatter):
        """Тест форматирования строки таблицы с пустыми колонками"""
        data = {"name": "Test"}
        columns = []
        result = formatter.format_table_row(data, columns)
        assert result == ""
    
    def test_format_item_complex_object(self, formatter):
        """Тест форматирования сложного объекта"""
        obj = {"key": "value", "nested": {"inner": "data"}}
        result = formatter.format_item(obj, 1)
        assert "1." in result
        assert str(obj) in result
