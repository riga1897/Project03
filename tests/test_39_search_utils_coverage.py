#!/usr/bin/env python3
"""
Тесты модуля search_utils.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций 
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Тестирование всех функций и классов

Модуль содержит:
- 6 утилитных функций поиска
- 2 класса для парсинга запросов и продвинутого поиска
- Функции нормализации, валидации и фильтрации
"""

import pytest
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

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


class TestNormalizeQuery:
    """100% покрытие функции normalize_query"""

    def test_normalize_query_with_none(self):
        """Покрытие: None input"""
        result = normalize_query(None)  # type: ignore
        assert result == ""

    def test_normalize_query_with_empty_string(self):
        """Покрытие: пустая строка"""
        result = normalize_query("")
        assert result == ""

    def test_normalize_query_with_whitespace_string(self):
        """Покрытие: строка из пробелов"""
        result = normalize_query("   ")
        assert result == ""

    def test_normalize_query_with_simple_string(self):
        """Покрытие: простая строка"""
        result = normalize_query("Python")
        assert result == "python"

    def test_normalize_query_with_mixed_case(self):
        """Покрытие: смешанный регистр"""
        result = normalize_query("Python Developer")
        assert result == "python developer"

    def test_normalize_query_with_multiple_spaces(self):
        """Покрытие: множественные пробелы"""
        result = normalize_query("Python    Django    Developer")
        assert result == "python django developer"

    def test_normalize_query_with_leading_trailing_spaces(self):
        """Покрытие: пробелы в начале и конце"""
        result = normalize_query("  Python Developer  ")
        assert result == "python developer"

    def test_normalize_query_with_tabs_and_newlines(self):
        """Покрытие: табы и переносы строк"""
        result = normalize_query("Python\tDjango\nDeveloper")
        assert result == "python django developer"

    def test_normalize_query_with_long_string(self):
        """Покрытие: ограничение длины строки (500 символов)"""
        long_query = "Python " * 100  # Создаем строку длиннее 500 символов
        result = normalize_query(long_query)
        assert len(result) == 500
        assert result.startswith("python python")

    def test_normalize_query_with_exactly_500_chars(self):
        """Покрытие: строка ровно 500 символов"""
        query_500 = "a" * 500
        result = normalize_query(query_500)
        assert len(result) == 500
        assert result == "a" * 500

    def test_normalize_query_with_non_string_input(self):
        """Покрытие: не-строковый input -> str()"""
        result = normalize_query(12345)  # type: ignore
        assert result == "12345"

    def test_normalize_query_with_boolean_input(self):
        """Покрытие: boolean input"""
        result = normalize_query(True)  # type: ignore
        assert result == "true"

    def test_normalize_query_complex_cleanup(self):
        """Покрытие: сложная очистка с разными пробелами"""
        result = normalize_query("  Python   \t  Django\n  FastAPI  ")
        assert result == "python django fastapi"


class TestExtractKeywords:
    """100% покрытие функции extract_keywords"""

    def test_extract_keywords_with_none(self):
        """Покрытие: None input"""
        result = extract_keywords(None)  # type: ignore
        assert result == []

    def test_extract_keywords_with_empty_string(self):
        """Покрытие: пустая строка"""
        result = extract_keywords("")
        assert result == []

    def test_extract_keywords_with_simple_words(self):
        """Покрытие: простые слова"""
        result = extract_keywords("Python Django")
        assert result == ["python", "django"]

    def test_extract_keywords_with_stop_words(self):
        """Покрытие: фильтрация стоп-слов"""
        result = extract_keywords("Python и Django для веб разработки")
        assert result == ["python", "django", "веб", "разработки"]

    def test_extract_keywords_with_short_words(self):
        """Покрытие: фильтрация коротких слов"""
        result = extract_keywords("Python и в на с")
        assert result == ["python"]

    def test_extract_keywords_with_operators(self):
        """Покрытие: удаление операторов AND/OR"""
        result = extract_keywords("Python AND Django OR FastAPI")
        assert result == ["python", "django", "fastapi"]

    def test_extract_keywords_with_punctuation(self):
        """Покрытие: удаление знаков препинания"""
        result = extract_keywords("Python, Django! FastAPI?")
        assert result == ["python", "django", "fastapi"]

    def test_extract_keywords_with_special_characters(self):
        """Покрытие: сохранение специальных символов в IT (. + #)"""
        result = extract_keywords("Python3.8 C++ C#")
        assert result == ["python3.8", "c++", "c#"]

    def test_extract_keywords_mixed_case_operators(self):
        """Покрытие: операторы в разном регистре"""
        result = extract_keywords("Python and Django or FastAPI")
        assert result == ["python", "django", "fastapi"]

    def test_extract_keywords_with_all_stop_words(self):
        """Покрытие: только стоп-слова"""
        result = extract_keywords("и в на с по для от до работа вакансия")
        assert result == []

    def test_extract_keywords_with_numbers_and_letters(self):
        """Покрытие: смешанные символы и числа"""
        result = extract_keywords("Python3 Django2.0 Vue.js")
        assert result == ["python3", "django2.0", "vue.js"]


class TestBuildSearchParams:
    """100% покрытие функции build_search_params"""

    def test_build_search_params_basic(self):
        """Покрытие: базовые параметры"""
        result = build_search_params("Python")
        expected = {"text": "Python", "per_page": 50, "page": 0}
        assert result == expected

    def test_build_search_params_with_per_page_and_page(self):
        """Покрытие: кастомные per_page и page"""
        result = build_search_params("Django", per_page=25, page=2)
        expected = {"text": "Django", "per_page": 25, "page": 2}
        assert result == expected

    def test_build_search_params_with_per_page_limit(self):
        """Покрытие: ограничение per_page до 100"""
        result = build_search_params("FastAPI", per_page=150)
        expected = {"text": "FastAPI", "per_page": 100, "page": 0}
        assert result == expected

    def test_build_search_params_with_salary_from(self):
        """Покрытие: добавление salary_from"""
        result = build_search_params("Python", salary_from=100000)
        expected = {"text": "Python", "per_page": 50, "page": 0, "salary": 100000}
        assert result == expected

    def test_build_search_params_with_salary_to(self):
        """Покрытие: добавление salary_to"""
        result = build_search_params("Python", salary_to=200000)
        expected = {"text": "Python", "per_page": 50, "page": 0, "salary_to": 200000}
        assert result == expected

    def test_build_search_params_with_area(self):
        """Покрытие: добавление area"""
        result = build_search_params("Python", area="1")
        expected = {"text": "Python", "per_page": 50, "page": 0, "area": "1"}
        assert result == expected

    def test_build_search_params_with_experience(self):
        """Покрытие: добавление experience"""
        result = build_search_params("Python", experience="between1And3")
        expected = {"text": "Python", "per_page": 50, "page": 0, "experience": "between1And3"}
        assert result == expected

    def test_build_search_params_with_schedule(self):
        """Покрытие: добавление schedule"""
        result = build_search_params("Python", schedule="remote")
        expected = {"text": "Python", "per_page": 50, "page": 0, "schedule": "remote"}
        assert result == expected

    def test_build_search_params_with_all_kwargs(self):
        """Покрытие: все дополнительные параметры"""
        result = build_search_params(
            "Python",
            per_page=30,
            page=1,
            salary_from=80000,
            salary_to=150000,
            area="2",
            experience="moreThan6",
            schedule="fullDay"
        )
        expected = {
            "text": "Python",
            "per_page": 30,
            "page": 1,
            "salary": 80000,
            "salary_to": 150000,
            "area": "2",
            "experience": "moreThan6",
            "schedule": "fullDay"
        }
        assert result == expected

    def test_build_search_params_with_unknown_kwargs(self):
        """Покрытие: неизвестные kwargs игнорируются"""
        result = build_search_params("Python", unknown_param="test", another_param=123)
        expected = {"text": "Python", "per_page": 50, "page": 0}
        assert result == expected


class TestValidateSearchQuery:
    """100% покрытие функции validate_search_query"""

    def test_validate_search_query_with_none(self):
        """Покрытие: None input"""
        result = validate_search_query(None)  # type: ignore
        assert result is False

    def test_validate_search_query_with_empty_string(self):
        """Покрытие: пустая строка"""
        result = validate_search_query("")
        assert result is False

    def test_validate_search_query_with_whitespace_only(self):
        """Покрытие: только пробелы"""
        result = validate_search_query("   ")
        assert result is False

    def test_validate_search_query_with_valid_string(self):
        """Покрытие: валидная строка"""
        result = validate_search_query("Python")
        assert result is True

    def test_validate_search_query_with_padded_string(self):
        """Покрытие: строка с пробелами по краям"""
        result = validate_search_query("  Python  ")
        assert result is True

    def test_validate_search_query_with_non_string(self):
        """Покрытие: не-строковый тип"""
        result = validate_search_query(123)  # type: ignore
        assert result is False

    def test_validate_search_query_with_boolean(self):
        """Покрытие: boolean тип"""
        result = validate_search_query(True)  # type: ignore
        assert result is False

    def test_validate_search_query_with_list(self):
        """Покрытие: список"""
        result = validate_search_query(["Python"])  # type: ignore
        assert result is False


class TestFormatSearchResults:
    """100% покрытие функции format_search_results"""

    def test_format_search_results_with_empty_list(self):
        """Покрытие: пустой список"""
        result = format_search_results([])
        assert result == []

    def test_format_search_results_with_none(self):
        """Покрытие: None input"""
        result = format_search_results(None)  # type: ignore
        assert result == []

    def test_format_search_results_with_hh_format(self):
        """Покрытие: формат HH.ru"""
        input_data = [
            {
                "id": "12345",
                "name": "Python Developer",
                "alternate_url": "https://hh.ru/vacancy/12345"
            }
        ]
        result = format_search_results(input_data)
        expected = [
            {
                "id": "12345",
                "title": "Python Developer", 
                "source": "unknown",
                "url": "https://hh.ru/vacancy/12345"
            }
        ]
        assert result == expected

    def test_format_search_results_with_sj_format(self):
        """Покрытие: формат SuperJob"""
        input_data = [
            {
                "vacancy_id": "67890",
                "profession": "Django Developer",
                "link": "https://superjob.ru/vacancy/67890"
            }
        ]
        result = format_search_results(input_data)
        expected = [
            {
                "id": "67890",
                "title": "Django Developer",
                "source": "unknown", 
                "url": "https://superjob.ru/vacancy/67890"
            }
        ]
        assert result == expected

    def test_format_search_results_with_mixed_formats(self):
        """Покрытие: смешанные форматы"""
        input_data = [
            {
                "id": "11111",
                "name": "Python Dev",
                "source": "hh",
                "alternate_url": "https://hh.ru/vacancy/11111"
            },
            {
                "vacancy_id": "22222", 
                "profession": "Django Dev",
                "source": "sj",
                "link": "https://superjob.ru/vacancy/22222"
            },
            {
                "title": "FastAPI Dev",
                "url": "https://example.com/vacancy"
            }
        ]
        result = format_search_results(input_data)
        expected = [
            {
                "id": "11111",
                "title": "Python Dev",
                "source": "hh",
                "url": "https://hh.ru/vacancy/11111"
            },
            {
                "id": "22222",
                "title": "Django Dev", 
                "source": "sj",
                "url": "https://superjob.ru/vacancy/22222"
            },
            {
                "id": "",
                "title": "FastAPI Dev",
                "source": "unknown",
                "url": "https://example.com/vacancy"
            }
        ]
        assert result == expected

    def test_format_search_results_with_missing_fields(self):
        """Покрытие: отсутствующие поля"""
        input_data = [
            {"id": "12345"},  # Только ID
            {"name": "Python Dev"},  # Только название
            {}  # Пустой объект
        ]
        result = format_search_results(input_data)
        expected = [
            {"id": "12345", "title": "", "source": "unknown", "url": ""},
            {"id": "", "title": "Python Dev", "source": "unknown", "url": ""},
            {"id": "", "title": "", "source": "unknown", "url": ""}
        ]
        assert result == expected

    def test_format_search_results_with_non_dict_items(self):
        """Покрытие: не-словарные элементы пропускаются"""
        input_data = [
            {"id": "12345", "name": "Python Dev"},
            "not a dict",
            123,
            None,
            {"id": "67890", "name": "Django Dev"}
        ]
        result = format_search_results(input_data)
        expected = [
            {"id": "12345", "title": "Python Dev", "source": "unknown", "url": ""},
            {"id": "67890", "title": "Django Dev", "source": "unknown", "url": ""}
        ]
        assert result == expected


class TestFilterVacanciesByKeyword:
    """100% покрытие функции filter_vacancies_by_keyword"""

    def test_filter_vacancies_by_keyword_basic(self):
        """Покрытие: базовая фильтрация"""
        # Мокируем объекты вакансий
        vacancy1 = MagicMock()
        vacancy1.id = "1"
        vacancy1.title = "Python Developer"
        vacancy1.requirements = "Django experience required"
        vacancy1.responsibilities = "Develop web applications"
        vacancy1.description = "Full stack development"
        vacancy1.skills = []
        vacancy1.employer = None
        vacancy1.employment = None
        vacancy1.schedule = None
        vacancy1.experience = None

        vacancy2 = MagicMock()
        vacancy2.id = "2"
        vacancy2.title = "Java Developer" 
        vacancy2.requirements = "Spring experience"
        vacancy2.responsibilities = "Backend development"
        vacancy2.description = "Enterprise applications"
        vacancy2.skills = []
        vacancy2.employer = None
        vacancy2.employment = None
        vacancy2.schedule = None
        vacancy2.experience = None

        vacancies = [vacancy1, vacancy2]
        
        result = filter_vacancies_by_keyword(vacancies, "Python")  # type: ignore
        assert len(result) == 1
        assert result[0] == vacancy1
        assert hasattr(result[0], "_relevance_score")
        assert result[0]._relevance_score == 10  # title match = 10 points

    def test_filter_vacancies_by_keyword_id_match(self):
        """Покрытие: поиск по ID (максимальный приоритет)"""
        vacancy = MagicMock()
        vacancy.id = "python_123"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None  
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "python")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 15  # ID match = 15 points

    def test_filter_vacancies_by_keyword_requirements_match(self):
        """Покрытие: поиск в requirements"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = "Python Django experience"
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Django")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 5  # requirements match = 5 points

    def test_filter_vacancies_by_keyword_responsibilities_match(self):
        """Покрытие: поиск в responsibilities"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = "Develop FastAPI applications"
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "FastAPI")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 5  # responsibilities match = 5 points

    def test_filter_vacancies_by_keyword_description_match(self):
        """Покрытие: поиск в description"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = "Work with React and Node.js"
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "React")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 3  # description match = 3 points

    def test_filter_vacancies_by_keyword_skills_dict_match(self):
        """Покрытие: поиск в skills (словарный формат)"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = [{"name": "Python"}, {"name": "Django"}]
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Python")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 6  # skills match = 6 points

    def test_filter_vacancies_by_keyword_skills_string_match(self):
        """Покрытие: поиск в skills (строковый формат)"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = ["Python", "Django", "FastAPI"]
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Django")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 6  # skills match = 6 points

    def test_filter_vacancies_by_keyword_employer_dict_match(self):
        """Покрытие: поиск в employer (словарный формат)"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = {"name": "Yandex"}
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Yandex")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 4  # employer match = 4 points

    def test_filter_vacancies_by_keyword_employer_object_match(self):
        """Покрытие: поиск в employer (объектный формат)"""
        employer_mock = MagicMock()
        employer_mock.name = "Google"

        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = employer_mock
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Google")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 4  # employer match = 4 points

    def test_filter_vacancies_by_keyword_employment_object_match(self):
        """Покрытие: поиск в employment (объектный формат)"""
        employment_mock = MagicMock()
        employment_mock.name = "Полная занятость"

        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = employment_mock
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Полная")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 3  # employment match = 3 points

    def test_filter_vacancies_by_keyword_employment_string_match(self):
        """Покрытие: поиск в employment (строковый формат)"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = "Удаленная работа"
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Удаленная")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 3  # employment match = 3 points

    def test_filter_vacancies_by_keyword_schedule_match(self):
        """Покрытие: поиск в schedule"""
        schedule_mock = MagicMock()
        schedule_mock.name = "Гибкий график"

        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = schedule_mock
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Гибкий")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 3  # schedule match = 3 points

    def test_filter_vacancies_by_keyword_experience_match(self):
        """Покрытие: поиск в experience"""
        experience_mock = MagicMock()
        experience_mock.name = "От 1 года до 3 лет"

        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = experience_mock

        result = filter_vacancies_by_keyword([vacancy], "года")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 3  # experience match = 3 points

    def test_filter_vacancies_by_keyword_benefits_match(self):
        """Покрытие: поиск в benefits (если поле существует)"""
        vacancy = MagicMock()
        vacancy.id = "1" 
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None
        vacancy.benefits = "ДМС, обучение"

        result = filter_vacancies_by_keyword([vacancy], "ДМС")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 2  # benefits match = 2 points

    def test_filter_vacancies_by_keyword_multiple_matches(self):
        """Покрытие: множественные совпадения суммируются"""
        vacancy = MagicMock()
        vacancy.id = "python_123"  # 15 points
        vacancy.title = "Python Developer"  # 10 points 
        vacancy.requirements = "Python experience"  # 5 points
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Python")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 30  # 15 + 10 + 5 = 30 points

    def test_filter_vacancies_by_keyword_no_matches(self):
        """Покрытие: нет совпадений"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Java Developer"
        vacancy.requirements = "Java experience"
        vacancy.responsibilities = "Backend development"
        vacancy.description = "Enterprise apps"
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Python")  # type: ignore
        assert len(result) == 0

    def test_filter_vacancies_by_keyword_sorting_by_relevance(self):
        """Покрытие: сортировка по релевантности"""
        # Vacancy с низким score
        vacancy1 = MagicMock()
        vacancy1.id = "1"
        vacancy1.title = "Developer"
        vacancy1.requirements = None
        vacancy1.responsibilities = None
        vacancy1.description = "Python development"  # 3 points
        vacancy1.skills = []
        vacancy1.employer = None
        vacancy1.employment = None
        vacancy1.schedule = None
        vacancy1.experience = None

        # Vacancy с высоким score
        vacancy2 = MagicMock()
        vacancy2.id = "2"
        vacancy2.title = "Python Developer"  # 10 points
        vacancy2.requirements = None
        vacancy2.responsibilities = None
        vacancy2.description = None
        vacancy2.skills = []
        vacancy2.employer = None
        vacancy2.employment = None
        vacancy2.schedule = None
        vacancy2.experience = None

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "Python")  # type: ignore
        assert len(result) == 2
        assert result[0] == vacancy2  # Высокий score первый
        assert result[1] == vacancy1  # Низкий score второй
        assert result[0]._relevance_score == 10
        assert result[1]._relevance_score == 3

    def test_filter_vacancies_by_keyword_exception_handling(self):
        """Покрытие: обработка исключений при установке атрибута"""
        # Создаем объект, который не позволяет устанавливать атрибуты
        class ReadOnlyVacancy:
            def __init__(self):
                self.id = "1"
                self.title = "Python Developer"
                self.requirements = None
                self.responsibilities = None
                self.description = None
                self.skills = []
                self.employer = None
                self.employment = None
                self.schedule = None
                self.experience = None

            def __setattr__(self, name, value):
                if name.startswith('_'):
                    raise AttributeError("Cannot set attribute")
                super().__setattr__(name, value)

        vacancy = ReadOnlyVacancy()
        result = filter_vacancies_by_keyword([vacancy], "Python")  # type: ignore
        
        # Должна пройти фильтрация, несмотря на невозможность установить _relevance_score
        assert len(result) == 1
        assert result[0] == vacancy

    def test_filter_vacancies_by_keyword_skills_attribute_error(self):
        """Покрытие: AttributeError в обработке skills - строки 222-223"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Python Developer"  # 10 очков
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None

        # Настраиваем hasattr для выброса исключения при итерации skills
        original_hasattr = hasattr
        def mock_hasattr(obj, name):
            if name == "skills" and obj == vacancy:
                return True
            if obj == vacancy and name == "skills":  
                return True
            return original_hasattr(obj, name)

        # Мокируем hasattr и итерацию для вызова исключения
        with patch('builtins.hasattr', side_effect=mock_hasattr):
            # Делаем skills.iter вызывающим AttributeError
            vacancy.skills = MagicMock()
            vacancy.skills.__iter__ = MagicMock(side_effect=AttributeError("skills error"))
            
            result = filter_vacancies_by_keyword([vacancy], "Python")  # type: ignore
            assert len(result) == 1  # Найдется по title
            assert result[0]._relevance_score == 10

    def test_filter_vacancies_by_keyword_schedule_string_match(self):
        """Покрытие: поиск в schedule как строка - строки 247-248"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = "Гибкий график работы"  # Строковое значение
        vacancy.experience = None

        result = filter_vacancies_by_keyword([vacancy], "Гибкий")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 3  # schedule string match = 3 points

    def test_filter_vacancies_by_keyword_experience_string_match(self):
        """Покрытие: поиск в experience как строка - строки 254-255"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = "Опыт работы от 3 лет"  # Строковое значение

        result = filter_vacancies_by_keyword([vacancy], "работы")  # type: ignore
        assert len(result) == 1
        assert result[0]._relevance_score == 3  # experience string match = 3 points

    def test_filter_vacancies_by_keyword_benefits_attribute_error(self):
        """Покрытие: AttributeError в обработке benefits - строки 262-263"""
        vacancy = MagicMock()
        vacancy.id = "1"
        vacancy.title = "ДМС Python Developer"  # 10 очков, содержит ДМС  
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = []
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None
        
        # Создаем объект benefits, который вызывает ошибку при преобразовании в строку
        benefits_mock = MagicMock()
        benefits_mock.__str__ = MagicMock(side_effect=AttributeError("benefits str error"))
        vacancy.benefits = benefits_mock

        result = filter_vacancies_by_keyword([vacancy], "ДМС")  # type: ignore
        assert len(result) == 1  # Найдется по title, несмотря на ошибку в benefits
        assert result[0]._relevance_score == 10  # Только title match


class TestVacancyContainsKeyword:
    """100% покрытие функции vacancy_contains_keyword"""

    def test_vacancy_contains_keyword_title_match(self):
        """Покрытие: поиск в title"""
        vacancy = MagicMock()
        vacancy.title = "Python Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None

        result = vacancy_contains_keyword(vacancy, "Python")
        assert result is True

    def test_vacancy_contains_keyword_requirements_match(self):
        """Покрытие: поиск в requirements"""
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.requirements = "Django experience required"
        vacancy.responsibilities = None
        vacancy.description = None

        result = vacancy_contains_keyword(vacancy, "Django")
        assert result is True

    def test_vacancy_contains_keyword_responsibilities_match(self):
        """Покрытие: поиск в responsibilities"""
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = "Develop FastAPI apps"
        vacancy.description = None

        result = vacancy_contains_keyword(vacancy, "FastAPI")
        assert result is True

    def test_vacancy_contains_keyword_description_match(self):
        """Покрытие: поиск в description"""
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = "Work with React framework"

        result = vacancy_contains_keyword(vacancy, "React")
        assert result is True

    def test_vacancy_contains_keyword_profession_match(self):
        """Покрытие: поиск в profession (SuperJob field)"""
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.profession = "Vue.js Developer"

        result = vacancy_contains_keyword(vacancy, "Vue")
        assert result is True

    def test_vacancy_contains_keyword_skills_dict_match(self):
        """Покрытие: поиск в skills (dict format)"""
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = [{"name": "Angular"}, {"name": "TypeScript"}]

        result = vacancy_contains_keyword(vacancy, "Angular")
        assert result is True

    def test_vacancy_contains_keyword_skills_string_match(self):
        """Покрытие: поиск в skills (string format)"""
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.skills = ["Node.js", "Express", "MongoDB"]

        result = vacancy_contains_keyword(vacancy, "Node")
        assert result is True

    def test_vacancy_contains_keyword_no_match(self):
        """Покрытие: нет совпадений"""
        vacancy = MagicMock()
        vacancy.title = "Java Developer"
        vacancy.requirements = "Spring experience"
        vacancy.responsibilities = "Backend development"
        vacancy.description = "Enterprise applications"

        result = vacancy_contains_keyword(vacancy, "Python")
        assert result is False

    def test_vacancy_contains_keyword_case_insensitive(self):
        """Покрытие: поиск без учета регистра"""
        vacancy = MagicMock()
        vacancy.title = "PYTHON DEVELOPER"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None

        result = vacancy_contains_keyword(vacancy, "python")
        assert result is True

    def test_vacancy_contains_keyword_none_fields(self):
        """Покрытие: все поля None"""
        vacancy = MagicMock()
        vacancy.title = None
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None

        result = vacancy_contains_keyword(vacancy, "Python")
        assert result is False

    def test_vacancy_contains_keyword_skills_exception_handling(self):
        """Покрытие: обработка исключений в skills"""
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None  
        vacancy.description = None
        # Мокируем skills так, чтобы вызывало исключение при итерации
        vacancy.skills = MagicMock()
        vacancy.skills.__iter__ = MagicMock(side_effect=AttributeError("Test error"))

        result = vacancy_contains_keyword(vacancy, "Python")
        assert result is False  # Должно вернуть False при исключении

    def test_vacancy_contains_keyword_profession_exception_handling(self):
        """Покрытие: обработка исключений в profession"""
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        # Мокируем profession так, чтобы вызывало исключение
        vacancy.profession = MagicMock()
        vacancy.profession.__str__ = MagicMock(side_effect=TypeError("Test error"))

        result = vacancy_contains_keyword(vacancy, "Python")
        assert result is False  # Должно вернуть False при исключении


class TestSearchQueryParser:
    """100% покрытие класса SearchQueryParser"""

    def test_search_query_parser_init(self):
        """Покрытие: инициализация"""
        parser = SearchQueryParser()
        assert parser is not None

    def test_search_query_parser_parse_none(self):
        """Покрытие: None input"""
        parser = SearchQueryParser()
        result = parser.parse(None)  # type: ignore
        assert result is None

    def test_search_query_parser_parse_empty(self):
        """Покрытие: пустая строка"""
        parser = SearchQueryParser()
        result = parser.parse("")
        assert result is None

    def test_search_query_parser_parse_whitespace(self):
        """Покрытие: только пробелы"""
        parser = SearchQueryParser()
        result = parser.parse("   ")
        assert result is None

    def test_search_query_parser_parse_and_operator(self):
        """Покрытие: оператор AND"""
        parser = SearchQueryParser()
        result = parser.parse("Python AND Django")
        expected = {"keywords": ["PYTHON", "DJANGO"], "operator": "AND"}
        assert result == expected

    def test_search_query_parser_parse_or_operator(self):
        """Покрытие: оператор OR"""
        parser = SearchQueryParser()
        result = parser.parse("Python OR Django")
        expected = {"keywords": ["PYTHON", "DJANGO"], "operator": "OR"}
        assert result == expected

    def test_search_query_parser_parse_comma_separator(self):
        """Покрытие: разделение запятыми"""
        parser = SearchQueryParser()
        result = parser.parse("Python, Django, FastAPI")
        expected = {"keywords": ["Python", "Django", "FastAPI"], "operator": "OR"}
        assert result == expected

    def test_search_query_parser_parse_single_word(self):
        """Покрытие: одно слово"""
        parser = SearchQueryParser()
        result = parser.parse("Python")
        expected = {"keywords": ["Python"], "operator": "OR"}
        assert result == expected

    def test_search_query_parser_parse_and_case_insensitive(self):
        """Покрытие: AND в разном регистре"""
        parser = SearchQueryParser()
        result = parser.parse("Python and Django")
        expected = {"keywords": ["PYTHON", "DJANGO"], "operator": "AND"}
        assert result == expected

    def test_search_query_parser_parse_or_case_insensitive(self):
        """Покрытие: OR в разном регистре"""  
        parser = SearchQueryParser()
        result = parser.parse("Python or Django")
        expected = {"keywords": ["PYTHON", "DJANGO"], "operator": "OR"}
        assert result == expected

    def test_search_query_parser_parse_mixed_case_operators(self):
        """Покрытие: операторы в смешанном регистре"""
        parser = SearchQueryParser()
        result = parser.parse("Python And Django")
        expected = {"keywords": ["PYTHON", "DJANGO"], "operator": "AND"}
        assert result == expected

    def test_search_query_parser_parse_multiple_and(self):
        """Покрытие: множественные AND"""
        parser = SearchQueryParser()
        result = parser.parse("Python AND Django AND FastAPI")
        expected = {"keywords": ["PYTHON", "DJANGO", "FASTAPI"], "operator": "AND"}
        assert result == expected

    def test_search_query_parser_parse_multiple_or(self):
        """Покрытие: множественные OR"""
        parser = SearchQueryParser()
        result = parser.parse("Python OR Django OR FastAPI")
        expected = {"keywords": ["PYTHON", "DJANGO", "FASTAPI"], "operator": "OR"}
        assert result == expected

    def test_search_query_parser_parse_comma_with_spaces(self):
        """Покрытие: запятые с пробелами"""
        parser = SearchQueryParser()
        result = parser.parse("Python,   Django,FastAPI  ")
        expected = {"keywords": ["Python", "Django", "FastAPI"], "operator": "OR"}
        assert result == expected

    def test_search_query_parser_parse_phrase_query(self):
        """Покрытие: фразовый запрос без операторов"""
        parser = SearchQueryParser()
        result = parser.parse("Python web developer")
        expected = {"keywords": ["Python web developer"], "operator": "OR"}
        assert result == expected


class TestAdvancedSearch:
    """100% покрытие класса AdvancedSearch"""

    def test_advanced_search_init(self):
        """Покрытие: инициализация"""
        search = AdvancedSearch()
        assert search is not None

    def test_advanced_search_with_and_basic(self):
        """Покрытие: поиск с оператором AND"""
        search = AdvancedSearch()
        
        # Мокируем вакансии
        vacancy1 = MagicMock()
        vacancy1.title = "Python Developer"
        vacancy1.description = "Django web development"
        vacancy1.search_query = None

        vacancy2 = MagicMock()
        vacancy2.title = "Java Developer"
        vacancy2.description = "Spring framework"
        vacancy2.search_query = None

        vacancy3 = MagicMock()
        vacancy3.title = "Python Django Developer"
        vacancy3.description = "Full stack development"
        vacancy3.search_query = None

        vacancies = [vacancy1, vacancy2, vacancy3]
        keywords = ["Python", "Django"]
        
        result = search.search_with_and(vacancies, keywords)
        
        # Должна найтись vacancy1 (есть Python в title и Django в description)
        # И vacancy3 (есть и Python и Django в title)
        assert len(result) == 2
        assert vacancy1 in result
        assert vacancy3 in result

    def test_advanced_search_with_and_with_search_query(self):
        """Покрытие: поиск AND с полем search_query"""
        search = AdvancedSearch()
        
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.description = "Web development"
        vacancy.search_query = "Python Django experience"

        result = search.search_with_and([vacancy], ["Python", "Django"])
        assert len(result) == 1
        assert vacancy in result

    def test_advanced_search_with_and_no_matches(self):
        """Покрытие: AND поиск без результатов"""
        search = AdvancedSearch()
        
        vacancy = MagicMock()
        vacancy.title = "Java Developer"
        vacancy.description = "Spring Boot"
        vacancy.search_query = None

        result = search.search_with_and([vacancy], ["Python", "Django"])
        assert len(result) == 0

    def test_advanced_search_with_and_none_description(self):
        """Покрытие: AND поиск с None description"""
        search = AdvancedSearch()
        
        vacancy = MagicMock()
        vacancy.title = "Python Django Developer"
        vacancy.description = None
        vacancy.search_query = None

        result = search.search_with_and([vacancy], ["Python", "Django"])
        assert len(result) == 1
        assert vacancy in result

    def test_advanced_search_with_or_basic(self):
        """Покрытие: поиск с оператором OR"""
        search = AdvancedSearch()
        
        vacancy1 = MagicMock()
        vacancy1.title = "Python Developer"
        vacancy1.description = "Web development"
        vacancy1.search_query = None

        vacancy2 = MagicMock()
        vacancy2.title = "Java Developer"
        vacancy2.description = "Django REST API"  # Содержит Django
        vacancy2.search_query = None

        vacancy3 = MagicMock()
        vacancy3.title = "Frontend Developer"
        vacancy3.description = "React applications"
        vacancy3.search_query = None

        vacancies = [vacancy1, vacancy2, vacancy3]
        keywords = ["Python", "Django"]
        
        result = search.search_with_or(vacancies, keywords)
        
        # Должны найтись vacancy1 (Python в title) и vacancy2 (Django в description)
        assert len(result) == 2
        assert vacancy1 in result
        assert vacancy2 in result

    def test_advanced_search_with_or_with_search_query(self):
        """Покрытие: поиск OR с полем search_query"""
        search = AdvancedSearch()
        
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.description = "Web development"
        vacancy.search_query = "Looking for Python developer"

        result = search.search_with_or([vacancy], ["Python", "NonExistentKeyword"])
        assert len(result) == 1
        assert vacancy in result

    def test_advanced_search_with_or_no_matches(self):
        """Покрытие: OR поиск без результатов"""
        search = AdvancedSearch()
        
        vacancy = MagicMock()
        vacancy.title = "C++ Developer"
        vacancy.description = "Systems programming"
        vacancy.search_query = None

        result = search.search_with_or([vacancy], ["Python", "Django"])
        assert len(result) == 0

    def test_advanced_search_with_or_none_description(self):
        """Покрытие: OR поиск с None description"""
        search = AdvancedSearch()
        
        vacancy = MagicMock()
        vacancy.title = "Python Developer"
        vacancy.description = None
        vacancy.search_query = None

        result = search.search_with_or([vacancy], ["Python", "Django"])
        assert len(result) == 1
        assert vacancy in result

    def test_advanced_search_case_insensitive(self):
        """Покрытие: поиск без учета регистра"""
        search = AdvancedSearch()
        
        vacancy = MagicMock()
        vacancy.title = "PYTHON DEVELOPER"
        vacancy.description = "DJANGO FRAMEWORK"
        vacancy.search_query = None

        result_and = search.search_with_and([vacancy], ["python", "django"])
        result_or = search.search_with_or([vacancy], ["python", "django"])
        
        assert len(result_and) == 1
        assert len(result_or) == 1

    def test_advanced_search_empty_search_query(self):
        """Покрытие: пустое поле search_query"""
        search = AdvancedSearch()
        
        vacancy = MagicMock()
        vacancy.title = "Developer"
        vacancy.description = "Web development"
        vacancy.search_query = ""

        result = search.search_with_and([vacancy], ["Python"])
        assert len(result) == 0  # Нет Python ни в title, ни в description, search_query пустое

    def test_advanced_search_missing_search_query_attribute(self):
        """Покрытие: отсутствие атрибута search_query"""
        search = AdvancedSearch()
        
        # Создаем объект без атрибута search_query
        vacancy = MagicMock()
        vacancy.title = "Python Developer"
        vacancy.description = "Django development"
        del vacancy.search_query  # Удаляем атрибут

        result = search.search_with_and([vacancy], ["Python", "Django"])
        assert len(result) == 1  # Должен найти через title + description