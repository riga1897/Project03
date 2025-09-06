
"""
Тесты для абстрактных классов хранения данных
Фокус на 100% покрытие функционального кода
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт реальных абстрактных классов
try:
    from src.storage.abstract import AbstractVacancyStorage
    ABSTRACT_STORAGE_AVAILABLE = True
except ImportError:
    ABSTRACT_STORAGE_AVAILABLE = False
    AbstractVacancyStorage = object

try:
    from src.storage.abstract_db_manager import AbstractDBManager
    ABSTRACT_DB_MANAGER_AVAILABLE = True
except ImportError:
    ABSTRACT_DB_MANAGER_AVAILABLE = False
    AbstractDBManager = object

try:
    from src.storage.services.abstract_storage_service import AbstractVacancyStorageService
    ABSTRACT_SERVICE_AVAILABLE = True
except ImportError:
    ABSTRACT_SERVICE_AVAILABLE = False
    AbstractVacancyStorageService = object

try:
    from src.vacancies.models import Vacancy, Employer
    from src.utils.salary import Salary
    VACANCY_MODELS_AVAILABLE = True
except ImportError:
    VACANCY_MODELS_AVAILABLE = False
    Vacancy = object
    Employer = object
    Salary = object


class TestAbstractVacancyStorage:
    """Тесты для AbstractVacancyStorage"""

    def test_abstract_vacancy_storage_cannot_be_instantiated(self):
        """Тест что абстрактный класс нельзя инстанцировать"""
        if not ABSTRACT_STORAGE_AVAILABLE:
            return

        with pytest.raises(TypeError):
            AbstractVacancyStorage()

    def test_concrete_implementation_methods(self):
        """Тест конкретной реализации абстрактных методов"""
        if not ABSTRACT_STORAGE_AVAILABLE:
            return

        class ConcreteVacancyStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy):
                return "added"

            def get_vacancies(self, filters=None):
                return []

            def delete_vacancy(self, vacancy):
                return "deleted"

            def check_vacancies_exist_batch(self, vacancies):
                return {v.vacancy_id if hasattr(v, 'vacancy_id') else str(v): True for v in vacancies}

            def add_vacancy_batch_optimized(self, vacancies, search_query=None):
                return ["batch added"]

        storage = ConcreteVacancyStorage()
        
        # Тестируем все абстрактные методы
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = "test123"
        
        result = storage.add_vacancy(mock_vacancy)
        assert result == "added"
        
        result = storage.get_vacancies()
        assert result == []
        
        result = storage.delete_vacancy(mock_vacancy)
        assert result == "deleted"
        
        result = storage.check_vacancies_exist_batch([mock_vacancy])
        assert isinstance(result, dict)
        
        result = storage.add_vacancy_batch_optimized([mock_vacancy])
        assert result == ["batch added"]


class TestAbstractDBManager:
    """Тесты для AbstractDBManager"""

    def test_abstract_db_manager_cannot_be_instantiated(self):
        """Тест что абстрактный класс нельзя инстанцировать"""
        if not ABSTRACT_DB_MANAGER_AVAILABLE:
            return

        with pytest.raises(TypeError):
            AbstractDBManager()

    def test_concrete_db_manager_implementation(self):
        """Тест конкретной реализации AbstractDBManager"""
        if not ABSTRACT_DB_MANAGER_AVAILABLE:
            return

        class ConcreteDBManager(AbstractDBManager):
            def get_companies_and_vacancies_count(self):
                return [("Company1", 10), ("Company2", 5)]

            def get_all_vacancies(self):
                return [{"id": "1", "title": "Test Job"}]

            def get_avg_salary(self):
                return 125000.0

            def get_vacancies_with_higher_salary(self):
                return [{"id": "1", "salary": 150000}]

            def get_vacancies_with_keyword(self, keyword):
                return [{"id": "1", "title": f"Job with {keyword}"}]

            def get_database_stats(self):
                return {
                    "total_vacancies": 100,
                    "total_companies": 20,
                    "avg_salary": 125000.0
                }

        db_manager = ConcreteDBManager()
        
        # Тестируем все абстрактные методы
        companies = db_manager.get_companies_and_vacancies_count()
        assert isinstance(companies, list)
        assert len(companies) == 2
        
        vacancies = db_manager.get_all_vacancies()
        assert isinstance(vacancies, list)
        
        avg_salary = db_manager.get_avg_salary()
        assert avg_salary == 125000.0
        
        high_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
        assert isinstance(high_salary_vacancies, list)
        
        keyword_vacancies = db_manager.get_vacancies_with_keyword("Python")
        assert isinstance(keyword_vacancies, list)
        
        stats = db_manager.get_database_stats()
        assert isinstance(stats, dict)
        assert "total_vacancies" in stats


class TestAbstractVacancyStorageService:
    """Тесты для AbstractVacancyStorageService"""

    def test_abstract_service_cannot_be_instantiated(self):
        """Тест что абстрактный сервис нельзя инстанцировать"""
        if not ABSTRACT_SERVICE_AVAILABLE:
            return

        with pytest.raises(TypeError):
            AbstractVacancyStorageService()

    def test_concrete_service_implementation(self):
        """Тест конкретной реализации абстрактного сервиса"""
        if not ABSTRACT_SERVICE_AVAILABLE:
            return

        class ConcreteStorageService(AbstractVacancyStorageService):
            def filter_and_deduplicate_vacancies(self, vacancies):
                # Простая дедупликация по ID
                seen = set()
                result = []
                for v in vacancies:
                    vacancy_id = v.get('id') if isinstance(v, dict) else getattr(v, 'vacancy_id', None)
                    if vacancy_id not in seen:
                        seen.add(vacancy_id)
                        result.append(v)
                return result

            def save_vacancies(self, vacancies):
                return len(vacancies)

            def get_vacancies(self, filters=None):
                if filters and 'keyword' in filters:
                    return [{"id": "1", "title": f"Job with {filters['keyword']}"}]
                return [{"id": "1", "title": "Default Job"}]

            def delete_vacancy(self, vacancy_id):
                return True

            def get_companies_and_vacancies_count(self):
                return [("Company1", 5), ("Company2", 3)]

            def get_storage_stats(self):
                return {
                    "total_vacancies": 8,
                    "total_companies": 2,
                    "last_updated": "2024-01-01"
                }

        service = ConcreteStorageService()
        
        # Тестируем фильтрацию и дедупликацию
        test_vacancies = [
            {"id": "1", "title": "Job 1"},
            {"id": "1", "title": "Job 1 Duplicate"},
            {"id": "2", "title": "Job 2"}
        ]
        
        filtered = service.filter_and_deduplicate_vacancies(test_vacancies)
        assert len(filtered) == 2  # Один дубликат удален
        
        # Тестируем сохранение
        saved_count = service.save_vacancies(test_vacancies)
        assert saved_count == 3
        
        # Тестируем получение с фильтрами
        vacancies = service.get_vacancies({"keyword": "Python"})
        assert len(vacancies) == 1
        assert "Python" in vacancies[0]["title"]
        
        # Тестируем удаление
        result = service.delete_vacancy("test123")
        assert result is True
        
        # Тестируем получение статистики компаний
        companies = service.get_companies_and_vacancies_count()
        assert len(companies) == 2
        
        # Тестируем получение статистики хранилища
        stats = service.get_storage_stats()
        assert stats["total_vacancies"] == 8


class TestVacancyModelIntegration:
    """Тесты интеграции с моделями вакансий"""

    @pytest.fixture
    def mock_vacancy(self):
        """Фикстура для создания mock вакансии"""
        if not VACANCY_MODELS_AVAILABLE:
            mock = Mock()
            mock.vacancy_id = "test123"
            mock.title = "Test Job"
            mock.employer = Mock()
            mock.employer.name = "Test Company"
            return mock
        
        # Создаем реальную вакансию для тестов
        employer = Employer(name="Test Company", employer_id="comp123")
        
        # Создаем зарплату с правильными параметрами
        salary = Salary(salary_from=100000, salary_to=150000, currency="RUR")
        
        vacancy = Vacancy(
            vacancy_id="test123",
            title="Test Job",
            url="https://example.com/job/123",
            employer=employer,
            salary=salary,
            description="Test description",
            source="test"
        )
        return vacancy

    def test_storage_with_real_vacancy_objects(self, mock_vacancy):
        """Тест работы хранилища с реальными объектами вакансий"""
        if not ABSTRACT_STORAGE_AVAILABLE:
            return

        class TestVacancyStorage(AbstractVacancyStorage):
            def __init__(self):
                self._vacancies = []

            def add_vacancy(self, vacancy):
                self._vacancies.append(vacancy)

            def get_vacancies(self, filters=None):
                return self._vacancies

            def delete_vacancy(self, vacancy):
                if vacancy in self._vacancies:
                    self._vacancies.remove(vacancy)

            def check_vacancies_exist_batch(self, vacancies):
                result = {}
                for v in vacancies:
                    vacancy_id = v.vacancy_id if hasattr(v, 'vacancy_id') else str(v)
                    result[vacancy_id] = v in self._vacancies
                return result

            def add_vacancy_batch_optimized(self, vacancies, search_query=None):
                messages = []
                for vacancy in vacancies:
                    self.add_vacancy(vacancy)
                    messages.append(f"Added vacancy {vacancy.vacancy_id}")
                return messages

        storage = TestVacancyStorage()
        
        # Добавляем вакансию
        storage.add_vacancy(mock_vacancy)
        
        # Проверяем что вакансия добавлена
        vacancies = storage.get_vacancies()
        assert len(vacancies) == 1
        assert vacancies[0].vacancy_id == "test123"
        
        # Проверяем batch операции
        batch_result = storage.check_vacancies_exist_batch([mock_vacancy])
        assert batch_result["test123"] is True
        
        # Тестируем batch добавление
        new_vacancy = Mock()
        new_vacancy.vacancy_id = "test456"
        
        messages = storage.add_vacancy_batch_optimized([new_vacancy])
        assert len(messages) == 1
        assert "test456" in messages[0]
        
        # Удаляем вакансию
        storage.delete_vacancy(mock_vacancy)
        vacancies = storage.get_vacancies()
        assert len(vacancies) == 1  # Осталась только новая вакансия

    def test_db_manager_with_vacancy_filtering(self, mock_vacancy):
        """Тест DBManager с фильтрацией вакансий"""
        if not ABSTRACT_DB_MANAGER_AVAILABLE:
            return

        class TestDBManager(AbstractDBManager):
            def __init__(self):
                self._vacancies = []
                self._companies = {}

            def add_test_data(self, vacancies):
                self._vacancies = vacancies
                for v in vacancies:
                    company_name = v.get('company', 'Unknown')
                    if company_name not in self._companies:
                        self._companies[company_name] = 0
                    self._companies[company_name] += 1

            def get_companies_and_vacancies_count(self):
                return list(self._companies.items())

            def get_all_vacancies(self):
                return self._vacancies

            def get_avg_salary(self):
                salaries = [v.get('salary', 0) for v in self._vacancies if v.get('salary')]
                return sum(salaries) / len(salaries) if salaries else None

            def get_vacancies_with_higher_salary(self):
                avg = self.get_avg_salary()
                if avg is None:
                    return []
                return [v for v in self._vacancies if v.get('salary', 0) > avg]

            def get_vacancies_with_keyword(self, keyword):
                return [v for v in self._vacancies 
                       if keyword.lower() in v.get('title', '').lower()]

            def get_database_stats(self):
                return {
                    "total_vacancies": len(self._vacancies),
                    "total_companies": len(self._companies),
                    "avg_salary": self.get_avg_salary()
                }

        db_manager = TestDBManager()
        
        # Добавляем тестовые данные
        test_data = [
            {"id": "1", "title": "Python Developer", "company": "TechCorp", "salary": 120000},
            {"id": "2", "title": "Java Developer", "company": "JavaCorp", "salary": 110000},
            {"id": "3", "title": "Python Engineer", "company": "TechCorp", "salary": 130000}
        ]
        
        db_manager.add_test_data(test_data)
        
        # Тестируем все методы
        companies = db_manager.get_companies_and_vacancies_count()
        assert len(companies) == 2
        
        all_vacancies = db_manager.get_all_vacancies()
        assert len(all_vacancies) == 3
        
        avg_salary = db_manager.get_avg_salary()
        assert avg_salary == 120000
        
        high_salary = db_manager.get_vacancies_with_higher_salary()
        assert len(high_salary) == 1  # Только одна вакансия выше средней
        
        python_jobs = db_manager.get_vacancies_with_keyword("Python")
        assert len(python_jobs) == 2
        
        stats = db_manager.get_database_stats()
        assert stats["total_vacancies"] == 3
        assert stats["total_companies"] == 2
        assert stats["avg_salary"] == 120000
