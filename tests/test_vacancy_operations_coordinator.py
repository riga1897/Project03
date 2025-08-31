import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ui_interfaces.vacancy_operations_coordinator import VacancyOperationsCoordinator
from src.vacancies.models import Vacancy

# Создаем тестовый класс VacancySalary
class VacancySalary:
    """Тестовый класс зарплаты вакансии"""
    
    def __init__(self, from_amount=None, to_amount=None, currency="RUR"):
        self.from_amount = from_amount
        self.to_amount = to_amount
        self.currency = currency


class TestVacancyOperationsCoordinator:
    """Тесты для VacancyOperationsCoordinator"""

    def test_coordinator_initialization(self):
        """Тест инициализации VacancyOperationsCoordinator"""
        mock_api = Mock()
        mock_storage = Mock()

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)

        assert coordinator.unified_api == mock_api
        assert coordinator.storage == mock_storage

    @patch("src.ui_interfaces.vacancy_search_handler.VacancySearchHandler")
    def test_handle_vacancy_search(self, mock_search_handler):
        """Тест обработки поиска вакансий"""
        mock_api = Mock()
        mock_storage = Mock()

        mock_handler_instance = Mock()
        mock_search_handler.return_value = mock_handler_instance

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)
        coordinator.handle_vacancy_search()

        # Проверяем, что обработчик поиска был вызван
        mock_handler_instance.search_vacancies.assert_called()

    @patch("src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler")
    def test_handle_show_saved_vacancies(self, mock_display_handler):
        """Тест отображения сохраненных вакансий"""
        mock_api = Mock()
        mock_storage = Mock()

        mock_handler_instance = Mock()
        mock_display_handler.return_value = mock_handler_instance

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)
        coordinator.handle_show_saved_vacancies()

        # Проверяем, что display handler был вызван
        mock_handler_instance.show_all_saved_vacancies.assert_called()

    @patch("src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler")
    def test_handle_top_vacancies_by_salary(self, mock_display_handler):
        """Тест получения топ вакансий по зарплате"""
        mock_api = Mock()
        mock_storage = Mock()

        mock_handler_instance = Mock()
        mock_display_handler.return_value = mock_handler_instance

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)
        coordinator.handle_top_vacancies_by_salary()

        # Проверяем, что display handler был вызван
        mock_handler_instance.show_top_vacancies_by_salary.assert_called()

    @patch("src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler")
    def test_handle_search_saved_by_keyword(self, mock_display_handler):
        """Тест поиска сохраненных вакансий по ключевому слову"""
        mock_api = Mock()
        mock_storage = Mock()

        mock_handler_instance = Mock()
        mock_display_handler.return_value = mock_handler_instance

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)
        coordinator.handle_search_saved_by_keyword()

        # Проверяем, что display handler был вызван
        mock_handler_instance.search_saved_vacancies_by_keyword.assert_called()

    @patch("builtins.input", return_value="Python")
    def test_handle_delete_vacancies(self, mock_input):
        """Тест удаления вакансий"""
        mock_api = Mock()
        mock_storage = Mock()

        test_vacancies = [Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")]
        mock_storage.get_vacancies.return_value = test_vacancies

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)

        with patch("builtins.print"):
            coordinator.handle_delete_vacancies()

        # Проверяем, что storage был вызван для получения вакансий
        mock_storage.get_vacancies.assert_called()

    @patch("src.utils.ui_helpers.confirm_action", return_value=True)
    @patch("src.ui_interfaces.source_selector.SourceSelector")
    def test_handle_cache_cleanup(self, mock_selector, mock_confirm):
        """Тест очистки кэша"""
        mock_api = Mock()
        mock_storage = Mock()

        mock_selector_instance = Mock()
        mock_selector_instance.get_user_source_choice.return_value = {"hh.ru"}
        mock_selector_instance.display_sources_info.return_value = None
        mock_selector.return_value = mock_selector_instance

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)

        with patch("builtins.print"):
            coordinator.handle_cache_cleanup()

        # Проверяем, что очистка кэша была вызвана
        mock_api.clear_cache.assert_called()

    @patch("builtins.input", return_value="test_key")
    @patch("builtins.print")
    def test_handle_superjob_setup(self, mock_print, mock_input):
        """Тест настройки SuperJob API"""
        mock_api = Mock()
        mock_storage = Mock()

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)
        coordinator.handle_superjob_setup()

        # Проверяем, что функция выполнилась без ошибок
        mock_print.assert_called()
