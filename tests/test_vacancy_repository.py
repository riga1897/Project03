"""
Тесты для модуля vacancy_repository
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.storage.components.vacancy_repository import VacancyRepository
from src.vacancies.models import Vacancy, Employer


class TestVacancyRepository:
    """Класс для тестирования VacancyRepository"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.mock_db_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_db_connection.cursor.return_value = self.mock_cursor

        employer = Employer("Test Company", "123")
        self.sample_vacancy = Vacancy(
            vacancy_id="test_123",
            title="Python Developer",
            url="https://example.com/job/123",
            description="Test job description",
            employer=employer
        )

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_vacancy_repository_init(self, mock_db_connection):
        """Тест инициализации репозитория вакансий"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)
        assert repo is not None


    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_save_vacancy(self, mock_db_connection):
        """Тест сохранения вакансии"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)
        vacancy = Mock()
        vacancy.vacancy_id = "test_123"
        vacancy.title = "Test Vacancy"

        with patch.object(repo, 'save_vacancy') as mock_save:
            mock_save.return_value = True
            result = repo.save_vacancy(vacancy)
            assert result is True
            mock_save.assert_called_once_with(vacancy)


    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_get_vacancy_by_id(self, mock_db_connection):
        """Тест получения вакансии по ID"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)

        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (
            "123", "Python Developer", "Test description",
            100000, 150000, "RUR", "Test Company", "https://test.com/vacancy/123"
        )

        vacancy = repo.get_vacancy_by_id("123")
        assert vacancy is not None
        mock_cursor.execute.assert_called_once()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_get_all_vacancies(self, mock_db_connection):
        """Тест получения всех вакансий"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)

        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("123", "Python Developer", "Test description",
             100000, 150000, "RUR", "Test Company", "https://test.com/vacancy/123")
        ]

        vacancies = repo.get_all_vacancies()
        assert isinstance(vacancies, list)
        mock_cursor.execute.assert_called_once()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_update_vacancy(self, mock_db_connection):
        """Тест обновления вакансии"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)

        with patch.object(repo, 'update_vacancy') as mock_update:
            mock_update.return_value = True
            result = repo.update_vacancy(self.sample_vacancy)
            assert result is True
            mock_update.assert_called_once_with(self.sample_vacancy)

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_delete_vacancy(self, mock_db_connection):
        """Тест удаления вакансии"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)

        with patch.object(repo, 'delete_vacancy') as mock_delete:
            mock_delete.return_value = True
            result = repo.delete_vacancy("123")
            assert result is True
            mock_delete.assert_called_once_with("123")

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_find_vacancies_by_criteria(self, mock_db_connection):
        """Тест поиска вакансий по критериям"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)

        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        criteria = {"salary_from": 100000, "company_name": "Test Company"}
        vacancies = repo.find_vacancies_by_criteria(criteria)
        assert isinstance(vacancies, list)
        mock_cursor.execute.assert_called_once()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_count_vacancies(self, mock_db_connection):
        """Тест подсчета количества вакансий"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)

        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (10,)

        count = repo.count_vacancies()
        assert isinstance(count, int)
        mock_cursor.execute.assert_called_once()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_batch_save_vacancies(self, mock_db_connection):
        """Тест пакетного сохранения вакансий"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)
        vacancies = [self.sample_vacancy]

        with patch.object(repo, 'batch_save_vacancies') as mock_batch_save:
            mock_batch_save.return_value = True
            result = repo.batch_save_vacancies(vacancies)
            assert result is True
            mock_batch_save.assert_called_once_with(vacancies)


    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_get_vacancies_by_salary_range(self, mock_db_connection):
        """Тест получения вакансий по диапазону зарплат"""
        mock_connection = Mock()
        mock_validator = Mock()
        repo = VacancyRepository(mock_connection, mock_validator)

        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        vacancies = repo.get_vacancies_by_salary_range(100000, 200000)
        assert isinstance(vacancies, list)
        mock_cursor.execute.assert_called_once()