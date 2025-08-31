import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.search_utils import AdvancedSearch, SearchQueryParser
from src.vacancies.models import Vacancy


class TestSearchQueryParser:
    """Тесты для SearchQueryParser"""

    def test_parse_simple_query(self):
        """Тест парсинга простого запроса"""
        parser = SearchQueryParser()
        result = parser.parse("python")

        assert isinstance(result, dict)
        assert "keywords" in result
        assert result["keywords"] == ["python"]
        assert result["operator"] == "OR"

    def test_parse_and_query(self):
        """Тест парсинга запроса с AND"""
        parser = SearchQueryParser()
        result = parser.parse("python AND django")

        assert isinstance(result, dict)
        assert result["operator"] == "AND"
        assert len(result["keywords"]) == 2

    def test_parse_or_query(self):
        """Тест парсинга запроса с OR"""
        parser = SearchQueryParser()
        result = parser.parse("python OR java")

        assert isinstance(result, dict)
        assert result["operator"] == "OR"
        assert len(result["keywords"]) == 2

    def test_parse_comma_separated(self):
        """Тест парсинга запроса через запятую"""
        parser = SearchQueryParser()
        result = parser.parse("python, django, flask")

        assert isinstance(result, dict)
        assert "keywords" in result
        assert len(result["keywords"]) == 3
        assert result["operator"] == "OR"

    def test_parse_empty_query(self):
        """Тест парсинга пустого запроса"""
        parser = SearchQueryParser()
        result = parser.parse("")

        assert result is None


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
            Vacancy(vacancy_id="125", title="Django Developer", url="https://test3.com", source="hh.ru"),
        ]

        result = self.search.search_with_and(vacancies, ["python", "django"])
        assert len(result) == 1
        assert result[0].vacancy_id == "123"

    def test_search_with_or_operator(self):
        """Тест поиска с оператором OR"""
        vacancies = [
            Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru"),
            Vacancy(vacancy_id="124", title="Java Developer", url="https://test2.com", source="hh.ru"),
            Vacancy(vacancy_id="125", title="C++ Developer", url="https://test3.com", source="hh.ru"),
        ]

        result = self.search.search_with_or(vacancies, ["python", "java"])
        assert len(result) == 2

    def test_search_case_insensitive(self):
        """Тест поиска без учета регистра"""
        vacancies = [
            Vacancy(vacancy_id="123", title="PYTHON Developer", url="https://test.com", source="hh.ru"),
            Vacancy(vacancy_id="124", title="python developer", url="https://test2.com", source="hh.ru"),
        ]

        result = self.search.search_with_or(vacancies, ["Python"])
        assert len(result) == 2

    def test_search_in_description(self):
        """Тест поиска в описании вакансии"""
        vacancies = [
            Vacancy(
                vacancy_id="123",
                title="Developer",
                url="https://test.com",
                source="hh.ru",
                description="Work with Python and Django",
            ),
            Vacancy(
                vacancy_id="124",
                title="Developer",
                url="https://test2.com",
                source="hh.ru",
                description="Work with Java",
            ),
        ]

        result = self.search.search_with_or(vacancies, ["Python"])
        assert len(result) == 1
        assert result[0].vacancy_id == "123"

    def test_search_no_matches(self):
        """Тест поиска без совпадений"""
        vacancies = [
            Vacancy(vacancy_id="123", title="Java Developer", url="https://test.com", source="hh.ru"),
            Vacancy(vacancy_id="124", title="C++ Developer", url="https://test2.com", source="hh.ru"),
        ]

        result = self.search.search_with_and(vacancies, ["python", "django"])
        assert len(result) == 0


class TestSearchUtilsFunctions:
    """Тесты для функций поиска"""

    def test_normalize_query(self):
        """Тест нормализации запроса"""
        from src.utils.search_utils import normalize_query

        assert normalize_query("Python Django") == "python django"
        assert normalize_query("  PYTHON   DJANGO  ") == "python django"
        assert normalize_query("") == ""
        assert normalize_query(None) == ""

    def test_extract_keywords(self):
        """Тест извлечения ключевых слов"""
        from src.utils.search_utils import extract_keywords

        keywords = extract_keywords("Python Django Flask")
        assert "python" in keywords
        assert "django" in keywords
        assert "flask" in keywords

    def test_build_search_params(self):
        """Тест построения параметров поиска"""
        from src.utils.search_utils import build_search_params

        params = build_search_params("python", per_page=50, page=0)
        assert params["text"] == "python"
        assert params["per_page"] == 50
        assert params["page"] == 0

    def test_validate_search_query(self):
        """Тест валидации поискового запроса"""
        from src.utils.search_utils import validate_search_query

        assert validate_search_query("python") is True
        assert validate_search_query("") is False
        assert validate_search_query(None) is False
        assert validate_search_query(123) is False

    def test_format_search_results(self):
        """Тест форматирования результатов поиска"""
        from src.utils.search_utils import format_search_results

        results = [
            {"id": "123", "name": "Python Developer", "alternate_url": "https://test.com"},
            {"vacancy_id": "124", "profession": "Java Developer", "link": "https://test2.com"},
        ]

        formatted = format_search_results(results)
        assert len(formatted) == 2
        assert formatted[0]["id"] == "123"
        assert formatted[0]["title"] == "Python Developer"

    def test_filter_vacancies_by_keyword(self):
        """Тест фильтрации вакансий по ключевому слову"""
        from src.utils.search_utils import filter_vacancies_by_keyword

        vacancies = [
            Vacancy(vacancy_id="123", title="Python Developer", url="https://test.com", source="hh.ru"),
            Vacancy(vacancy_id="124", title="Java Developer", url="https://test2.com", source="hh.ru"),
        ]

        filtered = filter_vacancies_by_keyword(vacancies, "python")
        assert len(filtered) == 1
        assert filtered[0].vacancy_id == "123"

    def test_vacancy_contains_keyword(self):
        """Тест проверки наличия ключевого слова в вакансии"""
        from src.utils.search_utils import vacancy_contains_keyword

        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com",
            source="hh.ru",
            description="Work with Python and Django",
        )

        assert vacancy_contains_keyword(vacancy, "python") is True
        assert vacancy_contains_keyword(vacancy, "django") is True
        assert vacancy_contains_keyword(vacancy, "java") is False
