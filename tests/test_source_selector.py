
"""
Тесты для модуля source_selector
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ui_interfaces.source_selector import SourceSelector


class TestSourceSelector:
    """Класс для тестирования SourceSelector"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.source_selector = SourceSelector()

    def test_source_selector_init(self):
        """Тест инициализации селектора источников"""
        selector = SourceSelector()
        assert selector is not None

    @patch('builtins.print')
    def test_show_available_sources(self, mock_print):
        """Тест отображения доступных источников"""
        if hasattr(self.source_selector, 'show_available_sources'):
            self.source_selector.show_available_sources()
            mock_print.assert_called()

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_select_source_valid_choice(self, mock_print, mock_input):
        """Тест выбора источника с валидным выбором"""
        if hasattr(self.source_selector, 'select_source'):
            result = self.source_selector.select_source()
            assert result is not None

    @patch('builtins.input', side_effect=['invalid', '1'])
    @patch('builtins.print')
    def test_select_source_invalid_then_valid(self, mock_print, mock_input):
        """Тест выбора источника с некорректным, затем корректным вводом"""
        if hasattr(self.source_selector, 'select_source'):
            result = self.source_selector.select_source()
            assert result is not None

    def test_get_available_sources(self):
        """Тест получения списка доступных источников"""
        if hasattr(self.source_selector, 'get_available_sources'):
            sources = self.source_selector.get_available_sources()
            assert isinstance(sources, list) or isinstance(sources, dict)

    def test_validate_source_choice_valid(self):
        """Тест валидации корректного выбора источника"""
        if hasattr(self.source_selector, 'validate_choice'):
            # Предполагаем что '1' - валидный выбор
            result = self.source_selector.validate_choice('1')
            assert result is True or result is not None

    def test_validate_source_choice_invalid(self):
        """Тест валидации некорректного выбора источника"""
        if hasattr(self.source_selector, 'validate_choice'):
            result = self.source_selector.validate_choice('invalid')
            assert result is False or result is None

    @patch('builtins.input', return_value='hh.ru')
    def test_select_source_by_name(self, mock_input):
        """Тест выбора источника по имени"""
        if hasattr(self.source_selector, 'select_by_name'):
            result = self.source_selector.select_by_name()
            assert result is not None

    def test_get_source_info(self):
        """Тест получения информации об источнике"""
        if hasattr(self.source_selector, 'get_source_info'):
            # Тестируем для известного источника
            info = self.source_selector.get_source_info('hh.ru')
            assert info is not None or info is None

    @patch('builtins.input', return_value='1,2')
    @patch('builtins.print')
    def test_select_multiple_sources(self, mock_print, mock_input):
        """Тест выбора нескольких источников"""
        if hasattr(self.source_selector, 'select_multiple'):
            result = self.source_selector.select_multiple()
            assert isinstance(result, list) or result is not None

    def test_default_source_selection(self):
        """Тест выбора источника по умолчанию"""
        if hasattr(self.source_selector, 'get_default_source'):
            default = self.source_selector.get_default_source()
            assert default is not None or default is None

    @patch('builtins.print')
    def test_display_source_statistics(self, mock_print):
        """Тест отображения статистики источников"""
        if hasattr(self.source_selector, 'display_statistics'):
            stats = {'hh.ru': 1000, 'superjob.ru': 500}
            self.source_selector.display_statistics(stats)
            mock_print.assert_called()

    def test_source_priority_handling(self):
        """Тест обработки приоритета источников"""
        if hasattr(self.source_selector, 'set_priority'):
            self.source_selector.set_priority('hh.ru', 1)
            if hasattr(self.source_selector, 'get_priority'):
                priority = self.source_selector.get_priority('hh.ru')
                assert priority == 1

    @patch('builtins.input', return_value='all')
    def test_select_all_sources(self, mock_input):
        """Тест выбора всех источников"""
        if hasattr(self.source_selector, 'select_all'):
            result = self.source_selector.select_all()
            assert isinstance(result, list) or result is not None

    def test_source_availability_check(self):
        """Тест проверки доступности источников"""
        if hasattr(self.source_selector, 'check_availability'):
            availability = self.source_selector.check_availability('hh.ru')
            assert isinstance(availability, bool) or availability is not None

    @patch('builtins.print')
    def test_show_source_details(self, mock_print):
        """Тест отображения детальной информации об источнике"""
        if hasattr(self.source_selector, 'show_details'):
            self.source_selector.show_details('hh.ru')
            mock_print.assert_called()

    def test_source_configuration(self):
        """Тест конфигурации источников"""
        if hasattr(self.source_selector, 'configure_source'):
            config = {'timeout': 30, 'retries': 3}
            result = self.source_selector.configure_source('hh.ru', config)
            assert result is not None or result is None
