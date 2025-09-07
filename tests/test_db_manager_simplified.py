#!/usr/bin/env python3
"""
Упрощенные тесты для максимального покрытия src/storage/db_manager.py

ИСПРАВЛЕННЫЙ ПОДХОД: Корректные сигнатуры методов и правильное мокирование
ЦЕЛЬ: Довести покрытие с 53% до максимального процента
"""

from unittest.mock import MagicMock, patch, call
import pytest
from src.storage.db_manager import DBManager, PSYCOPG2_AVAILABLE


class TestDBManagerBasics:
    """Тесты основной функциональности"""
    
    def test_init_default_config(self):
        """Тест инициализации с конфигом по умолчанию"""
        with patch('src.storage.db_manager.DatabaseConfig') as mock_config_class:
            db_manager = DBManager()
            
            mock_config_class.assert_called_once()
            assert db_manager.db_config is not None
    
    def test_init_custom_config(self):
        """Тест инициализации с пользовательским конфигом"""
        mock_config = MagicMock()
        db_manager = DBManager(db_config=mock_config)
        
        assert db_manager.db_config == mock_config
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', True)
    @patch('src.storage.db_manager.psycopg2')
    def test_get_connection_with_psycopg2(self, mock_psycopg2):
        """Покрытие подключения с psycopg2"""
        mock_config = MagicMock()
        mock_config.get_connection_params.return_value = {"host": "localhost"}
        mock_connection = MagicMock()
        mock_psycopg2.connect.return_value = mock_connection
        
        db_manager = DBManager(db_config=mock_config)
        result = db_manager._get_connection()
        
        # Проверяем что добавлена UTF-8 кодировка
        expected_params = {"host": "localhost", "client_encoding": "utf8"}
        mock_psycopg2.connect.assert_called_once_with(**expected_params)
        mock_connection.set_client_encoding.assert_called_once_with("UTF8")
        assert result == mock_connection
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', False)
    @patch('src.storage.db_manager.get_db_adapter')
    def test_get_connection_without_psycopg2(self, mock_get_adapter):
        """Покрытие подключения без psycopg2"""
        mock_adapter = MagicMock()
        mock_get_adapter.return_value = mock_adapter
        
        db_manager = DBManager()
        result = db_manager._get_connection()
        
        mock_get_adapter.assert_called_once()
        assert result == mock_adapter
    
    def test_create_tables_success(self):
        """Покрытие успешного создания таблиц"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.create_tables()
            
            # Проверяем что были SQL запросы
            assert mock_cursor.execute.called
            assert result is True
    
    def test_create_tables_exception(self):
        """Покрытие exception в create_tables"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_get_connection', side_effect=Exception("DB Error")):
            result = db_manager.create_tables()
            
            assert result is False


class TestDBManagerVacancyMethods:
    """Тесты методов работы с вакансиями"""
    
    def test_ensure_tables_exist(self):
        """Покрытие _ensure_tables_exist"""
        db_manager = DBManager()
        
        with patch.object(db_manager, 'create_tables', return_value=True):
            result = db_manager._ensure_tables_exist()
            
            assert result is True
    
    def test_get_all_vacancies_success(self):
        """Покрытие get_all_vacancies при успешном получении"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Мокируем результат
        mock_cursor.fetchall.return_value = [
            {'title': 'Python Dev', 'company_name': 'TestCo'}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
                result = db_manager.get_all_vacancies()
                
                assert len(result) == 1
                assert result[0]['title'] == 'Python Dev'
    
    def test_get_all_vacancies_exception(self):
        """Покрытие exception в get_all_vacancies"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_get_connection', side_effect=Exception("Error")):
            result = db_manager.get_all_vacancies()
            
            assert result == []
    
    def test_get_avg_salary_success(self):
        """Покрытие get_avg_salary с результатом"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Мокируем результат как кортеж (как в реальном psycopg2)
        mock_cursor.fetchone.return_value = (125000.5,)
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
                result = db_manager.get_avg_salary()
                
                assert result == 125000.5
    
    def test_get_avg_salary_none_result(self):
        """Покрытие get_avg_salary когда нет данных"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = (None,)
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
                result = db_manager.get_avg_salary()
                
                assert result is None
    
    def test_get_avg_salary_exception(self):
        """Покрытие exception в get_avg_salary"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_get_connection', side_effect=Exception("Error")):
            result = db_manager.get_avg_salary()
            
            assert result is None
    
    def test_get_vacancies_with_higher_salary_success(self):
        """Покрытие get_vacancies_with_higher_salary"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {'title': 'Senior Dev', 'calculated_salary': 200000}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
                with patch.object(db_manager, 'get_avg_salary', return_value=150000.0):
                    result = db_manager.get_vacancies_with_higher_salary()
                    
                    assert len(result) == 1
                    assert result[0]['title'] == 'Senior Dev'
    
    def test_get_vacancies_with_higher_salary_no_avg(self):
        """Покрытие когда нет средней зарплаты"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
            with patch.object(db_manager, 'get_avg_salary', return_value=None):
                result = db_manager.get_vacancies_with_higher_salary()
                
                assert result == []
    
    def test_get_vacancies_with_keyword_success(self):
        """Покрытие get_vacancies_with_keyword с результатом"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {'title': 'Python Developer', 'company_name': 'Tech Co'}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
                result = db_manager.get_vacancies_with_keyword("Python")
                
                assert len(result) == 1
                assert 'Python' in result[0]['title']
    
    def test_get_vacancies_with_keyword_empty(self):
        """Покрытие get_vacancies_with_keyword с пустым keyword"""
        db_manager = DBManager()
        
        result1 = db_manager.get_vacancies_with_keyword("")
        result2 = db_manager.get_vacancies_with_keyword("   ")
        result3 = db_manager.get_vacancies_with_keyword(None)
        
        assert result1 == []
        assert result2 == []
        assert result3 == []


class TestDBManagerCompanies:
    """Тесты методов работы с компаниями"""
    
    def test_populate_companies_table_success(self):
        """Покрытие populate_companies_table"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Мокируем что некоторые компании уже есть
        mock_cursor.fetchone.side_effect = [None, (1,)]  # первая нет, вторая есть
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch('src.storage.db_manager.TARGET_COMPANIES', [
                {'name': 'New Company'}, {'name': 'Existing Company'}
            ]):
                result = db_manager.populate_companies_table()
                
                # Должен быть INSERT только для новой компании
                assert mock_cursor.execute.call_count >= 2  # SELECT + INSERT
                assert result is True
    
    def test_get_target_companies_analysis_success(self):
        """Покрытие get_target_companies_analysis"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {'company_name': 'TestCo', 'vacancy_count': 15}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.get_target_companies_analysis()
            
            assert len(result) == 1
            assert result[0]['company_name'] == 'TestCo'
    
    def test_get_companies_and_vacancies_count(self):
        """Покрытие get_companies_and_vacancies_count"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {'company_name': 'CompanyA', 'vacancies_count': 20}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.get_companies_and_vacancies_count()
            
            assert len(result) == 1
            assert result[0]['vacancies_count'] == 20
    
    def test_is_target_company_match_true_cases(self):
        """Покрытие _is_target_company_match для True случаев"""
        db_manager = DBManager()
        
        with patch('src.storage.db_manager.TARGET_COMPANIES', [
            {'name': 'Exact Match Co'},
            {'name': 'Partial'}
        ]):
            # Точное совпадение
            assert db_manager._is_target_company_match('Exact Match Co') is True
            
            # Частичное совпадение (содержит)
            assert db_manager._is_target_company_match('Partial Systems LLC') is True
    
    def test_is_target_company_match_false_case(self):
        """Покрытие _is_target_company_match для False случая"""
        db_manager = DBManager()
        
        with patch('src.storage.db_manager.TARGET_COMPANIES', [
            {'name': 'Known Company'}
        ]):
            assert db_manager._is_target_company_match('Unknown Corporation') is False
    
    def test_filter_companies_by_targets(self):
        """Покрытие filter_companies_by_targets (заглушка)"""
        db_manager = DBManager()
        
        companies = [
            {'name': 'Company A'},
            {'name': 'Company B'}
        ]
        
        # В реальном коде это заглушка, возвращает все компании
        result = db_manager.filter_companies_by_targets(companies)
        
        assert result == companies
    
    def test_filter_companies_by_targets_empty(self):
        """Покрытие filter_companies_by_targets с пустым списком"""
        db_manager = DBManager()
        
        result = db_manager.filter_companies_by_targets([])
        
        assert result == []


class TestDBManagerStatisticsAndConnection:
    """Тесты статистики и подключения"""
    
    def test_get_database_stats_success(self):
        """Покрытие get_database_stats при успешном получении"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Мокируем результаты разных статистических запросов
        mock_cursor.fetchone.side_effect = [
            (100,),    # vacancies count
            (15,),     # companies count
            (120000.0,)  # average salary
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
                result = db_manager.get_database_stats()
                
                assert result['vacancies_count'] == 100
                assert result['companies_count'] == 15
                assert result['average_salary'] == 120000.0
    
    def test_get_database_stats_exception(self):
        """Покрытие exception в get_database_stats"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_get_connection', side_effect=Exception("Error")):
            result = db_manager.get_database_stats()
            
            assert result['vacancies_count'] == 0
            assert result['companies_count'] == 0
            assert result['average_salary'] == 0
    
    def test_get_connection_public_method(self):
        """Покрытие публичного метода get_connection"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.get_connection()
            
            assert result == mock_connection
    
    def test_check_connection_success(self):
        """Покрытие check_connection при успешном подключении"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = (1,)
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.check_connection()
            
            mock_cursor.execute.assert_called_with("SELECT 1")
            assert result is True
    
    def test_check_connection_failure(self):
        """Покрытие check_connection при ошибке"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_get_connection', side_effect=Exception("Connection failed")):
            result = db_manager.check_connection()
            
            assert result is False


class TestDBManagerAnalysisAndMisc:
    """Тесты анализа данных и прочих методов"""
    
    def test_analyze_api_data_with_sql_empty_data(self):
        """Покрытие analyze_api_data_with_sql с пустыми данными"""
        db_manager = DBManager()
        
        result = db_manager.analyze_api_data_with_sql([])
        
        assert result == {}
    
    def test_analyze_api_data_with_sql_success(self):
        """Покрытие analyze_api_data_with_sql с данными"""
        db_manager = DBManager()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        api_data = [
            {
                'id': '123',
                'name': 'Python Developer',
                'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
                'employer': {'name': 'Tech Co'},
                'area': {'name': 'Moscow'}
            }
        ]
        
        # Мокируем результаты анализа  
        mock_cursor.fetchone.side_effect = [
            (1,),       # total count
            (125000.0,) # avg salary
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch('src.storage.db_manager.execute_values') as mock_execute_values:
                result = db_manager.analyze_api_data_with_sql(api_data, "vacancy_stats")
                
                # Проверяем что временная таблица была создана
                assert any("CREATE TEMP TABLE" in str(call) for call in mock_cursor.execute.call_args_list)
                mock_execute_values.assert_called()
                assert isinstance(result, dict)
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', True)
    def test_ensure_database_exists_success(self):
        """Покрытие _ensure_database_exists при успешном создании"""
        mock_config = MagicMock()
        mock_config.get_connection_params.return_value = {
            "host": "localhost",
            "user": "test", 
            "password": "pass",
            "database": "newdb"
        }
        
        db_manager = DBManager(db_config=mock_config)
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        with patch('src.storage.db_manager.psycopg2') as mock_psycopg2:
            mock_psycopg2.connect.return_value = mock_connection
            
            result = db_manager._ensure_database_exists()
            
            # Проверяем создание БД
            assert any("CREATE DATABASE" in str(call) for call in mock_cursor.execute.call_args_list)
            assert result is True
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', True)
    def test_ensure_database_exists_already_exists(self):
        """Покрытие _ensure_database_exists когда БД уже существует"""
        db_manager = DBManager()
        
        with patch('src.storage.db_manager.psycopg2') as mock_psycopg2:
            mock_psycopg2.connect.side_effect = Exception('database "testdb" already exists')
            
            result = db_manager._ensure_database_exists()
            
            # БД уже существует - это нормально
            assert result is True