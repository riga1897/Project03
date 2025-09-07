#!/usr/bin/env python3
"""
Полное покрытие src/storage/db_manager.py

ЦЕЛЬ: Покрыть огромный модуль (1028 строк, 18 методов) с 9% до максимального процента
ПОДХОД: Систематическое тестирование от базовой функциональности к сложным операциям
ПРИНЦИП: НИ В КОЕМ СЛУЧАЕ НЕ ДОПУСКАЕТСЯ РЕАЛЬНЫХ I/O ОПЕРАЦИЙ - только моки!

Структура тестирования:
- Инициализация и подключения (с/без psycopg2)
- Создание БД и таблиц
- Операции с компаниями и вакансиями  
- Анализ данных и статистика
- Exception handling и edge cases
"""

from unittest.mock import MagicMock, patch, call
import pytest
from src.storage.db_manager import DBManager, PSYCOPG2_AVAILABLE


class TestDBManagerInitialization:
    """Тесты инициализации и базовых методов"""
    
    def test_init_with_default_config(self):
        """Тест инициализации с конфигом по умолчанию"""
        with patch('src.storage.db_manager.DatabaseConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            db_manager = DBManager()
            
            # Проверяем что использовался конфиг по умолчанию
            mock_config_class.assert_called_once()
            assert db_manager.db_config == mock_config
    
    def test_init_with_custom_config(self):
        """Тест инициализации с пользовательским конфигом"""
        mock_config = MagicMock()
        
        db_manager = DBManager(db_config=mock_config)
        
        assert db_manager.db_config == mock_config
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', True)
    @patch('src.storage.db_manager.psycopg2')
    def test_get_connection_with_psycopg2_available(self, mock_psycopg2):
        """Покрытие _get_connection при доступном psycopg2"""
        mock_config = MagicMock()
        mock_config.get_connection_params.return_value = {"host": "localhost"}
        mock_connection = MagicMock()
        mock_psycopg2.connect.return_value = mock_connection
        
        db_manager = DBManager(db_config=mock_config)
        result = db_manager._get_connection()
        
        # Проверяем вызов psycopg2.connect с UTF-8 кодировкой
        expected_params = {"host": "localhost", "client_encoding": "utf8"}
        mock_psycopg2.connect.assert_called_once_with(**expected_params)
        mock_connection.set_client_encoding.assert_called_once_with("UTF8")
        assert result == mock_connection
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', False)
    @patch('src.storage.db_manager.get_db_adapter')
    def test_get_connection_without_psycopg2(self, mock_get_adapter):
        """Покрытие _get_connection при недоступном psycopg2"""
        mock_adapter = MagicMock()
        mock_get_adapter.return_value = mock_adapter
        
        db_manager = DBManager()
        result = db_manager._get_connection()
        
        mock_get_adapter.assert_called_once()
        assert result == mock_adapter
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', True)
    @patch('src.storage.db_manager.psycopg2')
    def test_get_connection_exception_handling(self, mock_psycopg2):
        """Покрытие exception handling в _get_connection"""
        mock_config = MagicMock()
        mock_config.get_connection_params.return_value = {"host": "badhost"}
        mock_psycopg2.connect.side_effect = Exception("Connection failed")
        
        db_manager = DBManager(db_config=mock_config)
        
        with pytest.raises(Exception, match="Connection failed"):
            db_manager._get_connection()


class TestDBManagerDatabaseCreation:
    """Тесты создания базы данных и таблиц"""
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', True)
    def test_ensure_database_exists_success(self):
        """Покрытие _ensure_database_exists при успешном создании"""
        mock_config = MagicMock()
        mock_config.get_connection_params.return_value = {
            "host": "localhost",
            "user": "test",
            "password": "pass",
            "database": "testdb"
        }
        
        db_manager = DBManager(db_config=mock_config)
        
        # Мокируем подключения
        mock_conn_without_db = MagicMock()
        mock_cursor = MagicMock()
        mock_conn_without_db.cursor.return_value = mock_cursor
        
        with patch('src.storage.db_manager.psycopg2') as mock_psycopg2:
            mock_psycopg2.connect.return_value = mock_conn_without_db
            
            result = db_manager._ensure_database_exists()
            
            # Проверяем создание БД
            mock_cursor.execute.assert_any_call("CREATE DATABASE testdb")
            mock_conn_without_db.commit.assert_called()
            mock_conn_without_db.close.assert_called()
            assert result is True
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', True)
    def test_ensure_database_exists_already_exists(self):
        """Покрытие случая когда БД уже существует"""
        mock_config = MagicMock()
        mock_config.get_connection_params.return_value = {
            "database": "existingdb"
        }
        
        db_manager = DBManager(db_config=mock_config)
        
        with patch('src.storage.db_manager.psycopg2') as mock_psycopg2:
            # Имитируем ошибку "database already exists"
            mock_psycopg2.connect.side_effect = Exception("database \"existingdb\" already exists")
            
            result = db_manager._ensure_database_exists()
            
            # БД уже существует - это нормально
            assert result is True
    
    def test_create_tables_success(self):
        """Покрытие create_tables при успешном создании"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.create_tables()
            
            # Проверяем что выполнились SQL команды создания таблиц
            assert mock_cursor.execute.call_count >= 2  # companies и vacancies таблицы
            mock_connection.commit.assert_called()
            mock_connection.close.assert_called()
            assert result is True
    
    def test_create_tables_exception_handling(self):
        """Покрытие exception handling в create_tables"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_get_connection', side_effect=Exception("DB Error")):
            result = db_manager.create_tables()
            
            assert result is False


class TestDBManagerCompanyOperations:
    """Тесты операций с компаниями"""
    
    def test_populate_companies_table_success(self):
        """Покрытие populate_companies_table при успешном заполнении"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        # Мокируем что некоторые компании уже есть, некоторых нет
        mock_cursor.fetchone.side_effect = [None, (1,), None]  # 1-я нет, 2-я есть, 3-я нет
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch('src.storage.db_manager.TARGET_COMPANIES', [
                {'name': 'Company1'}, {'name': 'Company2'}, {'name': 'Company3'}
            ]):
                result = db_manager.populate_companies_table()
                
                # Проверяем INSERT запросы для отсутствующих компаний
                insert_calls = [call for call in mock_cursor.execute.call_args_list 
                               if 'INSERT' in str(call[0][0])]
                assert len(insert_calls) >= 2  # Для Company1 и Company3
                mock_connection.commit.assert_called()
                assert result is True
    
    def test_get_target_companies_analysis_success(self):
        """Покрытие get_target_companies_analysis"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        # Мокируем результат запроса
        mock_cursor.fetchall.return_value = [
            {'company_name': 'Company1', 'vacancy_count': 10},
            {'company_name': 'Company2', 'vacancy_count': 5}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.get_target_companies_analysis()
            
            mock_cursor.execute.assert_called()
            assert len(result) == 2
            assert result[0]['company_name'] == 'Company1'
            mock_connection.close.assert_called()
    
    def test_get_companies_and_vacancies_count(self):
        """Покрытие get_companies_and_vacancies_count"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {'company_name': 'Test Co', 'vacancies_count': 15}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.get_companies_and_vacancies_count()
            
            mock_cursor.execute.assert_called()
            assert len(result) == 1
            assert result[0]['vacancies_count'] == 15
    
    def test_is_target_company_match_true(self):
        """Покрытие _is_target_company_match возвращающего True"""
        db_manager = DBManager()
        
        with patch('src.storage.db_manager.TARGET_COMPANIES', [
            {'name': 'Exact Company'},
            {'name': 'Partial'}
        ]):
            # Точное совпадение
            assert db_manager._is_target_company_match('Exact Company') is True
            
            # Частичное совпадение
            assert db_manager._is_target_company_match('Partial Systems LLC') is True
    
    def test_is_target_company_match_false(self):
        """Покрытие _is_target_company_match возвращающего False"""
        db_manager = DBManager()
        
        with patch('src.storage.db_manager.TARGET_COMPANIES', [
            {'name': 'Known Company'}
        ]):
            assert db_manager._is_target_company_match('Unknown Company') is False
    
    def test_filter_companies_by_targets(self):
        """Покрытие filter_companies_by_targets"""
        db_manager = DBManager()
        
        companies = [
            {'name': 'Target Company'},
            {'name': 'Random Company'},
            {'name': 'Another Target'}
        ]
        
        with patch.object(db_manager, '_is_target_company_match', 
                         side_effect=[True, False, True]):
            result = db_manager.filter_companies_by_targets(companies)
            
            assert len(result) == 2
            assert result[0]['name'] == 'Target Company'
            assert result[1]['name'] == 'Another Target'


class TestDBManagerVacancyOperations:
    """Тесты операций с вакансиями"""
    
    def test_ensure_tables_exist(self):
        """Покрытие _ensure_tables_exist"""
        db_manager = DBManager()
        
        with patch.object(db_manager, 'create_tables', return_value=True) as mock_create:
            db_manager._ensure_tables_exist()
            
            mock_create.assert_called_once()
    
    def test_get_all_vacancies_success(self):
        """Покрытие get_all_vacancies при успешном получении"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {'title': 'Python Developer', 'salary_from': 100000},
            {'title': 'Java Developer', 'salary_from': 90000}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist'):
                result = db_manager.get_all_vacancies()
                
                mock_cursor.execute.assert_called()
                assert len(result) == 2
                assert result[0]['title'] == 'Python Developer'
    
    def test_get_all_vacancies_exception_handling(self):
        """Покрытие exception handling в get_all_vacancies"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_get_connection', side_effect=Exception("DB Error")):
            result = db_manager.get_all_vacancies()
            
            assert result == []
    
    def test_get_avg_salary_success(self):
        """Покрытие get_avg_salary при успешном расчете"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = {'avg_salary': 150000.0}
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist'):
                result = db_manager.get_avg_salary()
                
                assert result == 150000.0
                mock_cursor.execute.assert_called()
    
    def test_get_avg_salary_no_data(self):
        """Покрытие get_avg_salary когда нет данных"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = None
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist'):
                result = db_manager.get_avg_salary()
                
                assert result == 0
    
    def test_get_vacancies_with_higher_salary_success(self):
        """Покрытие get_vacancies_with_higher_salary"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {'title': 'Senior Developer', 'salary_from': 200000}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist'):
                result = db_manager.get_vacancies_with_higher_salary(150000)
                
                # Проверяем правильный SQL запрос
                mock_cursor.execute.assert_called()
                assert len(result) == 1
                assert result[0]['salary_from'] == 200000
    
    def test_get_vacancies_with_keyword_success(self):
        """Покрытие get_vacancies_with_keyword"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {'title': 'Python Django Developer'}
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist'):
                result = db_manager.get_vacancies_with_keyword("Python")
                
                mock_cursor.execute.assert_called()
                assert len(result) == 1
                assert 'Python' in result[0]['title']


class TestDBManagerStatistics:
    """Тесты статистических методов"""
    
    def test_get_database_stats_success(self):
        """Покрытие get_database_stats при успешном получении"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        # Мокируем результаты разных запросов
        mock_cursor.fetchone.side_effect = [
            {'count': 100},  # vacancies count
            {'count': 10},   # companies count
            {'avg_salary': 120000}  # average salary
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            with patch.object(db_manager, '_ensure_tables_exist'):
                result = db_manager.get_database_stats()
                
                assert result['vacancies_count'] == 100
                assert result['companies_count'] == 10
                assert result['average_salary'] == 120000
                assert mock_cursor.execute.call_count == 3
    
    def test_get_database_stats_exception_handling(self):
        """Покрытие exception handling в get_database_stats"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_get_connection', side_effect=Exception("DB Error")):
            result = db_manager.get_database_stats()
            
            # Возвращаются нулевые значения при ошибке
            assert result['vacancies_count'] == 0
            assert result['companies_count'] == 0
            assert result['average_salary'] == 0


class TestDBManagerConnectionMethods:
    """Тесты методов подключения"""
    
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
        mock_connection.cursor.return_value = mock_cursor
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.check_connection()
            
            mock_cursor.execute.assert_called_with("SELECT 1")
            mock_connection.close.assert_called()
            assert result is True
    
    def test_check_connection_failure(self):
        """Покрытие check_connection при ошибке подключения"""
        db_manager = DBManager()
        
        with patch.object(db_manager, '_get_connection', side_effect=Exception("Connection failed")):
            result = db_manager.check_connection()
            
            assert result is False


class TestDBManagerAnalysisMethods:
    """Тесты методов анализа данных"""
    
    def test_analyze_api_data_with_sql_success(self):
        """Покрытие analyze_api_data_with_sql"""
        db_manager = DBManager()
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        # Мокируем несколько запросов статистики
        mock_cursor.fetchone.side_effect = [
            {'count': 150},      # total vacancies
            {'avg_salary': 95000}, # average salary
            {'max_salary': 300000}, # max salary
            {'count': 25}        # companies count
        ]
        
        with patch.object(db_manager, '_get_connection', return_value=mock_connection):
            result = db_manager.analyze_api_data_with_sql()
            
            # Проверяем что выполнились множественные запросы
            assert mock_cursor.execute.call_count >= 4
            assert isinstance(result, dict)
            assert 'total_vacancies' in result or 'statistics' in result


class TestDBManagerEdgeCases:
    """Тесты edge cases и редких сценариев"""
    
    @patch('src.storage.db_manager.PSYCOPG2_AVAILABLE', False)
    def test_methods_without_psycopg2_fallback(self):
        """Покрытие методов при недоступном psycopg2"""
        db_manager = DBManager()
        
        # Большинство методов должны работать с простым адаптером
        with patch('src.storage.db_manager.get_db_adapter') as mock_adapter_func:
            mock_adapter = MagicMock()
            mock_adapter_func.return_value = mock_adapter
            
            connection = db_manager._get_connection()
            
            assert connection == mock_adapter
            mock_adapter_func.assert_called_once()
    
    def test_empty_target_companies_list(self):
        """Покрытие случая пустого списка целевых компаний"""
        db_manager = DBManager()
        
        with patch('src.storage.db_manager.TARGET_COMPANIES', []):
            companies = [{'name': 'Any Company'}]
            result = db_manager.filter_companies_by_targets(companies)
            
            assert result == []
    
    def test_none_parameters_handling(self):
        """Покрытие обработки None параметров в различных методах"""
        db_manager = DBManager()
        
        # Тестируем методы которые могут принимать None
        with patch.object(db_manager, '_get_connection', side_effect=Exception("Test")):
            result1 = db_manager.get_vacancies_with_keyword(None)
            result2 = db_manager.get_vacancies_with_higher_salary(None)
            
            assert result1 == []
            assert result2 == []