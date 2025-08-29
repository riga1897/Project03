
"""
Тесты для PostgresSaver с правильными моками
"""

from unittest.mock import MagicMock, Mock, patch
import pytest
from src.storage.postgres_saver import PostgresSaver
from src.vacancies.models import Vacancy


class TestPostgresSaver:
    """Тесты для PostgresSaver"""

    @pytest.fixture
    def mock_db_config(self):
        """Фикстура конфигурации БД"""
        return {
            "host": "localhost",
            "port": "5432",
            "database": "test_db",
            "username": "test_user",
            "password": "test_pass"
        }

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура тестовой вакансии"""
        return Vacancy(
            title="Test Vacancy",
            url="https://test.com/vacancy/1",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Test description",
            requirements="Test requirements",
            responsibilities="Test responsibilities",
            experience="Test experience",
            employment="Test employment",
            schedule="Test schedule",
            employer={"name": "Test Company"},
            vacancy_id="test_1",
            published_at="2024-01-15T10:00:00",
            source="hh.ru",
        )

    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_initialization(self, mock_ensure_tables, mock_ensure_db, mock_db_config):
        """Тест инициализации PostgresSaver"""
        storage = PostgresSaver(mock_db_config)
        assert storage is not None
        assert storage.host == "localhost"
        assert storage.port == "5432"
        assert storage.database == "test_db"

    @patch("psycopg2.connect")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_save_vacancies_success(self, mock_ensure_tables, mock_ensure_db, mock_connect, sample_vacancy):
        """Тест успешного сохранения вакансий"""
        # Настраиваем мок подключения
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = None

        storage = PostgresSaver()
        
        # Мокируем методы для избежания реальных запросов к БД
        with patch.object(storage, 'add_vacancy_batch_optimized', return_value=["Success"]) as mock_batch:
            result = storage.save_vacancies([sample_vacancy])
            assert result == 1  # Возвращает количество операций
            mock_batch.assert_called_once_with([sample_vacancy])

    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_save_vacancies_empty_list(self, mock_ensure_tables, mock_ensure_db):
        """Тест сохранения пустого списка"""
        storage = PostgresSaver()
        result = storage.save_vacancies([])
        assert result == 0

    @patch("psycopg2.connect")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists") 
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_get_vacancies_count(self, mock_ensure_tables, mock_ensure_db, mock_connect):
        """Тест получения количества вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (42,)

        storage = PostgresSaver()
        
        with patch.object(storage, '_get_connection', return_value=mock_conn):
            count = storage.get_vacancies_count()
            assert count == 42

    @patch("psycopg2.connect")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_delete_vacancy_by_id_success(self, mock_ensure_tables, mock_ensure_db, mock_connect):
        """Тест успешного удаления вакансии"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1

        storage = PostgresSaver()
        
        with patch.object(storage, '_get_connection', return_value=mock_conn):
            result = storage.delete_vacancy_by_id("test_1")
            assert result is True

    @patch("psycopg2.connect")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_delete_vacancy_by_id_not_found(self, mock_ensure_tables, mock_ensure_db, mock_connect):
        """Тест удаления несуществующей вакансии"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0

        storage = PostgresSaver()
        
        with patch.object(storage, '_get_connection', return_value=mock_conn):
            result = storage.delete_vacancy_by_id("nonexistent")
            assert result is False

    @patch("psycopg2.connect")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_get_vacancies(self, mock_ensure_tables, mock_ensure_db, mock_connect, sample_vacancy):
        """Тест получения вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        
        # Настраиваем context manager для подключения
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        
        # Настраиваем RealDictCursor context manager
        from psycopg2.extras import RealDictCursor
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor_context

        # Мокируем результат запроса как RealDictRow
        mock_row = {
            "vacancy_id": "test_1",
            "title": "Test Vacancy",
            "url": "https://test.com/vacancy/1",
            "salary_from": 100000,
            "salary_to": 150000,
            "salary_currency": "RUR",
            "description": "Test description",
            "requirements": "Test requirements",
            "responsibilities": "Test responsibilities",
            "experience": "Test experience",
            "employment": "Test employment",
            "schedule": "Test schedule",
            "area": "Test Area",
            "source": "hh.ru",
            "published_at": None,
            "company_name": "Test Company"
        }
        
        mock_cursor.fetchall.return_value = [mock_row]

        storage = PostgresSaver()
        
        with patch.object(storage, '_get_connection', return_value=mock_conn):
            vacancies = storage.get_vacancies()
            assert len(vacancies) == 1
            assert vacancies[0].title == "Test Vacancy"

    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_add_vacancy(self, mock_ensure_tables, mock_ensure_db, sample_vacancy):
        """Тест добавления одной вакансии"""
        storage = PostgresSaver()
        
        # Мокируем add_vacancies
        with patch.object(storage, 'add_vacancies', return_value=["Success"]) as mock_add:
            result = storage.add_vacancy(sample_vacancy)
            assert result is True
            mock_add.assert_called_once_with([sample_vacancy])

    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_is_vacancy_exists(self, mock_ensure_tables, mock_ensure_db, sample_vacancy):
        """Тест проверки существования вакансии"""
        storage = PostgresSaver()
        
        # Мокируем подключение и курсор
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)  # Вакансия существует
        
        with patch.object(storage, '_get_connection', return_value=mock_conn):
            mock_conn.cursor.return_value = mock_cursor
            exists = storage.is_vacancy_exists(sample_vacancy)
            assert exists is True

    @patch("src.storage.postgres_saver.PostgresSaver._ensure_database_exists")
    @patch("src.storage.postgres_saver.PostgresSaver._ensure_tables_exist")
    def test_error_handling(self, mock_ensure_tables, mock_ensure_db):
        """Тест обработки ошибок"""
        storage = PostgresSaver()
        
        # Тест обработки ошибки при получении вакансий
        with patch.object(storage, '_get_connection', side_effect=Exception("Connection error")):
            vacancies = storage.get_vacancies()
            assert vacancies == []
            
        # Тест обработки ошибки при добавлении вакансии
        sample_vacancy = Mock()
        with patch.object(storage, 'add_vacancies', side_effect=Exception("Add error")):
            result = storage.add_vacancy(sample_vacancy)
            assert result is False
