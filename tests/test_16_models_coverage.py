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
        # Пустое имя должно вызывать ValidationError
        with pytest.raises(ValidationError):
            Employer(name="")
        
        with pytest.raises(ValidationError):
            Employer(name="   ")
    
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
        # Пустое имя должно вызывать ValidationError
        with pytest.raises(ValidationError):
            Experience(name="")
        
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
        with pytest.raises(ValidationError):
            Employment(name="")
        
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
        with pytest.raises(ValidationError):
            Schedule(name="")
        
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
        vacancy = Vacancy(
            title="",
            employer=Employer(name="Test")
        )
        assert vacancy.title == "Название не указано"
        
        vacancy = Vacancy(
            title="   ",
            employer=Employer(name="Test")
        )
        assert vacancy.title == "Название не указано"
    
    def test_vacancy_title_validation_strip(self):
        """Покрытие удаления пробелов из заголовка"""
        vacancy = Vacancy(
            title="  Developer Position  ",
            employer=Employer(name="Test")
        )
        assert vacancy.title == "Developer Position"
    
    def test_vacancy_url_validation_add_protocol(self):
        """Покрытие добавления протокола к URL"""
        vacancy = Vacancy(
            title="Test",
            employer=Employer(name="Test"),
            url="job-site.com/vacancy/123"
        )
        assert vacancy.url == "https://job-site.com/vacancy/123"
    
    def test_vacancy_url_validation_existing_protocol(self):
        """Покрытие URL с существующим протоколом"""
        vacancy = Vacancy(
            title="Test",
            employer=Employer(name="Test"),
            url="http://job-site.com/vacancy/123"
        )
        assert vacancy.url == "http://job-site.com/vacancy/123"
    
    def test_vacancy_url_validation_none(self):
        """Покрытие None URL"""
        vacancy = Vacancy(
            title="Test",
            employer=Employer(name="Test"),
            url=None
        )
        assert vacancy.url is None
    
    def test_vacancy_compatibility_methods(self):
        """Покрытие методов совместимости"""
        employer = Employer(name="Test Company")
        vacancy = Vacancy(
            title="Test Job",
            employer=employer,
            url="https://test.com",
            description="Test description",
            area="Moscow"
        )
        
        assert vacancy.get_title() == "Test Job"
        assert vacancy.get_employer() == employer
        assert vacancy.get_url() == "https://test.com"
        assert vacancy.get_description() == "Test description"
        assert vacancy.get_area() == "Moscow"
    
    def test_vacancy_to_dict(self):
        """Покрытие метода to_dict"""
        vacancy = Vacancy(
            title="Test",
            employer=Employer(name="Test Company")
        )
        result = vacancy.to_dict()
        
        assert isinstance(result, dict)
        assert result["title"] == "Test"
        assert "employer" in result
        assert "id" in result
    
    def test_vacancy_from_dict(self):
        """Покрытие метода from_dict"""
        data = {
            "title": "Dict Vacancy",
            "employer": {"name": "Dict Company"},
            "url": "https://dict.com"
        }
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.title == "Dict Vacancy"
        assert vacancy.employer.name == "Dict Company"
        assert vacancy.url == "https://dict.com"
    
    def test_vacancy_get_method(self):
        """Покрытие dictionary-like доступа"""
        vacancy = Vacancy(
            title="Test",
            employer=Employer(name="Test"),
            area="SPB"
        )
        
        assert vacancy.get("title") == "Test"
        assert vacancy.get("area") == "SPB"
        assert vacancy.get("nonexistent") is None
        assert vacancy.get("nonexistent", "default") == "default"


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
    
    def test_factory_create_experience_dict(self):
        """Покрытие создания опыта из словаря"""
        exp_data = {"name": "Middle", "id": "mid"}
        experience = VacancyFactory._create_experience(exp_data)
        
        assert isinstance(experience, Experience)
        assert experience.name == "Middle"
        assert experience.id == "mid"
    
    def test_factory_create_experience_string(self):
        """Покрытие создания опыта из строки"""
        experience = VacancyFactory._create_experience("Без опыта")
        
        assert isinstance(experience, Experience)
        assert experience.name == "Без опыта"
    
    def test_factory_create_experience_none(self):
        """Покрытие создания опыта из None"""
        experience = VacancyFactory._create_experience(None)
        
        assert experience is None
    
    def test_factory_create_employment_dict(self):
        """Покрытие создания типа занятости из словаря"""
        emp_data = {"name": "Частичная", "id": "part"}
        employment = VacancyFactory._create_employment(emp_data)
        
        assert isinstance(employment, Employment)
        assert employment.name == "Частичная"
        assert employment.id == "part"
    
    def test_factory_create_employment_string(self):
        """Покрытие создания типа занятости из строки"""
        employment = VacancyFactory._create_employment("Стажировка")
        
        assert isinstance(employment, Employment)
        assert employment.name == "Стажировка"
    
    def test_factory_create_employment_none(self):
        """Покрытие создания типа занятости из None"""
        employment = VacancyFactory._create_employment(None)
        
        assert employment is None
    
    def test_factory_create_schedule_dict(self):
        """Покрытие создания графика из словаря"""
        sch_data = {"name": "Удаленно", "id": "remote"}
        schedule = VacancyFactory._create_schedule(sch_data)
        
        assert isinstance(schedule, Schedule)
        assert schedule.name == "Удаленно"
        assert schedule.id == "remote"
    
    def test_factory_create_schedule_string(self):
        """Покрытие создания графика из строки"""
        schedule = VacancyFactory._create_schedule("Вахта")
        
        assert isinstance(schedule, Schedule)
        assert schedule.name == "Вахта"
    
    def test_factory_create_schedule_none(self):
        """Покрытие создания графика из None"""
        schedule = VacancyFactory._create_schedule(None)
        
        assert schedule is None
    
    def test_factory_create_salary_valid(self):
        """Покрытие создания зарплаты из валидного словаря"""
        salary_data = {"from": 50000, "to": 80000, "currency": "USD"}
        salary = VacancyFactory._create_salary(salary_data)
        
        assert isinstance(salary, Salary)
        assert salary.amount_from == 50000
        assert salary.amount_to == 80000
        assert salary.currency == "USD"
    
    def test_factory_create_salary_invalid(self):
        """Покрытие создания зарплаты из невалидного словаря"""
        # Невалидные данные
        salary = VacancyFactory._create_salary({"invalid": "data"})
        assert salary is None
        
        # None
        salary = VacancyFactory._create_salary(None)
        assert salary is None
        
        # Не словарь
        salary = VacancyFactory._create_salary("invalid")
        assert salary is None
    
    def test_factory_extract_description(self):
        """Покрытие извлечения описания"""
        data_with_snippet = {
            "snippet": {
                "requirement": "Python",
                "responsibility": "Development"
            }
        }
        
        description = VacancyFactory._extract_description(data_with_snippet)
        assert "Python" in description
        assert "Development" in description
        
        # Без snippet
        description = VacancyFactory._extract_description({})
        assert description is None
    
    def test_factory_extract_area(self):
        """Покрытие извлечения области"""
        data_with_area = {"area": {"name": "Новосибирск"}}
        area = VacancyFactory._extract_area(data_with_area)
        assert area == "Новосибирск"
        
        # Без area
        area = VacancyFactory._extract_area({})
        assert area is None
    
    def test_factory_with_exception_handling(self):
        """Покрытие обработки исключений в фабрике"""
        # Данные которые могут вызвать ошибку
        problematic_data = {
            "name": "Test",
            "employer": {"name": "Test"},
            "salary": {"from": "invalid_number"}  # Невалидная зарплата
        }
        
        # Фабрика должна обработать исключение и создать вакансию
        vacancy = VacancyFactory.create_from_dict(problematic_data)
        
        assert isinstance(vacancy, Vacancy)
        assert vacancy.title == "Test"
        assert vacancy.salary is None  # Невалидная зарплата игнорируется


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
        
        # Присваивание пустого имени должно валидироваться
        employer.name = ""
        assert employer.name == "Не указана"


class TestEdgeCases:
    """Покрытие крайних случаев и специфичных ветвей"""
    
    def test_large_data_handling(self):
        """Покрытие обработки больших объемов данных"""
        large_description = "A" * 10000  # Большое описание
        
        vacancy = Vacancy(
            title="Large Data Test",
            employer=Employer(name="Big Company"),
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
            "name": "Complex Job",
            "employer": {
                "name": "Nested Company",
                "nested": {
                    "deep": "value"
                }
            },
            "snippet": {
                "requirement": "Complex requirement",
                "responsibility": None  # None значение
            }
        }
        
        vacancy = VacancyFactory.create_from_dict(complex_data)
        
        assert vacancy.title == "Complex Job"
        assert vacancy.employer.name == "Nested Company"
        assert "Complex requirement" in vacancy.description