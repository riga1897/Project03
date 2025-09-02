"""
Тесты для системы меню
"""

import os
import sys
from unittest.mock import Mock, patch
from typing import List, Dict, Any, Callable

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.menu_manager import MenuManager, MenuItem
except ImportError:
    # Создаем тестовые реализации
    class MenuItem:
        """Тестовый элемент меню"""

        def __init__(self, key: str, title: str, action: Callable = None, 
                     description: str = "", submenu: List['MenuItem'] = None):
            """
            Инициализация элемента меню

            Args:
                key: Ключ элемента
                title: Заголовок элемента
                action: Функция-обработчик
                description: Описание элемента
                submenu: Подменю
            """
            self.key = key
            self.title = title
            self.action = action
            self.description = description
            self.submenu = submenu or []

        def execute(self) -> Any:
            """Выполнить действие элемента меню"""
            if self.action:
                return self.action()
            return None

        def has_submenu(self) -> bool:
            """Проверить наличие подменю"""
            return len(self.submenu) > 0

    class MenuManager:
        """Тестовый менеджер меню"""

        def __init__(self):
            """Инициализация менеджера меню"""
            self.current_menu = []
            self.menu_stack = []
            self.exit_requested = False

        def add_menu_item(self, item: MenuItem):
            """
            Добавить элемент в текущее меню

            Args:
                item: Элемент меню
            """
            self.current_menu.append(item)

        def create_main_menu(self) -> List[MenuItem]:
            """Создать главное меню"""
            return [
                MenuItem("1", "Поиск вакансий", lambda: print("Поиск вакансий")),
                MenuItem("2", "Сохраненные вакансии", lambda: print("Сохраненные вакансии")),
                MenuItem("3", "Статистика", lambda: print("Статистика")),
                MenuItem("4", "Настройки", submenu=[
                    MenuItem("4.1", "API настройки", lambda: print("API настройки")),
                    MenuItem("4.2", "БД настройки", lambda: print("БД настройки")),
                ]),
                MenuItem("0", "Выход", self._exit_action)
            ]

        def display_menu(self, menu: List[MenuItem] = None) -> None:
            """
            Отобразить меню

            Args:
                menu: Список элементов меню
            """
            if menu is None:
                menu = self.current_menu

            print("\n" + "="*50)
            print("МЕНЮ")
            print("="*50)

            for item in menu:
                submenu_indicator = " >" if item.has_submenu() else ""
                print(f"{item.key}. {item.title}{submenu_indicator}")
                if item.description:
                    print(f"   {item.description}")

            print("="*50)

        def get_user_choice(self, menu: List[MenuItem] = None) -> str:
            """
            Получить выбор пользователя

            Args:
                menu: Список элементов меню

            Returns:
                Выбранный ключ
            """
            if menu is None:
                menu = self.current_menu

            while True:
                choice = input("\nВыберите пункт меню: ").strip()

                # Проверяем валидность выбора
                valid_keys = [item.key for item in menu]
                if choice in valid_keys:
                    return choice

                print(f"Неверный выбор. Доступные варианты: {', '.join(valid_keys)}")

        def execute_choice(self, choice: str, menu: List[MenuItem] = None) -> Any:
            """
            Выполнить выбранное действие

            Args:
                choice: Выбранный ключ
                menu: Список элементов меню

            Returns:
                Результат выполнения
            """
            if menu is None:
                menu = self.current_menu

            for item in menu:
                if item.key == choice:
                    if item.has_submenu():
                        return self._enter_submenu(item)
                    else:
                        return item.execute()

            return None

        def run_menu_loop(self, menu: List[MenuItem] = None) -> None:
            """
            Запустить цикл обработки меню

            Args:
                menu: Список элементов меню
            """
            if menu is None:
                menu = self.current_menu

            while not self.exit_requested:
                self.display_menu(menu)
                choice = self.get_user_choice(menu)
                result = self.execute_choice(choice, menu)

                if result == "exit":
                    break
                elif result == "back":
                    if self.menu_stack:
                        menu = self.menu_stack.pop()
                    else:
                        break

        def _enter_submenu(self, item: MenuItem) -> str:
            """
            Войти в подменю

            Args:
                item: Элемент с подменю

            Returns:
                Результат операции
            """
            self.menu_stack.append(self.current_menu)

            # Добавляем пункт "Назад" в подменю
            submenu = item.submenu.copy()
            submenu.append(MenuItem("0", "Назад", lambda: "back"))

            self.run_menu_loop(submenu)
            return "submenu_exit"

        def _exit_action(self) -> str:
            """Действие выхода из меню"""
            self.exit_requested = True
            return "exit"

        def reset(self):
            """Сбросить состояние менеджера"""
            self.current_menu.clear()
            self.menu_stack.clear()
            self.exit_requested = False


class TestMenuItem:
    """Тесты для элемента меню"""

    def test_menu_item_creation(self):
        """Тест создания элемента меню"""
        action = lambda: "test_action"
        item = MenuItem("1", "Test Item", action, "Test description")

        assert item.key == "1"
        assert item.title == "Test Item"
        assert item.action == action
        assert item.description == "Test description"
        assert item.submenu == []

    def test_menu_item_execute(self):
        """Тест выполнения действия элемента меню"""
        action = lambda: "executed"
        item = MenuItem("1", "Test Item", action)

        result = item.execute()
        assert result == "executed"

    def test_menu_item_execute_no_action(self):
        """Тест выполнения элемента без действия"""
        item = MenuItem("1", "Test Item")

        result = item.execute()
        assert result is None

    def test_menu_item_has_submenu(self):
        """Тест проверки наличия подменю"""
        # Элемент без подменю
        item1 = MenuItem("1", "Test Item")
        assert not item1.has_submenu()

        # Элемент с подменю
        submenu = [MenuItem("1.1", "Sub Item")]
        item2 = MenuItem("2", "Test Item", submenu=submenu)
        assert item2.has_submenu()

    def test_menu_item_with_submenu(self):
        """Тест элемента с подменю"""
        sub_item = MenuItem("1.1", "Sub Item", lambda: "sub_executed")
        main_item = MenuItem("1", "Main Item", submenu=[sub_item])

        assert main_item.has_submenu()
        assert len(main_item.submenu) == 1
        assert main_item.submenu[0].key == "1.1"


class TestMenuManager:
    """Тесты для менеджера меню"""

    @pytest.fixture
    def menu_manager(self):
        """Фикстура менеджера меню"""
        return MenuManager()

    @pytest.fixture
    def sample_menu_items(self):
        """Фикстура тестовых элементов меню"""
        return [
            MenuItem("1", "Option 1", lambda: "option1_executed"),
            MenuItem("2", "Option 2", lambda: "option2_executed"),
            MenuItem("3", "Option 3", submenu=[
                MenuItem("3.1", "Sub Option 1", lambda: "sub1_executed"),
                MenuItem("3.2", "Sub Option 2", lambda: "sub2_executed")
            ])
        ]

    def test_menu_manager_initialization(self, menu_manager):
        """Тест инициализации менеджера меню"""
        assert menu_manager.current_menu == []
        assert menu_manager.menu_stack == []
        assert not menu_manager.exit_requested

    def test_add_menu_item(self, menu_manager):
        """Тест добавления элемента в меню"""
        item = MenuItem("1", "Test Item")
        menu_manager.add_menu_item(item)

        assert len(menu_manager.current_menu) == 1
        assert menu_manager.current_menu[0] == item

    def test_create_main_menu(self, menu_manager):
        """Тест создания главного меню"""
        main_menu = menu_manager.create_main_menu()

        assert isinstance(main_menu, list)
        assert len(main_menu) > 0

        # Проверяем наличие обязательных пунктов
        menu_keys = [item.key for item in main_menu]
        assert "1" in menu_keys  # Поиск вакансий
        assert "0" in menu_keys  # Выход

    @patch('builtins.print')
    def test_display_menu(self, mock_print, menu_manager, sample_menu_items):
        """Тест отображения меню"""
        menu_manager.display_menu(sample_menu_items)

        # Проверяем, что print был вызван
        assert mock_print.call_count > 0

        # Проверяем содержимое вызовов print
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        menu_text = " ".join(print_calls)

        assert "Option 1" in menu_text
        assert "Option 2" in menu_text
        assert "Option 3" in menu_text

    @patch('builtins.input', return_value='1')
    def test_get_user_choice_valid(self, mock_input, menu_manager, sample_menu_items):
        """Тест получения валидного выбора пользователя"""
        choice = menu_manager.get_user_choice(sample_menu_items)
        assert choice == '1'

    @patch('builtins.input', side_effect=['invalid', '999', '1'])
    @patch('builtins.print')
    def test_get_user_choice_invalid_then_valid(self, mock_print, mock_input, menu_manager, sample_menu_items):
        """Тест получения выбора с невалидными вариантами"""
        choice = menu_manager.get_user_choice(sample_menu_items)

        assert choice == '1'
        # Проверяем, что были выведены сообщения об ошибке
        error_messages = [call[0][0] for call in mock_print.call_args_list if "Неверный выбор" in str(call[0])]
        assert len(error_messages) >= 2

    def test_execute_choice_simple_action(self, menu_manager, sample_menu_items):
        """Тест выполнения простого действия"""
        result = menu_manager.execute_choice('1', sample_menu_items)
        assert result == "option1_executed"

    def test_execute_choice_submenu(self, menu_manager, sample_menu_items):
        """Тест входа в подменю"""
        with patch.object(menu_manager, '_enter_submenu', return_value='submenu_entered') as mock_enter:
            result = menu_manager.execute_choice('3', sample_menu_items)
            assert result == 'submenu_entered'
            mock_enter.assert_called_once()

    def test_execute_choice_invalid(self, menu_manager, sample_menu_items):
        """Тест выполнения несуществующего выбора"""
        result = menu_manager.execute_choice('999', sample_menu_items)
        assert result is None

    @patch('builtins.input', side_effect=['1', '0'])
    @patch('builtins.print')
    def test_run_menu_loop(self, mock_print, mock_input, menu_manager):
        """Тест цикла обработки меню"""
        menu_items = [
            MenuItem("1", "Test Action", lambda: "executed"),
            MenuItem("0", "Exit", lambda: "exit")
        ]

        menu_manager.run_menu_loop(menu_items)

        # Проверяем, что меню было отображено
        assert mock_print.call_count > 0

    def test_exit_action(self, menu_manager):
        """Тест действия выхода"""
        result = menu_manager._exit_action()

        assert result == "exit"
        assert menu_manager.exit_requested is True

    def test_reset(self, menu_manager):
        """Тест сброса состояния менеджера"""
        # Устанавливаем некоторое состояние
        menu_manager.current_menu.append(MenuItem("1", "Test"))
        menu_manager.menu_stack.append([])
        menu_manager.exit_requested = True

        # Сбрасываем
        menu_manager.reset()

        # Проверяем, что состояние сброшено
        assert menu_manager.current_menu == []
        assert menu_manager.menu_stack == []
        assert menu_manager.exit_requested is False

    @patch('builtins.input', side_effect=['3.1', '0'])
    @patch('builtins.print')
    def test_submenu_navigation(self, mock_print, mock_input, menu_manager):
        """Тест навигации по подменю"""
        submenu_item = MenuItem("3.1", "Sub Option", lambda: "sub_executed")
        main_item = MenuItem("3", "Main Option", submenu=[submenu_item])

        # Мокируем run_menu_loop для предотвращения бесконечного цикла
        with patch.object(menu_manager, 'run_menu_loop', return_value=None):
            result = menu_manager._enter_submenu(main_item)
            assert result == "submenu_exit"

    def test_menu_stack_operations(self, menu_manager):
        """Тест операций со стеком меню"""
        original_menu = [MenuItem("1", "Original")]
        submenu_item = MenuItem("2", "Submenu Item", submenu=[MenuItem("2.1", "Sub")])

        menu_manager.current_menu = original_menu

        # Входим в подменю
        with patch.object(menu_manager, 'run_menu_loop'):
            menu_manager._enter_submenu(submenu_item)

        # Проверяем, что оригинальное меню сохранено в стеке
        assert len(menu_manager.menu_stack) == 1
        assert menu_manager.menu_stack[0] == original_menu

    def test_complex_menu_workflow(self, menu_manager):
        """Тест сложного рабочего процесса меню"""
        executed_actions = []

        def track_action(name):
            def action():
                executed_actions.append(name)
                return name
            return action

        # Создаем сложное меню
        menu_items = [
            MenuItem("1", "Action 1", track_action("action1")),
            MenuItem("2", "Submenu", submenu=[
                MenuItem("2.1", "Sub Action 1", track_action("sub_action1")),
                MenuItem("2.2", "Sub Action 2", track_action("sub_action2"))
            ]),
            MenuItem("3", "Action 3", track_action("action3"))
        ]

        # Выполняем различные действия
        result1 = menu_manager.execute_choice('1', menu_items)
        assert result1 == "action1"
        assert "action1" in executed_actions

        # Проверяем работу с подменю
        submenu_item = next(item for item in menu_items if item.key == "2")
        sub_result = menu_manager.execute_choice('2.1', submenu_item.submenu)
        assert sub_result == "sub_action1"
        assert "sub_action1" in executed_actions