
"""
Полные тесты для search_utils
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
    from src.vacancies.models import Vacancy
    SEARCH_UTILS_AVAILABLE = True
except ImportError:
    SEARCH_UTILS_AVAILABLE = False


@pytest.mark.skipif(not SEARCH_UTILS_AVAILABLE, reason="Search utils not available")
class TestSearchUtilsFunctions:
    """Тесты для функций поиска"""
    
    def test_normalize_query_basic(self):
        """Тест базовой нормализации запроса"""
        result = normalize_query("Python Developer")
        assert result == "python developer"
    
    def test_normalize_query_with_extra_spaces(self):
        """Тест нормализации с лишними пробелами"""
        result = normalize_query("  Python    Developer  ")
        assert result == "python developer"
    
    def test_normalize_query_empty(self):
        """Тест нормализации пустого запроса"""
        assert normalize_query("") == ""
        assert normalize_query(None) == ""
        assert normalize_query("   ") == ""
    
    def test_normalize_query_long(self):
        """Тест нормализации длинного запроса"""
        long_query = "python " * 100  # 700 символов
        result = normalize_query(long_query)
        assert len(result) == 500
    
    def test_extract_keywords_basic(self):
        """Тест базового извлечения ключевых слов"""
        keywords = extract_keywords("Python Django PostgreSQL")
        assert "python" in keywords
        assert "django" in keywords
        assert "postgresql" in keywords
    
    def test_extract_keywords_with_operators(self):
        """Тест извлечения ключевых слов с операторами"""
        keywords = extract_keywords("Python AND Django OR FastAPI")
        assert "python" in keywords
        assert "django" in keywords
        assert "fastapi" in keywords
        assert "and" not in keywords
        assert "or" not in keywords
    
    def test_extract_keywords_with_punctuation(self):
        """Тест извлечения ключевых слов с пунктуацией"""
        keywords = extract_keywords("Python, Django; PostgreSQL!")
        assert "python" in keywords
        assert "django" in keywords
        assert "postgresql" in keywords
    
    def test_extract_keywords_filter_short_words(self):
        """Тест фильтрации коротких слов"""
        keywords = extract_keywords("Python и на с для от до работа вакансия")
        assert "python" in keywords
        # Стоп-слова и короткие слова должны быть отфильтрованы
        stop_words = {"и", "на", "с", "для", "от", "до", "работа", "вакансия"}
        for word in stop_words:
            assert word not in keywords
    
    def test_extract_keywords_empty(self):
        """Тест извлечения ключевых слов из пустого запроса"""
        assert extract_keywords("") == []
        assert extract_keywords(None) == []
    
    def test_build_search_params_basic(self):
        """Тест построения базовых параметров поиска"""
        params = build_search_params("python", per_page=20, page=1)
        expected = {"text": "python", "per_page": 20, "page": 1}
        assert params == expected
    
    def test_build_search_params_with_salary(self):
        """Тест построения параметров с зарплатой"""
        params = build_search_params("python", salary_from=50000, salary_to=100000)
        assert params["salary"] == 50000
        assert params["salary_to"] == 100000
    
    def test_build_search_params_with_area(self):
        """Тест построения параметров с регионом"""
        params = build_search_params("python", area="Moscow")
        assert params["area"] == "Moscow"
    
    def test_build_search_params_limit_per_page(self):
        """Тест ограничения количества элементов на странице"""
        params = build_search_params("python", per_page=150)  # Больше лимита
        assert params["per_page"] == 100  # Должно быть ограничено
    
    def test_validate_search_query_valid(self):
        """Тест валидации корректного запроса"""
        assert validate_search_query("python") is True
        assert validate_search_query("Python Developer") is True
        assert validate_search_query("   python   ") is True
    
    def test_validate_search_query_invalid(self):
        """Тест валидации некорректного запроса"""
        assert validate_search_query("") is False
        assert validate_search_query(None) is False
        assert validate_search_query("   ") is False
        assert validate_search_query(123) is False
        assert validate_search_query([]) is False
    
    def test_format_search_results_basic(self):
        """Тест форматирования результатов поиска"""
        results = [
            {
                "id": "1",
                "name": "Python Developer",
                "alternate_url": "https://hh.ru/vacancy/1"
            },
            {
                "vacancy_id": "2", 
                "profession": "Java Developer",
                "link": "https://superjob.ru/vacancy/2"
            }
        ]
        
        formatted = format_search_results(results)
        assert len(formatted) == 2
        
        # Проверяем первый результат (HH формат)
        assert formatted[0]["id"] == "1"
        assert formatted[0]["title"] == "Python Developer"
        assert formatted[0]["url"] == "https://hh.ru/vacancy/1"
        
        # Проверяем второй результат (SJ формат)
        assert formatted[1]["id"] == "2"
        assert formatted[1]["title"] == "Java Developer"
        assert formatted[1]["url"] == "https://superjob.ru/vacancy/2"
    
    def test_format_search_results_empty(self):
        """Тест форматирования пустых результатов"""
        assert format_search_results([]) == []
        assert format_search_results(None) == []
    
    def test_format_search_results_invalid_items(self):
        """Тест форматирования с невалидными элементами"""
        results = [
            {"id": "1", "name": "Valid Job"},
            "invalid_item",
            None,
            {"incomplete": "data"}
        ]
        
        formatted = format_search_results(results)
        # Должен обработать только валидные элементы
        assert len(formatted) >= 1


@pytest.mark.skipif(not SEARCH_UTILS_AVAILABLE, reason="Search utils not available")
class TestVacancyFiltering:
    """Тесты фильтрации вакансий"""
    
    @pytest.fixture
    def sample_vacancies(self):
        """Создание образцов вакансий для тестирования"""
        vacancies = []
        
        # Мокаем вакансии с различными атрибутами
        vacancy1 = Mock(spec=Vacancy)
        vacancy1.vacancy_id = "hh_001"
        vacancy1.title = "Senior Python Developer"
        vacancy1.requirements = "Python, Django, PostgreSQL"
        vacancy1.responsibilities = "Разработка веб-приложений"
        vacancy1.description = "Ищем опытного Python разработчика"
        vacancy1.detailed_description = "Работа с микросервисами на Python"
        vacancy1.skills = [{"name": "Python"}, {"name": "Django"}]
        vacancy1.employer = {"name": "Яндекс"}
        vacancy1.employment = "Полная занятость"
        vacancy1.schedule = "Полный день"
        vacancy1.experience = "От 3 до 6 лет"
        vacancy1.benefits = "ДМС, спорт"
        
        vacancy2 = Mock(spec=Vacancy)
        vacancy2.vacancy_id = "hh_002"
        vacancy2.title = "Java Backend Developer"
        vacancy2.requirements = "Java, Spring, MySQL"
        vacancy2.responsibilities = "Backend разработка"
        vacancy2.description = "Java разработчик в команду"
        vacancy2.detailed_description = "Разработка REST API на Java"
        vacancy2.skills = [{"name": "Java"}, {"name": "Spring"}]
        vacancy2.employer = {"name": "Mail.Ru"}
        vacancy2.employment = "Удаленная работа"
        vacancy2.schedule = "Гибкий график"
        vacancy2.experience = "От 1 до 3 лет"
        vacancy2.benefits = "Обучение"
        
        vacancy3 = Mock(spec=Vacancy)
        vacancy3.vacancy_id = "sj_001"
        vacancy3.title = "Frontend Python Developer"  # Содержит и Python и Frontend
        vacancy3.requirements = "React, JavaScript"
        vacancy3.responsibilities = "Разработка интерфейсов"
        vacancy3.description = "Frontend разработчик"
        vacancy3.detailed_description = "Создание пользовательских интерфейсов с элементами Python"
        vacancy3.skills = ["React", "JavaScript"]
        vacancy3.employer = {"name": "Тинькофф"}
        vacancy3.employment = "Частичная занятость"
        vacancy3.schedule = "Удаленная работа"
        vacancy3.experience = "Без опыта"
        vacancy3.benefits = "Гибкий график"
        
        return [vacancy1, vacancy2, vacancy3]
    
    def test_filter_vacancies_by_keyword_title(self, sample_vacancies):
        """Тест фильтрации по ключевому слову в заголовке"""
        result = filter_vacancies_by_keyword(sample_vacancies, "Python")
        # Должно найти 2 вакансии (Senior Python Developer и Frontend Python Developer)
        assert len(result) == 2
        assert result[0].title == "Senior Python Developer"  # Более релевантная должна быть первой
    
    def test_filter_vacancies_by_keyword_description(self, sample_vacancies):
        """Тест фильтрации по ключевому слову в описании"""
        result = filter_vacancies_by_keyword(sample_vacancies, "API")
        # Должно найти 1 вакансию (Java Backend с REST API)
        assert len(result) == 1
        assert result[0].title == "Java Backend Developer"
    
    def test_filter_vacancies_by_keyword_skills(self, sample_vacancies):
        """Тест фильтрации по навыкам"""
        result = filter_vacancies_by_keyword(sample_vacancies, "Django")
        # Должно найти 1 вакансию (Senior Python с Django)
        assert len(result) == 1
        assert result[0].title == "Senior Python Developer"
    
    def test_filter_vacancies_by_keyword_no_match(self, sample_vacancies):
        """Тест фильтрации когда нет совпадений"""
        result = filter_vacancies_by_keyword(sample_vacancies, "PHP")
        assert len(result) == 0
    
    def test_filter_vacancies_by_keyword_empty_list(self):
        """Тест фильтрации пустого списка"""
        result = filter_vacancies_by_keyword([], "Python")
        assert len(result) == 0
    
    def test_filter_vacancies_by_keyword_case_insensitive(self, sample_vacancies):
        """Тест регистронезависимой фильтрации"""
        result1 = filter_vacancies_by_keyword(sample_vacancies, "python")
        result2 = filter_vacancies_by_keyword(sample_vacancies, "PYTHON")
        assert len(result1) == len(result2) == 2
    
    def test_vacancy_contains_keyword_title(self, sample_vacancies):
        """Тест проверки наличия ключевого слова в заголовке"""
        assert vacancy_contains_keyword(sample_vacancies[0], "Python") is True
        assert vacancy_contains_keyword(sample_vacancies[0], "Java") is False
    
    def test_vacancy_contains_keyword_description(self, sample_vacancies):
        """Тест проверки наличия ключевого слова в описании"""
        assert vacancy_contains_keyword(sample_vacancies[1], "REST") is True
        assert vacancy_contains_keyword(sample_vacancies[1], "GraphQL") is False
    
    def test_vacancy_contains_keyword_case_insensitive(self, sample_vacancies):
        """Тест регистронезависимой проверки ключевого слова"""
        assert vacancy_contains_keyword(sample_vacancies[0], "python") is True
        assert vacancy_contains_keyword(sample_vacancies[0], "DJANGO") is True


@pytest.mark.skipif(not SEARCH_UTILS_AVAILABLE, reason="Search utils not available")
class TestSearchQueryParser:
    """Тесты парсера поисковых запросов"""
    
    @pytest.fixture
    def parser(self):
        """Экземпляр парсера"""
        return SearchQueryParser()
    
    def test_parser_init(self, parser):
        """Тест инициализации парсера"""
        assert parser is not None
    
    def test_parse_simple_query(self, parser):
        """Тест парсинга простого запроса"""
        result = parser.parse("Python")
        expected = {"keywords": ["Python"], "operator": "OR"}
        assert result == expected
    
    def test_parse_and_query(self, parser):
        """Тест парсинга запроса с AND"""
        result = parser.parse("Python AND Django")
        expected = {"keywords": ["Python", "Django"], "operator": "AND"}
        assert result == expected
    
    def test_parse_or_query(self, parser):
        """Тест парсинга запроса с OR"""
        result = parser.parse("Python OR Java")
        expected = {"keywords": ["Python", "Java"], "operator": "OR"}
        assert result == expected
    
    def test_parse_comma_query(self, parser):
        """Тест парсинга запроса с запятыми"""
        result = parser.parse("Python, Java, JavaScript")
        expected = {"keywords": ["Python", "Java", "JavaScript"], "operator": "OR"}
        assert result == expected
    
    def test_parse_empty_query(self, parser):
        """Тест парсинга пустого запроса"""
        assert parser.parse("") is None
        assert parser.parse("   ") is None
        assert parser.parse(None) is None


@pytest.mark.skipif(not SEARCH_UTILS_AVAILABLE, reason="Search utils not available")
class TestAdvancedSearch:
    """Тесты продвинутого поиска"""
    
    @pytest.fixture
    def advanced_search(self):
        """Экземпляр продвинутого поиска"""
        return AdvancedSearch()
    
    @pytest.fixture
    def sample_vacancies_with_search_query(self):
        """Образцы вакансий с полем search_query"""
        vacancies = []
        
        vacancy1 = Mock()
        vacancy1.title = "Python Developer"
        vacancy1.description = "Разработка на Python"
        vacancy1.search_query = "python django postgresql"  # Добавляем поле для поиска
        
        vacancy2 = Mock()
        vacancy2.title = "Java Developer"
        vacancy2.description = "Backend разработка"
        vacancy2.search_query = "java spring mysql"
        
        vacancy3 = Mock()
        vacancy3.title = "Full Stack Developer"
        vacancy3.description = "Разработка фронтенда и бэкенда"
        vacancy3.search_query = "javascript react node python"
        
        return [vacancy1, vacancy2, vacancy3]
    
    def test_advanced_search_init(self, advanced_search):
        """Тест инициализации продвинутого поиска"""
        assert advanced_search is not None
    
    def test_search_with_and(self, advanced_search, sample_vacancies_with_search_query):
        """Тест поиска с оператором AND"""
        keywords = ["Python", "Django"]
        result = advanced_search.search_with_and(sample_vacancies_with_search_query, keywords)
        # Только первая вакансия содержит оба ключевых слова
        assert len(result) == 1
        assert result[0].title == "Python Developer"
    
    def test_search_with_or(self, advanced_search, sample_vacancies_with_search_query):
        """Тест поиска с оператором OR"""
        keywords = ["Python", "Java"]
        result = advanced_search.search_with_or(sample_vacancies_with_search_query, keywords)
        # Должно найти 3 вакансии (Python Developer, Java Developer, Full Stack с Python)
        assert len(result) == 3
    
    def test_search_with_search_query_field(self, advanced_search, sample_vacancies_with_search_query):
        """Тест поиска с использованием поля search_query"""
        keywords = ["PostgreSQL"]
        result = advanced_search.search_with_and(sample_vacancies_with_search_query, keywords)
        # Должно найти 1 вакансию (в search_query есть postgresql)
        assert len(result) == 1
        assert result[0].title == "Python Developer"
    
    def test_search_without_search_query_field(self, advanced_search):
        """Тест поиска с вакансиями без поля search_query"""
        vacancy = Mock()
        vacancy.title = "Test Job"
        vacancy.description = "Test description"
        # Нет атрибута search_query
        
        keywords = ["Test"]
        result = advanced_search.search_with_or([vacancy], keywords)
        assert len(result) == 1
    
    def test_search_empty_vacancies(self, advanced_search):
        """Тест поиска в пустом списке вакансий"""
        result = advanced_search.search_with_and([], ["Python"])
        assert result == []
        
        result2 = advanced_search.search_with_or([], ["Python"])
        assert result2 == []


@pytest.mark.skipif(not SEARCH_UTILS_AVAILABLE, reason="Search utils not available")
class TestSearchUtilsIntegration:
    """Интеграционные тесты для поисковых утилит"""
    
    def test_full_search_pipeline(self):
        """Тест полного пайплайна поиска"""
        # Нормализация запроса
        raw_query = "  Python AND Django  "
        normalized = normalize_query(raw_query)
        assert normalized == "python and django"
        
        # Извлечение ключевых слов
        keywords = extract_keywords(normalized)
        assert "python" in keywords
        assert "django" in keywords
        
        # Построение параметров поиска
        params = build_search_params("python django", per_page=25)
        assert params["text"] == "python django"
        assert params["per_page"] == 25
        
        # Валидация запроса
        assert validate_search_query("python django") is True
    
    def test_search_with_parser_and_advanced_search(self):
        """Тест интеграции парсера и продвинутого поиска"""
        parser = SearchQueryParser()
        advanced_search = AdvancedSearch()
        
        # Создаем тестовые вакансии
        vacancy1 = Mock()
        vacancy1.title = "Python Django Developer"
        vacancy1.description = "Backend development"
        
        vacancy2 = Mock()
        vacancy2.title = "Python Flask Developer" 
        vacancy2.description = "API development"
        
        vacancies = [vacancy1, vacancy2]
        
        # Парсим запрос
        parsed = parser.parse("Python AND Django")
        assert parsed["operator"] == "AND"
        
        # Выполняем поиск
        if parsed["operator"] == "AND":
            result = advanced_search.search_with_and(vacancies, parsed["keywords"])
        else:
            result = advanced_search.search_with_or(vacancies, parsed["keywords"])
        
        # Должно найти только Django вакансию
        assert len(result) == 1
        assert "Django" in result[0].title
    
    def test_error_handling_in_search_functions(self):
        """Тест обработки ошибок в поисковых функциях"""
        # Функции должны корректно обрабатывать некорректные данные
        assert normalize_query(None) == ""
        assert extract_keywords(None) == []
        assert validate_search_query(None) is False
        assert format_search_results(None) == []
        
        # С пустыми или некорректными вакансиями
        assert filter_vacancies_by_keyword(None, "test") == []
        assert filter_vacancies_by_keyword([], "test") == []
