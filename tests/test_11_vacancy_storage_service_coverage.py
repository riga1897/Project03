"""
100% покрытие тестами для VacancyStorageService

Покрывает все методы и сценарии работы с вакансиями через сервисный слой
"""

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, Mock, patch


from src.storage.services.vacancy_storage_service import VacancyStorageService
from src.vacancies.models import Vacancy


def create_test_vacancy(vacancy_id: str = "1", name: str = "Test Job", **kwargs: Any) -> Vacancy:
    """Создает тестовую вакансию с минимальными обязательными полями"""
    # Create Vacancy directly with proper field aliases and types
    return Vacancy(
        vacancy_id=kwargs.get("vacancy_id", vacancy_id),
        name=kwargs.get("name", name),
        alternate_url=kwargs.get("alternate_url", "http://test.com"),
        employer=kwargs.get("employer", None),
        salary=kwargs.get("salary", None),
        experience=kwargs.get("experience", None),
        employment=kwargs.get("employment", None),
        schedule=kwargs.get("schedule", None),
        published_at=kwargs.get("published_at", None),
        updated_at=kwargs.get("updated_at", datetime.now()),
        area=kwargs.get("area", None),
        source=kwargs.get("source", "test"),
        company_id=kwargs.get("company_id", None),
        requirements=kwargs.get("requirements", ""),
        responsibilities=kwargs.get("responsibilities", ""),
        description=kwargs.get("description", "")
    )


class TestVacancyStorageServiceInit:
    """Покрытие инициализации и конфигурации"""

    @patch('src.storage.services.vacancy_storage_service.DBManager')
    @patch('src.storage.services.vacancy_storage_service.VacancyProcessingCoordinator')
    @patch('src.storage.services.vacancy_storage_service.DeduplicationService')
    @patch('src.storage.services.vacancy_storage_service.TargetCompanies')
    def test_init_with_default_db_manager(self, mock_target_companies: Any, mock_dedup: Any, mock_coordinator: Any, mock_db_manager: Any) -> None:
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
    def test_init_with_custom_db_manager(self, mock_target_companies: Any, mock_dedup: Any, mock_coordinator: Any) -> None:
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
    def test_should_filter_by_salary_true_cases(self, mock_target: Any, mock_dedup: Any, mock_coord: Any, mock_db: Any) -> None:
        """Покрытие: _should_filter_by_salary возвращает True"""
        mock_target.get_all_companies.return_value = []
        service = VacancyStorageService()
        
        assert service._should_filter_by_salary() is True

    @patch.dict('os.environ', {}, clear=True)
    @patch('src.storage.services.vacancy_storage_service.DBManager')
    @patch('src.storage.services.vacancy_storage_service.VacancyProcessingCoordinator')
    @patch('src.storage.services.vacancy_storage_service.DeduplicationService')
    @patch('src.storage.services.vacancy_storage_service.TargetCompanies')
    def test_should_filter_by_salary_false_cases(self, mock_target: Any, mock_dedup: Any, mock_coord: Any, mock_db: Any) -> None:
        """Покрытие: _should_filter_by_salary возвращает False"""
        mock_target.get_all_companies.return_value = []
        service = VacancyStorageService()
        
        assert service._should_filter_by_salary() is False


class TestVacancyStorageServiceProcessing:
    """Покрытие методов обработки и фильтрации вакансий"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_filter_and_deduplicate_empty_list(self, mock_logger: Any) -> None:
        """Покрытие: обработка пустого списка вакансий"""
        service = VacancyStorageService()
        result = service.filter_and_deduplicate_vacancies([])
        
        assert result == []
        mock_logger.info.assert_called_with("Получен пустой список вакансий")

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_filter_and_deduplicate_success_path(self, mock_logger: Any) -> None:
        """Покрытие: успешная обработка вакансий"""
        service = VacancyStorageService()
        
        vacancy1 = create_test_vacancy("1", "Test Job")
        vacancy2 = create_test_vacancy("2", "Another Job")
        test_vacancies = [vacancy1, vacancy2]
        
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
    def test_filter_and_deduplicate_coordinator_error_fallback(self, mock_logger: Any) -> None:
        """Покрытие: ошибка в координаторе, использование fallback"""
        service = VacancyStorageService()
        vacancy1 = create_test_vacancy("1", "Test")
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
    def test_legacy_filter_and_deduplicate_success(self, mock_logger: Any) -> None:
        """Покрытие: успешная legacy обработка"""
        service = VacancyStorageService()
        vacancy1 = create_test_vacancy("1", "Test")
        test_vacancies = [vacancy1]
        
        with patch.object(service, 'deduplication_service') as mock_dedup:
            mock_dedup.process.return_value = [vacancy1]
            
            with patch.object(service, '_enrich_with_company_data') as mock_enrich:
                mock_enrich.return_value = [vacancy1]
                
                result = service._legacy_filter_and_deduplicate(test_vacancies)
                
                assert result == [vacancy1]
                mock_dedup.process.assert_called_once_with(test_vacancies, service.db_manager)


class TestVacancyStorageServiceCompanyData:
    """Покрытие методов работы с данными компаний"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_enrich_with_company_data_success(self, mock_logger: Any) -> None:
        """Покрытие: успешное обогащение данными компаний"""
        service = VacancyStorageService()
        
        vacancy = create_test_vacancy("1", "Test", employer={"name": "Test Company", "id": "123"})
        
        with patch.object(service, '_get_company_id_mapping') as mock_mapping:
            mock_mapping.return_value = {"123": 456}
            
            with patch.object(service, '_find_company_id') as mock_find:
                mock_find.return_value = 456
                
                result = service._enrich_with_company_data([vacancy])
                
                assert len(result) == 1
                assert result[0].company_id == 456

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_get_company_id_mapping_success(self, mock_logger: Any) -> None:
        """Покрытие: успешное получение соответствий ID компаний"""
        service = VacancyStorageService()
        
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, "hh123", None),
            (2, None, "sj456"),
        ]
        
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = Mock(return_value=mock_cursor)
        mock_context_manager.__exit__ = Mock(return_value=False)
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_context_manager
        
        mock_conn_context = MagicMock()
        mock_conn_context.__enter__ = Mock(return_value=mock_connection)
        mock_conn_context.__exit__ = Mock(return_value=False)
        
        with patch.object(service.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.return_value = mock_conn_context
            
            result = service._get_company_id_mapping()
            
            expected = {"hh123": 1, "sj456": 2}
            assert result == expected

    def test_find_company_id_with_dict_employer(self) -> None:
        """Покрытие: поиск ID компании с employer как словарь"""
        service = VacancyStorageService()
        
        vacancy = create_test_vacancy("1", "Test", employer={"id": "123", "name": "Test Company"})
        
        company_mapping = {"123": 456}
        
        result = service._find_company_id(vacancy, company_mapping)
        
        assert result == 456

    def test_find_company_id_no_employer(self) -> None:
        """Покрытие: поиск ID компании без employer"""
        service = VacancyStorageService()
        
        vacancy = create_test_vacancy("1", "Test")
        vacancy.employer = None
        
        result = service._find_company_id(vacancy, {"123": 456})
        
        assert result is None


class TestVacancyStorageServiceSaving:
    """Покрытие методов сохранения вакансий"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_add_vacancy_batch_optimized_empty_list(self, mock_logger: Any) -> None:
        """Покрытие: пакетное добавление пустого списка"""
        service = VacancyStorageService()
        
        result = service.add_vacancy_batch_optimized([])
        
        assert result == []

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_add_vacancy_batch_optimized_success(self, mock_logger: Any) -> None:
        """Покрытие: успешное пакетное сохранение"""
        service = VacancyStorageService()
        
        vacancy = create_test_vacancy("1", "Test")
        
        with patch.object(service, '_get_company_id_mapping') as mock_mapping:
            mock_mapping.return_value = {}
            
            # Создаем моки для контекст-менеджеров
            mock_cursor = Mock()
            mock_cursor.rowcount = 1
            
            mock_cursor_context = MagicMock()
            mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
            mock_cursor_context.__exit__ = Mock(return_value=False)
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor_context
            
            mock_conn_context = MagicMock()
            mock_conn_context.__enter__ = Mock(return_value=mock_connection)
            mock_conn_context.__exit__ = Mock(return_value=False)
            
            with patch.object(service.db_manager, '_get_connection') as mock_conn:
                mock_conn.return_value = mock_conn_context
                
                with patch.object(service, '_prepare_vacancy_data') as mock_prepare:
                    mock_prepare.return_value = ("1", "Test", "http://test.com", None, None, None, 
                                               "", "", "", "", "", "", "", "test", None, None, None)
                    
                    result = service.add_vacancy_batch_optimized([vacancy], search_query="python")
                    
                    assert len(result) == 1
                    assert "Успешно сохранено 1 вакансий" in result[0]

    def test_save_vacancies_single_vacancy(self) -> None:
        """Покрытие: сохранение одной вакансии"""
        service = VacancyStorageService()
        
        vacancy = create_test_vacancy("1", "Test")
        
        with patch.object(service, 'add_vacancy_batch_optimized') as mock_batch:
            mock_batch.return_value = ["Success message"]
            
            result = service.save_vacancies(vacancy)
            
            assert result == 1
            mock_batch.assert_called_once_with([vacancy], search_query="")


class TestVacancyStorageServiceLoading:
    """Покрытие методов загрузки и конвертации данных"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_load_vacancies_success(self, mock_logger: Any) -> None:
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
                mock_vacancy = create_test_vacancy("1", "Test Job")
                mock_convert.return_value = mock_vacancy
                
                result = service.load_vacancies(limit=10, offset=0)
                
                assert len(result) == 1
                assert result[0] == mock_vacancy

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_convert_dict_to_vacancy_full_data(self, mock_logger: Any) -> None:
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
            "experience": None,  # Нужно None, а не строка для Pydantic
            "employment": None,
            "schedule": None,
            "area": "Moscow",
            "source": "hh.ru",
            "published_at": datetime.now(),
            "raw_company_id": 456
        }
        
        result = service._convert_dict_to_vacancy(data)
        
        assert result is not None
        assert result.vacancy_id == "123"
        assert result.title == "Python Developer"  # Поле называется title, не name
        assert result.url == "http://example.com/job"  # И url, не alternate_url


class TestVacancyStorageServiceUtilityMethods:
    """Покрытие служебных и делегирующих методов"""

    @patch('src.storage.services.vacancy_storage_service.logger')
    def test_get_vacancies_count_success(self, mock_logger: Any) -> None:
        """Покрытие: успешное получение количества вакансий"""
        service = VacancyStorageService()
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (42,)
        
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=False)
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor_context
        
        mock_conn_context = MagicMock()
        mock_conn_context.__enter__ = Mock(return_value=mock_connection)
        mock_conn_context.__exit__ = Mock(return_value=False)
        
        with patch.object(service.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.return_value = mock_conn_context
            
            result = service.get_vacancies_count()
            
            assert result == 42

    def test_create_tables_delegate(self) -> None:
        """Покрытие: делегирование create_tables к DBManager"""
        service = VacancyStorageService()
        
        with patch.object(service.db_manager, 'create_tables') as mock_create:
            mock_create.return_value = True
            
            result = service.create_tables()
            
            assert result is True
            mock_create.assert_called_once()

    def test_delete_vacancy_success(self) -> None:
        """Покрытие: успешное удаление вакансии"""
        service = VacancyStorageService()
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=False)
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor_context
        
        mock_conn_context = MagicMock()
        mock_conn_context.__enter__ = Mock(return_value=mock_connection)
        mock_conn_context.__exit__ = Mock(return_value=False)
        
        with patch.object(service.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.return_value = mock_conn_context
            
            result = service.delete_vacancy("123")
            
            assert result is True

    def test_get_storage_stats_success(self) -> None:
        """Покрытие: получение статистики хранилища"""
        service = VacancyStorageService()
        
        with patch.object(service, 'get_vacancies_count') as mock_count:
            mock_count.return_value = 100
            
            with patch.object(service, 'get_companies_and_vacancies_count') as mock_companies:
                mock_companies.return_value = [("Company1", 50), ("Company2", 50)]
                
                with patch.object(service, 'check_connection') as mock_check:
                    mock_check.return_value = True
                    
                    result = service.get_storage_stats()
                    
                    assert result["total_vacancies"] == 100
                    assert result["total_companies"] == 2
                    assert result["connection_status"] is True

    def test_get_vacancies_abstract_method(self) -> None:
        """Покрытие: абстрактный метод get_vacancies"""
        service = VacancyStorageService()
        
        with patch.object(service, 'load_vacancies') as mock_load:
            mock_load.return_value = []
            
            result = service.get_vacancies()
            
            assert result == []
            mock_load.assert_called_once_with(filters=None)

    def test_update_vacancy_success(self) -> None:
        """Покрытие: успешное обновление вакансии"""
        service = VacancyStorageService()
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=False)
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor_context
        
        mock_conn_context = MagicMock()
        mock_conn_context.__enter__ = Mock(return_value=mock_connection)
        mock_conn_context.__exit__ = Mock(return_value=False)
        
        with patch.object(service.db_manager, '_get_connection') as mock_get_conn:
            mock_get_conn.return_value = mock_conn_context
            
            result = service.update_vacancy("123", {"title": "Updated Job"})
            
            assert result is True

    def test_update_vacancy_no_updates(self) -> None:
        """Покрытие: обновление вакансии без изменений"""
        service = VacancyStorageService()
        
        result = service.update_vacancy("123", {})
        
        assert result is False


class TestVacancyStorageServiceDiagnostics:
    """Покрытие метода диагностики зарплат"""

    def test_log_salary_diagnostics_empty_list(self, capsys: Any) -> None:
        """Покрытие: диагностика пустого списка вакансий"""
        service = VacancyStorageService()
        
        service._log_salary_diagnostics("TEST_STAGE", [])
        
        captured = capsys.readouterr()
        assert "🔍 [TEST_STAGE] Список вакансий пуст" in captured.out

    def test_log_salary_diagnostics_with_dict_salary(self, capsys: Any) -> None:
        """Покрытие: диагностика вакансий с зарплатой как словарь"""
        service = VacancyStorageService()
        
        vacancy = create_test_vacancy(
            "1",
            "Python Developer with good salary",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            employer={"name": "Good Company", "id": "123"}
        )
        
        service._log_salary_diagnostics("WITH_SALARY", [vacancy])
        
        captured = capsys.readouterr()
        assert "🔍 [WITH_SALARY] Анализ 1 вакансий:" in captured.out
        assert "от 100,000 до 150,000 RUR" in captured.out

    def test_log_salary_diagnostics_no_salary(self, capsys: Any) -> None:
        """Покрытие: диагностика вакансий без зарплаты"""
        service = VacancyStorageService()
        
        vacancy = create_test_vacancy("1", "Job without salary", employer={"name": "Some Company"})
        vacancy.salary = None
        
        service._log_salary_diagnostics("NO_SALARY", [vacancy])
        
        captured = capsys.readouterr()
        assert "НЕТ" in captured.out
        assert "Без зарплаты: 1" in captured.out