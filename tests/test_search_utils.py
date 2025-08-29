
"""
Тесты для модуля search_utils
"""

import pytest
from unittest.mock import Mock
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
            'benefits': None,
            'source': 'test',
            'url': 'https://test.com/1'
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

    def test_filter_vacancies_by_keyword_skills_dict_match(self):
        """Тест фильтрации по ключевому слову в навыках (словарь)"""
        vacancies = [
            self.create_test_vacancy(title="Developer", skills=[{"name": "Python"}, {"name": "Django"}]),
            self.create_test_vacancy(title="Developer", skills=[{"name": "Java"}, {"name": "Spring"}]),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert any(skill["name"] == "Python" for skill in filtered[0].skills)

    def test_filter_vacancies_by_keyword_skills_string_match(self):
        """Тест фильтрации по ключевому слову в навыках (строка)"""
        vacancies = [
            self.create_test_vacancy(title="Developer", skills=["Python", "Django"]),
            self.create_test_vacancy(title="Developer", skills=["Java", "Spring"]),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert "Python" in filtered[0].skills

    def test_filter_vacancies_by_keyword_employer_match(self):
        """Тест фильтрации по ключевому слову в работодателе"""
        vacancies = [
            self.create_test_vacancy(title="Developer", employer={"name": "Python Corp"}),
            self.create_test_vacancy(title="Developer", employer={"name": "Java Corp"}),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert filtered[0].employer["name"] == "Python Corp"

    def test_filter_vacancies_by_keyword_employment_match(self):
        """Тест фильтрации по ключевому слову в типе занятости"""
        vacancies = [
            self.create_test_vacancy(title="Developer", employment="Remote Python work"),
            self.create_test_vacancy(title="Developer", employment="Office Java work"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert "Remote Python work" in filtered[0].employment

    def test_filter_vacancies_by_keyword_schedule_match(self):
        """Тест фильтрации по ключевому слову в графике работы"""
        vacancies = [
            self.create_test_vacancy(title="Developer", schedule="Flexible Python schedule"),
            self.create_test_vacancy(title="Developer", schedule="Fixed Java schedule"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert "Flexible Python schedule" in filtered[0].schedule

    def test_filter_vacancies_by_keyword_experience_match(self):
        """Тест фильтрации по ключевому слову в опыте работы"""
        vacancies = [
            self.create_test_vacancy(title="Developer", experience="3+ years Python experience"),
            self.create_test_vacancy(title="Developer", experience="5+ years Java experience"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert "3+ years Python experience" in filtered[0].experience

    def test_filter_vacancies_by_keyword_benefits_match(self):
        """Тест фильтрации по ключевому слову в бонусах"""
        vacancies = [
            self.create_test_vacancy(title="Developer", benefits="Python training provided"),
            self.create_test_vacancy(title="Developer", benefits="Java certification support"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert "Python training provided" in filtered[0].benefits

    def test_filter_vacancies_by_keyword_vacancy_id_match(self):
        """Тест фильтрации по ключевому слову в ID вакансии"""
        vacancies = [
            self.create_test_vacancy(vacancy_id="python_123", title="Developer"),
            self.create_test_vacancy(vacancy_id="java_456", title="Developer"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert filtered[0].vacancy_id == "python_123"

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
            self.create_test_vacancy(
                vacancy_id="python_123", 
                title="Senior Python Developer", 
                requirements="Python expertise required"
            )
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 3
        # Вакансии должны быть отсортированы по релевантности
        assert filtered[0].vacancy_id == "python_123"  # Самый высокий балл (ID + title + requirements)
        assert filtered[1].title == "Python Developer"  # Следующий по релевантности

    def test_filter_vacancies_by_keyword_profession_attribute(self):
        """Тест фильтрации по атрибуту profession (для SuperJob)"""
        vacancy = self.create_test_vacancy(title="Developer")
        # Добавляем атрибут profession динамически
        vacancy.profession = "Python Developer"
        vacancies = [vacancy]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1

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

    def test_vacancy_contains_keyword_in_skills_dict(self):
        """Тест поиска ключевого слова в навыках (словарь)"""
        vacancy = self.create_test_vacancy(skills=[{"name": "Python"}, {"name": "Django"}])
        
        assert vacancy_contains_keyword(vacancy, "python") == True

    def test_vacancy_contains_keyword_in_skills_missing_name(self):
        """Тест поиска ключевого слова в навыках без поля name"""
        vacancy = self.create_test_vacancy(skills=[{"skill": "Python"}, {"name": "Django"}])
        
        assert vacancy_contains_keyword(vacancy, "django") == True
        assert vacancy_contains_keyword(vacancy, "python") == False

    def test_vacancy_contains_keyword_profession_attribute(self):
        """Тест поиска ключевого слова в атрибуте profession"""
        vacancy = self.create_test_vacancy(title="Developer")
        vacancy.profession = "Python Developer"
        
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
            skills=None,
            employer=None,
            employment=None,
            schedule=None,
            experience=None,
            benefits=None,
            vacancy_id=None
        )
        vacancies = [vacancy]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 0

    def test_filter_vacancies_by_keyword_employer_without_name(self):
        """Тест фильтрации с работодателем без поля name"""
        vacancies = [
            self.create_test_vacancy(title="Developer", employer={"company": "Python Corp"}),
            self.create_test_vacancy(title="Developer", employer={"name": "Java Corp"}),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 0  # Поле name отсутствует в первом работодателе

    def test_filter_vacancies_relevance_score_attribute(self):
        """Тест добавления атрибута _relevance_score"""
        vacancies = [
            self.create_test_vacancy(title="Python Developer"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert hasattr(filtered[0], '_relevance_score')
        assert filtered[0]._relevance_score > 0

    def test_vacancy_contains_keyword_edge_cases(self):
        """Тест граничных случаев для vacancy_contains_keyword"""
        # Вакансия с пустыми строками
        vacancy = self.create_test_vacancy(
            title="",
            description="",
            requirements="",
            responsibilities="",
            detailed_description=""
        )
        assert vacancy_contains_keyword(vacancy, "python") == False
        
        # Вакансия с пробелами
        vacancy = self.create_test_vacancy(title="   ")
        assert vacancy_contains_keyword(vacancy, "python") == False

    def test_filter_vacancies_by_keyword_complex_relevance(self):
        """Тест сложной системы релевантности с множественными совпадениями"""
        vacancy = self.create_test_vacancy(
            vacancy_id="python_senior_123",  # +15
            title="Senior Python Developer",  # +10
            requirements="Python, Django, Flask",  # +5
            responsibilities="Develop Python applications",  # +5
            description="Python backend development",  # +3
            detailed_description="Advanced Python programming",  # +4
            skills=[{"name": "Python"}, {"name": "FastAPI"}],  # +6
            employer={"name": "Python Solutions Inc"},  # +4
            employment="Full-time Python development",  # +3
            schedule="Flexible Python work",  # +3
            experience="5+ years Python",  # +3
            benefits="Python certification bonus"  # +2
        )
        
        vacancies = [vacancy]
        filtered = filter_vacancies_by_keyword(vacancies, "python")
        
        assert len(filtered) == 1
        # Проверяем, что балл релевантности высокий
        assert filtered[0]._relevance_score >= 50  # Минимум ожидаемый балл
