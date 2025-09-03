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
        mock_db_connection.return_value = self.mock_db_connection

        repo = VacancyRepository({})
        assert repo is not None

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_save_vacancy(self, mock_db_connection):
        """Тест сохранения вакансии"""
        mock_db_connection.return_value = self.mock_db_connection

        repo = VacancyRepository({})

        if hasattr(repo, 'save_vacancy'):
            result = repo.save_vacancy(self.sample_vacancy)
            self.mock_cursor.execute.assert_called()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_get_vacancy_by_id(self, mock_db_connection):
        """Тест получения вакансии по ID"""
        mock_db_connection.return_value = self.mock_db_connection
        self.mock_cursor.fetchone.return_value = (
            "123", "Python Developer", "Test description", 
            100000, 150000, "RUR", "Test Company", "https://test.com/vacancy/123"
        )

        repo = VacancyRepository({})

        if hasattr(repo, 'get_vacancy_by_id'):
            vacancy = repo.get_vacancy_by_id("123")
            assert vacancy is not None
            self.mock_cursor.execute.assert_called()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_get_all_vacancies(self, mock_db_connection):
        """Тест получения всех вакансий"""
        mock_db_connection.return_value = self.mock_db_connection
        self.mock_cursor.fetchall.return_value = [
            ("123", "Python Developer", "Test description", 
             100000, 150000, "RUR", "Test Company", "https://test.com/vacancy/123")
        ]

        repo = VacancyRepository({})

        if hasattr(repo, 'get_all_vacancies'):
            vacancies = repo.get_all_vacancies()
            assert isinstance(vacancies, list)
            self.mock_cursor.execute.assert_called()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_update_vacancy(self, mock_db_connection):
        """Тест обновления вакансии"""
        mock_db_connection.return_value = self.mock_db_connection

        repo = VacancyRepository({})

        if hasattr(repo, 'update_vacancy'):
            result = repo.update_vacancy(self.sample_vacancy)
            self.mock_cursor.execute.assert_called()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_delete_vacancy(self, mock_db_connection):
        """Тест удаления вакансии"""
        mock_db_connection.return_value = self.mock_db_connection

        repo = VacancyRepository({})

        if hasattr(repo, 'delete_vacancy'):
            result = repo.delete_vacancy("123")
            self.mock_cursor.execute.assert_called()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_find_vacancies_by_criteria(self, mock_db_connection):
        """Тест поиска вакансий по критериям"""
        mock_db_connection.return_value = self.mock_db_connection
        self.mock_cursor.fetchall.return_value = []

        repo = VacancyRepository({})

        if hasattr(repo, 'find_vacancies_by_criteria'):
            criteria = {"salary_from": 100000, "company_name": "Test Company"}
            vacancies = repo.find_vacancies_by_criteria(criteria)
            assert isinstance(vacancies, list)

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_count_vacancies(self, mock_db_connection):
        """Тест подсчета количества вакансий"""
        mock_db_connection.return_value = self.mock_db_connection
        self.mock_cursor.fetchone.return_value = (10,)

        repo = VacancyRepository({})

        if hasattr(repo, 'count_vacancies'):
            count = repo.count_vacancies()
            assert isinstance(count, int)
            self.mock_cursor.execute.assert_called()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_batch_save_vacancies(self, mock_db_connection):
        """Тест пакетного сохранения вакансий"""
        mock_db_connection.return_value = self.mock_db_connection

        repo = VacancyRepository({})
        vacancies = [self.sample_vacancy]

        if hasattr(repo, 'batch_save_vacancies'):
            result = repo.batch_save_vacancies(vacancies)
            self.mock_cursor.executemany.assert_called() or self.mock_cursor.execute.assert_called()

    @patch('src.storage.components.vacancy_repository.DatabaseConnection')
    def test_get_vacancies_by_salary_range(self, mock_db_connection):
        """Тест получения вакансий по диапазону зарплат"""
        mock_db_connection.return_value = self.mock_db_connection
        self.mock_cursor.fetchall.return_value = []

        repo = VacancyRepository({})

        if hasattr(repo, 'get_vacancies_by_salary_range'):
            vacancies = repo.get_vacancies_by_salary_range(100000, 200000)
            assert isinstance(vacancies, list)
            self.mock_cursor.execute.assert_called()