"""
Тесты для навигации пользовательского интерфейса
"""

import pytest
from unittest.mock import Mock, patch, call
from typing import Dict, List, Callable, Any

# Моковый UINavigation для тестов
class UINavigation:
    """Навигация по интерфейсу пользователя"""

    def __init__(self):
        self.menu_stack = []
        self.current_menu = None
        self.menu_items = {}
        self.exit_requested = False

    def create_menu(self, menu_id: str, title: str, items: List[Dict[str, Any]]):
        """Создание меню"""
        menu = {
            'id': menu_id,
            'title': title,
            'items': items
        }
        self.menu_items[menu_id] = menu

    def show_menu(self, menu_id: str) -> str:
        """Отображение меню"""
        if menu_id not in self.menu_items:
            return "Menu not found"

        menu = self.menu_items[menu_id]
        self.current_menu = menu_id

        output = []
        output.append("=" * 50)
        output.append(menu['title'])
        output.append("=" * 50)

        for i, item in enumerate(menu['items'], 1):
            if item.get('separator'):
                output.append("-" * 30)
            else:
                output.append(f"{i}. {item['text']}")

        output.append("0. Выход" if not self.menu_stack else "0. Назад")
        output.append("=" * 50)

        return "\n".join(output)

    def handle_menu_choice(self, menu_id: str, choice: str) -> Dict[str, Any]:
        """Обработка выбора пункта меню"""
        if menu_id not in self.menu_items:
            return {'error': 'Menu not found'}

        menu = self.menu_items[menu_id]

        if choice == '0':
            if self.menu_stack:
                return {'action': 'back'}
            else:
                return {'action': 'exit'}

        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(menu['items']):
                item = menu['items'][choice_index]

                if item.get('separator'):
                    return {'error': 'Invalid choice'}

                return {
                    'action': 'execute',
                    'item': item,
                    'function': item.get('function'),
                    'submenu': item.get('submenu')
                }
        except ValueError:
            pass

class TestUINavigation:
    """Тесты для UINavigation"""

    def setup_method(self):
        """Подготовка к каждому тесту"""
        self.nav = UINavigation()

    def test_create_menu(self):
        """Тест создания меню"""
        items = [
            {'text': 'Пункт 1', 'function': lambda: 'result1'},
            {'text': 'Пункт 2', 'submenu': 'submenu1'}
        ]

        self.nav.create_menu('main', 'Главное меню', items)

        assert 'main' in self.nav.menu_items
        menu = self.nav.menu_items['main']
        assert menu['id'] == 'main'
        assert menu['title'] == 'Главное меню'
        assert len(menu['items']) == 2
        assert menu['items'][0]['text'] == 'Пункт 1'

    def test_show_menu(self):
        """Тест отображения меню"""
        items = [
            {'text': 'Поиск вакансий'},
            {'text': 'Настройки'},
            {'separator': True},
            {'text': 'О программе'}
        ]

        self.nav.create_menu('main', 'Главное меню', items)
        output = self.nav.show_menu('main')

        assert 'Главное меню' in output
        assert '1. Поиск вакансий' in output
        assert '2. Настройки' in output
        assert '3. О программе' in output
        assert '0. Выход' in output
        assert '=' * 50 in output

    def test_show_menu_not_found(self):
        """Тест отображения несуществующего меню"""
        result = self.nav.show_menu('nonexistent')
        assert result == "Menu not found"

    def test_show_menu_with_stack(self):
        """Тест отображения меню с навигационным стеком"""
        items = [{'text': 'Пункт 1'}]

        self.nav.create_menu('main', 'Главное меню', items)
        self.nav.create_menu('sub', 'Подменю', items)

        # Навигируем к подменю
        self.nav.navigate_to_menu('sub')
        output = self.nav.show_menu('sub')

        assert '0. Назад' in output
        assert '0. Выход' not in output

    def test_handle_menu_choice_valid(self):
        """Тест обработки валидного выбора"""
        items = [
            {'text': 'Пункт 1', 'function': lambda: 'test_result'},
            {'text': 'Пункт 2', 'submenu': 'submenu'}
        ]

        self.nav.create_menu('main', 'Главное меню', items)

        result = self.nav.handle_menu_choice('main', '1')

        assert result['action'] == 'execute'
        assert result['function'] is not None
        assert callable(result['function'])

    def test_handle_menu_choice_invalid_number(self):
        """Тест обработки невалидного числового выбора"""
        items = [{'text': 'Пункт 1'}]

        self.nav.create_menu('main', 'Главное меню', items)

        result = self.nav.handle_menu_choice('main', '999')
        assert 'error' in result

    def test_handle_menu_choice_non_numeric(self):
        """Тест обработки нечислового выбора"""
        items = [{'text': 'Пункт 1'}]

        self.nav.create_menu('main', 'Главное меню', items)

        result = self.nav.handle_menu_choice('main', 'abc')
        assert 'error' in result

    def test_handle_menu_choice_exit(self):
        """Тест обработки выбора выхода"""
        items = [{'text': 'Пункт 1'}]

        self.nav.create_menu('main', 'Главное меню', items)

        result = self.nav.handle_menu_choice('main', '0')
        assert result['action'] == 'exit'

    def test_handle_menu_choice_back(self):
        """Тест обработки выбора назад"""
        items = [{'text': 'Пункт 1'}]

        self.nav.create_menu('main', 'Главное меню', items)
        self.nav.menu_stack = ['previous_menu']

        result = self.nav.handle_menu_choice('main', '0')
        assert result['action'] == 'back'

    def test_handle_menu_choice_separator(self):
        """Тест обработки выбора разделителя"""
        items = [
            {'text': 'Пункт 1'},
            {'separator': True}
        ]

        self.nav.create_menu('main', 'Главное меню', items)

        result = self.nav.handle_menu_choice('main', '2')
        assert 'error' in result

    def test_navigate_to_menu(self):
        """Тест навигации к меню"""
        self.nav.current_menu = 'main'
        self.nav.navigate_to_menu('submenu')

        assert self.nav.current_menu == 'submenu'
        assert 'main' in self.nav.menu_stack

    def test_navigate_to_menu_no_current(self):
        """Тест навигации к меню без текущего меню"""
        self.nav.navigate_to_menu('submenu')

        assert self.nav.current_menu == 'submenu'
        assert len(self.nav.menu_stack) == 0

    def test_go_back(self):
        """Тест возврата к предыдущему меню"""
        self.nav.menu_stack = ['main', 'submenu1']
        self.nav.current_menu = 'submenu2'

        result = self.nav.go_back()

        assert result is True
        assert self.nav.current_menu == 'submenu1'
        assert self.nav.menu_stack == ['main']

    def test_go_back_empty_stack(self):
        """Тест возврата при пустом стеке"""
        self.nav.menu_stack = []
        self.nav.current_menu = 'main'

        result = self.nav.go_back()

        assert result is False
        assert self.nav.current_menu == 'main'

    def test_get_current_menu(self):
        """Тест получения текущего меню"""
        self.nav.current_menu = 'test_menu'

        assert self.nav.get_current_menu() == 'test_menu'

    def test_get_menu_breadcrumb(self):
        """Тест получения хлебных крошек"""
        self.nav.menu_stack = ['main', 'submenu1']
        self.nav.current_menu = 'submenu2'

        breadcrumb = self.nav.get_menu_breadcrumb()

        assert breadcrumb == ['main', 'submenu1', 'submenu2']

    def test_get_menu_breadcrumb_empty(self):
        """Тест получения хлебных крошек при пустой навигации"""
        breadcrumb = self.nav.get_menu_breadcrumb()
        assert breadcrumb == []

    def test_clear_navigation_stack(self):
        """Тест очистки навигационного стека"""
        self.nav.menu_stack = ['main', 'submenu1']
        self.nav.current_menu = 'submenu2'

        self.nav.clear_navigation_stack()

        assert len(self.nav.menu_stack) == 0
        assert self.nav.current_menu is None

    def test_request_exit(self):
        """Тест запроса выхода"""
        assert self.nav.is_exit_requested() is False

        self.nav.request_exit()

        assert self.nav.is_exit_requested() is True

    def test_get_menu_depth(self):
        """Тест получения глубины навигации"""
        assert self.nav.get_menu_depth() == 0

        self.nav.menu_stack = ['main', 'submenu1']

        assert self.nav.get_menu_depth() == 2

    def test_execute_menu_item_with_function(self):
        """Тест выполнения пункта меню с функцией"""
        test_function = Mock(return_value="test_result")
        item = {'text': 'Test Item', 'function': test_function}

        result = self.nav.execute_menu_item(item)

        assert result == "test_result"
        test_function.assert_called_once()

    def test_execute_menu_item_with_submenu(self):
        """Тест выполнения пункта меню с подменю"""
        item = {'text': 'Test Item', 'submenu': 'test_submenu'}

        result = self.nav.execute_menu_item(item)

        assert result['action'] == 'navigate'
        assert result['menu'] == 'test_submenu'
        assert self.nav.current_menu == 'test_submenu'

    def test_execute_menu_item_function_exception(self):
        """Тест выполнения пункта меню с исключением в функции"""
        def error_function():
            raise ValueError("Test error")

        item = {'text': 'Test Item', 'function': error_function}

        result = self.nav.execute_menu_item(item)

        assert 'error' in result
        assert 'Test error' in result['error']

    def test_execute_menu_item_no_action(self):
        """Тест выполнения пункта меню без действия"""
        item = {'text': 'Test Item'}

        result = self.nav.execute_menu_item(item)

        assert 'error' in result
        assert 'No action defined' in result['error']

    def test_integration_navigation_flow(self):
        """Тест интегрированного потока навигации"""
        # Создаем главное меню
        main_items = [
            {'text': 'Поиск', 'submenu': 'search'},
            {'text': 'Настройки', 'function': lambda: 'settings_opened'}
        ]
        self.nav.create_menu('main', 'Главное меню', main_items)

        # Создаем подменю поиска
        search_items = [
            {'text': 'По ключевому слову', 'function': lambda: 'keyword_search'},
            {'text': 'Расширенный поиск', 'function': lambda: 'advanced_search'}
        ]
        self.nav.create_menu('search', 'Меню поиска', search_items)

        # Начинаем с главного меню
        assert self.nav.get_menu_depth() == 0

        # Навигируем к подменю поиска (выбор "1")
        choice_result = self.nav.handle_menu_choice('main', '1')
        assert choice_result['action'] == 'execute'

        execution_result = self.nav.execute_menu_item(choice_result['item'])
        assert execution_result['action'] == 'navigate'

        # Проверяем состояние навигации
        assert self.nav.get_current_menu() == 'search'
        assert self.nav.get_menu_depth() == 1

        breadcrumb = self.nav.get_menu_breadcrumb()
        assert breadcrumb == ['main', 'search']

        # Выполняем функцию из подменю (выбор "1")
        choice_result = self.nav.handle_menu_choice('search', '1')
        execution_result = self.nav.execute_menu_item(choice_result['item'])
        assert execution_result == 'keyword_search'

        # Возвращаемся назад (выбор "0")
        choice_result = self.nav.handle_menu_choice('search', '0')
        assert choice_result['action'] == 'back'

        back_result = self.nav.go_back()
        assert back_result is True
        assert self.nav.get_current_menu() == 'main'
        assert self.nav.get_menu_depth() == 0

        # Выходим (выбор "0" в главном меню)
        choice_result = self.nav.handle_menu_choice('main', '0')
        assert choice_result['action'] == 'exit'


        return {'error': 'Invalid choice'}

    def navigate_to_menu(self, menu_id: str):
        """Навигация к меню"""
        if self.current_menu:
            self.menu_stack.append(self.current_menu)
        self.current_menu = menu_id

    def go_back(self):
        """Возврат к предыдущему меню"""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            return True
        return False

    def get_current_menu(self) -> str:
        """Получение текущего меню"""
        return self.current_menu

    def get_menu_breadcrumb(self) -> List[str]:
        """Получение пути навигации (хлебные крошки)"""
        breadcrumb = self.menu_stack.copy()
        if self.current_menu:
            breadcrumb.append(self.current_menu)
        return breadcrumb

    def clear_navigation_stack(self):
        """Очистка стека навигации"""
        self.menu_stack.clear()
        self.current_menu = None

    def request_exit(self):
        """Запрос на выход"""
        self.exit_requested = True

    def is_exit_requested(self) -> bool:
        """Проверка запроса на выход"""
        return self.exit_requested

    def get_menu_depth(self) -> int:
        """Получение глубины навигации"""
        return len(self.menu_stack)

    def execute_menu_item(self, item: Dict[str, Any]) -> Any:
        """Выполнение пункта меню"""
        if 'function' in item and callable(item['function']):
            try:
                return item['function']()
            except Exception as e:
                return {'error': str(e)}

        if 'submenu' in item:
            self.navigate_to_menu(item['submenu'])
            return {'action': 'navigate', 'menu': item['submenu']}

        return {'error': 'No action defined for menu item'}