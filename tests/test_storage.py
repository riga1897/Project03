"""
Тесты для модулей хранения данных
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from src.storage.postgres_saver import PostgresSaver
from src.storage.storage_factory import StorageFactory
from src.vacancies.models import Vacancy


class TestPostgresSaver:
    """Тесты для PostgresSaver"""

    @pytest.fixture
    def mock_db_config(self):
        """Фикстура для мок-конфигурации БД"""
        return {
            'host': 'localhost',
            'port': '5432',
            'database': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

    @pytest.fixture
    def postgres_saver(self, mock_db_config):
        """Фикстура для PostgresSaver с мок-конфигурацией"""
        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'), \
             patch.object(PostgresSaver, '_ensure_companies_table_exists'):
            return PostgresSaver(mock_db_config)

    def test_postgres_saver_initialization(self, postgres_saver):
        """Тест инициализации PostgresSaver"""
        assert postgres_saver is not None
        assert postgres_saver.host == 'localhost'
        assert postgres_saver.port == '5432'
        assert postgres_saver.database == 'test_db'

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_get_connection(self, mock_connect, postgres_saver):
        """Тест получения соединения с БД"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        connection = postgres_saver._get_connection()

        assert connection == mock_connection
        mock_connect.assert_called_once()

    def test_add_vacancy_with_sample_data(self, postgres_saver, sample_vacancy):
        """Тест добавления вакансии с примерными данными"""
        with patch.object(postgres_saver, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_get_conn.return_value = mock_connection
            mock_connection.cursor.return_value = mock_cursor
            mock_cursor.__enter__ = Mock(return_value=mock_cursor)
            mock_cursor.__exit__ = Mock(return_value=None)
            mock_cursor.fetchall.return_value = []
            # Мокаем connection для psycopg2
            mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_connection.cursor.return_value.__exit__ = Mock(return_value=None)
            mock_connection.encoding = 'UTF8'

            result = postgres_saver.add_vacancy([sample_vacancy])

            assert isinstance(result, list)
            mock_cursor.execute.assert_called()

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_ensure_database_exists(self, mock_connect, mock_db_config):
        """Тест создания базы данных если она не существует"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [False]  # БД не существует

        with patch.object(PostgresSaver, '_ensure_tables_exist'), \
             patch.object(PostgresSaver, '_ensure_companies_table_exists'):
            saver = PostgresSaver(mock_db_config)

        # Проверяем, что была попытка создать БД
        mock_cursor.execute.assert_called()

    def test_format_vacancy_data(self, postgres_saver, sample_vacancy):
        """Тест форматирования данных вакансии"""
        # Метод _format_vacancy_data был удален, тестируем через add_vacancy
        with patch.object(postgres_saver, '_get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_get_conn.return_value = mock_connection
            mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_connection.cursor.return_value.__exit__ = Mock(return_value=None)
            mock_cursor.fetchall.return_value = []

            # Проверяем, что метод add_vacancy работает
            result = postgres_saver.add_vacancy([sample_vacancy])
            assert isinstance(result, list)


class TestStorageFactory:
    """Тесты для StorageFactory"""

    def test_get_storage_postgres(self):
        """Тест получения PostgreSQL хранилища"""
        config = {'type': 'postgres', 'host': 'localhost'}

        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'), \
             patch.object(PostgresSaver, '_ensure_companies_table_exists'):
            storage = StorageFactory.create_storage(config)

        assert isinstance(storage, PostgresSaver)

    def test_get_storage_invalid_type(self):
        """Тест получения хранилища с неверным типом"""
        config = {'type': 'invalid_type'}

        with pytest.raises(ValueError):
            StorageFactory.create_storage(config)

    def test_get_storage_missing_config(self):
        """Тест получения хранилища без конфигурации"""
        with pytest.raises((ValueError, TypeError)):
            StorageFactory.create_storage(None)