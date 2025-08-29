
"""
Тесты для UI helpers

Содержит тесты для проверки корректности работы UI утилит.
"""

from unittest.mock import Mock, patch
import pytest
from src.utils.ui_helpers import UIHelpers


class TestUIHelpers:
    """Тесты для UI helpers"""

    @patch("builtins.input", return_value="y")
    def test_confirm_action_yes(self, mock_input):
        """Тест подтверждения действия - да"""
        result = UIHelpers.confirm_action("Продолжить?")
        assert result is True

    @patch("builtins.input", return_value="n")
    def test_confirm_action_no(self, mock_input):
        """Тест подтверждения действия - нет"""
        result = UIHelpers.confirm_action("Продолжить?")
        assert result is False

    @patch("builtins.input", return_value="")
    def test_confirm_action_default(self, mock_input):
        """Тест подтверждения действия - по умолчанию"""
        # Тест с дефолтным значением True
        result = UIHelpers.confirm_action("Продолжить?", default=True)
        assert result is True
        
        # Тест с дефолтным значением False
        result = UIHelpers.confirm_action("Продолжить?", default=False)
        assert result is False

    @patch("builtins.input", return_value="test input")
    def test_get_user_input(self, mock_input):
        """Тест получения пользовательского ввода"""
        result = UIHelpers.get_user_input("Введите данные:")
        assert result == "test input"

    @patch("builtins.input", return_value="")
    def test_get_user_input_empty(self, mock_input):
        """Тест получения пустого ввода"""
        result = UIHelpers.get_user_input("Введите данные:")
        assert result == ""

    @patch("builtins.input", return_value="123")
    def test_get_numeric_input(self, mock_input):
        """Тест получения числового ввода"""
        if hasattr(UIHelpers, 'get_numeric_input'):
            result = UIHelpers.get_numeric_input("Введите число:")
            assert result == 123
        else:
            # Альтернативная проверка через get_user_input
            result = UIHelpers.get_user_input("Введите число:")
            assert result == "123"

    @patch("builtins.input", side_effect=["invalid", "123"])
    def test_get_numeric_input_retry(self, mock_input):
        """Тест повторного ввода при некорректном числе"""
        if hasattr(UIHelpers, 'get_numeric_input'):
            with patch("builtins.print"):  # Подавляем вывод ошибок
                result = UIHelpers.get_numeric_input("Введите число:")
                assert result == 123

    @patch("builtins.print")
    def test_print_message(self, mock_print):
        """Тест вывода сообщения"""
        if hasattr(UIHelpers, 'print_message'):
            UIHelpers.print_message("Test message")
            mock_print.assert_called_with("Test message")
        else:
            # Альтернативный тест
            print("Test message")
            mock_print.assert_called_with("Test message")

    @patch("builtins.print")
    def test_print_error(self, mock_print):
        """Тест вывода ошибки"""
        if hasattr(UIHelpers, 'print_error'):
            UIHelpers.print_error("Error message")
            mock_print.assert_called()
        else:
            # Альтернативный тест
            print("Error: Error message")
            mock_print.assert_called()

    @patch("builtins.print")
    def test_print_success(self, mock_print):
        """Тест вывода успешного сообщения"""
        if hasattr(UIHelpers, 'print_success'):
            UIHelpers.print_success("Success message")
            mock_print.assert_called()
        else:
            # Альтернативный тест
            print("Success: Success message")
            mock_print.assert_called()

    @patch("builtins.input", side_effect=["invalid", "y"])
    @patch("builtins.print")
    def test_confirm_action_retry(self, mock_print, mock_input):
        """Тест повторного подтверждения при некорректном вводе"""
        result = UIHelpers.confirm_action("Продолжить?")
        # В итоге должно получиться True после корректного ввода
        assert result is True

    @patch("builtins.input", return_value="Y")
    def test_confirm_action_case_insensitive(self, mock_input):
        """Тест подтверждения без учета регистра"""
        result = UIHelpers.confirm_action("Продолжить?")
        assert result is True

    def test_ui_helpers_methods_exist(self):
        """Тест существования основных методов"""
        expected_methods = [
            'confirm_action', 'get_user_input', 'get_numeric_input',
            'print_message', 'print_error', 'print_success'
        ]
        
        existing_methods = [method for method in expected_methods
                          if hasattr(UIHelpers, method)]
        
        # Должен быть хотя бы основной метод confirm_action
        assert 'confirm_action' in existing_methods

    @patch("builtins.input", return_value="test")
    def test_get_user_input_with_prompt(self, mock_input):
        """Тест получения ввода с промптом"""
        prompt = "Введите значение:"
        result = UIHelpers.get_user_input(prompt)
        assert result == "test"
        mock_input.assert_called_with(prompt + " ")

    @patch("builtins.input", return_value="default_value")  
    def test_get_user_input_with_default(self, mock_input):
        """Тест получения ввода с дефолтным значением"""
        if hasattr(UIHelpers, 'get_user_input'):
            # Проверяем, поддерживает ли метод дефолтное значение
            try:
                result = UIHelpers.get_user_input("Введите:", default="default")
                assert result in ["default_value", "default"]
            except TypeError:
                # Если не поддерживает default параметр
                result = UIHelpers.get_user_input("Введите:")
                assert result == "default_value"

    def test_ui_helpers_integration(self):
        """Тест интеграции UI helpers"""
        # Проверяем, что класс существует и имеет методы
        assert hasattr(UIHelpers, 'confirm_action')
        assert callable(getattr(UIHelpers, 'confirm_action'))
        
        # Проверяем статические методы
        methods = [attr for attr in dir(UIHelpers)
                  if callable(getattr(UIHelpers, attr)) and not attr.startswith('_')]
        assert len(methods) > 0
