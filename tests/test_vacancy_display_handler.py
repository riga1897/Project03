
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vacancies.models import Vacancy
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler


class TestVacancyDisplayHandler:
    """Тесты для VacancyDisplayHandler"""

    @pytest.fixture
    def mock_storage(self):
        """Фикстура для мокирования storage"""
        storage = Mock()
        storage.get_vacancies.return_value = []
        storage.get_vacancies_count.return_value = 0
        return storage

    @pytest.fixture
    def display_handler(self, mock_storage):
        """Фикстура для создания VacancyDisplayHandler"""
        return VacancyDisplayHandler(mock_storage)

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура для создания тестовой вакансии"""
        return Vacancy(
            title="Python Developer",
            url="https://test.com/vacancy/123",
            vacancy_id="123",
            source="hh.ru",
            employer={"name": "Test Company", "id": "comp123"},
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Test description",
            area="Москва"
        )

    def test_vacancy_display_handler_initialization(self, mock_storage):
        """Тест инициализации VacancyDisplayHandler"""
        handler = VacancyDisplayHandler(mock_storage)
        assert handler.storage == mock_storage
        assert hasattr(handler, 'vacancy_ops')

    @patch('src.ui_interfaces.vacancy_display_handler.quick_paginate')
    @patch('builtins.print')
    def test_show_all_saved_vacancies_empty(self, mock_print, mock_paginate, display_handler, mock_storage):
        """Тест отображения пустого списка сохраненных вакансий"""
        mock_storage.get_vacancies.return_value = []
        mock_storage.get_vacancies_count.return_value = 0
        
        display_handler.show_all_saved_vacancies()
        
        mock_print.assert_called_with("\nНет сохраненных вакансий.")
        mock_paginate.assert_not_called()

    @patch('src.ui_interfaces.vacancy_display_handler.quick_paginate')
    @patch('builtins.print')
    def test_show_all_saved_vacancies_with_data(self, mock_print, mock_paginate, display_handler, mock_storage, sample_vacancy):
        """Тест отображения списка сохраненных вакансий"""
        mock_storage.get_vacancies.return_value = [sample_vacancy]
        mock_storage.get_vacancies_count.return_value = 1
        
        display_handler.show_all_saved_vacancies()
        
        mock_paginate.assert_called_once()
        mock_print.assert_any_call("\nСохраненных вакансий: 1")

    @patch('src.ui_interfaces.vacancy_display_handler.quick_paginate')
    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=5)
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary(self, mock_print, mock_get_int, mock_paginate, display_handler, mock_storage, sample_vacancy):
        """Тест отображения топ вакансий по зарплате"""
        mock_storage.get_vacancies.return_value = [sample_vacancy]
        
        with patch.object(display_handler.vacancy_ops, 'get_vacancies_with_salary', return_value=[sample_vacancy]):
            with patch.object(display_handler.vacancy_ops, 'sort_vacancies_by_salary', return_value=[sample_vacancy]):
                display_handler.show_top_vacancies_by_salary()
        
        mock_paginate.assert_called_once()

    @patch('src.ui_interfaces.vacancy_display_handler.quick_paginate')
    @patch('src.ui_interfaces.vacancy_display_handler.filter_vacancies_by_keyword', return_value=[])
    @patch('src.utils.ui_helpers.get_user_input', return_value="Python")
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_no_results(self, mock_print, mock_input, mock_filter, mock_paginate, display_handler, mock_storage, sample_vacancy):
        """Тест поиска сохраненных вакансий по ключевому слову без результатов"""
        mock_storage.get_vacancies.return_value = [sample_vacancy]
        
        display_handler.search_saved_vacancies_by_keyword()
        
        mock_print.assert_any_call("Среди сохраненных вакансий не найдено ни одной с ключевым словом 'Python'.")
        mock_paginate.assert_not_called()

    @patch('src.ui_interfaces.vacancy_display_handler.quick_paginate')
    @patch('src.ui_interfaces.vacancy_display_handler.filter_vacancies_by_keyword')
    @patch('src.utils.ui_helpers.get_user_input', return_value="Python")
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_with_results(self, mock_print, mock_input, mock_filter, mock_paginate, display_handler, mock_storage, sample_vacancy):
        """Тест поиска сохраненных вакансий по ключевому слову с результатами"""
        mock_storage.get_vacancies.return_value = [sample_vacancy]
        mock_filter.return_value = [sample_vacancy]
        
        display_handler.search_saved_vacancies_by_keyword()
        
        mock_print.assert_any_call("\nНайдено 1 сохраненных вакансий с ключевым словом 'Python':")
        mock_paginate.assert_called_once()

    @patch('src.utils.ui_helpers.get_user_input', return_value="")
    def test_search_saved_vacancies_by_keyword_empty_input(self, mock_input, display_handler):
        """Тест поиска с пустым вводом"""
        display_handler.search_saved_vacancies_by_keyword()
        # Метод должен завершиться без ошибок при пустом вводе

    @patch('builtins.print')
    def test_show_all_saved_vacancies_storage_error(self, mock_print, display_handler, mock_storage):
        """Тест обработки ошибки storage при отображении вакансий"""
        mock_storage.get_vacancies.side_effect = Exception("Database error")
        
        display_handler.show_all_saved_vacancies()
        
        mock_print.assert_any_call("Ошибка при загрузке вакансий: Database error")

    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=None)
    def test_show_top_vacancies_by_salary_invalid_input(self, mock_get_int, display_handler):
        """Тест обработки неверного ввода количества вакансий"""
        display_handler.show_top_vacancies_by_salary()
        # Метод должен завершиться без ошибок при неверном вводе

    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=5)
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary_no_vacancies(self, mock_print, mock_get_int, display_handler, mock_storage):
        """Тест топ вакансий когда нет сохраненных вакансий"""
        mock_storage.get_vacancies.return_value = []
        
        display_handler.show_top_vacancies_by_salary()
        
        mock_print.assert_any_call("Нет сохраненных вакансий.")

    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=5)
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary_no_salary_vacancies(self, mock_print, mock_get_int, display_handler, mock_storage, sample_vacancy):
        """Тест топ вакансий когда нет вакансий с зарплатой"""
        mock_storage.get_vacancies.return_value = [sample_vacancy]
        
        with patch.object(display_handler.vacancy_ops, 'get_vacancies_with_salary', return_value=[]):
            display_handler.show_top_vacancies_by_salary()
        
        mock_print.assert_any_call("Среди сохраненных вакансий нет ни одной с указанной зарплатой.")

    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_no_saved_vacancies(self, mock_print, display_handler, mock_storage):
        """Тест поиска когда нет сохраненных вакансий"""
        mock_storage.get_vacancies.return_value = []
        
        with patch('src.utils.ui_helpers.get_user_input', return_value="Python"):
            display_handler.search_saved_vacancies_by_keyword()
        
        mock_print.assert_any_call("Нет сохраненных вакансий.")

    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_storage_error(self, mock_print, display_handler, mock_storage):
        """Тест обработки ошибки storage при поиске"""
        mock_storage.get_vacancies.side_effect = Exception("Database error")
        
        with patch('src.utils.ui_helpers.get_user_input', return_value="Python"):
            display_handler.search_saved_vacancies_by_keyword()
        
        mock_print.assert_any_call("Ошибка при поиске: Database error")

    def test_vacancy_display_handler_attributes(self, display_handler, mock_storage):
        """Тест проверки атрибутов VacancyDisplayHandler"""
        assert hasattr(display_handler, 'storage')
        assert hasattr(display_handler, 'vacancy_ops')
        assert display_handler.storage == mock_storage
