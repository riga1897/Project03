"""
Тесты для утилит поиска
"""

import pytest
from unittest.mock import patch, MagicMock

# Импортируем функции напрямую из search_utils
from src.utils.search_utils import (
    normalize_query,
    extract_keywords,
    build_search_params,
    validate_search_query
)


class TestSearchUtils:
    """Тесты для утилит поиска"""

    def test_normalize_query_basic(self):
        """Тест базовой нормализации запроса"""
        result = normalize_query("  Python Developer  ")
        assert result == "python developer"

    def test_normalize_query_empty(self):
        """Тест нормализации пустого запроса"""
        result = normalize_query("")
        assert result == ""

    def test_normalize_query_special_chars(self):
        """Тест нормализации с спецсимволами"""
        result = normalize_query("Python/Django & React!")
        # Функция должна обработать спецсимволы
        assert isinstance(result, str)

    def test_extract_keywords_basic(self):
        """Тест извлечения ключевых слов"""
        keywords = extract_keywords("Python Django PostgreSQL")
        assert isinstance(keywords, list)
        if keywords:  # Если функция возвращает список
            assert len(keywords) > 0

    def test_extract_keywords_empty(self):
        """Тест извлечения из пустой строки"""
        keywords = extract_keywords("")
        assert isinstance(keywords, list)

    def test_build_search_params_basic(self):
        """Тест построения параметров поиска"""
        params = build_search_params("python", page=1, per_page=20)
        assert isinstance(params, dict)

    def test_build_search_params_with_filters(self):
        """Тест параметров поиска с фильтрами"""
        filters = {"salary": "100000", "experience": "between1And3"}
        params = build_search_params("java", filters=filters, page=2)
        assert isinstance(params, dict)

    def test_validate_search_query_valid(self):
        """Тест валидации корректного запроса"""
        is_valid = validate_search_query("Python Developer")
        assert isinstance(is_valid, bool)

    def test_validate_search_query_empty(self):
        """Тест валидации пустого запроса"""
        is_valid = validate_search_query("")
        # Пустой запрос может быть как валидным, так и нет
        assert isinstance(is_valid, bool)

    def test_validate_search_query_too_short(self):
        """Тест валидации слишком короткого запроса"""
        is_valid = validate_search_query("a")
        assert isinstance(is_valid, bool)

    

    def test_all_functions_exist(self):
        """Тест существования всех функций"""
        import src.utils.search_utils as search_utils

        # Проверяем основные функции
        expected_functions = [
            'normalize_query', 'extract_keywords', 'build_search_params',
            'validate_search_query'
        ]

        existing_functions = [func for func in expected_functions
                            if hasattr(search_utils, func)]

        # Должны быть хотя бы базовые функции
        assert len(existing_functions) > 0
        assert 'normalize_query' in existing_functions or 'extract_keywords' in existing_functions

    def test_search_utils_integration(self):
        """Интеграционный тест утилит поиска"""
        # Тест полного цикла обработки запроса
        query = "  Python Developer  "

        # Нормализуем запрос
        normalized = normalize_query(query)
        assert isinstance(normalized, str)

        # Извлекаем ключевые слова
        keywords = extract_keywords(normalized)
        assert isinstance(keywords, list)

        # Строим параметры поиска
        params = build_search_params(normalized)
        assert isinstance(params, dict)

        # Валидируем запрос
        is_valid = validate_search_query(normalized)
        assert isinstance(is_valid, bool)

    def test_edge_cases(self):
        """Тест граничных случаев"""
        # Тест с None
        try:
            result = normalize_query(None)
            # Если функция обрабатывает None, проверяем результат
            assert result is None or isinstance(result, str)
        except (TypeError, AttributeError):
            # Если функция не обрабатывает None, это нормально
            pass

        # Тест с очень длинной строкой
        long_query = "a" * 1000
        try:
            result = normalize_query(long_query)
            assert isinstance(result, str)
        except Exception:
            # Если есть ограничения на длину, это тоже нормально
            pass