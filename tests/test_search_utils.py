
"""
Тесты для модуля search_utils
"""

import pytest
from src.utils.search_utils import SearchUtils


class TestSearchUtils:
    """Тесты для класса SearchUtils"""

    @pytest.fixture
    def search_utils(self):
        """Фикстура SearchUtils"""
        return SearchUtils()

    def test_normalize_query(self, search_utils):
        """Тест нормализации поискового запроса"""
        assert search_utils.normalize_query("  Python Developer  ") == "python developer"
        assert search_utils.normalize_query("Java-Script") == "java-script"
        assert search_utils.normalize_query("") == ""

    def test_extract_keywords(self, search_utils):
        """Тест извлечения ключевых слов"""
        keywords = search_utils.extract_keywords("Python Django Developer")
        assert "python" in keywords
        assert "django" in keywords
        assert "developer" in keywords
        assert len(keywords) == 3

    def test_extract_keywords_with_stopwords(self, search_utils):
        """Тест извлечения ключевых слов со стоп-словами"""
        keywords = search_utils.extract_keywords("Python and Django or Flask")
        assert "python" in keywords
        assert "django" in keywords
        assert "flask" in keywords
        # Стоп-слова должны быть исключены
        assert "and" not in keywords
        assert "or" not in keywords

    def test_build_search_pattern(self, search_utils):
        """Тест построения паттерна поиска"""
        pattern = search_utils.build_search_pattern("Python Developer")
        assert pattern is not None
        # Проверяем, что паттерн может найти совпадения
        import re
        assert re.search(pattern, "Python Developer", re.IGNORECASE)
        assert re.search(pattern, "Senior Python Developer", re.IGNORECASE)

    def test_calculate_relevance_score(self, search_utils):
        """Тест расчета релевантности"""
        text = "Python Developer with Django experience"
        keywords = ["python", "developer", "django"]
        
        score = search_utils.calculate_relevance_score(text, keywords)
        assert score > 0
        assert isinstance(score, (int, float))

    def test_calculate_relevance_score_no_matches(self, search_utils):
        """Тест расчета релевантности без совпадений"""
        text = "Java Spring Boot Developer"
        keywords = ["python", "django"]
        
        score = search_utils.calculate_relevance_score(text, keywords)
        assert score == 0

    def test_advanced_search_and_operator(self, search_utils):
        """Тест расширенного поиска с оператором AND"""
        text = "Senior Python Developer with Django"
        query = "Python AND Django"
        
        assert search_utils.matches_advanced_query(text, query) is True
        
        text2 = "Java Developer"
        assert search_utils.matches_advanced_query(text2, query) is False

    def test_advanced_search_or_operator(self, search_utils):
        """Тест расширенного поиска с оператором OR"""
        text1 = "Python Developer"
        text2 = "Java Developer"
        query = "Python OR Java"
        
        assert search_utils.matches_advanced_query(text1, query) is True
        assert search_utils.matches_advanced_query(text2, query) is True
        
        text3 = "C++ Developer"
        assert search_utils.matches_advanced_query(text3, query) is False

    def test_advanced_search_not_operator(self, search_utils):
        """Тест расширенного поиска с оператором NOT"""
        text1 = "Senior Python Developer"
        text2 = "Junior Python Developer"
        query = "Python NOT Junior"
        
        assert search_utils.matches_advanced_query(text1, query) is True
        assert search_utils.matches_advanced_query(text2, query) is False

    def test_fuzzy_match(self, search_utils):
        """Тест нечеткого поиска"""
        assert search_utils.fuzzy_match("Python", "Python") == 1.0
        assert search_utils.fuzzy_match("Python", "Pyton") > 0.8
        assert search_utils.fuzzy_match("Python", "Java") < 0.5

    def test_highlight_matches(self, search_utils):
        """Тест выделения совпадений"""
        text = "Python Developer with Django experience"
        keywords = ["python", "django"]
        
        highlighted = search_utils.highlight_matches(text, keywords)
        assert highlighted != text
        # Проверяем наличие маркеров выделения
        assert "**" in highlighted or "[" in highlighted
