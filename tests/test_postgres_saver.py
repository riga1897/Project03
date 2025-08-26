
"""
Тесты для PostgresSaver
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import psycopg2
from src.storage.postgres_saver import PostgresSaver
from src.vacancies.models import Vacancy


class TestPostgresSaver:
    """Тесты для PostgresSaver"""

    @pytest.fixture
    def mock_db_manager(self):
        """Фикстура мок DBManager"""
        mock_manager = Mock()
        mock_manager.check_connection.return_value = True
        return mock_manager

    @pytest.fixture
    def postgres_saver(self, mock_db_manager):
        """Фикстура PostgresSaver"""
        return PostgresSaver(db_manager=mock_db_manager)

    def test_initialization(self, postgres_saver, mock_db_manager):
        """Тест инициализации"""
        assert postgres_saver.db_manager == mock_db_manager

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_save_vacancies_success(self, mock_connect, postgres_saver):
        """Тест успешного сохранения вакансий"""
        # Мокаем подключение
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        # Создаем тестовые вакансии
        vacancies = [
            Vacancy(
                vacancy_id="1",
                title="Python Developer",
                url="https://test.com/1",
                salary_from=100000,
                salary_to=150000,
                salary_currency="RUR",
                description="Test description",
                requirements="Python",
                responsibilities="Development",
                experience="1-3 года",
                employment="Полная занятость",
                schedule="Полный день",
                employer="TechCorp",
                area="Москва",
                source="hh.ru",
                published_at="2024-01-15T10:30:00+0300",
                company_id="123"
            )
        ]

        # Мокаем get_connection из db_manager
        postgres_saver.db_manager._get_connection = Mock(return_value=mock_connection)

        result = postgres_saver.save_vacancies(vacancies)

        assert result is True
        # Проверяем, что execute был вызван
        assert mock_cursor.execute.called

    def test_save_vacancies_empty_list(self, postgres_saver):
        """Тест сохранения пустого списка"""
        result = postgres_saver.save_vacancies([])
        assert result is True

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_save_vacancies_database_error(self, mock_connect, postgres_saver):
        """Тест ошибки базы данных при сохранении"""
        mock_connect.side_effect = psycopg2.Error("Database error")
        postgres_saver.db_manager._get_connection = Mock(side_effect=psycopg2.Error("Database error"))

        vacancies = [Mock(spec=Vacancy)]
        result = postgres_saver.save_vacancies(vacancies)

        assert result is False

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_get_all_vacancies(self, mock_connect, postgres_saver):
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

        # Мокаем результат запроса
        mock_cursor.fetchall.return_value = [
            ("1", "Python Developer", "https://test.com/1", 100000, 150000, "RUR", 
             "Test description", "Python", "Development", "1-3 года", "Полная занятость",
             "Полный день", "TechCorp", "Москва", "hh.ru", "2024-01-15T10:30:00+0300", "123")
        ]

        postgres_saver.db_manager._get_connection = Mock(return_value=mock_connection)

        result = postgres_saver.get_all_vacancies()

        assert len(result) == 1
        assert isinstance(result[0], Vacancy)
        assert result[0].title == "Python Developer"

    def test_get_vacancies_count(self, postgres_saver):
        """Тест подсчета вакансий через DBManager"""
        postgres_saver.db_manager.get_companies_and_vacancies_count.return_value = [
            ("Company1", 5),
            ("Company2", 3)
        ]

        result = postgres_saver.get_vacancies_count()

        assert len(result) == 2
        assert result[0] == ("Company1", 5)

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_delete_vacancy_by_id_success(self, mock_connect, postgres_saver):
        """Тест успешного удаления вакансии"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        mock_cursor.rowcount = 1  # Удалена 1 строка

        postgres_saver.db_manager._get_connection = Mock(return_value=mock_connection)

        result = postgres_saver.delete_vacancy_by_id("123")

        assert result is True
        mock_cursor.execute.assert_called()

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_delete_vacancy_by_id_not_found(self, mock_connect, postgres_saver):
        """Тест удаления несуществующей вакансии"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor_context

        mock_cursor.rowcount = 0  # Не удалено ни одной строки

        postgres_saver.db_manager._get_connection = Mock(return_value=mock_connection)

        result = postgres_saver.delete_vacancy_by_id("nonexistent")

        assert result is False

    def test_filter_vacancies_by_salary(self, postgres_saver):
        """Тест фильтрации вакансий по зарплате через DBManager"""
        mock_vacancies = [
            Mock(spec=Vacancy, salary_from=100000),
            Mock(spec=Vacancy, salary_from=200000)
        ]
        
        postgres_saver.db_manager.get_vacancies_with_higher_salary.return_value = mock_vacancies

        result = postgres_saver.filter_vacancies_by_salary(150000)

        assert len(result) == 2
        postgres_saver.db_manager.get_vacancies_with_higher_salary.assert_called_once()

    def test_search_vacancies_by_keyword(self, postgres_saver):
        """Тест поиска вакансий по ключевому слову через DBManager"""
        mock_vacancies = [Mock(spec=Vacancy, title="Python Developer")]
        
        postgres_saver.db_manager.get_vacancies_with_keyword.return_value = mock_vacancies

        result = postgres_saver.search_vacancies_by_keyword("Python")

        assert len(result) == 1
        postgres_saver.db_manager.get_vacancies_with_keyword.assert_called_once_with("Python")
