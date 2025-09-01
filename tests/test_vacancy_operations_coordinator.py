
import os
import sys
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ui_interfaces.vacancy_operations_coordinator import VacancyOperationsCoordinator
from src.vacancies.models import Vacancy


class TestVacancyOperationsCoordinator:
    """Тесты для класса VacancyOperationsCoordinator"""

    @pytest.fixture
    def mock_api(self):
        """Фикстура для мокирования API"""
        api = Mock()
        api.get_vacancies_from_sources.return_value = []
        api.get_vacancies_from_target_companies.return_value = []
        api.clear_cache.return_value = None
        return api

    @pytest.fixture
    def mock_storage(self):
        """Фикстура для мокирования storage"""
        storage = Mock()
        storage.get_vacancies.return_value = []
        storage.delete_all_vacancies.return_value = True
        storage.add_vacancy.return_value = []
        storage.delete_vacancies_batch.return_value = 0
        storage.delete_vacancy_by_id.return_value = True
        return storage

    @pytest.fixture
    def mock_handlers(self):
        """Фикстура для мокирования обработчиков"""
        with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler') as mock_search, \
             patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler') as mock_display, \
             patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector') as mock_selector:
            
            # Настройка моков
            mock_search_instance = Mock()
            mock_display_instance = Mock()
            mock_selector_instance = Mock()
            
            mock_search.return_value = mock_search_instance
            mock_display.return_value = mock_display_instance
            mock_selector.return_value = mock_selector_instance
            
            yield {
                'search': mock_search_instance,
                'display': mock_display_instance,
                'selector': mock_selector_instance
            }

    @pytest.fixture
    def coordinator(self, mock_api, mock_storage, mock_handlers):
        """Фикстура для создания VacancyOperationsCoordinator с моками"""
        return VacancyOperationsCoordinator(mock_api, mock_storage)

    def test_coordinator_initialization(self, coordinator, mock_api, mock_storage):
        """Тест инициализации VacancyOperationsCoordinator"""
        assert coordinator.unified_api == mock_api
        assert coordinator.storage == mock_storage
        assert coordinator.search_handler is not None
        assert coordinator.display_handler is not None
        assert coordinator.source_selector is not None

    def test_handle_vacancy_search(self, coordinator, mock_handlers):
        """Тест обработки поиска вакансий"""
        coordinator.handle_vacancy_search()
        mock_handlers['search'].search_vacancies.assert_called_once()

    def test_handle_show_saved_vacancies(self, coordinator, mock_handlers):
        """Тест отображения сохраненных вакансий"""
        coordinator.handle_show_saved_vacancies()
        mock_handlers['display'].show_all_saved_vacancies.assert_called_once()

    def test_handle_top_vacancies_by_salary(self, coordinator, mock_handlers):
        """Тест получения топ вакансий по зарплате"""
        coordinator.handle_top_vacancies_by_salary()
        mock_handlers['display'].show_top_vacancies_by_salary.assert_called_once()

    def test_handle_search_saved_by_keyword(self, coordinator, mock_handlers):
        """Тест поиска сохраненных вакансий по ключевому слову"""
        coordinator.handle_search_saved_by_keyword()
        mock_handlers['display'].search_saved_vacancies_by_keyword.assert_called_once()

    @patch('builtins.print')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True)
    def test_handle_cache_cleanup(self, mock_confirm, mock_print, coordinator, mock_api, mock_handlers):
        """Тест очистки кэша"""
        mock_handlers['selector'].get_user_source_choice.return_value = {"hh.ru"}
        
        coordinator.handle_cache_cleanup()
        
        mock_handlers['selector'].get_user_source_choice.assert_called_once()
        mock_handlers['selector'].display_sources_info.assert_called_once_with({"hh.ru"})
        mock_api.clear_cache.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value='0')
    def test_handle_delete_vacancies_no_vacancies(self, mock_input, mock_print, coordinator, mock_storage):
        """Тест удаления вакансий когда их нет"""
        mock_storage.get_vacancies.return_value = []
        
        coordinator.handle_delete_vacancies()
        
        mock_storage.get_vacancies.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value='1')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True)
    def test_handle_delete_vacancies_all(self, mock_confirm, mock_input, mock_print, coordinator, mock_storage):
        """Тест удаления всех вакансий"""
        test_vacancies = [Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")]
        mock_storage.get_vacancies.return_value = test_vacancies
        
        coordinator.handle_delete_vacancies()
        
        mock_storage.delete_all_vacancies.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value="2")
    @patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value="Python")
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True)
    def test_handle_delete_vacancies_by_keyword(self, mock_confirm, mock_filter, mock_user_input, mock_input, mock_print, coordinator, mock_storage):
        """Тест удаления вакансий по ключевому слову"""
        test_vacancies = [Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")]
        mock_storage.get_vacancies.return_value = test_vacancies
        mock_filter.return_value = test_vacancies
        mock_storage.delete_vacancies_batch.return_value = 1
        
        coordinator.handle_delete_vacancies()
        
        mock_storage.delete_vacancies_batch.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value="Python")
    def test_handle_superjob_setup(self, mock_input, mock_print):
        """Тест настройки SuperJob API"""
        VacancyOperationsCoordinator.handle_superjob_setup()
        mock_print.assert_called()

    @patch('builtins.print')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.Vacancy')
    def test_get_vacancies_from_sources(self, mock_vacancy, mock_print, coordinator, mock_api, mock_storage):
        """Тест получения вакансий из источников"""
        mock_vacancy_data = [{"id": "123", "title": "Python Developer"}]
        mock_api.get_vacancies_from_sources.return_value = mock_vacancy_data
        
        mock_vacancy_instance = Mock()
        mock_vacancy.from_dict.return_value = mock_vacancy_instance
        
        mock_storage.add_vacancy.return_value = ["Vacancy added"]
        mock_storage.get_vacancies.return_value = [mock_vacancy_instance]
        
        result = coordinator.get_vacancies_from_sources("Python", ["hh.ru"])
        
        assert len(result) == 1
        mock_api.get_vacancies_from_sources.assert_called_once()

    @patch('builtins.print')
    @patch('src.ui_interfaces.vacancy_operations_coordinator.Vacancy')
    def test_get_vacancies_from_target_companies(self, mock_vacancy, mock_print, coordinator, mock_api, mock_storage):
        """Тест получения вакансий от целевых компаний"""
        mock_vacancy_data = [{"id": "123", "title": "Python Developer"}]
        mock_api.get_vacancies_from_target_companies.return_value = mock_vacancy_data
        
        mock_vacancy_instance = Mock()
        mock_vacancy.from_dict.return_value = mock_vacancy_instance
        
        mock_storage.add_vacancy.return_value = ["Vacancy added"]
        mock_storage.get_vacancies.return_value = [mock_vacancy_instance]
        
        result = coordinator.get_vacancies_from_target_companies("Python", ["hh.ru"])
        
        assert len(result) == 1
        mock_api.get_vacancies_from_target_companies.assert_called_once()

    @patch('builtins.print')
    def test_handle_delete_vacancies_cancel(self, mock_print, coordinator, mock_storage):
        """Тест отмены удаления вакансий"""
        test_vacancies = [Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")]
        mock_storage.get_vacancies.return_value = test_vacancies
        
        with patch('builtins.input', return_value='0'):
            coordinator.handle_delete_vacancies()
        
        mock_storage.delete_all_vacancies.assert_not_called()

    @patch('builtins.print')
    def test_handle_cache_cleanup_cancelled_source_selection(self, mock_print, coordinator, mock_handlers):
        """Тест отмены выбора источников при очистке кэша"""
        mock_handlers['selector'].get_user_source_choice.return_value = None
        
        coordinator.handle_cache_cleanup()
        
        # Метод должен завершиться без ошибок при отмене выбора источников
        mock_handlers['selector'].get_user_source_choice.assert_called_once()

    @patch('builtins.print')
    def test_get_vacancies_from_sources_error_handling(self, mock_print, coordinator, mock_api):
        """Тест обработки ошибок при получении вакансий из источников"""
        mock_api.get_vacancies_from_sources.side_effect = Exception("API Error")
        
        result = coordinator.get_vacancies_from_sources("Python", ["hh.ru"])
        
        assert result == []

    @patch('builtins.print')
    def test_get_vacancies_from_target_companies_error_handling(self, mock_print, coordinator, mock_api):
        """Тест обработки ошибок при получении вакансий от целевых компаний"""
        mock_api.get_vacancies_from_target_companies.side_effect = Exception("API Error")
        
        result = coordinator.get_vacancies_from_target_companies("Python", ["hh.ru"])
        
        assert result == []

    @patch('builtins.print')
    def test_handle_delete_vacancies_storage_error(self, mock_print, coordinator, mock_storage):
        """Тест обработки ошибки storage при удалении вакансий"""
        mock_storage.get_vacancies.side_effect = Exception("Storage error")
        
        coordinator.handle_delete_vacancies()
        
        mock_print.assert_called()
