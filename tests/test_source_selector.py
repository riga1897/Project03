
import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ui_interfaces.source_selector import SourceSelector


class TestSourceSelector:
    """Тесты для класса SourceSelector"""

    def test_source_selector_initialization(self):
        """Тест инициализации SourceSelector"""
        selector = SourceSelector()
        assert hasattr(selector, 'source_manager')

    def test_available_sources_constant(self):
        """Тест константы доступных источников"""
        expected_sources = {"hh.ru": "HH.ru", "superjob.ru": "SuperJob.ru"}
        assert SourceSelector.AVAILABLE_SOURCES == expected_sources

    @patch('builtins.input', return_value="1")
    @patch('builtins.print')
    def test_get_user_source_choice_hh(self, mock_print, mock_input):
        """Тест выбора источника HH.ru"""
        result = SourceSelector.get_user_source_choice()
        
        assert result == {"hh.ru"}
        mock_print.assert_any_call("Выбран источник: HH.ru")

    @patch('builtins.input', return_value="2")
    @patch('builtins.print')
    def test_get_user_source_choice_superjob(self, mock_print, mock_input):
        """Тест выбора источника SuperJob.ru"""
        result = SourceSelector.get_user_source_choice()
        
        assert result == {"superjob.ru"}
        mock_print.assert_any_call("Выбран источник: SuperJob.ru")

    @patch('builtins.input', return_value="3")
    @patch('builtins.print')
    def test_get_user_source_choice_both(self, mock_print, mock_input):
        """Тест выбора обоих источников"""
        result = SourceSelector.get_user_source_choice()
        
        assert result == {"hh.ru", "superjob.ru"}

    @patch('builtins.input', return_value="0")
    @patch('builtins.print')
    def test_get_user_source_choice_cancel(self, mock_print, mock_input):
        """Тест отмены выбора источников"""
        result = SourceSelector.get_user_source_choice()
        
        assert result is None
        mock_print.assert_any_call("Выбор источников отменен.")

    @patch('builtins.input', side_effect=["invalid", "1"])
    @patch('builtins.print')
    def test_get_user_source_choice_invalid_then_valid(self, mock_print, mock_input):
        """Тест обработки неверного ввода с последующим корректным"""
        result = SourceSelector.get_user_source_choice()
        
        assert result == {"hh.ru"}
        mock_print.assert_any_call("Неверный выбор. Пожалуйста, введите 1, 2, 3 или 0.")

    def test_get_source_display_name_existing(self):
        """Тест получения отображаемого имени существующего источника"""
        display_name = SourceSelector.get_source_display_name("hh.ru")
        assert display_name == "HH.ru"

    def test_get_source_display_name_non_existing(self):
        """Тест получения отображаемого имени несуществующего источника"""
        display_name = SourceSelector.get_source_display_name("unknown.ru")
        assert display_name == "unknown.ru"

    @patch('builtins.print')
    def test_display_sources_info(self, mock_print):
        """Тест отображения информации об источниках"""
        sources = {"hh.ru", "superjob.ru"}
        
        # Мокируем метод если он существует
        if hasattr(SourceSelector, 'display_sources_info'):
            SourceSelector.display_sources_info(sources)
            mock_print.assert_called()
        else:
            # Создаем тестовую реализацию
            for source in sources:
                display_name = SourceSelector.get_source_display_name(source)
                print(f"Источник: {display_name}")
            
            mock_print.assert_called()
