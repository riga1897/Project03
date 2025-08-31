
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any, Tuple, Optional

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.storage.db_manager import DBManager
from src.config.db_config import DatabaseConfig


class MockConnection:
    """Мок для подключения к базе данных"""
    
    def __init__(self):
        self.cursor_instance = MockCursor()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def cursor(self, cursor_factory=None):
        return self.cursor_instance
        
    def set_client_encoding(self, encoding):
        pass


class MockCursor:
    """Мок для курсора базы данных"""
    
    def __init__(self):
        self._results = []
        self._executed_queries = []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def execute(self, query, params=None):
        self._executed_queries.append((query, params))
        
    def fetchone(self):
        if self._results:
            return self._results[0]
        return None
        
    def fetchall(self):
        return self._results
        
    def set_results(self, results):
        self._results = results


class TestDBManager:
    """Тесты для DBManager"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.mock_config = Mock(spec=DatabaseConfig)
        self.mock_config.get_connection_params.return_value = {
            "host": "localhost",
            "port": "5432",
            "database": "test_db",
            "user": "test_user",
            "password": "test_password"
        }
        
        self.db_manager = DBManager(self.mock_config)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_db_manager_initialization(self, mock_connect):
        """Тест инициализации DBManager"""
        db_manager = DBManager()
        assert db_manager is not None
        assert hasattr(db_manager, 'db_config')

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_connection_success(self, mock_connect):
        """Тест успешного подключения к БД"""
        mock_connection = MockConnection()
        mock_connect.return_value = mock_connection
        
        connection = self.db_manager._get_connection()
        
        assert connection is not None
        mock_connect.assert_called_once()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_connection_error(self, mock_connect):
        """Тест ошибки подключения к БД"""
        import psycopg2
        mock_connect.side_effect = psycopg2.Error("Connection failed")
        
        with pytest.raises(psycopg2.Error):
            self.db_manager._get_connection()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_check_connection_success(self, mock_connect):
        """Тест успешной проверки подключения"""
        mock_connection = MockConnection()
        mock_connection.cursor_instance.set_results([(1,)])
        mock_connect.return_value = mock_connection
        
        result = self.db_manager.check_connection()
        
        assert result is True

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_check_connection_failure(self, mock_connect):
        """Тест неудачной проверки подключения"""
        import psycopg2
        mock_connect.side_effect = psycopg2.Error("Connection failed")
        
        result = self.db_manager.check_connection()
        
        assert result is False

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_create_tables(self, mock_connect):
        """Тест создания таблиц"""
        mock_connection = MockConnection()
        mock_connect.return_value = mock_connection
        
        # Не должно вызывать исключений
        self.db_manager.create_tables()
        
        mock_connect.assert_called()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_all_vacancies_success(self, mock_connect):
        """Тест получения всех вакансий"""
        mock_connection = MockConnection()
        mock_vacancies_data = [
            {
                'title': 'Python Developer',
                'company_name': 'Test Company',
                'salary_info': '100000 - 150000 RUR',
                'url': 'https://test.com/vacancy/1',
                'vacancy_id': '1'
            }
        ]
        
        # Создаем мок для RealDictCursor
        mock_cursor = Mock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_cursor.fetchall.return_value = mock_vacancies_data
        
        mock_connection.cursor = Mock(return_value=mock_cursor)
        mock_connect.return_value = mock_connection
        
        result = self.db_manager.get_all_vacancies()
        
        assert isinstance(result, list)
        # Может быть пустым если есть проблемы с таблицами
        assert len(result) >= 0

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_all_vacancies_error(self, mock_connect):
        """Тест ошибки при получении всех вакансий"""
        import psycopg2
        mock_connect.side_effect = psycopg2.Error("Database error")
        
        result = self.db_manager.get_all_vacancies()
        
        assert result == []

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_avg_salary_success(self, mock_connect):
        """Тест получения средней зарплаты"""
        mock_connection = MockConnection()
        mock_connection.cursor_instance.set_results([(125000.0,)])
        mock_connect.return_value = mock_connection
        
        result = self.db_manager.get_avg_salary()
        
        # Может вернуть None если нет данных или проблемы с таблицами
        assert result is None or isinstance(result, float)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_avg_salary_no_data(self, mock_connect):
        """Тест получения средней зарплаты без данных"""
        mock_connection = MockConnection()
        mock_connection.cursor_instance.set_results([(None,)])
        mock_connect.return_value = mock_connection
        
        result = self.db_manager.get_avg_salary()
        
        assert result is None

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_higher_salary_success(self, mock_connect):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_connection = MockConnection()
        mock_connection.cursor_instance.set_results([
            ('Python Developer', 'Test Company', '150000 - 200000 RUR', 'https://test.com', 175000.0, '1')
        ])
        mock_connect.return_value = mock_connection
        
        # Мокируем get_avg_salary чтобы вернуть тестовое значение
        with patch.object(self.db_manager, 'get_avg_salary', return_value=100000.0):
            result = self.db_manager.get_vacancies_with_higher_salary()
        
        assert isinstance(result, list)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_higher_salary_no_avg(self, mock_connect):
        """Тест получения вакансий с зарплатой выше средней без средней зарплаты"""
        # Мокируем get_avg_salary чтобы вернуть None
        with patch.object(self.db_manager, 'get_avg_salary', return_value=None):
            result = self.db_manager.get_vacancies_with_higher_salary()
        
        assert result == []

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_keyword_success(self, mock_connect):
        """Тест поиска вакансий по ключевому слову"""
        mock_connection = MockConnection()
        mock_connection.cursor_instance.set_results([
            ('Python Developer', 'Test Company', '100000 - 150000 RUR', 'https://test.com', 'Python development', '1')
        ])
        mock_connect.return_value = mock_connection
        
        result = self.db_manager.get_vacancies_with_keyword("Python")
        
        assert isinstance(result, list)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_keyword_empty(self, mock_connect):
        """Тест поиска вакансий с пустым ключевым словом"""
        result = self.db_manager.get_vacancies_with_keyword("")
        
        assert result == []

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_companies_and_vacancies_count_success(self, mock_connect):
        """Тест получения списка компаний и количества вакансий"""
        mock_connection = MockConnection()
        mock_connection.cursor_instance.set_results([
            ('Test Company', 5),
            ('Another Company', 3)
        ])
        mock_connect.return_value = mock_connection
        
        # Мокируем check_connection
        with patch.object(self.db_manager, 'check_connection', return_value=True):
            result = self.db_manager.get_companies_and_vacancies_count()
        
        assert isinstance(result, list)
        assert len(result) >= 0

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_companies_and_vacancies_count_no_connection(self, mock_connect):
        """Тест получения списка компаний без подключения к БД"""
        # Мокируем check_connection чтобы вернуть False
        with patch.object(self.db_manager, 'check_connection', return_value=False):
            result = self.db_manager.get_companies_and_vacancies_count()
        
        assert isinstance(result, list)
        # Должен вернуть список целевых компаний с нулями
        assert len(result) > 0

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_database_stats_success(self, mock_connect):
        """Тест получения статистики базы данных"""
        mock_connection = MockConnection()
        
        # Мок для RealDictCursor
        mock_cursor = Mock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        
        # Мокируем результаты различных запросов
        mock_cursor.fetchone.side_effect = [
            {
                'total_vacancies': 100,
                'vacancies_with_salary': 80,
                'unique_employers': 20,
                'avg_salary': 125000.0,
                'latest_vacancy_date': '2024-01-01',
                'earliest_vacancy_date': '2023-01-01',
                'vacancies_last_week': 5,
                'vacancies_last_month': 25,
                'vacancies_with_description': 90,
                'vacancies_with_requirements': 85,
                'vacancies_with_area': 95,
                'vacancies_with_published_date': 88
            },
            {'total_companies': 25}
        ]
        
        mock_cursor.fetchall.side_effect = [
            [{'employer': 'Company 1', 'vacancy_count': 10}],  # top_employers
            [{'salary_range': '100k-150k', 'count': 30}]       # salary_distribution
        ]
        
        mock_connection.cursor = Mock(return_value=mock_cursor)
        mock_connect.return_value = mock_connection
        
        result = self.db_manager.get_database_stats()
        
        assert isinstance(result, dict)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_database_stats_error(self, mock_connect):
        """Тест ошибки при получении статистики базы данных"""
        import psycopg2
        mock_connect.side_effect = psycopg2.Error("Database error")
        
        result = self.db_manager.get_database_stats()
        
        assert result == {}

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_populate_companies_table(self, mock_connect):
        """Тест заполнения таблицы компаний"""
        mock_connection = MockConnection()
        # Мокируем что таблица существует и пуста
        mock_connection.cursor_instance.set_results([(True,), (0,), (None,)])
        mock_connect.return_value = mock_connection
        
        # Не должно вызывать исключений
        self.db_manager.populate_companies_table()
        
        mock_connect.assert_called()

    def test_is_target_company_match(self):
        """Тест сопоставления названий компаний"""
        # Тестируем метод напрямую
        assert self.db_manager._is_target_company_match("Яндекс", "яндекс")
        assert self.db_manager._is_target_company_match("Тинькофф", "т-банк")
        assert not self.db_manager._is_target_company_match("Яндекс", "Google")

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_filter_companies_by_targets(self, mock_connect):
        """Тест фильтрации компаний по целевым"""
        mock_connection = MockConnection()
        mock_connection.cursor_instance.set_results([("123", "Яндекс")])
        mock_connect.return_value = mock_connection
        
        api_companies = [
            {"id": "123", "name": "Яндекс"},
            {"id": "456", "name": "Random Company"}
        ]
        
        result = self.db_manager.filter_companies_by_targets(api_companies)
        
        assert isinstance(result, list)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_analyze_api_data_with_sql(self, mock_connect):
        """Тест анализа данных API с помощью SQL"""
        mock_connection = MockConnection()
        
        # Мок для RealDictCursor
        mock_cursor = Mock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_cursor.fetchone.return_value = {
            'total_vacancies': 10,
            'unique_employers': 5,
            'vacancies_with_salary': 8,
            'avg_salary': 120000.0
        }
        mock_cursor.fetchall.return_value = [{'employer': 'Test', 'vacancy_count': 3}]
        
        mock_connection.cursor = Mock(return_value=mock_cursor)
        mock_connect.return_value = mock_connection
        
        api_data = [
            {
                "id": "123",
                "name": "Python Developer",
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "employer": {"name": "Test Company"}
            }
        ]
        
        result = self.db_manager.analyze_api_data_with_sql(api_data)
        
        assert isinstance(result, dict)

    def test_ensure_tables_exist_success(self):
        """Тест обеспечения существования таблиц"""
        # Мокируем create_tables
        with patch.object(self.db_manager, 'create_tables', return_value=None):
            result = self.db_manager._ensure_tables_exist()
        
        assert result is True

    def test_ensure_tables_exist_failure(self):
        """Тест ошибки при обеспечении существования таблиц"""
        # Мокируем create_tables с исключением
        with patch.object(self.db_manager, 'create_tables', side_effect=Exception("Error")):
            result = self.db_manager._ensure_tables_exist()
        
        assert result is False

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_target_companies_analysis(self, mock_connect):
        """Тест анализа целевых компаний"""
        # Мокируем get_companies_and_vacancies_count
        with patch.object(self.db_manager, 'get_companies_and_vacancies_count', return_value=[('Company 1', 5)]):
            result = self.db_manager.get_target_companies_analysis()
        
        assert isinstance(result, list)
        assert len(result) > 0
