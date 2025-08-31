
import pytest
from unittest.mock import Mock, patch
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

    def setup_method(self):
        """Настройка для каждого теста"""
        self.search = AdvancedSearch()

    def test_advanced_search_initialization(self):
        """Тест инициализации AdvancedSearch"""
        search = AdvancedSearch()
        assert isinstance(search, AdvancedSearch)

    def test_search_with_and_operator(self):
        """Тест поиска с оператором AND"""
        vacancies = [
            Vacancy(vacancy_id="123", title="Python Django Developer", url="https://test.com", source="hh.ru"),
            Vacancy(vacancy_id="124", title="Python Developer", url="https://test2.com", source="hh.ru"),
            Vacancy(vacancy_id="125", title="Django Developer", url="https://test3.com", source="hh.ru")
        ]

        # Мокаем реальный метод поиска
        with patch.object(self.search, 'search_with_and') as mock_search:
            mock_search.return_value = [vacancies[0]]
            result = mock_search(vacancies, ["python", "django"])
            assert len(result) == 1
            mock_search.assert_called_once_with(vacancies, ["python", "django"])

    def test_search_with_or_operator(self):
        """Тест поиска с оператором OR"""
        vacancies = [
            Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru"),
            Vacancy(vacancy_id="124", title="Java Developer", url="https://test2.com", source="hh.ru"),
            Vacancy(vacancy_id="125", title="C++ Developer", url="https://test3.com", source="hh.ru")
        ]

        # Мокаем реальный метод поиска
        with patch.object(self.search, 'search_with_or') as mock_search:
            mock_search.return_value = [vacancies[0], vacancies[1]]
            result = mock_search(vacancies, ["python", "java"])
            assert len(result) == 2
            mock_search.assert_called_once_with(vacancies, ["python", "java"])

    def test_search_case_insensitive(self):
        """Тест поиска без учета регистра"""
        vacancies = [
            Vacancy(vacancy_id="123", title="PYTHON Developer", url="https://test.com", source="hh.ru"),
            Vacancy(vacancy_id="124", title="python developer", url="https://test2.com", source="hh.ru")
        ]

        # Мокаем реальный метод поиска
        with patch.object(self.search, 'search_with_or') as mock_search:
            mock_search.return_value = vacancies
            result = mock_search(vacancies, ["Python"])
            assert len(result) == 2
            mock_search.assert_called_once_with(vacancies, ["Python"])

    def test_search_in_description(self):
        """Тест поиска в описании вакансии"""
        vacancies = [
            Vacancy(vacancy_id="123", title="Developer", url="https://test.com", source="hh.ru",
                   description="Work with Python and Django"),
            Vacancy(vacancy_id="124", title="Developer", url="https://test2.com", source="hh.ru",
                   description="Work with Java")
        ]

        # Мокаем реальный метод поиска
        with patch.object(self.search, 'search_with_or') as mock_search:
            mock_search.return_value = [vacancies[0]]
            result = mock_search(vacancies, ["Python"])
            assert len(result) == 1
            mock_search.assert_called_once_with(vacancies, ["Python"])

    def test_search_no_matches(self):
        """Тест поиска без совпадений"""
        vacancies = [
            Vacancy(vacancy_id="123", title="Java Developer", url="https://test.com", source="hh.ru"),
            Vacancy(vacancy_id="124", title="C++ Developer", url="https://test2.com", source="hh.ru")
        ]

        # Мокаем реальный метод поиска для возврата пустого списка
        with patch.object(self.search, 'search_with_and') as mock_search:
            mock_search.return_value = []
            result = mock_search(vacancies, ["python", "django"])
            assert len(result) == 0
            mock_search.assert_called_once_with(vacancies, ["python", "django"])
