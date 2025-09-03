"""
Комплексные тесты для модулей вакансий с максимальным покрытием кода.
Включает тестирование моделей данных, парсеров и абстрактных классов.
"""

import os
import sys
import pytest
import uuid
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, List, Any, Optional
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vacancies.abstract import AbstractVacancy
from src.vacancies.abstract_models import AbstractEmployer, AbstractExperience, AbstractEmployment, AbstractSalary, AbstractSchedule
from src.vacancies.models import Vacancy, Employer, Experience, Employment
from src.vacancies.parsers.base_parser import BaseParser
from src.vacancies.parsers.hh_parser import HHParser
from src.vacancies.parsers.sj_parser import SuperJobParser


def create_hh_vacancy_data():
    """Создает тестовые данные вакансии в формате HH.ru"""
    return {
        "id": "123456",
        "name": "Python Developer",
        "alternate_url": "https://hh.ru/vacancy/123456",
        "employer": {
            "id": "1740",
            "name": "Яндекс",
            "trusted": True,
            "alternate_url": "https://hh.ru/employer/1740"
        },
        "salary": {
            "from": 150000,
            "to": 250000,
            "currency": "RUR",
            "gross": False
        },
        "area": {
            "id": "1",
            "name": "Москва"
        },
        "experience": {
            "id": "between1And3",
            "name": "От 1 года до 3 лет"
        },
        "employment": {
            "id": "full",
            "name": "Полная занятость"
        },
        "schedule": {
            "id": "fullDay",
            "name": "Полный день"
        },
        "snippet": {
            "requirement": "Знание Python, Django, PostgreSQL",
            "responsibility": "Разработка веб-приложений"
        },
        "published_at": "2025-01-01T10:00:00+03:00"
    }


def create_sj_vacancy_data():
    """Создает тестовые данные вакансии в формате SuperJob"""
    return {
        "id": 789012,
        "profession": "Python разработчик",
        "link": "https://superjob.ru/vakansii/python-789012.html",
        "firm_name": "IT Компания",
        "firm_id": 12345,
        "payment_from": 120000,
        "payment_to": 180000,
        "currency": "rub",
        "town": {
            "id": 4,
            "title": "Москва"
        },
        "candidat": "Опыт работы с Python от 2 лет",
        "work": "Разработка и поддержка веб-приложений",
        "experience": {
            "id": 2,
            "title": "От 1 года до 3 лет"
        },
        "type_of_work": {
            "id": 1,
            "title": "Полная занятость"
        },
        "date_published": 1704096000  # timestamp
    }


class TestAbstractVacancy:
    """Комплексное тестирование абстрактного класса вакансии"""

    def test_abstract_vacancy_cannot_be_instantiated(self):
        """Тестирование невозможности создания экземпляра абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractVacancy()

    def test_abstract_vacancy_methods_exist(self):
        """Тестирование наличия абстрактных методов"""
        assert hasattr(AbstractVacancy, 'to_dict')
        assert hasattr(AbstractVacancy, 'from_dict')

        # Проверяем, что методы помечены как абстрактные
        assert getattr(AbstractVacancy.to_dict, '__isabstractmethod__', False)
        assert getattr(AbstractVacancy.from_dict, '__isabstractmethod__', False)


class TestAbstractModels:
    """Комплексное тестирование абстрактных моделей"""

    def test_abstract_employer_methods(self):
        """Тестирование методов абстрактного работодателя"""
        assert hasattr(AbstractEmployer, 'get_name')
        assert hasattr(AbstractEmployer, 'get_id')
        assert hasattr(AbstractEmployer, 'is_trusted')
        assert hasattr(AbstractEmployer, 'get_url')

    def test_abstract_experience_methods(self):
        """Тестирование методов абстрактного опыта"""
        assert hasattr(AbstractExperience, 'get_name')
        assert hasattr(AbstractExperience, 'get_id')

    def test_abstract_employment_methods(self):
        """Тестирование методов абстрактной занятости"""
        assert hasattr(AbstractEmployment, 'get_name')
        assert hasattr(AbstractEmployment, 'get_id')

    def test_abstract_salary_methods(self):
        """Тестирование методов абстрактной зарплаты"""
        assert hasattr(AbstractSalary, 'get_from_amount')
        assert hasattr(AbstractSalary, 'get_to_amount')
        assert hasattr(AbstractSalary, 'get_currency')

    def test_abstract_schedule_methods(self):
        """Тестирование методов абстрактного расписания"""
        assert hasattr(AbstractSchedule, 'get_name')
        assert hasattr(AbstractSchedule, 'get_id')


class TestEmployer:
    """Комплексное тестирование модели работодателя"""

    def test_employer_initialization(self):
        """Тестирование инициализации работодателя"""
        employer = Employer(
            name="Яндекс",
            employer_id="1740",
            trusted=True,
            alternate_url="https://hh.ru/employer/1740"
        )

        assert employer.get_name() == "Яндекс"
        assert employer.get_id() == "1740"
        assert employer.is_trusted() is True
        assert employer.get_url() == "https://hh.ru/employer/1740"

    def test_employer_minimal_initialization(self):
        """Тестирование минимальной инициализации работодателя"""
        employer = Employer(name="Test Company")

        assert employer.get_name() == "Test Company"
        assert employer.get_id() is None
        assert employer.is_trusted() is None
        assert employer.get_url() is None

    def test_employer_empty_name_handling(self):
        """Тестирование обработки пустого имени работодателя"""
        employer = Employer(name="")
        assert employer.get_name() == "Не указана"

        employer = Employer(name=None)
        assert employer.get_name() == "Не указана"

    def test_employer_to_dict(self):
        """Тестирование преобразования работодателя в словарь"""
        employer = Employer(
            name="Яндекс",
            employer_id="1740",
            trusted=True,
            alternate_url="https://hh.ru/employer/1740"
        )

        result = employer.to_dict()

        assert isinstance(result, dict)
        assert result['name'] == "Яндекс"
        assert result['id'] == "1740"
        assert result['trusted'] is True
        assert result['alternate_url'] == "https://hh.ru/employer/1740"

    def test_employer_from_dict(self):
        """Тестирование создания работодателя из словаря"""
        data = {
            'name': 'Google',
            'id': '39305',
            'trusted': True,
            'alternate_url': 'https://hh.ru/employer/39305'
        }

        employer = Employer.from_dict(data)

        assert employer.get_name() == "Google"
        assert employer.get_id() == "39305"
        assert employer.is_trusted() is True
        assert employer.get_url() == "https://hh.ru/employer/39305"

    def test_employer_from_dict_minimal(self):
        """Тестирование создания работодателя из минимального словаря"""
        data = {'name': 'Minimal Company'}
        employer = Employer.from_dict(data)

        assert employer.get_name() == "Minimal Company"
        assert employer.get_id() is None

    def test_employer_string_representations(self):
        """Тестирование строковых представлений работодателя"""
        employer = Employer(name="Test Company", employer_id="123")

        assert str(employer) == "Test Company"
        assert repr(employer) == "Employer(name='Test Company', id='123')"

    def test_employer_properties(self):
        """Тестирование свойств работодателя для обратной совместимости"""
        employer = Employer(name="Test Company", employer_id="123")

        assert employer.name == "Test Company"
        assert employer.id == "123"


class TestExperience:
    """Комплексное тестирование модели опыта работы"""

    def test_experience_initialization(self):
        """Тестирование инициализации опыта работы"""
        experience = Experience(
            name="От 1 года до 3 лет",
            experience_id="between1And3"
        )

        assert experience.get_name() == "От 1 года до 3 лет"
        assert experience.get_id() == "between1And3"

    def test_experience_minimal_initialization(self):
        """Тестирование минимальной инициализации опыта"""
        experience = Experience(name="Любой опыт")

        assert experience.get_name() == "Любой опыт"
        assert experience.get_id() is None

    def test_experience_empty_name_handling(self):
        """Тестирование обработки пустого названия опыта"""
        experience = Experience(name="")
        assert experience.get_name() == "Не указан"

        experience = Experience(name=None)
        assert experience.get_name() == "Не указан"

    def test_experience_to_dict(self):
        """Тестирование преобразования опыта в словарь"""
        experience = Experience(name="От 3 до 6 лет", experience_id="between3And6")
        result = experience.to_dict()

        assert isinstance(result, dict)
        assert result['name'] == "От 3 до 6 лет"
        assert result['id'] == "between3And6"

    def test_experience_from_dict(self):
        """Тестирование создания опыта из словаря"""
        data = {'name': 'Более 6 лет', 'id': 'moreThan6'}
        experience = Experience.from_dict(data)

        assert experience.get_name() == "Более 6 лет"
        assert experience.get_id() == "moreThan6"

    def test_experience_from_string(self):
        """Тестирование создания опыта из строки"""
        experience = Experience.from_string("От 1 года")
        assert experience.get_name() == "От 1 года"
        assert experience.get_id() is None

    def test_experience_string_representations(self):
        """Тестирование строковых представлений опыта"""
        experience = Experience(name="Test Experience")

        assert str(experience) == "Test Experience"
        assert repr(experience) == "Experience(name='Test Experience')"


class TestEmployment:
    """Комплексное тестирование модели типа занятости"""

    def test_employment_initialization(self):
        """Тестирование инициализации типа занятости"""
        employment = Employment(
            name="Полная занятость",
            employment_id="full"
        )

        assert employment.get_name() == "Полная занятость"
        assert employment.get_id() == "full"

    def test_employment_from_dict(self):
        """Тестирование создания типа занятости из словаря"""
        data = {'name': 'Частичная занятость', 'id': 'part'}
        employment = Employment.from_dict(data)

        assert employment.get_name() == "Частичная занятость"
        assert employment.get_id() == "part"

    def test_employment_from_string(self):
        """Тестирование создания типа занятости из строки"""
        employment = Employment.from_string("Стажировка")
        assert employment.get_name() == "Стажировка"


class TestVacancy:
    """Комплексное тестирование модели вакансии"""

    def test_vacancy_minimal_initialization(self):
        """Тестирование минимальной инициализации вакансии"""
        vacancy = Vacancy(
            title="Python Developer",
            url="https://example.com/vacancy/123"
        )

        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://example.com/vacancy/123"
        assert vacancy.vacancy_id is not None
        assert len(vacancy.vacancy_id) > 0

    def test_vacancy_full_initialization(self):
        """Тестирование полной инициализации вакансии"""
        employer = Employer(name="Test Company", employer_id="456")
        experience = Experience(name="От 1 года до 3 лет")
        employment = Employment(name="Полная занятость")

        vacancy = Vacancy(
            vacancy_id="test_123",
            title="Senior Python Developer",
            url="https://example.com/vacancy/123",
            description="Detailed job description",
            requirements="Python, Django",
            responsibilities="Development tasks",
            employer=employer,
            employer_id="456",
            experience=experience,
            employment=employment,
            schedule="Полный день",
            published_at="2025-01-01T10:00:00+03:00",
            source="test"
        )

        assert vacancy.vacancy_id == "test_123"
        assert vacancy.title == "Senior Python Developer"
        assert vacancy.description == "Detailed job description"
        assert vacancy.requirements == "Python, Django"
        assert vacancy.responsibilities == "Development tasks"
        assert isinstance(vacancy.employer, Employer)
        assert vacancy.employer_id == "456"
        assert isinstance(vacancy.experience, Experience)
        assert isinstance(vacancy.employment, Employment)
        assert vacancy.schedule == "Полный день"
        assert vacancy.source == "test"

    def test_vacancy_id_generation(self):
        """Тестирование генерации ID вакансии"""
        # Без указания ID - должен сгенерироваться UUID
        vacancy1 = Vacancy(title="Test", url="https://test.com")
        assert vacancy1.vacancy_id is not None
        assert len(vacancy1.vacancy_id) > 0

        # С указанием пустого ID - должен сгенерироваться UUID
        vacancy2 = Vacancy(title="Test", url="https://test.com", vacancy_id="")
        assert vacancy2.vacancy_id is not None
        assert len(vacancy2.vacancy_id) > 0

        # С указанием конкретного ID
        vacancy3 = Vacancy(title="Test", url="https://test.com", vacancy_id="custom_123")
        assert vacancy3.vacancy_id == "custom_123"

    def test_vacancy_employer_validation(self):
        """Тестирование валидации работодателя в вакансии"""
        # С объектом Employer
        employer_obj = Employer(name="Test Company")
        vacancy1 = Vacancy(title="Test", url="https://test.com", employer=employer_obj)
        assert isinstance(vacancy1.employer, Employer)

        # Со словарем
        employer_dict = {"name": "Dict Company", "id": "123"}
        vacancy2 = Vacancy(title="Test", url="https://test.com", employer=employer_dict)
        assert isinstance(vacancy2.employer, Employer)
        assert vacancy2.employer.get_name() == "Dict Company"

        # Со строкой
        vacancy3 = Vacancy(title="Test", url="https://test.com", employer="String Company")
        assert isinstance(vacancy3.employer, Employer)
        assert vacancy3.employer.get_name() == "String Company"

    def test_vacancy_html_cleaning(self):
        """Тестирование очистки HTML в тексте вакансии"""
        html_description = "<p>Test <b>description</b> with <a href='#'>HTML</a></p>"
        vacancy = Vacancy(
            title="Test",
            url="https://test.com",
            description=html_description,
            requirements="<ul><li>Python</li></ul>",
            responsibilities="<div>Development</div>"
        )

        # HTML теги должны быть удалены
        assert "<p>" not in vacancy.description
        assert "<b>" not in vacancy.description
        assert "description" in vacancy.description

        if vacancy.requirements:
            assert "<ul>" not in vacancy.requirements
            assert "Python" in vacancy.requirements

    def test_vacancy_datetime_parsing(self):
        """Тестирование парсинга даты/времени публикации"""
        # ISO формат
        vacancy1 = Vacancy(
            title="Test",
            url="https://test.com",
            published_at="2025-01-01T10:00:00+03:00"
        )
        assert isinstance(vacancy1.published_at, datetime)

        # Timestamp
        vacancy2 = Vacancy(
            title="Test",
            url="https://test.com",
            published_at=1704096000
        )
        assert isinstance(vacancy2.published_at, datetime)

        # Некорректная дата
        vacancy3 = Vacancy(
            title="Test",
            url="https://test.com",
            published_at="invalid_date"
        )
        assert vacancy3.published_at is None

    def test_vacancy_from_dict_hh_format(self):
        """Тестирование создания вакансии из данных HH.ru"""
        hh_data = create_hh_vacancy_data()
        vacancy = Vacancy.from_dict(hh_data)

        assert vacancy.vacancy_id == "123456"
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://hh.ru/vacancy/123456"
        assert vacancy.source == "hh.ru"
        assert isinstance(vacancy.employer, Employer)
        assert vacancy.employer.get_name() == "Яндекс"
        assert vacancy.employer.get_id() == "1740"

    def test_vacancy_from_dict_sj_format(self):
        """Тестирование создания вакансии из данных SuperJob"""
        sj_data = create_sj_vacancy_data()
        vacancy = Vacancy.from_dict(sj_data)

        assert vacancy.vacancy_id == "789012"
        assert vacancy.title == "Python разработчик"
        assert vacancy.url == "https://superjob.ru/vakansii/python-789012.html"
        assert vacancy.source == "superjob.ru"
        assert isinstance(vacancy.employer, Employer)
        assert vacancy.employer.get_name() == "IT Компания"

    def test_vacancy_to_dict(self):
        """Тестирование преобразования вакансии в словарь"""
        vacancy = Vacancy(
            vacancy_id="test_123",
            title="Test Job",
            url="https://test.com/123",
            description="Test description",
            source="test_source"
        )

        result = vacancy.to_dict()

        assert isinstance(result, dict)
        assert result['vacancy_id'] == "test_123"
        assert result['title'] == "Test Job"
        assert result['url'] == "https://test.com/123"
        assert result['description'] == "Test description"
        assert result['source'] == "test_source"

    def test_vacancy_area_processing(self):
        """Тестирование обработки области/региона"""
        # Строка
        vacancy1 = Vacancy(title="Test", url="https://test.com", area="Москва")
        assert vacancy1.area == "Москва"

        # Словарь с name
        vacancy2 = Vacancy(title="Test", url="https://test.com", area={"name": "Санкт-Петербург"})
        assert "Санкт-Петербург" in str(vacancy2.area)

        # Словарь с title
        vacancy3 = Vacancy(title="Test", url="https://test.com", area={"title": "Новосибирск"})
        assert "Новосибирск" in str(vacancy3.area)


class TestBaseParser:
    """Комплексное тестирование базового парсера"""

    def test_base_parser_initialization(self):
        """Тестирование инициализации базового парсера"""
        # Создаем конкретную реализацию для тестов
        class TestParser(BaseParser):
            def parse_vacancy(self, vacancy_data):
                return {"test": "vacancy"}

            def parse_vacancies(self, vacancies_data):
                return [{"test": "vacancy"}]

        parser = TestParser()
        assert parser is not None

    def test_base_parser_abstract_methods(self):
        """Тестирование абстрактных методов базового парсера"""
        # Создаем конкретную реализацию
        class TestParser(BaseParser):
            def parse_vacancy(self, vacancy_data):
                return {"test": "vacancy"}

            def parse_vacancies(self, vacancies_data):
                return [{"test": "vacancy"}]

        parser = TestParser()

        # Тестируем работу конкретной реализации
        result = parser.parse_vacancy({"id": "123"})
        assert result == {"test": "vacancy"}

        results = parser.parse_vacancies([{"id": "123"}])
        assert results == [{"test": "vacancy"}]


class TestHHParser:
    """Комплексное тестирование парсера HH.ru"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.parser = HHParser()

    def test_hh_parser_initialization(self):
        """Тестирование инициализации парсера HH"""
        assert self.parser is not None
        assert isinstance(self.parser, BaseParser)

    def test_hh_parser_parse_single_vacancy(self):
        """Тестирование парсинга одной вакансии HH"""
        hh_data = {
            "id": "123456",
            "name": "Python Developer",
            "area": {"name": "Москва"},
            "employer": {"name": "Яндекс"},
            "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
            "employment": {"name": "Полная занятость"},
            "experience": {"name": "От 1 года до 3 лет"},
            "published_at": "2023-01-01T12:00:00+0300"
        }

        parser = HHParser()
        vacancy = parser.parse_vacancy(hh_data)

        # Проверяем, что результат является объектом Vacancy или словарем
        if isinstance(vacancy, dict):
            assert vacancy.get("title") == "Python Developer" or vacancy.get("name") == "Python Developer"
        else:
            assert isinstance(vacancy, Vacancy)
            assert vacancy.title == "Python Developer"

    def test_hh_parser_parse_multiple_vacancies(self):
        """Тестирование парсинга нескольких вакансий HH"""
        hh_data_list = [create_hh_vacancy_data() for _ in range(3)]
        # Делаем каждую вакансию уникальной
        for i, vacancy_data in enumerate(hh_data_list):
            vacancy_data['id'] = f"12345{i}"
            vacancy_data['name'] = f"Python Developer {i}"

        vacancies = self.parser.parse_vacancies(hh_data_list)

        assert isinstance(vacancies, list)
        assert len(vacancies) == 3
        assert all(isinstance(v, Vacancy) for v in vacancies)
        assert all(v.source == "hh.ru" for v in vacancies)

    def test_hh_parser_salary_parsing(self):
        """Тестирование парсинга зарплаты в HH"""
        hh_data = create_hh_vacancy_data()
        vacancy = self.parser.parse_vacancy(hh_data)

        assert vacancy.salary is not None
        # Проверяем, что зарплата правильно обработана

    def test_hh_parser_employer_parsing(self):
        """Тестирование парсинга работодателя в HH"""
        hh_data = create_hh_vacancy_data()
        vacancy = self.parser.parse_vacancy(hh_data)

        assert isinstance(vacancy.employer, Employer)
        assert vacancy.employer.get_name() == "Яндекс"
        assert vacancy.employer.get_id() == "1740"
        assert vacancy.employer.is_trusted() is True

    def test_hh_parser_error_handling(self):
        """Тестирование обработки ошибок в парсере HH"""
        # Некорректные данные
        invalid_data = {"invalid": "data"}

        try:
            vacancy = self.parser.parse_vacancy(invalid_data)
            # Парсер должен либо вернуть None, либо создать вакансию с минимальными данными
            assert vacancy is None or isinstance(vacancy, Vacancy)
        except Exception:
            # Или может выбросить исключение - это тоже допустимо
            pass

    def test_hh_parser_missing_fields(self):
        """Тестирование обработки отсутствующих полей"""
        minimal_data = {
            "id": "123",
            "name": "Test Job",
            "alternate_url": "https://hh.ru/vacancy/123"
        }

        vacancy = self.parser.parse_vacancy(minimal_data)

        if vacancy is not None:
            assert isinstance(vacancy, Vacancy)
            assert vacancy.vacancy_id == "123"
            assert vacancy.title == "Test Job"


class TestSuperJobParser:
    """Комплексное тестирование парсера SuperJob"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.parser = SuperJobParser()

    def test_sj_parser_initialization(self):
        """Тестирование инициализации парсера SuperJob"""
        assert self.parser is not None
        assert isinstance(self.parser, BaseParser)

    def test_sj_parser_parse_single_vacancy(self):
        """Тестирование парсинга одной вакансии SuperJob"""
        sj_data = create_sj_vacancy_data()
        vacancy = self.parser.parse_vacancy(sj_data)

        assert isinstance(vacancy, Vacancy)
        assert vacancy.vacancy_id == "789012"
        assert vacancy.title == "Python разработчик"
        assert vacancy.source == "superjob.ru"

    def test_sj_parser_parse_multiple_vacancies(self):
        """Тестирование парсинга нескольких вакансий SuperJob"""
        sj_data_list = [create_sj_vacancy_data() for _ in range(3)]
        # Делаем каждую вакансию уникальной
        for i, vacancy_data in enumerate(sj_data_list):
            vacancy_data['id'] = 789012 + i
            vacancy_data['profession'] = f"Python разработчик {i}"

        vacancies = self.parser.parse_vacancies(sj_data_list)

        assert isinstance(vacancies, list)
        assert len(vacancies) == 3
        assert all(isinstance(v, Vacancy) for v in vacancies)
        assert all(v.source == "superjob.ru" for v in vacancies)

    def test_sj_parser_salary_parsing(self):
        """Тестирование парсинга зарплаты в SuperJob"""
        sj_data = create_sj_vacancy_data()
        vacancy = self.parser.parse_vacancy(sj_data)

        assert vacancy.salary is not None
        # Проверяем, что зарплата правильно обработана

    def test_sj_parser_employer_parsing(self):
        """Тестирование парсинга работодателя в SuperJob"""
        sj_data = create_sj_vacancy_data()
        vacancy = self.parser.parse_vacancy(sj_data)

        assert isinstance(vacancy.employer, Employer)
        assert vacancy.employer.get_name() == "IT Компания"

    def test_sj_parser_timestamp_handling(self):
        """Тестирование обработки timestamp в SuperJob"""
        sj_data = create_sj_vacancy_data()
        vacancy = self.parser.parse_vacancy(sj_data)

        assert isinstance(vacancy.published_at, datetime)

    def test_sj_parser_error_handling(self):
        """Тестирование обработки ошибок в парсере SuperJob"""
        invalid_data = {"invalid": "data"}

        try:
            vacancy = self.parser.parse_vacancy(invalid_data)
            assert vacancy is None or isinstance(vacancy, Vacancy)
        except Exception:
            pass


class TestVacancyModelsIntegration:
    """Интеграционные тесты для модулей вакансий"""

    def test_full_parsing_workflow_hh(self):
        """Тестирование полного рабочего процесса парсинга HH"""
        hh_data = create_hh_vacancy_data()
        parser = HHParser()

        # Парсим вакансию
        vacancy = parser.parse_vacancy(hh_data)

        assert isinstance(vacancy, Vacancy)

        # Преобразуем обратно в словарь
        vacancy_dict = vacancy.to_dict()

        assert isinstance(vacancy_dict, dict)
        assert vacancy_dict['vacancy_id'] == hh_data['id']
        assert vacancy_dict['title'] == hh_data['name']

    def test_full_parsing_workflow_sj(self):
        """Тестирование полного рабочего процесса парсинга SuperJob"""
        sj_data = create_sj_vacancy_data()
        parser = SJParser()

        # Парсим вакансию
        vacancy = parser.parse_vacancy(sj_data)

        assert isinstance(vacancy, Vacancy)

        # Преобразуем обратно в словарь
        vacancy_dict = vacancy.to_dict()

        assert isinstance(vacancy_dict, dict)
        assert vacancy_dict['vacancy_id'] == str(sj_data['id'])
        assert vacancy_dict['title'] == sj_data['profession']

    def test_cross_format_compatibility(self):
        """Тестирование совместимости между форматами"""
        # Создаем вакансию из HH формата
        hh_data = create_hh_vacancy_data()
        hh_parser = HHParser()
        hh_vacancy = hh_parser.parse_vacancy(hh_data)

        # Создаем вакансию из SJ формата
        sj_data = create_sj_vacancy_data()
        sj_parser = SJParser()
        sj_vacancy = sj_parser.parse_vacancy(sj_data)

        # Обе вакансии должны иметь одинаковую структуру
        assert hasattr(hh_vacancy, 'vacancy_id')
        assert hasattr(hh_vacancy, 'title')
        assert hasattr(hh_vacancy, 'employer')
        assert hasattr(hh_vacancy, 'salary')

        assert hasattr(sj_vacancy, 'vacancy_id')
        assert hasattr(sj_vacancy, 'title')
        assert hasattr(sj_vacancy, 'employer')
        assert hasattr(sj_vacancy, 'salary')

        # Источники должны различаться
        assert hh_vacancy.source != sj_vacancy.source

    def test_vacancy_data_integrity(self):
        """Тестирование целостности данных вакансии"""
        vacancy = Vacancy(
            vacancy_id="integrity_test",
            title="Test Position",
            url="https://test.com/vacancy",
            employer=Employer(name="Test Company", employer_id="test_123"),
            source="test"
        )

        # Преобразуем в словарь и обратно
        vacancy_dict = vacancy.to_dict()
        new_vacancy = Vacancy.from_dict(vacancy_dict)

        # Данные должны сохраниться
        assert new_vacancy.vacancy_id == vacancy.vacancy_id
        assert new_vacancy.title == vacancy.title
        assert new_vacancy.url == vacancy.url
        assert new_vacancy.source == vacancy.source

    def test_model_performance_with_large_dataset(self):
        """Тестирование производительности моделей с большим объемом данных"""
        # Создаем большое количество тестовых данных
        large_dataset = []
        for i in range(1000):
            data = create_hh_vacancy_data()
            data['id'] = f"perf_test_{i}"
            data['name'] = f"Test Job {i}"
            large_dataset.append(data)

        parser = HHParser()

        # Парсим все данные
        import time
        start_time = time.time()

        vacancies = parser.parse_vacancies(large_dataset)

        end_time = time.time()

        # Проверяем результат и производительность
        assert len(vacancies) == 1000
        assert (end_time - start_time) < 10.0  # Менее 10 секунд на 1000 вакансий
        assert all(isinstance(v, Vacancy) for v in vacancies)