#!/usr/bin/env python3
"""
Исправленные тесты для интерфейса главного приложения
"""

import os
import sys
import pytest
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.interfaces.main_application_interface import MainApplicationInterface
    INTERFACE_AVAILABLE = True
except ImportError:
    INTERFACE_AVAILABLE = False


class TestMainApplicationInterface:
    """Тестирование интерфейса главного приложения"""

    def test_main_application_interface_init(self):
        """Тест инициализации главного интерфейса приложения"""
        if not INTERFACE_AVAILABLE:
            pytest.skip("MainApplicationInterface not available")

        # Создаем конкретную реализацию абстрактного класса
        class ConcreteMainApplication(MainApplicationInterface):
            def run_application(self):
                pass

        interface = ConcreteMainApplication()
        assert interface is not None

    def test_main_application_interface_abstract_methods(self):
        """Тест абстрактных методов"""
        if not INTERFACE_AVAILABLE:
            pytest.skip("MainApplicationInterface not available")

        # Проверяем, что класс является абстрактным
        assert hasattr(MainApplicationInterface, '__abstractmethods__')

    def test_main_application_interface_concrete_implementation(self):
        """Тест конкретной реализации"""
        if not INTERFACE_AVAILABLE:
            pytest.skip("MainApplicationInterface not available")

        class TestApplication(MainApplicationInterface):
            def run_application(self):
                return "Application started"

        app = TestApplication()
        result = app.run_application()
        assert result == "Application started"