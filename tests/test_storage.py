"""
Тесты для модулей хранения данных

Содержит тесты для проверки корректности работы с различными
типами хранилищ данных (PostgreSQL).
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.storage.postgres_saver import PostgresSaver
from src.storage.storage_factory import StorageFactory
from src.vacancies.models import Vacancy


class TestPostgresSaver:
    """Тесты для PostgreSQL хранилища"""

    @patch("psycopg2.connect")
    def test_initialization(self, mock_connect):
        """Тест инициализации хранилища"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        storage = PostgresSaver()
        assert storage is not None

    @patch("psycopg2.connect")
    def test_add_vacancy(self, mock_connect, sample_vacancy):
        """Тест добавления вакансии"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        storage = PostgresSaver()
        result = storage.add_vacancy(sample_vacancy)

        assert result is True
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch("psycopg2.connect")
    def test_get_vacancies(self, mock_connect):
        """Тест получения вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (
                "12345",
                "Python Developer",
                "Test Company",
                "https://hh.ru/vacancy/12345",
                "100000",
                "150000",
                "RUR",
                "Test description",
                "Python, Django",
                "Development",
                "От 1 года до 3 лет",
                "Полная занятость",
                "Полный день",
                "2024-01-01T00:00:00",
                "hh.ru",
            )
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        storage = PostgresSaver()
        vacancies = storage.get_vacancies()

        assert len(vacancies) == 1
        assert vacancies[0].title == "Python Developer"
        assert vacancies[0].vacancy_id == "12345"

    @patch("psycopg2.connect")
    def test_delete_vacancy_by_id(self, mock_connect):
        """Тест удаления вакансии по ID"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        storage = PostgresSaver()
        result = storage.delete_vacancy_by_id("12345")

        assert result is True
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch("psycopg2.connect")
    def test_get_vacancies_count(self, mock_connect):
        """Тест получения количества вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (10,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        storage = PostgresSaver()
        count = storage.get_vacancies_count()

        assert count == 10


class TestStorageFactory:
    """Тесты для фабрики хранилищ"""

    def test_create_postgres_storage(self):
        """Тест создания PostgreSQL хранилища"""
        storage = StorageFactory.create_storage("postgres")
        assert isinstance(storage, PostgresSaver)

    def test_get_default_storage(self):
        """Тест получения хранилища по умолчанию"""
        storage = StorageFactory.get_default_storage()
        assert isinstance(storage, PostgresSaver)

    def test_invalid_storage_type(self):
        """Тест обработки неверного типа хранилища"""
        with pytest.raises((ValueError, KeyError)):
            StorageFactory.create_storage("invalid_type")
