
"""
Полные тесты для модуля пользовательского интерфейса
"""

import os
import sys
from typing import List, Dict, Any, Optional
from unittest.mock import MagicMock, Mock, patch, call
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт из реального кода
from src.user_interface import UserInterface
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestUserInterfaceComprehensive:
    """Полные тесты для класса пользовательского интерфейса"""

    @pytest.fixture
    def mock_storage(self) -> Mock:
        """Создание мока хранилища"""
        storage = Mock()
        storage.get_vacancies.return_value = []
        storage.save_vacancy.return_value = True
        storage.delete_vacancy_by_id.return_value = True
        storage.delete_vacancies_by_keyword.return_value = 5
        return storage

    @pytest.fixture
    def mock_db_manager(self) -> Mock:
        """Создание мока DB менеджера"""
        db_manager = Mock()
        db_manager.check_connection.return_value = True
        db_manager.get_companies_and_vacancies_count.return_value = []
        db_manager.get_all_vacancies.return_value = []
        db_manager.get_avg_salary.return_value = 100000.0
        return db_manager

    @pytest.fixture 
    def user_interface(self, mock_storage, mock_db_manager) -> UserInterface:
        """Создание экземпляра пользовательского интерфейса"""
        with patch('src.user_interface.StorageFactory.get_default_storage', return_value=mock_storage):
            return UserInterface(storage=mock_storage, db_manager=mock_db_manager)

    @pytest.fixture
    def sample_vacancies(self) -> List[Vacancy]:
        """Создание тестовых вакансий"""
        vacancies = []
        
        # Вакансия с полной информацией
        salary1 = Salary(salary_from=100000, salary_to=150000, currency="RUR")
        vacancy1 = Vacancy(
            title="Python Developer",
            vacancy_id="1",
            url="https://example.com/1",
            source="hh.ru",
            employer={"name": "Яндекс"},
            salary=salary1,
            description="Разработка на Python"
        )
        vacancies.append(vacancy1)
        
        # Вакансия без зарплаты
        vacancy2 = Vacancy(
            title="Frontend Developer", 
            vacancy_id="2",
            url="https://example.com/2",
            source="superjob.ru",
            employer={"name": "Тинькофф"},
            salary=None,
            description="Разработка интерфейсов"
        )
        vacancies.append(vacancy2)
        
        return vacancies

    def test_user_interface_initialization(self, user_interface):
        """Тест инициализации пользовательского интерфейса"""
        assert user_interface is not None
        assert hasattr(user_interface, 'run')
        assert hasattr(user_interface, 'storage')
        assert hasattr(user_interface, 'unified_api')
        assert hasattr(user_interface, 'operations_coordinator')

    @patch('builtins.input', side_effect=['0'])  # Выход из меню
    @patch('builtins.print')
    def test_run_main_loop_exit(self, mock_print, mock_input, user_interface):
        """Тест основного цикла с выходом"""
        user_interface.run()
        
        # Проверяем что приветствие было выведено
        assert mock_print.called
        
        # Проверяем что input был вызван для получения выбора пользователя
        assert mock_input.called

    @patch('builtins.input', side_effect=['1', '0'])  # Поиск, затем выход
    @patch('builtins.print')
    def test_run_search_vacancies(self, mock_print, mock_input, user_interface):
        """Тест запуска поиска вакансий"""
        # Мокаем метод поиска в operations_coordinator
        user_interface.operations_coordinator.handle_vacancy_search = Mock()
        
        user_interface.run()
        
        # Проверяем что поиск был вызван
        assert user_interface.operations_coordinator.handle_vacancy_search.called

    @patch('builtins.input', side_effect=['2', '0'])  # Показать сохраненные, затем выход
    @patch('builtins.print')
    def test_run_show_saved_vacancies(self, mock_print, mock_input, user_interface):
        """Тест показа сохраненных вакансий"""
        user_interface.operations_coordinator.handle_show_saved_vacancies = Mock()
        
        user_interface.run()
        
        assert user_interface.operations_coordinator.handle_show_saved_vacancies.called

    @patch('builtins.input', side_effect=['3', '0'])  # Топ по зарплате, затем выход
    @patch('builtins.print') 
    def test_run_top_vacancies_by_salary(self, mock_print, mock_input, user_interface):
        """Тест получения топ вакансий по зарплате"""
        user_interface.operations_coordinator.handle_top_vacancies_by_salary = Mock()
        
        user_interface.run()
        
        assert user_interface.operations_coordinator.handle_top_vacancies_by_salary.called

    @patch('builtins.input', side_effect=['4', '0'])  # Поиск по ключевому слову, затем выход
    @patch('builtins.print')
    def test_run_search_by_keyword(self, mock_print, mock_input, user_interface):
        """Тест поиска по ключевому слову"""
        user_interface.operations_coordinator.handle_search_saved_by_keyword = Mock()
        
        user_interface.run()
        
        assert user_interface.operations_coordinator.handle_search_saved_by_keyword.called

    @patch('builtins.input', side_effect=['5', 'python django', '0'])  # Расширенный поиск, затем выход
    @patch('builtins.print')
    def test_run_advanced_search(self, mock_print, mock_input, user_interface, sample_vacancies):
        """Тест расширенного поиска"""
        # Настраиваем storage для возврата тестовых вакансий
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        
        # Мокаем vacancy_ops
        user_interface.vacancy_ops = Mock()
        user_interface.vacancy_ops.filter_vacancies_by_multiple_keywords.return_value = sample_vacancies[:1]
        
        user_interface.run()
        
        # Проверяем что расширенный поиск был выполнен
        assert user_interface.storage.get_vacancies.called

    @patch('builtins.input', side_effect=['6', '1', '100000', '0'])  # Фильтр по зарплате, затем выход
    @patch('builtins.print')
    def test_run_salary_filter(self, mock_print, mock_input, user_interface, sample_vacancies):
        """Тест фильтрации по зарплате"""
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        user_interface.vacancy_ops = Mock()
        user_interface.vacancy_ops.filter_vacancies_by_min_salary.return_value = sample_vacancies[:1]
        user_interface.vacancy_ops.sort_vacancies_by_salary.return_value = sample_vacancies[:1]
        
        user_interface.run()
        
        assert user_interface.storage.get_vacancies.called

    @patch('builtins.input', side_effect=['7', '0'])  # Удаление, затем выход
    @patch('builtins.print')
    def test_run_delete_vacancies(self, mock_print, mock_input, user_interface):
        """Тест удаления вакансий"""
        user_interface.operations_coordinator.handle_delete_vacancies = Mock()
        
        user_interface.run()
        
        assert user_interface.operations_coordinator.handle_delete_vacancies.called

    @patch('builtins.input', side_effect=['8', '0'])  # Очистка кэша, затем выход
    @patch('builtins.print')
    def test_run_cache_cleanup(self, mock_print, mock_input, user_interface):
        """Тест очистки кэша"""
        user_interface.operations_coordinator.handle_cache_cleanup = Mock()
        
        user_interface.run()
        
        assert user_interface.operations_coordinator.handle_cache_cleanup.called

    @patch('builtins.input', side_effect=['9', '0'])  # Настройка SuperJob, затем выход
    @patch('builtins.print')
    def test_run_superjob_setup(self, mock_print, mock_input, user_interface):
        """Тест настройки SuperJob API"""
        user_interface.operations_coordinator.handle_superjob_setup = Mock()
        
        user_interface.run()
        
        assert user_interface.operations_coordinator.handle_superjob_setup.called

    @patch('builtins.input', side_effect=['10', '0'])  # DB Demo, затем выход
    @patch('builtins.print')
    def test_run_db_demo(self, mock_print, mock_input, user_interface):
        """Тест демонстрации DBManager"""
        # Мокаем demo объект
        user_interface.demo = Mock()
        user_interface.demo.run_full_demo = Mock()
        
        user_interface.run()
        
        assert user_interface.demo.run_full_demo.called

    @patch('builtins.input', side_effect=['invalid', '0'])  # Неверный выбор, затем выход
    @patch('builtins.print')
    def test_run_invalid_choice(self, mock_print, mock_input, user_interface):
        """Тест обработки неверного выбора в меню"""
        user_interface.run()
        
        # Проверяем что было сообщение об ошибке
        error_messages = [str(call) for call in mock_print.call_args_list]
        error_found = any("неверный" in msg.lower() or "неправильный" in msg.lower() for msg in error_messages)
        assert error_found

    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input, user_interface):
        """Тест обработки прерывания клавиатурой"""
        user_interface.run()
        
        # Проверяем что прерывание было обработано
        assert mock_print.called

    def test_show_menu_method(self, user_interface):
        """Тест метода показа меню"""
        with patch('builtins.input', return_value='1') as mock_input:
            with patch('builtins.print'):
                choice = user_interface._show_menu()
        
        assert choice == '1'
        assert mock_input.called

    def test_get_period_choice_method(self, user_interface):
        """Тест метода выбора периода"""
        with patch('builtins.input', return_value='4') as mock_input:
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
        
        assert period == 15  # По умолчанию 15 дней для выбора '4'

    def test_get_period_choice_custom(self, user_interface):
        """Тест выбора пользовательского периода"""
        with patch('builtins.input', side_effect=['6', '21']) as mock_input:
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
        
        assert period == 21

    def test_get_period_choice_cancel(self, user_interface):
        """Тест отмены выбора периода"""
        with patch('builtins.input', return_value='0') as mock_input:
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
        
        assert period is None

    def test_display_vacancies_static_method(self, sample_vacancies):
        """Тест статического метода отображения вакансий"""
        with patch('builtins.print') as mock_print:
            UserInterface._display_vacancies(sample_vacancies)
        
        # Проверяем что print был вызван для каждой вакансии
        assert mock_print.call_count > 0

    def test_display_vacancies_with_pagination_static_method(self, sample_vacancies):
        """Тест статического метода отображения с пагинацией"""
        with patch('src.user_interface.quick_paginate') as mock_paginate:
            UserInterface._display_vacancies_with_pagination(sample_vacancies)
        
        assert mock_paginate.called

    def test_advanced_search_with_comma_separated_keywords(self, user_interface, sample_vacancies):
        """Тест расширенного поиска с ключевыми словами через запятую"""
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        user_interface.vacancy_ops = Mock()
        user_interface.vacancy_ops.filter_vacancies_by_multiple_keywords.return_value = sample_vacancies[:1]
        
        with patch('builtins.input', return_value='python, django'):
            with patch('builtins.print'):
                with patch('src.user_interface.get_user_input', return_value='python, django'):
                    user_interface._advanced_search_vacancies()
        
        assert user_interface.vacancy_ops.filter_vacancies_by_multiple_keywords.called

    def test_advanced_search_with_and_operator(self, user_interface, sample_vacancies):
        """Тест расширенного поиска с оператором AND"""
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        user_interface.vacancy_ops = Mock()
        user_interface.vacancy_ops.search_vacancies_advanced.return_value = sample_vacancies[:1]
        
        with patch('src.user_interface.get_user_input', return_value='python AND django'):
            with patch('builtins.print'):
                user_interface._advanced_search_vacancies()
        
        assert user_interface.vacancy_ops.search_vacancies_advanced.called

    def test_salary_filter_min_salary(self, user_interface, sample_vacancies):
        """Тест фильтрации по минимальной зарплате"""
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        user_interface.vacancy_ops = Mock()
        user_interface.vacancy_ops.filter_vacancies_by_min_salary.return_value = sample_vacancies[:1]
        user_interface.vacancy_ops.sort_vacancies_by_salary.return_value = sample_vacancies[:1]
        
        with patch('builtins.input', side_effect=['1', '100000']):
            with patch('builtins.print'):
                user_interface._filter_saved_vacancies_by_salary()
        
        assert user_interface.vacancy_ops.filter_vacancies_by_min_salary.called

    def test_salary_filter_max_salary(self, user_interface, sample_vacancies):
        """Тест фильтрации по максимальной зарплате"""
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        user_interface.vacancy_ops = Mock()
        user_interface.vacancy_ops.filter_vacancies_by_max_salary.return_value = sample_vacancies[:1]
        user_interface.vacancy_ops.sort_vacancies_by_salary.return_value = sample_vacancies[:1]
        
        with patch('builtins.input', side_effect=['2', '200000']):
            with patch('builtins.print'):
                user_interface._filter_saved_vacancies_by_salary()
        
        assert user_interface.vacancy_ops.filter_vacancies_by_max_salary.called

    def test_salary_filter_range(self, user_interface, sample_vacancies):
        """Тест фильтрации по диапазону зарплат"""
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        user_interface.vacancy_ops = Mock()
        user_interface.vacancy_ops.filter_vacancies_by_salary_range.return_value = sample_vacancies[:1]
        user_interface.vacancy_ops.sort_vacancies_by_salary.return_value = sample_vacancies[:1]
        
        with patch('builtins.input', side_effect=['3', '100000 - 200000']):
            with patch('builtins.print'):
                with patch('src.user_interface.parse_salary_range', return_value=(100000, 200000)):
                    user_interface._filter_saved_vacancies_by_salary()
        
        assert user_interface.vacancy_ops.filter_vacancies_by_salary_range.called

    def test_show_vacancies_for_deletion_navigation(self, user_interface, sample_vacancies):
        """Тест навигации при показе вакансий для удаления"""
        with patch('builtins.input', side_effect=['q']):  # Выход из меню удаления
            with patch('builtins.print'):
                with patch('src.user_interface.confirm_action', return_value=False):
                    user_interface._show_vacancies_for_deletion(sample_vacancies, "python")

    def test_show_vacancies_for_deletion_delete_all(self, user_interface, sample_vacancies):
        """Тест удаления всех вакансий с ключевым словом"""
        user_interface.storage.delete_vacancies_by_keyword.return_value = 5
        
        with patch('builtins.input', side_effect=['a']):  # Удалить все
            with patch('builtins.print'):
                with patch('src.user_interface.confirm_action', return_value=True):
                    user_interface._show_vacancies_for_deletion(sample_vacancies, "python")
        
        assert user_interface.storage.delete_vacancies_by_keyword.called

    def test_show_vacancies_for_deletion_delete_single(self, user_interface, sample_vacancies):
        """Тест удаления одной вакансии"""
        user_interface.storage.delete_vacancy_by_id.return_value = True
        
        with patch('builtins.input', side_effect=['1']):  # Удалить первую вакансию
            with patch('builtins.print'):
                with patch('src.user_interface.confirm_action', return_value=True):
                    user_interface._show_vacancies_for_deletion(sample_vacancies, "python")
        
        assert user_interface.storage.delete_vacancy_by_id.called

    def test_show_vacancies_for_deletion_delete_range(self, user_interface, sample_vacancies):
        """Тест удаления диапазона вакансий"""
        user_interface.storage.delete_vacancy_by_id.return_value = True
        
        with patch('builtins.input', side_effect=['1-2']):  # Удалить диапазон 1-2
            with patch('builtins.print'):
                with patch('src.user_interface.confirm_action', return_value=True):
                    user_interface._show_vacancies_for_deletion(sample_vacancies, "python")
        
        # Должен быть вызван для каждой вакансии в диапазоне
        assert user_interface.storage.delete_vacancy_by_id.call_count >= 1

    def test_configure_superjob_api_static_method(self):
        """Тест статического метода настройки SuperJob API"""
        with patch('builtins.input'):
            with patch('builtins.print') as mock_print:
                with patch.dict(os.environ, {"SUPERJOB_API_KEY": "test_key"}):
                    UserInterface._configure_superjob_api()
        
        assert mock_print.called

    def test_setup_superjob_api_method(self, user_interface):
        """Тест метода настройки SuperJob API"""
        user_interface.operations_coordinator.handle_superjob_setup = Mock()
        
        user_interface._setup_superjob_api()
        
        assert user_interface.operations_coordinator.handle_superjob_setup.called

    def test_demo_db_manager_method(self, user_interface):
        """Тест метода демонстрации DBManager"""
        user_interface.demo = Mock()
        user_interface.demo.run_full_demo = Mock()
        
        with patch('builtins.input'):
            with patch('builtins.print'):
                user_interface._demo_db_manager()
        
        assert user_interface.demo.run_full_demo.called

    def test_demo_db_manager_without_demo_object(self, user_interface):
        """Тест демонстрации DBManager без demo объекта"""
        user_interface.demo = None
        
        with patch('builtins.input'):
            with patch('builtins.print') as mock_print:
                user_interface._demo_db_manager()
        
        # Должно быть сообщение о недоступности БД
        assert mock_print.called

    def test_error_handling_in_main_loop(self, user_interface):
        """Тест обработки ошибок в основном цикле"""
        # Мокаем метод, который выбрасывает исключение
        user_interface.operations_coordinator.handle_vacancy_search = Mock(side_effect=Exception("Test error"))
        
        with patch('builtins.input', side_effect=['1', '0']):  # Поиск с ошибкой, затем выход
            with patch('builtins.print') as mock_print:
                user_interface.run()
        
        # Проверяем что ошибка была обработана и программа продолжила работу
        assert mock_print.called

    def test_advanced_search_empty_query(self, user_interface, sample_vacancies):
        """Тест расширенного поиска с пустым запросом"""
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        
        with patch('src.user_interface.get_user_input', return_value=''):
            with patch('builtins.print'):
                user_interface._advanced_search_vacancies()
        
        # При пустом запросе метод должен завершиться без поиска
        assert user_interface.storage.get_vacancies.called

    def test_advanced_search_no_saved_vacancies(self, user_interface):
        """Тест расширенного поиска без сохраненных вакансий"""
        user_interface.storage.get_vacancies.return_value = []
        
        with patch('builtins.print') as mock_print:
            user_interface._advanced_search_vacancies()
        
        # Должно быть сообщение об отсутствии вакансий
        assert mock_print.called

    def test_salary_filter_no_saved_vacancies(self, user_interface):
        """Тест фильтрации зарплат без сохраненных вакансий"""
        user_interface.storage.get_vacancies.return_value = []
        
        with patch('builtins.print') as mock_print:
            user_interface._filter_saved_vacancies_by_salary()
        
        # Должно быть сообщение об отсутствии вакансий
        assert mock_print.called

    def test_salary_filter_invalid_input(self, user_interface, sample_vacancies):
        """Тест фильтрации зарплат с некорректным вводом"""
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        
        with patch('builtins.input', side_effect=['1', 'not_a_number']):
            with patch('builtins.print') as mock_print:
                user_interface._filter_saved_vacancies_by_salary()
        
        # Должно быть сообщение об ошибке
        assert mock_print.called

    def test_user_interface_components_integration(self, user_interface):
        """Тест интеграции компонентов пользовательского интерфейса"""
        # Проверяем что все компоненты инициализированы
        assert user_interface.unified_api is not None
        assert user_interface.storage is not None  
        assert user_interface.menu_manager is not None
        assert user_interface.vacancy_ops is not None
        assert user_interface.search_handler is not None
        assert user_interface.display_handler is not None
        assert user_interface.operations_coordinator is not None

    def test_period_choice_edge_cases(self, user_interface):
        """Тест граничных случаев выбора периода"""
        # Тест с пустым вводом (должен использовать значение по умолчанию)
        with patch('builtins.input', return_value=''):
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
        
        assert period == 15  # Значение по умолчанию
        
        # Тест с некорректным вводом для пользовательского периода
        with patch('builtins.input', side_effect=['6', '999']):
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
        
        assert period == 15  # Возврат к значению по умолчанию при некорректном вводе
        
        # Тест с отрицательным числом
        with patch('builtins.input', side_effect=['6', '-5']):
            with patch('builtins.print'):
                period = user_interface._get_period_choice()
        
        assert period == 15  # Возврат к значению по умолчанию

    def test_salary_range_parsing_edge_cases(self, user_interface, sample_vacancies):
        """Тест граничных случаев парсинга диапазона зарплат"""
        user_interface.storage.get_vacancies.return_value = sample_vacancies
        
        # Тест с некорректным форматом диапазона
        with patch('builtins.input', side_effect=['3', 'invalid range']):
            with patch('builtins.print'):
                with patch('src.user_interface.parse_salary_range', return_value=None):
                    user_interface._filter_saved_vacancies_by_salary()
        
        # Метод должен завершиться без ошибки при некорректном диапазоне
        assert user_interface.storage.get_vacancies.called

    def test_exception_handling_in_methods(self, user_interface):
        """Тест обработки исключений в методах интерфейса"""
        # Настраиваем storage для выброса исключения
        user_interface.storage.get_vacancies.side_effect = Exception("Storage error")
        
        with patch('builtins.print') as mock_print:
            user_interface._advanced_search_vacancies()
        
        # Исключение должно быть обработано
        assert mock_print.called

    def test_interface_with_none_components(self):
        """Тест интерфейса с None компонентами"""
        with patch('src.user_interface.StorageFactory.get_default_storage', return_value=Mock()):
            # Создаем интерфейс с None db_manager
            ui = UserInterface(storage=None, db_manager=None)
            
            assert ui is not None
            assert ui.storage is not None  # Должен использовать default storage
            assert ui.db_manager is None
            assert ui.demo is None  # Demo не должен быть создан без db_manager

    def test_menu_display_with_db_manager(self, user_interface):
        """Тест отображения меню с доступным DBManager"""
        user_interface.db_manager = Mock()
        user_interface.demo = Mock()
        
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print') as mock_print:
                choice = user_interface._show_menu()
        
        # Проверяем что в меню есть пункт демонстрации DBManager
        menu_text = " ".join([str(call) for call in mock_print.call_args_list])
        assert "демонстрация" in menu_text.lower() or "dbmanager" in menu_text.lower()

    def test_menu_display_without_db_manager(self, mock_storage):
        """Тест отображения меню без DBManager"""
        with patch('src.user_interface.StorageFactory.get_default_storage', return_value=mock_storage):
            ui = UserInterface(storage=mock_storage, db_manager=None)
        
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print') as mock_print:
                choice = ui._show_menu()
        
        # Меню должно отображаться даже без DBManager
        assert mock_print.called
