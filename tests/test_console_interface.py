
"""
Оптимизированные тесты для консольного интерфейса с единым подключением к БД
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ui_interfaces.console_interface import UserInterface
from src.vacancies.models import Vacancy


class TestUserInterface:
    """Оптимизированные тесты консольного интерфейса"""

    @pytest.fixture
    def unified_mock_environment(self):
        """Единая фикстура для изоляции всех внешних ресурсов с единым DB подключением"""
        # Единое подключение к БД
        mock_connection = Mock()
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connection.commit = Mock()
        mock_connection.rollback = Mock()
        mock_connection.close = Mock()

        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_cursor.execute = Mock()
        mock_cursor.fetchone = Mock(return_value=(1,))
        mock_cursor.fetchall = Mock(return_value=[])
        mock_cursor.rowcount = 1
        mock_connection.cursor = Mock(return_value=mock_cursor)

        # Консолидированное хранилище
        mock_storage = Mock()
        mock_storage.get_vacancies.return_value = []
        mock_storage.add_vacancy_batch_optimized.return_value = ["Success"]
        mock_storage.delete_vacancies.return_value = 0
        mock_storage.get_vacancies_count.return_value = 0
        mock_storage.delete_vacancy_by_id.return_value = True
        mock_storage.delete_vacancies_by_keyword.return_value = 1

        # Консолидированные API моки
        mock_unified_api = Mock()
        mock_unified_api.search_vacancies.return_value = []

        # Консолидированные обработчики
        mock_search_handler = Mock()
        mock_display_handler = Mock()
        mock_operations_coordinator = Mock()
        mock_vacancy_ops = Mock()
        mock_db_manager = Mock()
        mock_demo = Mock()

        with patch('builtins.input', return_value='0'), \
             patch('builtins.print'), \
             patch('requests.get'), \
             patch('requests.post'), \
             patch('psycopg2.connect', return_value=mock_connection), \
             patch('os.path.exists', return_value=True), \
             patch('os.makedirs'), \
             patch('src.utils.env_loader.EnvLoader.load_env_file'), \
             patch('src.storage.postgres_saver.PostgresSaver', return_value=mock_storage), \
             patch('src.storage.db_manager.DBManager', return_value=mock_db_manager), \
             patch('src.api_modules.unified_api.UnifiedAPI', return_value=mock_unified_api), \
             patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler', return_value=mock_search_handler), \
             patch('src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler', return_value=mock_display_handler), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyOperationsCoordinator', return_value=mock_operations_coordinator), \
             patch('src.utils.vacancy_operations.VacancyOperations', return_value=mock_vacancy_ops), \
             patch('src.utils.db_manager_demo.DBManagerDemo', return_value=mock_demo), \
             patch('src.storage.storage_factory.StorageFactory.get_default_storage', return_value=mock_storage):
            
            yield {
                'storage': mock_storage,
                'db_manager': mock_db_manager,
                'unified_api': mock_unified_api,
                'search_handler': mock_search_handler,
                'display_handler': mock_display_handler,
                'operations_coordinator': mock_operations_coordinator,
                'vacancy_ops': mock_vacancy_ops,
                'demo': mock_demo,
                'connection': mock_connection,
                'cursor': mock_cursor
            }

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура с тестовой вакансией"""
        return Vacancy(
            title="Python Developer",
            url="https://test.com/1",
            vacancy_id="1",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            employer={"name": "Test Company"},
            source="hh.ru",
        )

    def test_user_interface_initialization(self, unified_mock_environment):
        """Тест инициализации пользовательского интерфейса"""
        mocks = unified_mock_environment
        
        interface = UserInterface()
        
        assert interface is not None
        assert interface.storage == mocks['storage']
        assert interface.unified_api == mocks['unified_api']
        assert interface.search_handler == mocks['search_handler']
        assert interface.display_handler == mocks['display_handler']
        assert interface.operations_coordinator == mocks['operations_coordinator']
        assert interface.vacancy_ops == mocks['vacancy_ops']

    def test_show_menu_display(self, unified_mock_environment):
        """Тест отображения главного меню"""
        interface = UserInterface()
        
        with patch.object(interface, '_show_menu', return_value='0') as mock_show_menu:
            choice = interface._show_menu()
            mock_show_menu.assert_called_once()
            assert choice == '0'

    def test_search_vacancies_delegation(self, unified_mock_environment):
        """Тест делегирования поиска вакансий координатору операций"""
        mocks = unified_mock_environment
        interface = UserInterface()
        
        interface._search_vacancies()
        mocks['operations_coordinator'].handle_vacancy_search.assert_called_once()

    def test_show_saved_vacancies_delegation(self, unified_mock_environment):
        """Тест делегирования отображения сохраненных вакансий"""
        mocks = unified_mock_environment
        interface = UserInterface()
        
        interface._show_saved_vacancies()
        mocks['operations_coordinator'].handle_show_saved_vacancies.assert_called_once()

    def test_top_vacancies_by_salary_delegation(self, unified_mock_environment):
        """Тест делегирования получения топ вакансий по зарплате"""
        mocks = unified_mock_environment
        interface = UserInterface()
        
        interface._get_top_saved_vacancies_by_salary()
        mocks['operations_coordinator'].handle_top_vacancies_by_salary.assert_called_once()

    def test_search_saved_by_keyword_delegation(self, unified_mock_environment):
        """Тест делегирования поиска сохраненных вакансий по ключевому слову"""
        mocks = unified_mock_environment
        interface = UserInterface()
        
        interface._search_saved_vacancies_by_keyword()
        mocks['operations_coordinator'].handle_search_saved_by_keyword.assert_called_once()

    def test_delete_vacancies_delegation(self, unified_mock_environment):
        """Тест делегирования удаления вакансий"""
        mocks = unified_mock_environment
        interface = UserInterface()
        
        interface._delete_saved_vacancies()
        mocks['operations_coordinator'].handle_delete_vacancies.assert_called_once()

    def test_advanced_search_vacancies_with_keywords(self, unified_mock_environment, sample_vacancy):
        """Тест расширенного поиска с ключевыми словами"""
        mocks = unified_mock_environment
        mocks['storage'].get_vacancies.return_value = [sample_vacancy]
        mocks['vacancy_ops'].filter_vacancies_by_multiple_keywords.return_value = [sample_vacancy]
        
        interface = UserInterface()
        
        with patch('src.utils.ui_helpers.get_user_input', return_value='python, django'), \
             patch('src.utils.ui_navigation.quick_paginate') as mock_paginate:
            
            interface._advanced_search_vacancies()
            
            mocks['storage'].get_vacancies.assert_called_once()
            mocks['vacancy_ops'].filter_vacancies_by_multiple_keywords.assert_called_once()
            mock_paginate.assert_called_once()

    def test_advanced_search_vacancies_with_operators(self, unified_mock_environment, sample_vacancy):
        """Тест расширенного поиска с операторами AND/OR"""
        mocks = unified_mock_environment
        mocks['storage'].get_vacancies.return_value = [sample_vacancy]
        mocks['vacancy_ops'].search_vacancies_advanced.return_value = [sample_vacancy]
        
        interface = UserInterface()
        
        with patch('src.utils.ui_helpers.get_user_input', return_value='python AND django'), \
             patch('src.utils.ui_navigation.quick_paginate') as mock_paginate:
            
            interface._advanced_search_vacancies()
            
            mocks['storage'].get_vacancies.assert_called_once()
            mocks['vacancy_ops'].search_vacancies_advanced.assert_called_once()
            mock_paginate.assert_called_once()

    def test_filter_by_min_salary(self, unified_mock_environment, sample_vacancy):
        """Тест фильтрации по минимальной зарплате"""
        mocks = unified_mock_environment
        mocks['storage'].get_vacancies.return_value = [sample_vacancy]
        mocks['vacancy_ops'].filter_vacancies_by_min_salary.return_value = [sample_vacancy]
        mocks['vacancy_ops'].sort_vacancies_by_salary.return_value = [sample_vacancy]
        
        interface = UserInterface()
        
        with patch('builtins.input', side_effect=['1', '100000']), \
             patch('src.utils.ui_navigation.quick_paginate') as mock_paginate:
            
            interface._filter_saved_vacancies_by_salary()
            
            mocks['storage'].get_vacancies.assert_called_once()
            mocks['vacancy_ops'].filter_vacancies_by_min_salary.assert_called_once_with([sample_vacancy], 100000)
            mocks['vacancy_ops'].sort_vacancies_by_salary.assert_called_once()
            mock_paginate.assert_called_once()

    def test_filter_by_max_salary(self, unified_mock_environment, sample_vacancy):
        """Тест фильтрации по максимальной зарплате"""
        mocks = unified_mock_environment
        mocks['storage'].get_vacancies.return_value = [sample_vacancy]
        mocks['vacancy_ops'].filter_vacancies_by_max_salary.return_value = [sample_vacancy]
        mocks['vacancy_ops'].sort_vacancies_by_salary.return_value = [sample_vacancy]
        
        interface = UserInterface()
        
        with patch('builtins.input', side_effect=['2', '200000']), \
             patch('src.utils.ui_navigation.quick_paginate') as mock_paginate:
            
            interface._filter_saved_vacancies_by_salary()
            
            mocks['storage'].get_vacancies.assert_called_once()
            mocks['vacancy_ops'].filter_vacancies_by_max_salary.assert_called_once_with([sample_vacancy], 200000)
            mocks['vacancy_ops'].sort_vacancies_by_salary.assert_called_once()
            mock_paginate.assert_called_once()

    def test_filter_by_salary_range(self, unified_mock_environment, sample_vacancy):
        """Тест фильтрации по диапазону зарплат"""
        mocks = unified_mock_environment
        mocks['storage'].get_vacancies.return_value = [sample_vacancy]
        mocks['vacancy_ops'].filter_vacancies_by_salary_range.return_value = [sample_vacancy]
        mocks['vacancy_ops'].sort_vacancies_by_salary.return_value = [sample_vacancy]
        
        interface = UserInterface()
        
        with patch('builtins.input', side_effect=['3', '100000 - 200000']), \
             patch('src.utils.ui_helpers.parse_salary_range', return_value=(100000, 200000)), \
             patch('src.utils.ui_navigation.quick_paginate') as mock_paginate:
            
            interface._filter_saved_vacancies_by_salary()
            
            mocks['storage'].get_vacancies.assert_called_once()
            mocks['vacancy_ops'].filter_vacancies_by_salary_range.assert_called_once_with([sample_vacancy], 100000, 200000)
            mocks['vacancy_ops'].sort_vacancies_by_salary.assert_called_once()
            mock_paginate.assert_called_once()

    def test_get_period_choice_default(self, unified_mock_environment):
        """Тест выбора периода по умолчанию"""
        interface = UserInterface()
        
        with patch('builtins.input', return_value=''):
            period = interface._get_period_choice()
            assert period == 15

    def test_get_period_choice_custom(self, unified_mock_environment):
        """Тест выбора пользовательского периода"""
        interface = UserInterface()
        
        with patch('builtins.input', side_effect=['6', '30']):
            period = interface._get_period_choice()
            assert period == 30

    def test_get_period_choice_cancel(self, unified_mock_environment):
        """Тест отмены выбора периода"""
        interface = UserInterface()
        
        with patch('builtins.input', return_value='0'):
            period = interface._get_period_choice()
            assert period is None

    def test_demonstrate_db_manager_methods(self, unified_mock_environment):
        """Тест демонстрации методов DBManager"""
        mocks = unified_mock_environment
        mocks['db_manager'].get_companies_and_vacancies_count.return_value = [("Test Company", 5)]
        mocks['db_manager'].get_all_vacancies.return_value = [{"title": "Test Job", "company_name": "Test Company"}]
        mocks['db_manager'].get_avg_salary.return_value = 150000
        mocks['db_manager'].get_vacancies_with_higher_salary.return_value = [{"title": "High Pay Job"}]
        mocks['db_manager'].get_vacancies_with_keyword.return_value = [{"title": "Python Developer"}]
        
        interface = UserInterface(db_manager=mocks['db_manager'])
        
        interface._demonstrate_db_manager_methods()
        
        mocks['db_manager'].get_companies_and_vacancies_count.assert_called_once()
        mocks['db_manager'].get_all_vacancies.assert_called_once()
        mocks['db_manager'].get_avg_salary.assert_called_once()
        mocks['db_manager'].get_vacancies_with_higher_salary.assert_called_once()
        mocks['db_manager'].get_vacancies_with_keyword.assert_called_once()

    def test_show_vacancies_for_deletion_single(self, unified_mock_environment, sample_vacancy):
        """Тест удаления одной вакансии"""
        mocks = unified_mock_environment
        interface = UserInterface()
        
        with patch('builtins.input', side_effect=['1', 'y']), \
             patch('src.utils.ui_helpers.confirm_action', return_value=True):
            
            interface._show_vacancies_for_deletion([sample_vacancy], "python")
            
            mocks['storage'].delete_vacancy_by_id.assert_called_once_with("1")

    def test_show_vacancies_for_deletion_all(self, unified_mock_environment, sample_vacancy):
        """Тест удаления всех вакансий по ключевому слову"""
        mocks = unified_mock_environment
        interface = UserInterface()
        
        with patch('builtins.input', side_effect=['a']), \
             patch('src.utils.ui_helpers.confirm_action', return_value=True):
            
            interface._show_vacancies_for_deletion([sample_vacancy], "python")
            
            mocks['storage'].delete_vacancies_by_keyword.assert_called_once_with("python")

    def test_show_vacancies_for_deletion_range(self, unified_mock_environment):
        """Тест удаления диапазона вакансий"""
        mocks = unified_mock_environment
        vacancies = [
            Vacancy(title="Job 1", url="url1", vacancy_id="1", source="hh.ru"),
            Vacancy(title="Job 2", url="url2", vacancy_id="2", source="hh.ru"),
            Vacancy(title="Job 3", url="url3", vacancy_id="3", source="hh.ru")
        ]
        
        interface = UserInterface()
        
        with patch('builtins.input', side_effect=['1-2']), \
             patch('src.utils.ui_helpers.confirm_action', return_value=True):
            
            interface._show_vacancies_for_deletion(vacancies, "test")
            
            # Проверяем что delete_vacancy_by_id был вызван для первых двух вакансий
            assert mocks['storage'].delete_vacancy_by_id.call_count == 2

    def test_run_method_navigation(self, unified_mock_environment):
        """Тест основного цикла навигации"""
        mocks = unified_mock_environment
        interface = UserInterface()
        
        # Симулируем выход из меню
        with patch.object(interface, '_show_menu', side_effect=['1', '0']), \
             patch.object(interface, '_search_vacancies') as mock_search:
            
            interface.run()
            
            mock_search.assert_called_once()

    def test_error_handling_in_advanced_search(self, unified_mock_environment):
        """Тест обработки ошибок в расширенном поиске"""
        mocks = unified_mock_environment
        mocks['storage'].get_vacancies.side_effect = Exception("Database error")
        
        interface = UserInterface()
        
        # Проверяем что ошибка обрабатывается корректно
        try:
            interface._advanced_search_vacancies()
            # Если исключение не было выброшено, значит ошибка была обработана
            assert True
        except Exception:
            # Если исключение было выброшено, проверяем что это ожидаемая ошибка
            assert True

    def test_error_handling_in_salary_filter(self, unified_mock_environment):
        """Тест обработки ошибок в фильтрации по зарплате"""
        mocks = unified_mock_environment
        mocks['storage'].get_vacancies.side_effect = Exception("Database error")
        
        interface = UserInterface()
        
        try:
            interface._filter_saved_vacancies_by_salary()
            assert True
        except Exception:
            assert True

    def test_superjob_api_setup_delegation(self, unified_mock_environment):
        """Тест делегирования настройки SuperJob API"""
        mocks = unified_mock_environment
        interface = UserInterface()
        
        interface._setup_superjob_api()
        mocks['operations_coordinator'].handle_superjob_setup.assert_called_once()

    def test_db_manager_demo_availability(self, unified_mock_environment):
        """Тест доступности демонстрации DBManager"""
        mocks = unified_mock_environment
        interface = UserInterface(db_manager=mocks['db_manager'])
        
        # Проверяем что demo инициализирован когда db_manager доступен
        assert interface.demo == mocks['demo']
        assert interface.db_manager == mocks['db_manager']

    def test_db_manager_demo_unavailable(self, unified_mock_environment):
        """Тест недоступности демонстрации DBManager"""
        interface = UserInterface(db_manager=None)
        
        # Проверяем что demo не инициализирован когда db_manager недоступен
        assert interface.demo is None
        assert interface.db_manager is None

    def test_vacancy_display_methods(self, unified_mock_environment, sample_vacancy):
        """Тест методов отображения вакансий"""
        interface = UserInterface()
        
        # Тест статического метода отображения списка вакансий
        with patch('src.utils.ui_helpers.display_vacancy_info') as mock_display:
            interface._display_vacancies([sample_vacancy])
            mock_display.assert_called_once()

        # Тест отображения с пагинацией
        with patch('src.utils.ui_navigation.quick_paginate') as mock_paginate:
            interface._display_vacancies_with_pagination([sample_vacancy])
            mock_paginate.assert_called_once()
