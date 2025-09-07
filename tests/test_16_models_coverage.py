#!/usr/bin/env python3
"""
Тесты для 100% покрытия src/vacancies/models.py
Покрываем все Pydantic v2 модели с валидацией и методами совместимости.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional, List

# Импорты из реального кода для покрытия
from src.vacancies.models import (
    Employer, 
    Experience,
    Employment,
    Schedule,
    Vacancy,
    VacancyFactory
)
from src.utils.salary import Salary
from pydantic import ValidationError


class TestEmployer:
    """100% покрытие модели Employer"""
    
    def test_employer_creation_basic(self):
        """Покрытие базового создания работодателя"""
        employer = Employer(name="Test Company")
        
        assert employer.name == "Test Company"
        assert employer.id is None
        assert employer.trusted is None
        assert employer.alternate_url is None
    
    def test_employer_creation_full(self):
        """Покрытие создания с полными данными"""
        employer = Employer(
            name="Full Company",
            id="123",
            trusted=True,
            alternate_url="https://company.com"
        )
        
        assert employer.name == "Full Company"
        assert employer.id == "123"
        assert employer.trusted is True
        assert employer.alternate_url == "https://company.com"
    
    def test_employer_name_validation_empty(self):
        """Покрытие валидации пустого имени"""
        # Пустое имя вызывает ValidationError (min_length=1)
        with pytest.raises(ValidationError):
            Employer(name="")
        
        # Пробелы преобразуются валидатором в "Не указана"
        employer = Employer(name="   ")
        assert employer.name == "Не указана"
    
    def test_employer_name_validation_strip(self):
        """Покрытие удаления пробелов из имени"""
        employer = Employer(name="  Company Name  ")
        assert employer.name == "Company Name"
    
    def test_employer_url_validation_add_protocol(self):
        """Покрытие добавления протокола к URL"""
        employer = Employer(name="Test", alternate_url="company.com")
        assert employer.alternate_url == "https://company.com"
    
    def test_employer_url_validation_existing_protocol(self):
        """Покрытие URL с существующим протоколом"""
        employer = Employer(name="Test", alternate_url="http://company.com")
        assert employer.alternate_url == "http://company.com"
        
        employer = Employer(name="Test", alternate_url="https://company.com")
        assert employer.alternate_url == "https://company.com"
    
    def test_employer_url_validation_none(self):
        """Покрытие None URL"""
        employer = Employer(name="Test", alternate_url=None)
        assert employer.alternate_url is None
    
    def test_employer_compatibility_methods(self):
        """Покрытие методов совместимости"""
        employer = Employer(
            name="Test Company",
            id="123", 
            trusted=True,
            alternate_url="https://test.com"
        )
        
        assert employer.get_name() == "Test Company"
        assert employer.get_id() == "123"
        assert employer.is_trusted() is True
        assert employer.get_url() == "https://test.com"
    
    def test_employer_to_dict(self):
        """Покрытие метода to_dict"""
        employer = Employer(name="Test", id="123")
        result = employer.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "Test"
        assert result["id"] == "123"
    
    def test_employer_from_dict(self):
        """Покрытие метода from_dict"""
        data = {"name": "Dict Company", "id": "dict_123", "trusted": False}
        employer = Employer.from_dict(data)
        
        assert employer.name == "Dict Company"
        assert employer.id == "dict_123"
        assert employer.trusted is False
    
    def test_employer_get_method(self):
        """Покрытие dictionary-like доступа"""
        employer = Employer(name="Test", id="123")
        
        assert employer.get("name") == "Test"
        assert employer.get("id") == "123"
        assert employer.get("nonexistent") is None
        assert employer.get("nonexistent", "default") == "default"


class TestExperience:
    """100% покрытие модели Experience"""
    
    def test_experience_creation_basic(self):
        """Покрытие базового создания опыта"""
        experience = Experience(name="1-3 года")
        
        assert experience.name == "1-3 года"
        assert experience.id is None
    
    def test_experience_creation_full(self):
        """Покрытие создания с полными данными"""
        experience = Experience(name="3-6 лет", id="exp_123")
        
        assert experience.name == "3-6 лет"
        assert experience.id == "exp_123"
    
    def test_experience_name_validation_empty(self):
        """Покрытие валидации пустого имени"""
        # Пустое имя возвращает "Не указан"
        experience = Experience(name="")
        assert experience.name == "Не указан"
        
        # None вызывает ValidationError (type validation)
        with pytest.raises(ValidationError):
            Experience(name=None)
    
    def test_experience_name_validation_strip(self):
        """Покрытие удаления пробелов"""
        experience = Experience(name="  Без опыта  ")
        assert experience.name == "Без опыта"
    
    def test_experience_compatibility_methods(self):
        """Покрытие методов совместимости"""
        experience = Experience(name="Senior", id="exp_456")
        
        assert experience.get_name() == "Senior"
        assert experience.get_id() == "exp_456"
    
    def test_experience_to_dict(self):
        """Покрытие метода to_dict"""
        experience = Experience(name="Middle", id="exp_789")
        result = experience.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "Middle"
        assert result["id"] == "exp_789"
    
    def test_experience_from_dict(self):
        """Покрытие метода from_dict"""
        data = {"name": "Junior", "id": "exp_junior"}
        experience = Experience.from_dict(data)
        
        assert experience.name == "Junior"
        assert experience.id == "exp_junior"
    
    def test_experience_from_string(self):
        """Покрытие метода from_string"""
        experience = Experience.from_string("Стажер")
        
        assert experience.name == "Стажер"
        assert experience.id is None


class TestEmployment:
    """100% покрытие модели Employment"""
    
    def test_employment_creation_basic(self):
        """Покрытие базового создания типа занятости"""
        employment = Employment(name="Полная занятость")
        
        assert employment.name == "Полная занятость"
        assert employment.id is None
    
    def test_employment_creation_full(self):
        """Покрытие создания с полными данными"""
        employment = Employment(name="Частичная занятость", id="part_time")
        
        assert employment.name == "Частичная занятость"
        assert employment.id == "part_time"
    
    def test_employment_name_validation_empty(self):
        """Покрытие валидации пустого имени"""
        # Пустое имя возвращает "Не указан"
        employment = Employment(name="")
        assert employment.name == "Не указан"
        
        # None вызывает ValidationError (type validation)
        with pytest.raises(ValidationError):
            Employment(name=None)
    
    def test_employment_name_validation_strip(self):
        """Покрытие удаления пробелов"""
        employment = Employment(name="  Стажировка  ")
        assert employment.name == "Стажировка"
    
    def test_employment_compatibility_methods(self):
        """Покрытие методов совместимости"""
        employment = Employment(name="Проектная работа", id="project")
        
        assert employment.get_name() == "Проектная работа"
        assert employment.get_id() == "project"
    
    def test_employment_to_dict(self):
        """Покрытие метода to_dict"""
        employment = Employment(name="Волонтерство", id="volunteer")
        result = employment.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "Волонтерство"
        assert result["id"] == "volunteer"
    
    def test_employment_from_dict(self):
        """Покрытие метода from_dict"""
        data = {"name": "Фриланс", "id": "freelance"}
        employment = Employment.from_dict(data)
        
        assert employment.name == "Фриланс"
        assert employment.id == "freelance"
    
    def test_employment_from_string(self):
        """Покрытие метода from_string"""
        employment = Employment.from_string("Удаленная работа")
        
        assert employment.name == "Удаленная работа"
        assert employment.id is None


class TestSchedule:
    """100% покрытие модели Schedule"""
    
    def test_schedule_creation_basic(self):
        """Покрытие базового создания графика"""
        schedule = Schedule(name="Полный день")
        
        assert schedule.name == "Полный день"
        assert schedule.id is None
    
    def test_schedule_creation_full(self):
        """Покрытие создания с полными данными"""
        schedule = Schedule(name="Гибкий график", id="flexible")
        
        assert schedule.name == "Гибкий график"
        assert schedule.id == "flexible"
    
    def test_schedule_name_validation_empty(self):
        """Покрытие валидации пустого имени"""
        # Пустое имя возвращает "Не указан"
        schedule = Schedule(name="")
        assert schedule.name == "Не указан"
        
        # None вызывает ValidationError (type validation)
        with pytest.raises(ValidationError):
            Schedule(name=None)
    
    def test_schedule_name_validation_strip(self):
        """Покрытие удаления пробелов"""
        schedule = Schedule(name="  Сменный график  ")
        assert schedule.name == "Сменный график"
    
    def test_schedule_compatibility_methods(self):
        """Покрытие методов совместимости"""
        schedule = Schedule(name="Ночная смена", id="night")
        
        assert schedule.get_name() == "Ночная смена"
        assert schedule.get_id() == "night"
    
    def test_schedule_to_dict(self):
        """Покрытие метода to_dict"""
        schedule = Schedule(name="Выходные", id="weekend")
        result = schedule.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "Выходные"
        assert result["id"] == "weekend"
    
    def test_schedule_from_dict(self):
        """Покрытие метода from_dict"""
        data = {"name": "24/7", "id": "round_clock"}
        schedule = Schedule.from_dict(data)
        
        assert schedule.name == "24/7"
        assert schedule.id == "round_clock"
    
    def test_schedule_from_string(self):
        """Покрытие метода from_string"""
        schedule = Schedule.from_string("4/2")
        
        assert schedule.name == "4/2"
        assert schedule.id is None


class TestVacancy:
    """100% покрытие модели Vacancy"""
    
    def test_vacancy_creation_minimal(self):
        """Покрытие минимального создания вакансии"""
        vacancy = Vacancy(
            vacancy_id="test_123",
            name="Python Developer",
            alternate_url="https://test.com/vacancy/123"
        )
        
        assert vacancy.title == "Python Developer"
        assert vacancy.id == "test_123"
        assert vacancy.url == "https://test.com/vacancy/123"
    
    def test_vacancy_creation_full(self):
        """Покрытие создания с полными данными"""
        employer = Employer(name="Full Company", id="emp_123")
        experience = Experience(name="3-6 лет", id="exp_123")
        employment = Employment(name="Полная занятость", id="full")
        schedule = Schedule(name="Полный день", id="full_day")
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        
        vacancy = Vacancy(
            vacancy_id="senior_123",
            name="Senior Python Developer",
            alternate_url="https://job.com/vacancy/123",
            employer=employer,
            experience=experience,
            employment=employment,
            schedule=schedule,
            salary=salary_data,
            description="Описание вакансии",
            area="Москва",
            source="hh"
        )
        
        assert vacancy.title == "Senior Python Developer"
        assert vacancy.id == "senior_123"
        assert vacancy.employer == employer
        assert vacancy.experience == experience
        assert vacancy.employment == employment
        assert vacancy.schedule == schedule
        assert vacancy.salary == salary_data
        assert vacancy.url == "https://job.com/vacancy/123"
        assert vacancy.description == "Описание вакансии"
        assert vacancy.area == "Москва"
        assert vacancy.source == "hh"
    
    def test_vacancy_title_validation_empty(self):
        """Покрытие валидации пустого заголовка"""
        # Пустой title должен вызывать ValidationError согласно validator
        with pytest.raises(ValidationError):
            Vacancy(
                vacancy_id="test_empty",
                name="",
                alternate_url="https://test.com"
            )
    
    def test_vacancy_title_validation_strip(self):
        """Покрытие удаления пробелов из заголовка"""
        vacancy = Vacancy(
            vacancy_id="test_strip",
            name="  Developer Position  ",
            alternate_url="https://test.com"
        )
        assert vacancy.title == "Developer Position"
    
    def test_vacancy_url_validation_add_protocol(self):
        """Покрытие добавления протокола к URL"""
        vacancy = Vacancy(
            vacancy_id="test_protocol",
            name="Test",
            alternate_url="job-site.com/vacancy/123"
        )
        assert vacancy.url == "https://job-site.com/vacancy/123"
    
    def test_vacancy_url_validation_existing_protocol(self):
        """Покрытие URL с существующим протоколом"""
        vacancy = Vacancy(
            vacancy_id="test_http",
            name="Test",
            alternate_url="http://job-site.com/vacancy/123"
        )
        assert vacancy.url == "http://job-site.com/vacancy/123"
    
    def test_vacancy_url_validation_none(self):
        """Покрытие None URL"""
        # None URL должен вызывать ValidationError согласно validator
        with pytest.raises(ValidationError):
            Vacancy(
                vacancy_id="test_none",
                name="Test",
                alternate_url=None
            )
    
    def test_vacancy_compatibility_methods(self):
        """Покрытие методов совместимости"""
        employer = Employer(name="Test Company")
        vacancy = Vacancy(
            vacancy_id="test_compat",
            name="Test Job",
            alternate_url="https://test.com",
            employer=employer,
            description="Test description",
            area="Moscow"
        )
        
        # Проверяем прямой доступ к атрибутам (методы get_ не реализованы в Vacancy)
        assert vacancy.title == "Test Job"
        assert vacancy.employer == employer
        assert vacancy.url == "https://test.com"
        assert vacancy.description == "Test description"
        assert vacancy.area == "Moscow"
    
    def test_vacancy_to_dict(self):
        """Покрытие метода to_dict"""
        vacancy = Vacancy(
            vacancy_id="test_dict",
            name="Test",
            alternate_url="https://test.com"
        )
        result = vacancy.to_dict()
        
        assert isinstance(result, dict)
        assert result["title"] == "Test"
        assert result["id"] == "test_dict"
        assert result["url"] == "https://test.com"
    
    def test_vacancy_from_dict(self):
        """Покрытие метода from_dict"""
        data = {
            "vacancy_id": "dict_123",
            "name": "Dict Vacancy",
            "alternate_url": "https://dict.com",
            "employer": {"name": "Dict Company"}
        }
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.title == "Dict Vacancy"
        assert vacancy.id == "dict_123"
        assert vacancy.url == "https://dict.com"
        assert vacancy.employer.name == "Dict Company"
    
    def test_vacancy_attribute_access(self):
        """Покрытие доступа к атрибутам Vacancy"""
        vacancy = Vacancy(
            vacancy_id="test_attr",
            name="Test",
            alternate_url="https://test.com",
            area="SPB"
        )
        
        # Проверяем прямой доступ к атрибутам
        assert vacancy.title == "Test"
        assert vacancy.area == "SPB"
        assert vacancy.id == "test_attr"
        assert vacancy.url == "https://test.com"


class TestVacancyFactory:
    """100% покрытие VacancyFactory"""
    
    def test_factory_from_hh_api_minimal(self):
        """Покрытие создания из минимальных HH данных"""
        data = {
            "id": "123",
            "name": "HH Job",
            "alternate_url": "https://hh.ru/vacancy/123"
        }
        
        vacancy = VacancyFactory.from_hh_api(data)
        
        assert isinstance(vacancy, Vacancy)
        assert vacancy.title == "HH Job"
        assert vacancy.id == "123"
        assert vacancy.source == "hh.ru"
    
    def test_factory_from_hh_api_full(self):
        """Покрытие создания из полных HH данных"""
        data = {
            "id": "456",
            "name": "Full HH Job",
            "alternate_url": "https://hh.ru/vacancy/456",
            "employer": {"name": "HH Corp", "id": "123"},
            "experience": {"name": "5+ лет", "id": "senior"},
            "employment": {"name": "Полная", "id": "full"},
            "schedule": {"name": "Офис", "id": "office"},
            "salary": {"from": 80000, "to": 120000, "currency": "RUR"},
            "snippet": {"requirement": "Python skills", "responsibility": "Development"},
            "area": {"name": "Екатеринбург"},
            "published_at": "2023-01-01T12:00:00",
            "description": "Job description"
        }
        
        vacancy = VacancyFactory.from_hh_api(data)
        
        assert vacancy.title == "Full HH Job"
        assert vacancy.employer.name == "HH Corp"
        assert vacancy.source == "hh.ru"
        assert vacancy.area == "Екатеринбург"
        assert vacancy.requirements == "Python skills"
        assert vacancy.responsibilities == "Development"
    
    def test_factory_from_superjob_api(self):
        """Покрытие создания из SuperJob данных"""
        data = {
            "id": "789",
            "profession": "SuperJob Developer",
            "link": "https://superjob.ru/vacancy/789",
            "payment_from": 100000,
            "payment_to": 150000,
            "firm_name": "SuperJob Company"
        }
        
        vacancy = VacancyFactory.from_superjob_api(data)
        
        assert isinstance(vacancy, Vacancy)
        assert vacancy.title == "SuperJob Developer"
        assert vacancy.id == "789"
        assert vacancy.source == "superjob.ru"
    
    def test_factory_experience_handling(self):
        """Покрытие обработки опыта в Factory методах"""
        # Тестируем создание вакансии с опытом
        data_with_exp = {
            "id": "exp_test",
            "name": "Job with Experience",
            "alternate_url": "https://test.com/exp",
            "experience": {"name": "Middle", "id": "mid"}
        }
        
        vacancy = VacancyFactory.from_hh_api(data_with_exp)
        
        assert isinstance(vacancy.experience, Experience)
        assert vacancy.experience.name == "Middle"
        assert vacancy.experience.id == "mid"
    
    def test_factory_employment_handling(self):
        """Покрытие обработки типа занятости в Factory методах"""
        # Тестируем создание вакансии с типом занятости
        data_with_emp = {
            "id": "emp_test",
            "name": "Job with Employment",
            "alternate_url": "https://test.com/emp",
            "employment": {"name": "Частичная", "id": "part"}
        }
        
        vacancy = VacancyFactory.from_hh_api(data_with_emp)
        
        assert isinstance(vacancy.employment, Employment)
        assert vacancy.employment.name == "Частичная"
        assert vacancy.employment.id == "part"
    
    def test_factory_schedule_handling(self):
        """Покрытие обработки графика в Factory методах"""
        data_with_schedule = {
            "id": "sch_test",
            "name": "Job with Schedule",
            "alternate_url": "https://test.com/sch",
            "schedule": {"name": "Удаленно", "id": "remote"}
        }
        
        vacancy = VacancyFactory.from_hh_api(data_with_schedule)
        
        assert isinstance(vacancy.schedule, Schedule)
        assert vacancy.schedule.name == "Удаленно"
        assert vacancy.schedule.id == "remote"
    
    def test_factory_salary_handling(self):
        """Покрытие обработки зарплаты в Factory методах"""
        data_with_salary = {
            "id": "sal_test",
            "name": "Job with Salary",
            "alternate_url": "https://test.com/sal",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"}
        }
        
        vacancy = VacancyFactory.from_hh_api(data_with_salary)
        
        assert vacancy.salary is not None
        assert vacancy.salary["from"] == 100000
        assert vacancy.salary["to"] == 150000
    
    def test_factory_area_extraction(self):
        """Покрытие извлечения области из API данных"""
        data_with_area = {
            "id": "area_test",
            "name": "Job in Area",
            "alternate_url": "https://test.com/area",
            "area": {"name": "Новосибирск"}
        }
        
        vacancy = VacancyFactory.from_hh_api(data_with_area)
        
        assert vacancy.area == "Новосибирск"
    
    def test_factory_description_extraction(self):
        """Покрытие извлечения описания из snippet"""
        data_with_snippet = {
            "id": "snippet_test",
            "name": "Job with Snippet",
            "alternate_url": "https://test.com/snippet",
            "snippet": {
                "requirement": "Python skills",
                "responsibility": "Development tasks"
            }
        }
        
        vacancy = VacancyFactory.from_hh_api(data_with_snippet)
        
        assert vacancy.requirements == "Python skills"
        assert vacancy.responsibilities == "Development tasks"
    
    def test_factory_superjob_salary_handling(self):
        """Покрытие обработки зарплаты SuperJob"""
        data_with_payment = {
            "id": "sj_payment_test",
            "profession": "SuperJob with Payment",
            "link": "https://superjob.ru/payment",
            "payment_from": 80000,
            "payment_to": 120000,
            "firm_name": "SJ Company"
        }
        
        vacancy = VacancyFactory.from_superjob_api(data_with_payment)
        
        assert vacancy.salary is not None
        assert vacancy.salary["from"] == 80000
        assert vacancy.salary["to"] == 120000
        assert vacancy.salary["currency"] == "RUR"
    
    def test_factory_empty_data_handling(self):
        """Покрытие обработки пустых данных"""
        # Минимальные данные без опциональных полей
        minimal_data = {
            "id": "minimal_test",
            "name": "Minimal Job",
            "alternate_url": "https://test.com/minimal"
        }
        
        vacancy = VacancyFactory.from_hh_api(minimal_data)
        
        assert vacancy.title == "Minimal Job"
        assert vacancy.employer is None
        assert vacancy.salary is None
        assert vacancy.experience is None
    
    def test_factory_uuid_generation(self):
        """Покрытие генерации UUID для вакансий без ID"""
        # Данные без ID
        data_no_id = {
            "name": "Job without ID",
            "alternate_url": "https://test.com/no-id"
        }
        
        vacancy = VacancyFactory.from_hh_api(data_no_id)
        
        # Проверяем что UUID был сгенерирован
        assert vacancy.id is not None
        assert len(vacancy.id) > 0
        assert vacancy.title == "Job without ID"
    
    def test_factory_published_at_handling(self):
        """Покрытие обработки даты публикации"""
        data_with_date = {
            "id": "date_test",
            "name": "Job with Date",
            "alternate_url": "https://test.com/date",
            "published_at": "2023-01-01T12:00:00"
        }
        
        vacancy = VacancyFactory.from_hh_api(data_with_date)
        
        # published_at преобразуется в datetime объект валидатором
        assert vacancy.published_at is not None
        assert str(vacancy.published_at).startswith("2023-01-01")
        assert vacancy.source == "hh.ru"


class TestModelValidation:
    """100% покрытие валидации Pydantic"""
    
    def test_required_fields_validation(self):
        """Покрытие валидации обязательных полей"""
        # Employer без name
        with pytest.raises(ValidationError):
            Employer()
        
        # Experience без name
        with pytest.raises(ValidationError):
            Experience()
        
        # Vacancy без обязательных полей
        with pytest.raises(ValidationError):
            Vacancy()
    
    def test_field_assignment_validation(self):
        """Покрытие validate_assignment=True"""
        employer = Employer(name="Test")
        
        # Валидное присваивание
        employer.name = "New Name"
        assert employer.name == "New Name"
        
        # Присваивание пустого имени вызывает ValidationError (min_length=1)
        with pytest.raises(ValidationError):
            employer.name = ""


class TestEdgeCases:
    """Покрытие крайних случаев и специфичных ветвей"""
    
    def test_large_data_handling(self):
        """Покрытие обработки больших объемов данных"""
        large_description = "A" * 10000  # Большое описание
        
        vacancy = Vacancy(
            vacancy_id="large_test",
            name="Large Data Test",
            alternate_url="https://test.com/large",
            description=large_description
        )
        
        assert len(vacancy.description) == 10000
        assert vacancy.title == "Large Data Test"
    
    def test_unicode_handling(self):
        """Покрытие обработки Unicode символов"""
        employer = Employer(name="Компания 测试 🏢")
        experience = Experience(name="Опыт работы с Unicode 🔧")
        
        assert "测试" in employer.name
        assert "🔧" in experience.name
    
    def test_nested_dict_access(self):
        """Покрытие глубокого доступа к вложенным данным"""
        complex_data = {
            "id": "complex_test",
            "name": "Complex Job",
            "alternate_url": "https://test.com/complex",
            "employer": {
                "name": "Nested Company",
                "id": "nested_123"
            },
            "snippet": {
                "requirement": "Complex requirement",
                "responsibility": None  # None значение
            }
        }
        
        vacancy = VacancyFactory.from_hh_api(complex_data)
        
        assert vacancy.title == "Complex Job"
        assert vacancy.employer.name == "Nested Company"
        assert vacancy.requirements == "Complex requirement"
        assert vacancy.responsibilities is None