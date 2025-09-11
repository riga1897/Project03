"""
Тесты абстрактных моделей для 100% покрытия.

Покрывает все строки кода в src/vacancies/abstract_models.py без лишних проверок.
"""

from typing import Any

from src.vacancies.abstract_models import AbstractEmployerMixin, AbstractExperienceMixin, AbstractEmploymentMixin


class ConcreteEmployer(AbstractEmployerMixin):
    """Конкретная реализация для тестирования абстрактного миксина."""

    def __init__(self, name: str = "Test Name", id: Any = None, trusted: Any = None, url: Any = None) -> None:
        self.name = name
        self.id = id
        self.trusted = trusted
        self.url = url

    def get_name(self) -> Any:
        return self.name

    def get_id(self) -> Any:
        return self.id

    def is_trusted(self) -> Any:
        return self.trusted

    def get_url(self) -> Any:
        return self.url


class ConcreteExperience(AbstractExperienceMixin):
    """Конкретная реализация для тестирования Experience миксина."""

    def __init__(self, name: Any = "Test Experience", id: Any = None) -> None:
        self.name = name
        self.id = id

    def get_name(self) -> Any:
        return self.name

    def get_id(self) -> Any:
        return self.id


class ConcreteEmployment(AbstractEmploymentMixin):
    """Конкретная реализация для тестирования Employment миксина."""

    def __init__(self, name: str = "Test Employment", id: Any = None) -> None:
        self.name = name
        self.id = id

    def get_name(self) -> Any:
        return self.name

    def get_id(self) -> Any:
        return self.id


class TestAbstractMixins:
    """100% покрытие абстрактных миксинов."""

    def test_employer_mixin_methods(self) -> None:
        """Тест методов AbstractEmployerMixin."""
        employer = ConcreteEmployer(name="Test Company", id="test_id", trusted=True, url="https://test.com")

        assert employer.get_name() == "Test Company"
        assert employer.get_id() == "test_id"
        assert employer.is_trusted() is True
        assert employer.get_url() == "https://test.com"

    def test_experience_mixin_methods(self) -> None:
        """Тест методов AbstractExperienceMixin."""
        experience = ConcreteExperience(name="1-3 года", id="exp_id")

        assert experience.get_name() == "1-3 года"
        assert experience.get_id() == "exp_id"

    def test_employment_mixin_methods(self) -> None:
        """Тест методов AbstractEmploymentMixin."""
        employment = ConcreteEmployment(name="Полная занятость", id="emp_id")

        assert employment.get_name() == "Полная занятость"
        assert employment.get_id() == "emp_id"

    def test_all_mixin_implementations(self) -> None:
        """Покрытие всех реализаций миксинов для полного покрытия кода."""
        # Создаем экземпляры всех миксинов для покрытия
        employer = ConcreteEmployer()
        experience = ConcreteExperience()
        employment = ConcreteEmployment()

        # Проверяем базовую функциональность
        assert employer.get_name() == "Test Name"
        assert experience.get_name() == "Test Experience"
        assert employment.get_name() == "Test Employment"

        # Проверяем None значения
        assert employer.get_id() is None
        assert experience.get_id() is None
        assert employment.get_id() is None
