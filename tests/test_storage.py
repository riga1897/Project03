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
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_initialization(self, mock_ensure_tables, mock_connect):
        """Тест инициализации хранилища"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        storage = PostgresSaver()
        assert storage is not None

    @patch("psycopg2.connect")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_add_vacancy(self, mock_ensure_tables, mock_connect, sample_vacancy):
        """Тест добавления вакансии"""
        mock_conn = Mock()
        mock_cursor = Mock()

        # Настраиваем context manager для cursor
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_cursor.rowcount = 1
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = None

        # Настраиваем context manager для connection
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.commit.return_value = None

        mock_connect.return_value = mock_conn

        # Мокируем метод add_vacancy_batch_optimized для возврата успешного результата
        with patch.object(PostgresSaver, 'add_vacancy_batch_optimized', return_value=["Successfully added 1 vacancy"]) as mock_batch:
            storage = PostgresSaver()
            result = storage.add_vacancy(sample_vacancy)

            assert result is True
            # Проверяем что вызван add_vacancy_batch_optimized, а не прямые операции с БД
            mock_batch.assert_called_once()

    @patch("psycopg2.connect")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_get_vacancies(self, mock_ensure_tables, mock_connect):
        """Тест получения вакансий"""
        from datetime import datetime

        mock_conn = Mock()
        mock_cursor = Mock()

        # Настраиваем context manager для cursor
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)

        # Мокируем данные в формате словаря (как RealDictCursor)
        mock_row = {
            "vacancy_id": "12345",
            "title": "Python Developer",
            "url": "https://hh.ru/vacancy/12345",
            "salary_from": 100000,
            "salary_to": 150000,
            "salary_currency": "RUR",
            "description": "Test description",
            "requirements": "Python, Django",
            "responsibilities": "Development",
            "experience": "От 1 года до 3 лет",
            "employment": "Полная занятость",
            "schedule": "Полный день",
            "area": "Москва",
            "source": "hh.ru",
            "published_at": datetime(2024, 1, 1),
            "company_name": "Test Company"
        }

        mock_cursor.fetchall.return_value = [mock_row]
        mock_cursor.execute.return_value = None

        # Настраиваем context manager для connection
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor

        mock_connect.return_value = mock_conn

        storage = PostgresSaver()
        vacancies = storage.get_vacancies()

        assert len(vacancies) == 1
        assert vacancies[0].title == "Python Developer"
        assert vacancies[0].vacancy_id == "12345"

    @patch("psycopg2.connect")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_delete_vacancy_by_id(self, mock_ensure_tables, mock_connect):
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
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_get_vacancies_count(self, mock_ensure_tables, mock_connect):
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