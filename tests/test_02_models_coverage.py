"""
Тесты моделей вакансий для 100% покрытия.

Покрывает все строки кода в src/vacancies/models.py с использованием реальных импортов.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.utils.salary import Salary
from src.vacancies.models import Employer, Experience, Employment, Vacancy


class TestSalary:
    """100% покрытие класса Salary."""

    def test_init_with_all_params(self) -> None:
        """Покрытие инициализации со всеми параметрами."""
        salary_data = {"from": 50000, "to": 80000, "currency": "RUR"}
        salary = Salary(salary_data)
        assert salary._salary_from == 50000
        assert salary._salary_to == 80000
        assert salary._currency == "RUR"

    def test_init_minimal(self) -> None:
        """Покрытие минимальной инициализации."""
        salary = Salary()
        assert salary._salary_from is None
        assert salary._salary_to is None
        assert salary._currency == "RUR"

    def test_init_from_dict_full(self) -> None:
        """Покрытие инициализации с полными данными."""
        data = {"from": 100000, "to": 150000, "currency": "USD"}
        salary = Salary(data)
        assert salary._salary_from == 100000
        assert salary._salary_to == 150000
        assert salary._currency == "USD"

    def test_init_from_dict_partial(self) -> None:
        """Покрытие инициализации с частичными данными."""
        data = {"from": 60000}
        salary = Salary(data)
        assert salary._salary_from == 60000
        assert salary._salary_to is None
        assert salary._currency == "RUR"

    def test_to_dict(self) -> None:
        """Покрытие метода to_dict."""
        salary_data = {"from": 70000, "to": 90000, "currency": "EUR"}
        salary = Salary(salary_data)
        result = salary.to_dict()
        assert result["from"] == 70000
        assert result["to"] == 90000
        assert result["currency"] == "EUR"

    def test_str_method_full(self) -> None:
        """Покрытие __str__ с полной зарплатой."""
        salary_data = {"from": 50000, "to": 70000, "currency": "RUR"}
        salary = Salary(salary_data)
        result = str(salary)
        assert "50,000" in result and "70,000" in result and "руб" in result

    def test_str_method_from_only(self) -> None:
        """Покрытие __str__ только с минимальной зарплатой."""
        salary_data = {"from": 40000, "currency": "RUR"}
        salary = Salary(salary_data)
        result = str(salary)
        assert "40,000" in result and "руб" in result

    def test_str_method_to_only(self) -> None:
        """Покрытие __str__ только с максимальной зарплатой."""
        salary_data = {"to": 60000, "currency": "RUR"}
        salary = Salary(salary_data)
        result = str(salary)
        assert "60,000" in result and "руб" in result

    def test_str_method_no_salary(self) -> None:
        """Покрытие __str__ без указания зарплаты."""
        salary = Salary()
        result = str(salary)
        assert result == "Не указана"


class TestEmployer:
    """100% покрытие класса Employer."""

    def test_init_full(self) -> None:
        """Покрытие полной инициализации."""
        employer = Employer(name="Test Company", id="123", trusted=True, alternate_url="https://test.com")
        assert employer.name == "Test Company"
        assert employer.id == "123"
        assert employer.trusted is True
        assert employer.alternate_url == "https://test.com"

    def test_init_minimal(self) -> None:
        """Покрытие минимальной инициализации."""
        employer = Employer(name="Minimal Company")
        assert employer.name == "Minimal Company"
        assert employer.id is None
        assert employer.trusted is None
        assert employer.alternate_url is None

    def test_from_dict(self) -> None:
        """Покрытие from_dict."""
        data = {"name": "Dict Company", "id": "dict123", "trusted": False, "alternate_url": "https://dict.com"}
        employer = Employer.from_dict(data)
        assert employer.name == "Dict Company"
        assert employer.id == "dict123"
        assert employer.trusted is False
        assert employer.alternate_url == "https://dict.com"

    def test_all_methods(self) -> None:
        """Покрытие всех методов класса."""
        employer = Employer(name="Method Test", id="method123", trusted=True, alternate_url="https://method.com")

        # Тестируем все методы get_*
        assert employer.get_name() == "Method Test"
        assert employer.get_id() == "method123" 
        assert employer.is_trusted() is True
        assert employer.get_url() == "https://method.com"

        # Тестируем to_dict
        result = employer.to_dict()
        expected = {"name": "Method Test", "id": "method123", "trusted": True, "alternate_url": "https://method.com"}
        assert result == expected


class TestExperience:
    """100% покрытие класса Experience."""

    def test_init_and_methods(self) -> None:
        """Покрытие инициализации и всех методов."""
        experience = Experience(name="3-6 лет", id="exp123")
        assert experience.name == "3-6 лет"
        assert experience.id == "exp123"
        assert experience.get_name() == "3-6 лет"
        assert experience.get_id() == "exp123"

    def test_from_dict_and_to_dict(self) -> None:
        """Покрытие from_dict и to_dict."""
        data = {"name": "1-3 года", "id": "exp456"}
        experience = Experience.from_dict(data)
        assert experience.to_dict() == data

    def test_from_string(self) -> None:
        """Покрытие from_string."""
        experience = Experience.from_string("Без опыта")
        assert experience.get_name() == "Без опыта"
        assert experience.get_id() is None


class TestEmployment:
    """100% покрытие класса Employment."""

    def test_init_and_methods(self) -> None:
        """Покрытие инициализации и всех методов."""
        employment = Employment(name="Полная занятость", id="emp123")
        assert employment.name == "Полная занятость"
        assert employment.id == "emp123"
        assert employment.get_name() == "Полная занятость"
        assert employment.get_id() == "emp123"

    def test_from_dict_and_to_dict(self) -> None:
        """Покрытие from_dict и to_dict."""
        data = {"name": "Частичная занятость", "id": "emp456"}
        employment = Employment.from_dict(data)
        assert employment.to_dict() == data

    def test_from_string(self) -> None:
        """Покрытие from_string."""
        employment = Employment.from_string("Проектная работа")
        assert employment.get_name() == "Проектная работа"
        assert employment.get_id() is None


class TestVacancy:
    """100% покрытие класса Vacancy."""

    @patch('src.vacancies.models.uuid.uuid4')
    @patch('src.vacancies.models.datetime')
    def test_init_minimal(self, mock_datetime, mock_uuid):
        """Покрытие минимальной инициализации."""
        mock_uuid.return_value.hex = "test_uuid"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"

        vacancy = Vacancy(vacancy_id="123", name="Test Job", alternate_url="https://test.com")
        assert vacancy.id == "123"
        assert vacancy.title == "Test Job" 
        assert vacancy.url == "https://test.com"

    @patch('src.vacancies.models.uuid.uuid4')
    def test_init_full(self, mock_uuid):
        """Покрытие полной инициализации."""
        mock_uuid.return_value.hex = "test_uuid"

        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        employer_data = {"name": "Test Company", "id": "comp123"}

        vacancy = Vacancy(
            vacancy_id="456",
            name="Senior Developer", 
            alternate_url="https://senior.com",
            salary=salary_data,
            description="Great job",
            requirements="Python skills",
            responsibilities="Coding",
            employer=employer_data,
            area="Moscow",
            experience={"name": "3-6 лет", "id": "exp123"},
            employment={"name": "Полная занятость", "id": "emp123"},
            schedule={"name": "Полный день", "id": "sch123"},
            published_at="2024-01-01",
            source="test_source",
            updated_at="2024-01-02",
            company_id="comp123"
        )

        assert vacancy.id == "456"
        assert vacancy.title == "Senior Developer"
        assert isinstance(vacancy.salary, dict)
        assert isinstance(vacancy.employer, Employer)
        assert isinstance(vacancy.experience, Experience)
        assert isinstance(vacancy.employment, Employment)

    @patch('src.vacancies.models.uuid.uuid4')
    def test_salary_property(self, mock_uuid):
        """Покрытие свойства salary."""
        mock_uuid.return_value.hex = "test_uuid"

        vacancy = Vacancy(vacancy_id="123", name="Test", alternate_url="url", salary={"from": 50000})
        assert isinstance(vacancy.salary, dict)

    @patch('src.vacancies.models.uuid.uuid4')
    def test_employer_property(self, mock_uuid):
        """Покрытие свойства employer."""
        mock_uuid.return_value.hex = "test_uuid"

        employer_data = {"name": "Dict Company", "id": "dict123"}
        vacancy = Vacancy(vacancy_id="123", name="Test", alternate_url="url", employer=employer_data)
        assert isinstance(vacancy.employer, Employer)

    @patch('src.vacancies.models.uuid.uuid4')
    def test_all_methods(self, mock_uuid):
        """Покрытие всех методов Vacancy."""
        mock_uuid.return_value.hex = "test_uuid"

        vacancy = Vacancy(vacancy_id="method_test", name="Method Test", alternate_url="https://method.com")

        # Покрываем все поля модели
        assert vacancy.id == "method_test"
        assert vacancy.title == "Method Test"
        assert vacancy.url == "https://method.com"
        assert vacancy.description is None  # значение по умолчанию
        assert vacancy.requirements is None
        assert vacancy.responsibilities is None
        assert vacancy.area is None
        assert vacancy.source is None

        # Покрываем model_dump
        result = vacancy.model_dump()
        assert isinstance(result, dict)
        assert result["id"] == "method_test"
        assert result["title"] == "Method Test"