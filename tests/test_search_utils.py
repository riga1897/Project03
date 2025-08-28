
"""
Тесты для модуля search_utils
"""

import pytest
from unittest.mock import Mock, patch
from src.utils.search_utils import create_search_params, filter_by_keywords, normalize_query


class TestSearchUtils:
    """Тесты для утилит поиска"""

    def test_create_search_params_basic(self):
        """Тест создания базовых параметров поиска"""
        query = "python developer"
        params = create_search_params(query)
        
        assert "text" in params
        assert params["text"] == query

    def test_create_search_params_with_additional_params(self):
        """Тест создания параметров поиска с дополнительными параметрами"""
        query = "python"
        additional_params = {"page": 1, "per_page": 20}
        
        params = create_search_params(query, **additional_params)
        
        assert params["text"] == query
        assert params["page"] == 1
        assert params["per_page"] == 20

    def test_filter_by_keywords_single_keyword(self):
        """Тест фильтрации по одному ключевому слову"""
        vacancies = [
            {"title": "Python Developer", "description": "Python programming"},
            {"title": "Java Developer", "description": "Java programming"},
            {"title": "Frontend Developer", "description": "JavaScript and React"}
        ]
        
        filtered = filter_by_keywords(vacancies, ["python"])
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Python Developer"

    def test_filter_by_keywords_multiple_keywords(self):
        """Тест фильтрации по нескольким ключевым словам"""
        vacancies = [
            {"title": "Python Developer", "description": "Python programming"},
            {"title": "Java Developer", "description": "Java programming"},
            {"title": "Senior Python Developer", "description": "Senior Python programming"}
        ]
        
        filtered = filter_by_keywords(vacancies, ["python", "senior"])
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Senior Python Developer"

    def test_filter_by_keywords_case_insensitive(self):
        """Тест нечувствительности к регистру при фильтрации"""
        vacancies = [
            {"title": "Python Developer", "description": "Python programming"},
            {"title": "PYTHON DEVELOPER", "description": "PYTHON PROGRAMMING"}
        ]
        
        filtered = filter_by_keywords(vacancies, ["python"])
        assert len(filtered) == 2

    def test_filter_by_keywords_no_matches(self):
        """Тест фильтрации без совпадений"""
        vacancies = [
            {"title": "Java Developer", "description": "Java programming"},
            {"title": "C++ Developer", "description": "C++ programming"}
        ]
        
        filtered = filter_by_keywords(vacancies, ["python"])
        assert len(filtered) == 0

    def test_normalize_query_basic(self):
        """Тест базовой нормализации запроса"""
        query = "  Python   Developer  "
        normalized = normalize_query(query)
        assert normalized == "python developer"

    def test_normalize_query_empty_string(self):
        """Тест нормализации пустой строки"""
        query = "   "
        normalized = normalize_query(query)
        assert normalized == ""

    def test_normalize_query_special_characters(self):
        """Тест нормализации с специальными символами"""
        query = "Python/JavaScript Developer!"
        normalized = normalize_query(query)
        assert "python" in normalized.lower()
        assert "javascript" in normalized.lower()

    def test_create_search_params_with_salary_range(self):
        """Тест создания параметров поиска с диапазоном зарплаты"""
        query = "python"
        params = create_search_params(query, salary_from=50000, salary_to=100000)
        
        assert params["text"] == query
        assert params["salary_from"] == 50000
        assert params["salary_to"] == 100000

    def test_filter_by_keywords_in_description(self):
        """Тест поиска ключевых слов в описании"""
        vacancies = [
            {"title": "Developer", "description": "Looking for Python developer"},
            {"title": "Developer", "description": "Java and Spring framework"},
            {"title": "Developer", "description": "Frontend with React and Python"}
        ]
        
        filtered = filter_by_keywords(vacancies, ["python"])
        assert len(filtered) == 2

    def test_filter_by_keywords_empty_list(self):
        """Тест фильтрации с пустым списком ключевых слов"""
        vacancies = [
            {"title": "Python Developer", "description": "Python programming"},
            {"title": "Java Developer", "description": "Java programming"}
        ]
        
        filtered = filter_by_keywords(vacancies, [])
        assert len(filtered) == 2  # Все вакансии должны остаться

    def test_create_search_params_validation(self):
        """Тест валидации параметров поиска"""
        query = ""
        params = create_search_params(query)
        
        # Даже с пустым запросом должен возвращаться словарь
        assert isinstance(params, dict)
        assert "text" in params
