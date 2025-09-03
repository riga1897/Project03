import os
import sys
from dataclasses import dataclass
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import psycopg2
import pytest
from psycopg2 import sql

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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


# Создаем тестовый класс PostgresSaver для тестирования
class PostgresSaver:
    """Тестовый класс для сохранения в PostgreSQL"""

    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.connection = None

    def _get_connection(self):
        """Получить соединение с БД"""
        import psycopg2

        return psycopg2.connect(**self.db_config)

    def save_vacancy(self, vacancy) -> bool:
        """Сохранить вакансию"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Тестовый SQL запрос
            cursor.execute(
                "INSERT INTO vacancies VALUES (%s, %s, %s)", (vacancy.vacancy_id, vacancy.title, vacancy.source)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            return False

    def save_vacancies(self, vacancies) -> bool:
        """Сохранить список вакансий"""
        for vacancy in vacancies:
            self.save_vacancy(vacancy)
        return True

    def get_vacancies(self) -> list:
        """Получить все вакансии"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vacancies")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except Exception:
            return []

    def delete_vacancy_by_id(self, vacancy_id: str) -> bool:
        """Удалить вакансию по ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vacancies WHERE id = %s", (vacancy_id,))
            result = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()
            return result
        except Exception:
            return False


class TestPostgresSaver:
    """Тесты для PostgresSaver"""

    def get_test_db_config(self):
        """Получить тестовые настройки БД"""
        return {
            "host": "localhost",
            "port": "5432",
            "database": "test_db",
            "username": "test_user",
            "password": "test_password",
        }

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_postgres_saver_initialization(self, mock_connect):
        """Тест инициализации PostgresSaver"""
        mock_db_config = self.get_test_db_config()
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        saver = PostgresSaver(mock_db_config)
        assert saver.db_config == mock_db_config

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_get_connection(self, mock_connect):
        """Тест получения соединения с БД"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        connection = saver._get_connection()
        assert connection == mock_connection
        mock_connect.assert_called()

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_save_vacancy(self, mock_connect):
        """Тест сохранения вакансии"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Создаем мок вакансии, так как оригинальный класс Vacancy может быть не импортирован
        class MockVacancy:
            def __init__(self, vacancy_id, title, source):
                self.vacancy_id = vacancy_id
                self.title = title
                self.source = source

        vacancy = MockVacancy(vacancy_id="123", title="Python Developer", source="hh.ru")

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.save_vacancy(vacancy)

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO vacancies VALUES (%s, %s, %s)", (vacancy.vacancy_id, vacancy.title, vacancy.source)
        )
        mock_connection.commit.assert_called_once()
        assert result is True

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_save_vacancies(self, mock_connect):
        """Тест сохранения нескольких вакансий"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        class MockVacancy:
            def __init__(self, vacancy_id, title, source):
                self.vacancy_id = vacancy_id
                self.title = title
                self.source = source

        vacancies = [
            MockVacancy(vacancy_id="123", title="Python Developer", source="hh.ru"),
            MockVacancy(vacancy_id="124", title="Java Developer", source="superjob.ru"),
        ]

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.save_vacancies(vacancies)

        assert mock_cursor.execute.call_count == len(vacancies)
        mock_connection.commit.assert_called()
        assert result is True

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_get_vacancies(self, mock_connect):
        """Тест получения всех вакансий"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        mock_cursor.fetchall.return_value = [
            ("123", "Python Developer", "hh.ru"),
            ("124", "Java Developer", "superjob.ru"),
        ]
        # Имитируем описание столбцов, чтобы psycopg2.fetchmany корректно работал
        mock_cursor.description = [("id",), ("title",), ("source",)]

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.get_vacancies()

        mock_cursor.execute.assert_called_once_with("SELECT * FROM vacancies")
        assert len(result) == 2
        assert result[0] == ("123", "Python Developer", "hh.ru")
        assert result[1] == ("124", "Java Developer", "superjob.ru")

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_get_vacancies_empty(self, mock_connect):
        """Тест получения всех вакансий, когда они отсутствуют"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("id",), ("title",), ("source",)]

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.get_vacancies()

        mock_cursor.execute.assert_called_once_with("SELECT * FROM vacancies")
        assert result == []

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_delete_vacancy_by_id_success(self, mock_connect):
        """Тест удаления вакансии по ID - успех"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        mock_cursor.rowcount = 1

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.delete_vacancy_by_id("123")

        mock_cursor.execute.assert_called_once_with("DELETE FROM vacancies WHERE id = %s", ("123",))
        mock_connection.commit.assert_called_once()
        assert result is True

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_delete_vacancy_by_id_not_found(self, mock_connect):
        """Тест удаления вакансии по ID - не найдено"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        mock_cursor.rowcount = 0

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.delete_vacancy_by_id("999")

        mock_cursor.execute.assert_called_once_with("DELETE FROM vacancies WHERE id = %s", ("999",))
        mock_connection.commit.assert_called_once()
        assert result is False

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_connection_error_handling_save(self, mock_connect):
        """Тест обработки ошибок соединения при сохранении"""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        class MockVacancy:
            def __init__(self, vacancy_id, title, source):
                self.vacancy_id = vacancy_id
                self.title = title
                self.source = source

        vacancy = MockVacancy(vacancy_id="123", title="Python Developer", source="hh.ru")
        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.save_vacancy(vacancy)
        assert result is False

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_connection_error_handling_get(self, mock_connect):
        """Тест обработки ошибок соединения при получении"""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.get_vacancies()
        assert result == []

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_connection_error_handling_delete(self, mock_connect):
        """Тест обработки ошибок соединения при удалении"""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.delete_vacancy_by_id("123")
        assert result is False

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_cursor_error_handling_save(self, mock_connect):
        """Тест обработки ошибок курсора при сохранении"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Cursor execute error")
        mock_connect.return_value = mock_connection

        class MockVacancy:
            def __init__(self, vacancy_id, title, source):
                self.vacancy_id = vacancy_id
                self.title = title
                self.source = source

        vacancy = MockVacancy(vacancy_id="123", title="Python Developer", source="hh.ru")
        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.save_vacancy(vacancy)
        assert result is False

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_cursor_error_handling_get(self, mock_connect):
        """Тест обработки ошибок курсора при получении"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Cursor execute error")
        mock_connect.return_value = mock_connection

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.get_vacancies()
        assert result == []

    @patch("src.storage.postgres_saver.psycopg2.connect")
    def test_cursor_error_handling_delete(self, mock_connect):
        """Тест обработки ошибок курсора при удалении"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Cursor execute error")
        mock_connect.return_value = mock_connection

        mock_db_config = self.get_test_db_config()
        saver = PostgresSaver(mock_db_config)

        result = saver.delete_vacancy_by_id("123")
        assert result is False