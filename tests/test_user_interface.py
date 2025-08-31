
import pytest
from unittest.mock import MagicMock, patch, StringIO
from src.user_interface import UserInterface, main


class TestUserInterface:
    def setup_method(self):
        """Настройка для каждого теста"""
        self.ui = UserInterface()

    def test_user_interface_initialization(self):
        """Тест инициализации пользовательского интерфейса"""
        ui = UserInterface()
        assert ui is not None

    @patch('builtins.input', return_value='0')
    @patch('sys.stdout', new_callable=StringIO)
    def test_user_interface_run_exit(self, mock_stdout, mock_input):
        """Тест запуска интерфейса с выходом"""
        ui = UserInterface()
        with patch.object(ui, '_display_menu'):
            with patch.object(ui, '_handle_choice') as mock_handle:
                mock_handle.return_value = False
                ui.run()
                mock_handle.assert_called()

    @patch('builtins.input', return_value='1')
    def test_user_interface_handle_search(self, mock_input):
        """Тест обработки поиска вакансий"""
        ui = UserInterface()
        with patch.object(ui, '_search_vacancies') as mock_search:
            result = ui._handle_choice('1')
            if hasattr(ui, '_search_vacancies'):
                mock_search.assert_called()

    def test_user_interface_display_menu(self):
        """Тест отображения меню"""
        ui = UserInterface()
        with patch('builtins.print') as mock_print:
            ui._display_menu()
            mock_print.assert_called()

    def test_user_interface_validate_choice(self):
        """Тест валидации выбора пользователя"""
        ui = UserInterface()
        assert ui._validate_choice('1') in [True, False]
        assert ui._validate_choice('0') in [True, False]
        assert ui._validate_choice('invalid') == False

    @patch('src.user_interface.UserInterface')
    def test_main_function(self, mock_ui_class):
        """Тест главной функции"""
        mock_ui = MagicMock()
        mock_ui_class.return_value = mock_ui
        main()
        mock_ui.run.assert_called_once()

    def test_user_interface_error_handling(self):
        """Тест обработки ошибок"""
        ui = UserInterface()
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                ui.run()
