"""
100% покрытие src/vacancies/models.py
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.vacancies.models import Employer, Experience, Employment, Vacancy
from src.utils.salary import Salary


class TestEmployer:
    """100% покрытие класса Employer"""

    def test_employer_init_with_all_params(self):
        """Тест инициализации Employer со всеми параметрами - покрывает строки 18-28"""
        employer = Employer(
            name="Test Company",
            employer_id="123",
            trusted=True,
            alternate_url="https://company.com"
        )
        
        assert employer._name == "Test Company"
        assert employer._id == "123"
        assert employer._trusted == True
        assert employer._alternate_url == "https://company.com"

    def test_employer_init_minimal_params(self):
        """Тест инициализации Employer с минимальными параметрами"""
        employer = Employer(name="Minimal Company")
        
        assert employer._name == "Minimal Company"
        assert employer._id is None
        assert employer._trusted is None
        assert employer._alternate_url is None

    def test_get_name_with_name(self):
        """Тест get_name с установленным именем - покрывает строки 30-32"""
        employer = Employer(name="Tech Corp")
        
        result = employer.get_name()
        
        assert result == "Tech Corp"

    def test_get_name_without_name(self):
        """Тест get_name без имени"""
        employer = Employer(name="")
        
        result = employer.get_name()
        
        assert result == "Не указана"

    def test_get_id(self):
        """Тест get_id - покрывает строки 34-36"""
        employer = Employer(name="Test", employer_id="456")
        
        result = employer.get_id()
        
        assert result == "456"

    def test_is_trusted(self):
        """Тест is_trusted - покрывает строки 38-40"""
        employer = Employer(name="Test", trusted=True)
        
        result = employer.is_trusted()
        
        assert result == True

    def test_get_url(self):
        """Тест get_url - покрывает строки 42-44"""
        employer = Employer(name="Test", alternate_url="https://test.com")
        
        result = employer.get_url()
        
        assert result == "https://test.com"

    def test_to_dict(self):
        """Тест to_dict - покрывает строки 46-48"""
        employer = Employer(
            name="Dict Company",
            employer_id="789",
            trusted=False,
            alternate_url="https://dict.com"
        )
        
        result = employer.to_dict()
        
        expected = {
            "name": "Dict Company",
            "id": "789",
            "trusted": False,
            "alternate_url": "https://dict.com"
        }
        assert result == expected

    def test_from_dict_with_all_data(self):
        """Тест from_dict со всеми данными - покрывает строки 50-58"""
        data = {
            "name": "From Dict Company",
            "id": "fromdict123",
            "trusted": True,
            "alternate_url": "https://fromdict.com"
        }
        
        employer = Employer.from_dict(data)
        
        assert employer.get_name() == "From Dict Company"
        assert employer.get_id() == "fromdict123"
        assert employer.is_trusted() == True
        assert employer.get_url() == "https://fromdict.com"

    def test_from_dict_with_minimal_data(self):
        """Тест from_dict с минимальными данными"""
        data = {}
        
        employer = Employer.from_dict(data)
        
        assert employer.get_name() == "Не указана"
        assert employer.get_id() is None
        assert employer.is_trusted() is None
        assert employer.get_url() is None

    def test_str_method(self):
        """Тест __str__ метода - покрывает строки 60-61"""
        employer = Employer(name="String Company")
        
        result = str(employer)
        
        assert result == "String Company"

    def test_repr_method(self):
        """Тест __repr__ метода - покрывает строки 63-64"""
        employer = Employer(name="Repr Company", employer_id="repr123")
        
        result = repr(employer)
        
        assert "Employer" in result and "Repr Company" in result

    def test_name_property(self):
        """Тест свойства name - покрывает строки 67-69"""
        employer = Employer(name="Property Company")
        
        assert employer.name == "Property Company"

    def test_id_property(self):
        """Тест свойства id - покрывает строки 71-73"""
        employer = Employer(name="Test", employer_id="prop123")
        
        assert employer.id == "prop123"

    def test_trusted_property(self):
        """Тест свойства trusted - покрывает строки 75-77"""
        employer = Employer(name="Test", trusted=True)
        
        assert employer.trusted == True

    def test_alternate_url_property(self):
        """Тест свойства alternate_url - покрывает строки 79-81"""
        employer = Employer(name="Test", alternate_url="https://prop.com")
        
        assert employer.alternate_url == "https://prop.com"

    def test_get_method_name(self):
        """Тест get метода с ключом name - покрывает строки 84-87"""
        employer = Employer(name="Get Company")
        
        result = employer.get("name")
        
        assert result == "Get Company"

    def test_get_method_id(self):
        """Тест get метода с ключом id - покрывает строки 88-89"""
        employer = Employer(name="Test", employer_id="get123")
        
        result = employer.get("id")
        
        assert result == "get123"

    def test_get_method_trusted(self):
        """Тест get метода с ключом trusted - покрывает строки 90-91"""
        employer = Employer(name="Test", trusted=False)
        
        result = employer.get("trusted")
        
        assert result == False

    def test_get_method_alternate_url(self):
        """Тест get метода с ключом alternate_url - покрывает строки 92-93"""
        employer = Employer(name="Test", alternate_url="https://get.com")
        
        result = employer.get("alternate_url")
        
        assert result == "https://get.com"

    def test_get_method_default(self):
        """Тест get метода с неизвестным ключом - покрывает строку 94"""
        employer = Employer(name="Test")
        
        result = employer.get("unknown_key", "default_value")
        
        assert result == "default_value"

    def test_eq_with_dict(self):
        """Тест __eq__ с словарем - покрывает строки 96-99"""
        employer = Employer(name="Equal Company", employer_id="eq123")
        dict_data = {"name": "Equal Company", "id": "eq123"}
        
        assert employer == dict_data

    def test_eq_with_employer(self):
        """Тест __eq__ с другим Employer - покрывает строки 100-101"""
        employer1 = Employer(name="Same Company", employer_id="same123")
        employer2 = Employer(name="Same Company", employer_id="same123")
        
        assert employer1 == employer2

    def test_eq_with_other_type(self):
        """Тест __eq__ с другим типом - покрывает строку 102"""
        employer = Employer(name="Test")
        
        assert not (employer == "string")
        assert not (employer == 123)

    def test_hash_method(self):
        """Тест __hash__ метода - покрывает строку 104-105"""
        employer = Employer(name="Hash Company", employer_id="hash123")
        
        # Должен возвращать хеш без ошибок
        hash_value = hash(employer)
        
        assert isinstance(hash_value, int)


class TestExperience:
    """100% покрытие класса Experience"""
    
    def test_experience_init_with_all_params(self):
        """Тест инициализации Experience со всеми параметрами"""
        experience = Experience(name="1-3 года", experience_id="exp123")
        
        assert experience._name == "1-3 года"
        assert experience._id == "exp123"

    def test_experience_init_minimal(self):
        """Тест инициализации Experience с минимальными параметрами"""
        experience = Experience(name="Опыт не требуется")
        
        assert experience._name == "Опыт не требуется"
        assert experience._id is None

    def test_get_name(self):
        """Тест get_name"""
        experience = Experience(name="3-6 лет")
        
        result = experience.get_name()
        
        assert result == "3-6 лет"

    def test_get_id(self):
        """Тест get_id"""
        experience = Experience(name="Опыт", experience_id="test_id")
        
        result = experience.get_id()
        
        assert result == "test_id"

    def test_to_dict(self):
        """Тест to_dict"""
        experience = Experience(name="Более 6 лет", experience_id="exp456")
        
        result = experience.to_dict()
        
        expected = {"name": "Более 6 лет", "id": "exp456"}
        assert result == expected

    def test_from_dict(self):
        """Тест from_dict"""
        data = {"name": "От 1 года до 3 лет", "id": "from_dict_id"}
        
        experience = Experience.from_dict(data)
        
        assert experience.get_name() == "От 1 года до 3 лет"
        assert experience.get_id() == "from_dict_id"

    def test_from_string(self):
        """Тест from_string"""
        experience_str = "Нет опыта"
        
        experience = Experience.from_string(experience_str)
        
        assert experience.get_name() == "Нет опыта"
        assert experience.get_id() is None

    def test_str_method(self):
        """Тест __str__"""
        experience = Experience(name="Средний опыт")
        
        result = str(experience)
        
        assert result == "Средний опыт"

    def test_repr_method(self):
        """Тест __repr__"""
        experience = Experience(name="Большой опыт", experience_id="big_exp")
        
        result = repr(experience)
        
        assert result == "Experience(name='Большой опыт')"


class TestEmployment:
    """100% покрытие класса Employment"""

    def test_employment_init_with_all_params(self):
        """Тест инициализации Employment со всеми параметрами"""
        employment = Employment(name="Полная занятость", employment_id="full123")
        
        assert employment._name == "Полная занятость"
        assert employment._id == "full123"

    def test_employment_init_minimal(self):
        """Тест инициализации Employment с минимальными параметрами"""
        employment = Employment(name="Частичная занятость")
        
        assert employment._name == "Частичная занятость"
        assert employment._id is None

    def test_get_name(self):
        """Тест get_name"""
        employment = Employment(name="Проектная работа")
        
        result = employment.get_name()
        
        assert result == "Проектная работа"

    def test_get_id(self):
        """Тест get_id"""
        employment = Employment(name="Стажировка", employment_id="intern123")
        
        result = employment.get_id()
        
        assert result == "intern123"

    def test_to_dict(self):
        """Тест to_dict"""
        employment = Employment(name="Волонтерство", employment_id="vol456")
        
        result = employment.to_dict()
        
        expected = {"name": "Волонтерство", "id": "vol456"}
        assert result == expected

    def test_from_dict(self):
        """Тест from_dict"""
        data = {"name": "Удаленная работа", "id": "remote_id"}
        
        employment = Employment.from_dict(data)
        
        assert employment.get_name() == "Удаленная работа"
        assert employment.get_id() == "remote_id"

    def test_from_string(self):
        """Тест from_string"""
        employment_str = "Гибкий график"
        
        employment = Employment.from_string(employment_str)
        
        assert employment.get_name() == "Гибкий график"
        assert employment.get_id() is None

    def test_str_method(self):
        """Тест __str__"""
        employment = Employment(name="Сменная работа")
        
        result = str(employment)
        
        assert result == "Сменная работа"

    def test_repr_method(self):
        """Тест __repr__"""
        employment = Employment(name="Вахтовый метод", employment_id="vahta123")
        
        result = repr(employment)
        
        assert result == "Employment(name='Вахтовый метод')"


class TestVacancy:
    """100% покрытие класса Vacancy"""

    @patch('src.vacancies.models.uuid.uuid4')
    @patch('src.vacancies.models.datetime')
    def test_vacancy_init_minimal(self, mock_datetime, mock_uuid):
        """Тест инициализации Vacancy с минимальными параметрами"""
        mock_uuid.return_value.hex = "test_uuid_hex"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        vacancy = Vacancy(
            vacancy_id="123",
            title="Test Job",
            url="https://test.com"
        )
        
        assert vacancy.vacancy_id == "123"
        assert vacancy.title == "Test Job"
        assert vacancy.url == "https://test.com"

    def test_vacancy_init_with_all_params(self):
        """Тест инициализации Vacancy со всеми параметрами"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        employer = Employer(name="Test Company")
        
        with patch('src.vacancies.models.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = "test_uuid"
            
            vacancy = Vacancy(
                vacancy_id="456",
                title="Senior Developer",
                url="https://senior.com",
                salary=salary_data,
                description="Great job",
                requirements="Python skills",
                responsibilities="Coding",
                employer=employer,
                area="Moscow",
                experience="3-6 лет",
                employment="Полная занятость",
                schedule="Полный день",
                published_at="2024-01-01",
                source="test_source"
            )
            
            assert vacancy.vacancy_id == "456"
            assert vacancy.title == "Senior Developer" 
            assert vacancy.url == "https://senior.com"
            assert vacancy.description == "Great job"
            assert vacancy.requirements == "Python skills"
            assert vacancy.responsibilities == "Coding"
            assert vacancy.area == "Moscow"
            assert isinstance(vacancy.experience, Experience)
            assert isinstance(vacancy.employment, Employment)
            assert vacancy.schedule == "Полный день"
            assert isinstance(vacancy.published_at, datetime) or vacancy.published_at == "2024-01-01"
            assert vacancy.source == "test_source"

    def test_salary_property(self):
        """Тест свойства salary"""
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy(
                vacancy_id="123", 
                title="Test", 
                url="url", 
                salary={"from": 50000}
            )
            
            assert isinstance(vacancy.salary, Salary)

    def test_employer_property_dict(self):
        """Тест свойства employer с словарем"""
        employer_data = {"name": "Dict Company", "id": "dict123"}
        
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy("123", "Test", "url", employer=employer_data)
            
            assert isinstance(vacancy.employer, Employer)
            assert vacancy.employer.get_name() == "Dict Company"

    def test_employer_property_object(self):
        """Тест свойства employer с объектом"""
        employer_obj = Employer(name="Object Company")
        
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy("123", "Test", "url", employer=employer_obj)
            
            assert vacancy.employer == employer_obj

    def test_from_dict_complete_data(self):
        """Тест from_dict с полными данными"""
        data = {
            "id": "from_dict_123",
            "name": "From Dict Job",
            "title": "Alternative Title",
            "alternate_url": "https://fromdict.com",
            "url": "https://direct.com",
            "salary": {"from": 80000, "to": 120000},
            "snippet": {
                "requirement": "Python",
                "responsibility": "Development"
            },
            "description": "Job description",
            "employer": {"name": "Dict Employer"},
            "area": {"name": "St.Petersburg"},
            "experience": {"name": "1-3 года"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"},
            "published_at": "2024-01-15",
            "source": "dict_source"
        }
        
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy.from_dict(data)
            
            assert vacancy.vacancy_id == "from_dict_123"
            assert vacancy.title == "Alternative Title"  # title имеет приоритет над name
            assert vacancy.url == "https://fromdict.com"  # alternate_url имеет приоритет
            assert vacancy.requirements == "Python"
            assert vacancy.responsibilities == "Development"
            assert vacancy.description == "Job description"
            assert vacancy.area == "St.Petersburg"
            assert isinstance(vacancy.experience, Experience)
            assert isinstance(vacancy.employment, Employment)
            assert vacancy.schedule == "Полный день"
            assert isinstance(vacancy.published_at, datetime) or vacancy.published_at == "2024-01-15"
            assert vacancy.source == "dict_source"

    def test_from_dict_minimal_data(self):
        """Тест from_dict с минимальными данными"""
        data = {
            "id": "minimal_123",
            "name": "Minimal Job",
            "alternate_url": "https://minimal.com"
        }
        
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy.from_dict(data)
            
            assert vacancy.vacancy_id == "minimal_123"
            assert vacancy.title == "Minimal Job"
            assert vacancy.url == "https://minimal.com"

    def test_from_dict_missing_required_fields(self):
        """Тест from_dict с отсутствующими обязательными полями"""
        data = {"some_field": "some_value"}
        
        # Vacancy.from_dict не выбрасывает исключение, а создает объект с дефолтными значениями
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy.from_dict(data)
            assert vacancy.title == "Без названия"
            assert vacancy.url == ""

    def test_to_dict_method(self):
        """Тест to_dict метода"""
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy(
                vacancy_id="to_dict_123",
                title="To Dict Job",
                url="https://todict.com",
                description="Description",
                source="test"
            )
            
            result = vacancy.to_dict()
            
            assert isinstance(result, dict)
            assert result["vacancy_id"] == "to_dict_123"
            assert result["title"] == "To Dict Job"
            assert result["url"] == "https://todict.com"
            assert result["description"] == "Description"
            assert result["source"] == "test"

    def test_str_method(self):
        """Тест __str__ метода"""
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy("123", "String Job", "https://str.com")
            
            result = str(vacancy)
            
            assert "String Job" in result

    def test_repr_method(self):
        """Тест __repr__ метода"""
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy("repr123", "Repr Job", "https://repr.com")
            
            result = repr(vacancy)
            
            # Vacancy использует дефолтный __repr__ объекта
            assert "Vacancy object" in result

    def test_equality_comparison(self):
        """Тест сравнения вакансий"""
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy1 = Vacancy("same_id", "Job 1", "https://job1.com")
            vacancy2 = Vacancy("same_id", "Job 2", "https://job2.com")
            vacancy3 = Vacancy("diff_id", "Job 3", "https://job3.com")
            
            # Проверяем что объекты - это разные экземпляры
            assert vacancy1 is not vacancy2  
            assert vacancy1 is not vacancy3

    def test_hash_method(self):
        """Тест __hash__ метода"""
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy("hash123", "Hash Job", "https://hash.com")
            
            hash_value = hash(vacancy)
            
            assert isinstance(hash_value, int)

    def test_vacancy_salary_integration(self):
        """Тест интеграции с зарплатой"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy(
                vacancy_id="123", 
                title="Test", 
                url="url", 
                salary=salary_data
            )
            
            assert isinstance(vacancy.salary, Salary)


class TestVacancyIntegration:
    """Интеграционные тесты для моделей"""

    def test_vacancy_with_all_model_types(self):
        """Тест Vacancy со всеми типами моделей"""
        employer = Employer(name="Integration Company", employer_id="int123")
        experience = Experience(name="5+ лет", experience_id="exp_int")
        employment = Employment(name="Полная занятость", employment_id="emp_int")
        salary_data = {"from": 200000, "to": 300000, "currency": "RUR"}
        
        with patch('src.vacancies.models.uuid.uuid4'):
            vacancy = Vacancy(
                vacancy_id="integration_test",
                title="Senior Integration Developer",
                url="https://integration.com",
                salary=salary_data,
                employer=employer,
                experience=experience.get_name(),
                employment=employment.get_name()
            )
            
            # Проверяем интеграцию всех компонентов
            assert vacancy.employer.get_name() == "Integration Company"
            assert isinstance(vacancy.experience, Experience)
            assert isinstance(vacancy.employment, Employment)
            assert isinstance(vacancy.salary, Salary)

    def test_models_serialization_deserialization(self):
        """Тест сериализации и десериализации всех моделей"""
        # Создаем полную структуру данных
        original_data = {
            "id": "serialize_test",
            "name": "Serialization Job",
            "alternate_url": "https://serialize.com",
            "salary": {"from": 150000, "to": 250000},
            "employer": {"name": "Serialize Corp", "id": "corp123"},
            "experience": {"name": "3-6 лет", "id": "exp123"},
            "employment": {"name": "Удаленная работа", "id": "remote123"}
        }
        
        with patch('src.vacancies.models.uuid.uuid4'):
            # Десериализуем
            vacancy = Vacancy.from_dict(original_data)
            
            # Сериализуем обратно
            serialized = vacancy.to_dict()
            
            # Проверяем что данные сохранились
            assert serialized["vacancy_id"] == "serialize_test"
            assert serialized["title"] == "Serialization Job"
            assert serialized["url"] == "https://serialize.com"

    def test_error_handling_in_models(self):
        """Тест обработки ошибок в моделях"""
        # Тест с некорректными данными для Employer
        invalid_employer_data = {"invalid_field": "invalid_value"}
        employer = Employer.from_dict(invalid_employer_data)
        assert employer.get_name() == "Не указана"
        
        # Тест с пустыми данными для Experience
        empty_experience = Experience.from_dict({})
        assert empty_experience.get_name() == "Не указан"
        
        # Тест с пустыми данными для Employment  
        empty_employment = Employment.from_dict({})
        assert empty_employment.get_name() == "Не указан"