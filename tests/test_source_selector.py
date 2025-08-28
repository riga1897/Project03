
"""
Тесты для модуля SourceSelector
"""

import pytest
from unittest.mock import patch, Mock
from src.ui_interfaces.source_selector import SourceSelector


class TestSourceSelector:
    """Тесты для класса SourceSelector"""

    @pytest.fixture
    def source_selector(self):
        """Фикстура SourceSelector"""
        return SourceSelector()

    def test_source_selector_initialization(self, source_selector):
        """Тест инициализации SourceSelector"""
        assert source_selector is not None
        assert hasattr(source_selector, 'available_sources')

    @patch('builtins.input', return_value='1')
    def test_get_user_source_choice_single(self, mock_input, source_selector):
        """Тест выбора одного источника"""
        with patch('builtins.print'):
            sources = source_selector.get_user_source_choice()
            assert isinstance(sources, list)
            assert len(sources) > 0

    @patch('builtins.input', return_value='3')
    def test_get_user_source_choice_all(self, mock_input, source_selector):
        """Тест выбора всех источников"""
        with patch('builtins.print'):
            sources = source_selector.get_user_source_choice()
            assert isinstance(sources, list)

    @patch('builtins.input', return_value='0')
    def test_get_user_source_choice_exit(self, mock_input, source_selector):
        """Тест выхода из выбора источников"""
        with patch('builtins.print'):
            sources = source_selector.get_user_source_choice()
            assert sources is None or sources == []

    @patch('builtins.input', side_effect=['invalid', '1'])
    @patch('builtins.print')
    def test_get_user_source_choice_invalid_then_valid(self, mock_print, mock_input, source_selector):
        """Тест некорректного, затем корректного выбора"""
        sources = source_selector.get_user_source_choice()
        assert isinstance(sources, list)
        mock_print.assert_called()

    def test_display_sources_info(self, source_selector):
        """Тест отображения информации об источниках"""
        sources = ["hh.ru", "superjob.ru"]
        with patch('builtins.print') as mock_print:
            source_selector.display_sources_info(sources)
            mock_print.assert_called()

    def test_get_available_sources(self, source_selector):
        """Тест получения доступных источников"""
        sources = source_selector.get_available_sources()
        assert isinstance(sources, list)
        assert len(sources) > 0
        assert "hh.ru" in sources or "superjob.ru" in sources

    def test_validate_source_choice(self, source_selector):
        """Тест валидации выбора источника"""
        assert source_selector.validate_source_choice("1") is True
        assert source_selector.validate_source_choice("2") is True
        assert source_selector.validate_source_choice("3") is True
        assert source_selector.validate_source_choice("0") is True
        assert source_selector.validate_source_choice("invalid") is False
        assert source_selector.validate_source_choice("10") is False

    def test_get_source_name_by_choice(self, source_selector):
        """Тест получения имени источника по выбору"""
        # Предполагаем стандартную нумерацию
        source_name = source_selector.get_source_name_by_choice("1")
        assert source_name in ["hh.ru", "superjob.ru"]

    def test_is_source_available(self, source_selector):
        """Тест проверки доступности источника"""
        assert source_selector.is_source_available("hh.ru") is True
        assert source_selector.is_source_available("superjob.ru") is True
        assert source_selector.is_source_available("nonexistent.com") is False

    @patch('builtins.print')
    def test_display_source_menu(self, mock_print, source_selector):
        """Тест отображения меню источников"""
        source_selector.display_source_menu()
        mock_print.assert_called()
        # Проверяем, что меню содержит варианты выбора
        call_args_list = [str(call) for call in mock_print.call_args_list]
        menu_text = " ".join(call_args_list)
        assert "1" in menu_text or "hh" in menu_text.lower()
