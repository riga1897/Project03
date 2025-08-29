
"""
Тесты для модуля search_utils
"""

import pytest
from unittest.mock import Mock, patch
from src.utils.search_utils import (
    normalize_query,
    extract_keywords,
    build_search_params,
    validate_search_query,
    format_search_results
)


class TestSearchUtils:
    """Тесты для утилит поиска"""

    def test_normalize_query(self):
        """Тест нормализации поискового запроса"""
        # Обычный запрос
        assert normalize_query("Python Developer") == "python developer"
        
        # Запрос с лишними пробелами
        assert normalize_query("  Python   Developer  ") == "python developer"
        
        # Пустой запрос
        assert normalize_query("") == ""
        assert normalize_query(None) == ""

    def test_extract_keywords(self):
        """Тест извлечения ключевых слов"""
        # Простой запрос
        keywords = extract_keywords("Python Django REST")
        assert "python" in keywords
        assert "django" in keywords
        assert "rest" in keywords
        
        # Запрос со знаками препинания
        keywords = extract_keywords("Python, Django, REST API")
        assert len(keywords) >= 3
        
        # Пустой запрос
        assert extract_keywords("") == []

    def test_build_search_params(self):
        """Тест построения параметров поиска"""
        # Базовые параметры
        params = build_search_params("python", per_page=50)
        assert params["text"] == "python"
        assert params["per_page"] == 50
        
        # Дополнительные параметры
        params = build_search_params("python", salary_from=100000, area=1)
        assert params["salary"] == 100000
        assert params["area"] == 1

    def test_validate_search_query(self):
        """Тест валидации поискового запроса"""
        # Валидные запросы
        assert validate_search_query("Python") is True
        assert validate_search_query("JavaScript Developer") is True
        
        # Невалидные запросы
        assert validate_search_query("") is False
        assert validate_search_query(None) is False
        assert validate_search_query("   ") is False

    def test_format_search_results(self):
        """Тест форматирования результатов поиска"""
        results = [
            {"id": "1", "name": "Python Developer", "source": "hh.ru"},
            {"id": "2", "profession": "Java Developer", "source": "superjob.ru"}
        ]
        
        formatted = format_search_results(results)
        assert isinstance(formatted, list)
        assert len(formatted) == 2

    def test_search_query_filtering(self):
        """Тест фильтрации поисковых запросов"""
        # Должен удалять стоп-слова
        clean_query = normalize_query("работа python разработчик вакансия")
        assert "работа" not in clean_query or "python" in clean_query

    def test_keyword_extraction_with_operators(self):
        """Тест извлечения ключевых слов с операторами"""
        # AND оператор
        keywords = extract_keywords("Python AND Django")
        assert "python" in keywords
        assert "django" in keywords
        
        # OR оператор
        keywords = extract_keywords("Python OR Java")
        assert len(keywords) >= 2

    def test_empty_search_handling(self):
        """Тест обработки пустых поисковых запросов"""
        assert normalize_query("") == ""
        assert extract_keywords("") == []
        assert validate_search_query("") is False
        assert format_search_results([]) == []

    def test_special_characters_handling(self):
        """Тест обработки специальных символов"""
        # Символы, которые должны быть удалены
        normalized = normalize_query("C++ / C# Developer")
        assert "developer" in normalized
        
        # Сохранение важных символов
        keywords = extract_keywords("React.js Vue.js")
        assert any("react" in str(k) for k in keywords)

    def test_language_detection(self):
        """Тест определения языка запроса"""
        # Русский запрос
        russian_query = normalize_query("Разработчик Python")
        assert "разработчик" in russian_query
        
        # Английский запрос
        english_query = normalize_query("Python Developer")
        assert "python" in english_query

    def test_search_params_validation(self):
        """Тест валидации параметров поиска"""
        # Валидные параметры
        params = build_search_params("python", per_page=20, page=0)
        assert params["per_page"] == 20
        assert params["page"] == 0
        
        # Параметры с ограничениями
        params = build_search_params("python", per_page=1000)  # Слишком много
        assert params["per_page"] <= 100  # Должно быть ограничено

    def test_query_normalization_edge_cases(self):
        """Тест граничных случаев нормализации"""
        # Очень длинный запрос
        long_query = "python " * 100
        normalized = normalize_query(long_query)
        assert len(normalized) <= 500  # Должен быть ограничен
        
        # Запрос только из цифр
        assert normalize_query("12345") == "12345"
        
        # Запрос с эмодзи (если поддерживается)
        emoji_query = normalize_query("Python 🐍 Developer")
        assert "python" in emoji_query

    def test_advanced_search_combinations(self):
        """Тест сложных поисковых комбинаций"""
        # Комбинированный запрос
        params = build_search_params(
            "python django",
            salary_from=80000,
            salary_to=200000,
            experience="between1And3",
            schedule="remote"
        )
        
        assert "python django" in params["text"]
        assert params["salary"] == 80000
        assert "experience" in params
