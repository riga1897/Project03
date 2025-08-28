
"""
Тесты для модуля VacancyDisplayHandler
"""

import pytest
from unittest.mock import Mock, patch
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.vacancies.models import Vacancy


class TestVacancyDisplayHandler:
    """Тесты для класса VacancyDisplayHandler"""

    @pytest.fixture
    def mock_storage(self):
        """Фикстура mock storage"""
        storage = Mock()
        storage.get_vacancies.return_value = []
        storage.get_top_vacancies_by_salary.return_value = []
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

    @patch('builtins.print')
    def test_show_all_saved_vacancies_empty(self, mock_print, display_handler, mock_storage):
        """Тест отображения всех вакансий - пустой список"""
        mock_storage.get_vacancies.return_value = []
        
        display_handler.show_all_saved_vacancies()
        
        mock_print.assert_called()
        # Проверяем, что выводится сообщение о отсутствии вакансий
        call_args = [str(call) for call in mock_print.call_args_list]
        output = " ".join(call_args)
        assert "вакансий" in output.lower()

    @patch('src.utils.ui_navigation.quick_paginate')
    def test_show_all_saved_vacancies_with_data(self, mock_paginate, display_handler, mock_storage, sample_vacancies):
        """Тест отображения всех вакансий - с данными"""
        mock_storage.get_vacancies.return_value = sample_vacancies
        
        display_handler.show_all_saved_vacancies()
        
        mock_paginate.assert_called_once()
        args, kwargs = mock_paginate.call_args
        assert len(args[0]) == len(sample_vacancies)

    @patch('src.utils.ui_helpers.get_positive_integer', return_value=10)
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary_empty(self, mock_print, mock_get_int, display_handler, mock_storage):
        """Тест отображения топ вакансий по зарплате - пустой список"""
        mock_storage.get_vacancies.return_value = []
        
        display_handler.show_top_vacancies_by_salary()
        
        mock_get_int.assert_called_once()
        mock_print.assert_called()

    @patch('src.utils.ui_helpers.get_positive_integer', return_value=10)
    @patch('src.utils.ui_navigation.quick_paginate')
    def test_show_top_vacancies_by_salary_with_data(self, mock_paginate, mock_get_int, display_handler, mock_storage, sample_vacancies):
        """Тест отображения топ вакансий по зарплате - с данными"""
        mock_storage.get_vacancies.return_value = sample_vacancies
        
        display_handler.show_top_vacancies_by_salary()
        
        mock_get_int.assert_called_once()
        mock_paginate.assert_called_once()

    @patch('src.utils.ui_helpers.get_user_input', return_value='python')
    @patch('src.utils.ui_navigation.quick_paginate')
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    def test_search_saved_vacancies_by_keyword_found(self, mock_filter, mock_paginate, mock_get_input, display_handler, mock_storage, sample_vacancies):
        """Тест поиска сохраненных вакансий по ключевому слову - найдены"""
        mock_storage.get_vacancies.return_value = sample_vacancies
        mock_filter.return_value = [sample_vacancies[0]]  # Возвращаем Python вакансию
        
        display_handler.search_saved_vacancies_by_keyword()
        
        mock_get_input.assert_called_once()
        mock_filter.assert_called_once_with(sample_vacancies, 'python')
        mock_paginate.assert_called_once()

    @patch('src.utils.ui_helpers.get_user_input', return_value='nonexistent')
    @patch('builtins.print')
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    def test_search_saved_vacancies_by_keyword_not_found(self, mock_filter, mock_print, mock_get_input, display_handler, mock_storage, sample_vacancies):
        """Тест поиска сохраненных вакансий по ключевому слову - не найдены"""
        mock_storage.get_vacancies.return_value = sample_vacancies
        mock_filter.return_value = []  # Ничего не найдено
        
        display_handler.search_saved_vacancies_by_keyword()
        
        mock_get_input.assert_called_once()
        mock_filter.assert_called_once_with(sample_vacancies, 'nonexistent')
        mock_print.assert_called()

    @patch('src.utils.ui_helpers.get_user_input', return_value=None)
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_empty_query(self, mock_print, mock_get_input, display_handler, mock_storage):
        """Тест поиска сохраненных вакансий по ключевому слову - пустой запрос"""
        # Настраиваем моки чтобы не было реальных вызовов
        mock_storage.get_vacancies.return_value = []
        
        display_handler.search_saved_vacancies_by_keyword()
        
        # Проверяем что функция завершилась корректно
        mock_get_input.assert_called_once()
        # Не должно быть дополнительных вызовов при пустом вводе

    @patch('src.utils.ui_helpers.get_user_input', return_value='python')
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_no_saved_vacancies(self, mock_print, mock_get_input, display_handler, mock_storage):
        """Тест поиска сохраненных вакансий - нет сохраненных вакансий"""
        mock_storage.get_vacancies.return_value = []
        
        display_handler.search_saved_vacancies_by_keyword()
        
        mock_print.assert_called()
        # Проверяем что get_user_input был вызван
        mock_get_input.assert_called_once()

    def test_format_vacancy_for_display(self, display_handler, sample_vacancies):
        """Тест форматирования вакансии для отображения"""
        vacancy = sample_vacancies[0]
        
        with patch('src.utils.vacancy_formatter.VacancyFormatter.format_vacancy_info') as mock_format:
            mock_format.return_value = "Formatted vacancy"
            
            result = display_handler._format_vacancy_for_display(vacancy, 1)
            
            mock_format.assert_called_once_with(vacancy)
            assert "1." in result or "Formatted vacancy" in result

    def test_get_vacancy_display_stats(self, display_handler, sample_vacancies):
        """Тест получения статистики для отображения"""
        stats = display_handler._get_vacancy_display_stats(sample_vacancies)
        
        assert isinstance(stats, dict)
        assert 'total_count' in stats
        assert 'with_salary_count' in stats
        assert stats['total_count'] == len(sample_vacancies)
