
"""
Тесты для абстрактных классов вакансий
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.vacancies.parsers import (
        AbstractVacancy, 
        Vacancy, 
        BaseJobAPI, 
        BaseParser, 
        BaseDBManager
    )
    ABSTRACTIONS_AVAILABLE = True
except ImportError:
    ABSTRACTIONS_AVAILABLE = False


class TestVacancy:
    """Тесты для класса Vacancy"""

    @pytest.fixture
    def vacancy(self):
        """Фикстура для создания тестовой вакансии"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        return Vacancy(
            title="Python Developer",
            salary="100000-150000 руб.",
            url="https://example.com/vacancy/123",
            description="Разработка на Python",
            city="Москва"
        )

    def test_vacancy_creation(self, vacancy):
        """Тест создания вакансии"""
        assert vacancy is not None
        assert isinstance(vacancy, AbstractVacancy)

    def test_get_title(self, vacancy):
        """Тест получения названия вакансии"""
        assert vacancy.get_title() == "Python Developer"

    def test_get_salary(self, vacancy):
        """Тест получения зарплаты"""
        assert vacancy.get_salary() == "100000-150000 руб."

    def test_get_url(self, vacancy):
        """Тест получения URL"""
        assert vacancy.get_url() == "https://example.com/vacancy/123"

    def test_get_description(self, vacancy):
        """Тест получения описания"""
        assert vacancy.get_description() == "Разработка на Python"

    def test_get_city(self, vacancy):
        """Тест получения города"""
        assert vacancy.get_city() == "Москва"


class TestAbstractVacancy:
    """Тесты для абстрактного класса AbstractVacancy"""

    def test_abstract_vacancy_cannot_be_instantiated(self):
        """Тест что абстрактный класс нельзя инстанциировать"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        with pytest.raises(TypeError):
            AbstractVacancy()

    def test_abstract_methods_exist(self):
        """Тест что абстрактные методы определены"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        abstract_methods = AbstractVacancy.__abstractmethods__
        expected_methods = {
            'get_title', 'get_salary', 'get_url', 
            'get_description', 'get_city'
        }
        assert expected_methods.issubset(abstract_methods)


class ConcreteJobAPI(BaseJobAPI):
    """Конкретная реализация BaseJobAPI для тестирования"""
    
    def get_jobs(self, search_query: str):
        return []


class ConcreteParser(BaseParser):
    """Конкретная реализация BaseParser для тестирования"""
    
    def parse(self, html_content: str):
        return []


class ConcreteDBManager(BaseDBManager):
    """Конкретная реализация BaseDBManager для тестирования"""
    
    def save_vacancy(self, vacancy):
        pass
    
    def get_vacancies(self, search_params: dict):
        return []
    
    def delete_vacancy(self, vacancy_id: int):
        pass
    
    def count_vacancies(self) -> int:
        return 0


class TestBaseJobAPI:
    """Тесты для базового класса BaseJobAPI"""

    def test_base_job_api_cannot_be_instantiated(self):
        """Тест что базовый класс нельзя инстанциировать"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        with pytest.raises(TypeError):
            BaseJobAPI()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        api = ConcreteJobAPI()
        result = api.get_jobs("python")
        assert isinstance(result, list)

    def test_abstract_methods_exist(self):
        """Тест что абстрактные методы определены"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        abstract_methods = BaseJobAPI.__abstractmethods__
        assert 'get_jobs' in abstract_methods


class TestBaseParser:
    """Тесты для базового класса BaseParser"""

    def test_base_parser_cannot_be_instantiated(self):
        """Тест что базовый класс нельзя инстанциировать"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        with pytest.raises(TypeError):
            BaseParser()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        parser = ConcreteParser()
        result = parser.parse("<html></html>")
        assert isinstance(result, list)

    def test_abstract_methods_exist(self):
        """Тест что абстрактные методы определены"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        abstract_methods = BaseParser.__abstractmethods__
        assert 'parse' in abstract_methods


class TestBaseDBManager:
    """Тесты для базового класса BaseDBManager"""

    def test_base_db_manager_cannot_be_instantiated(self):
        """Тест что базовый класс нельзя инстанциировать"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        with pytest.raises(TypeError):
            BaseDBManager()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        db_manager = ConcreteDBManager()
        
        # Тестируем все методы
        mock_vacancy = Mock()
        db_manager.save_vacancy(mock_vacancy)
        
        result = db_manager.get_vacancies({})
        assert isinstance(result, list)
        
        db_manager.delete_vacancy(1)
        
        count = db_manager.count_vacancies()
        assert isinstance(count, int)

    def test_abstract_methods_exist(self):
        """Тест что абстрактные методы определены"""
        if not ABSTRACTIONS_AVAILABLE:
            pytest.skip("Abstractions not available")
        
        abstract_methods = BaseDBManager.__abstractmethods__
        expected_methods = {
            'save_vacancy', 'get_vacancies', 
            'delete_vacancy', 'count_vacancies'
        }
        assert expected_methods.issubset(abstract_methods)
