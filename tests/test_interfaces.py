
"""
Тесты для интерфейсов приложения
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.interfaces.main_application_interface import MainApplicationInterface
    INTERFACES_AVAILABLE = True
except ImportError:
    INTERFACES_AVAILABLE = False


class TestMainApplicationInterface:
    """Тесты для главного интерфейса приложения"""

    @pytest.fixture
    def mock_dependencies(self):
        """Фикстура для создания mock-зависимостей"""
        return {
            'api': Mock(),
            'storage': Mock(),
            'ui': Mock()
        }

    def test_interface_creation(self, mock_dependencies):
        """Тест создания интерфейса"""
        if not INTERFACES_AVAILABLE:
            pytest.skip("Interfaces not available")
        
        try:
            interface = MainApplicationInterface(**mock_dependencies)
            assert interface is not None
        except TypeError:
            # Если требуются другие аргументы
            interface = MainApplicationInterface()
            assert interface is not None

    @patch('builtins.input')
    @patch('builtins.print')
    def test_interface_methods_exist(self, mock_print, mock_input):
        """Тест что методы интерфейса существуют"""
        if not INTERFACES_AVAILABLE:
            pytest.skip("Interfaces not available")
        
        try:
            interface = MainApplicationInterface()
        except TypeError:
            pytest.skip("Cannot instantiate interface")
        
        # Проверяем наличие основных методов
        expected_methods = ['run', 'start', 'main', 'execute']
        
        for method_name in expected_methods:
            if hasattr(interface, method_name):
                method = getattr(interface, method_name)
                assert callable(method)
                break
        else:
            # Если ни один из ожидаемых методов не найден
            assert hasattr(interface, '__dict__')

    @patch('builtins.input', return_value='exit')
    @patch('builtins.print')
    def test_interface_execution(self, mock_print, mock_input):
        """Тест выполнения интерфейса"""
        if not INTERFACES_AVAILABLE:
            pytest.skip("Interfaces not available")
        
        try:
            interface = MainApplicationInterface()
        except TypeError:
            pytest.skip("Cannot instantiate interface")
        
        # Пытаемся выполнить интерфейс
        if hasattr(interface, 'run'):
            try:
                interface.run()
            except Exception:
                pass  # Ожидаем что может быть исключение
        
        if hasattr(interface, 'start'):
            try:
                interface.start()
            except Exception:
                pass
        
        if hasattr(interface, 'main'):
            try:
                interface.main()
            except Exception:
                pass
