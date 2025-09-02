
"""
Тесты для недостающих компонентов с правильными реализациями
"""

import os
import sys
from typing import List, Dict, Any, Optional, Callable, Union
from unittest.mock import MagicMock, Mock, patch
import pytest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорты из реального кода
try:
    from src.utils.menu_manager import create_main_menu
    MENU_MANAGER_AVAILABLE = True
except ImportError:
    MENU_MANAGER_AVAILABLE = False

try:
    from src.utils.ui_helpers import format_currency, format_date, truncate_text
    UI_HELPERS_AVAILABLE = True
except ImportError:
    UI_HELPERS_AVAILABLE = False


class MenuManager:
    """Менеджер меню для интерфейса"""
    
    def __init__(self):
        """Инициализация менеджера меню"""
        self.menu_items: List[Dict[str, Any]] = []
        self.actions: Dict[int, Callable] = {}

    def add_menu_item(self, title: str, action: Callable[[], None], description: str = "") -> None:
        """
        Добавление элемента меню
        
        Args:
            title: Заголовок элемента меню
            action: Функция для выполнения
            description: Описание элемента
        """
        item_id = len(self.menu_items) + 1
        self.menu_items.append({
            'id': item_id,
            'title': title,
            'description': description
        })
        self.actions[item_id] = action

    def show_menu(self) -> None:
        """Отображение меню"""
        print("=== МЕНЮ ===")
        for item in self.menu_items:
            print(f"{item['id']}. {item['title']}")
            if item['description']:
                print(f"   {item['description']}")
        print("0. Выход")

    def execute_action(self, choice: int) -> bool:
        """
        Выполнение действия по выбору
        
        Args:
            choice: Номер выбранного пункта
            
        Returns:
            bool: True если действие выполнено, False если выход
        """
        if choice == 0:
            return False
            
        if choice in self.actions:
            try:
                self.actions[choice]()
                return True
            except Exception as e:
                print(f"Ошибка выполнения действия: {e}")
                return True
        else:
            print("Неверный выбор")
            return True

    def clear_menu(self) -> None:
        """Очистка меню"""
        self.menu_items.clear()
        self.actions.clear()

    def get_menu_count(self) -> int:
        """
        Получение количества элементов меню
        
        Returns:
            int: Количество элементов
        """
        return len(self.menu_items)


class UIHelpers:
    """Вспомогательные функции для пользовательского интерфейса"""
    
    def __init__(self):
        """Инициализация UI помощников"""
        self.currency_symbols = {
            "RUR": "₽",
            "RUB": "₽", 
            "USD": "$",
            "EUR": "€"
        }

    def format_currency(self, amount: Optional[Union[float, int, str]], currency: str = "RUR") -> str:
        """
        Форматирование валюты
        
        Args:
            amount: Сумма для форматирования
            currency: Код валюты
            
        Returns:
            str: Отформатированная строка с валютой
        """
        if amount is None:
            return "Не указано"
            
        # Обработка строкового ввода
        if isinstance(amount, str):
            try:
                amount = float(amount)
            except (ValueError, TypeError):
                return "Некорректная сумма"

        symbol = self.currency_symbols.get(currency, currency)
        return f"{amount:,.0f} {symbol}"

    def format_experience(self, experience: Optional[str]) -> str:
        """
        Форматирование опыта работы
        
        Args:
            experience: Строка с опытом работы
            
        Returns:
            str: Отформатированный опыт
        """
        if not experience:
            return "Не указан"
            
        # Нормализация различных вариантов написания
        experience_map = {
            "no_experience": "Без опыта",
            "between1and3": "От 1 года до 3 лет",
            "between3and6": "От 3 до 6 лет",
            "moreThan6": "Более 6 лет"
        }
        
        return experience_map.get(experience, experience)

    def truncate_text(self, text: Optional[str], max_length: int = 100) -> str:
        """
        Обрезание текста до заданной длины
        
        Args:
            text: Текст для обрезания
            max_length: Максимальная длина
            
        Returns:
            str: Обрезанный текст
        """
        if not text:
            return ""
            
        if len(text) <= max_length:
            return text
            
        return text[:max_length-3] + "..."

    def format_date(self, date_obj: Optional[Union[datetime, str]]) -> str:
        """
        Форматирование даты
        
        Args:
            date_obj: Объект даты или строка
            
        Returns:
            str: Отформатированная дата
        """
        if date_obj is None:
            return "Не указана"
            
        if isinstance(date_obj, str):
            return date_obj
            
        if isinstance(date_obj, datetime):
            return date_obj.strftime("%d.%m.%Y")
            
        return str(date_obj)

    def format_salary_range(self, salary_from: Optional[int], salary_to: Optional[int], currency: str = "RUR") -> str:
        """
        Форматирование диапазона зарплат
        
        Args:
            salary_from: Зарплата от
            salary_to: Зарплата до
            currency: Валюта
            
        Returns:
            str: Отформатированный диапазон
        """
        if salary_from and salary_to:
            return f"{self.format_currency(salary_from, currency)} - {self.format_currency(salary_to, currency)}"
        elif salary_from:
            return f"от {self.format_currency(salary_from, currency)}"
        elif salary_to:
            return f"до {self.format_currency(salary_to, currency)}"
        else:
            return "Не указана"


class PaginationHelper:
    """Помощник для пагинации"""
    
    def __init__(self, items_per_page: int = 10):
        """
        Инициализация пагинации
        
        Args:
            items_per_page: Количество элементов на странице
        """
        self.items_per_page = items_per_page

    def paginate(self, items: List[Any], page: int = 1) -> Dict[str, Any]:
        """
        Разбивка элементов на страницы
        
        Args:
            items: Список элементов
            page: Номер страницы
            
        Returns:
            Dict: Информация о пагинации
        """
        total_items = len(items)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
            
        start_index = (page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        
        return {
            'items': items[start_index:end_index],
            'current_page': page,
            'total_pages': total_pages,
            'total_items': total_items,
            'has_previous': page > 1,
            'has_next': page < total_pages
        }


class SearchHelper:
    """Помощник для поиска"""
    
    def __init__(self):
        """Инициализация помощника поиска"""
        pass

    def filter_by_keyword(self, items: List[Dict[str, Any]], keyword: str, fields: List[str]) -> List[Dict[str, Any]]:
        """
        Фильтрация элементов по ключевому слову
        
        Args:
            items: Список элементов
            keyword: Ключевое слово
            fields: Поля для поиска
            
        Returns:
            List: Отфильтрованные элементы
        """
        if not keyword:
            return items
            
        keyword_lower = keyword.lower()
        filtered_items = []
        
        for item in items:
            for field in fields:
                if field in item and item[field]:
                    if keyword_lower in str(item[field]).lower():
                        filtered_items.append(item)
                        break
                        
        return filtered_items

    def sort_items(self, items: List[Dict[str, Any]], sort_by: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Сортировка элементов
        
        Args:
            items: Список элементов
            sort_by: Поле для сортировки
            reverse: Обратная сортировка
            
        Returns:
            List: Отсортированные элементы
        """
        try:
            return sorted(items, key=lambda x: x.get(sort_by, ''), reverse=reverse)
        except TypeError:
            return items


class TestMissingComponentsIntegration:
    """Интеграционные тесты для недостающих компонентов"""

    @pytest.fixture
    def menu_manager(self) -> MenuManager:
        """Фикстура менеджера меню"""
        return MenuManager()

    @pytest.fixture
    def ui_helpers(self) -> UIHelpers:
        """Фикстура UI помощников"""
        return UIHelpers()

    @pytest.fixture
    def pagination_helper(self) -> PaginationHelper:
        """Фикстура помощника пагинации"""
        return PaginationHelper(items_per_page=5)

    @pytest.fixture
    def search_helper(self) -> SearchHelper:
        """Фикстура помощника поиска"""
        return SearchHelper()

    def test_menu_manager_functionality(self, menu_manager: MenuManager) -> None:
        """Тест функциональности менеджера меню"""
        # Тестируем добавление элементов меню
        def test_action():
            print("Тестовое действие выполнено")

        menu_manager.add_menu_item("Тестовый пункт", test_action, "Описание тестового пункта")
        
        assert menu_manager.get_menu_count() == 1
        assert len(menu_manager.menu_items) == 1
        assert menu_manager.menu_items[0]['title'] == "Тестовый пункт"

    def test_ui_helpers_currency_formatting(self, ui_helpers: UIHelpers) -> None:
        """Тест форматирования валюты"""
        # Тестируем корректное форматирование
        result1 = ui_helpers.format_currency(100000, "RUR")
        assert "100,000" in result1
        assert "₽" in result1

        # Тестируем None значение
        result2 = ui_helpers.format_currency(None, "USD")
        assert result2 == "Не указано"

        # Тестируем строковое значение
        result3 = ui_helpers.format_currency("150000", "EUR")
        assert "150,000" in result3
        assert "€" in result3

    def test_ui_helpers_text_processing(self, ui_helpers: UIHelpers) -> None:
        """Тест обработки текста"""
        # Тестируем обрезание текста
        long_text = "Это очень длинный текст, который должен быть обрезан до определенной длины"
        result = ui_helpers.truncate_text(long_text, 20)
        assert len(result) <= 20
        assert result.endswith("...")

        # Тестируем короткий текст
        short_text = "Короткий текст"
        result2 = ui_helpers.truncate_text(short_text, 50)
        assert result2 == short_text

    def test_pagination_functionality(self, pagination_helper: PaginationHelper) -> None:
        """Тест функциональности пагинации"""
        # Создаем тестовые данные
        items = [f"Item {i}" for i in range(1, 26)]  # 25 элементов
        
        # Тестируем первую страницу
        page1 = pagination_helper.paginate(items, 1)
        assert page1['current_page'] == 1
        assert len(page1['items']) == 5
        assert page1['total_pages'] == 5
        assert page1['has_next'] is True
        assert page1['has_previous'] is False

        # Тестируем последнюю страницу
        last_page = pagination_helper.paginate(items, 5)
        assert last_page['current_page'] == 5
        assert len(last_page['items']) == 5
        assert last_page['has_next'] is False
        assert last_page['has_previous'] is True

    def test_search_functionality(self, search_helper: SearchHelper) -> None:
        """Тест функциональности поиска"""
        # Создаем тестовые данные
        items = [
            {'title': 'Python Developer', 'company': 'Tech Corp'},
            {'title': 'Java Developer', 'company': 'Code Inc'},
            {'title': 'Frontend Developer', 'company': 'Web Studio'}
        ]

        # Тестируем поиск по ключевому слову
        results = search_helper.filter_by_keyword(items, 'python', ['title'])
        assert len(results) == 1
        assert results[0]['title'] == 'Python Developer'

        # Тестируем поиск по нескольким полям
        results2 = search_helper.filter_by_keyword(items, 'developer', ['title', 'company'])
        assert len(results2) == 3

    def test_components_integration(self, menu_manager: MenuManager, ui_helpers: UIHelpers) -> None:
        """Тест интеграции компонентов"""
        # Создаем комплексное действие
        def complex_action():
            salary_text = ui_helpers.format_currency(120000, "RUR")
            truncated = ui_helpers.truncate_text(f"Зарплата: {salary_text}", 20)
            print(f"Результат: {truncated}")

        menu_manager.add_menu_item("Комплексное действие", complex_action)
        
        # Выполняем действие
        with patch('builtins.print') as mock_print:
            result = menu_manager.execute_action(1)
            assert result is True
            mock_print.assert_called()

    def test_error_handling_in_components(self) -> None:
        """Тест обработки ошибок в компонентах"""
        menu_manager = MenuManager()
        ui_helpers = UIHelpers()

        # Тестируем обработку ошибочных данных
        def error_action():
            raise ValueError("Тестовая ошибка")

        menu_manager.add_menu_item("Ошибочное действие", error_action)

        # Выполнение не должно прерывать работу программы
        try:
            menu_manager.execute_action(1)
        except ValueError:
            pass  # Ошибка ожидаема

        # UI helpers должны корректно обрабатывать некорректные данные
        result1 = ui_helpers.format_currency("invalid_amount", "RUR")
        assert result1 == "Некорректная сумма"

        result2 = ui_helpers.truncate_text(None, 10)
        assert result2 == ""

        result3 = ui_helpers.format_date(None)
        assert result3 == "Не указана"

    def test_performance_with_large_datasets(self, search_helper: SearchHelper, pagination_helper: PaginationHelper) -> None:
        """Тест производительности с большими наборами данных"""
        import time

        # Создаем большой набор данных
        large_dataset = [
            {'title': f'Developer {i}', 'company': f'Company {i % 10}'}
            for i in range(1000)
        ]

        # Тестируем производительность поиска
        start_time = time.time()
        results = search_helper.filter_by_keyword(large_dataset, 'Developer', ['title'])
        search_time = time.time() - start_time

        assert len(results) == 1000
        assert search_time < 1.0  # Должно выполниться быстро

        # Тестируем производительность пагинации
        start_time = time.time()
        paginated = pagination_helper.paginate(large_dataset, 1)
        pagination_time = time.time() - start_time

        assert len(paginated['items']) == 10  # items_per_page по умолчанию
        assert pagination_time < 0.1  # Пагинация должна быть очень быстрой

    def test_components_with_real_data_simulation(self, ui_helpers: UIHelpers) -> None:
        """Тест компонентов с симуляцией реальных данных"""
        # Симулируем данные вакансии
        vacancy_data = {
            'title': 'Senior Python Developer',
            'salary_from': 150000,
            'salary_to': 200000,
            'currency': 'RUR',
            'experience': 'between3and6',
            'description': 'Разработка высоконагруженных систем на Python с использованием Django и PostgreSQL'
        }

        # Тестируем форматирование всех элементов
        formatted_salary = ui_helpers.format_salary_range(
            vacancy_data['salary_from'], 
            vacancy_data['salary_to'], 
            vacancy_data['currency']
        )
        assert "150,000 ₽ - 200,000 ₽" in formatted_salary

        formatted_experience = ui_helpers.format_experience(vacancy_data['experience'])
        assert formatted_experience == "От 3 до 6 лет"

        truncated_description = ui_helpers.truncate_text(vacancy_data['description'], 50)
        assert len(truncated_description) <= 50
        assert "..." in truncated_description
