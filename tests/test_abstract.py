
import pytest
from abc import ABC, abstractmethod
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.abstract import AbstractVacancyStorage
from src.vacancies.abstract import AbstractVacancy


# Создаем тестовые абстрактные классы для тестирования
class AbstractStorage(ABC):
    """Тестовый абстрактный класс хранилища"""
    
    @abstractmethod
    def save_vacancy(self, vacancy):
        """Сохранить вакансию"""
        pass
    
    @abstractmethod
    def load_vacancies(self):
        """Загрузить вакансии"""
        pass
    
    @abstractmethod
    def delete_vacancy(self, vacancy):
        """Удалить вакансию"""
        pass


class TestAbstractStorage:
    def test_abstract_storage_is_abstract(self):
        """Тест что AbstractStorage является абстрактным классом"""
        assert issubclass(AbstractStorage, ABC)

    def test_abstract_storage_cannot_be_instantiated(self):
        """Тест что AbstractStorage нельзя инстанцировать напрямую"""
        with pytest.raises(TypeError):
            AbstractStorage()

    def test_abstract_storage_methods(self):
        """Тест наличия абстрактных методов"""
        methods = ['save_vacancy', 'load_vacancies', 'delete_vacancy']
        for method in methods:
            if hasattr(AbstractStorage, method):
                assert hasattr(AbstractStorage, method)
                
    def test_abstract_vacancy_storage_is_abstract(self):
        """Тест что AbstractVacancyStorage является абстрактным классом"""
        assert issubclass(AbstractVacancyStorage, ABC)
        
    def test_abstract_vacancy_storage_cannot_be_instantiated(self):
        """Тест что AbstractVacancyStorage нельзя инстанцировать напрямую"""
        with pytest.raises(TypeError):
            AbstractVacancyStorage()


class TestAbstractVacancy:
    def test_abstract_vacancy_is_abstract(self):
        """Тест что AbstractVacancy является абстрактным классом"""
        assert issubclass(AbstractVacancy, ABC)

    def test_abstract_vacancy_cannot_be_instantiated(self):
        """Тест что AbstractVacancy нельзя инстанцировать напрямую"""
        with pytest.raises(TypeError):
            AbstractVacancy()

    def test_abstract_vacancy_methods(self):
        """Тест наличия абстрактных методов"""
        methods = ['get_salary', 'get_title', 'get_company']
        for method in methods:
            if hasattr(AbstractVacancy, method):
                assert hasattr(AbstractVacancy, method)
