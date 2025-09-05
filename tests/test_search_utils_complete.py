
"""
Полные тесты для утилит поиска
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.search_utils import (
        normalize_query, extract_keywords, build_search_params,
        validate_search_query, format_search_results,
        filter_vacancies_by_keyword, vacancy_contains_keyword,
        SearchQueryParser, AdvancedSearch
    )
    SEARCH_UTILS_AVAILABLE = True
except ImportError:
    SEARCH_UTILS_AVAILABLE = False


class MockVacancy:
    """Мок объект вакансии для тестирования"""
    
    def __init__(self, **kwargs):
        self.vacancy_id = kwargs.get('vacancy_id', '1')
        self.title = kwargs.get('title', 'Python Developer')
        self.description = kwargs.get('description', 'Python development job')
        self.requirements = kwargs.get('requirements', 'Python, Django')
        self.responsibilities = kwargs.get('responsibilities', 'Develop applications')
        self.detailed_description = kwargs.get('detailed_description', 'Detailed job description')
        self.skills = kwargs.get('skills', [])
        self.employer = kwargs.get('employer', {'name': 'Test Company'})
        self.employment = kwargs.get('employment', 'Полная занятость')
        self.schedule = kwargs.get('schedule', 'Полный день')
        self.experience = kwargs.get('experience', 'От 1 года до 3 лет')
        self.benefits = kwargs.get('benefits', 'Good benefits')
        self.search_query = kwargs.get('search_query', '')


class TestSearchUtilsComplete:
    """Полные тесты для утилит поиска"""

    def test_normalize_query_basic(self):
        """Тест базовой нормализации запроса"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = normalize_query("  Python Developer  ")
        assert result == "python developer"

    def test_normalize_query_multiple_spaces(self):
        """Тест нормализации запроса с множественными пробелами"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = normalize_query("Python    Developer    Job")
        assert result == "python developer job"

    def test_normalize_query_empty(self):
        """Тест нормализации пустого запроса"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = normalize_query("")
        assert result == ""

    def test_normalize_query_long(self):
        """Тест нормализации длинного запроса"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        long_query = "a" * 600
        result = normalize_query(long_query)
        assert len(result) == 500

    def test_extract_keywords_basic(self):
        """Тест извлечения ключевых слов"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = extract_keywords("Python Django Developer")
        assert "python" in result
        assert "django" in result
        assert "developer" in result

    def test_extract_keywords_with_stop_words(self):
        """Тест извлечения ключевых слов со стоп-словами"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = extract_keywords("Python и Django разработка")
        assert "python" in result
        assert "django" in result
        assert "разработка" in result
        assert "и" not in result

    def test_extract_keywords_empty(self):
        """Тест извлечения из пустого запроса"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = extract_keywords("")
        assert result == []

    def test_build_search_params_basic(self):
        """Тест построения базовых параметров поиска"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = build_search_params("Python")
        assert result['text'] == "Python"
        assert result['per_page'] == 50
        assert result['page'] == 0

    def test_build_search_params_with_kwargs(self):
        """Тест построения параметров с дополнительными аргументами"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = build_search_params("Python", salary_from=100000, area="Moscow")
        assert result['salary'] == 100000
        assert result['area'] == "Moscow"

    def test_build_search_params_limit_per_page(self):
        """Тест ограничения количества на странице"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = build_search_params("Python", per_page=200)
        assert result['per_page'] == 100  # Максимум 100

    def test_validate_search_query_valid(self):
        """Тест валидации корректного запроса"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        assert validate_search_query("Python") == True

    def test_validate_search_query_empty(self):
        """Тест валидации пустого запроса"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        assert validate_search_query("") == False

    def test_validate_search_query_not_string(self):
        """Тест валидации не строки"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        assert validate_search_query(123) == False

    def test_validate_search_query_whitespace_only(self):
        """Тест валидации запроса только из пробелов"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        assert validate_search_query("   ") == False

    def test_format_search_results_basic(self):
        """Тест форматирования результатов поиска"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        results = [
            {'id': '1', 'name': 'Python Developer', 'alternate_url': 'http://test.com'},
            {'vacancy_id': '2', 'profession': 'Java Developer', 'link': 'http://test2.com'}
        ]
        
        formatted = format_search_results(results)
        assert len(formatted) == 2
        assert formatted[0]['id'] == '1'
        assert formatted[0]['title'] == 'Python Developer'
        assert formatted[1]['id'] == '2'
        assert formatted[1]['title'] == 'Java Developer'

    def test_format_search_results_empty(self):
        """Тест форматирования пустых результатов"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        result = format_search_results([])
        assert result == []

    def test_format_search_results_invalid_items(self):
        """Тест форматирования с невалидными элементами"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        results = [
            {'id': '1', 'name': 'Python Developer'},
            "invalid_item",
            None
        ]
        
        formatted = format_search_results(results)
        assert len(formatted) == 1  # Только валидный элемент


class TestVacancyFiltering:
    """Тесты для фильтрации вакансий"""

    def test_filter_vacancies_by_keyword_title(self):
        """Тест фильтрации по ключевому слову в заголовке"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        vacancies = [
            MockVacancy(title="Python Developer"),
            MockVacancy(title="Java Developer"),
            MockVacancy(title="Python Analyst")
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "Python")
        assert len(filtered) == 2
        assert all("Python" in v.title for v in filtered)

    def test_filter_vacancies_by_keyword_description(self):
        """Тест фильтрации по ключевому слову в описании"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        vacancies = [
            MockVacancy(description="Work with Python frameworks"),
            MockVacancy(description="Java development"),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "Python")
        assert len(filtered) == 1

    def test_filter_vacancies_by_keyword_skills(self):
        """Тест фильтрации по навыкам"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        vacancies = [
            MockVacancy(skills=[{"name": "Python"}, {"name": "Django"}]),
            MockVacancy(skills=[{"name": "Java"}, {"name": "Spring"}]),
        ]
        
        filtered = filter_vacancies_by_keyword(vacancies, "Python")
        assert len(filtered) == 1

    def test_filter_vacancies_by_keyword_case_insensitive(self):
        """Тест регистронезависимой фильтрации"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        vacancies = [MockVacancy(title="python developer")]
        filtered = filter_vacancies_by_keyword(vacancies, "PYTHON")
        assert len(filtered) == 1

    def test_vacancy_contains_keyword_title(self):
        """Тест проверки наличия ключевого слова в заголовке"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        vacancy = MockVacancy(title="Python Developer")
        assert vacancy_contains_keyword(vacancy, "Python") == True
        assert vacancy_contains_keyword(vacancy, "Java") == False

    def test_vacancy_contains_keyword_multiple_fields(self):
        """Тест проверки во множественных полях"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        vacancy = MockVacancy(
            title="Developer",
            requirements="Python required",
            responsibilities="Django development"
        )
        
        assert vacancy_contains_keyword(vacancy, "Python") == True
        assert vacancy_contains_keyword(vacancy, "Django") == True
        assert vacancy_contains_keyword(vacancy, "Java") == False


class TestSearchQueryParser:
    """Тесты для парсера поисковых запросов"""

    def test_parser_single_keyword(self):
        """Тест парсинга одного ключевого слова"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        parser = SearchQueryParser()
        result = parser.parse("Python")
        assert result['keywords'] == ["Python"]
        assert result['operator'] == "OR"

    def test_parser_and_operator(self):
        """Тест парсинга с оператором AND"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        parser = SearchQueryParser()
        result = parser.parse("Python AND Django")
        assert "PYTHON" in result['keywords']
        assert "DJANGO" in result['keywords']
        assert result['operator'] == "AND"

    def test_parser_or_operator(self):
        """Тест парсинга с оператором OR"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        parser = SearchQueryParser()
        result = parser.parse("Python OR Java")
        assert "PYTHON" in result['keywords']
        assert "JAVA" in result['keywords']
        assert result['operator'] == "OR"

    def test_parser_comma_separated(self):
        """Тест парсинга через запятую"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        parser = SearchQueryParser()
        result = parser.parse("Python, Java, Django")
        assert "Python" in result['keywords']
        assert "Java" in result['keywords']
        assert "Django" in result['keywords']
        assert result['operator'] == "OR"

    def test_parser_empty_query(self):
        """Тест парсинга пустого запроса"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        parser = SearchQueryParser()
        result = parser.parse("")
        assert result is None


class TestAdvancedSearch:
    """Тесты для продвинутого поиска"""

    def test_search_with_and(self):
        """Тест поиска с оператором AND"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        search = AdvancedSearch()
        vacancies = [
            MockVacancy(title="Python Developer", description="Django framework"),
            MockVacancy(title="Python Analyst", description="Data analysis"),
            MockVacancy(title="Java Developer", description="Spring framework")
        ]
        
        result = search.search_with_and(vacancies, ["Python", "Django"])
        assert len(result) == 1
        assert result[0].title == "Python Developer"

    def test_search_with_or(self):
        """Тест поиска с оператором OR"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        search = AdvancedSearch()
        vacancies = [
            MockVacancy(title="Python Developer"),
            MockVacancy(title="Java Developer"),
            MockVacancy(title="C++ Developer")
        ]
        
        result = search.search_with_or(vacancies, ["Python", "Java"])
        assert len(result) == 2

    def test_search_with_search_query_field(self):
        """Тест поиска с полем search_query"""
        if not SEARCH_UTILS_AVAILABLE:
            pytest.skip("Search utils not available")
        
        search = AdvancedSearch()
        vacancies = [
            MockVacancy(title="Developer", search_query="Python Django"),
            MockVacancy(title="Analyst", search_query="Data Science")
        ]
        
        result = search.search_with_and(vacancies, ["Python"])
        assert len(result) == 1
        assert result[0].search_query == "Python Django"
