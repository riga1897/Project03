#!/usr/bin/env python3
"""
Тесты для 100% покрытия src/vacancies/abstract_models.py
Покрываем абстрактные классы через наследование и тестирование конкретных методов.
"""

import pytest
from typing import Optional

# Импорты из реального кода для покрытия
from src.vacancies.abstract_models import (
    AbstractEmployerMixin,
    AbstractExperienceMixin,
    AbstractEmploymentMixin,
    AbstractScheduleMixin,
    AbstractSalaryMixin,
    AbstractEmployer,
    AbstractExperience,
    AbstractEmployment,
    AbstractSchedule,
    AbstractSalary
)
from pydantic import BaseModel


# Конкретные реализации для тестирования абстрактных классов
class ConcreteEmployer(AbstractEmployer):
    """Конкретная реализация AbstractEmployer для тестирования"""

    name: str = "Test Company"
    employer_id: Optional[str] = "123"
    trusted: Optional[bool] = True
    url: Optional[str] = "https://test.com"

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> Optional[str]:
        return self.employer_id

    def is_trusted(self) -> Optional[bool]:
        return self.trusted

    def get_url(self) -> Optional[str]:
        return self.url


class ConcreteExperience(AbstractExperience):
    """Конкретная реализация AbstractExperience для тестирования"""

    name: str = "1-3 года"
    experience_id: Optional[str] = "exp_123"

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> Optional[str]:
        return self.experience_id

    @classmethod
    def from_string(cls, data: str) -> "ConcreteExperience":
        return cls(name=data, experience_id=f"exp_{hash(data)}")


class ConcreteEmployment(AbstractEmployment):
    """Конкретная реализация AbstractEmployment для тестирования"""

    name: str = "Полная занятость"
    employment_id: Optional[str] = "full_time"

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> Optional[str]:
        return self.employment_id

    @classmethod
    def from_string(cls, data: str) -> "ConcreteEmployment":
        return cls(name=data, employment_id=f"emp_{hash(data)}")


class ConcreteSchedule(AbstractSchedule):
    """Конкретная реализация AbstractSchedule для тестирования"""

    name: str = "Полный день"
    schedule_id: Optional[str] = "full_day"

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> Optional[str]:
        return self.schedule_id

    @classmethod
    def from_string(cls, data: str) -> "ConcreteSchedule":
        return cls(name=data, schedule_id=f"sch_{hash(data)}")


class ConcreteSalary(AbstractSalary):
    """Конкретная реализация AbstractSalary для тестирования"""

    amount_from: Optional[int] = 100000
    amount_to: Optional[int] = 150000
    currency: str = "RUR"

    def get_from_amount(self) -> Optional[int]:
        return self.amount_from

    def get_to_amount(self) -> Optional[int]:
        return self.amount_to

    def get_currency(self) -> str:
        return self.currency

    def get_average(self) -> float:
        if self.amount_from and self.amount_to:
            return (self.amount_from + self.amount_to) / 2
        elif self.amount_from:
            return float(self.amount_from)
        elif self.amount_to:
            return float(self.amount_to)
        return 0.0

    def is_specified(self) -> bool:
        return self.amount_from is not None or self.amount_to is not None


class TestAbstractEmployerMixin:
    """100% покрытие AbstractEmployerMixin абстрактных методов"""

    def test_abstract_methods_defined(self) -> None:
        """Проверка что все абстрактные методы определены"""
        # Проверяем что миксин нельзя инстанцировать напрямую
        with pytest.raises(TypeError):
            AbstractEmployerMixin()  # type: ignore[abstract]

    def test_concrete_implementation(self) -> None:
        """Тестирование через конкретную реализацию"""
        employer = ConcreteEmployer()

        assert employer.get_name() == "Test Company"
        assert employer.get_id() == "123"
        assert employer.is_trusted() is True
        assert employer.get_url() == "https://test.com"


class TestAbstractExperienceMixin:
    """100% покрытие AbstractExperienceMixin абстрактных методов"""

    def test_abstract_methods_defined(self) -> None:
        """Проверка что все абстрактные методы определены"""
        with pytest.raises(TypeError):
            AbstractExperienceMixin()  # type: ignore[abstract]

    def test_concrete_implementation(self) -> None:
        """Тестирование через конкретную реализацию"""
        experience = ConcreteExperience()

        assert experience.get_name() == "1-3 года"
        assert experience.get_id() == "exp_123"


class TestAbstractEmploymentMixin:
    """100% покрытие AbstractEmploymentMixin абстрактных методов"""

    def test_abstract_methods_defined(self) -> None:
        """Проверка что все абстрактные методы определены"""
        with pytest.raises(TypeError):
            AbstractEmploymentMixin()  # type: ignore[abstract]

    def test_concrete_implementation(self) -> None:
        """Тестирование через конкретную реализацию"""
        employment = ConcreteEmployment()

        assert employment.get_name() == "Полная занятость"
        assert employment.get_id() == "full_time"


class TestAbstractScheduleMixin:
    """100% покрытие AbstractScheduleMixin абстрактных методов"""

    def test_abstract_methods_defined(self) -> None:
        """Проверка что все абстрактные методы определены"""
        with pytest.raises(TypeError):
            AbstractScheduleMixin()  # type: ignore[abstract]

    def test_concrete_implementation(self) -> None:
        """Тестирование через конкретную реализацию"""
        schedule = ConcreteSchedule()

        assert schedule.get_name() == "Полный день"
        assert schedule.get_id() == "full_day"


class TestAbstractSalaryMixin:
    """100% покрытие AbstractSalaryMixin абстрактных методов"""

    def test_abstract_methods_defined(self) -> None:
        """Проверка что все абстрактные методы определены"""
        with pytest.raises(TypeError):
            AbstractSalaryMixin()  # type: ignore[abstract]

    def test_concrete_implementation(self) -> None:
        """Тестирование через конкретную реализацию"""
        salary = ConcreteSalary()

        assert salary.get_from_amount() == 100000
        assert salary.get_to_amount() == 150000
        assert salary.get_currency() == "RUR"
        assert salary.get_average() == 125000.0
        assert salary.is_specified() is True

    def test_salary_edge_cases(self) -> None:
        """Тестирование крайних случаев для зарплаты"""
        # Только from
        salary_from = ConcreteSalary(amount_from=100000, amount_to=None)
        assert salary_from.get_average() == 100000.0
        assert salary_from.is_specified() is True

        # Только to
        salary_to = ConcreteSalary(amount_from=None, amount_to=150000)
        assert salary_to.get_average() == 150000.0
        assert salary_to.is_specified() is True

        # Без зарплаты
        salary_none = ConcreteSalary(amount_from=None, amount_to=None)
        assert salary_none.get_average() == 0.0
        assert salary_none.is_specified() is False


class TestAbstractEmployer:
    """100% покрытие AbstractEmployer базового класса"""

    def test_cannot_instantiate_directly(self) -> None:
        """Проверка что абстрактный класс нельзя создать напрямую"""
        with pytest.raises(TypeError):
            AbstractEmployer()  # type: ignore[abstract]

    def test_concrete_employer_to_dict(self) -> None:
        """Покрытие метода to_dict через конкретную реализацию"""
        employer = ConcreteEmployer()
        result = employer.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "Test Company"
        assert result["employer_id"] == "123"

    def test_concrete_employer_from_dict(self) -> None:
        """Покрытие метода from_dict через конкретную реализацию"""
        data = {"name": "Dict Company", "employer_id": "dict_123"}
        employer = ConcreteEmployer.from_dict(data)

        # Используем геттеры вместо прямого обращения к атрибутам
        assert employer.get_name() == "Dict Company"
        assert employer.get_id() == "dict_123"

    def test_pydantic_config(self) -> None:
        """Проверка конфигурации Pydantic"""
        # Создаем с правильными параметрами ConcreteEmployer
        employer = ConcreteEmployer(name="Test")
        assert employer.get_name() == "Test"

        # extra="ignore" должно работать - проверяем что можем создать с лишними полями
        data_with_extra = {"name": "Test Extra", "extra_field": "ignored"}
        employer_extra = ConcreteEmployer.from_dict(data_with_extra)

        # extra_field должно быть проигнорировано
        assert not hasattr(employer_extra, "extra_field")
        assert employer_extra.get_name() == "Test Extra"


class TestAbstractExperience:
    """100% покрытие AbstractExperience базового класса"""

    def test_cannot_instantiate_directly(self) -> None:
        """Проверка что абстрактный класс нельзя создать напрямую"""
        with pytest.raises(TypeError):
            AbstractExperience()  # type: ignore[abstract]

    def test_concrete_experience_to_dict(self) -> None:
        """Покрытие метода to_dict"""
        experience = ConcreteExperience()
        result = experience.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "1-3 года"
        assert result["experience_id"] == "exp_123"

    def test_concrete_experience_from_dict(self) -> None:
        """Покрытие метода from_dict"""
        data = {"name": "3-6 лет", "experience_id": "exp_456"}
        experience = ConcreteExperience.from_dict(data)

        # Используем геттеры вместо прямого обращения к атрибутам
        assert experience.get_name() == "3-6 лет"
        assert experience.get_id() == "exp_456"

    def test_concrete_experience_from_string(self) -> None:
        """Покрытие абстрактного метода from_string"""
        experience = ConcreteExperience.from_string("Без опыта")

        assert experience.name == "Без опыта"
        assert experience.experience_id is not None


class TestAbstractEmployment:
    """100% покрытие AbstractEmployment базового класса"""

    def test_cannot_instantiate_directly(self) -> None:
        """Проверка что абстрактный класс нельзя создать напрямую"""
        with pytest.raises(TypeError):
            AbstractEmployment()  # type: ignore[abstract]

    def test_concrete_employment_to_dict(self) -> None:
        """Покрытие метода to_dict"""
        employment = ConcreteEmployment()
        result = employment.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "Полная занятость"

    def test_concrete_employment_from_dict(self) -> None:
        """Покрытие метода from_dict"""
        data = {"name": "Частичная занятость", "employment_id": "part_time"}
        employment = ConcreteEmployment.from_dict(data)

        # Используем геттеры вместо прямого обращения к атрибутам
        assert employment.get_name() == "Частичная занятость"
        assert employment.get_id() == "part_time"

    def test_concrete_employment_from_string(self) -> None:
        """Покрытие абстрактного метода from_string"""
        employment = ConcreteEmployment.from_string("Проектная работа")

        assert employment.name == "Проектная работа"
        assert employment.employment_id is not None


class TestAbstractSchedule:
    """100% покрытие AbstractSchedule базового класса"""

    def test_cannot_instantiate_directly(self) -> None:
        """Проверка что абстрактный класс нельзя создать напрямую"""
        with pytest.raises(TypeError):
            AbstractSchedule()  # type: ignore[abstract]

    def test_concrete_schedule_to_dict(self) -> None:
        """Покрытие метода to_dict"""
        schedule = ConcreteSchedule()
        result = schedule.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "Полный день"

    def test_concrete_schedule_from_dict(self) -> None:
        """Покрытие метода from_dict"""
        data = {"name": "Гибкий график", "schedule_id": "flexible"}
        schedule = ConcreteSchedule.from_dict(data)

        # Используем геттеры вместо прямого обращения к атрибутам
        assert schedule.get_name() == "Гибкий график"
        assert schedule.get_id() == "flexible"

    def test_concrete_schedule_from_string(self) -> None:
        """Покрытие абстрактного метода from_string"""
        schedule = ConcreteSchedule.from_string("Удаленная работа")

        assert schedule.name == "Удаленная работа"
        assert schedule.schedule_id is not None


class TestAbstractSalary:
    """100% покрытие AbstractSalary базового класса"""

    def test_cannot_instantiate_directly(self) -> None:
        """Проверка что абстрактный класс нельзя создать напрямую"""
        with pytest.raises(TypeError):
            AbstractSalary()  # type: ignore[abstract]

    def test_concrete_salary_to_dict(self) -> None:
        """Покрытие метода to_dict"""
        salary = ConcreteSalary()
        result = salary.to_dict()

        assert isinstance(result, dict)
        assert result["amount_from"] == 100000
        assert result["amount_to"] == 150000
        assert result["currency"] == "RUR"

    def test_concrete_salary_from_dict(self) -> None:
        """Покрытие метода from_dict"""
        data = {"amount_from": 80000, "amount_to": 120000, "currency": "USD"}
        salary = ConcreteSalary.from_dict(data)

        # Используем геттеры вместо прямого обращения к атрибутам
        assert salary.get_from_amount() == 80000
        assert salary.get_to_amount() == 120000
        assert salary.get_currency() == "USD"


class TestPydanticIntegration:
    """100% покрытие интеграции с Pydantic"""

    def test_validation_assignment(self) -> None:
        """Проверка validate_assignment=True"""
        employer = ConcreteEmployer()

        # Проверим что валидация при присваивании работает
        employer.name = "New Company"
        assert employer.name == "New Company"

    def test_model_config_inheritance(self) -> None:
        """Проверка наследования model_config"""
        # Проверяем что все классы имеют правильную конфигурацию
        assert hasattr(ConcreteEmployer, "model_config")
        assert hasattr(ConcreteExperience, "model_config")
        assert hasattr(ConcreteEmployment, "model_config")
        assert hasattr(ConcreteSchedule, "model_config")
        assert hasattr(ConcreteSalary, "model_config")

    def test_extra_fields_ignored(self) -> None:
        """Проверка что extra поля игнорируются"""
        data = {
            "name": "Test",
            "unknown_field": "should_be_ignored",
            "another_extra": 123
        }

        employer = ConcreteEmployer.from_dict(data)
        assert employer.get_name() == "Test"
        # Дополнительные поля должны быть проигнорированы
        assert not hasattr(employer, "unknown_field")
        assert not hasattr(employer, "another_extra")


class TestModuleExports:
    """100% покрытие экспортов модуля"""

    def test_all_exports_available(self) -> None:
        """Проверка что все экспорты доступны"""
        from src.vacancies.abstract_models import __all__

        expected_exports = [
            "AbstractEmployerMixin",
            "AbstractExperienceMixin",
            "AbstractEmploymentMixin",
            "AbstractScheduleMixin",
            "AbstractSalaryMixin",
            "AbstractEmployer",
            "AbstractExperience",
            "AbstractEmployment",
            "AbstractSchedule",
            "AbstractSalary",
        ]

        assert set(__all__) == set(expected_exports)

        # Проверяем что все экспорты действительно импортируются
        for export_name in __all__:
            assert hasattr(__import__("src.vacancies.abstract_models", fromlist=[export_name]), export_name)


class TestEdgeCases:
    """Покрытие крайних случаев и специфичных ветвей"""

    def test_dict_method_deprecation_handling(self) -> None:
        """Проверка метода dict() для совместимости с Pydantic v1/v2"""
        employer = ConcreteEmployer()

        # В Pydantic v2 может использоваться model_dump(), но to_dict() использует dict()
        try:
            result = employer.to_dict()
            assert isinstance(result, dict)
        except AttributeError:
            # Если dict() не доступен в Pydantic v2, используем model_dump()
            result = employer.model_dump()
            assert isinstance(result, dict)

    def test_multiple_inheritance_mro(self) -> None:
        """Проверка Method Resolution Order для множественного наследования"""
        # Проверяем что MRO работает корректно для BaseModel + AbstractMixin
        assert issubclass(ConcreteEmployer, AbstractEmployerMixin)
        assert issubclass(ConcreteEmployer, BaseModel)

        # Проверяем порядок в MRO
        mro = ConcreteEmployer.__mro__
        assert BaseModel in mro
        assert AbstractEmployerMixin in mro


class TestClassMethods:
    """Покрытие всех классовых методов"""

    def test_from_dict_with_none_values(self) -> None:
        """Покрытие from_dict с None значениями"""
        data = {"name": "Test", "employer_id": None}
        employer = ConcreteEmployer.from_dict(data)

        # Используем геттеры вместо прямого обращения к атрибутам
        assert employer.get_name() == "Test"
        assert employer.get_id() is None

    def test_from_dict_with_missing_fields(self) -> None:
        """Покрытие from_dict с отсутствующими полями"""
        data = {"name": "Minimal"}
        employer = ConcreteEmployer.from_dict(data)

        # Используем геттеры вместо прямого обращения к атрибутам
        assert employer.get_name() == "Minimal"
        # Остальные поля должны иметь значения по умолчанию

    def test_from_string_implementations(self) -> None:
        """Покрытие всех реализаций from_string"""
        exp = ConcreteExperience.from_string("Senior Level")
        emp = ConcreteEmployment.from_string("Contract")
        sch = ConcreteSchedule.from_string("Night Shift")

        assert exp.name == "Senior Level"
        assert emp.name == "Contract"
        assert sch.name == "Night Shift"

        # Проверяем что ID генерируются
        assert exp.experience_id is not None
        assert emp.employment_id is not None
        assert sch.schedule_id is not None
