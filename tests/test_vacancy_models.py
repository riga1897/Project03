
"""
Тесты для моделей вакансий
"""

import pytest
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestVacancy:
    """Тесты для класса Vacancy"""

    def test_vacancy_creation_with_dict_salary(self):
        """Тест создания вакансии со словарем зарплаты"""
        vacancy_data = {
            "title": "Python Developer",
            "url": "https://hh.ru/vacancy/12345",
            "salary": {
                "from": 100000,
                "to": 150000,
                "currency": "RUR"
            },
            "vacancy_id": "12345",
            "source": "hh.ru"
        }
        
        vacancy = Vacancy(**vacancy_data)
        
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://hh.ru/vacancy/12345"
        assert vacancy.vacancy_id == "12345"
        assert vacancy.source == "hh.ru"
        assert isinstance(vacancy.salary, Salary)
        assert vacancy.salary.salary_from == 100000
        assert vacancy.salary.salary_to == 150000
        assert vacancy.salary.currency == "RUR"

    def test_vacancy_creation_without_salary(self):
        """Тест создания вакансии без зарплаты"""
        vacancy_data = {
            "title": "Test Position",
            "url": "https://example.com",
            "vacancy_id": "999",
            "source": "superjob.ru"
        }
        
        vacancy = Vacancy(**vacancy_data)
        
        assert vacancy.title == "Test Position"
        assert vacancy.source == "superjob.ru"
        assert vacancy.salary.salary_from is None
        assert vacancy.salary.salary_to is None

    def test_vacancy_string_representation(self, sample_vacancy):
        """Тест строкового представления вакансии"""
        result = str(sample_vacancy)
        
        assert "Python Developer" in result
        assert "12345" in result

    def test_vacancy_comparison(self):
        """Тест сравнения вакансий"""
        vacancy1 = Vacancy(title="Dev", url="https://example.com/1", vacancy_id="1", salary={"from": 100000}, source="hh.ru")
        vacancy2 = Vacancy(title="Dev", url="https://example.com/2", vacancy_id="2", salary={"from": 150000}, source="hh.ru")
        vacancy3 = Vacancy(title="Dev", url="https://example.com/3", vacancy_id="3", salary=None, source="superjob.ru")
        
        assert vacancy2 > vacancy1  # Больше зарплата
        assert vacancy1 < vacancy2
        assert vacancy1 > vacancy3  # Есть зарплата vs нет зарплаты

    def test_vacancy_equality(self):
        """Тест равенства вакансий по ID"""
        vacancy1 = Vacancy(title="Dev1", url="https://example.com/123", vacancy_id="123", source="hh.ru")
        vacancy2 = Vacancy(title="Dev2", url="https://superjob.com/123", vacancy_id="123", source="superjob.ru")
        vacancy3 = Vacancy(title="Dev1", url="https://example.com/456", vacancy_id="456", source="hh.ru")
        
        assert vacancy1 == vacancy2  # Одинаковые ID
        assert vacancy1 != vacancy3  # Разные ID


class TestSalary:
    """Тесты для класса Salary"""

    def test_salary_creation_from_dict(self):
        """Тест создания зарплаты из словаря"""
        salary_data = {
            "from": 80000,
            "to": 120000,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        
        assert salary.salary_from == 80000
        assert salary.salary_to == 120000
        assert salary.currency == "RUR"

    def test_salary_string_representation(self):
        """Тест строкового представления зарплаты"""
        salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        result = str(salary)
        
        assert "от 100,000" in result
        assert "до 150,000" in result
        assert "руб." in result

    def test_salary_only_from(self):
        """Тест зарплаты только с минимальным значением"""
        salary = Salary({"from": 80000, "currency": "RUR"})
        result = str(salary)
        
        assert "от 80,000" in result
        assert "до" not in result

    def test_salary_only_to(self):
        """Тест зарплаты только с максимальным значением"""
        salary = Salary({"to": 120000, "currency": "RUR"})
        result = str(salary)
        
        assert "до 120,000" in result
        assert "от" not in result

    def test_salary_comparison(self):
        """Тест сравнения зарплат"""
        salary1 = Salary({"from": 100000, "to": 150000})
        salary2 = Salary({"from": 120000, "to": 180000})
        salary3 = Salary({"from": 50000})
        
        assert salary2 > salary1
        assert salary1 > salary3
        assert salary1 != salary2



    def test_source_detection_from_dict(self):
        """Тест определения источника при создании из словаря"""
        # HH вакансия
        hh_data = {
            "id": "12345",
            "name": "Python Developer", 
            "alternate_url": "https://hh.ru/vacancy/12345",
            "source": "hh.ru"
        }
        
        hh_vacancy = Vacancy.from_dict(hh_data)
        assert hh_vacancy.source == "hh.ru"
        
        # SuperJob вакансия
        sj_data = {
            "id": "67890",
            "profession": "Java Developer",
            "link": "https://superjob.ru/vacancy/67890",
            "source": "superjob.ru"
        }
        
        sj_vacancy = Vacancy.from_dict(sj_data)
        assert sj_vacancy.source == "superjob.ru"

    def test_source_fallback_detection(self):
        """Тест fallback определения источника"""
        # HH без явного source
        hh_data = {
            "id": "12345",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/12345",
            "snippet": {"requirement": "Python"}
        }
        
        hh_vacancy = Vacancy.from_dict(hh_data)
        assert hh_vacancy.source == "hh.ru"
        
        # SuperJob без явного source
        sj_data = {
            "id": "67890", 
            "profession": "Java Developer",
            "payment_from": 100000,
            "payment_to": 150000
        }
        
        sj_vacancy = Vacancy.from_dict(sj_data)
        assert sj_vacancy.source == "superjob.ru"
