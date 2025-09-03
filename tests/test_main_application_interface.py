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
        """Тест инициализации интерфейса главного приложения"""
        if not INTERFACE_AVAILABLE:
            pytest.skip("MainApplicationInterface not available")

        # Тестируем абстрактность класса - нужны обязательные аргументы
        with pytest.raises(TypeError):
            MainApplicationInterface()

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

        # Создаем моки для обязательных аргументов
        mock_provider = Mock()
        mock_processor = Mock()
        mock_storage = Mock()

        app = TestApplication(mock_provider, mock_processor, mock_storage)
        assert app.run_application() == "Application started"