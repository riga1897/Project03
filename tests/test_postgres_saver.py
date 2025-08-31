import pytest
from unittest.mock import MagicMock, patch
import psycopg2
from psycopg2 import sql
import sys
import os
from dataclasses import dataclass
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.vacancies.models import Vacancy
except ImportError:
    # Создаем тестовый класс Vacancy, если не удается импортировать
    @dataclass
    class Vacancy:
        id: str
        title: str
        company: str
        salary: Optional[str] = None
        url: str = ""
        description: str = ""

# Создаем недостающие тестовые классы
@dataclass
class VacancySalary:
    """Тестовый класс зарплаты вакансии"""
    from_amount: Optional[int] = None
    to_amount: Optional[int] = None
    currency: str = "RUR"
    gross: bool = False

    def __str__(self):
        if self.from_amount and self.to_amount:
            return f"{self.from_amount}-{self.to_amount} {self.currency}"
        elif self.from_amount:
            return f"от {self.from_amount} {self.currency}"
        elif self.to_amount:
            return f"до {self.to_amount} {self.currency}"
        return "Зарплата не указана"

@dataclass  
class VacancyEmployer:
    """Тестовый класс работодателя"""
    id: str
    name: str
    url: Optional[str] = None
    trusted: bool = False

    def __str__(self):
        return self.name

from src.storage.postgres_saver import PostgresSaver


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
            id="123",
            title="Python Developer",
            company="Test Company",
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
            ("123", "Python Developer", "Test Company", "https://test.com", None, None, None, None, None, None, None, None)
        ]
        mock_cursor.description = [
            ("vacancy_id",), ("title",), ("company",), ("url",), ("salary_from",), ("salary_to",), 
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
            Vacancy(id="123", title="Python Developer", company="Test Company", url="https://test1.com", source="hh.ru"),
            Vacancy(id="124", title="Java Developer", company="Test Company", url="https://test2.com", source="hh.ru")
        ]

        mock_db_config = {"host": "localhost", "database": "test_db"}
        saver = PostgresSaver(mock_db_config)

        result = saver.save_vacancies(vacancies)

        # Проверяем, что все вакансии были обработаны
        assert mock_cursor.execute.call_count >= len(vacancies)