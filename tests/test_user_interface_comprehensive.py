"""
Комплексные тесты пользовательского интерфейса
"""

import os
import sys
from typing import List, Dict, Any, Optional
from unittest.mock import MagicMock, Mock, patch, call
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт из реального кода
from src.ui_interfaces.console_interface import UserInterface
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestUserInterfaceComprehensive:
    """Комплексные тесты пользовательского интерфейса"""

    @pytest.fixture
    def sample_vacancies(self) -> List[Vacancy]:
        """
        Создание тестовых вакансий

        Returns:
            List[Vacancy]: Список тестовых объектов вакансий
        """
        vacancies = []

        # Вакансия с полной информацией - используем правильный конструктор Salary
        salary1 = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        vacancy1 = Vacancy(
            title="Python Developer",
            vacancy_id="1",
            url="https://example.com/1",
            source="hh.ru",
            employer={"name": "Яндекс"},
            salary=salary1,
            description="Работа с Python и Django"
        )
        vacancies.append(vacancy1)

        # Вакансия без зарплаты
        vacancy2 = Vacancy(
            title="Java Developer",
            vacancy_id="2",
            url="https://example.com/2",
            source="superjob.ru",
            employer={"name": "СБЕР"},
            salary=None,
            description="Разработка на Java Spring"
        )
        vacancies.append(vacancy2)

        # Вакансия с минимальной зарплатой
        salary3 = Salary.from_range(80000, None, "RUR")
        vacancy3 = Vacancy(
            title="Frontend Developer",
            vacancy_id="3",
            url="https://example.com/3",
            source="hh.ru",
            employer={"name": "Тинькофф"},
            salary=salary3,
            description="Работа с React и TypeScript"
        )
        vacancies.append(vacancy3)

        return vacancies

    @pytest.fixture
    def user_interface(self) -> UserInterface:
        """
        Создание экземпляра пользовательского интерфейса с mock зависимостями

        Returns:
            UserInterface: Экземпляр пользовательского интерфейса
        """
        # Создаем mock storage
        mock_storage = Mock()
        mock_storage.get_vacancies.return_value = []
        mock_storage.add_vacancy.return_value = []
        mock_storage.delete_all_vacancies.return_value = True
        mock_storage.delete_vacancy_by_id.return_value = True

        # Создаем mock db_manager
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True

        return UserInterface(storage=mock_storage, db_manager=mock_db_manager)

    @patch('builtins.input', side_effect=['0'])  # Сразу выход
    @patch('builtins.print')
    def test_run_main_loop_exit(self, mock_print: Mock, mock_input: Mock, user_interface: UserInterface) -> None:
        """Тест основного цикла с выходом"""
        # Запускаем интерфейс
        user_interface.run()

        # Проверяем что приветствие было выведено
        assert mock_print.called
        # Проверяем что input был вызван для получения выбора пользователя
        assert mock_input.called

    @patch('builtins.input', side_effect=['1', '0'])  # Поиск, затем выход
    @patch('builtins.print')
    def test_run_search_vacancies(self, mock_print: Mock, mock_input: Mock, user_interface: UserInterface) -> None:
        """Тест поиска вакансий"""
        # Мокаем метод поиска в operations_coordinator
        user_interface.operations_coordinator.handle_vacancy_search = Mock()

        # Запускаем интерфейс
        user_interface.run()

        # Проверяем что поиск был вызван
        assert user_interface.operations_coordinator.handle_vacancy_search.called

    @patch('builtins.input', side_effect=[KeyboardInterrupt()])
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print: Mock, mock_input: Mock, user_interface: UserInterface) -> None:
        """Тест обработки прерывания клавиатурой"""
        # Запускаем интерфейс
        user_interface.run()

        # Проверяем что прерывание было обработано
        assert mock_print.called

    def test_show_menu_output(self, user_interface: UserInterface) -> None:
        """Тест отображения меню"""
        with patch('builtins.input', return_value='0') as mock_input, \
             patch('builtins.print') as mock_print:

            # Вызываем метод отображения меню
            choice = user_interface._show_menu()

            # Проверяем что меню было выведено
            assert mock_print.called
            assert choice == '0'

    def test_operations_coordinator_integration(self, user_interface: UserInterface) -> None:
        """Тест интеграции с координатором операций"""
        # Проверяем что координатор операций инициализирован
        assert user_interface.operations_coordinator is not None
        assert hasattr(user_interface.operations_coordinator, 'handle_vacancy_search')
        assert hasattr(user_interface.operations_coordinator, 'handle_show_saved_vacancies')
        assert hasattr(user_interface.operations_coordinator, 'handle_top_vacancies_by_salary')

    def test_run_advanced_search(self, user_interface: UserInterface, sample_vacancies: List[Vacancy]) -> None:
        """Тест расширенного поиска"""
        # Мокаем storage для возврата тестовых вакансий
        user_interface.storage.get_vacancies.return_value = sample_vacancies

        with patch('builtins.input', side_effect=['python', '0']) as mock_input, \
             patch('builtins.print') as mock_print, \
             patch('src.utils.ui_helpers.get_user_input', return_value='python'):

            # Вызываем метод расширенного поиска
            user_interface._advanced_search_vacancies()

            # Проверяем что поиск был выполнен
            assert mock_print.called

    def test_run_salary_filter(self, user_interface: UserInterface, sample_vacancies: List[Vacancy]) -> None:
        """Тест фильтрации по зарплате"""
        # Мокаем storage для возврата тестовых вакансий
        user_interface.storage.get_vacancies.return_value = sample_vacancies

        with patch('builtins.input', side_effect=['1', '100000']) as mock_input, \
             patch('builtins.print') as mock_print:

            # Вызываем метод фильтрации по зарплате
            user_interface._filter_saved_vacancies_by_salary()

            # Проверяем что фильтрация была выполнена
            assert mock_print.called

    def test_error_handling_in_run_loop(self, user_interface: UserInterface) -> None:
        """Тест обработки ошибок в основном цикле"""
        # Мокаем метод, который выбрасывает исключение
        user_interface.operations_coordinator.handle_vacancy_search = Mock(side_effect=Exception("Test error"))

        with patch('builtins.input', side_effect=['1', '0']):  # Поиск с ошибкой, затем выход
            with patch('builtins.print') as mock_print:
                user_interface.run()

        # Проверяем что ошибка была обработана и выведена
        assert mock_print.called
        # Проверяем что приложение не упало
        assert True

    def test_user_interface_initialization(self, user_interface: UserInterface) -> None:
        """Тест инициализации пользовательского интерфейса"""
        # Проверяем что все компоненты инициализированы
        assert user_interface.unified_api is not None
        assert user_interface.storage is not None
        assert user_interface.search_handler is not None
        assert user_interface.display_handler is not None
        assert user_interface.operations_coordinator is not None
        assert user_interface.vacancy_ops is not None

    def test_menu_navigation(self, user_interface: UserInterface) -> None:
        """Тест навигации по меню"""
        menu_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '0']

        for choice in menu_choices:
            with patch('builtins.input', return_value=choice) as mock_input, \
                 patch('builtins.print') as mock_print:

                # Мокаем все обработчики операций
                user_interface.operations_coordinator.handle_vacancy_search = Mock()
                user_interface.operations_coordinator.handle_show_saved_vacancies = Mock()
                user_interface.operations_coordinator.handle_top_vacancies_by_salary = Mock()
                user_interface.operations_coordinator.handle_search_saved_by_keyword = Mock()
                user_interface.operations_coordinator.handle_delete_vacancies = Mock()
                user_interface.operations_coordinator.handle_cache_cleanup = Mock()
                user_interface.operations_coordinator.handle_superjob_setup = Mock()

                # Мокаем storage для расширенного поиска и фильтрации
                user_interface.storage.get_vacancies.return_value = []

                # Мокаем дополнительные методы
                with patch('src.utils.ui_helpers.get_user_input', return_value='') as mock_get_input:

                    menu_result = user_interface._show_menu()
                    assert menu_result == choice

    def test_db_manager_demo_availability(self, user_interface: UserInterface) -> None:
        """Тест доступности демонстрации DBManager"""
        # Проверяем что demo инициализирован если db_manager доступен
        if user_interface.db_manager is not None:
            assert user_interface.demo is not None
        else:
            assert user_interface.demo is None

    def test_storage_operations_delegation(self, user_interface: UserInterface) -> None:
        """Тест делегирования операций с хранилищем"""
        # Проверяем что операции делегируются координатору
        assert hasattr(user_interface, 'operations_coordinator')
        coordinator = user_interface.operations_coordinator

        # Проверяем наличие методов обработки
        assert hasattr(coordinator, 'handle_vacancy_search')
        assert hasattr(coordinator, 'handle_show_saved_vacancies')
        assert hasattr(coordinator, 'handle_top_vacancies_by_salary')
        assert hasattr(coordinator, 'handle_search_saved_by_keyword')
        assert hasattr(coordinator, 'handle_delete_vacancies')
        assert hasattr(coordinator, 'handle_cache_cleanup')

    def test_period_choice_method(self, user_interface: UserInterface) -> None:
        """Тест метода выбора периода"""
        # Тестируем различные варианты выбора периода
        test_cases = [
            ('1', 1),
            ('2', 3),
            ('3', 7),
            ('4', 15),
            ('5', 30),
            ('', 15),  # По умолчанию
            ('0', None),  # Отмена
        ]

        for input_value, expected_result in test_cases:
            with patch('builtins.input', return_value=input_value) as mock_input, \
                 patch('builtins.print') as mock_print:

                result = user_interface._get_period_choice()
                assert result == expected_result

    def test_custom_period_input(self, user_interface: UserInterface) -> None:
        """Тест ввода пользовательского периода"""
        with patch('builtins.input', side_effect=['6', '45']) as mock_input, \
             patch('builtins.print') as mock_print:

            result = user_interface._get_period_choice()
            assert result == 45

    def test_invalid_custom_period(self, user_interface: UserInterface) -> None:
        """Тест неверного пользовательского периода"""
        with patch('builtins.input', side_effect=['6', '999']) as mock_input, \
             patch('builtins.print') as mock_print:

            result = user_interface._get_period_choice()
            assert result == 15  # Должен вернуться к значению по умолчанию

    def test_interface_components_types(self, user_interface: UserInterface) -> None:
        """Тест типов компонентов интерфейса"""
        # Проверяем что все компоненты имеют правильные типы
        from src.api_modules.unified_api import UnifiedAPI
        from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
        from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
        from src.ui_interfaces.vacancy_operations_coordinator import VacancyOperationsCoordinator
        from src.utils.vacancy_operations import VacancyOperations

        assert isinstance(user_interface.unified_api, UnifiedAPI)
        assert isinstance(user_interface.search_handler, VacancySearchHandler)
        assert isinstance(user_interface.display_handler, VacancyDisplayHandler)
        assert isinstance(user_interface.operations_coordinator, VacancyOperationsCoordinator)
        assert isinstance(user_interface.vacancy_ops, VacancyOperations)