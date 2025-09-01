
import os
import sys
from unittest.mock import Mock, patch, MagicMock, call
from typing import List, Dict, Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ui_interfaces.vacancy_operations_coordinator import VacancyOperationsCoordinator
from src.vacancies.models import Vacancy


class TestVacancyOperationsCoordinator:
    """
    Тесты для класса VacancyOperationsCoordinator
    
    Тестирует координацию операций с вакансиями, включая поиск, отображение,
    сохранение, удаление и очистку кэша.
    """

    @pytest.fixture
    def consolidated_mocks(self):
        """
        Консолидированная фикстура всех необходимых моков
        
        Returns:
            Dict[str, Mock]: Словарь со всеми мокированными объектами
        """
        mocks = {
            'api': Mock(),
            'storage': Mock(),
            'search_handler': Mock(),
            'display_handler': Mock(),
            'source_selector': Mock(),
            'vacancy': Mock(),
            'formatter': Mock(),
            'ui_helpers': {
                'confirm_action': Mock(),
                'get_user_input': Mock(),
                'filter_vacancies_by_keyword': Mock()
            }
        }
        
        # Настройка API мока
        mocks['api'].get_vacancies_from_sources.return_value = []
        mocks['api'].get_vacancies_from_target_companies.return_value = []
        mocks['api'].clear_cache.return_value = None
        
        # Настройка storage мока
        mocks['storage'].get_vacancies.return_value = []
        mocks['storage'].delete_all_vacancies.return_value = True
        mocks['storage'].add_vacancy.return_value = []
        mocks['storage'].delete_vacancies_batch.return_value = 0
        mocks['storage'].delete_vacancy_by_id.return_value = True
        
        # Настройка обработчиков
        mocks['search_handler'].search_vacancies.return_value = None
        mocks['display_handler'].show_all_saved_vacancies.return_value = None
        mocks['display_handler'].show_top_vacancies_by_salary.return_value = None
        mocks['display_handler'].search_saved_vacancies_by_keyword.return_value = None
        
        # Настройка селектора источников
        mocks['source_selector'].get_user_source_choice.return_value = {"hh.ru"}
        mocks['source_selector'].display_sources_info.return_value = None
        
        # Настройка создания вакансий
        test_vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com",
            source="hh.ru"
        )
        mocks['vacancy'].from_dict.return_value = test_vacancy
        
        # Настройка форматтера
        mocks['formatter'].format_vacancy_info.return_value = "Formatted vacancy info"
        
        # Настройка UI helpers
        mocks['ui_helpers']['confirm_action'].return_value = True
        mocks['ui_helpers']['get_user_input'].return_value = "test input"
        mocks['ui_helpers']['filter_vacancies_by_keyword'].return_value = []
        
        return mocks

    @pytest.fixture
    def coordinator(self, consolidated_mocks):
        """
        Фикстура для создания VacancyOperationsCoordinator с полными моками
        
        Args:
            consolidated_mocks: Консолидированные моки
            
        Returns:
            VacancyOperationsCoordinator: Координатор с мокированными зависимостями
        """
        with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancySearchHandler') as mock_search_class, \
             patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyDisplayHandler') as mock_display_class, \
             patch('src.ui_interfaces.vacancy_operations_coordinator.SourceSelector') as mock_selector_class:
            
            # Настройка классов-моков
            mock_search_class.return_value = consolidated_mocks['search_handler']
            mock_display_class.return_value = consolidated_mocks['display_handler']
            mock_selector_class.return_value = consolidated_mocks['source_selector']
            
            coordinator = VacancyOperationsCoordinator(
                consolidated_mocks['api'], 
                consolidated_mocks['storage']
            )
            
            return coordinator

    def test_coordinator_initialization(self, coordinator, consolidated_mocks):
        """
        Тест правильной инициализации VacancyOperationsCoordinator
        
        Проверяет, что все компоненты правильно инициализированы
        """
        assert coordinator.unified_api == consolidated_mocks['api']
        assert coordinator.storage == consolidated_mocks['storage']
        assert coordinator.search_handler is not None
        assert coordinator.display_handler is not None
        assert coordinator.source_selector is not None

    def test_handle_vacancy_search(self, coordinator, consolidated_mocks):
        """Тест делегирования поиска вакансий обработчику"""
        coordinator.handle_vacancy_search()
        consolidated_mocks['search_handler'].search_vacancies.assert_called_once()

    def test_handle_show_saved_vacancies(self, coordinator, consolidated_mocks):
        """Тест делегирования отображения сохраненных вакансий"""
        coordinator.handle_show_saved_vacancies()
        consolidated_mocks['display_handler'].show_all_saved_vacancies.assert_called_once()

    def test_handle_top_vacancies_by_salary(self, coordinator, consolidated_mocks):
        """Тест делегирования получения топ вакансий по зарплате"""
        coordinator.handle_top_vacancies_by_salary()
        consolidated_mocks['display_handler'].show_top_vacancies_by_salary.assert_called_once()

    def test_handle_search_saved_by_keyword(self, coordinator, consolidated_mocks):
        """Тест делегирования поиска сохраненных вакансий по ключевому слову"""
        coordinator.handle_search_saved_by_keyword()
        consolidated_mocks['display_handler'].search_saved_vacancies_by_keyword.assert_called_once()

    @patch('builtins.print')
    def test_handle_cache_cleanup_success(self, mock_print, coordinator, consolidated_mocks):
        """Тест успешной очистки кэша"""
        with patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True):
            coordinator.handle_cache_cleanup()
            
            consolidated_mocks['source_selector'].get_user_source_choice.assert_called_once()
            consolidated_mocks['source_selector'].display_sources_info.assert_called_once_with({"hh.ru"})
            consolidated_mocks['api'].clear_cache.assert_called_once_with({"hh": True, "sj": False})

    @patch('builtins.print')
    def test_handle_cache_cleanup_cancelled(self, mock_print, coordinator, consolidated_mocks):
        """Тест отмены очистки кэша"""
        with patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=False):
            coordinator.handle_cache_cleanup()
            
            consolidated_mocks['source_selector'].get_user_source_choice.assert_called_once()
            consolidated_mocks['api'].clear_cache.assert_not_called()

    @patch('builtins.print')
    def test_handle_cache_cleanup_no_sources(self, mock_print, coordinator, consolidated_mocks):
        """Тест очистки кэша без выбранных источников"""
        consolidated_mocks['source_selector'].get_user_source_choice.return_value = None
        
        coordinator.handle_cache_cleanup()
        
        consolidated_mocks['source_selector'].get_user_source_choice.assert_called_once()
        consolidated_mocks['api'].clear_cache.assert_not_called()

    @patch('builtins.print')
    @patch('builtins.input', return_value='0')
    def test_handle_delete_vacancies_cancel(self, mock_input, mock_print, coordinator, consolidated_mocks):
        """Тест отмены удаления вакансий"""
        test_vacancies = [
            Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        ]
        consolidated_mocks['storage'].get_vacancies.return_value = test_vacancies
        
        coordinator.handle_delete_vacancies()
        
        consolidated_mocks['storage'].get_vacancies.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value='1')
    def test_handle_delete_all_vacancies_success(self, mock_input, mock_print, coordinator, consolidated_mocks):
        """Тест успешного удаления всех вакансий"""
        test_vacancies = [
            Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        ]
        consolidated_mocks['storage'].get_vacancies.return_value = test_vacancies
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True):
            coordinator.handle_delete_vacancies()
            
            consolidated_mocks['storage'].delete_all_vacancies.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value='2')
    def test_handle_delete_by_keyword(self, mock_input, mock_print, coordinator, consolidated_mocks):
        """Тест удаления вакансий по ключевому слову"""
        test_vacancies = [
            Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        ]
        consolidated_mocks['storage'].get_vacancies.return_value = test_vacancies
        consolidated_mocks['storage'].delete_vacancies_batch.return_value = 1
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value="Python"), \
             patch('src.utils.ui_helpers.filter_vacancies_by_keyword', return_value=test_vacancies), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True):
            
            coordinator.handle_delete_vacancies()
            
            consolidated_mocks['storage'].delete_vacancies_batch.assert_called_once_with(["123"])

    @patch('builtins.print')
    @patch('builtins.input', return_value='3')
    def test_handle_delete_by_id_found(self, mock_input, mock_print, coordinator, consolidated_mocks):
        """Тест удаления вакансии по найденному ID"""
        test_vacancy = Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        consolidated_mocks['storage'].get_vacancies.return_value = [test_vacancy]
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value="123"), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyFormatter') as mock_formatter_class:
            
            mock_formatter = Mock()
            mock_formatter.format_vacancy_info.return_value = "Formatted info"
            mock_formatter_class.return_value = mock_formatter
            
            coordinator.handle_delete_vacancies()
            
            consolidated_mocks['storage'].delete_vacancy_by_id.assert_called_once_with("123")

    @patch('builtins.print')
    @patch('builtins.input', return_value='3')
    def test_handle_delete_by_id_not_found(self, mock_input, mock_print, coordinator, consolidated_mocks):
        """Тест удаления вакансии по несуществующему ID"""
        test_vacancy = Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        consolidated_mocks['storage'].get_vacancies.return_value = [test_vacancy]
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value="999"):
            coordinator.handle_delete_vacancies()
            
            consolidated_mocks['storage'].delete_vacancy_by_id.assert_not_called()

    @patch('builtins.print')
    def test_handle_delete_vacancies_empty_storage(self, mock_print, coordinator, consolidated_mocks):
        """Тест удаления вакансий при пустом хранилище"""
        consolidated_mocks['storage'].get_vacancies.return_value = []
        
        coordinator.handle_delete_vacancies()
        
        consolidated_mocks['storage'].get_vacancies.assert_called_once()

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_handle_superjob_setup(self, mock_print, mock_input):
        """Тест настройки SuperJob API"""
        with patch.dict(os.environ, {"SUPERJOB_API_KEY": "test_key"}):
            VacancyOperationsCoordinator.handle_superjob_setup()
            
            mock_print.assert_called()

    @patch('builtins.print')
    def test_get_vacancies_from_sources_success(self, mock_print, coordinator, consolidated_mocks):
        """Тест успешного получения вакансий из источников"""
        # Настройка тестовых данных
        mock_vacancy_data = [{"id": "123", "title": "Python Developer", "url": "https://test.com"}]
        test_vacancy = Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        
        consolidated_mocks['api'].get_vacancies_from_sources.return_value = mock_vacancy_data
        consolidated_mocks['storage'].add_vacancy.return_value = ["Vacancy added"]
        consolidated_mocks['storage'].get_vacancies.return_value = [test_vacancy]
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.Vacancy') as mock_vacancy_class:
            mock_vacancy_class.from_dict.return_value = test_vacancy
            
            result = coordinator.get_vacancies_from_sources("Python", ["hh"])
            
            assert len(result) == 1
            assert result[0] == test_vacancy
            consolidated_mocks['api'].get_vacancies_from_sources.assert_called_once_with(
                search_query="Python", sources=["hh"]
            )

    @patch('builtins.print')
    def test_get_vacancies_from_sources_error(self, mock_print, coordinator, consolidated_mocks):
        """Тест обработки ошибки при получении вакансий из источников"""
        consolidated_mocks['api'].get_vacancies_from_sources.side_effect = Exception("API Error")
        
        result = coordinator.get_vacancies_from_sources("Python", ["hh"])
        
        assert result == []

    @patch('builtins.print')
    def test_get_vacancies_from_target_companies_success(self, mock_print, coordinator, consolidated_mocks):
        """Тест успешного получения вакансий от целевых компаний"""
        mock_vacancy_data = [{"id": "123", "title": "Python Developer", "url": "https://test.com"}]
        test_vacancy = Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        
        consolidated_mocks['api'].get_vacancies_from_target_companies.return_value = mock_vacancy_data
        consolidated_mocks['storage'].add_vacancy.return_value = ["Vacancy added"]
        consolidated_mocks['storage'].get_vacancies.return_value = [test_vacancy]
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.Vacancy') as mock_vacancy_class:
            mock_vacancy_class.from_dict.return_value = test_vacancy
            
            result = coordinator.get_vacancies_from_target_companies("Python", ["hh"])
            
            assert len(result) == 1
            assert result[0] == test_vacancy
            consolidated_mocks['api'].get_vacancies_from_target_companies.assert_called_once_with(
                search_query="Python", sources=["hh"]
            )

    @patch('builtins.print')
    def test_get_vacancies_from_target_companies_error(self, mock_print, coordinator, consolidated_mocks):
        """Тест обработки ошибки при получении вакансий от целевых компаний"""
        consolidated_mocks['api'].get_vacancies_from_target_companies.side_effect = Exception("API Error")
        
        result = coordinator.get_vacancies_from_target_companies("Python", ["hh"])
        
        assert result == []

    def test_handle_delete_all_vacancies_success(self, coordinator, consolidated_mocks):
        """Тест успешного удаления всех вакансий"""
        with patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True), \
             patch('builtins.print'):
            
            coordinator._handle_delete_all_vacancies()
            
            consolidated_mocks['storage'].delete_all_vacancies.assert_called_once()

    def test_handle_delete_all_vacancies_cancelled(self, coordinator, consolidated_mocks):
        """Тест отмены удаления всех вакансий"""
        with patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=False), \
             patch('builtins.print'):
            
            coordinator._handle_delete_all_vacancies()
            
            consolidated_mocks['storage'].delete_all_vacancies.assert_not_called()

    def test_handle_delete_by_keyword_found(self, coordinator, consolidated_mocks):
        """Тест удаления вакансий по найденному ключевому слову"""
        test_vacancies = [
            Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        ]
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value="Python"), \
             patch('src.utils.ui_helpers.filter_vacancies_by_keyword', return_value=test_vacancies), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True), \
             patch('builtins.print'):
            
            consolidated_mocks['storage'].delete_vacancies_batch.return_value = 1
            
            coordinator._handle_delete_by_keyword(test_vacancies)
            
            consolidated_mocks['storage'].delete_vacancies_batch.assert_called_once_with(["123"])

    def test_handle_delete_by_keyword_not_found(self, coordinator, consolidated_mocks):
        """Тест удаления вакансий по ненайденному ключевому слову"""
        test_vacancies = [
            Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        ]
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value="Java"), \
             patch('src.utils.ui_helpers.filter_vacancies_by_keyword', return_value=[]), \
             patch('builtins.print'):
            
            coordinator._handle_delete_by_keyword(test_vacancies)
            
            consolidated_mocks['storage'].delete_vacancies_batch.assert_not_called()

    def test_handle_delete_by_keyword_empty_input(self, coordinator, consolidated_mocks):
        """Тест удаления вакансий при пустом вводе ключевого слова"""
        test_vacancies = []
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value=""), \
             patch('builtins.print'):
            
            coordinator._handle_delete_by_keyword(test_vacancies)
            
            consolidated_mocks['storage'].delete_vacancies_batch.assert_not_called()

    def test_handle_delete_by_id_found_and_confirmed(self, coordinator, consolidated_mocks):
        """Тест удаления найденной вакансии по ID с подтверждением"""
        test_vacancy = Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        test_vacancies = [test_vacancy]
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value="123"), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=True), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyFormatter') as mock_formatter_class, \
             patch('builtins.print'):
            
            mock_formatter = Mock()
            mock_formatter.format_vacancy_info.return_value = "Formatted vacancy info"
            mock_formatter_class.return_value = mock_formatter
            
            coordinator._handle_delete_by_id(test_vacancies)
            
            consolidated_mocks['storage'].delete_vacancy_by_id.assert_called_once_with("123")

    def test_handle_delete_by_id_found_not_confirmed(self, coordinator, consolidated_mocks):
        """Тест отмены удаления найденной вакансии по ID"""
        test_vacancy = Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        test_vacancies = [test_vacancy]
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value="123"), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.confirm_action', return_value=False), \
             patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyFormatter') as mock_formatter_class, \
             patch('builtins.print'):
            
            mock_formatter = Mock()
            mock_formatter_class.return_value = mock_formatter
            
            coordinator._handle_delete_by_id(test_vacancies)
            
            consolidated_mocks['storage'].delete_vacancy_by_id.assert_not_called()

    def test_handle_delete_by_id_not_found(self, coordinator, consolidated_mocks):
        """Тест удаления несуществующей вакансии по ID"""
        test_vacancy = Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        test_vacancies = [test_vacancy]
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value="999"), \
             patch('builtins.print'):
            
            coordinator._handle_delete_by_id(test_vacancies)
            
            consolidated_mocks['storage'].delete_vacancy_by_id.assert_not_called()

    def test_handle_delete_by_id_empty_input(self, coordinator, consolidated_mocks):
        """Тест удаления вакансии при пустом вводе ID"""
        test_vacancies = []
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.get_user_input', return_value=""), \
             patch('builtins.print'):
            
            coordinator._handle_delete_by_id(test_vacancies)
            
            consolidated_mocks['storage'].delete_vacancy_by_id.assert_not_called()

    def test_show_vacancy_for_confirmation(self, coordinator, consolidated_mocks):
        """Тест отображения вакансии для подтверждения удаления"""
        test_vacancy = Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru")
        
        with patch('src.ui_interfaces.vacancy_operations_coordinator.VacancyFormatter') as mock_formatter_class, \
             patch('builtins.print'):
            
            mock_formatter = Mock()
            mock_formatter.format_vacancy_info.return_value = "Formatted vacancy info"
            mock_formatter_class.return_value = mock_formatter
            
            coordinator._show_vacancy_for_confirmation(test_vacancy)
            
            mock_formatter.format_vacancy_info.assert_called_once_with(test_vacancy)
