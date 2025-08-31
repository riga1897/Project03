
import pytest
from abc import ABC
from src.storage.abstract import AbstractStorage
from src.vacancies.abstract import AbstractVacancy


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
                assert getattr(AbstractStorage, method).__isabstractmethod__


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
                assert getattr(AbstractVacancy, method).__isabstractmethod__
