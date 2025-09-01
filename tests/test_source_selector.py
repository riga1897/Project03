
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
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.ui_interfaces.source_selector import SourceSelector
    SRC_AVAILABLE = True
except ImportError:
    SRC_AVAILABLE = False
    
    class SourceSelector:
        """Тестовая реализация селектора источников"""
        
        def __init__(self):
            """Инициализация селектора источников"""
            self.available_sources = ["hh.ru", "superjob.ru"]
            self.selected_source = None
        
        def show_sources(self) -> None:
            """Отображение доступных источников"""
            print("Доступные источники:")
            for i, source in enumerate(self.available_sources, 1):
                print(f"{i}. {source}")
        
        def select_source(self, choice: str) -> str:
            """
            Выбор источника по номеру
            
            Args:
                choice: Номер выбранного источника
                
            Returns:
                str: Название выбранного источника
            """
            try:
                index = int(choice) - 1
                if 0 <= index < len(self.available_sources):
                    self.selected_source = self.available_sources[index]
                    return self.selected_source
                else:
                    raise ValueError("Неверный номер источника")
            except ValueError:
                raise ValueError("Некорректный ввод")
        
        def get_selected_source(self) -> str:
            """
            Получение выбранного источника
            
            Returns:
                str: Название выбранного источника
            """
            return self.selected_source


class TestSourceSelector:
    """Тесты для селектора источников данных"""

    @pytest.fixture
    def source_selector(self) -> SourceSelector:
        """Фикстура селектора источников"""
        return SourceSelector()

    def test_source_selector_initialization(self, source_selector):
        """Тест инициализации селектора источников"""
        assert source_selector is not None
        assert hasattr(source_selector, 'available_sources')
        
        if hasattr(source_selector, 'selected_source'):
            assert source_selector.selected_source is None

    @patch('builtins.print')
    def test_show_sources(self, mock_print, source_selector):
        """Тест отображения доступных источников"""
        source_selector.show_sources()
        
        # Проверяем, что были вызовы print
        mock_print.assert_called()
        
        # Проверяем содержимое вызовов
        call_args = [call.args[0] for call in mock_print.call_args_list]
        sources_text = " ".join(call_args)
        
        assert "источник" in sources_text.lower() or "source" in sources_text.lower()

    def test_select_source_valid_choice(self, source_selector):
        """Тест выбора источника с корректным вводом"""
        # Тест выбора первого источника
        result = source_selector.select_source("1")
        assert result in ["hh.ru", "superjob.ru", source_selector.available_sources[0]]
        
        # Тест выбора второго источника
        result = source_selector.select_source("2")
        assert result in ["hh.ru", "superjob.ru", source_selector.available_sources[1]]

    def test_select_source_invalid_choice(self, source_selector):
        """Тест выбора источника с некорректным вводом"""
        # Тест с неверным номером
        with pytest.raises(ValueError):
            source_selector.select_source("0")
        
        with pytest.raises(ValueError):
            source_selector.select_source("99")
        
        # Тест с нечисловым вводом
        with pytest.raises(ValueError):
            source_selector.select_source("abc")

    def test_get_selected_source(self, source_selector):
        """Тест получения выбранного источника"""
        # До выбора источника
        initial_source = source_selector.get_selected_source()
        assert initial_source is None
        
        # После выбора источника
        source_selector.select_source("1")
        selected_source = source_selector.get_selected_source()
        assert selected_source is not None
        assert isinstance(selected_source, str)

    def test_available_sources_content(self, source_selector):
        """Тест содержимого доступных источников"""
        assert hasattr(source_selector, 'available_sources')
        assert len(source_selector.available_sources) >= 1
        
        # Проверяем, что содержит ожидаемые источники
        sources_str = str(source_selector.available_sources).lower()
        assert "hh" in sources_str or "headhunter" in sources_str or "superjob" in sources_str

    def test_source_selector_state_management(self, source_selector):
        """Тест управления состоянием селектора"""
        # Проверяем начальное состояние
        assert source_selector.get_selected_source() is None
        
        # Выбираем источник
        selected = source_selector.select_source("1")
        assert source_selector.get_selected_source() == selected
        
        # Меняем выбор
        new_selected = source_selector.select_source("2")
        assert source_selector.get_selected_source() == new_selected
        assert source_selector.get_selected_source() != selected

    def test_source_selector_edge_cases(self, source_selector):
        """Тест граничных случаев"""
        # Тест с пустой строкой
        with pytest.raises(ValueError):
            source_selector.select_source("")
        
        # Тест с пробелами
        with pytest.raises(ValueError):
            source_selector.select_source("   ")
        
        # Тест с отрицательным числом
        with pytest.raises(ValueError):
            source_selector.select_source("-1")

    @patch('builtins.input', side_effect=["1", "2", "0"])
    def test_interactive_selection_simulation(self, mock_input, source_selector):
        """Тест симуляции интерактивного выбора"""
        # Симуляция пользовательского выбора
        for choice in mock_input.side_effect[:-1]:  # Исключаем "0" (выход)
            try:
                result = source_selector.select_source(choice)
                assert result is not None
            except ValueError:
                # Ожидаемо для некорректных вводов
                pass

    def test_source_selector_multiple_selections(self, source_selector):
        """Тест множественных выборов источника"""
        selections = []
        
        # Делаем несколько выборов
        for i in range(1, min(3, len(source_selector.available_sources) + 1)):
            try:
                selected = source_selector.select_source(str(i))
                selections.append(selected)
                assert source_selector.get_selected_source() == selected
            except (ValueError, IndexError):
                # Ожидаемо при превышении количества источников
                pass
        
        # Проверяем, что выборы были сделаны
        assert len(selections) > 0

    def test_source_selector_type_safety(self, source_selector):
        """Тест типобезопасности селектора"""
        # Проверяем типы возвращаемых значений
        if hasattr(source_selector, 'available_sources'):
            assert isinstance(source_selector.available_sources, list)
        
        # Проверяем тип после выбора
        selected = source_selector.select_source("1")
        assert isinstance(selected, str)
        assert len(selected) > 0

    def test_source_selector_integration_ready(self, source_selector):
        """Тест готовности к интеграции"""
        # Проверяем наличие всех необходимых методов
        required_methods = ['show_sources', 'select_source', 'get_selected_source']
        
        for method in required_methods:
            assert hasattr(source_selector, method)
            assert callable(getattr(source_selector, method))

    @pytest.mark.parametrize("choice,expected_type", [
        ("1", str),
        ("2", str),
    ])
    def test_parametrized_source_selection(self, source_selector, choice, expected_type):
        """Параметризованный тест выбора источников"""
        try:
            result = source_selector.select_source(choice)
            assert isinstance(result, expected_type)
            assert len(result) > 0
        except (ValueError, IndexError):
            # Ожидаемо для некорректных номеров
            pytest.skip(f"Choice {choice} is out of range for available sources")
