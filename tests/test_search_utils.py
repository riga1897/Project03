
"""
Тесты для модуля search_utils
"""

import pytest
from unittest.mock import Mock, patch
from src.utils.search_utils import filter_vacancies_by_keyword, vacancy_contains_keyword
from src.vacancies.models import Vacancy


class TestSearchUtils:
    """Тесты для утилит поиска"""

    def create_test_vacancy(self, **kwargs):
        """Создает тестовую вакансию с заданными параметрами"""
        defaults = {
            'vacancy_id': '1',
            'title': 'Test Vacancy',
            'description': None,
            'requirements': None,
            'responsibilities': None,
            'detailed_description': None,
            'skills': None,
            'employer': None,
            'employment': None,
            'schedule': None,
            'experience': None,
            'benefits': None
        }
        defaults.update(kwargs)
        
        vacancy = Vacancy()
        for key, value in defaults.items():
            setattr(vacancy, key, value)
        return vacancy

    def test_filter_vacancies_by_keyword_title_match(self):
        """Тест фильтрации по ключевому слову в заголовке"""
        vacancies = [
            self.create_test_vacancy(title="Python Developer"),
            self.create_test_vacancy(title="Java Developer"),
            self.create_test_vacancy(title="Frontend Developer")
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert filtered[0].title == "Python Developer"

    def test_filter_vacancies_by_keyword_description_match(self):
        """Тест фильтрации по ключевому слову в описании"""
        vacancies = [
            self.create_test_vacancy(title="Developer", description="Python programming required"),
            self.create_test_vacancy(title="Developer", description="Java programming required"),
            self.create_test_vacancy(title="Developer", description="Frontend development with React")
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert "Python programming required" in filtered[0].description

    def test_filter_vacancies_by_keyword_requirements_match(self):
        """Тест фильтрации по ключевому слову в требованиях"""
        vacancies = [
            self.create_test_vacancy(title="Developer", requirements="Experience with Python"),
            self.create_test_vacancy(title="Developer", requirements="Experience with Java"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert "Experience with Python" in filtered[0].requirements

    def test_filter_vacancies_by_keyword_responsibilities_match(self):
        """Тест фильтрации по ключевому слову в обязанностях"""
        vacancies = [
            self.create_test_vacancy(title="Developer", responsibilities="Develop Python applications"),
            self.create_test_vacancy(title="Developer", responsibilities="Develop Java applications"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert "Develop Python applications" in filtered[0].responsibilities

    def test_filter_vacancies_by_keyword_detailed_description_match(self):
        """Тест фильтрации по ключевому слову в детальном описании"""
        vacancies = [
            self.create_test_vacancy(title="Developer", detailed_description="Work with Python and Django"),
            self.create_test_vacancy(title="Developer", detailed_description="Work with Java and Spring"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert "Work with Python and Django" in filtered[0].detailed_description

    def test_filter_vacancies_by_keyword_skills_match(self):
        """Тест фильтрации по ключевому слову в навыках"""
        vacancies = [
            self.create_test_vacancy(title="Developer", skills=[{"name": "Python"}, {"name": "Django"}]),
            self.create_test_vacancy(title="Developer", skills=[{"name": "Java"}, {"name": "Spring"}]),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert any(skill["name"] == "Python" for skill in filtered[0].skills)

    def test_filter_vacancies_by_keyword_case_insensitive(self):
        """Тест нечувствительности к регистру"""
        vacancies = [
            self.create_test_vacancy(title="PYTHON DEVELOPER"),
            self.create_test_vacancy(title="python developer"),
            self.create_test_vacancy(title="Python Developer")
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 3

    def test_filter_vacancies_by_keyword_no_matches(self):
        """Тест фильтрации без совпадений"""
        vacancies = [
            self.create_test_vacancy(title="Java Developer"),
            self.create_test_vacancy(title="C++ Developer")
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 0

    def test_filter_vacancies_by_keyword_relevance_scoring(self):
        """Тест сортировки по релевантности"""
        vacancies = [
            self.create_test_vacancy(title="Developer", description="Python mentioned here"),
            self.create_test_vacancy(title="Python Developer", description="Main Python role"),
            self.create_test_vacancy(title="Senior Python Developer", requirements="Python expertise required")
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 3
        # Вакансии должны быть отсортированы по релевантности
        assert filtered[0].title == "Senior Python Developer"  # Больше всего совпадений
        assert filtered[1].title == "Python Developer"  # Совпадение в заголовке

    def test_vacancy_contains_keyword_true(self):
        """Тест функции vacancy_contains_keyword с положительным результатом"""
        vacancy = self.create_test_vacancy(title="Python Developer", description="Python programming")
        
        assert vacancy_contains_keyword(vacancy, "python") == True

    def test_vacancy_contains_keyword_false(self):
        """Тест функции vacancy_contains_keyword с отрицательным результатом"""
        vacancy = self.create_test_vacancy(title="Java Developer", description="Java programming")
        
        assert vacancy_contains_keyword(vacancy, "python") == False

    def test_vacancy_contains_keyword_in_title(self):
        """Тест поиска ключевого слова в заголовке"""
        vacancy = self.create_test_vacancy(title="Python Developer")
        
        assert vacancy_contains_keyword(vacancy, "python") == True

    def test_vacancy_contains_keyword_in_requirements(self):
        """Тест поиска ключевого слова в требованиях"""
        vacancy = self.create_test_vacancy(requirements="Python experience required")
        
        assert vacancy_contains_keyword(vacancy, "python") == True

    def test_vacancy_contains_keyword_in_responsibilities(self):
        """Тест поиска ключевого слова в обязанностях"""
        vacancy = self.create_test_vacancy(responsibilities="Develop Python applications")
        
        assert vacancy_contains_keyword(vacancy, "python") == True

    def test_vacancy_contains_keyword_in_description(self):
        """Тест поиска ключевого слова в описании"""
        vacancy = self.create_test_vacancy(description="Work with Python and frameworks")
        
        assert vacancy_contains_keyword(vacancy, "python") == True

    def test_vacancy_contains_keyword_in_detailed_description(self):
        """Тест поиска ключевого слова в детальном описании"""
        vacancy = self.create_test_vacancy(detailed_description="Python development role")
        
        assert vacancy_contains_keyword(vacancy, "python") == True

    def test_vacancy_contains_keyword_in_skills(self):
        """Тест поиска ключевого слова в навыках"""
        vacancy = self.create_test_vacancy(skills=[{"name": "Python"}, {"name": "Django"}])
        
        assert vacancy_contains_keyword(vacancy, "python") == True

    def test_filter_vacancies_by_keyword_empty_list(self):
        """Тест фильтрации пустого списка"""
        vacancies = []
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 0

    def test_filter_vacancies_by_keyword_empty_keyword(self):
        """Тест фильтрации с пустым ключевым словом"""
        vacancies = [
            self.create_test_vacancy(title="Python Developer"),
            self.create_test_vacancy(title="Java Developer")
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "")
        assert len(filtered) == 0

    def test_filter_vacancies_by_keyword_none_fields(self):
        """Тест фильтрации вакансий с пустыми полями"""
        vacancy = self.create_test_vacancy(
            title=None,
            description=None,
            requirements=None,
            responsibilities=None,
            detailed_description=None,
            skills=None
        )
        vacancies = [vacancy]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 0
"""
Тесты для утилит поиска
"""

import pytest
from unittest.mock import Mock
from src.utils.search_utils import SearchUtils
from src.vacancies.models import Vacancy


class TestSearchUtils:
    """Тесты для SearchUtils"""

    @pytest.fixture
    def sample_vacancies(self):
        """Фикстура с тестовыми вакансиями"""
        return [
            Vacancy(
                title="Python Developer",
                url="https://test.com/vacancy/1",
                salary={'from': 100000, 'to': 150000, 'currency': 'RUR'},
                description="Python development",
                requirements="Python, Django",
                responsibilities="Backend development",
                experience="3-5 лет",
                employment="Полная занятость",
                schedule="Полный день",
                employer={'name': 'Python Corp'},
                vacancy_id="1",
                published_at="2024-01-15T10:00:00",
                source="hh.ru"
            ),
            Vacancy(
                title="Java Developer",
                url="https://test.com/vacancy/2",
                salary={'from': 120000, 'to': 180000, 'currency': 'RUR'},
                description="Java development",
                requirements="Java, Spring",
                responsibilities="Backend development",
                experience="5+ лет",
                employment="Полная занятость",
                schedule="Полный день",
                employer={'name': 'Java Corp'},
                vacancy_id="2",
                published_at="2024-01-15T11:00:00",
                source="hh.ru"
            )
        ]

    def test_search_by_keyword(self, sample_vacancies):
        """Тест поиска по ключевому слову"""
        utils = SearchUtils()
        
        # Поиск по названию
        result = utils.search_by_keyword(sample_vacancies, "Python")
        assert len(result) == 1
        assert result[0].title == "Python Developer"
        
        # Поиск по описанию
        result = utils.search_by_keyword(sample_vacancies, "development")
        assert len(result) == 2

    def test_search_case_insensitive(self, sample_vacancies):
        """Тест поиска без учета регистра"""
        utils = SearchUtils()
        
        result = utils.search_by_keyword(sample_vacancies, "python")
        assert len(result) == 1
        assert result[0].title == "Python Developer"

    def test_search_multiple_keywords(self, sample_vacancies):
        """Тест поиска по нескольким ключевым словам"""
        utils = SearchUtils()
        
        keywords = ["Python", "Java"]
        result = utils.search_by_multiple_keywords(sample_vacancies, keywords)
        assert len(result) == 2

    def test_search_no_results(self, sample_vacancies):
        """Тест поиска без результатов"""
        utils = SearchUtils()
        
        result = utils.search_by_keyword(sample_vacancies, "C++")
        assert len(result) == 0

    def test_filter_by_experience(self, sample_vacancies):
        """Тест фильтрации по опыту"""
        utils = SearchUtils()
        
        result = utils.filter_by_experience(sample_vacancies, "3-5")
        assert len(result) == 1
        assert result[0].experience == "3-5 лет"

    def test_filter_by_employment(self, sample_vacancies):
        """Тест фильтрации по типу занятости"""
        utils = SearchUtils()
        
        result = utils.filter_by_employment(sample_vacancies, "Полная")
        assert len(result) == 2

    def test_filter_by_company(self, sample_vacancies):
        """Тест фильтрации по компании"""
        utils = SearchUtils()
        
        result = utils.filter_by_company(sample_vacancies, "Python Corp")
        assert len(result) == 1
        assert result[0].employer['name'] == "Python Corp"
