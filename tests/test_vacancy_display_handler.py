
"""
Тесты для модуля VacancyDisplayHandler
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.vacancies.models import Vacancy


class TestVacancyDisplayHandler:
    """Тесты для класса VacancyDisplayHandler"""

    @pytest.fixture
    def mock_storage(self):
        """Фикстура mock storage"""
        storage = Mock()
        storage.get_vacancies.return_value = []
        return storage

    @pytest.fixture
    def display_handler(self, mock_storage):
        """Фикстура VacancyDisplayHandler"""
        return VacancyDisplayHandler(mock_storage)

    @pytest.fixture
    def sample_vacancies(self):
        """Фикстура с примерами вакансий"""
        return [
            Vacancy(
                title="Python Developer",
                url="https://example.com/1",
                vacancy_id="1",
                salary={"from": 100000, "to": 150000, "currency": "RUR"},
                source="hh.ru"
            ),
            Vacancy(
                title="Java Developer", 
                url="https://example.com/2",
                vacancy_id="2",
                salary={"from": 120000, "to": 180000, "currency": "RUR"},
                source="superjob.ru"
            )
        ]

    def test_display_handler_initialization(self, display_handler, mock_storage):
        """Тест инициализации VacancyDisplayHandler"""
        assert display_handler.storage == mock_storage
        assert hasattr(display_handler, 'vacancy_ops')

    @patch('builtins.print')
    def test_show_all_saved_vacancies_empty(self, mock_print, display_handler, mock_storage):
        """Тест отображения всех вакансий - пустой список"""
        mock_storage.get_vacancies.return_value = []
        
        display_handler.show_all_saved_vacancies()
        
        # Проверяем, что print был вызван с сообщением о пустом списке
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(print_calls)
        assert "вакансий" in output.lower()

    @patch('src.utils.ui_navigation.quick_paginate')
    @patch('builtins.input', return_value='')  # Мокаем input для избежания блокировки
    def test_show_all_saved_vacancies_with_data(self, mock_input, mock_paginate, display_handler, mock_storage, sample_vacancies):
        """Тест отображения всех вакансий - с данными"""
        mock_storage.get_vacancies.return_value = sample_vacancies
        
        # Настраиваем quick_paginate чтобы не блокировать выполнение
        mock_paginate.return_value = None
        
        display_handler.show_all_saved_vacancies()
        
        # Проверяем, что quick_paginate был вызван
        mock_paginate.assert_called_once()
        args, kwargs = mock_paginate.call_args
        assert len(args[0]) == len(sample_vacancies)

    @patch('src.utils.ui_helpers.get_positive_integer')
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary_empty(self, mock_print, mock_get_int, display_handler, mock_storage):
        """Тест отображения топ вакансий по зарплате - пустой список"""
        mock_get_int.return_value = 10
        mock_storage.get_vacancies.return_value = []
        
        display_handler.show_top_vacancies_by_salary()
        
        mock_get_int.assert_called_once()
        mock_print.assert_called()

    @patch('src.utils.ui_helpers.get_positive_integer')
    @patch('src.utils.ui_navigation.quick_paginate')
    @patch('builtins.input', return_value='')  # Мокаем input
    def test_show_top_vacancies_by_salary_with_data(self, mock_input, mock_paginate, mock_get_int, display_handler, mock_storage, sample_vacancies):
        """Тест отображения топ вакансий по зарплате - с данными"""
        mock_get_int.return_value = 10
        mock_storage.get_vacancies.return_value = sample_vacancies
        mock_paginate.return_value = None
        
        display_handler.show_top_vacancies_by_salary()
        
        mock_get_int.assert_called_once()
        mock_paginate.assert_called_once()

    @patch('src.utils.ui_helpers.get_user_input')
    @patch('src.utils.ui_navigation.quick_paginate')
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    @patch('builtins.input', return_value='')  # Мокаем input
    def test_search_saved_vacancies_by_keyword_found(self, mock_input, mock_filter, mock_paginate, mock_get_input, display_handler, mock_storage, sample_vacancies):
        """Тест поиска сохраненных вакансий по ключевому слову - найдены"""
        mock_get_input.return_value = 'python'
        mock_storage.get_vacancies.return_value = sample_vacancies
        mock_filter.return_value = [sample_vacancies[0]]  # Возвращаем Python вакансию
        mock_paginate.return_value = None
        
        display_handler.search_saved_vacancies_by_keyword()
        
        mock_get_input.assert_called_once()
        mock_filter.assert_called_once_with(sample_vacancies, 'python')
        mock_paginate.assert_called_once()

    @patch('src.utils.ui_helpers.get_user_input')
    @patch('builtins.print')
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    def test_search_saved_vacancies_by_keyword_not_found(self, mock_filter, mock_print, mock_get_input, display_handler, mock_storage, sample_vacancies):
        """Тест поиска сохраненных вакансий по ключевому слову - не найдены"""
        mock_get_input.return_value = 'nonexistent'
        mock_storage.get_vacancies.return_value = sample_vacancies
        mock_filter.return_value = []  # Ничего не найдено
        
        display_handler.search_saved_vacancies_by_keyword()
        
        mock_get_input.assert_called_once()
        mock_filter.assert_called_once_with(sample_vacancies, 'nonexistent')
        mock_print.assert_called()

    @patch('src.utils.ui_helpers.get_user_input')
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_empty_query(self, mock_print, mock_get_input, display_handler, mock_storage):
        """Тест поиска сохраненных вакансий по ключевому слову - пустой запрос"""
        mock_get_input.return_value = None
        mock_storage.get_vacancies.return_value = []
        
        display_handler.search_saved_vacancies_by_keyword()
        
        # Проверяем что функция завершилась корректно
        mock_get_input.assert_called_once()

    @patch('src.utils.ui_helpers.get_user_input')
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_no_saved_vacancies(self, mock_print, mock_get_input, display_handler, mock_storage):
        """Тест поиска сохраненных вакансий - нет сохраненных вакансий"""
        mock_get_input.return_value = 'python'
        mock_storage.get_vacancies.return_value = []
        
        display_handler.search_saved_vacancies_by_keyword()
        
        mock_print.assert_called()
        mock_get_input.assert_called_once()

    def test_display_handler_has_vacancy_operations(self, display_handler):
        """Тест что у display_handler есть VacancyOperations"""
        assert hasattr(display_handler, 'vacancy_ops')
        assert display_handler.vacancy_ops is not None

    def test_display_handler_storage_integration(self, display_handler, mock_storage, sample_vacancies):
        """Тест интеграции с storage"""
        mock_storage.get_vacancies.return_value = sample_vacancies
        
        # Проверяем, что storage правильно настроен
        vacancies = display_handler.storage.get_vacancies()
        assert len(vacancies) == len(sample_vacancies)
        assert vacancies[0].title == "Python Developer"

    @patch('src.utils.ui_helpers.get_positive_integer')  
    def test_show_top_vacancies_by_salary_user_cancellation(self, mock_get_int, display_handler, mock_storage):
        """Тест отмены пользователем при выборе количества вакансий"""
        mock_get_int.return_value = None  # Пользователь отменил
        mock_storage.get_vacancies.return_value = []
        
        result = display_handler.show_top_vacancies_by_salary()
        
        # Функция должна завершиться без ошибок
        assert result is None
        mock_get_int.assert_called_once()

    @patch('builtins.print')  
    def test_show_all_saved_vacancies_exception_handling(self, mock_print, display_handler, mock_storage):
        """Тест обработки исключений при отображении вакансий"""
        mock_storage.get_vacancies.side_effect = Exception("Database error")
        
        display_handler.show_all_saved_vacancies()
        
        # Проверяем что ошибка была обработана
        mock_print.assert_called()
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(print_calls)
        assert "ошибка" in output.lower() or "error" in output.lower()

    def test_display_handler_methods_exist(self, display_handler):
        """Тест что все необходимые методы существуют"""
        assert hasattr(display_handler, 'show_all_saved_vacancies')
        assert hasattr(display_handler, 'show_top_vacancies_by_salary') 
        assert hasattr(display_handler, 'search_saved_vacancies_by_keyword')
        assert callable(display_handler.show_all_saved_vacancies)
        assert callable(display_handler.show_top_vacancies_by_salary)
        assert callable(display_handler.search_saved_vacancies_by_keyword)
