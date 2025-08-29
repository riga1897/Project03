
"""
Полные тесты для VacancyOperations
"""

import pytest
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy


class TestVacancyOperationsComplete:
    """Полное тестирование VacancyOperations"""

    @pytest.fixture
    def operations(self):
        """Фикстура VacancyOperations"""
        return VacancyOperations()

    @pytest.fixture
    def test_vacancies(self):
        """Фикстура с разнообразными вакансиями для тестов"""
        return [
            Vacancy(
                title="Senior Python Developer",
                url="https://example.com/1",
                salary={"from": 150000, "to": 200000, "currency": "RUR"},
                description="Python, Django, PostgreSQL",
                vacancy_id="1",
                source="hh.ru"
            ),
            Vacancy(
                title="Java Developer",
                url="https://example.com/2",
                salary={"from": 80000, "to": 120000, "currency": "RUR"},
                description="Java, Spring Boot",
                vacancy_id="2",
                source="hh.ru"
            ),
            Vacancy(
                title="Python Data Scientist",
                url="https://example.com/3",
                salary={"from": 120000, "to": 180000, "currency": "RUR"},
                description="Python, pandas, scikit-learn",
                vacancy_id="3",
                source="superjob.ru"
            ),
            Vacancy(
                title="Frontend Developer",
                url="https://example.com/4",
                description="React, JavaScript",
                vacancy_id="4",
                source="hh.ru"
            )
        ]

    def test_filter_vacancies_by_min_salary(self, operations, test_vacancies):
        """Тест фильтрации по минимальной зарплате"""
        result = operations.filter_vacancies_by_min_salary(test_vacancies, 100000)
        assert len(result) == 3  # 3 вакансии с зарплатой >= 100000

        result = operations.filter_vacancies_by_min_salary(test_vacancies, 150000)
        assert len(result) == 2  # 2 вакансии с зарплатой >= 150000

    def test_filter_vacancies_by_max_salary(self, operations, test_vacancies):
        """Тест фильтрации по максимальной зарплате"""
        result = operations.filter_vacancies_by_max_salary(test_vacancies, 150000)
        assert len(result) == 2  # 2 вакансии с зарплатой <= 150000

    def test_filter_vacancies_by_salary_range(self, operations, test_vacancies):
        """Тест фильтрации по диапазону зарплат"""
        result = operations.filter_vacancies_by_salary_range(test_vacancies, 100000, 150000)
        assert len(result) == 2  # 2 вакансии в диапазоне

    def test_filter_vacancies_by_multiple_keywords(self, operations, test_vacancies):
        """Тест фильтрации по нескольким ключевым словам"""
        result = operations.filter_vacancies_by_multiple_keywords(test_vacancies, ["Python"])
        assert len(result) == 2  # 2 вакансии с Python

        result = operations.filter_vacancies_by_multiple_keywords(test_vacancies, ["Java"])
        assert len(result) == 1  # 1 вакансия с Java

        result = operations.filter_vacancies_by_multiple_keywords(test_vacancies, ["Python", "Java"])
        assert len(result) == 3  # 3 вакансии с Python или Java

    def test_search_vacancies_advanced_and_operator(self, operations, test_vacancies):
        """Тест расширенного поиска с оператором AND"""
        result = operations.search_vacancies_advanced(test_vacancies, "Python AND Django")
        assert len(result) == 1  # Только Senior Python Developer содержит оба слова

    def test_search_vacancies_advanced_or_operator(self, operations, test_vacancies):
        """Тест расширенного поиска с оператором OR"""
        result = operations.search_vacancies_advanced(test_vacancies, "Python OR Java")
        assert len(result) == 3  # Все вакансии с Python или Java

    def test_sort_vacancies_by_salary(self, operations, test_vacancies):
        """Тест сортировки по зарплате"""
        result = operations.sort_vacancies_by_salary(test_vacancies)
        
        # Проверяем, что вакансии отсортированы по убыванию зарплаты
        salaries = []
        for vacancy in result:
            if vacancy.salary and vacancy.salary.get('from'):
                salaries.append(vacancy.salary['from'])
        
        # Проверяем, что зарплаты идут в убывающем порядке
        for i in range(1, len(salaries)):
            assert salaries[i-1] >= salaries[i]

    def test_empty_list_handling(self, operations):
        """Тест обработки пустых списков"""
        empty_list = []
        
        assert operations.filter_vacancies_by_min_salary(empty_list, 100000) == []
        assert operations.filter_vacancies_by_multiple_keywords(empty_list, ["Python"]) == []
        assert operations.search_vacancies_advanced(empty_list, "Python") == []
        assert operations.sort_vacancies_by_salary(empty_list) == []

    def test_none_salary_handling(self, operations):
        """Тест обработки вакансий без зарплаты"""
        vacancy_no_salary = Vacancy(
            title="No Salary Job",
            url="https://example.com/no-salary",
            vacancy_id="no_salary",
            source="test"
        )
        
        vacancies = [vacancy_no_salary]
        
        # Вакансии без зарплаты должны фильтроваться корректно
        result = operations.filter_vacancies_by_min_salary(vacancies, 50000)
        assert len(result) == 0
        
        # Но должны оставаться при сортировке
        sorted_result = operations.sort_vacancies_by_salary(vacancies)
        assert len(sorted_result) == 1
