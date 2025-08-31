
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.postgres_saver import PostgresSaver
from src.vacancies.models import Vacancy, VacancySalary, VacancyEmployer


class TestPostgresSaver:
    """Тесты для PostgresSaver"""

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_postgres_saver_initialization(self, mock_connect):
        """Тест инициализации PostgresSaver"""
        mock_db_config = {
            "host": "localhost",
            "port": "5432",
            "database": "test_db",
            "username": "test_user",
            "password": "test_password"
        }
        
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        saver = PostgresSaver(mock_db_config)
        assert saver.db_config == mock_db_config

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_get_connection(self, mock_connect):
        """Тест получения соединения с БД"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        mock_db_config = {"host": "localhost", "database": "test_db"}
        saver = PostgresSaver(mock_db_config)
        
        connection = saver._get_connection()
        assert connection == mock_connection
        mock_connect.assert_called()

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_save_vacancy(self, mock_connect):
        """Тест сохранения вакансии"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru"
        )
        
        mock_db_config = {"host": "localhost", "database": "test_db"}
        saver = PostgresSaver(mock_db_config)
        
        result = saver.save_vacancy(vacancy)
        
        # Проверяем, что SQL запрос был выполнен
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_get_vacancies(self, mock_connect):
        """Тест получения всех вакансий"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Настраиваем возвращаемые данные
        mock_cursor.fetchall.return_value = [
            ("123", "Python Developer", "https://test.com", "hh.ru", None, None, None, None, None, None, None, None)
        ]
        mock_cursor.description = [
            ("vacancy_id",), ("title",), ("url",), ("source",), ("salary_from",), ("salary_to",), 
            ("salary_currency",), ("employer_name",), ("area",), ("experience",), ("employment",), ("description",)
        ]
        
        mock_db_config = {"host": "localhost", "database": "test_db"}
        saver = PostgresSaver(mock_db_config)
        
        result = saver.get_vacancies()
        
        assert isinstance(result, list)
        mock_cursor.execute.assert_called()

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_delete_vacancy_by_id(self, mock_connect):
        """Тест удаления вакансии по ID"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        mock_cursor.rowcount = 1
        
        mock_db_config = {"host": "localhost", "database": "test_db"}
        saver = PostgresSaver(mock_db_config)
        
        result = saver.delete_vacancy_by_id("123")
        
        assert result is True
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_connection_error_handling(self, mock_connect):
        """Тест обработки ошибок соединения"""
        mock_connect.side_effect = Exception("Connection failed")
        
        mock_db_config = {"host": "localhost", "database": "test_db"}
        saver = PostgresSaver(mock_db_config)
        
        # При ошибке соединения методы должны обрабатывать исключения
        result = saver.get_vacancies()
        assert result == []

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_save_multiple_vacancies(self, mock_connect):
        """Тест сохранения нескольких вакансий"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        vacancies = [
            Vacancy("123", "Python Developer", "https://test1.com", "hh.ru"),
            Vacancy("124", "Java Developer", "https://test2.com", "hh.ru")
        ]
        
        mock_db_config = {"host": "localhost", "database": "test_db"}
        saver = PostgresSaver(mock_db_config)
        
        result = saver.save_vacancies(vacancies)
        
        # Проверяем, что все вакансии были обработаны
        assert mock_cursor.execute.call_count >= len(vacancies)
