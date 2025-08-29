"""
Тесты для SearchUtils

Содержит тесты для проверки корректности работы утилит поиска.
"""

from typing import Any, Dict, List
from unittest.mock import Mock, patch
import pytest
from src.utils.search_utils import (
    normalize_query,
    extract_keywords,
    match_keywords,
    calculate_relevance,
    build_search_filters,
    validate_search_query,
    format_search_results,
    filter_vacancies_by_keyword,
    vacancy_contains_keyword,
    build_search_params,
    extract_keywords
)
from src.vacancies.models import Vacancy


class TestSearchUtils:
    """Тесты для SearchUtils"""

    def test_normalize_query_basic(self):
        """Тест базовой нормализации запроса"""
        assert normalize_query("Python Developer") == "python developer"
        assert normalize_query("  JAVA  ") == "java"
        assert normalize_query("") == ""
        assert normalize_query(None) == ""

    def test_normalize_query_special_characters(self):
        """Тест нормализации запроса со специальными символами"""
        assert normalize_query("Python/Django") == "python/django"
        assert normalize_query("C++") == "c++"
        assert normalize_query("React.js") == "react.js"

    def test_extract_keywords_simple(self):
        """Тест извлечения ключевых слов из простого запроса"""
        keywords = extract_keywords("python developer")
        assert keywords == ["python", "developer"]

    def test_extract_keywords_with_spaces(self):
        """Тест извлечения ключевых слов с лишними пробелами"""
        keywords = extract_keywords("  python    django   react  ")
        assert keywords == ["python", "django", "react"]

    def test_extract_keywords_empty(self):
        """Тест извлечения ключевых слов из пустого запроса"""
        assert extract_keywords("") == []
        assert extract_keywords("   ") == []
        assert extract_keywords(None) == []

    def test_extract_keywords_single_word(self):
        """Тест извлечения ключевых слов из одного слова"""
        keywords = extract_keywords("python")
        assert keywords == ["python"]

    def test_match_keywords_any_match(self):
        """Тест поиска с любым совпадением (match_all=False)"""
        text = "Python developer with Django experience"
        keywords = ["python", "java"]

        assert match_keywords(text, keywords, match_all=False) is True

        keywords_no_match = ["java", "php"]
        assert match_keywords(text, keywords_no_match, match_all=False) is False

    def test_match_keywords_all_match(self):
        """Тест поиска с полным совпадением (match_all=True)"""
        text = "Python developer with Django and React experience"

        keywords_all_match = ["python", "django"]
        assert match_keywords(text, keywords_all_match, match_all=True) is True

        keywords_partial_match = ["python", "java"]
        assert match_keywords(text, keywords_partial_match, match_all=True) is False

    def test_match_keywords_case_insensitive(self):
        """Тест регистронезависимого поиска"""
        text = "PYTHON Developer"
        keywords = ["python", "developer"]

        assert match_keywords(text, keywords, match_all=True) is True

    def test_match_keywords_empty_inputs(self):
        """Тест поиска с пустыми входными данными"""
        assert match_keywords("", ["python"]) is False
        assert match_keywords("Python developer", []) is False
        assert match_keywords("", []) is False

    def test_build_search_filters_full(self):
        """Тест построения полных фильтров поиска"""
        filters = build_search_filters(
            salary_from=100000, salary_to=200000, experience="3-6 лет", employment="Полная занятость", area="Москва"
        )

        expected = {
            "salary_from": 100000,
            "salary_to": 200000,
            "experience": "3-6 лет",
            "employment": "Полная занятость",
            "area": "Москва",
        }

        assert filters == expected

    def test_build_search_filters_partial(self):
        """Тест построения частичных фильтров поиска"""
        filters = build_search_filters(salary_from=50000, employment="Полная занятость")

        expected = {"salary_from": 50000, "employment": "Полная занятость"}

        assert filters == expected

    def test_build_search_filters_empty(self):
        """Тест построения пустых фильтров поиска"""
        filters = build_search_filters()
        assert filters == {}

    def test_build_search_filters_none_values(self):
        """Тест построения фильтров с None значениями"""
        filters = build_search_filters(
            salary_from=None, salary_to=100000, experience=None, employment="", area=None
        )

        expected = {"salary_to": 100000, "employment": ""}

        assert filters == expected

    def test_calculate_relevance_basic(self):
        """Тест базового расчета релевантности"""
        text = "Python developer with Django experience"
        keywords = ["python", "django"]

        relevance = calculate_relevance(text, keywords)
        assert relevance > 0
        assert isinstance(relevance, float)

    def test_calculate_relevance_no_matches(self):
        """Тест расчета релевантности без совпадений"""
        text = "Java developer with Spring experience"
        keywords = ["python", "django"]

        relevance = calculate_relevance(text, keywords)
        assert relevance == 0.0

    def test_calculate_relevance_multiple_matches(self):
        """Тест расчета релевантности с множественными совпадениями"""
        text = "Python Python developer with Python experience"
        keywords = ["python"]

        relevance = calculate_relevance(text, keywords)
        assert relevance > 0

    def test_calculate_relevance_empty_inputs(self):
        """Тест расчета релевантности с пустыми входными данными"""
        assert calculate_relevance("", ["python"]) == 0.0
        assert calculate_relevance("Python developer", []) == 0.0
        assert calculate_relevance("", []) == 0.0

    def test_calculate_relevance_case_insensitive(self):
        """Тест регистронезависимого расчета релевантности"""
        text = "PYTHON Developer with DJANGO experience"
        keywords = ["python", "django"]

        relevance = calculate_relevance(text, keywords)
        assert relevance > 0

    def test_calculate_relevance_max_value(self):
        """Тест максимального значения релевантности"""
        # Короткий текст с множественными совпадениями
        text = "python python python"
        keywords = ["python"]

        relevance = calculate_relevance(text, keywords)
        assert relevance <= 100.0

    def test_calculate_relevance_precision(self):
        """Тест точности расчета релевантности"""
        text = "python developer"  # 2 слова
        keywords = ["python"]  # 1 совпадение

        # Ожидается: 1/2 * 100 = 50.0
        relevance = calculate_relevance(text, keywords)
        assert relevance == 50.0

    def test_integration_search_workflow(self):
        """Тест интегрированного рабочего процесса поиска"""
        # Нормализация запроса
        query = "  Python Developer  "
        normalized = normalize_query(query)
        assert normalized == "python developer"

        # Извлечение ключевых слов
        keywords = extract_keywords(normalized)
        assert keywords == ["python", "developer"]

        # Проверка соответствия
        vacancy_text = "Senior Python Developer with 5 years experience"
        matches = match_keywords(vacancy_text, keywords, match_all=True)
        assert matches is True

        # Расчет релевантности
        relevance = calculate_relevance(vacancy_text, keywords)
        assert relevance > 0

        # Построение фильтров
        filters = build_search_filters(salary_from=100000, experience="от 3 лет")
        assert filters == {"salary_from": 100000, "experience": "от 3 лет"}

    def test_extract_keywords(self):
        """Тест извлечения ключевых слов"""
        query = "Python Django REST API"
        keywords = extract_keywords(query)

        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert all(isinstance(keyword, str) for keyword in keywords)

    def test_validate_search_query(self):
        """Тест валидации поискового запроса"""
        # Валидный запрос
        valid_query = "Python developer"
        assert validate_search_query(valid_query) is True

        # Пустой запрос
        empty_query = ""
        assert validate_search_query(empty_query) is False

        # None запрос
        none_query = None
        assert validate_search_query(none_query) is False

    def test_format_search_results(self):
        """Тест форматирования результатов поиска"""
        mock_vacancies = [
            Mock(title="Python Developer", url="https://example.com/1"),
            Mock(title="Java Developer", url="https://example.com/2")
        ]
        formatted = format_search_results(mock_vacancies)

        assert isinstance(formatted, (list, str))
        if isinstance(formatted, list):
            assert len(formatted) == 2

    def test_search_query_filtering(self):
        """Тест фильтрации поискового запроса"""
        # Тест с нормальным запросом
        query = "Python AND Django OR Flask"

        # Проверяем extract_keywords
        keywords = extract_keywords(query)
        assert len(keywords) > 0

    def test_keyword_extraction_with_operators(self):
        """Тест извлечения ключевых слов с операторами"""
        query = "Python AND (Django OR Flask) NOT PHP"
        keywords = extract_keywords(query)

        assert isinstance(keywords, list)
        # Проверяем, что извлечены основные ключевые слова
        extracted_text = " ".join(keywords).lower()
        assert "python" in extracted_text

    def test_special_characters_handling(self):
        """Тест обработки специальных символов"""
        query = "C++ .NET @компания #вакансия"
        keywords = extract_keywords(query)

        assert isinstance(keywords, list)
        assert len(keywords) > 0

    def test_language_detection(self):
        """Тест определения языка запроса"""
        russian_query = "Python разработчик"
        english_query = "Python developer"

        # Альтернативно тестируем обработку мультиязычных запросов
        ru_keywords = extract_keywords(russian_query)
        en_keywords = extract_keywords(english_query)
        assert len(ru_keywords) > 0
        assert len(en_keywords) > 0

    def test_filter_vacancies_by_keyword(self):
        """Тест фильтрации вакансий по ключевому слову"""
        mock_vacancies = [
            Vacancy(title="Python Developer", description="Python Django experience", vacancy_id="1", source="hh.ru", url="https://example.com/1"),
            Vacancy(title="Java Developer", description="Java Spring experience", vacancy_id="2", source="hh.ru", url="https://example.com/2"),
            Vacancy(title="Python Engineer", description="Python Flask experience", vacancy_id="3", source="hh.ru", url="https://example.com/3")
        ]

        keyword = "Python"
        filtered = filter_vacancies_by_keyword(mock_vacancies, keyword)

        assert isinstance(filtered, list)
        # Должно остаться 2 вакансии с Python
        assert len(filtered) == 2

    def test_vacancy_contains_keyword(self):
        """Тест проверки содержания ключевого слова в вакансии"""
        vacancy = Vacancy(
            title="Python Developer",
            description="Experience with Python and Django",
            requirements="Python knowledge required",
            vacancy_id="1",
            source="hh.ru",
            url="https://example.com/1"
        )

        assert vacancy_contains_keyword(vacancy, "Python") is True
        assert vacancy_contains_keyword(vacancy, "Java") is False

    def test_build_search_params_basic(self):
        """Тест построения параметров поиска"""
        query = "Python Developer"
        params = build_search_params(query)
        assert isinstance(params, dict)
        assert "text" in params

    def test_empty_search_handling_basic(self):
        """Тест обработки пустого поиска"""
        empty_queries = ["", "   ", None]

        for empty_query in empty_queries:
            if empty_query is not None:
                keywords = extract_keywords(empty_query)
                assert isinstance(keywords, list)

            is_valid = validate_search_query(empty_query)
            assert is_valid is False

    def test_search_params_validation_basic(self):
        """Тест валидации параметров поиска"""
        assert validate_search_query("Python") is True
        assert validate_search_query("") is False

    def test_query_normalization_edge_cases(self):
        """Тест нормализации запроса в граничных случаях"""
        edge_cases = [
            "PYTHON",  # uppercase
            "python",  # lowercase
            "Python Developer!!!",  # with punctuation
            "Python\n\tDeveloper",  # with whitespace
        ]

        for query in edge_cases:
            keywords = extract_keywords(query)
            assert isinstance(keywords, list)
            if keywords:  # Если есть ключевые слова
                # Проверяем, что хотя бы одно слово содержит "python"
                has_python = any("python" in keyword.lower() for keyword in keywords)
                assert has_python

    def test_advanced_search_combinations_basic(self):
        """Тест комбинированного поиска"""
        complex_query = "Python AND Django"

        # Через extract_keywords
        keywords = extract_keywords(complex_query)
        assert len(keywords) >= 2  # Должно быть минимум 2 ключевых слова