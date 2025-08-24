"""
Тесты для операций с вакансиями
"""

import pytest
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy


class TestVacancyOperations:
    """Тесты для класса VacancyOperations"""

    @pytest.fixture
    def vacancy_ops(self):
        """Фикстура для VacancyOperations"""
        return VacancyOperations()

    @pytest.fixture
    def sample_vacancies(self):
        """Фикстура с примерами вакансий"""
        return [
            Vacancy(
                title="Python Developer",
                url="https://hh.ru/vacancy/1",
                vacancy_id="1",
                salary={"from": 100000, "to": 150000, "currency": "RUR"},
                requirements="Python, Django",
                source="hh.ru"
            ),
            Vacancy(
                title="Java Developer",
                url="https://superjob.ru/vacancy/2",
                vacancy_id="2",
                salary={"from": 120000, "to": 180000, "currency": "RUR"},
                requirements="Java, Spring",
                source="superjob.ru"
            ),
            Vacancy(
                title="Frontend Developer",
                url="https://hh.ru/vacancy/3",
                vacancy_id="3",
                requirements="JavaScript, React",
                source="hh.ru"
            )
        ]

    def test_search_vacancies_advanced(self, vacancy_ops, sample_vacancies):
        """Тест расширенного поиска"""
        result = vacancy_ops.search_vacancies_advanced(sample_vacancies, "Python")
        assert len(result) == 1
        assert result[0].title == "Python Developer"

    def test_get_vacancies_with_salary(self, vacancy_ops, sample_vacancies):
        """Тест фильтрации по наличию зарплаты"""
        result = vacancy_ops.get_vacancies_with_salary(sample_vacancies)
        assert len(result) == 2  # Только Python и Java Developer имеют зарплату

    def test_sort_vacancies_by_salary(self, vacancy_ops, sample_vacancies):
        """Тест сортировки по зарплате"""
        with_salary = vacancy_ops.get_vacancies_with_salary(sample_vacancies)
        result = vacancy_ops.sort_vacancies_by_salary(with_salary)

        # Java Developer должен быть первым (более высокая зарплата)
        assert result[0].title == "Java Developer"
        assert result[1].title == "Python Developer"


    def test_get_vacancies_with_salary(self):
        """Тест получения вакансий с зарплатой"""
        vacancy_with_salary = Vacancy(
            title="Python Developer",
            url="https://example.com/1",
            vacancy_id="1",
            source="hh.ru",
            salary={"from": 100000, "to": 150000, "currency": "RUR"}
        )

        vacancy_without_salary = Vacancy(
            title="Java Developer",
            url="https://example.com/2",
            vacancy_id="2",
            source="hh.ru"
        )
        all_vacancies = [vacancy_with_salary, vacancy_without_salary]

        ops = VacancyOperations()
        with_salary = ops.get_vacancies_with_salary(all_vacancies)

        assert len(with_salary) == 1  # Только вакансии с зарплатой
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
            Vacancy(title="Python Django Developer", url="https://example.com/1", vacancy_id="1", source="hh.ru"),
            Vacancy(title="Java Spring Developer", url="https://example.com/2", vacancy_id="2", source="hh.ru"),
            Vacancy(title="Python Flask Developer", url="https://example.com/3", vacancy_id="3", source="hh.ru"),
            Vacancy(title="Frontend React Developer", url="https://example.com/4", vacancy_id="4", source="hh.ru")
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
            Vacancy(title="Senior Python Developer", url="https://example.com/1", description="Django REST API", vacancy_id="1", source="hh.ru"),
            Vacancy(title="Python Developer", url="https://example.com/2", description="Flask API", vacancy_id="2", source="hh.ru"),
            Vacancy(title="Java Developer", url="https://example.com/3", description="Spring Boot", vacancy_id="3", source="hh.ru")
        ]

        ops = VacancyOperations()
        result = ops.search_vacancies_advanced(vacancies, "Senior AND Python")

        assert len(result) == 1
        assert result[0].vacancy_id == "1"

    def test_search_vacancies_advanced_or_operator(self):
        """Тест расширенного поиска с оператором OR"""
        vacancies = [
            Vacancy(title="Python Developer", url="https://example.com/1", vacancy_id="1", source="hh.ru"),
            Vacancy(title="Java Developer", url="https://example.com/2", vacancy_id="2", source="hh.ru"),
            Vacancy(title="C++ Developer", url="https://example.com/3", vacancy_id="3", source="hh.ru")
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
            Vacancy(title="Python Developer", url="https://example.com/1", vacancy_id="1", source="hh.ru"),
            Vacancy(title="Java Developer", url="https://example.com/2", vacancy_id="2", source="hh.ru")
        ]

        ops = VacancyOperations()
        result = ops.search_vacancies_advanced(vacancies, "Python")

        assert len(result) == 1
        assert result[0].vacancy_id == "1"

    def test_calculate_vacancy_relevance(self):
        """Тест вычисления релевантности вакансии"""
        vacancy = Vacancy(
            title="Senior Python Developer",
            url="https://example.com/1",
            description="Django, PostgreSQL, Redis",
            vacancy_id="1",
            source="hh.ru"
        )

        ops = VacancyOperations()
        relevance = ops.calculate_vacancy_relevance(vacancy, "Python")

        # Ожидаем: 10 (title) + 3 (description) + 5 (requirements) + 5 (responsibilities) = 23
        assert relevance == 23

    def test_calculate_vacancy_relevance_no_matches(self):
        """Тест вычисления релевантности без совпадений"""
        vacancy = Vacancy(
            title="Java Developer",
            url="https://example.com/1",
            description="Spring Boot",
            vacancy_id="1",
            source="hh.ru"
        )

        ops = VacancyOperations()
        relevance = ops.calculate_vacancy_relevance(vacancy, "Python")

        assert relevance == 0