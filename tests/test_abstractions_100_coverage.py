"""
Тесты для абстрактных классов - базовый уровень архитектуры
100% покрытие всех абстрактных модулей
"""

import os
import sys
from unittest.mock import Mock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vacancies.abstract import AbstractVacancy
from src.vacancies.abstract_models import (
    AbstractEmployer, AbstractExperience, AbstractEmployment, AbstractSalary
)
from src.storage.abstract import AbstractVacancyStorage
from src.storage.abstract_db_manager import AbstractDBManager
from src.api_modules.base_api import BaseJobAPI
from src.utils.abstract_filter import AbstractDataFilter


class TestAbstractVacancy:
    """Тесты для AbstractVacancy - базовый абстрактный класс вакансии"""

    def test_cannot_instantiate_directly(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractVacancy()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        class ConcreteVacancy(AbstractVacancy):
            def __init__(self):
                pass
                
            def to_dict(self):
                return {"test": "data"}
            
            @classmethod
            def from_dict(cls, data):
                return cls()
        
        # Создание экземпляра должно работать
        vacancy = ConcreteVacancy()
        assert vacancy.to_dict() == {"test": "data"}
        
        # Создание из словаря должно работать
        from_dict_vacancy = ConcreteVacancy.from_dict({"some": "data"})
        assert isinstance(from_dict_vacancy, ConcreteVacancy)


class TestAbstractEmployer:
    """Тесты для AbstractEmployer"""

    def test_cannot_instantiate_directly(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractEmployer()

    def test_concrete_implementation_all_methods(self):
        """Тест что конкретная реализация реализует все методы"""
        class ConcreteEmployer(AbstractEmployer):
            def get_name(self):
                return "Test Company"
            
            def get_id(self):
                return "123"
            
            def is_trusted(self):
                return True
            
            def get_url(self):
                return "http://test.com"
            
            def to_dict(self):
                return {"name": "Test Company"}
            
            @classmethod
            def from_dict(cls, data):
                return cls()
        
        employer = ConcreteEmployer()
        assert employer.get_name() == "Test Company"
        assert employer.get_id() == "123"
        assert employer.is_trusted() == True
        assert employer.get_url() == "http://test.com"
        assert employer.to_dict() == {"name": "Test Company"}
        
        from_dict_employer = ConcreteEmployer.from_dict({})
        assert isinstance(from_dict_employer, ConcreteEmployer)


class TestAbstractExperience:
    """Тесты для AbstractExperience"""

    def test_cannot_instantiate_directly(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractExperience()

    def test_concrete_implementation_all_methods(self):
        """Тест конкретной реализации всех методов"""
        class ConcreteExperience(AbstractExperience):
            def get_name(self):
                return "От 1 года до 3 лет"
            
            def get_id(self):
                return "between1And3"
            
            def to_dict(self):
                return {"id": "between1And3", "name": "От 1 года до 3 лет"}
            
            @classmethod
            def from_dict(cls, data):
                return cls()
            
            @classmethod
            def from_string(cls, data):
                return cls()
        
        experience = ConcreteExperience()
        assert experience.get_name() == "От 1 года до 3 лет"
        assert experience.get_id() == "between1And3"
        assert experience.to_dict() == {"id": "between1And3", "name": "От 1 года до 3 лет"}
        
        from_dict_exp = ConcreteExperience.from_dict({})
        assert isinstance(from_dict_exp, ConcreteExperience)


class TestAbstractEmployment:
    """Тесты для AbstractEmployment"""

    def test_cannot_instantiate_directly(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractEmployment()

    def test_concrete_implementation_all_methods(self):
        """Тест конкретной реализации всех методов"""
        class ConcreteEmployment(AbstractEmployment):
            def get_name(self):
                return "Полная занятость"
            
            def get_id(self):
                return "full"
            
            def to_dict(self):
                return {"id": "full", "name": "Полная занятость"}
            
            @classmethod
            def from_dict(cls, data):
                return cls()
            
            @classmethod
            def from_string(cls, data):
                return cls()
        
        employment = ConcreteEmployment()
        assert employment.get_name() == "Полная занятость"
        assert employment.get_id() == "full"
        assert employment.to_dict() == {"id": "full", "name": "Полная занятость"}
        
        from_dict_emp = ConcreteEmployment.from_dict({})
        assert isinstance(from_dict_emp, ConcreteEmployment)


class TestAbstractSalary:
    """Тесты для AbstractSalary"""

    def test_cannot_instantiate_directly(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractSalary()

    def test_concrete_implementation_all_methods(self):
        """Тест конкретной реализации всех методов"""
        class ConcreteSalary(AbstractSalary):
            def get_from(self):
                return 100000
            
            def get_to(self):
                return 150000
            
            def get_currency(self):
                return "RUR"
            
            def is_gross(self):
                return True
            
            def format_salary(self):
                return "100 000 - 150 000 RUR"
            
            def to_dict(self):
                return {"from": 100000, "to": 150000, "currency": "RUR"}
            
            @classmethod
            def from_dict(cls, data):
                return cls()
            
            def compare(self, other):
                return 0
            
            def get_from_amount(self):
                return 100000
            
            def get_to_amount(self):
                return 150000
            
            def get_average(self):
                return 125000
            
            def is_specified(self):
                return True
        
        salary = ConcreteSalary()
        assert salary.get_from() == 100000
        assert salary.get_to() == 150000
        assert salary.get_currency() == "RUR"
        assert salary.is_gross() == True
        assert salary.format_salary() == "100 000 - 150 000 RUR"
        assert salary.to_dict() == {"from": 100000, "to": 150000, "currency": "RUR"}
        assert salary.compare(None) == 0
        
        from_dict_salary = ConcreteSalary.from_dict({})
        assert isinstance(from_dict_salary, ConcreteSalary)


class TestAbstractVacancyStorage:
    """Тесты для AbstractVacancyStorage"""

    def test_cannot_instantiate_directly(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractVacancyStorage()

    def test_concrete_implementation_all_methods(self):
        """Тест конкретной реализации всех методов"""
        class ConcreteStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy):
                pass
            
            def get_vacancies(self, filters=None):
                return []
            
            def delete_vacancy(self, vacancy):
                pass
            
            def check_vacancies_exist_batch(self, vacancies):
                return {}
            
            def add_vacancy_batch_optimized(self, vacancies, search_query=None):
                return []
        
        storage = ConcreteStorage()
        
        # Тестируем все методы
        mock_vacancy = Mock()
        storage.add_vacancy(mock_vacancy)
        
        result = storage.get_vacancies()
        assert result == []
        
        result_with_filters = storage.get_vacancies({"test": "filter"})
        assert result_with_filters == []
        
        storage.delete_vacancy(mock_vacancy)
        
        batch_result = storage.check_vacancies_exist_batch([mock_vacancy])
        assert batch_result == {}
        
        batch_add_result = storage.add_vacancy_batch_optimized([mock_vacancy])
        assert batch_add_result == []
        
        batch_add_with_query = storage.add_vacancy_batch_optimized([mock_vacancy], "python")
        assert batch_add_with_query == []


class TestAbstractDBManager:
    """Тесты для AbstractDBManager"""

    def test_cannot_instantiate_directly(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractDBManager()

    def test_concrete_implementation_basic_methods(self):
        """Тест конкретной реализации основных методов"""
        class ConcreteDBManager(AbstractDBManager):
            def connect(self):
                return Mock()
            
            def disconnect(self):
                pass
            
            def execute_query(self, query, params=None):
                return []
            
            def get_companies_and_vacancies_count(self):
                return [("Company A", 5), ("Company B", 3)]
            
            def get_all_vacancies(self):
                return [{"id": "1", "title": "Test"}]
            
            def get_avg_salary(self):
                return 120000.0
            
            def get_vacancies_with_higher_salary(self):
                return [{"id": "2", "salary": 150000}]
            
            def get_vacancies_with_keyword(self, keyword):
                return [{"id": "3", "title": f"Job with {keyword}"}]
            
            def get_database_stats(self):
                return {"total_vacancies": 10, "total_companies": 2}
        
        db_manager = ConcreteDBManager()
        
        # Тестируем методы
        connection = db_manager.connect()
        assert connection is not None
        
        db_manager.disconnect()
        
        result = db_manager.execute_query("SELECT * FROM test")
        assert result == []
        
        result_with_params = db_manager.execute_query("SELECT * FROM test WHERE id = ?", [1])
        assert result_with_params == []


class TestBaseJobAPI:
    """Тесты для BaseJobAPI"""

    def test_cannot_instantiate_directly(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            BaseJobAPI()

    def test_concrete_implementation_all_methods(self):
        """Тест конкретной реализации всех методов"""
        class ConcreteAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return [{"title": "Test Job", "url": "http://test.com"}]
            
            def _validate_vacancy(self, vacancy):
                return "title" in vacancy and "url" in vacancy
        
        api = ConcreteAPI()
        
        # Тестируем методы
        vacancies = api.get_vacancies("python")
        assert len(vacancies) == 1
        assert vacancies[0]["title"] == "Test Job"
        
        vacancies_with_kwargs = api.get_vacancies("python", salary=100000)
        assert len(vacancies_with_kwargs) == 1
        
        # Тестируем валидацию
        valid_vacancy = {"title": "Test", "url": "http://test.com"}
        assert api._validate_vacancy(valid_vacancy) == True
        
        invalid_vacancy = {"title": "Test"}
        assert api._validate_vacancy(invalid_vacancy) == False
        
        # Тестируем наследованный метод clear_cache
        api.clear_cache("test")  # Не должно падать


class TestAbstractDataFilter:
    """Тесты для AbstractDataFilter"""

    def test_cannot_instantiate_directly(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractDataFilter()

    def test_concrete_implementation_all_methods(self):
        """Тест конкретной реализации всех методов"""
        class ConcreteDataFilter(AbstractDataFilter):
            def filter_by_company(self, data, companies):
                return [item for item in data if any(company.lower() in str(item).lower() for company in companies)]
            
            def filter_by_salary(self, data, min_salary=None, max_salary=None):
                filtered = []
                for item in data:
                    salary = item.get('salary', {})
                    if isinstance(salary, dict):
                        salary_from = salary.get('from', 0)
                        if min_salary and salary_from < min_salary:
                            continue
                        if max_salary and salary_from > max_salary:
                            continue
                    filtered.append(item)
                return filtered
            
            def filter_by_location(self, data, locations):
                return [item for item in data if any(loc.lower() in str(item).lower() for loc in locations)]
            
            def filter_by_experience(self, data, experience_levels):
                return [item for item in data if any(exp.lower() in str(item).lower() for exp in experience_levels)]
        
        filter_obj = ConcreteDataFilter()
        
        # Тестируем фильтрацию по компаниям
        test_data = [
            {"employer": {"name": "Yandex"}, "title": "Python Dev"},
            {"employer": {"name": "Google"}, "title": "Java Dev"},
            {"employer": {"name": "Microsoft"}, "title": "C# Dev"}
        ]
        filtered = filter_obj.filter_by_company(test_data, ["yandex", "google"])
        assert len(filtered) == 2
        
        # Тестируем фильтрацию по зарплате
        salary_data = [
            {"title": "Junior", "salary": {"from": 80000}},
            {"title": "Middle", "salary": {"from": 120000}},
            {"title": "Senior", "salary": {"from": 180000}}
        ]
        filtered_salary = filter_obj.filter_by_salary(salary_data, min_salary=100000, max_salary=150000)
        assert len(filtered_salary) == 1


class TestAbstractClassIntegration:
    """Интеграционные тесты для взаимодействия абстрактных классов"""

    def test_abstract_classes_composition(self):
        """Тест композиции абстрактных классов"""
        # Создаем конкретные реализации всех абстрактных классов
        class TestVacancy(AbstractVacancy):
            def __init__(self):
                self.employer = None
                self.salary = None
                
            def to_dict(self):
                return {"title": "Test"}
            
            @classmethod
            def from_dict(cls, data):
                return cls()
        
        class TestEmployer(AbstractEmployer):
            def get_name(self): return "Test Company"
            def get_id(self): return "123"
            def is_trusted(self): return True
            def get_url(self): return "http://test.com"
            def to_dict(self): return {"name": "Test Company"}
            @classmethod
            def from_dict(cls, data): return cls()
        
        class TestSalary(AbstractSalary):
            def get_from(self): return 100000
            def get_to(self): return 150000
            def get_currency(self): return "RUR"
            def is_gross(self): return True
            def format_salary(self): return "100k-150k RUR"
            def to_dict(self): return {"from": 100000, "to": 150000}
            @classmethod
            def from_dict(cls, data): return cls()
            def compare(self, other): return 0
            def get_from_amount(self): return 100000
            def get_to_amount(self): return 150000
            def get_average(self): return 125000
            def is_specified(self): return True
        
        # Тестируем композицию
        vacancy = TestVacancy()
        employer = TestEmployer()
        salary = TestSalary()
        
        vacancy.employer = employer
        vacancy.salary = salary
        
        # Проверяем что все работает вместе
        assert vacancy.employer.get_name() == "Test Company"
        assert vacancy.salary.get_from() == 100000
        assert vacancy.to_dict() == {"title": "Test"}

    def test_inheritance_hierarchy_validation(self):
        """Тест валидации иерархии наследования"""
        from abc import ABC
        
        # Проверяем что все абстрактные классы наследуются от ABC
        assert issubclass(AbstractVacancy, ABC)
        assert issubclass(AbstractEmployer, ABC)
        assert issubclass(AbstractExperience, ABC)
        assert issubclass(AbstractEmployment, ABC)
        assert issubclass(AbstractSalary, ABC)
        assert issubclass(AbstractVacancyStorage, ABC)
        assert issubclass(AbstractDBManager, ABC)
        assert issubclass(BaseJobAPI, ABC)
        assert issubclass(AbstractDataFilter, ABC)