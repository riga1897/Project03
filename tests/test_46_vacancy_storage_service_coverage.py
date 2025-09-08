"""
100% покрытие тестами для VacancyStorageService

Покрывает все методы и сценарии работы с вакансиями через сервисный слой
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.storage.services.vacancy_storage_service import VacancyStorageService
from src.vacancies.models import Vacancy, Employer


class TestVacancyStorageServiceInit:
    """Покрытие инициализации и конфигурации"""

    @patch('src.storage.services.vacancy_storage_service.DBManager')
    @patch('src.storage.services.vacancy_storage_service.VacancyProcessingCoordinator')
    @patch('src.storage.services.vacancy_storage_service.DeduplicationService')
    @patch('src.storage.services.vacancy_storage_service.TargetCompanies')
    def test_init_with_default_db_manager(self, mock_target_companies, mock_dedup, mock_coordinator, mock_db_manager):
        """Покрытие: инициализация с db_manager=None"""
        mock_target_companies.get_all_companies.return_value = ["Company1", "Company2"]
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        
        service = VacancyStorageService()
        
        assert service.db_manager == mock_db_instance
        assert service.processing_coordinator is not None
        assert service.deduplication_service is not None
        assert service.target_companies == ["Company1", "Company2"]
        mock_db_manager.assert_called_once_with()

    @patch('src.storage.services.vacancy_storage_service.VacancyProcessingCoordinator')
    @patch('src.storage.services.vacancy_storage_service.DeduplicationService')
    @patch('src.storage.services.vacancy_storage_service.TargetCompanies')
    def test_init_with_custom_db_manager(self, mock_target_companies, mock_dedup, mock_coordinator):
        """Покрытие: инициализация с кастомным db_manager"""
        mock_target_companies.get_all_companies.return_value = []
        custom_db_manager = Mock()
        
        service = VacancyStorageService(db_manager=custom_db_manager)
        
        assert service.db_manager == custom_db_manager
        mock_coordinator.assert_called_once_with(custom_db_manager)

    @patch.dict('os.environ', {'FILTER_ONLY_WITH_SALARY': 'true'})
    @patch('src.storage.services.vacancy_storage_service.DBManager')
    @patch('src.storage.services.vacancy_storage_service.VacancyProcessingCoordinator')
    @patch('src.storage.services.vacancy_storage_service.DeduplicationService')
    @patch('src.storage.services.vacancy_storage_service.TargetCompanies')
    def test_should_filter_by_salary_true_cases(self, mock_target, mock_dedup, mock_coord, mock_db):
        """Покрытие: _should_filter_by_salary возвращает True"""
        mock_target.get_all_companies.return_value = []
        service = VacancyStorageService()
        
        assert service._should_filter_by_salary() is True

    @patch.dict('os.environ', {}, clear=True)
    @patch('src.storage.services.vacancy_storage_service.DBManager')
    @patch('src.storage.services.vacancy_storage_service.VacancyProcessingCoordinator')
    @patch('src.storage.services.vacancy_storage_service.DeduplicationService')
    @patch('src.storage.services.vacancy_storage_service.TargetCompanies')
    def test_should_filter_by_salary_false_cases(self, mock_target, mock_dedup, mock_coord, mock_db):
        """Покрытие: _should_filter_by_salary возвращает False"""
        mock_target.get_all_companies.return_value = []
        service = VacancyStorageService()
        
        assert service._should_filter_by_salary() is False

    @patch.dict('os.environ', {'FILTER_ONLY_WITH_SALARY': '1'})
    @patch('src.storage.services.vacancy_storage_service.DBManager')
    @patch('src.storage.services.vacancy_storage_service.VacancyProcessingCoordinator')
    @patch('src.storage.services.vacancy_storage_service.DeduplicationService')
    @patch('src.storage.services.vacancy_storage_service.TargetCompanies')
    def test_should_filter_by_salary_various_true_values(self, mock_target, mock_dedup, mock_coord, mock_db):
        """Покрытие: различные значения для включения фильтра"""
        mock_target.get_all_companies.return_value = []
        service = VacancyStorageService()
        
        assert service._should_filter_by_salary() is True


class TestVacancyStorageServiceProcessing:
    """Покрытие методов обработки и фильтрации вакансий"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_filter_and_deduplicate_empty_list(self, mock_logger):
        """Покрытие: обработка пустого списка вакансий"""
        service = VacancyStorageService()
        result = service.filter_and_deduplicate_vacancies([])
        
        assert result == []
        mock_logger.info.assert_called_with("Получен пустой список вакансий")

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_filter_and_deduplicate_success_path(self, mock_logger):
        """Покрытие: успешная обработка вакансий"""
        service = VacancyStorageService()
        
        # Создаем тестовые вакансии
        vacancy1 = Vacancy(vacancy_id="1", name="Test Job", alternate_url="http://test.com")
        vacancy2 = Vacancy(vacancy_id="2", name="Another Job", alternate_url="http://test2.com")
        test_vacancies = [vacancy1, vacancy2]
        
        # Мокируем зависимости
        with patch.object(service, 'processing_coordinator') as mock_coord:
            mock_coord.process_vacancies.return_value = [vacancy1]
            
            with patch.object(service, '_enrich_with_company_data') as mock_enrich:
                mock_enrich.return_value = [vacancy1]
                
                result = service.filter_and_deduplicate_vacancies(test_vacancies)
                
                assert result == [vacancy1]
                mock_coord.process_vacancies.assert_called_once_with(
                    test_vacancies, 
                    apply_company_filter=True, 
                    apply_deduplication=True
                )

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_filter_and_deduplicate_coordinator_returns_empty(self, mock_logger):
        """Покрытие: координатор возвращает пустой список"""
        service = VacancyStorageService()
        vacancy1 = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        
        with patch.object(service, 'processing_coordinator') as mock_coord:
            mock_coord.process_vacancies.return_value = []
            
            result = service.filter_and_deduplicate_vacancies([vacancy1])
            
            assert result == []
            mock_logger.warning.assert_called_with("Координатор не вернул ни одной вакансии")

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_filter_and_deduplicate_coordinator_error_fallback(self, mock_logger):
        """Покрытие: ошибка в координаторе, использование fallback"""
        service = VacancyStorageService()
        vacancy1 = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        test_vacancies = [vacancy1]
        
        with patch.object(service, 'processing_coordinator') as mock_coord:
            mock_coord.process_vacancies.side_effect = Exception("Coordinator error")
            
            with patch.object(service, '_legacy_filter_and_deduplicate') as mock_legacy:
                mock_legacy.return_value = [vacancy1]
                
                result = service.filter_and_deduplicate_vacancies(test_vacancies)
                
                assert result == [vacancy1]
                mock_logger.error.assert_called_once()
                mock_legacy.assert_called_once_with(test_vacancies)

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_legacy_filter_and_deduplicate_success(self, mock_logger):
        """Покрытие: успешная legacy обработка"""
        service = VacancyStorageService()
        vacancy1 = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        test_vacancies = [vacancy1]
        
        with patch.object(service, 'deduplication_service') as mock_dedup:
            mock_dedup.process.return_value = [vacancy1]
            
            with patch.object(service, '_enrich_with_company_data') as mock_enrich:
                mock_enrich.return_value = [vacancy1]
                
                result = service._legacy_filter_and_deduplicate(test_vacancies)
                
                assert result == [vacancy1]
                mock_dedup.process.assert_called_once_with(test_vacancies, service.db_manager)

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_legacy_filter_and_deduplicate_no_vacancies_after_filter(self, mock_logger):
        """Покрытие: legacy фильтрация не оставляет вакансий"""
        service = VacancyStorageService()
        vacancy1 = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        
        # Эмулируем что фильтрация оставила пустой список
        filtered_vacancies = []
        
        with patch.object(service, 'deduplication_service'):
            result = service._legacy_filter_and_deduplicate([vacancy1])
            
            assert result == []
            mock_logger.warning.assert_called_with("После legacy фильтрации не осталось вакансий")

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_legacy_filter_and_deduplicate_error(self, mock_logger):
        """Покрытие: ошибка в legacy обработке"""
        service = VacancyStorageService()
        vacancy1 = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        test_vacancies = [vacancy1]
        
        with patch.object(service, 'deduplication_service') as mock_dedup:
            mock_dedup.process.side_effect = Exception("Legacy error")
            
            result = service._legacy_filter_and_deduplicate(test_vacancies)
            
            assert result == test_vacancies
            mock_logger.error.assert_called_once()


class TestVacancyStorageServiceCompanyData:
    """Покрытие методов работы с данными компаний"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_enrich_with_company_data_success(self, mock_logger):
        """Покрытие: успешное обогащение данными компаний"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="1", 
            name="Test", 
            alternate_url="http://test.com",
            employer={"name": "Test Company", "id": "123"}
        )
        
        with patch.object(service, '_get_company_id_mapping') as mock_mapping:
            mock_mapping.return_value = {"123": 456}
            
            with patch.object(service, '_find_company_id') as mock_find:
                mock_find.return_value = 456
                
                result = service._enrich_with_company_data([vacancy])
                
                assert len(result) == 1
                assert result[0].company_id == 456
                assert result[0].company_name == "Test Company"

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_enrich_with_company_data_error(self, mock_logger):
        """Покрытие: ошибка при обогащении данными компаний"""
        service = VacancyStorageService()
        vacancy = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        
        with patch.object(service, '_get_company_id_mapping') as mock_mapping:
            mock_mapping.side_effect = Exception("Mapping error")
            
            result = service._enrich_with_company_data([vacancy])
            
            assert result == [vacancy]
            mock_logger.warning.assert_called_once()

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_get_company_id_mapping_success(self, mock_logger):
        """Покрытие: успешное получение соответствий ID компаний"""
        service = VacancyStorageService()
        
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, "hh123", None),
            (2, None, "sj456"),
            (3, "hh789", "sj789")
        ]
        
        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        with patch.object(service.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection
            
            result = service._get_company_id_mapping()
            
            expected = {"hh123": 1, "sj456": 2, "hh789": 3, "sj789": 3}
            assert result == expected
            mock_logger.info.assert_called_with("Загружено 4 соответствий ID компаний")

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_get_company_id_mapping_error(self, mock_logger):
        """Покрытие: ошибка при получении соответствий компаний"""
        service = VacancyStorageService()
        
        with patch.object(service.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.side_effect = Exception("DB error")
            
            result = service._get_company_id_mapping()
            
            assert result == {}
            mock_logger.error.assert_called_once()

    def test_find_company_id_with_dict_employer(self):
        """Покрытие: поиск ID компании с employer как словарь"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="1", 
            name="Test", 
            alternate_url="http://test.com",
            employer={"id": "123", "name": "Test Company"}
        )
        
        company_mapping = {"123": 456}
        
        result = service._find_company_id(vacancy, company_mapping)
        
        assert result == 456

    def test_find_company_id_with_object_employer(self):
        """Покрытие: поиск ID компании с employer как объект"""
        service = VacancyStorageService()
        
        mock_employer = Mock()
        mock_employer.id = "789"
        
        vacancy = Vacancy(
            vacancy_id="1", 
            name="Test", 
            alternate_url="http://test.com",
            employer=mock_employer
        )
        
        company_mapping = {"789": 999}
        
        result = service._find_company_id(vacancy, company_mapping)
        
        assert result == 999

    def test_find_company_id_no_employer(self):
        """Покрытие: поиск ID компании без employer"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        vacancy.employer = None
        
        result = service._find_company_id(vacancy, {"123": 456})
        
        assert result is None

    def test_find_company_id_no_employer_id(self):
        """Покрытие: поиск ID компании без ID в employer"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="1", 
            name="Test", 
            alternate_url="http://test.com",
            employer={"name": "Test Company"}  # Без ID
        )
        
        result = service._find_company_id(vacancy, {"123": 456})
        
        assert result is None

    def test_find_company_id_not_in_mapping(self):
        """Покрытие: ID компании не найден в соответствиях"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="1", 
            name="Test", 
            alternate_url="http://test.com",
            employer={"id": "999", "name": "Unknown Company"}
        )
        
        result = service._find_company_id(vacancy, {"123": 456})
        
        assert result is None


class TestVacancyStorageServiceDiagnostics:
    """Покрытие метода диагностики зарплат"""

    def test_log_salary_diagnostics_empty_list(self, capsys):
        """Покрытие: диагностика пустого списка вакансий"""
        service = VacancyStorageService()
        
        service._log_salary_diagnostics("TEST_STAGE", [])
        
        captured = capsys.readouterr()
        assert "🔍 [TEST_STAGE] Список вакансий пуст" in captured.out

    def test_log_salary_diagnostics_with_dict_salary(self, capsys):
        """Покрытие: диагностика вакансий с зарплатой как словарь"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="1",
            name="Python Developer with good salary",
            alternate_url="http://test.com",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            employer={"name": "Good Company", "id": "123"}
        )
        
        service._log_salary_diagnostics("WITH_SALARY", [vacancy])
        
        captured = capsys.readouterr()
        assert "🔍 [WITH_SALARY] Анализ 1 вакансий:" in captured.out
        assert "от 100,000 до 150,000 RUR" in captured.out
        assert "Python Developer with good salary" in captured.out

    def test_log_salary_diagnostics_with_object_salary(self, capsys):
        """Покрытие: диагностика вакансий с зарплатой как объект"""
        service = VacancyStorageService()
        
        mock_salary = Mock()
        mock_salary.salary_from = 80000
        mock_salary.salary_to = None
        mock_salary.currency = "USD"
        
        vacancy = Vacancy(
            vacancy_id="1",
            name="Senior Developer",
            alternate_url="http://test.com",
            salary=mock_salary,
            employer={"name": "Tech Corp", "id": "456"}
        )
        
        service._log_salary_diagnostics("OBJECT_SALARY", [vacancy])
        
        captured = capsys.readouterr()
        assert "от 80,000 USD" in captured.out

    def test_log_salary_diagnostics_no_salary(self, capsys):
        """Покрытие: диагностика вакансий без зарплаты"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="1",
            name="Job without salary",
            alternate_url="http://test.com",
            employer={"name": "Some Company"}
        )
        vacancy.salary = None
        
        service._log_salary_diagnostics("NO_SALARY", [vacancy])
        
        captured = capsys.readouterr()
        assert "НЕТ" in captured.out
        assert "Без зарплаты: 1" in captured.out

    def test_log_salary_diagnostics_complex_salary_object(self, capsys):
        """Покрытие: диагностика неожиданного объекта зарплаты"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="1",
            name="Complex salary job",
            alternate_url="http://test.com",
            salary="Some string salary",  # Неожиданный тип
            employer="String employer"  # Неожиданный тип
        )
        
        service._log_salary_diagnostics("COMPLEX", [vacancy])
        
        captured = capsys.readouterr()
        assert "ОБЪЕКТ:" in captured.out


class TestVacancyStorageServiceSaving:
    """Покрытие методов сохранения вакансий"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_add_vacancy_batch_optimized_empty_list(self, mock_logger):
        """Покрытие: пакетное добавление пустого списка"""
        service = VacancyStorageService()
        
        result = service.add_vacancy_batch_optimized([])
        
        assert result == []

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_add_vacancy_batch_optimized_double_nested_list(self, mock_logger):
        """Покрытие: исправление двойной вложенности списка"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        nested_list = [[vacancy]]  # Двойная вложенность
        
        with patch.object(service, '_get_company_id_mapping') as mock_mapping:
            mock_mapping.return_value = {}
            
            with patch.object(service.db_manager, '_get_connection') as mock_conn:
                mock_connection = Mock()
                mock_cursor = Mock()
                mock_cursor.rowcount = 1
                mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
                mock_conn.return_value.__enter__.return_value = mock_connection
                
                with patch.object(service, '_prepare_vacancy_data') as mock_prepare:
                    mock_prepare.return_value = ("1", "Test", "http://test.com", None, None, None, 
                                               "", "", "", "", "", "", "", "test", None, None, None)
                    
                    result = service.add_vacancy_batch_optimized(nested_list)
                    
                    assert "Успешно сохранено 1 вакансий" in result[0]
                    mock_logger.debug.assert_called_with(
                        "VacancyStorageService: исправлена двойная вложенность списка: получено 1 вакансий"
                    )

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_add_vacancy_batch_optimized_success(self, mock_logger):
        """Покрытие: успешное пакетное сохранение"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        
        with patch.object(service, '_get_company_id_mapping') as mock_mapping:
            mock_mapping.return_value = {}
            
            with patch.object(service.db_manager, '_get_connection') as mock_conn:
                mock_connection = Mock()
                mock_cursor = Mock()
                mock_cursor.rowcount = 1
                mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
                mock_conn.return_value.__enter__.return_value = mock_connection
                
                with patch.object(service, '_prepare_vacancy_data') as mock_prepare:
                    mock_prepare.return_value = ("1", "Test", "http://test.com", None, None, None, 
                                               "", "", "", "", "", "", "", "test", None, None, None)
                    
                    result = service.add_vacancy_batch_optimized([vacancy], search_query="python")
                    
                    assert len(result) == 1
                    assert "Успешно сохранено 1 вакансий" in result[0]

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_add_vacancy_batch_optimized_prepare_error(self, mock_logger):
        """Покрытие: ошибка при подготовке данных вакансии"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        
        with patch.object(service, '_get_company_id_mapping') as mock_mapping:
            mock_mapping.return_value = {}
            
            with patch.object(service, '_prepare_vacancy_data') as mock_prepare:
                mock_prepare.side_effect = Exception("Prepare error")
                
                with patch.object(service.db_manager, '_get_connection') as mock_conn:
                    mock_connection = Mock()
                    mock_cursor = Mock()
                    mock_cursor.rowcount = 0
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
                    mock_conn.return_value.__enter__.return_value = mock_connection
                    
                    result = service.add_vacancy_batch_optimized([vacancy])
                    
                    mock_logger.warning.assert_called_with("Ошибка подготовки данных вакансии 1: Prepare error")

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_add_vacancy_batch_optimized_db_error(self, mock_logger):
        """Покрытие: ошибка базы данных при сохранении"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        
        with patch.object(service, '_get_company_id_mapping') as mock_mapping:
            mock_mapping.side_effect = Exception("DB mapping error")
            
            result = service.add_vacancy_batch_optimized([vacancy])
            
            assert len(result) == 1
            assert "Ошибка сохранения:" in result[0]

    def test_save_vacancies_single_vacancy(self):
        """Покрытие: сохранение одной вакансии"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(vacancy_id="1", name="Test", alternate_url="http://test.com")
        
        with patch.object(service, 'add_vacancy_batch_optimized') as mock_batch:
            mock_batch.return_value = ["Success message"]
            
            result = service.save_vacancies(vacancy)
            
            assert result == 1
            mock_batch.assert_called_once_with([vacancy], search_query="")

    def test_save_vacancies_list_of_vacancies(self):
        """Покрытие: сохранение списка вакансий"""
        service = VacancyStorageService()
        
        vacancies = [
            Vacancy(vacancy_id="1", name="Test1", alternate_url="http://test1.com"),
            Vacancy(vacancy_id="2", name="Test2", alternate_url="http://test2.com")
        ]
        
        with patch.object(service, 'add_vacancy_batch_optimized') as mock_batch:
            mock_batch.return_value = ["Message1", "Message2"]
            
            result = service.save_vacancies(vacancies)
            
            assert result == 2
            mock_batch.assert_called_once_with(vacancies, search_query="")


class TestVacancyStorageServiceLoading:
    """Покрытие методов загрузки и конвертации данных"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_load_vacancies_success(self, mock_logger):
        """Покрытие: успешная загрузка вакансий"""
        service = VacancyStorageService()
        
        mock_data = [{
            "vacancy_id": "1",
            "title": "Test Job",
            "url": "http://test.com",
            "salary_info": "от 100000 до 150000 RUR",
            "company_name": "Test Company"
        }]
        
        with patch.object(service.db_manager, 'get_all_vacancies') as mock_get_all:
            mock_get_all.return_value = mock_data
            
            with patch.object(service, '_convert_dict_to_vacancy') as mock_convert:
                mock_vacancy = Vacancy(vacancy_id="1", name="Test Job", alternate_url="http://test.com")
                mock_convert.return_value = mock_vacancy
                
                result = service.load_vacancies(limit=10, offset=0)
                
                assert len(result) == 1
                assert result[0] == mock_vacancy

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_load_vacancies_with_pagination(self, mock_logger):
        """Покрытие: загрузка с пагинацией"""
        service = VacancyStorageService()
        
        mock_vacancies = [
            Vacancy(vacancy_id=str(i), name=f"Job {i}", alternate_url=f"http://test{i}.com")
            for i in range(1, 6)
        ]
        
        with patch.object(service.db_manager, 'get_all_vacancies'):
            with patch.object(service, '_convert_dict_to_vacancy') as mock_convert:
                mock_convert.side_effect = mock_vacancies
                
                # Тестируем offset
                result = service.load_vacancies(limit=2, offset=2)
                assert len(result) <= 2

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_load_vacancies_convert_error(self, mock_logger):
        """Покрытие: ошибка при конвертации данных"""
        service = VacancyStorageService()
        
        mock_data = [{"vacancy_id": "1"}]
        
        with patch.object(service.db_manager, 'get_all_vacancies') as mock_get_all:
            mock_get_all.return_value = mock_data
            
            with patch.object(service, '_convert_dict_to_vacancy') as mock_convert:
                mock_convert.side_effect = Exception("Convert error")
                
                result = service.load_vacancies()
                
                assert result == []
                mock_logger.warning.assert_called_with("Ошибка преобразования данных вакансии: Convert error")

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_load_vacancies_db_error(self, mock_logger):
        """Покрытие: ошибка базы данных при загрузке"""
        service = VacancyStorageService()
        
        with patch.object(service.db_manager, 'get_all_vacancies') as mock_get_all:
            mock_get_all.side_effect = Exception("DB error")
            
            result = service.load_vacancies()
            
            assert result == []
            mock_logger.error.assert_called_with("Ошибка загрузки вакансий: DB error")

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_convert_dict_to_vacancy_full_data(self, mock_logger):
        """Покрытие: конвертация полных данных в Vacancy"""
        service = VacancyStorageService()
        
        data = {
            "vacancy_id": "123",
            "title": "Python Developer",
            "url": "http://example.com/job",
            "salary_info": "от 100000 до 150000 RUR",
            "company_name": "Tech Corp",
            "description": "Great job",
            "requirements": "Python skills",
            "responsibilities": "Code development",
            "experience": "3-5 years",
            "employment": "Full-time",
            "schedule": "Full day",
            "area": "Moscow",
            "source": "hh.ru",
            "published_at": datetime.now(),
            "raw_company_id": 456
        }
        
        result = service._convert_dict_to_vacancy(data)
        
        assert result is not None
        assert result.vacancy_id == "123"
        assert result.name == "Python Developer"
        assert result.alternate_url == "http://example.com/job"
        assert result.salary["from"] == 100000
        assert result.salary["to"] == 150000
        assert result.employer.name == "Tech Corp"

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_convert_dict_to_vacancy_minimal_data(self, mock_logger):
        """Покрытие: конвертация минимальных данных"""
        service = VacancyStorageService()
        
        data = {
            "vacancy_id": "456",
            "title": "Simple Job"
        }
        
        result = service._convert_dict_to_vacancy(data)
        
        assert result is not None
        assert result.vacancy_id == "456"
        assert result.name == "Simple Job"
        assert result.salary is None
        assert result.employer is None

    @patch('src.storage.services.vacancy_storage_service.logger') 
    def test_convert_dict_to_vacancy_salary_parsing(self, mock_logger):
        """Покрытие: различные варианты парсинга зарплаты"""
        service = VacancyStorageService()
        
        # Только "от"
        data1 = {"vacancy_id": "1", "salary_info": "от 80000 RUR"}
        result1 = service._convert_dict_to_vacancy(data1)
        assert result1.salary["from"] == 80000
        assert "to" not in result1.salary
        
        # Только "до" 
        data2 = {"vacancy_id": "2", "salary_info": "до 120000 RUR"}
        result2 = service._convert_dict_to_vacancy(data2)
        assert result2.salary["to"] == 120000
        assert "from" not in result2.salary
        
        # Без зарплаты
        data3 = {"vacancy_id": "3", "salary_info": "Не указана"}
        result3 = service._convert_dict_to_vacancy(data3)
        assert result3.salary is None

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_convert_dict_to_vacancy_error(self, mock_logger):
        """Покрытие: ошибка при конвертации"""
        service = VacancyStorageService()
        
        # Передаем некорректные данные
        with patch('src.vacancies.models.Vacancy') as mock_vacancy_class:
            mock_vacancy_class.side_effect = Exception("Conversion error")
            
            result = service._convert_dict_to_vacancy({"vacancy_id": "1"})
            
            assert result is None
            mock_logger.error.assert_called_with("Ошибка преобразования в объект Vacancy: Conversion error")


class TestVacancyStorageServicePrepareData:
    """Покрытие метода подготовки данных для БД"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_prepare_vacancy_data_full_dict_salary(self, mock_logger):
        """Покрытие: подготовка данных с зарплатой как словарь"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="123",
            name="Python Developer",
            alternate_url="http://example.com",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Great job",
            requirements="Python skills",
            responsibilities="Code development",
            source="hh.ru"
        )
        
        company_mapping = {"employer_id": 456}
        
        with patch.object(service, '_find_company_id') as mock_find_company:
            mock_find_company.return_value = 456
            
            with patch('src.utils.data_normalizers.normalize_area_data') as mock_normalize:
                mock_normalize.return_value = "Moscow"
                
                result = service._prepare_vacancy_data(vacancy, company_mapping, "python")
                
                assert result is not None
                assert result[0] == "123"  # vacancy_id
                assert result[1] == "Python Developer"  # title
                assert result[3] == 100000  # salary_from
                assert result[4] == 150000  # salary_to
                assert result[5] == "RUR"  # currency

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_prepare_vacancy_data_object_salary(self, mock_logger):
        """Покрытие: подготовка данных с зарплатой как объект"""
        service = VacancyStorageService()
        
        mock_salary = Mock()
        mock_salary.salary_from = 80000
        mock_salary.salary_to = 120000
        mock_salary.currency = "USD"
        
        vacancy = Vacancy(
            vacancy_id="456",
            name="Senior Developer", 
            alternate_url="http://test.com",
            salary=mock_salary,
            source="sj.ru"
        )
        
        result = service._prepare_vacancy_data(vacancy, {})
        
        assert result[3] == 80000  # salary_from
        assert result[4] == 120000  # salary_to
        assert result[5] == "USD"  # currency

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_prepare_vacancy_data_experience_with_get_name(self, mock_logger):
        """Покрытие: подготовка данных с опытом имеющим метод get_name"""
        service = VacancyStorageService()
        
        mock_experience = Mock()
        mock_experience.get_name.return_value = "1-3 года"
        
        vacancy = Vacancy(
            vacancy_id="789",
            name="Junior Dev",
            alternate_url="http://test.com",
            experience=mock_experience
        )
        
        result = service._prepare_vacancy_data(vacancy, {})
        
        assert result[9] == "1-3 года"  # experience

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_prepare_vacancy_data_experience_without_get_name(self, mock_logger):
        """Покрытие: подготовка данных с опытом без метода get_name"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="101112",
            name="Mid Dev",
            alternate_url="http://test.com",
            experience="3-5 years"  # Строка вместо объекта
        )
        
        result = service._prepare_vacancy_data(vacancy, {})
        
        assert result[9] == "3-5 years"

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_prepare_vacancy_data_employment_schedule_get_name(self, mock_logger):
        """Покрытие: подготовка данных с employment и schedule имеющими get_name"""
        service = VacancyStorageService()
        
        mock_employment = Mock()
        mock_employment.get_name.return_value = "Полная занятость"
        
        mock_schedule = Mock()
        mock_schedule.get_name.return_value = "Полный день"
        
        vacancy = Vacancy(
            vacancy_id="131415",
            name="Full-time Dev",
            alternate_url="http://test.com",
            employment=mock_employment,
            schedule=mock_schedule
        )
        
        result = service._prepare_vacancy_data(vacancy, {})
        
        assert result[10] == "Полная занятость"  # employment
        assert result[11] == "Полный день"  # schedule

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_prepare_vacancy_data_datetime_published_at(self, mock_logger):
        """Покрытие: подготовка данных с published_at как datetime"""
        service = VacancyStorageService()
        
        test_datetime = datetime(2023, 12, 1, 10, 30)
        
        vacancy = Vacancy(
            vacancy_id="161718",
            name="Date Test Job",
            alternate_url="http://test.com",
            published_at=test_datetime
        )
        
        result = service._prepare_vacancy_data(vacancy, {})
        
        assert result[14] == test_datetime

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_prepare_vacancy_data_string_published_at(self, mock_logger):
        """Покрытие: подготовка данных с published_at как строка"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="192021",
            name="String Date Job",
            alternate_url="http://test.com",
            published_at="2023-12-01T10:30:00Z"
        )
        
        result = service._prepare_vacancy_data(vacancy, {})
        
        # Проверяем что строка была правильно преобразована в datetime
        assert result[14] is not None
        assert isinstance(result[14], datetime)

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_prepare_vacancy_data_invalid_string_published_at(self, mock_logger):
        """Покрытие: подготовка данных с некорректной строкой published_at"""
        service = VacancyStorageService()
        
        vacancy = Vacancy(
            vacancy_id="222324",
            name="Invalid Date Job",
            alternate_url="http://test.com",
            published_at="invalid-date-string"
        )
        
        result = service._prepare_vacancy_data(vacancy, {})
        
        assert result[14] is None  # published_at должно быть None

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_prepare_vacancy_data_error(self, mock_logger):
        """Покрытие: ошибка при подготовке данных"""
        service = VacancyStorageService()
        
        # Создаем вакансию с некорректными данными
        vacancy = Vacancy(vacancy_id="error", name="Error Job", alternate_url="http://test.com")
        
        # Мокируем ошибку при нормализации area
        with patch('src.utils.data_normalizers.normalize_area_data') as mock_normalize:
            mock_normalize.side_effect = Exception("Normalization error")
            
            result = service._prepare_vacancy_data(vacancy, {})
            
            assert result is None
            mock_logger.error.assert_called_once()


class TestVacancyStorageServiceUtilityMethods:
    """Покрытие служебных и делегирующих методов"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_get_vacancies_count_success(self, mock_logger):
        """Покрытие: успешное получение количества вакансий"""
        service = VacancyStorageService()
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (42,)
        
        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        with patch.object(service.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection
            
            result = service.get_vacancies_count()
            
            assert result == 42
            mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM vacancies")

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_get_vacancies_count_none_result(self, mock_logger):
        """Покрытие: получение None из запроса количества"""
        service = VacancyStorageService()
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        with patch.object(service.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection
            
            result = service.get_vacancies_count()
            
            assert result == 0

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_get_vacancies_count_error(self, mock_logger):
        """Покрытие: ошибка при получении количества вакансий"""
        service = VacancyStorageService()
        
        with patch.object(service.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.side_effect = Exception("DB count error")
            
            result = service.get_vacancies_count()
            
            assert result == 0
            mock_logger.error.assert_called_with("Ошибка получения количества вакансий: DB count error")

    def test_create_tables_delegate(self):
        """Покрытие: делегирование create_tables к DBManager"""
        service = VacancyStorageService()
        
        with patch.object(service.db_manager, 'create_tables') as mock_create:
            mock_create.return_value = True
            
            result = service.create_tables()
            
            assert result is True
            mock_create.assert_called_once()

    def test_populate_companies_table_delegate(self):
        """Покрытие: делегирование populate_companies_table к DBManager"""
        service = VacancyStorageService()
        
        with patch.object(service.db_manager, 'populate_companies_table') as mock_populate:
            mock_populate.return_value = True
            
            result = service.populate_companies_table()
            
            assert result is True
            mock_populate.assert_called_once()

    def test_get_companies_and_vacancies_count_delegate(self):
        """Покрытие: делегирование get_companies_and_vacancies_count к DBManager"""
        service = VacancyStorageService()
        
        expected_result = [("Company1", 10), ("Company2", 5)]
        
        with patch.object(service.db_manager, 'get_companies_and_vacancies_count') as mock_get_stats:
            mock_get_stats.return_value = expected_result
            
            result = service.get_companies_and_vacancies_count()
            
            assert result == expected_result
            mock_get_stats.assert_called_once()

    def test_check_connection_delegate(self):
        """Покрытие: делегирование check_connection к DBManager"""
        service = VacancyStorageService()
        
        with patch.object(service.db_manager, 'check_connection') as mock_check:
            mock_check.return_value = True
            
            result = service.check_connection()
            
            assert result is True
            mock_check.assert_called_once()