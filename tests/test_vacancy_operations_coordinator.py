
import os
import sys
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ui_interfaces.vacancy_operations_coordinator import VacancyOperationsCoordinator
from src.vacancies.models import Vacancy


class TestVacancyOperationsCoordinator:
    """Тесты для VacancyOperationsCoordinator"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.mock_api = Mock()
        self.mock_storage = Mock()
        
    def test_coordinator_initialization(self):
        """Тест инициализации VacancyOperationsCoordinator"""
        with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler'), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler'), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector'):
            
            coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
            
            assert coordinator.unified_api == self.mock_api
            assert coordinator.storage == self.mock_storage
            assert coordinator.search_handler is not None
            assert coordinator.display_handler is not None
            assert coordinator.source_selector is not None

    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_handle_vacancy_search(self, mock_source_selector, mock_display_handler, mock_search_handler):
        """Тест обработки поиска вакансий"""
        mock_search_instance = Mock()
        mock_search_handler.return_value = mock_search_instance
        
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        coordinator.handle_vacancy_search()
        
        mock_search_instance.search_vacancies.assert_called_once()

    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_handle_show_saved_vacancies(self, mock_source_selector, mock_display_handler, mock_search_handler):
        """Тест отображения сохраненных вакансий"""
        mock_display_instance = Mock()
        mock_display_handler.return_value = mock_display_instance
        
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        coordinator.handle_show_saved_vacancies()
        
        mock_display_instance.show_all_saved_vacancies.assert_called_once()

    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_handle_top_vacancies_by_salary(self, mock_source_selector, mock_display_handler, mock_search_handler):
        """Тест получения топ вакансий по зарплате"""
        mock_display_instance = Mock()
        mock_display_handler.return_value = mock_display_instance
        
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        coordinator.handle_top_vacancies_by_salary()
        
        mock_display_instance.show_top_vacancies_by_salary.assert_called_once()

    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_handle_search_saved_by_keyword(self, mock_source_selector, mock_display_handler, mock_search_handler):
        """Тест поиска сохраненных вакансий по ключевому слову"""
        mock_display_instance = Mock()
        mock_display_handler.return_value = mock_display_instance
        
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        coordinator.handle_search_saved_by_keyword()
        
        mock_display_instance.search_saved_vacancies_by_keyword.assert_called_once()

    @patch('builtins.print')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True)
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_handle_cache_cleanup(self, mock_source_selector, mock_display_handler, mock_search_handler, mock_confirm, mock_print):
        """Тест очистки кэша"""
        # Настройка моков
        mock_selector_instance = Mock()
        mock_selector_instance.get_user_source_choice.return_value = {"hh.ru"}
        mock_source_selector.return_value = mock_selector_instance
        
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        coordinator.handle_cache_cleanup()
        
        # Проверяем, что методы были вызваны
        mock_selector_instance.get_user_source_choice.assert_called_once()
        mock_selector_instance.display_sources_info.assert_called_once_with({"hh.ru"})
        self.mock_api.clear_cache.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value='0')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_handle_delete_vacancies_no_vacancies(self, mock_source_selector, mock_display_handler, mock_search_handler, mock_input, mock_print):
        """Тест удаления вакансий когда их нет"""
        self.mock_storage.get_vacancies.return_value = []
        
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        coordinator.handle_delete_vacancies()
        
        # Проверяем, что был вызван get_vacancies
        self.mock_storage.get_vacancies.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value='1')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True)
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_handle_delete_vacancies_all(self, mock_source_selector, mock_display_handler, mock_search_handler, mock_confirm, mock_input, mock_print):
        """Тест удаления всех вакансий"""
        test_vacancies = [Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")]
        self.mock_storage.get_vacancies.return_value = test_vacancies
        self.mock_storage.delete_all_vacancies.return_value = True
        
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        coordinator.handle_delete_vacancies()
        
        self.mock_storage.delete_all_vacancies.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value="Python")
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_handle_superjob_setup(self, mock_source_selector, mock_display_handler, mock_search_handler, mock_input, mock_print):
        """Тест настройки SuperJob API"""
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        coordinator.handle_superjob_setup()
        
        # Проверяем, что функция выполнилась без ошибок
        mock_print.assert_called()

    @patch('src.ui_interfaces.vacancy_operations_coordinator.Vacancy')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_get_vacancies_from_sources(self, mock_source_selector, mock_display_handler, mock_search_handler, mock_vacancy):
        """Тест получения вакансий из источников"""
        # Настройка моков
        mock_vacancy_data = [{"id": "123", "title": "Python Developer"}]
        self.mock_api.get_vacancies_from_sources.return_value = mock_vacancy_data
        
        mock_vacancy_instance = Mock()
        mock_vacancy.from_dict.return_value = mock_vacancy_instance
        
        self.mock_storage.add_vacancy.return_value = ["Vacancy added"]
        self.mock_storage.get_vacancies.return_value = [mock_vacancy_instance]
        
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        
        with patch('builtins.print'):
            result = coordinator.get_vacancies_from_sources("Python", ["hh.ru"])
        
        assert len(result) == 1
        self.mock_api.get_vacancies_from_sources.assert_called_once()

    @patch('src.ui_interfaces.vacancy_operations_coordinator.Vacancy')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector')
    def test_get_vacancies_from_target_companies(self, mock_source_selector, mock_display_handler, mock_search_handler, mock_vacancy):
        """Тест получения вакансий от целевых компаний"""
        # Настройка моков
        mock_vacancy_data = [{"id": "123", "title": "Python Developer"}]
        self.mock_api.get_vacancies_from_target_companies.return_value = mock_vacancy_data
        
        mock_vacancy_instance = Mock()
        mock_vacancy.from_dict.return_value = mock_vacancy_instance
        
        self.mock_storage.add_vacancy.return_value = ["Vacancy added"]
        self.mock_storage.get_vacancies.return_value = [mock_vacancy_instance]
        
        coordinator = VacancyOperationsCoordinator(self.mock_api, self.mock_storage)
        
        with patch('builtins.print'):
            result = coordinator.get_vacancies_from_target_companies("Python", ["hh.ru"])
        
        assert len(result) == 1
        self.mock_api.get_vacancies_from_target_companies.assert_called_once()
