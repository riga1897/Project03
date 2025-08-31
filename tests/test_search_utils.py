
import pytest
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.search_utils import SearchQueryParser, AdvancedSearch
from src.vacancies.models import Vacancy


class TestSearchQueryParser:
    """Тесты для SearchQueryParser"""

    def test_parse_simple_query(self):
        """Тест парсинга простого запроса"""
        parser = SearchQueryParser()
        result = parser.parse("python")
        
        assert isinstance(result, dict)
        assert "keywords" in result

    def test_parse_and_query(self):
        """Тест парсинга запроса с AND"""
        parser = SearchQueryParser()
        result = parser.parse("python AND django")
        
        assert isinstance(result, dict)
        assert result["operator"] == "AND"

    def test_parse_or_query(self):
        """Тест парсинга запроса с OR"""
        parser = SearchQueryParser()
        result = parser.parse("python OR java")
        
        assert isinstance(result, dict)
        assert result["operator"] == "OR"

    def test_parse_comma_separated(self):
        """Тест парсинга запроса через запятую"""
        parser = SearchQueryParser()
        result = parser.parse("python, django, flask")
        
        assert isinstance(result, dict)
        assert "keywords" in result
        assert len(result["keywords"]) == 3

    def test_parse_empty_query(self):
        """Тест парсинга пустого запроса"""
        parser = SearchQueryParser()
        result = parser.parse("")
        
        assert result is None or result == {}


class TestAdvancedSearch:
    """Тесты для AdvancedSearch"""

    def test_advanced_search_initialization(self):
        """Тест инициализации AdvancedSearch"""
        search = AdvancedSearch()
        assert isinstance(search, AdvancedSearch)

    def test_search_with_and_operator(self):
        """Тест поиска с оператором AND"""
        vacancies = [
            Vacancy("123", "Python Django Developer", "https://test.com", "hh.ru"),
            Vacancy("124", "Python Developer", "https://test2.com", "hh.ru"),
            Vacancy("125", "Django Developer", "https://test3.com", "hh.ru")
        ]
        
        search = AdvancedSearch()
        result = search.search_with_and(vacancies, ["python", "django"])
        
        # Должна найтись только первая вакансия
        assert len(result) == 1
        assert result[0].vacancy_id == "123"

    def test_search_with_or_operator(self):
        """Тест поиска с оператором OR"""
        vacancies = [
            Vacancy("123", "Python Developer", "https://test.com", "hh.ru"),
            Vacancy("124", "Java Developer", "https://test2.com", "hh.ru"),
            Vacancy("125", "C++ Developer", "https://test3.com", "hh.ru")
        ]
        
        search = AdvancedSearch()
        result = search.search_with_or(vacancies, ["python", "java"])
        
        # Должны найтись первые две вакансии
        assert len(result) == 2

    def test_search_case_insensitive(self):
        """Тест поиска без учета регистра"""
        vacancies = [
            Vacancy("123", "PYTHON Developer", "https://test.com", "hh.ru"),
            Vacancy("124", "python developer", "https://test2.com", "hh.ru")
        ]
        
        search = AdvancedSearch()
        result = search.search_with_or(vacancies, ["Python"])
        
        # Должны найтись обе вакансии
        assert len(result) == 2

    def test_search_in_description(self):
        """Тест поиска в описании вакансии"""
        vacancies = [
            Vacancy("123", "Developer", "https://test.com", "hh.ru", 
                   description="Work with Python and Django"),
            Vacancy("124", "Developer", "https://test2.com", "hh.ru", 
                   description="Work with Java")
        ]
        
        search = AdvancedSearch()
        result = search.search_with_or(vacancies, ["python"])
        
        # Должна найтись первая вакансия
        assert len(result) == 1
        assert result[0].vacancy_id == "123"

    def test_search_no_matches(self):
        """Тест поиска без совпадений"""
        vacancies = [
            Vacancy("123", "Java Developer", "https://test.com", "hh.ru"),
            Vacancy("124", "C++ Developer", "https://test2.com", "hh.ru")
        ]
        
        search = AdvancedSearch()
        result = search.search_with_and(vacancies, ["python", "django"])
        
        assert len(result) == 0
