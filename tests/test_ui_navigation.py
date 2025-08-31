
"""
Тесты для UINavigation

Содержит тесты для проверки корректности работы навигации по меню
согласно реальной реализации класса UINavigation.
"""

from unittest.mock import Mock, patch
import pytest
from src.utils.ui_navigation import UINavigation


class TestUINavigation:
    """Тесты для класса UINavigation"""

    @pytest.fixture
    def nav(self):
        """Фикстура с экземпляром UINavigation"""
        return UINavigation()

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_initialization(self, mock_input, mock_print, nav):
        """Тест инициализации UINavigation"""
        assert nav is not None
        assert hasattr(nav, 'menus')
        assert isinstance(nav.menus, dict)

    @patch("builtins.print") 
    @patch("builtins.input", return_value="")
    def test_create_menu(self, mock_input, mock_print, nav):
        """Тест создания меню"""
        items = [{"text": "Пункт 1"}, {"text": "Пункт 2"}]
        
        nav.create_menu("test_menu", "Тестовое меню", items)
        
        assert "test_menu" in nav.menus
        menu_data = nav.menus["test_menu"]
        assert menu_data["title"] == "Тестовое меню"
        assert menu_data["items"] == items

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_show_menu_basic(self, mock_input, mock_print, nav):
        """Тест базового отображения меню"""
        items = [{"text": "Поиск вакансий"}, {"text": "Настройки"}]
        
        nav.create_menu("main", "Главное меню", items)
        output = nav.show_menu("main")
        
        assert "Главное меню" in output
        assert "1. Поиск вакансий" in output
        assert "2. Настройки" in output
        assert "0. Выход" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_show_menu_with_separator(self, mock_input, mock_print, nav):
        """Тест отображения меню с разделителем"""
        items = [
            {"text": "Поиск вакансий"}, 
            {"text": "Настройки"}, 
            {"separator": True}, 
            {"text": "О программе"}
        ]
        
        nav.create_menu("main", "Главное меню", items)
        output = nav.show_menu("main")
        
        assert "Главное меню" in output
        assert "1. Поиск вакансий" in output
        assert "2. Настройки" in output
        # Согласно реальной логике - разделитель не влияет на нумерацию
        assert "3. О программе" in output
        assert "------------------------------" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_show_menu_nonexistent(self, mock_input, mock_print, nav):
        """Тест отображения несуществующего меню"""
        output = nav.show_menu("nonexistent")
        
        # Реальная реализация возвращает сообщение об ошибке
        assert "Меню с ID 'nonexistent' не найдено" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_handle_menu_choice_valid(self, mock_input, mock_print, nav):
        """Тест обработки валидного выбора меню"""
        items = [
            {"text": "Пункт 1", "action": lambda: "action1"},
            {"text": "Пункт 2", "action": lambda: "action2"}
        ]
        
        nav.create_menu("test", "Тест", items)
        
        result = nav.handle_menu_choice("test", "1")
        
        # Реальная реализация возвращает словарь с информацией о выборе
        assert isinstance(result, dict)
        assert result.get("action") == "select"
        assert "item" in result

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_handle_menu_choice_exit(self, mock_input, mock_print, nav):
        """Тест обработки выбора выхода"""
        items = [{"text": "Пункт 1"}]
        
        nav.create_menu("test", "Тест", items)
        
        result = nav.handle_menu_choice("test", "0")
        
        # Реальная реализация возвращает словарь с action: exit
        assert isinstance(result, dict)
        assert result.get("action") == "exit"

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_handle_menu_choice_invalid_number(self, mock_input, mock_print, nav):
        """Тест обработки невалидного числового выбора"""
        items = [{"text": "Пункт 1"}]
        
        nav.create_menu("main", "Главное меню", items)
        
        # Тестируем невалидный номер (больше количества пунктов)
        result = nav.handle_menu_choice("main", "99")
        
        # Реальная реализация возвращает словарь с ошибкой
        assert isinstance(result, dict)
        assert "error" in result
        assert "Выбор должен быть от 1 до 1" in result["error"]

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_handle_menu_choice_invalid_format(self, mock_input, mock_print, nav):
        """Тест обработки невалидного формата выбора"""
        items = [{"text": "Пункт 1"}]
        
        nav.create_menu("test", "Тест", items)
        
        # Тестируем нечисловой ввод
        result = nav.handle_menu_choice("test", "abc")
        
        # Реальная реализация возвращает словарь с ошибкой
        assert isinstance(result, dict)
        assert "error" in result
        assert "Выбор должен быть числом" in result["error"]

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_handle_menu_choice_nonexistent_menu(self, mock_input, mock_print, nav):
        """Тест обработки выбора в несуществующем меню"""
        result = nav.handle_menu_choice("nonexistent", "1")
        
        # Реальная реализация возвращает словарь с ошибкой
        assert isinstance(result, dict)
        assert "error" in result
        assert "Меню с ID 'nonexistent' не найдено" in result["error"]

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_display_formatting(self, mock_input, mock_print, nav):
        """Тест форматирования отображения меню"""
        items = [{"text": "Тестовый пункт"}]
        nav.create_menu("format", "Тест форматирования", items)
        
        output = nav.show_menu("format")
        
        # Проверяем наличие границ меню
        assert "==================================================" in output
        assert "1. Тестовый пункт" in output
        assert "0. Выход" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_item_with_action(self, mock_input, mock_print, nav):
        """Тест пункта меню с действием"""
        mock_action = Mock(return_value="test_result")
        items = [{"text": "Действие", "action": mock_action}]
        
        nav.create_menu("action_menu", "Меню с действием", items)
        
        result = nav.handle_menu_choice("action_menu", "1")
        
        # Реальная реализация возвращает информацию о выборе, но не вызывает действие напрямую
        assert isinstance(result, dict)
        assert result.get("action") == "select"

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_item_without_action(self, mock_input, mock_print, nav):
        """Тест пункта меню без действия"""
        items = [{"text": "Пункт без действия"}]
        
        nav.create_menu("no_action", "Меню без действий", items)
        
        result = nav.handle_menu_choice("no_action", "1")
        
        # Реальная реализация возвращает информацию о выборе
        assert isinstance(result, dict)
        assert result.get("action") == "select"
        assert "item" in result

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_complex_menu_structure(self, mock_input, mock_print, nav):
        """Тест сложной структуры меню с различными типами элементов"""
        items = [
            {"text": "Обычный пункт"},
            {"text": "Пункт с действием", "action": lambda: "executed"},
            {"separator": True},
            {"text": "Последний пункт"}
        ]
        
        nav.create_menu("complex", "Сложное меню", items)
        output = nav.show_menu("complex")
        
        assert "Сложное меню" in output
        assert "1. Обычный пункт" in output
        assert "2. Пункт с действием" in output
        assert "------------------------------" in output
        # Согласно реальной логике нумерации
        assert "3. Последний пункт" in output
        assert "0. Выход" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_choice_edge_cases(self, mock_input, mock_print, nav):
        """Тест граничных случаев выбора меню"""
        items = [{"text": "Единственный пункт"}]
        nav.create_menu("edge", "Граничный тест", items)
        
        # Тест пустого ввода
        result = nav.handle_menu_choice("edge", "")
        assert isinstance(result, dict)
        assert "error" in result
        
        # Тест отрицательного числа
        result = nav.handle_menu_choice("edge", "-1")
        assert isinstance(result, dict)
        assert "error" in result
        
        # Тест нуля (выход)
        result = nav.handle_menu_choice("edge", "0")
        assert isinstance(result, dict)
        assert result.get("action") == "exit"

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_empty_menu(self, mock_input, mock_print, nav):
        """Тест пустого меню"""
        nav.create_menu("empty", "Пустое меню", [])
        output = nav.show_menu("empty")
        
        assert "Пустое меню" in output
        assert "0. Выход" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_overwrite(self, mock_input, mock_print, nav):
        """Тест перезаписи существующего меню"""
        items1 = [{"text": "Старый пункт"}]
        items2 = [{"text": "Новый пункт"}]
        
        nav.create_menu("test", "Первое меню", items1)
        nav.create_menu("test", "Второе меню", items2)
        
        output = nav.show_menu("test")
        
        assert "Второе меню" in output
        assert "Новый пункт" in output
        assert "Старый пункт" not in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_action_exception_handling(self, mock_input, mock_print, nav):
        """Тест обработки исключений в действиях"""
        def failing_action():
            raise Exception("Test exception")
        
        items = [{"text": "Падающее действие", "action": failing_action}]
        nav.create_menu("error_test", "Тест ошибок", items)
        
        # Действие должно обрабатываться без падения тестов
        result = nav.handle_menu_choice("error_test", "1")
        
        # Результат должен быть словарем с информацией о выборе
        assert isinstance(result, dict)
        assert result.get("action") == "select"

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_multiple_separators(self, mock_input, mock_print, nav):
        """Тест меню с несколькими разделителями"""
        items = [
            {"text": "Пункт 1"},
            {"separator": True},
            {"text": "Пункт 2"},
            {"separator": True},
            {"text": "Пункт 3"}
        ]
        
        nav.create_menu("multi_sep", "Меню с разделителями", items)
        output = nav.show_menu("multi_sep")
        
        assert "1. Пункт 1" in output
        # Согласно реальной логике нумерации
        assert "2. Пункт 2" in output
        assert "3. Пункт 3" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_choice_validation(self, mock_input, mock_print, nav):
        """Тест валидации выбора пользователя"""
        items = [{"text": "Пункт 1"}, {"text": "Пункт 2"}]
        nav.create_menu("validation", "Валидация", items)
        
        # Тестируем различные варианты ввода
        test_cases = [
            ("1", "valid"),      # Валидный выбор
            ("2", "valid"),      # Валидный выбор  
            ("0", "exit"),       # Выход
            ("3", "invalid"),    # Превышает количество пунктов
            ("-1", "invalid"),   # Отрицательное число
            ("abc", "invalid"),  # Не число
            ("", "invalid"),     # Пустой ввод
            ("1.5", "invalid"),  # Дробное число
        ]
        
        for choice, expected_type in test_cases:
            result = nav.handle_menu_choice("validation", choice)
            
            if expected_type == "exit":
                assert isinstance(result, dict)
                assert result.get("action") == "exit"
            elif expected_type == "invalid":
                assert isinstance(result, dict)
                assert "error" in result
            elif expected_type == "valid":
                assert isinstance(result, dict)
                assert result.get("action") == "select"

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_with_long_text(self, mock_input, mock_print, nav):
        """Тест меню с длинными текстами"""
        long_text = "Очень длинный текст пункта меню который может не поместиться в одну строку"
        items = [{"text": long_text}]
        
        nav.create_menu("long", "Длинный текст", items)
        output = nav.show_menu("long")
        
        assert f"1. {long_text}" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_item_numbering_with_complex_structure(self, mock_input, mock_print, nav):
        """Тест нумерации в сложной структуре меню"""
        items = [
            {"text": "Первый"},           # 1
            {"text": "Второй"},           # 2  
            {"separator": True},          # Не нумеруется
            {"text": "Третий"},           # 3 (согласно реальной логике)
            {"text": "Четвертый"},        # 4
            {"separator": True},          # Не нумеруется
            {"text": "Пятый"}             # 5
        ]
        
        nav.create_menu("complex_num", "Сложная нумерация", items)
        output = nav.show_menu("complex_num")
        
        # Проверяем правильную нумерацию согласно реальной логике
        assert "1. Первый" in output
        assert "2. Второй" in output
        assert "3. Третий" in output
        assert "4. Четвертый" in output
        assert "5. Пятый" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_actions_with_parameters(self, mock_input, mock_print, nav):
        """Тест действий меню с параметрами"""
        def action_with_params():
            return "action_executed"
        
        items = [{"text": "Действие с параметрами", "action": action_with_params}]
        nav.create_menu("params", "Параметры", items)
        
        result = nav.handle_menu_choice("params", "1")
        
        # Проверяем, что возвращается информация о выборе
        assert isinstance(result, dict)
        assert result.get("action") == "select"

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_concurrent_menu_operations(self, mock_input, mock_print, nav):
        """Тест одновременных операций с меню"""
        # Создаем несколько меню
        for i in range(5):
            items = [{"text": f"Пункт {j}"} for j in range(3)]
            nav.create_menu(f"menu_{i}", f"Меню {i}", items)
        
        # Проверяем, что все меню созданы
        assert len(nav.menus) == 5
        
        # Проверяем отображение каждого меню
        for i in range(5):
            output = nav.show_menu(f"menu_{i}")
            assert f"Меню {i}" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")  
    def test_menu_state_isolation(self, mock_input, mock_print, nav):
        """Тест изоляции состояния между меню"""
        items1 = [{"text": "Пункт 1"}]
        items2 = [{"text": "Пункт A"}]
        
        nav.create_menu("menu1", "Первое меню", items1)
        nav.create_menu("menu2", "Второе меню", items2)
        
        output1 = nav.show_menu("menu1")
        output2 = nav.show_menu("menu2")
        
        # Проверяем, что меню не влияют друг на друга
        assert "Первое меню" in output1 and "Первое меню" not in output2
        assert "Второе меню" in output2 and "Второе меню" not in output1
        assert "Пункт 1" in output1 and "Пункт 1" not in output2
        assert "Пункт A" in output2 and "Пункт A" not in output1

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_memory_efficiency(self, mock_input, mock_print, nav):
        """Тест эффективности памяти при работе с меню"""
        # Создаем большое количество меню для проверки утечек памяти
        for i in range(100):
            items = [{"text": f"Пункт {j}"} for j in range(10)]
            nav.create_menu(f"big_menu_{i}", f"Большое меню {i}", items)
        
        # Очищаем некоторые меню
        for i in range(0, 100, 2):
            if f"big_menu_{i}" in nav.menus:
                del nav.menus[f"big_menu_{i}"]
        
        # Проверяем, что остались только нечетные меню
        remaining_menus = [key for key in nav.menus.keys() if key.startswith("big_menu_")]
        assert len(remaining_menus) == 50

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_unicode_support(self, mock_input, mock_print, nav):
        """Тест поддержки Unicode символов"""
        items = [
            {"text": "🔍 Поиск"},
            {"text": "⚙️ Настройки"}, 
            {"text": "📊 Статистика"}
        ]
        
        nav.create_menu("unicode", "Unicode меню", items)
        output = nav.show_menu("unicode")
        
        assert "🔍 Поиск" in output
        assert "⚙️ Настройки" in output
        assert "📊 Статистика" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_consistency(self, mock_input, mock_print, nav):
        """Тест консистентности меню при множественных операциях"""
        items = [{"text": "Консистентный пункт"}]
        
        # Многократно создаем и отображаем меню
        for i in range(10):
            nav.create_menu("consistent", f"Консистентное меню {i}", items)
            output = nav.show_menu("consistent")
            
            assert f"Консистентное меню {i}" in output
            assert "1. Консистентный пункт" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_menu_error_recovery(self, mock_input, mock_print, nav):
        """Тест восстановления после ошибок"""
        # Создаем меню с корректными данными
        good_items = [{"text": "Хороший пункт"}]
        nav.create_menu("recovery", "Тест восстановления", good_items)
        
        # Проверяем, что меню работает после потенциальных ошибок
        output = nav.show_menu("recovery")
        assert "Тест восстановления" in output
        assert "1. Хороший пункт" in output

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_special_characters_in_menu(self, mock_input, mock_print, nav):
        """Тест специальных символов в меню"""
        items = [
            {"text": "Пункт с &*#@!"},
            {"text": "Пункт с 'кавычками'"},
            {"text": 'Пункт с "двойными кавычками"'}
        ]
        
        nav.create_menu("special", "Спецсимволы", items)
        output = nav.show_menu("special")
        
        assert "Пункт с &*#@!" in output
        assert "Пункт с 'кавычками'" in output
        assert 'Пункт с "двойными кавычками"' in output
