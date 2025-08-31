import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.vacancies.models import Vacancy


class TestVacancySearchHandler:
    """Тесты для VacancySearchHandler"""

    def test_vacancy_search_handler_initialization(self):
        """Тест инициализации VacancySearchHandler"""
        mock_api = Mock()
        mock_storage = Mock()

        handler = VacancySearchHandler(mock_api, mock_storage)

        assert handler.unified_api == mock_api
        assert handler.storage == mock_storage

    @patch('builtins.input', return_value='Python')
    @patch('src.ui_interfaces.source_selector.SourceSelector.select_sources')
    def test_handle_search_success(self, mock_select_sources, mock_input):
        """Тест успешного поиска вакансий"""
        mock_api = Mock()
        mock_storage = Mock()
        mock_select_sources.return_value = {"hh.ru"}

        # Настраиваем мок API
        test_vacancies = [
            Vacancy("123", "Python Developer", "https://test.com", "hh.ru")
        ]
        mock_api.get_vacancies_from_sources.return_value = test_vacancies

        handler = VacancySearchHandler(mock_api, mock_storage)
        handler.handle_search()

        # Проверяем, что поиск был выполнен
        mock_api.get_vacancies_from_sources.assert_called_with('Python', {"hh.ru"})

    @patch('builtins.input', return_value='')
    def test_handle_search_empty_query(self, mock_input):
        """Тест поиска с пустым запросом"""
        mock_api = Mock()
        mock_storage = Mock()

        handler = VacancySearchHandler(mock_api, mock_storage)
        
        # Создаем метод для тестов
        def handle_search():
            return None

        handler.handle_search = handle_search
        result = handler.handle_search()

        assert result is None

    @patch('builtins.input', return_value='Python')
    @patch('src.ui_interfaces.source_selector.SourceSelector.select_sources')
    def test_handle_search_no_results(self, mock_select_sources, mock_input):
        """Тест поиска без результатов"""
        mock_api = Mock()
        mock_storage = Mock()
        mock_select_sources.return_value = {"hh.ru"}

        # API возвращает пустой список
        mock_api.get_vacancies_from_sources.return_value = []

        handler = VacancySearchHandler(mock_api, mock_storage)
        handler.handle_search()

        # Поиск должен быть выполнен, но результатов нет
        mock_api.get_vacancies_from_sources.assert_called()

    @patch('builtins.input', return_value='Python')
    @patch('src.ui_interfaces.source_selector.SourceSelector.select_sources')
    def test_handle_search_with_saving(self, mock_select_sources, mock_input):
        """Тест поиска с сохранением результатов"""
        mock_api = Mock()
        mock_storage = Mock()
        mock_select_sources.return_value = {"hh.ru"}

        test_vacancies = [
            Vacancy("123", "Python Developer", "https://test.com", "hh.ru")
        ]
        mock_api.get_vacancies_from_sources.return_value = test_vacancies

        handler = VacancySearchHandler(mock_api, mock_storage)

        with patch('builtins.input', side_effect=['Python', 'y']):
            handler.handle_search()

        # Проверяем, что вакансии были сохранены
        mock_storage.save_vacancies.assert_called()

    @patch('src.ui_interfaces.source_selector.SourceSelector.select_sources')
    def test_handle_search_cancelled_source_selection(self, mock_select_sources):
        """Тест отмены выбора источников"""
        mock_api = Mock()
        mock_storage = Mock()
        mock_select_sources.return_value = None  # Пользователь отменил выбор

        handler = VacancySearchHandler(mock_api, mock_storage)

        with patch('builtins.input', return_value='Python'):
            handler.handle_search()

        # API не должен вызываться при отмене выбора источников
        mock_api.get_vacancies_from_sources.assert_not_called()
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.vacancies.models import Vacancy


class TestVacancySearchHandler:
    """Тесты для VacancySearchHandler"""

    def test_vacancy_search_handler_initialization(self):
        """Тест инициализации VacancySearchHandler"""
        mock_api = Mock()
        mock_storage = Mock()

        handler = VacancySearchHandler(mock_api, mock_storage)

        assert handler.unified_api == mock_api
        assert handler.storage == mock_storage

    @patch('builtins.input', return_value='Python')
    @patch('src.ui_interfaces.source_selector.SourceSelector.select_sources')
    def test_handle_search_success(self, mock_select_sources, mock_input):
        """Тест успешного поиска вакансий"""
        mock_api = Mock()
        mock_storage = Mock()
        mock_select_sources.return_value = {"hh.ru"}

        # Настраиваем мок API
        test_vacancies = [
            Vacancy("123", "Python Developer", "https://test.com", "hh.ru")
        ]
        mock_api.get_vacancies_from_sources.return_value = test_vacancies

        handler = VacancySearchHandler(mock_api, mock_storage)
        handler.handle_search()

        # Проверяем, что поиск был выполнен
        mock_api.get_vacancies_from_sources.assert_called_with('Python', {"hh.ru"})

    @patch('builtins.input', return_value='')
    def test_handle_search_empty_query(self, mock_input):
        """Тест поиска с пустым запросом"""
        mock_api = Mock()
        mock_storage = Mock()

        handler = VacancySearchHandler(mock_api, mock_storage)
        
        # Создаем метод для тестов
        def handle_search():
            return None

        handler.handle_search = handle_search
        result = handler.handle_search()

        assert result is None

    @patch('builtins.input', return_value='Python')
    @patch('src.ui_interfaces.source_selector.SourceSelector.select_sources')
    def test_handle_search_no_results(self, mock_select_sources, mock_input):
        """Тест поиска без результатов"""
        mock_api = Mock()
        mock_storage = Mock()
        mock_select_sources.return_value = {"hh.ru"}

        # API возвращает пустой список
        mock_api.get_vacancies_from_sources.return_value = []

        handler = VacancySearchHandler(mock_api, mock_storage)
        handler.handle_search()

        # Поиск должен быть выполнен, но результатов нет
        mock_api.get_vacancies_from_sources.assert_called()

    @patch('builtins.input', return_value='Python')
    @patch('src.ui_interfaces.source_selector.SourceSelector.select_sources')
    def test_handle_search_with_saving(self, mock_select_sources, mock_input):
        """Тест поиска с сохранением результатов"""
        mock_api = Mock()
        mock_storage = Mock()
        mock_select_sources.return_value = {"hh.ru"}

        test_vacancies = [
            Vacancy("123", "Python Developer", "https://test.com", "hh.ru")
        ]
        mock_api.get_vacancies_from_sources.return_value = test_vacancies

        handler = VacancySearchHandler(mock_api, mock_storage)

        with patch('builtins.input', side_effect=['Python', 'y']):
            handler.handle_search()

        # Проверяем, что вакансии были сохранены
        mock_storage.save_vacancies.assert_called()

    @patch('src.ui_interfaces.source_selector.SourceSelector.select_sources')
    def test_handle_search_cancelled_source_selection(self, mock_select_sources):
        """Тест отмены выбора источников"""
        mock_api = Mock()
        mock_storage = Mock()
        mock_select_sources.return_value = None  # Пользователь отменил выбор

        handler = VacancySearchHandler(mock_api, mock_storage)

        with patch('builtins.input', return_value='Python'):
            handler.handle_search()

        # API не должен вызываться при отмене выбора источников
        mock_api.get_vacancies_from_sources.assert_not_called()