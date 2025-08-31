import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ui_interfaces.vacancy_operations_coordinator import VacancyOperationsCoordinator
from src.vacancies.models import Vacancy, VacancySalary


class TestVacancyOperationsCoordinator:
    """Тесты для VacancyOperationsCoordinator"""

    def test_coordinator_initialization(self):
        """Тест инициализации VacancyOperationsCoordinator"""
        mock_api = Mock()
        mock_storage = Mock()

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)

        assert coordinator.unified_api == mock_api
        assert coordinator.storage == mock_storage

    @patch("builtins.input", return_value="q")
    @patch("src.ui_interfaces.vacancy_search_handler.VacancySearchHandler")
    def test_handle_vacancy_search(self, mock_search_handler, mock_input):
        """Тест обработки поиска вакансий"""
        mock_api = Mock()
        mock_storage = Mock()

        mock_handler_instance = Mock()
        mock_search_handler.return_value = mock_handler_instance

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)

        # Мокаем все зависимости
        with patch("src.ui_interfaces.source_selector.SourceSelector") as mock_selector:
            mock_selector_instance = Mock()
            mock_selector_instance.get_user_source_choice.return_value = {"hh.ru"}
            mock_selector.return_value = mock_selector_instance

            coordinator.handle_vacancy_search()

        # Проверяем, что обработчик поиска был вызван
        mock_handler_instance.handle_search.assert_called()

    @patch("src.ui_interfaces.vacancy_display_handler.VacancyDisplayHandler")
    def test_handle_show_saved_vacancies(self, mock_display_handler):
        """Тест отображения сохраненных вакансий"""
        mock_api = Mock()
        mock_storage = Mock()
        mock_storage.get_vacancies.return_value = []

        mock_handler_instance = Mock()
        mock_display_handler.return_value = mock_handler_instance

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)
        coordinator.handle_show_saved_vacancies()

        # Проверяем, что storage был вызван для получения вакансий
        mock_storage.get_vacancies.assert_called()

    @patch("builtins.input", return_value="5")
    @patch("builtins.print")
    def test_handle_top_vacancies_by_salary(self, mock_print, mock_input):
        """Тест получения топ вакансий по зарплате"""
        mock_api = Mock()
        mock_storage = Mock()

        test_vacancies = [
            Vacancy(
                "123",
                "Python Developer",
                "https://test.com",
                "hh.ru",
                salary=VacancySalary(from_amount=150000, currency="RUR"),
            ),
            Vacancy(
                "124",
                "Java Developer",
                "https://test2.com",
                "hh.ru",
                salary=VacancySalary(from_amount=100000, currency="RUR"),
            ),
        ]
        mock_storage.get_vacancies.return_value = test_vacancies

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)
        coordinator.handle_top_vacancies_by_salary()

        # Проверяем, что storage был вызван
        mock_storage.get_vacancies.assert_called()

    @patch("builtins.input", return_value="Python")
    @patch("builtins.print")
    def test_handle_search_saved_by_keyword(self, mock_print, mock_input):
        """Тест поиска сохраненных вакансий по ключевому слову"""
        mock_api = Mock()
        mock_storage = Mock()

        test_vacancies = [Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")]
        mock_storage.get_vacancies.return_value = test_vacancies

        coordinator = VacancyOperationsCoordinator(mock_api, mock_storage)
        coordinator.handle_search_saved_by_keyword()

        # Проверяем, что storage был вызван
        mock_storage.get_vacancies.assert_called()

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

    def test_handle_cache_cleanup(self):
        """Тест очистки кэша"""
        mock_api = Mock()
        mock_storage = Mock()

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
