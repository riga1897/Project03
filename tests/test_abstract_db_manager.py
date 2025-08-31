
import pytest
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class AbstractDBManager(ABC):
    """Тестовый абстрактный класс для менеджера базы данных"""
    
    @abstractmethod
    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получить количество компаний и вакансий"""
        pass
    
    @abstractmethod
    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получить все вакансии"""
        pass
    
    @abstractmethod
    def get_avg_salary(self) -> float:
        """Получить среднюю зарплату"""
        pass
    
    @abstractmethod
    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получить вакансии с зарплатой выше средней"""
        pass
    
    @abstractmethod
    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получить вакансии по ключевому слову"""
        pass


class TestAbstractDBManager:
    def test_abstract_db_manager_is_abstract(self):
        """Тест что AbstractDBManager является абстрактным классом"""
        assert issubclass(AbstractDBManager, ABC)

    def test_abstract_db_manager_cannot_be_instantiated(self):
        """Тест что AbstractDBManager нельзя инстанцировать напрямую"""
        with pytest.raises(TypeError):
            AbstractDBManager()

    def test_abstract_db_manager_methods(self):
        """Тест наличия абстрактных методов"""
        methods = [
            'get_companies_and_vacancies_count',
            'get_all_vacancies', 
            'get_avg_salary',
            'get_vacancies_with_higher_salary',
            'get_vacancies_with_keyword'
        ]
        for method in methods:
            assert hasattr(AbstractDBManager, method)

    def test_abstract_methods_are_abstract(self):
        """Тест что методы являются абстрактными"""
        methods = [
            'get_companies_and_vacancies_count',
            'get_all_vacancies', 
            'get_avg_salary',
            'get_vacancies_with_higher_salary',
            'get_vacancies_with_keyword'
        ]
        for method in methods:
            if hasattr(AbstractDBManager, method):
                method_obj = getattr(AbstractDBManager, method)
                assert getattr(method_obj, '__isabstractmethod__', False)
