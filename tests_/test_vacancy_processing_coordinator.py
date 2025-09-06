"""
Тесты для координатора обработки вакансий
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch
import pytest

# Мокаем psycopg2 перед импортом
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.sql'] = MagicMock()

# Добавляем путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.storage.services.vacancy_processing_coordinator import VacancyProcessingCoordinator


class MockDBManager:
    """Мок менеджера базы данных"""
    
    def __init__(self):
        self.connected = True
    
    def get_connection(self):
        return Mock()


class MockVacancy:
    """Мок вакансии"""
    
    def __init__(self, id_val, title, employer_id=None):
        self.id = id_val
        self.title = title
        self.employer_id = employer_id
        self.employer = Mock(id=employer_id) if employer_id else None


class TestVacancyProcessingCoordinator:
    """Тесты координатора обработки вакансий"""
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.mock_db_manager = MockDBManager()
        
        # Мокаем компоненты
        with patch('src.storage.services.vacancy_processing_coordinator.CompanyIDFilterService') as mock_filter, \
             patch('src.storage.services.vacancy_processing_coordinator.SQLDeduplicationService') as mock_dedup:
            
            self.mock_filter_service = Mock()
            self.mock_dedup_service = Mock()
            
            mock_filter.return_value = self.mock_filter_service
            mock_dedup.return_value = self.mock_dedup_service
            
            self.coordinator = VacancyProcessingCoordinator(self.mock_db_manager)
            self.coordinator.id_filter_service = self.mock_filter_service
            self.coordinator.deduplication_service = self.mock_dedup_service
    
    def test_coordinator_initialization(self):
        """Тест инициализации координатора"""
        with patch('src.storage.services.vacancy_processing_coordinator.CompanyIDFilterService') as mock_filter, \
             patch('src.storage.services.vacancy_processing_coordinator.SQLDeduplicationService') as mock_dedup:
            
            coordinator = VacancyProcessingCoordinator(self.mock_db_manager)
            
            # Проверяем что сервисы были созданы
            mock_filter.assert_called_once_with(self.mock_db_manager)
            mock_dedup.assert_called_once_with(self.mock_db_manager)
    
    def test_process_vacancies_empty_list(self):
        """Тест обработки пустого списка вакансий"""
        result = self.coordinator.process_vacancies([])
        
        assert result == []
        self.mock_filter_service.filter_by_company_ids.assert_not_called()
        self.mock_dedup_service.deduplicate_vacancies.assert_not_called()
    
    def test_process_vacancies_full_processing(self):
        """Тест полной обработки вакансий с фильтрацией и дедупликацией"""
        # Подготавливаем тестовые данные
        input_vacancies = [MockVacancy(1, "Python Dev"), MockVacancy(2, "Java Dev")]
        filtered_vacancies = [MockVacancy(1, "Python Dev")]
        deduplicated_vacancies = [MockVacancy(1, "Python Dev")]
        
        # Настраиваем моки
        self.mock_filter_service.filter_by_company_ids.return_value = filtered_vacancies
        self.mock_dedup_service.deduplicate_vacancies.return_value = deduplicated_vacancies
        
        # Тестируем
        result = self.coordinator.process_vacancies(
            input_vacancies, 
            apply_company_filter=True, 
            apply_deduplication=True
        )
        
        # Проверяем результат
        assert result == deduplicated_vacancies
        
        # Проверяем вызовы
        self.mock_filter_service.filter_by_company_ids.assert_called_once_with(input_vacancies)
        self.mock_dedup_service.deduplicate_vacancies.assert_called_once_with(filtered_vacancies)
    
    def test_process_vacancies_filter_only(self):
        """Тест обработки только с фильтрацией"""
        input_vacancies = [MockVacancy(1, "Python Dev"), MockVacancy(2, "Java Dev")]
        filtered_vacancies = [MockVacancy(1, "Python Dev")]
        
        self.mock_filter_service.filter_by_company_ids.return_value = filtered_vacancies
        
        result = self.coordinator.process_vacancies(
            input_vacancies, 
            apply_company_filter=True, 
            apply_deduplication=False
        )
        
        assert result == filtered_vacancies
        self.mock_filter_service.filter_by_company_ids.assert_called_once_with(input_vacancies)
        self.mock_dedup_service.deduplicate_vacancies.assert_not_called()
    
    def test_process_vacancies_deduplication_only(self):
        """Тест обработки только с дедупликацией"""
        input_vacancies = [MockVacancy(1, "Python Dev"), MockVacancy(2, "Java Dev")]
        deduplicated_vacancies = [MockVacancy(1, "Python Dev")]
        
        self.mock_dedup_service.deduplicate_vacancies.return_value = deduplicated_vacancies
        
        result = self.coordinator.process_vacancies(
            input_vacancies, 
            apply_company_filter=False, 
            apply_deduplication=True
        )
        
        assert result == deduplicated_vacancies
        self.mock_filter_service.filter_by_company_ids.assert_not_called()
        self.mock_dedup_service.deduplicate_vacancies.assert_called_once_with(input_vacancies)
    
    def test_process_vacancies_no_processing(self):
        """Тест обработки без фильтрации и дедупликации"""
        input_vacancies = [MockVacancy(1, "Python Dev"), MockVacancy(2, "Java Dev")]
        
        result = self.coordinator.process_vacancies(
            input_vacancies, 
            apply_company_filter=False, 
            apply_deduplication=False
        )
        
        assert result == input_vacancies
        self.mock_filter_service.filter_by_company_ids.assert_not_called()
        self.mock_dedup_service.deduplicate_vacancies.assert_not_called()
    
    def test_process_vacancies_filter_returns_empty(self):
        """Тест обработки когда фильтр возвращает пустой список"""
        input_vacancies = [MockVacancy(1, "Python Dev"), MockVacancy(2, "Java Dev")]
        
        self.mock_filter_service.filter_by_company_ids.return_value = []
        
        result = self.coordinator.process_vacancies(input_vacancies)
        
        assert result == []
        self.mock_filter_service.filter_by_company_ids.assert_called_once_with(input_vacancies)
        # Дедупликация не должна вызываться, так как после фильтра ничего не осталось
        self.mock_dedup_service.deduplicate_vacancies.assert_not_called()
    
    def test_filter_only_method(self):
        """Тест метода filter_only"""
        input_vacancies = [MockVacancy(1, "Python Dev")]
        filtered_vacancies = [MockVacancy(1, "Python Dev")]
        
        self.mock_filter_service.filter_by_company_ids.return_value = filtered_vacancies
        
        result = self.coordinator.filter_only(input_vacancies)
        
        assert result == filtered_vacancies
        self.mock_filter_service.filter_by_company_ids.assert_called_once_with(input_vacancies)
        self.mock_dedup_service.deduplicate_vacancies.assert_not_called()
    
    def test_deduplicate_only_method(self):
        """Тест метода deduplicate_only"""
        input_vacancies = [MockVacancy(1, "Python Dev")]
        deduplicated_vacancies = [MockVacancy(1, "Python Dev")]
        
        self.mock_dedup_service.deduplicate_vacancies.return_value = deduplicated_vacancies
        
        result = self.coordinator.deduplicate_only(input_vacancies)
        
        assert result == deduplicated_vacancies
        self.mock_filter_service.filter_by_company_ids.assert_not_called()
        self.mock_dedup_service.deduplicate_vacancies.assert_called_once_with(input_vacancies)
    
    def test_get_target_company_stats(self):
        """Тест получения статистики целевых компаний"""
        expected_stats = ([1, 2, 3], [4, 5, 6])
        self.mock_filter_service.get_target_company_stats.return_value = expected_stats
        
        result = self.coordinator.get_target_company_stats()
        
        assert result == expected_stats
        self.mock_filter_service.get_target_company_stats.assert_called_once()
    
    def test_get_processing_summary_empty_vacancies(self):
        """Тест получения сводки для пустого списка вакансий"""
        result = self.coordinator.get_processing_summary([])
        
        expected = {
            "total_vacancies": 0,
            "after_company_filter": 0,
            "after_deduplication": 0,
            "target_hh_ids": 0,
            "target_sj_ids": 0
        }
        
        assert result == expected
    
    def test_get_processing_summary_with_vacancies(self):
        """Тест получения сводки для списка вакансий"""
        input_vacancies = [MockVacancy(1, "Python Dev"), MockVacancy(2, "Java Dev"), MockVacancy(3, "C++ Dev")]
        filtered_vacancies = [MockVacancy(1, "Python Dev"), MockVacancy(2, "Java Dev")]
        deduplicated_vacancies = [MockVacancy(1, "Python Dev")]
        
        # Настраиваем моки
        self.mock_filter_service.filter_by_company_ids.return_value = filtered_vacancies
        self.mock_dedup_service.deduplicate_vacancies.return_value = deduplicated_vacancies
        self.mock_filter_service.get_target_company_stats.return_value = ([1, 2], [3, 4, 5])
        
        result = self.coordinator.get_processing_summary(input_vacancies)
        
        expected = {
            "total_vacancies": 3,
            "after_company_filter": 2,
            "after_deduplication": 1,
            "target_hh_ids": 2,
            "target_sj_ids": 3
        }
        
        assert result == expected
        
        # Проверяем что методы вызывались
        self.mock_filter_service.get_target_company_stats.assert_called_once()
        self.mock_filter_service.filter_by_company_ids.assert_called_once_with(input_vacancies)
        self.mock_dedup_service.deduplicate_vacancies.assert_called_once_with(filtered_vacancies)
    
    def test_get_processing_summary_filter_returns_empty(self):
        """Тест получения сводки когда фильтр возвращает пустой результат"""
        input_vacancies = [MockVacancy(1, "Python Dev")]
        
        # Настраиваем моки
        self.mock_filter_service.filter_by_company_ids.return_value = []
        self.mock_filter_service.get_target_company_stats.return_value = ([1], [2])
        
        result = self.coordinator.get_processing_summary(input_vacancies)
        
        expected = {
            "total_vacancies": 1,
            "after_company_filter": 0,
            "after_deduplication": 0,
            "target_hh_ids": 1,
            "target_sj_ids": 1
        }
        
        assert result == expected
        
        # Дедупликация не должна вызываться для пустого списка
        self.mock_dedup_service.deduplicate_vacancies.assert_not_called()