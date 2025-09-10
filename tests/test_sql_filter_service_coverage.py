#!/usr/bin/env python3
"""
Тесты модуля sql_filter_service.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций 
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Тестирование класса SQLFilterService и всех его методов

Модуль содержит:
- 1 класс SQLFilterService с 8 методами (включая статический)
- SQL фильтрация и дедупликация вакансий через временные таблицы
- Работа с целевыми компаниями и статистикой
- Критический компонент системы фильтрации
"""

import pytest
from unittest.mock import MagicMock, patch, call
import logging
from typing import Any

from src.storage.services.sql_filter_service import SQLFilterService


class MockVacancy:
    """Мок-объект вакансии для тестирования"""
    
    def __init__(self, **kwargs: Any) -> None:
        self.vacancy_id = kwargs.get('vacancy_id', 'test_id')
        self.title = kwargs.get('title', 'Test Job')
        self.description = kwargs.get('description', 'Test description')
        self.employer = kwargs.get('employer', None)
        self.salary = kwargs.get('salary', None)
        self.source = kwargs.get('source', 'hh')
        
        # Добавляем любые дополнительные атрибуты
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)


class MockEmployer:
    """Мок-объект работодателя"""
    
    def __init__(self, id_value: Any = None, name_value: Any = None) -> None:
        self._id = id_value
        self._name = name_value
    
    def get_id(self) -> Any:
        return self._id
    
    def get_name(self) -> Any:
        return self._name


class MockSalary:
    """Мок-объект зарплаты"""
    
    def __init__(self, salary_from: Any = None, salary_to: Any = None) -> None:
        self.salary_from = salary_from
        self.salary_to = salary_to


class MockCompany:
    """Мок-объект компании"""
    
    def __init__(self, hh_id: Any = None, sj_id: Any = None) -> None:
        self.hh_id = hh_id
        self.sj_id = sj_id


class TestSQLFilterService:
    """100% покрытие класса SQLFilterService"""

    def test_class_exists(self) -> None:
        """Покрытие: существование класса"""
        assert SQLFilterService is not None

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.storage.services.sql_filter_service.logger')
    def test_init_successful(self, mock_logger: Any, mock_target_companies: Any) -> None:
        """Покрытие: успешная инициализация"""
        # Мокируем db_manager
        mock_db_manager = MagicMock()
        
        # Мокируем TargetCompanies
        mock_companies = [
            MockCompany(hh_id='123', sj_id='456'),
            MockCompany(hh_id='789', sj_id=None),
            MockCompany(hh_id=None, sj_id='321')
        ]
        mock_target_companies.get_all_companies.return_value = mock_companies
        
        service = SQLFilterService(mock_db_manager)
        
        assert service.db_manager == mock_db_manager
        assert '123' in service._target_hh_ids
        assert '789' in service._target_hh_ids
        assert '456' in service._target_sj_ids
        assert '321' in service._target_sj_ids
        
        # Проверяем логирование
        mock_logger.info.assert_called_once()

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_load_target_company_ids_hh(self, mock_target_companies: Any) -> None:
        """Покрытие: загрузка HH ID компаний"""
        mock_db_manager = MagicMock()
        mock_companies = [
            MockCompany(hh_id='123', sj_id='456'),
            MockCompany(hh_id='789', sj_id=None),
            MockCompany(hh_id=None, sj_id='321')
        ]
        mock_target_companies.get_all_companies.return_value = mock_companies
        
        service = SQLFilterService(mock_db_manager)
        hh_ids = service._load_target_company_ids("hh")
        
        assert hh_ids == {'123', '789'}

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_load_target_company_ids_sj(self, mock_target_companies: Any) -> None:
        """Покрытие: загрузка SJ ID компаний"""
        mock_db_manager = MagicMock()
        mock_companies = [
            MockCompany(hh_id='123', sj_id='456'),
            MockCompany(hh_id='789', sj_id=None),
            MockCompany(hh_id=None, sj_id='321')
        ]
        mock_target_companies.get_all_companies.return_value = mock_companies
        
        service = SQLFilterService(mock_db_manager)
        sj_ids = service._load_target_company_ids("sj")
        
        assert sj_ids == {'456', '321'}

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_load_target_company_ids_unknown_source(self, mock_target_companies: Any) -> None:
        """Покрытие: неизвестный источник"""
        mock_db_manager = MagicMock()
        mock_companies = [MockCompany(hh_id='123', sj_id='456')]
        mock_target_companies.get_all_companies.return_value = mock_companies
        
        service = SQLFilterService(mock_db_manager)
        unknown_ids = service._load_target_company_ids("unknown")
        
        assert unknown_ids == set()

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_load_target_company_ids_empty_companies(self, mock_target_companies: Any) -> None:
        """Покрытие: пустой список компаний"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        
        service = SQLFilterService(mock_db_manager)
        
        assert service._target_hh_ids == set()
        assert service._target_sj_ids == set()

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.storage.services.sql_filter_service.logger')
    def test_filter_and_deduplicate_empty_vacancies(self, mock_logger: Any, mock_target_companies: Any) -> None:
        """Покрытие: пустой список вакансий"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        
        service = SQLFilterService(mock_db_manager)
        result = service.filter_and_deduplicate_vacancies([])
        
        assert result == []

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.storage.services.sql_filter_service.logger')
    def test_filter_and_deduplicate_successful(self, mock_logger: Any, mock_target_companies: Any) -> None:
        """Покрытие: успешная фильтрация и дедупликация"""
        # Настройка моков
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = [
            MockCompany(hh_id='123', sj_id=None)
        ]
        
        # Мокируем соединение с БД
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_manager._get_connection.return_value.__enter__.return_value = mock_connection
        
        service = SQLFilterService(mock_db_manager)
        
        # Мокируем внутренние методы
        with patch.object(service, '_create_temp_vacancy_table') as mock_create_table, \
             patch.object(service, '_execute_filter_query') as mock_execute_query, \
             patch.object(service, '_build_filtered_vacancies') as mock_build_filtered:
            
            mock_execute_query.return_value = ['id1', 'id2']
            mock_build_filtered.return_value = [MockVacancy(vacancy_id='id1')]
            
            vacancies = [MockVacancy(vacancy_id='id1'), MockVacancy(vacancy_id='id2')]
            result = service.filter_and_deduplicate_vacancies(vacancies)
            
            # Проверяем вызовы
            mock_create_table.assert_called_once_with(mock_cursor, vacancies)
            mock_execute_query.assert_called_once_with(mock_cursor)
            mock_build_filtered.assert_called_once_with(vacancies, ['id1', 'id2'])
            
            assert len(result) == 1

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.storage.services.sql_filter_service.logger')
    def test_filter_and_deduplicate_exception(self, mock_logger: Any, mock_target_companies: Any) -> None:
        """Покрытие: исключение при фильтрации"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        
        # Мокируем исключение при получении соединения
        mock_db_manager._get_connection.side_effect = Exception("Database connection failed")
        
        service = SQLFilterService(mock_db_manager)
        vacancies = [MockVacancy()]
        result = service.filter_and_deduplicate_vacancies(vacancies)
        
        assert result == []
        mock_logger.error.assert_called_once()


class TestSQLFilterServiceTempTable:
    """100% покрытие метода _create_temp_vacancy_table"""
    
    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.utils.description_parser.DescriptionParser')
    @patch('src.storage.services.sql_filter_service.logger')
    def test_create_temp_vacancy_table_complete(self, mock_logger: Any, mock_description_parser: Any, mock_target_companies: Any) -> None:
        """Покрытие: создание временной таблицы с полными данными"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        mock_cursor = MagicMock()
        
        # Мокируем DescriptionParser
        mock_description_parser.extract_requirements_and_responsibilities.return_value = (
            "Test requirements", "Test responsibilities"
        )
        
        service = SQLFilterService(mock_db_manager)
        
        # Создаем вакансию с полными данными
        employer = MockEmployer('emp123', 'Test Company')
        salary = MockSalary(100000, 150000)
        vacancy = MockVacancy(
            vacancy_id='vac123',
            title='Python Developer',
            description='Test description',
            employer=employer,
            salary=salary,
            source='hh'
        )
        
        service._create_temp_vacancy_table(mock_cursor, [vacancy])
        
        # Проверяем создание таблицы
        assert mock_cursor.execute.call_count == 1
        create_table_call = mock_cursor.execute.call_args_list[0][0][0]
        assert 'CREATE TEMP TABLE temp_filter_vacancies' in create_table_call
        
        # Проверяем вставку данных
        mock_cursor.executemany.assert_called_once()
        insert_call = mock_cursor.executemany.call_args
        insert_query = insert_call[0][0]
        insert_data = insert_call[0][1]
        
        assert 'INSERT INTO temp_filter_vacancies' in insert_query
        assert len(insert_data) == 1
        
        # Проверяем данные
        data_row = insert_data[0]
        assert data_row[0] == 'vac123'  # vacancy_id
        assert data_row[1] == 'python developer'  # title_normalized
        assert data_row[2] == 'emp123'  # employer_id
        assert data_row[3] == 'test company'  # employer_name_normalized
        assert data_row[4] == 'hh'  # source
        assert data_row[5] == 100000  # salary_from
        assert data_row[6] == 150000  # salary_to
        assert data_row[7] == 0  # original_index
        
        # Проверяем что есть логирование создания таблицы (игнорируем вызов из __init__)
        table_calls = [call for call in mock_logger.info.call_args_list if 'таблица' in str(call)]
        assert len(table_calls) == 1

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.utils.description_parser.DescriptionParser')
    def test_create_temp_vacancy_table_no_employer(self, mock_description_parser: Any, mock_target_companies: Any) -> None:
        """Покрытие: вакансия без работодателя"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        mock_cursor = MagicMock()
        
        mock_description_parser.extract_requirements_and_responsibilities.return_value = (None, None)
        
        service = SQLFilterService(mock_db_manager)
        vacancy = MockVacancy(employer=None, salary=None)
        
        service._create_temp_vacancy_table(mock_cursor, [vacancy])
        
        insert_data = mock_cursor.executemany.call_args[0][1]
        data_row = insert_data[0]
        
        assert data_row[2] is None  # employer_id
        assert data_row[3] == 'не указана'  # employer_name_normalized
        assert data_row[5] is None  # salary_from
        assert data_row[6] is None  # salary_to

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.utils.description_parser.DescriptionParser')
    def test_create_temp_vacancy_table_employer_without_methods(self, mock_description_parser: Any, mock_target_companies: Any) -> None:
        """Покрытие: работодатель без методов get_id/get_name"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        mock_cursor = MagicMock()
        
        mock_description_parser.extract_requirements_and_responsibilities.return_value = (None, None)
        
        service = SQLFilterService(mock_db_manager)
        
        # Создаем работодателя без методов get_id и get_name
        employer = MagicMock()
        del employer.get_id
        del employer.get_name
        
        vacancy = MockVacancy(employer=employer)
        
        service._create_temp_vacancy_table(mock_cursor, [vacancy])
        
        insert_data = mock_cursor.executemany.call_args[0][1]
        data_row = insert_data[0]
        
        assert data_row[2] is None  # employer_id
        assert data_row[3] == 'не указана'  # employer_name_normalized


class TestSQLFilterServiceFilterQuery:
    """100% покрытие метода _execute_filter_query"""
    
    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.storage.services.sql_filter_service.logger')
    def test_execute_filter_query_with_results(self, mock_logger: Any, mock_target_companies: Any) -> None:
        """Покрытие: выполнение запроса с результатами"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = [
            MockCompany(hh_id='123', sj_id='456')
        ]
        
        service = SQLFilterService(mock_db_manager)
        mock_cursor = MagicMock()
        
        # Мокируем результаты запроса
        mock_cursor.fetchall.return_value = [('vac1',), ('vac2',)]
        
        result = service._execute_filter_query(mock_cursor)
        
        assert result == ['vac1', 'vac2']
        mock_cursor.execute.assert_called_once()
        # Проверяем что есть логирование фильтрации (игнорируем вызов из __init__)
        info_calls = [call for call in mock_logger.info.call_args_list if 'фильтрация' in str(call)]
        assert len(info_calls) == 1

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.storage.services.sql_filter_service.logger')
    def test_execute_filter_query_no_results(self, mock_logger: Any, mock_target_companies: Any) -> None:
        """Покрытие: запрос без результатов"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = [
            MockCompany(hh_id='123', sj_id=None)
        ]
        
        service = SQLFilterService(mock_db_manager)
        mock_cursor = MagicMock()
        
        # Мокируем пустой результат
        mock_cursor.fetchall.return_value = []
        
        result = service._execute_filter_query(mock_cursor)
        
        assert result == []
        mock_logger.warning.assert_called_once()
        mock_logger.info.assert_called()

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_execute_filter_query_empty_target_ids(self, mock_target_companies: Any) -> None:
        """Покрытие: пустые списки целевых ID"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        
        service = SQLFilterService(mock_db_manager)
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        
        result = service._execute_filter_query(mock_cursor)
        
        # Проверяем что запрос выполнился с пустыми списками
        executed_query = mock_cursor.execute.call_args[0][0]
        assert 'NULL' in executed_query
        assert result == []


class TestSQLFilterServiceBuildResults:
    """100% покрытие метода _build_filtered_vacancies"""
    
    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_build_filtered_vacancies_all_found(self, mock_target_companies: Any) -> None:
        """Покрытие: все ID найдены в исходном списке"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        
        service = SQLFilterService(mock_db_manager)
        
        vacancy1 = MockVacancy(vacancy_id='id1', title='Job 1')
        vacancy2 = MockVacancy(vacancy_id='id2', title='Job 2')
        original_vacancies = [vacancy1, vacancy2]
        filtered_ids = ['id1', 'id2']
        
        result = service._build_filtered_vacancies(original_vacancies, filtered_ids)
        
        assert len(result) == 2
        assert result[0] == vacancy1
        assert result[1] == vacancy2

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_build_filtered_vacancies_partial_found(self, mock_target_companies: Any) -> None:
        """Покрытие: не все ID найдены"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        
        service = SQLFilterService(mock_db_manager)
        
        vacancy1 = MockVacancy(vacancy_id='id1', title='Job 1')
        vacancy2 = MockVacancy(vacancy_id='id2', title='Job 2')
        original_vacancies = [vacancy1, vacancy2]
        filtered_ids = ['id1', 'id3']  # id3 не существует
        
        result = service._build_filtered_vacancies(original_vacancies, filtered_ids)
        
        assert len(result) == 1
        assert result[0] == vacancy1

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_build_filtered_vacancies_none_found(self, mock_target_companies: Any) -> None:
        """Покрытие: ни один ID не найден"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        
        service = SQLFilterService(mock_db_manager)
        
        vacancy1 = MockVacancy(vacancy_id='id1')
        original_vacancies = [vacancy1]
        filtered_ids = ['id2', 'id3']  # несуществующие ID
        
        result = service._build_filtered_vacancies(original_vacancies, filtered_ids)
        
        assert result == []


class TestSQLFilterServiceNormalizeText:
    """100% покрытие статического метода _normalize_text"""
    
    def test_normalize_text_normal_string(self) -> None:
        """Покрытие: обычная строка"""
        result = SQLFilterService._normalize_text("Python Developer")
        assert result == "python developer"

    def test_normalize_text_empty_string(self) -> None:
        """Покрытие: пустая строка"""
        result = SQLFilterService._normalize_text("")
        assert result == ""

    def test_normalize_text_none(self) -> None:
        """Покрытие: None"""
        result = SQLFilterService._normalize_text(None)
        assert result == ""

    def test_normalize_text_with_spaces(self) -> None:
        """Покрытие: строка с пробелами по краям"""
        result = SQLFilterService._normalize_text("  Senior Python  ")
        assert result == "senior python"

    def test_normalize_text_mixed_case(self) -> None:
        """Покрытие: смешанный регистр"""
        result = SQLFilterService._normalize_text("PyThOn DeVeLoPeR")
        assert result == "python developer"


class TestSQLFilterServiceCompanyStats:
    """100% покрытие метода get_companies_vacancy_count"""
    
    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.storage.services.sql_filter_service.logger')
    def test_get_companies_vacancy_count_success(self, mock_logger: Any, mock_target_companies: Any) -> None:
        """Покрытие: успешное получение статистики"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = [
            MockCompany(hh_id='123', sj_id='456')
        ]
        
        # Мокируем соединение и результаты
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_manager._get_connection.return_value.__enter__.return_value = mock_connection
        
        mock_cursor.fetchall.return_value = [
            ('Company A', 10),
            ('Company B', 5)
        ]
        
        service = SQLFilterService(mock_db_manager)
        result = service.get_companies_vacancy_count()
        
        assert result == [('Company A', 10), ('Company B', 5)]
        mock_cursor.execute.assert_called_once()

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_get_companies_vacancy_count_no_target_companies(self, mock_target_companies: Any) -> None:
        """Покрытие: нет целевых компаний"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        
        service = SQLFilterService(mock_db_manager)
        result = service.get_companies_vacancy_count()
        
        assert result == []

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.storage.services.sql_filter_service.logger')
    def test_get_companies_vacancy_count_exception(self, mock_logger: Any, mock_target_companies: Any) -> None:
        """Покрытие: исключение при получении статистики"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = [
            MockCompany(hh_id='123', sj_id=None)
        ]
        
        # Мокируем исключение
        mock_db_manager._get_connection.side_effect = Exception("Database error")
        
        service = SQLFilterService(mock_db_manager)
        result = service.get_companies_vacancy_count()
        
        assert result == []
        mock_logger.error.assert_called_once()


class TestSQLFilterServiceComplexScenarios:
    """Сложные сценарии для полного покрытия"""
    
    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    @patch('src.utils.description_parser.DescriptionParser')
    def test_vacancy_without_description_and_source_attributes(self, mock_description_parser: Any, mock_target_companies: Any) -> None:
        """Покрытие: вакансия без атрибутов description и source"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = []
        mock_cursor = MagicMock()
        
        mock_description_parser.extract_requirements_and_responsibilities.return_value = (None, None)
        
        service = SQLFilterService(mock_db_manager)
        
        # Создаем вакансию с пустыми значениями description и source
        vacancy = MockVacancy(vacancy_id='test')
        # Удаляем атрибуты чтобы getattr использовал значения по умолчанию
        if hasattr(vacancy, 'description'):
            delattr(vacancy, 'description')
        if hasattr(vacancy, 'source'):
            delattr(vacancy, 'source')
        
        service._create_temp_vacancy_table(mock_cursor, [vacancy])
        
        insert_data = mock_cursor.executemany.call_args[0][1]
        data_row = insert_data[0]
        
        assert data_row[4] == 'unknown'  # source по умолчанию через getattr
        assert data_row[8] == ''  # description по умолчанию через getattr

    @patch('src.storage.services.sql_filter_service.TargetCompanies')
    def test_company_stats_with_mixed_ids(self, mock_target_companies: Any) -> None:
        """Покрытие: статистика с смешанными HH и SJ ID"""
        mock_db_manager = MagicMock()
        mock_target_companies.get_all_companies.return_value = [
            MockCompany(hh_id='123', sj_id=None),
            MockCompany(hh_id=None, sj_id='456'),
            MockCompany(hh_id='789', sj_id='101')
        ]
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_manager._get_connection.return_value.__enter__.return_value = mock_connection
        
        mock_cursor.fetchall.return_value = []
        
        service = SQLFilterService(mock_db_manager)
        result = service.get_companies_vacancy_count()
        
        # Проверяем что метод работает с разными наборами ID
        execute_call = mock_cursor.execute.call_args
        query = execute_call[0][0]
        params = execute_call[0][1]
        
        # Проверяем что в параметрах есть все ID
        assert '123' in params
        assert '456' in params  
        assert '789' in params
        assert '101' in params
        
        assert result == []