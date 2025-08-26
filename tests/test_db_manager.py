"""
Тесты для класса DBManager
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import psycopg2
from src.storage.db_manager import DBManager
from src.config.db_config import DatabaseConfig


class TestDBManager:
    """Тесты для класса DBManager"""

    @pytest.fixture
    def mock_db_config(self):
        """Фикстура для мок-конфигурации БД"""
        config = Mock(spec=DatabaseConfig)
        config.get_connection_params.return_value = {
            'host': 'localhost',
            'port': '5432',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }
        return config

    @pytest.fixture
    def db_manager(self, mock_db_config):
        """Фикстура для DBManager с мок-конфигурацией"""
        return DBManager(mock_db_config)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_connection_success(self, mock_connect, db_manager):
        """Тест успешного подключения к БД"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        connection = db_manager._get_connection()

        assert connection == mock_connection
        mock_connect.assert_called_once()
        mock_connection.set_client_encoding.assert_called_once_with('UTF8')

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_connection_failure(self, mock_connect, db_manager):
        """Тест ошибки подключения к БД"""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        with pytest.raises(psycopg2.Error):
            db_manager._get_connection()

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_create_tables_success(self, mock_connect, db_manager):
        """Тест успешного создания таблиц"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        db_manager.create_tables()

        # Проверяем, что были выполнены SQL-запросы для создания таблиц
        assert mock_cursor.execute.call_count >= 3  # SET encoding + 2 CREATE TABLE

    @patch('src.config.target_companies.TARGET_COMPANIES', [
        {"hh_id": "1", "name": "Test Company", "description": "Test Description"}
    ])
    @patch('src.storage.db_manager.psycopg2.connect')
    def test_populate_companies_table(self, mock_connect, db_manager):
        """Тест заполнения таблицы компаний"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        # Имитируем пустую таблицу
        mock_cursor.fetchone.return_value = [0]

        db_manager.populate_companies_table()

        # Проверяем, что был выполнен INSERT запрос
        insert_calls = [call for call in mock_cursor.execute.call_args_list
                       if 'INSERT INTO companies' in str(call)]
        assert len(insert_calls) >= 1

    @patch('src.config.target_companies.TARGET_COMPANIES', [
        {"name": "Test Company 1"},
        {"name": "Test Company 2"}
    ])
    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_companies_and_vacancies_count(self, mock_connect, db_manager):
        """Тест получения количества вакансий по компаниям"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        # Имитируем результат запроса
        mock_cursor.fetchall.return_value = [
            ("Test Company 1", 5),
            ("Test Company 2", 3)
        ]

        result = db_manager.get_companies_and_vacancies_count()

        assert len(result) == 2
        assert result[0] == ("Test Company 1", 5)
        assert result[1] == ("Test Company 2", 3)

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_all_vacancies(self, mock_connect, db_manager):
        """Тест получения всех вакансий"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        # Имитируем результат запроса
        mock_cursor.fetchall.return_value = [
            {
                'title': 'Python Developer',
                'company_name': 'Test Company',
                'salary_info': '100000 - 150000 RUR',
                'url': 'https://test.com/vacancy/1',
                'vacancy_id': 'test_1',
                'employer': 'Test Company',
                'area': 'Moscow',
                'company_id': '1'
            }
        ]

        result = db_manager.get_all_vacancies()

        assert len(result) == 1
        assert result[0]['title'] == 'Python Developer'
        assert result[0]['company_name'] == 'Test Company'

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_avg_salary(self, mock_connect, db_manager):
        """Тест расчета средней зарплаты"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        # Имитируем результат запроса
        mock_cursor.fetchone.return_value = [125000.0]

        result = db_manager.get_avg_salary()

        assert result == 125000.0

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_avg_salary_no_data(self, mock_connect, db_manager):
        """Тест расчета средней зарплаты при отсутствии данных"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        # Имитируем отсутствие результата
        mock_cursor.fetchone.return_value = [None]

        result = db_manager.get_avg_salary()

        assert result is None

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect, db_manager):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        # Мокаем get_avg_salary
        with patch.object(db_manager, 'get_avg_salary', return_value=100000.0):
            # Имитируем результат запроса - возвращаем список кортежей
            mock_cursor.fetchall.return_value = [
                ('Senior Python Developer', 'Test Company', '150000 - 200000 RUR', 
                 'https://test.com/vacancy/2', 175000.0, 'test_2', 'Test Company')
            ]

            result = db_manager.get_vacancies_with_higher_salary()

            assert len(result) == 1
            assert result[0]['calculated_salary'] == 175000.0

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_vacancies_with_keyword(self, mock_connect, db_manager):
        """Тест поиска вакансий по ключевому слову"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        # Имитируем результат запроса - возвращаем список кортежей
        mock_cursor.fetchall.return_value = [
            ('Python Developer', 'Test Company', '100000 - 150000 RUR', 
             'https://test.com/vacancy/1', 'Python development position', 'test_1', 'Test Company')
        ]

        result = db_manager.get_vacancies_with_keyword('Python')

        assert len(result) == 1
        assert 'Python' in result[0]['title']
        # Проверяем, что был вызван с правильными параметрами
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args[0]
        assert '%Python%' in call_args[1]

    def test_get_vacancies_with_keyword_empty(self, db_manager):
        """Тест поиска с пустым ключевым словом"""
        result = db_manager.get_vacancies_with_keyword('')
        assert result == []

        result = db_manager.get_vacancies_with_keyword(None)
        assert result == []

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_database_stats(self, mock_connect, db_manager):
        """Тест получения статистики БД"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        # Имитируем результаты разных запросов - возвращаем одиночные значения
        mock_cursor.fetchone.side_effect = [
            (100,),  # total_vacancies
            (15,),   # total_companies  
            (75,),   # vacancies_with_salary
            ('2024-01-15',)  # latest_vacancy_date
        ]

        result = db_manager.get_database_stats()

        assert result is not None
        assert result['total_vacancies'] == 100
        assert result['total_companies'] == 15
        assert result['vacancies_with_salary'] == 75
        assert result['latest_vacancy_date'] == '2024-01-15'

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_get_database_stats_error(self, mock_connect, db_manager):
        """Тест получения статистики БД при ошибке"""
        mock_connect.side_effect = psycopg2.Error("Database error")

        result = db_manager.get_database_stats()

        assert result is None

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_check_connection_success(self, mock_connect, db_manager):
        """Тест успешной проверки подключения"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        result = db_manager.check_connection()

        assert result is True
        mock_cursor.execute.assert_called_with("SELECT 1")

    @patch('src.storage.db_manager.psycopg2.connect')
    def test_check_connection_failure(self, mock_connect, db_manager):
        """Тест неудачной проверки подключения"""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        result = db_manager.check_connection()

        assert result is False

    def test_is_target_company_match(self, db_manager):
        """Тест сопоставления названий компаний"""
        # Точное совпадение
        assert db_manager._is_target_company_match("Яндекс", "яндекс") is True

        # Альтернативные названия
        assert db_manager._is_target_company_match("Тинькофф", "т-банк") is True
        assert db_manager._is_target_company_match("СБЕР", "сбербанк") is True
        assert db_manager._is_target_company_match("VK (ВКонтакте)", "вконтакте") is True

        # Несовпадение
        assert db_manager._is_target_company_match("Яндекс", "Google") is False