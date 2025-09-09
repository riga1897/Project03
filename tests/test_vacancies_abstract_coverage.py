#!/usr/bin/env python3
"""
Тесты модуля src/vacancies/abstract.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций 
- ТОЛЬКО мокированные данные
- 100% покрытие всех строк кода
- Импорт из реального кода для покрытия

Модуль содержит:
- 1 абстрактный класс: AbstractVacancy (ABC)
- 2 абстрактных метода: to_dict, from_dict (без __init__)
- 25 строк кода, простая структура без сложной логики
"""

import pytest
from abc import ABC, abstractmethod
from typing import Any, Dict

# Импорт из реального кода для покрытия
from src.vacancies.abstract import AbstractVacancy


class TestAbstractVacancy:
    """100% покрытие класса AbstractVacancy"""

    def test_class_exists(self):
        """Покрытие: существование класса"""
        assert AbstractVacancy is not None
        assert issubclass(AbstractVacancy, ABC)

    def test_class_is_abstract(self):
        """Покрытие: класс является абстрактным"""
        assert getattr(AbstractVacancy, '__abstractmethods__') is not None
        # Должно быть 2 абстрактных метода (без __init__)
        abstract_methods = AbstractVacancy.__abstractmethods__
        assert len(abstract_methods) == 2
        assert 'to_dict' in abstract_methods  
        assert 'from_dict' in abstract_methods

    def test_cannot_instantiate_abstract_class(self):
        """Покрытие: нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError) as exc_info:
            AbstractVacancy()
        
        error_message = str(exc_info.value)
        assert "Can't instantiate abstract class AbstractVacancy" in error_message

    def test_abstract_init_method_signature(self):
        """Покрытие: метод __init__ не является абстрактным"""
        assert hasattr(AbstractVacancy, '__init__')
        assert callable(AbstractVacancy.__init__)
        
        # Проверяем что метод НЕ помечен как абстрактный (Pydantic BaseModel)
        init_is_abstract = getattr(AbstractVacancy.__init__, '__isabstractmethod__', False)
        assert init_is_abstract is False

    def test_abstract_to_dict_method_signature(self):
        """Покрытие: сигнатура абстрактного метода to_dict"""
        assert hasattr(AbstractVacancy, 'to_dict')
        assert callable(AbstractVacancy.to_dict)
        
        # Проверяем что метод помечен как абстрактный
        assert hasattr(AbstractVacancy.to_dict, '__isabstractmethod__')
        assert AbstractVacancy.to_dict.__isabstractmethod__ is True

    def test_abstract_from_dict_method_signature(self):
        """Покрытие: сигнатура абстрактного метода from_dict"""
        assert hasattr(AbstractVacancy, 'from_dict')
        assert callable(AbstractVacancy.from_dict)
        
        # Проверяем что метод помечен как абстрактный
        assert hasattr(AbstractVacancy.from_dict, '__isabstractmethod__')
        assert AbstractVacancy.from_dict.__isabstractmethod__ is True

    def test_from_dict_is_classmethod(self):
        """Покрытие: from_dict является classmethod"""
        # Проверяем что from_dict это classmethod по атрибуту __func__
        from_dict_method = AbstractVacancy.__dict__.get('from_dict')
        assert from_dict_method is not None
        # classmethod содержит __func__ атрибут
        assert hasattr(from_dict_method, '__func__') or isinstance(from_dict_method, classmethod)

    def test_abstract_methods_docstrings(self):
        """Покрытие: проверка документации абстрактных методов"""
        # Проверяем наличие докстрингов
        init_doc = AbstractVacancy.__init__.__doc__
        to_dict_doc = AbstractVacancy.to_dict.__doc__ 
        from_dict_doc = AbstractVacancy.from_dict.__doc__
        
        assert init_doc is not None
        # __init__ наследуется от BaseModel, документация может отличаться
        
        assert to_dict_doc is not None
        assert "Преобразует вакансию в словарь" in to_dict_doc
        
        assert from_dict_doc is not None
        assert "Создает объект вакансии из словаря" in from_dict_doc
        assert ":param data: Словарь с данными вакансии" in from_dict_doc
        assert ":return: Объект вакансии" in from_dict_doc


class TestConcreteImplementation:
    """Тестирование через конкретную реализацию для покрытия абстрактных методов"""

    def test_concrete_implementation_works(self):
        """Покрытие: конкретная реализация должна работать"""
        
        # Создаем конкретную реализацию для тестирования
        class ConcreteVacancy(AbstractVacancy):
            """Конкретная реализация для тестирования"""
            
            def __init__(self):
                """Конкретная реализация инициализации"""
                self.id = "test_id"
                self.title = "Test Vacancy"
            
            def to_dict(self) -> Dict[str, Any]:
                """Конкретная реализация преобразования в словарь"""
                return {
                    "id": self.id,
                    "title": self.title
                }
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "ConcreteVacancy":
                """Конкретная реализация создания из словаря"""
                instance = cls()
                instance.id = data.get("id", "default_id")
                instance.title = data.get("title", "Default Title")
                return instance
        
        # Проверяем что конкретная реализация работает
        vacancy = ConcreteVacancy()
        assert vacancy.id == "test_id"
        assert vacancy.title == "Test Vacancy"
        
        # Проверяем to_dict
        vacancy_dict = vacancy.to_dict()
        expected_dict = {"id": "test_id", "title": "Test Vacancy"}
        assert vacancy_dict == expected_dict
        
        # Проверяем from_dict
        data = {"id": "new_id", "title": "New Vacancy"}
        new_vacancy = ConcreteVacancy.from_dict(data)
        assert new_vacancy.id == "new_id"
        assert new_vacancy.title == "New Vacancy"
        
        # Проверяем что это экземпляр AbstractVacancy
        assert isinstance(new_vacancy, AbstractVacancy)
        assert isinstance(new_vacancy, ConcreteVacancy)

    def test_concrete_implementation_with_empty_data(self):
        """Покрытие: конкретная реализация с пустыми данными"""
        
        class ConcreteVacancy(AbstractVacancy):
            def __init__(self):
                self.data = {}
            
            def to_dict(self) -> Dict[str, Any]:
                return self.data
            
            @classmethod  
            def from_dict(cls, data: Dict[str, Any]) -> "ConcreteVacancy":
                instance = cls()
                instance.data = data
                return instance
        
        # Тестируем с пустыми данными
        empty_vacancy = ConcreteVacancy.from_dict({})
        assert empty_vacancy.data == {}
        assert empty_vacancy.to_dict() == {}

    def test_multiple_concrete_implementations(self):
        """Покрытие: несколько конкретных реализаций"""
        
        class SimpleVacancy(AbstractVacancy):
            def __init__(self):
                self.name = "Simple"
            
            def to_dict(self) -> Dict[str, Any]:
                return {"type": "simple", "name": self.name}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "SimpleVacancy":
                return cls()
        
        class ComplexVacancy(AbstractVacancy):
            def __init__(self):
                self.name = "Complex"
                self.details = {"advanced": True}
            
            def to_dict(self) -> Dict[str, Any]:
                return {"type": "complex", "name": self.name, "details": self.details}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "ComplexVacancy":
                instance = cls()
                instance.details = data.get("details", {})
                return instance
        
        # Проверяем что обе реализации работают
        simple = SimpleVacancy()
        complex_vacancy = ComplexVacancy()
        
        assert isinstance(simple, AbstractVacancy)
        assert isinstance(complex_vacancy, AbstractVacancy)
        
        assert simple.to_dict()["type"] == "simple"
        assert complex_vacancy.to_dict()["type"] == "complex"
        
        # Проверяем from_dict
        simple_from_dict = SimpleVacancy.from_dict({"test": "data"})
        complex_from_dict = ComplexVacancy.from_dict({"details": {"custom": True}})
        
        assert isinstance(simple_from_dict, SimpleVacancy)
        assert isinstance(complex_from_dict, ComplexVacancy)
        assert complex_from_dict.details == {"custom": True}


class TestInheritanceAndPolymorphism:
    """Тестирование наследования и полиморфизма"""

    def test_inheritance_chain(self):
        """Покрытие: цепочка наследования"""
        
        class BaseVacancy(AbstractVacancy):
            def __init__(self):
                self.base_attr = "base"
            
            def to_dict(self) -> Dict[str, Any]:
                return {"base_attr": self.base_attr}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "BaseVacancy":
                return cls()
        
        class DerivedVacancy(BaseVacancy):
            def __init__(self):
                super().__init__()
                self.derived_attr = "derived"
            
            def to_dict(self) -> Dict[str, Any]:
                base_dict = super().to_dict()
                base_dict["derived_attr"] = self.derived_attr
                return base_dict
        
        # Проверяем цепочку наследования
        derived = DerivedVacancy()
        assert isinstance(derived, AbstractVacancy)
        assert isinstance(derived, BaseVacancy)
        assert isinstance(derived, DerivedVacancy)
        
        # Проверяем что методы работают правильно
        result_dict = derived.to_dict()
        assert result_dict["base_attr"] == "base"
        assert result_dict["derived_attr"] == "derived"

    def test_polymorphism(self):
        """Покрытие: полиморфизм с AbstractVacancy"""
        
        class VacancyA(AbstractVacancy):
            def __init__(self):
                self.type = "A"
            
            def to_dict(self) -> Dict[str, Any]:
                return {"type": self.type, "source": "A"}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "VacancyA":
                return cls()
        
        class VacancyB(AbstractVacancy):
            def __init__(self):
                self.type = "B"
            
            def to_dict(self) -> Dict[str, Any]:
                return {"type": self.type, "source": "B"}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "VacancyB":
                return cls()
        
        # Создаем список разных реализаций
        vacancies = [VacancyA(), VacancyB()]
        
        # Проверяем полиморфное поведение
        for vacancy in vacancies:
            assert isinstance(vacancy, AbstractVacancy)
            result = vacancy.to_dict()
            assert "type" in result
            assert "source" in result
        
        # Проверяем что каждая реализация ведет себя по-своему
        assert vacancies[0].to_dict()["source"] == "A"
        assert vacancies[1].to_dict()["source"] == "B"


class TestAbstractMethodsEnforcement:
    """Тестирование принуждения реализации абстрактных методов"""

    def test_missing_init_method_fails(self):
        """Покрытие: класс с только абстрактными методами должен работать (без абстрактного __init__)"""
        
        # Теперь __init__ не абстрактный, поэтому создаем класс с правильными абстрактными методами
        class IncompleteVacancy1(AbstractVacancy):
            def to_dict(self) -> Dict[str, Any]:
                return {}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "IncompleteVacancy1":
                return cls()
        
        # Этот класс должен работать без ошибок
        instance = IncompleteVacancy1()
        assert instance is not None

    def test_missing_to_dict_method_fails(self):
        """Покрытие: отсутствие to_dict вызывает ошибку"""
        
        with pytest.raises(TypeError) as exc_info:
            class IncompleteVacancy2(AbstractVacancy):
                def __init__(self):
                    pass
                
                @classmethod
                def from_dict(cls, data: Dict[str, Any]) -> "IncompleteVacancy2":
                    return cls()
            
            IncompleteVacancy2()
        
        error_message = str(exc_info.value)
        assert "abstract method to_dict" in error_message or "to_dict" in error_message

    def test_missing_from_dict_method_fails(self):
        """Покрытие: отсутствие from_dict вызывает ошибку"""
        
        with pytest.raises(TypeError) as exc_info:
            class IncompleteVacancy3(AbstractVacancy):
                def __init__(self):
                    pass
                
                def to_dict(self) -> Dict[str, Any]:
                    return {}
            
            IncompleteVacancy3()
        
        error_message = str(exc_info.value)
        assert "abstract method from_dict" in error_message or "from_dict" in error_message

    def test_all_methods_must_be_implemented(self):
        """Покрытие: все методы должны быть реализованы"""
        
        with pytest.raises(TypeError) as exc_info:
            class EmptyVacancy(AbstractVacancy):
                pass
            
            EmptyVacancy()
        
        error_message = str(exc_info.value)
        assert "abstract methods" in error_message
        # Должны быть упомянуты только 2 метода (без __init__)
        assert "from_dict" in error_message  
        assert "to_dict" in error_message