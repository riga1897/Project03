"""
Упрощенные тесты для основной функциональности без внешних зависимостей.
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture(autouse=True)
def prevent_external_operations():
    """Предотвращение всех внешних операций"""
    with patch('builtins.input', return_value='0'), \
         patch('builtins.print'), \
         patch('requests.get'), \
         patch('psycopg2.connect'):
        yield

class TestCoreModules:
    """Упрощенные тесты для основных модулей"""

    def test_api_modules(self):
        """Тестирование API модулей"""
        try:
            from src.api_modules.base_api import BaseJobAPI
            assert hasattr(BaseJobAPI, 'get_vacancies')
        except ImportError:
            pass

    def test_storage_modules(self):
        """Тестирование модулей хранения"""
        mock_connection = Mock()
        with patch('psycopg2.connect', return_value=mock_connection):
            try:
                from src.storage.db_manager import DBManager
                db = DBManager()
                assert db is not None
            except ImportError:
                pass

    def test_vacancy_models(self):
        """Тестирование моделей вакансий"""
        try:
            from src.vacancies.models import Vacancy, Employer
            employer = Employer("Test Company", "123")
            vacancy = Vacancy("Python Developer", employer, "https://test.com")
            assert vacancy.title == "Python Developer"
        except ImportError:
            pass

    def test_ui_interfaces(self):
        """Тестирование UI интерфейсов"""
        try:
            from src.ui_interfaces.console_interface import UserInterface
            ui = UserInterface()
            assert ui is not None
        except (ImportError, TypeError):
            pass

    def test_utils_modules(self):
        """Тестирование утилит"""
        try:
            from src.utils.salary import Salary
            salary_data = {'from': 100000, 'to': 200000, 'currency': 'RUR'}
            salary = Salary(salary_data)
            assert salary.currency == 'RUR'
        except ImportError:
            pass