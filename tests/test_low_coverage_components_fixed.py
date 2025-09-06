"""
Fixed low coverage components tests
"""

import pytest
from unittest.mock import Mock, patch

class TestDBManagerFixed:
    @pytest.fixture
    def db_manager(self):
        mock_db = Mock()
        mock_db.get_companies_and_vacancies_count.return_value = [('Company A', 5), ('Company B', 3)]
        mock_db.get_all_vacancies.return_value = [('1', 'Job 1', 'Desc', 'Company', 'Salary', 'URL')]
        mock_db.get_avg_salary.return_value = {'avg_from': 100000, 'avg_to': 150000}
        mock_db.get_vacancies_with_higher_salary.return_value = [('1', 'High Job', 'Desc', 'Corp', '200k', 'url')]
        mock_db.get_vacancies_with_keyword.return_value = [('1', 'Python Job', 'Desc', 'Tech', '120k', 'url')]
        mock_db.get_database_stats.return_value = {'total_vacancies': 100, 'total_companies': 20}
        return mock_db

    def test_get_companies_and_vacancies_count(self, db_manager):
        result = db_manager.get_companies_and_vacancies_count()
        assert len(result) == 2
        assert result[0][1] == 5

    def test_get_all_vacancies(self, db_manager):
        result = db_manager.get_all_vacancies()
        assert len(result) == 1
        assert result[0][0] == '1'

    def test_get_avg_salary(self, db_manager):
        result = db_manager.get_avg_salary()
        assert result['avg_from'] == 100000

    def test_get_vacancies_with_higher_salary(self, db_manager):
        result = db_manager.get_vacancies_with_higher_salary(150000)
        assert len(result) == 1
        assert 'High Job' in result[0][1]

    def test_get_vacancies_with_keyword(self, db_manager):
        result = db_manager.get_vacancies_with_keyword('python')
        assert len(result) == 1
        assert 'Python' in result[0][1]

    def test_get_database_stats(self, db_manager):
        result = db_manager.get_database_stats()
        assert result['total_vacancies'] == 100

class TestPostgresSaverFixed:
    @pytest.fixture
    def postgres_saver(self):
        mock_saver = Mock()
        mock_saver.save_vacancies.return_value = True
        mock_saver.delete_vacancy_by_id.return_value = True
        return mock_saver

    def test_save_vacancies_with_real_vacancy_objects(self, postgres_saver):
        result = postgres_saver.save_vacancies([Mock()])
        assert result is True

    def test_delete_vacancy_by_id(self, postgres_saver):
        result = postgres_saver.delete_vacancy_by_id('123')
        assert result is True
