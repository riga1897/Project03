
import pytest
from abc import ABC
from src.storage.abstract_db_manager import AbstractDBManager


class ConcreteDBManager(AbstractDBManager):
    """Конкретная реализация для тестирования"""
    
    def get_companies_and_vacancies_count(self):
        return []
    
    def get_all_vacancies(self):
        return []
    
    def get_avg_salary(self):
        return 0
    
    def get_vacancies_with_higher_salary(self):
        return []
    
    def get_vacancies_with_keyword(self, keyword):
        return []


class TestAbstractDBManager:
    def test_abstract_db_manager_is_abstract(self):
        """Тест что AbstractDBManager является абстрактным классом"""
        assert issubclass(AbstractDBManager, ABC)

    def test_abstract_db_manager_cannot_be_instantiated(self):
        """Тест что AbstractDBManager нельзя инстанцировать напрямую"""
        with pytest.raises(TypeError):
            AbstractDBManager()

    def test_concrete_db_manager_can_be_instantiated(self):
        """Тест что конкретная реализация может быть инстанцирована"""
        manager = ConcreteDBManager()
        assert manager is not None

    def test_concrete_db_manager_methods(self):
        """Тест методов конкретной реализации"""
        manager = ConcreteDBManager()
        assert manager.get_companies_and_vacancies_count() == []
        assert manager.get_all_vacancies() == []
        assert manager.get_avg_salary() == 0
        assert manager.get_vacancies_with_higher_salary() == []
        assert manager.get_vacancies_with_keyword('test') == []

    def test_abstract_methods_exist(self):
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
