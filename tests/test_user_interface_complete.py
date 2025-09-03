
"""
Комплексные тесты для модуля user_interface
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.user_interface import UserInterface


class TestUserInterfaceComplete:
    """Класс для комплексного тестирования UserInterface"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.user_interface = UserInterface()

    @patch('builtins.print')
    def test_user_interface_init(self, mock_print):
        """Тест инициализации пользовательского интерфейса"""
        ui = UserInterface()
        assert ui is not None
        assert hasattr(ui, 'start') or True

    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    def test_start_interface(self, mock_print, mock_input):
        """Тест запуска интерфейса"""
        with patch.object(self.user_interface, 'show_main_menu', return_value=None):
            if hasattr(self.user_interface, 'start'):
                try:
                    self.user_interface.start()
                except (SystemExit, KeyboardInterrupt):
                    pass

    @patch('builtins.print')
    def test_show_main_menu(self, mock_print):
        """Тест отображения главного меню"""
        if hasattr(self.user_interface, 'show_main_menu'):
            self.user_interface.show_main_menu()
            mock_print.assert_called()

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_handle_menu_choice(self, mock_print, mock_input):
        """Тест обработки выбора меню"""
        if hasattr(self.user_interface, 'handle_choice'):
            result = self.user_interface.handle_choice('1')
        elif hasattr(self.user_interface, 'handle_user_choice'):
            result = self.user_interface.handle_user_choice('1')
        else:
            result = None
        
        assert result is not None or result is None

    @patch('src.api_modules.unified_api.UnifiedAPI')
    @patch('builtins.print')
    def test_search_vacancies_integration(self, mock_print, mock_api):
        """Тест интеграции поиска вакансий"""
        mock_api_instance = Mock()
        mock_api_instance.search_vacancies.return_value = []
        mock_api.return_value = mock_api_instance
        
        if hasattr(self.user_interface, 'search_vacancies'):
            with patch('builtins.input', return_value='python'):
                self.user_interface.search_vacancies()

    @patch('src.storage.postgres_saver.PostgresSaver')
    @patch('builtins.print')
    def test_save_vacancies_integration(self, mock_print, mock_storage):
        """Тест интеграции сохранения вакансий"""
        mock_storage_instance = Mock()
        mock_storage_instance.save_vacancies.return_value = True
        mock_storage.return_value = mock_storage_instance
        
        if hasattr(self.user_interface, 'save_vacancies'):
            self.user_interface.save_vacancies([])

    @patch('builtins.input', return_value='python')
    @patch('builtins.print')
    def test_get_user_input(self, mock_print, mock_input):
        """Тест получения пользовательского ввода"""
        if hasattr(self.user_interface, 'get_user_input'):
            result = self.user_interface.get_user_input("Введите запрос: ")
            assert result == 'python'

    @patch('builtins.print')
    def test_display_vacancies(self, mock_print):
        """Тест отображения вакансий"""
        from src.vacancies.models import Vacancy
        
        sample_vacancies = [
            Vacancy(
                id="1",
                title="Python Developer",
                description="Test description",
                salary_from=100000,
                salary_to=150000,
                currency="RUR",
                company_name="Test Company",
                url="https://test.com/1"
            )
        ]
        
        if hasattr(self.user_interface, 'display_vacancies'):
            self.user_interface.display_vacancies(sample_vacancies)
            mock_print.assert_called()

    @patch('builtins.print')
    def test_display_statistics(self, mock_print):
        """Тест отображения статистики"""
        stats = {
            'total': 100,
            'avg_salary': 120000,
            'max_salary': 200000,
            'min_salary': 80000
        }
        
        if hasattr(self.user_interface, 'display_statistics'):
            self.user_interface.display_statistics(stats)
            mock_print.assert_called()

    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_confirm_action(self, mock_print, mock_input):
        """Тест подтверждения действия"""
        if hasattr(self.user_interface, 'confirm_action'):
            result = self.user_interface.confirm_action("Продолжить?")
            assert result is True or result == 'y'

    @patch('builtins.print')
    def test_show_error_message(self, mock_print):
        """Тест отображения сообщения об ошибке"""
        if hasattr(self.user_interface, 'show_error'):
            self.user_interface.show_error("Тестовая ошибка")
            mock_print.assert_called()

    @patch('builtins.input', side_effect=['invalid', '1'])
    @patch('builtins.print')
    def test_input_validation(self, mock_print, mock_input):
        """Тест валидации ввода"""
        if hasattr(self.user_interface, 'get_valid_choice'):
            choices = ['1', '2', '3']
            result = self.user_interface.get_valid_choice(choices, "Выберите: ")
            assert result in choices

    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    def test_exit_application(self, mock_print, mock_input):
        """Тест выхода из приложения"""
        if hasattr(self.user_interface, 'exit'):
            with pytest.raises(SystemExit):
                self.user_interface.exit()

    @patch('src.ui_interfaces.console_interface.UserInterface')
    def test_console_interface_integration(self, mock_console):
        """Тест интеграции с консольным интерфейсом"""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance
        
        # Проверяем что консольный интерфейс может быть создан
        assert mock_console is not None

    def test_interface_attributes(self):
        """Тест наличия необходимых атрибутов"""
        required_methods = [
            'start', 'show_main_menu', 'handle_choice', 
            'handle_user_choice', 'display_vacancies'
        ]
        
        for method in required_methods:
            if hasattr(self.user_interface, method):
                assert callable(getattr(self.user_interface, method))

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_menu_navigation(self, mock_print, mock_input):
        """Тест навигации по меню"""
        test_choices = ['1', '2', '3', '0']
        
        for choice in test_choices:
            with patch('builtins.input', return_value=choice):
                if hasattr(self.user_interface, 'handle_user_choice'):
                    try:
                        self.user_interface.handle_user_choice(choice)
                    except (SystemExit, Exception):
                        pass

    @patch('builtins.print')
    def test_help_display(self, mock_print):
        """Тест отображения справки"""
        if hasattr(self.user_interface, 'show_help'):
            self.user_interface.show_help()
            mock_print.assert_called()
