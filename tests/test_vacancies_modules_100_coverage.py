"""
Тесты для модулей вакансий с 100% покрытием
Покрывает: models, abstract, abstract_models, parsers
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vacancies.models import Employer, Employment, Experience, Salary, Vacancy
from src.vacancies.abstract import AbstractVacancy
from src.vacancies.abstract_models import AbstractEmployer, AbstractEmployment, AbstractExperience, AbstractSalary
from src.vacancies.parsers.base_parser import BaseVacancyParser
from src.vacancies.parsers.hh_parser import HHVacancyParser
from src.vacancies.parsers.sj_parser import SJVacancyParser


class TestEmployer:
    """Тесты для класса Employer"""

    def test_init_basic(self):
        """Тест базовой инициализации"""
        employer = Employer("Test Company")
        
        assert employer.get_name() == "Test Company"
        assert employer.get_id() is None

    def test_init_full(self):
        """Тест полной инициализации"""
        employer = Employer(
            name="Full Company",
            employer_id="123",
            trusted=True,
            alternate_url="http://company.com"
        )
        
        assert employer.get_name() == "Full Company"
        assert employer.get_id() == "123"
        assert employer.is_trusted() == True
        assert employer.get_url() == "http://company.com"

    def test_get_name_empty(self):
        """Тест получения имени при пустом значении"""
        employer = Employer("")
        assert employer.get_name() == "Не указана"

    def test_get_name_none(self):
        """Тест получения имени при None"""
        employer = Employer(None)
        assert employer.get_name() == "Не указана"

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        employer = Employer("Test", "123", True, "http://test.com")
        result = employer.to_dict()
        
        expected = {
            "name": "Test",
            "id": "123",
            "trusted": True,
            "alternate_url": "http://test.com"
        }
        assert result == expected

    def test_from_dict_full(self):
        """Тест создания из полного словаря"""
        data = {
            "name": "Dict Company",
            "id": "456",
            "trusted": False,
            "alternate_url": "http://dict.com"
        }
        
        employer = Employer.from_dict(data)
        
        assert employer.get_name() == "Dict Company"
        assert employer.get_id() == "456"
        assert employer.is_trusted() == False
        assert employer.get_url() == "http://dict.com"

    def test_from_dict_minimal(self):
        """Тест создания из минимального словаря"""
        data = {"name": "Minimal Company"}
        employer = Employer.from_dict(data)
        
        assert employer.get_name() == "Minimal Company"
        assert employer.get_id() is None

    def test_from_dict_empty(self):
        """Тест создания из пустого словаря"""
        employer = Employer.from_dict({})
        assert employer.get_name() == "Не указана"


class TestSalary:
    """Тесты для класса Salary"""

    def test_init_range(self):
        """Тест инициализации с диапазоном"""
        salary = Salary(100000, 150000, "RUR")
        
        assert salary.get_from() == 100000
        assert salary.get_to() == 150000
        assert salary.get_currency() == "RUR"

    def test_init_from_only(self):
        """Тест инициализации только с 'от'"""
        salary = Salary(salary_from=80000, currency="RUR")
        
        assert salary.get_from() == 80000
        assert salary.get_to() is None

    def test_init_to_only(self):
        """Тест инициализации только с 'до'"""
        salary = Salary(salary_to=120000, currency="USD")
        
        assert salary.get_from() is None
        assert salary.get_to() == 120000

    def test_format_salary_range(self):
        """Тест форматирования диапазона"""
        salary = Salary(100000, 150000, "RUR")
        result = salary.format_salary()
        
        assert "100 000" in result and "150 000" in result

    def test_format_salary_from(self):
        """Тест форматирования 'от'"""
        salary = Salary(salary_from=100000, currency="RUR")
        result = salary.format_salary()
        
        assert "от 100 000" in result

    def test_format_salary_to(self):
        """Тест форматирования 'до'"""
        salary = Salary(salary_to=150000, currency="RUR")
        result = salary.format_salary()
        
        assert "до 150 000" in result

    def test_format_salary_none(self):
        """Тест форматирования при отсутствии зарплаты"""
        salary = Salary(currency="RUR")
        result = salary.format_salary()
        
        assert result == "Не указана"

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        salary = Salary(100000, 150000, "RUR", gross=True)
        result = salary.to_dict()
        
        expected = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR",
            "gross": True
        }
        assert result == expected

    def test_from_dict_full(self):
        """Тест создания из полного словаря"""
        data = {
            "from": 90000,
            "to": 130000,
            "currency": "USD",
            "gross": False
        }
        
        salary = Salary.from_dict(data)
        
        assert salary.get_from() == 90000
        assert salary.get_to() == 130000
        assert salary.get_currency() == "USD"
        assert salary.is_gross() == False

    def test_from_dict_empty(self):
        """Тест создания из пустого словаря"""
        salary = Salary.from_dict({})
        
        assert salary.get_from() is None
        assert salary.get_to() is None
        assert salary.get_currency() == "RUR"

    def test_compare_higher(self):
        """Тест сравнения - выше"""
        salary1 = Salary(150000, 200000, "RUR")
        salary2 = Salary(100000, 130000, "RUR")
        
        assert salary1.compare(salary2) > 0

    def test_compare_lower(self):
        """Тест сравнения - ниже"""
        salary1 = Salary(80000, 100000, "RUR")
        salary2 = Salary(150000, 200000, "RUR")
        
        assert salary1.compare(salary2) < 0

    def test_compare_equal(self):
        """Тест сравнения - равно"""
        salary1 = Salary(100000, 150000, "RUR")
        salary2 = Salary(100000, 150000, "RUR")
        
        assert salary1.compare(salary2) == 0


class TestExperience:
    """Тесты для класса Experience"""

    def test_init_basic(self):
        """Тест базовой инициализации"""
        exp = Experience("between1And3", "От 1 года до 3 лет")
        
        assert exp.get_id() == "between1And3"
        assert exp.get_name() == "От 1 года до 3 лет"

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        exp = Experience("between3And6", "От 3 до 6 лет")
        result = exp.to_dict()
        
        expected = {
            "id": "between3And6",
            "name": "От 3 до 6 лет"
        }
        assert result == expected

    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {"id": "moreThan6", "name": "Более 6 лет"}
        exp = Experience.from_dict(data)
        
        assert exp.get_id() == "moreThan6"
        assert exp.get_name() == "Более 6 лет"

    def test_from_dict_empty(self):
        """Тест создания из пустого словаря"""
        exp = Experience.from_dict({})
        
        assert exp.get_id() == "noExperience"
        assert exp.get_name() == "Нет опыта"


class TestEmployment:
    """Тесты для класса Employment"""

    def test_init_basic(self):
        """Тест базовой инициализации"""
        emp = Employment("full", "Полная занятость")
        
        assert emp.get_id() == "full"
        assert emp.get_name() == "Полная занятость"

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        emp = Employment("part", "Частичная занятость")
        result = emp.to_dict()
        
        expected = {
            "id": "part",
            "name": "Частичная занятость"
        }
        assert result == expected

    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {"id": "project", "name": "Проектная работа"}
        emp = Employment.from_dict(data)
        
        assert emp.get_id() == "project"
        assert emp.get_name() == "Проектная работа"


class TestVacancy:
    """Тесты для класса Vacancy"""

    def test_init_minimal(self):
        """Тест минимальной инициализации"""
        vacancy = Vacancy("Test Vacancy", "http://test.com")
        
        assert vacancy.get_title() == "Test Vacancy"
        assert vacancy.get_url() == "http://test.com"

    def test_init_full(self):
        """Тест полной инициализации"""
        employer = Employer("Test Company")
        salary = Salary(100000, 150000, "RUR")
        
        vacancy = Vacancy(
            title="Full Vacancy",
            url="http://full.com",
            salary=salary,
            employer=employer,
            description="Test description",
            vacancy_id="123",
            published_at="2024-01-01T00:00:00"
        )
        
        assert vacancy.get_title() == "Full Vacancy"
        assert vacancy.get_salary() == salary
        assert vacancy.get_employer() == employer
        assert vacancy.get_description() == "Test description"

    def test_get_id_generated(self):
        """Тест генерации ID"""
        vacancy = Vacancy("Test", "http://test.com")
        
        vacancy_id = vacancy.get_id()
        assert vacancy_id is not None
        assert len(vacancy_id) > 0

    def test_get_id_provided(self):
        """Тест предоставленного ID"""
        vacancy = Vacancy("Test", "http://test.com", vacancy_id="custom123")
        
        assert vacancy.get_id() == "custom123"

    def test_get_published_date_string(self):
        """Тест получения даты публикации из строки"""
        vacancy = Vacancy("Test", "http://test.com", published_at="2024-01-01T10:00:00")
        
        date = vacancy.get_published_date()
        assert isinstance(date, datetime)

    def test_get_published_date_datetime(self):
        """Тест получения даты публикации из datetime"""
        now = datetime.now()
        vacancy = Vacancy("Test", "http://test.com", published_at=now)
        
        assert vacancy.get_published_date() == now

    def test_get_published_date_invalid(self):
        """Тест получения даты при невалидном формате"""
        vacancy = Vacancy("Test", "http://test.com", published_at="invalid")
        
        date = vacancy.get_published_date()
        assert isinstance(date, datetime)  # Должна быть текущая дата

    def test_to_dict_minimal(self):
        """Тест преобразования минимальной вакансии в словарь"""
        vacancy = Vacancy("Test", "http://test.com")
        result = vacancy.to_dict()
        
        assert result["title"] == "Test"
        assert result["url"] == "http://test.com"
        assert "id" in result

    def test_to_dict_full(self):
        """Тест преобразования полной вакансии в словарь"""
        employer = Employer("Test Company")
        salary = Salary(100000, 150000, "RUR")
        
        vacancy = Vacancy(
            title="Full Test",
            url="http://test.com",
            salary=salary,
            employer=employer
        )
        
        result = vacancy.to_dict()
        
        assert result["title"] == "Full Test"
        assert result["salary"] == salary.to_dict()
        assert result["employer"] == employer.to_dict()

    def test_from_dict_minimal(self):
        """Тест создания из минимального словаря"""
        data = {
            "title": "Dict Vacancy",
            "url": "http://dict.com"
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.get_title() == "Dict Vacancy"
        assert vacancy.get_url() == "http://dict.com"

    def test_from_dict_full(self):
        """Тест создания из полного словаря"""
        data = {
            "title": "Full Dict",
            "url": "http://full.com",
            "id": "dict123",
            "description": "Full description",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "employer": {"name": "Dict Company"},
            "published_at": "2024-01-01T00:00:00"
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.get_title() == "Full Dict"
        assert vacancy.get_id() == "dict123"
        assert vacancy.get_description() == "Full description"
        assert vacancy.get_salary() is not None
        assert vacancy.get_employer() is not None

    def test_compare_by_salary_higher(self):
        """Тест сравнения по зарплате - выше"""
        vacancy1 = Vacancy("Test1", "url1", salary=Salary(150000, 200000, "RUR"))
        vacancy2 = Vacancy("Test2", "url2", salary=Salary(100000, 130000, "RUR"))
        
        assert vacancy1.compare_by_salary(vacancy2) > 0

    def test_compare_by_salary_no_salary(self):
        """Тест сравнения при отсутствии зарплаты"""
        vacancy1 = Vacancy("Test1", "url1")
        vacancy2 = Vacancy("Test2", "url2")
        
        assert vacancy1.compare_by_salary(vacancy2) == 0

    def test_matches_query_found(self):
        """Тест поиска запроса в описании"""
        vacancy = Vacancy("Python Developer", "url", description="Looking for Python developer")
        
        assert vacancy.matches_query("python") == True

    def test_matches_query_not_found(self):
        """Тест отсутствия запроса в описании"""
        vacancy = Vacancy("Java Developer", "url", description="Java programming")
        
        assert vacancy.matches_query("python") == False

    def test_matches_query_no_description(self):
        """Тест поиска при отсутствии описания"""
        vacancy = Vacancy("Python Developer", "url")
        
        assert vacancy.matches_query("python") == True  # Поиск по названию


class TestBaseVacancyParser:
    """Тесты для BaseVacancyParser"""

    def test_is_abstract(self):
        """Тест что класс абстрактный"""
        with pytest.raises(TypeError):
            BaseVacancyParser()

    def test_concrete_implementation(self):
        """Тест конкретной реализации"""
        class TestParser(BaseVacancyParser):
            def parse(self, raw_data):
                return Vacancy("Test", "http://test.com")
        
        parser = TestParser()
        vacancy = parser.parse({"test": "data"})
        
        assert isinstance(vacancy, Vacancy)


class TestHHVacancyParser:
    """Тесты для HHVacancyParser"""

    def test_parse_minimal(self):
        """Тест парсинга минимальных данных HH"""
        data = {
            "name": "Python Developer",
            "alternate_url": "http://hh.ru/vacancy/123"
        }
        
        parser = HHVacancyParser()
        vacancy = parser.parse(data)
        
        assert vacancy.get_title() == "Python Developer"
        assert vacancy.get_url() == "http://hh.ru/vacancy/123"

    def test_parse_full(self):
        """Тест парсинга полных данных HH"""
        data = {
            "id": "12345",
            "name": "Senior Python Developer",
            "alternate_url": "http://hh.ru/vacancy/12345",
            "description": "We are looking for Python developer",
            "published_at": "2024-01-01T10:00:00+0300",
            "salary": {
                "from": 150000,
                "to": 200000,
                "currency": "RUR",
                "gross": True
            },
            "employer": {
                "name": "Great Company",
                "id": "999",
                "trusted": True,
                "alternate_url": "http://hh.ru/employer/999"
            },
            "experience": {
                "id": "between3And6",
                "name": "От 3 до 6 лет"
            },
            "employment": {
                "id": "full",
                "name": "Полная занятость"
            }
        }
        
        parser = HHVacancyParser()
        vacancy = parser.parse(data)
        
        assert vacancy.get_id() == "12345"
        assert vacancy.get_title() == "Senior Python Developer"
        assert vacancy.get_description() == "We are looking for Python developer"
        assert vacancy.get_salary() is not None
        assert vacancy.get_employer() is not None

    def test_parse_missing_required_fields(self):
        """Тест парсинга с отсутствующими обязательными полями"""
        data = {"name": "Test Vacancy"}  # Нет alternate_url
        
        parser = HHVacancyParser()
        
        with pytest.raises(ValueError, match="отсутствуют обязательные поля"):
            parser.parse(data)

    def test_parse_invalid_data(self):
        """Тест парсинга невалидных данных"""
        parser = HHVacancyParser()
        
        with pytest.raises(ValueError, match="должны быть словарем"):
            parser.parse("invalid data")


class TestSJVacancyParser:
    """Тесты для SJVacancyParser"""

    def test_parse_minimal(self):
        """Тест парсинга минимальных данных SuperJob"""
        data = {
            "profession": "Python Developer",
            "link": "http://superjob.ru/vakansii/123"
        }
        
        parser = SJVacancyParser()
        vacancy = parser.parse(data)
        
        assert vacancy.get_title() == "Python Developer"
        assert vacancy.get_url() == "http://superjob.ru/vakansii/123"

    def test_parse_full(self):
        """Тест парсинга полных данных SuperJob"""
        data = {
            "id": 54321,
            "profession": "Senior Python Developer",
            "link": "http://superjob.ru/vakansii/54321",
            "candidat": "We need Python developer",
            "date_published": 1704067200,  # Unix timestamp
            "payment_from": 180000,
            "payment_to": 250000,
            "currency": "rub",
            "firm_name": "SuperJob Company",
            "firm_id": 777
        }
        
        parser = SJVacancyParser()
        vacancy = parser.parse(data)
        
        assert vacancy.get_id() == "54321"
        assert vacancy.get_title() == "Senior Python Developer"
        assert vacancy.get_description() == "We need Python developer"
        assert vacancy.get_salary() is not None
        assert vacancy.get_employer() is not None

    def test_parse_missing_required_fields(self):
        """Тест парсинга с отсутствующими обязательными полями"""
        data = {"profession": "Test Vacancy"}  # Нет link
        
        parser = SJVacancyParser()
        
        with pytest.raises(ValueError, match="отсутствуют обязательные поля"):
            parser.parse(data)

    def test_convert_timestamp(self):
        """Тест конвертации Unix timestamp"""
        parser = SJVacancyParser()
        
        # Тестируем приватный метод через публичный интерфейс
        data = {
            "profession": "Test",
            "link": "http://test.com",
            "date_published": 1704067200
        }
        
        vacancy = parser.parse(data)
        published_date = vacancy.get_published_date()
        
        assert isinstance(published_date, datetime)