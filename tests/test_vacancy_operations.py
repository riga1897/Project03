
"""
Тесты для операций с вакансиями
"""

import pytest
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy


class TestVacancyOperations:
    """Тесты для класса VacancyOperations"""

    def test_get_vacancies_with_salary(self, sample_vacancies):
        """Тест фильтрации вакансий с зарплатой"""
        # Добавляем вакансию без зарплаты
        vacancy_without_salary = Vacancy(
            title="No Salary Job",
            vacancy_id="no_salary",
            salary=None
        )
        all_vacancies = sample_vacancies + [vacancy_without_salary]
        
        ops = VacancyOperations()
        with_salary = ops.get_vacancies_with_salary(all_vacancies)
        
        assert len(with_salary) == 2  # Только вакансии с зарплатой
        assert all(v.salary is not None for v in with_salary)

    def test_sort_vacancies_by_salary(self, sample_vacancies):
        """Тест сортировки вакансий по зарплате"""
        ops = VacancyOperations()
        sorted_vacancies = ops.sort_vacancies_by_salary(sample_vacancies)
        
        # Проверяем, что сортировка по убыванию (первая вакансия имеет большую зарплату)
        assert sorted_vacancies[0].salary.salary_from >= sorted_vacancies[1].salary.salary_from

    def test_filter_vacancies_by_multiple_keywords(self):
        """Тест фильтрации по нескольким ключевым словам"""
        vacancies = [
            Vacancy(title="Python Django Developer", vacancy_id="1"),
            Vacancy(title="Java Spring Developer", vacancy_id="2"),
            Vacancy(title="Frontend React Developer", vacancy_id="3"),
            Vacancy(title="Python Flask Developer", vacancy_id="4"),
        ]
        
        ops = VacancyOperations()
        
        # Поиск AND (все ключевые слова должны присутствовать)
        python_django = ops.filter_vacancies_by_multiple_keywords(
            vacancies, ["Python", "Django"], operator="AND"
        )
        assert len(python_django) == 1
        assert python_django[0].vacancy_id == "1"
        
        # Поиск OR (любое из ключевых слов)
        python_or_java = ops.filter_vacancies_by_multiple_keywords(
            vacancies, ["Python", "Java"], operator="OR"
        )
        assert len(python_or_java) == 3  # Python Django, Java Spring, Python Flask

    def test_search_vacancies_advanced_and_operator(self):
        """Тест расширенного поиска с оператором AND"""
        vacancies = [
            Vacancy(title="Senior Python Developer", description="Django REST API", vacancy_id="1"),
            Vacancy(title="Junior Python Developer", description="Basic Python", vacancy_id="2"),
            Vacancy(title="Senior Java Developer", description="Spring Boot", vacancy_id="3"),
        ]
        
        ops = VacancyOperations()
        result = ops.search_vacancies_advanced(vacancies, "Senior AND Python")
        
        assert len(result) == 1
        assert result[0].vacancy_id == "1"

    def test_search_vacancies_advanced_or_operator(self):
        """Тест расширенного поиска с оператором OR"""
        vacancies = [
            Vacancy(title="Python Developer", vacancy_id="1"),
            Vacancy(title="Java Developer", vacancy_id="2"),
            Vacancy(title="JavaScript Developer", vacancy_id="3"),
        ]
        
        ops = VacancyOperations()
        result = ops.search_vacancies_advanced(vacancies, "Python OR Java")
        
        assert len(result) == 2
        vacancy_ids = [v.vacancy_id for v in result]
        assert "1" in vacancy_ids
        assert "2" in vacancy_ids

    def test_search_vacancies_advanced_simple_query(self):
        """Тест расширенного поиска с простым запросом"""
        vacancies = [
            Vacancy(title="Python Developer", vacancy_id="1"),
            Vacancy(title="Java Developer", vacancy_id="2"),
        ]
        
        ops = VacancyOperations()
        result = ops.search_vacancies_advanced(vacancies, "Python")
        
        assert len(result) == 1
        assert result[0].vacancy_id == "1"

    def test_calculate_vacancy_relevance(self):
        """Тест вычисления релевантности вакансии"""
        vacancy = Vacancy(
            title="Senior Python Developer",  # +10 за title
            description="Python Django development",  # +3 за description
            requirements="Python, Django, REST",  # +5 за requirements
            responsibilities="Develop Python applications",  # +5 за responsibilities
            vacancy_id="test"
        )
        
        ops = VacancyOperations()
        relevance = ops.calculate_vacancy_relevance(vacancy, "Python")
        
        # Ожидаем: 10 (title) + 3 (description) + 5 (requirements) + 5 (responsibilities) = 23
        assert relevance == 23

    def test_calculate_vacancy_relevance_no_matches(self):
        """Тест вычисления релевантности без совпадений"""
        vacancy = Vacancy(
            title="Java Developer",
            description="Spring Boot development",
            vacancy_id="test"
        )
        
        ops = VacancyOperations()
        relevance = ops.calculate_vacancy_relevance(vacancy, "Python")
        
        assert relevance == 0
