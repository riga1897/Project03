"""
Тесты для DBManager

Содержит тесты для проверки корректности работы с базой данных PostgreSQL
и специфичных методов согласно требованиям проекта.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.storage.db_manager import DBManager


class TestDBManager:
    """Тесты для класса DBManager"""

    @patch('psycopg2.connect')
    def test_initialization(self, mock_connect):
        """Тест инициализации DBManager"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        assert db_manager is not None

    @patch('psycopg2.connect')
    def test_check_connection(self, mock_connect):
        """Тест проверки подключения к базе данных"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        result = db_manager.check_connection()

        assert result is True

    @patch('psycopg2.connect')
    def test_check_connection_failure(self, mock_connect):
        """Тест неудачной проверки подключения"""
        mock_connect.side_effect = Exception("Connection failed")

        db_manager = DBManager()
        result = db_manager.check_connection()

        assert result is False

    @pytest.fixture
    def sample_companies_data(self):
        """Фикстура с примерами данных компаний"""
        return [
            {"name": "СБЕР", "vacancies_count": 10},
            {"name": "Яндекс", "vacancies_count": 15}
        ]

    @patch('psycopg2.connect')
    def test_get_companies_and_vacancies_count(self, mock_connect, sample_companies_data):
        """Тест получения списка компаний и количества вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = sample_companies_data
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        companies = db_manager.get_companies_and_vacancies_count()

        assert len(companies) == 2
        assert companies[0]["name"] == "СБЕР"
        assert companies[0]["vacancies_count"] == 10

    @patch('psycopg2.connect')
    def test_get_all_vacancies(self, mock_connect):
        """Тест получения всех вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("Python Developer", "СБЕР", 100000, 150000, "https://hh.ru/vacancy/12345")
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        vacancies = db_manager.get_all_vacancies()

        assert len(vacancies) == 1
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_avg_salary(self, mock_connect):
        """Тест получения средней зарплаты"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (125000.0,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        avg_salary = db_manager.get_avg_salary()

        assert avg_salary == 125000.0
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("Senior Python Developer", "СБЕР", 150000, 200000, "https://hh.ru/vacancy/67890")
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        vacancies = db_manager.get_vacancies_with_higher_salary()

        assert len(vacancies) == 1
        mock_cursor.execute.assert_called()

    @patch('psycopg2.connect')
    def test_get_vacancies_with_keyword(self, mock_connect):
        """Тест поиска вакансий по ключевому слову"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("Python Developer", "СБЕР", 100000, 150000, "https://hh.ru/vacancy/12345")
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        vacancies = db_manager.get_vacancies_with_keyword("python")

        assert len(vacancies) == 1
        mock_cursor.execute.assert_called_with(
            pytest.approx(mock_cursor.execute.call_args[0][0], abs=1e-2),
            ("python",)
        )

    @patch('psycopg2.connect')
    def test_create_tables(self, mock_connect):
        """Тест создания таблиц"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        db_manager.create_tables()

        # Проверяем, что execute был вызван несколько раз (для создания таблиц)
        assert mock_cursor.execute.call_count >= 2
        mock_conn.commit.assert_called()

    @patch('psycopg2.connect')
    def test_populate_companies_table(self, mock_connect):
        """Тест заполнения таблицы компаний"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        db_manager.populate_companies_table()

        # Проверяем, что были выполнены SQL запросы
        assert mock_cursor.execute.call_count > 0
        mock_conn.commit.assert_called()