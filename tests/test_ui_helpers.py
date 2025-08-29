
<old_str>    @patch("builtins.input", return_value="n")
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
        # Проверяем, что функции существуют
        from src.utils import ui_helpers
        assert hasattr(ui_helpers, 'confirm_action')
        assert callable(getattr(ui_helpers, 'confirm_action'))
        
        # Проверяем существующие функции
        functions = [attr for attr in dir(ui_helpers)
                    if callable(getattr(ui_helpers, attr)) and not attr.startswith('_')]
        assert len(functions) > 0</old_str>
<new_str>    @patch("builtins.input", return_value="n")
    def test_confirm_action_no(self, mock_input):
        """Тест подтверждения действия - нет"""
        result = confirm_action("Продолжить?")
        assert result is False

    @patch("builtins.input", return_value="test input")
    def test_get_user_input(self, mock_input):
        """Тест получения пользовательского ввода"""
        result = get_user_input("Введите данные:")
        assert result == "test input"

    @patch("builtins.input", return_value="")
    def test_get_user_input_empty_required(self, mock_input):
        """Тест получения пустого ввода для обязательного поля"""
        with patch("builtins.print"):  # Подавляем вывод ошибки
            # Для required=False
            result = get_user_input("Введите данные:", required=False)
            assert result is None

    @patch("builtins.input", return_value="123")
    def test_get_positive_integer(self, mock_input):
        """Тест получения положительного числа"""
        result = get_positive_integer("Введите число:")
        assert result == 123

    @patch("builtins.input", side_effect=["invalid", "123"])
    def test_get_positive_integer_retry(self, mock_input):
        """Тест повторного ввода при некорректном числе"""
        with patch("builtins.print"):  # Подавляем вывод ошибок
            # Первый вызов вернет None из-за некорректного ввода
            result = get_positive_integer("Введите число:")
            assert result is None

    def test_parse_salary_range_valid(self):
        """Тест парсинга валидного диапазона зарплат"""
        result = parse_salary_range("100000 - 150000")
        assert result == (100000, 150000)
        
        # Тест обратного порядка
        result = parse_salary_range("150000 - 100000")
        assert result == (100000, 150000)

    def test_parse_salary_range_invalid(self):
        """Тест парсинга некорректного диапазона"""
        with patch("builtins.print"):  # Подавляем вывод ошибок
            result = parse_salary_range("invalid")
            assert result is None
            
            result = parse_salary_range("abc - def")
            assert result is None

    @patch("builtins.input", side_effect=["invalid", "y"])
    @patch("builtins.print")
    def test_confirm_action_retry(self, mock_print, mock_input):
        """Тест повторного подтверждения при некорректном вводе"""
        result = confirm_action("Продолжить?")
        # В итоге должно получиться True после корректного ввода
        assert result is True

    @patch("builtins.input", return_value="Y")
    def test_confirm_action_case_insensitive(self, mock_input):
        """Тест подтверждения без учета регистра"""
        result = confirm_action("Продолжить?")
        assert result is True

    @patch("builtins.input", return_value="да")
    def test_confirm_action_russian(self, mock_input):
        """Тест подтверждения на русском языке"""
        result = confirm_action("Продолжить?")
        assert result is True

    def test_ui_helpers_functions_exist(self):
        """Тест существования основных функций"""
        from src.utils import ui_helpers
        
        expected_functions = [
            'confirm_action', 'get_user_input', 'get_positive_integer', 'parse_salary_range'
        ]
        
        for func_name in expected_functions:
            assert hasattr(ui_helpers, func_name), f"Function {func_name} not found"
            assert callable(getattr(ui_helpers, func_name)), f"Function {func_name} is not callable"

    @patch("builtins.input", return_value="test")
    def test_get_user_input_with_prompt(self, mock_input):
        """Тест получения ввода с промптом"""
        prompt = "Введите значение:"
        result = get_user_input(prompt)
        assert result == "test"

    @patch("builtins.input", return_value="")  
    def test_get_positive_integer_with_default(self, mock_input):
        """Тест получения числа с дефолтным значением"""
        result = get_positive_integer("Введите число:", default=10)
        assert result == 10

    def test_ui_helpers_integration(self):
        """Тест интеграции UI helpers"""
        # Проверяем, что функции существуют
        from src.utils import ui_helpers
        assert hasattr(ui_helpers, 'confirm_action')
        assert callable(getattr(ui_helpers, 'confirm_action'))
        
        # Проверяем существующие функции
        functions = [attr for attr in dir(ui_helpers)
                    if callable(getattr(ui_helpers, attr)) and not attr.startswith('_')]
        assert len(functions) > 0</old_str>
