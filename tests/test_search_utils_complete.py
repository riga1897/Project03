
"""
Полные тесты для модуля search_utils с 100% покрытием
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.search_utils import (
    normalize_query,
    extract_keywords, 
    build_search_params,
    validate_search_query,
    format_search_results,
    filter_vacancies_by_keyword,
    vacancy_contains_keyword,
    SearchQueryParser,
    AdvancedSearch
)
from src.vacancies.models import Vacancy


class TestSearchUtilsFunctions:
    """Тесты для функций поиска"""

    def test_normalize_query_empty(self):
        """Тест нормализации пустого запроса"""
        assert normalize_query("") == ""
        assert normalize_query(None) == ""

    def test_normalize_query_basic(self):
        """Тест базовой нормализации"""
        result = normalize_query("  Python  Developer  ")
        assert result == "python developer"

    def test_normalize_query_long(self):
        """Тест обрезания длинного запроса"""
        long_query = "a" * 600
        result = normalize_query(long_query)
        assert len(result) == 500

    def test_extract_keywords_empty(self):
        """Тест извлечения ключевых слов из пустого запроса"""
        assert extract_keywords("") == []
        assert extract_keywords(None) == []

    def test_extract_keywords_basic(self):
        """Тест извлечения ключевых слов"""
        keywords = extract_keywords("Python AND Java OR C++")
        assert "python" in keywords
        assert "java" in keywords
        assert "c++" in keywords

    def test_extract_keywords_stop_words(self):
        """Тест фильтрации стоп-слов"""
        keywords = extract_keywords("работа в IT")
        assert "работа" not in keywords
        assert "в" not in keywords
        assert "it" in keywords

    def test_build_search_params_basic(self):
        """Тест построения базовых параметров"""
        params = build_search_params("Python", per_page=20, page=1)
        assert params["text"] == "Python"
        assert params["per_page"] == 20
        assert params["page"] == 1

    def test_build_search_params_limit(self):
        """Тест ограничения per_page"""
        params = build_search_params("Python", per_page=150)
        assert params["per_page"] == 100

    def test_build_search_params_extra(self):
        """Тест дополнительных параметров"""
        params = build_search_params(
            "Python", 
            salary_from=100000,
            salary_to=200000,
            area="Moscow",
            experience="between1And3"
        )
        assert params["salary"] == 100000
        assert params["salary_to"] == 200000
        assert params["area"] == "Moscow"
        assert params["experience"] == "between1And3"

    def test_validate_search_query_valid(self):
        """Тест валидации корректного запроса"""
        assert validate_search_query("Python") is True
        assert validate_search_query("  Java  ") is True

    def test_validate_search_query_invalid(self):
        """Тест валидации некорректного запроса"""
        assert validate_search_query("") is False
        assert validate_search_query(None) is False
        assert validate_search_query(123) is False
        assert validate_search_query("   ") is False

    def test_format_search_results_empty(self):
        """Тест форматирования пустых результатов"""
        assert format_search_results([]) == []
        assert format_search_results(None) == []

    def test_format_search_results_basic(self):
        """Тест форматирования результатов"""
        results = [
            {"id": "123", "name": "Python Developer", "alternate_url": "http://example.com"},
            {"vacancy_id": "456", "profession": "Java Developer", "link": "http://example2.com"}
        ]
        formatted = format_search_results(results)
        
        assert len(formatted) == 2
        assert formatted[0]["id"] == "123"
        assert formatted[0]["title"] == "Python Developer"
        assert formatted[1]["id"] == "456"
        assert formatted[1]["title"] == "Java Developer"

    def test_format_search_results_invalid_data(self):
        """Тест обработки невалидных данных"""
        results = [
            {"id": "123", "name": "Developer"},
            "invalid_item",
            None,
            {"title": "Test"}
        ]
        formatted = format_search_results(results)
        assert len(formatted) == 2


class TestVacancyFiltering:
    """Тесты для фильтрации вакансий"""

    @pytest.fixture
    def sample_vacancies(self):
        """Фикстура с тестовыми вакансиями"""
        vacancies = []
        
        # Вакансия 1
        v1 = Vacancy("1", "Python Developer", "http://example.com/1")
        v1.requirements = "Python, Django, REST API"
        v1.responsibilities = "Разработка веб-приложений"
        v1.description = "Опыт работы с Python"
        v1.detailed_description = "Требуется знание фреймворков"
        v1.skills = [{"name": "Python"}, {"name": "Django"}]
        v1.employer = {"name": "Tech Company"}
        v1.employment = "Полная занятость"
        v1.schedule = "Полный день"
        v1.experience = "От 1 года до 3 лет"
        v1.benefits = "ДМС, обучение"
        vacancies.append(v1)
        
        # Вакансия 2
        v2 = Vacancy("2", "Java Developer", "http://example.com/2")
        v2.requirements = "Java, Spring"
        v2.description = "Backend разработка"
        v2.skills = ["Java", "Spring Boot"]
        vacancies.append(v2)
        
        return vacancies

    def test_filter_vacancies_by_keyword_title(self, sample_vacancies):
        """Тест фильтрации по заголовку"""
        filtered = filter_vacancies_by_keyword(sample_vacancies, "Python")
        assert len(filtered) == 1
        assert filtered[0].title == "Python Developer"

    def test_filter_vacancies_by_keyword_requirements(self, sample_vacancies):
        """Тест фильтрации по требованиям"""
        filtered = filter_vacancies_by_keyword(sample_vacancies, "Django")
        assert len(filtered) == 1

    def test_filter_vacancies_by_keyword_skills(self, sample_vacancies):
        """Тест фильтрации по навыкам"""
        filtered = filter_vacancies_by_keyword(sample_vacancies, "Spring")
        assert len(filtered) == 1

    def test_filter_vacancies_by_keyword_employer(self, sample_vacancies):
        """Тест фильтрации по работодателю"""
        filtered = filter_vacancies_by_keyword(sample_vacancies, "Tech")
        assert len(filtered) == 1

    def test_filter_vacancies_relevance_score(self, sample_vacancies):
        """Тест оценки релевантности"""
        filtered = filter_vacancies_by_keyword(sample_vacancies, "Python")
        assert hasattr(filtered[0], "_relevance_score")
        assert filtered[0]._relevance_score > 0

    def test_vacancy_contains_keyword_true(self, sample_vacancies):
        """Тест проверки наличия ключевого слова"""
        assert vacancy_contains_keyword(sample_vacancies[0], "Python") is True
        assert vacancy_contains_keyword(sample_vacancies[0], "Django") is True

    def test_vacancy_contains_keyword_false(self, sample_vacancies):
        """Тест отсутствия ключевого слова"""
        assert vacancy_contains_keyword(sample_vacancies[0], "C++") is False

    def test_vacancy_contains_keyword_profession(self):
        """Тест поиска в поле profession"""
        vacancy = Vacancy("1", "Test", "http://example.com")
        vacancy.profession = "Python Developer"
        assert vacancy_contains_keyword(vacancy, "Python") is True


class TestSearchQueryParser:
    """Тесты для парсера запросов"""

    def test_parser_init(self):
        """Тест инициализации парсера"""
        parser = SearchQueryParser()
        assert parser is not None

    def test_parse_empty(self):
        """Тест парсинга пустого запроса"""
        parser = SearchQueryParser()
        assert parser.parse("") is None
        assert parser.parse("  ") is None
        assert parser.parse(None) is None

    def test_parse_and_operator(self):
        """Тест парсинга с оператором AND"""
        parser = SearchQueryParser()
        result = parser.parse("Python AND Django")
        assert result["operator"] == "AND"
        assert "PYTHON" in result["keywords"]
        assert "DJANGO" in result["keywords"]

    def test_parse_or_operator(self):
        """Тест парсинга с оператором OR"""
        parser = SearchQueryParser()
        result = parser.parse("Python OR Java")
        assert result["operator"] == "OR"
        assert "PYTHON" in result["keywords"]
        assert "JAVA" in result["keywords"]

    def test_parse_comma_separator(self):
        """Тест парсинга с запятой"""
        parser = SearchQueryParser()
        result = parser.parse("Python, Java, C++")
        assert result["operator"] == "OR"
        assert len(result["keywords"]) == 3

    def test_parse_single_keyword(self):
        """Тест парсинга одного ключевого слова"""
        parser = SearchQueryParser()
        result = parser.parse("Python")
        assert result["operator"] == "OR"
        assert result["keywords"] == ["Python"]


class TestAdvancedSearch:
    """Тесты для продвинутого поиска"""

    @pytest.fixture
    def search_instance(self):
        """Фикстура с экземпляром поиска"""
        return AdvancedSearch()

    @pytest.fixture
    def test_vacancies(self):
        """Фикстура с тестовыми вакансиями для поиска"""
        vacancies = []
        
        v1 = Mock()
        v1.title = "Python Developer"
        v1.description = "Опыт с Django"
        v1.search_query = "backend python"
        vacancies.append(v1)
        
        v2 = Mock()
        v2.title = "Java Developer"
        v2.description = "Spring Boot"
        v2.search_query = "java backend"
        vacancies.append(v2)
        
        v3 = Mock()
        v3.title = "Frontend Developer"
        v3.description = "React, JavaScript"
        v3.search_query = None
        vacancies.append(v3)
        
        return vacancies

    def test_advanced_search_init(self, search_instance):
        """Тест инициализации"""
        assert search_instance is not None

    def test_search_with_and(self, search_instance, test_vacancies):
        """Тест поиска с оператором AND"""
        keywords = ["Python", "backend"]
        result = search_instance.search_with_and(test_vacancies, keywords)
        assert len(result) == 1
        assert result[0].title == "Python Developer"

    def test_search_with_and_no_results(self, search_instance, test_vacancies):
        """Тест поиска AND без результатов"""
        keywords = ["Python", "React"]
        result = search_instance.search_with_and(test_vacancies, keywords)
        assert len(result) == 0

    def test_search_with_or(self, search_instance, test_vacancies):
        """Тест поиска с оператором OR"""
        keywords = ["Python", "React"]
        result = search_instance.search_with_or(test_vacancies, keywords)
        assert len(result) == 2

    def test_search_with_or_single_keyword(self, search_instance, test_vacancies):
        """Тест поиска OR с одним ключевым словом"""
        keywords = ["backend"]
        result = search_instance.search_with_or(test_vacancies, keywords)
        assert len(result) == 2

    def test_search_with_none_search_query(self, search_instance, test_vacancies):
        """Тест поиска с None в search_query"""
        keywords = ["Frontend"]
        result = search_instance.search_with_or(test_vacancies, keywords)
        assert len(result) == 1
        assert result[0].title == "Frontend Developer"

    def test_search_case_insensitive(self, search_instance, test_vacancies):
        """Тест поиска без учета регистра"""
        keywords = ["PYTHON"]
        result = search_instance.search_with_or(test_vacancies, keywords)
        assert len(result) == 1

    def test_search_partial_match(self, search_instance, test_vacancies):
        """Тест частичного совпадения"""
        keywords = ["Develop"]
        result = search_instance.search_with_or(test_vacancies, keywords)
        assert len(result) == 3  # Все содержат "Developer"
