#!/usr/bin/env python3
"""
Тесты модуля ui_helpers.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций 
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Мокирование всех input() и print() операций

Модуль содержит:
- Функции пользовательского ввода с валидацией
- Парсинг поисковых запросов и диапазонов зарплат  
- Фильтрация вакансий по ключевым словам
- Wrapper функции (устаревшие)
- Отладочные функции вывода
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import List

from src.utils.ui_helpers import (
    get_user_input,
    get_positive_integer,
    parse_salary_range,
    confirm_action,
    filter_vacancies_by_keyword,
    _parse_search_query,
    _build_searchable_text,
    filter_vacancies_by_min_salary,
    filter_vacancies_by_max_salary,
    filter_vacancies_by_salary_range,
    get_vacancies_with_salary,
    sort_vacancies_by_salary,
    filter_vacancies_by_multiple_keywords,
    search_vacancies_advanced,
    debug_vacancy_search,
    debug_search_vacancies,
    display_vacancy_info
)


class MockVacancy:
    """Мок-объект вакансии для тестирования"""
    
    def __init__(self, **kwargs):
        # Базовые поля
        self.id = kwargs.get('id', 'test123')
        self.title = kwargs.get('title', 'Test Job')
        self.description = kwargs.get('description', '')
        self.requirements = kwargs.get('requirements', '')
        self.responsibilities = kwargs.get('responsibilities', '')
        self.employer = kwargs.get('employer', None)
        self.employment = kwargs.get('employment', None)
        self.schedule = kwargs.get('schedule', None)
        self.experience = kwargs.get('experience', None)
        self.benefits = kwargs.get('benefits', None)
        self.skills = kwargs.get('skills', [])
        self.salary = kwargs.get('salary', None)
        
        # Любые дополнительные атрибуты
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)


class MockEmployer:
    """Мок-объект работодателя"""
    
    def __init__(self, name=None):
        self.name = name
    
    def __str__(self):
        return self.name or "Test Company"


class TestUserInputFunctions:
    """100% покрытие функций пользовательского ввода"""

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_valid_required(self, mock_print, mock_input):
        """Покрытие: валидный ввод для обязательного поля"""
        mock_input.return_value = "  test input  "
        
        result = get_user_input("Enter text:", required=True)
        
        assert result == "test input"  # Проверяем strip()
        mock_input.assert_called_once_with("Enter text:")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_empty_required_then_valid(self, mock_print, mock_input):
        """Покрытие: пустой ввод для обязательного поля, затем валидный"""
        mock_input.side_effect = ["", "   ", "valid input"]
        
        result = get_user_input("Enter text:", required=True)
        
        assert result == "valid input"
        assert mock_input.call_count == 3
        assert mock_print.call_count == 2
        mock_print.assert_any_call("Поле не может быть пустым!")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_empty_not_required(self, mock_print, mock_input):
        """Покрытие: пустой ввод для необязательного поля"""
        mock_input.return_value = ""
        
        result = get_user_input("Enter optional text:", required=False)
        
        assert result is None
        mock_print.assert_not_called()  # Нет сообщений об ошибке

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_valid_not_required(self, mock_print, mock_input):
        """Покрытие: валидный ввод для необязательного поля"""
        mock_input.return_value = "optional text"
        
        result = get_user_input("Enter optional text:", required=False)
        
        assert result == "optional text"

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_valid_input(self, mock_print, mock_input):
        """Покрытие: валидный положительный integer"""
        mock_input.return_value = "123"
        
        result = get_positive_integer("Enter number:")
        
        assert result == 123
        mock_print.assert_not_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_empty_with_default(self, mock_print, mock_input):
        """Покрытие: пустой ввод с default значением"""
        mock_input.return_value = ""
        
        result = get_positive_integer("Enter number:", default=42)
        
        assert result == 42

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_empty_no_default(self, mock_print, mock_input):
        """Покрытие: пустой ввод без default"""
        mock_input.return_value = ""
        
        result = get_positive_integer("Enter number:")
        
        assert result is None
        mock_print.assert_called_once_with("Введите корректное число!")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_negative(self, mock_print, mock_input):
        """Покрытие: отрицательное число"""
        mock_input.return_value = "-5"
        
        result = get_positive_integer("Enter number:")
        
        assert result is None
        mock_print.assert_called_once_with("Число должно быть положительным!")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_zero(self, mock_print, mock_input):
        """Покрытие: ноль (не положительное число)"""
        mock_input.return_value = "0"
        
        result = get_positive_integer("Enter number:")
        
        assert result is None
        mock_print.assert_called_once_with("Число должно быть положительным!")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_invalid_format(self, mock_print, mock_input):
        """Покрытие: некорректный формат числа"""
        mock_input.return_value = "abc"
        
        result = get_positive_integer("Enter number:")
        
        assert result is None
        mock_print.assert_called_once_with("Введите корректное число!")

    @patch('builtins.print')
    def test_parse_salary_range_valid_with_spaces(self, mock_print):
        """Покрытие: валидный диапазон с пробелами"""
        result = parse_salary_range("100000 - 150000")
        
        assert result == (100000, 150000)
        mock_print.assert_not_called()

    @patch('builtins.print')
    def test_parse_salary_range_valid_without_spaces(self, mock_print):
        """Покрытие: валидный диапазон без пробелов"""
        result = parse_salary_range("80000-120000")
        
        assert result == (80000, 120000)

    @patch('builtins.print')
    def test_parse_salary_range_reversed_order(self, mock_print):
        """Покрытие: обратный порядок чисел (автоисправление)"""
        result = parse_salary_range("200000 - 100000")
        
        assert result == (100000, 200000)  # Исправляется порядок

    @patch('builtins.print')
    def test_parse_salary_range_invalid_format(self, mock_print):
        """Покрытие: некорректный формат без дефиса"""
        result = parse_salary_range("100000 150000")
        
        assert result is None
        mock_print.assert_called_once_with("Неверный формат диапазона. Используйте формат: 100000 - 150000")

    @patch('builtins.print')
    def test_parse_salary_range_invalid_numbers(self, mock_print):
        """Покрытие: некорректные числа в диапазоне"""
        result = parse_salary_range("abc - def")
        
        assert result is None
        mock_print.assert_called_once_with("Введите корректные числа!")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_confirm_action_yes_variants(self, mock_print, mock_input):
        """Покрытие: различные варианты подтверждения"""
        # Тестируем разные варианты "да"
        for answer in ["y", "yes", "д", "да"]:
            mock_input.return_value = answer
            result = confirm_action("Continue?")
            assert result is True
            
        # Проверяем заглавные буквы
        mock_input.return_value = "YES"
        result = confirm_action("Continue?")
        assert result is True

    @patch('builtins.input')
    @patch('builtins.print')
    def test_confirm_action_no_variants(self, mock_print, mock_input):
        """Покрытие: различные варианты отказа"""
        # Тестируем разные варианты "нет"
        for answer in ["n", "no", "н", "нет"]:
            mock_input.return_value = answer
            result = confirm_action("Continue?")
            assert result is False

    @patch('builtins.input')
    @patch('builtins.print')
    def test_confirm_action_invalid_then_valid(self, mock_print, mock_input):
        """Покрытие: некорректный ввод, затем валидный"""
        mock_input.side_effect = ["maybe", "invalid", "y"]
        
        result = confirm_action("Continue?")
        
        assert result is True
        assert mock_input.call_count == 3
        assert mock_print.call_count == 2
        mock_print.assert_any_call("Введите 'y' для да или 'n' для нет.")


class TestSearchQueryParsing:
    """100% покрытие парсинга поисковых запросов"""

    def test_parse_search_query_empty(self):
        """Покрытие: пустой или None запрос"""
        assert _parse_search_query("") is None
        assert _parse_search_query(None) is None
        assert _parse_search_query("   ") is None

    def test_parse_search_query_single_word(self):
        """Покрытие: одно слово"""
        result = _parse_search_query("Python")
        
        assert result == {"keywords": ["Python"], "operator": "OR"}

    def test_parse_search_query_and_operator(self):
        """Покрытие: оператор AND"""
        result = _parse_search_query("Python AND Django")
        
        assert result == {"keywords": ["Python", "Django"], "operator": "AND"}

    def test_parse_search_query_and_operator_case_insensitive(self):
        """Покрытие: оператор AND в разном регистре (маленькие буквы не распознаются)"""
        result = _parse_search_query("python and django and flask")
        
        # Маленькие буквы 'and' не распознаются как оператор, интерпретируются как одна фраза
        assert result == {"keywords": ["python and django and flask"], "operator": "OR"}

    def test_parse_search_query_or_operator(self):
        """Покрытие: оператор OR"""
        result = _parse_search_query("Java OR Kotlin")
        
        assert result == {"keywords": ["Java", "Kotlin"], "operator": "OR"}

    def test_parse_search_query_or_operator_case_insensitive(self):
        """Покрытие: оператор OR в разном регистре (маленькие буквы не распознаются)"""
        result = _parse_search_query("java or kotlin or scala")
        
        # Маленькие буквы 'or' не распознаются, интерпретируются как одна фраза
        assert result == {"keywords": ["java or kotlin or scala"], "operator": "OR"}

    def test_parse_search_query_comma_separator(self):
        """Покрытие: запятая как разделитель"""
        result = _parse_search_query("Python, Django, Flask")
        
        assert result == {"keywords": ["Python", "Django", "Flask"], "operator": "OR"}

    def test_parse_search_query_comma_with_spaces(self):
        """Покрытие: запятая с пробелами и пустые элементы"""
        result = _parse_search_query("Python,  ,Django, ,Flask")
        
        assert result == {"keywords": ["Python", "Django", "Flask"], "operator": "OR"}

    def test_parse_search_query_phrase(self):
        """Покрытие: фраза из нескольких слов"""
        result = _parse_search_query("Senior Python Developer")
        
        assert result == {"keywords": ["Senior Python Developer"], "operator": "OR"}


class TestBuildSearchableText:
    """100% покрытие функции построения поискового текста"""

    def test_build_searchable_text_all_fields(self):
        """Покрытие: все поля заполнены"""
        employer = MockEmployer("Test Company")
        employment = MagicMock()
        employment.__str__ = MagicMock(return_value="Full-time")
        
        vacancy = MockVacancy(
            title="Senior Developer",
            description="Great job opportunity",
            requirements="Python experience",
            responsibilities="Code development",
            employer=employer,
            employment=employment,
            skills=["Python", "Django"]
        )
        
        result = _build_searchable_text(vacancy)
        
        # Должны быть включены все поля в нижнем регистре
        assert "senior developer" in result
        assert "great job opportunity" in result
        assert "python experience" in result
        assert "code development" in result
        assert "test company" in result
        assert "full-time" in result
        assert "python" in result
        assert "django" in result

    def test_build_searchable_text_empty_fields(self):
        """Покрытие: пустые поля"""
        vacancy = MockVacancy(
            title=None,
            description="",
            requirements=None,
            responsibilities="",
            employer=None,
            employment=None,
            skills=None
        )
        
        result = _build_searchable_text(vacancy)
        
        # Должна быть пустая строка или только пробелы
        assert result.strip() == ""

    def test_build_searchable_text_employer_variations(self):
        """Покрытие: различные форматы employer"""
        # Employer с атрибутом name
        employer1 = MockEmployer("Company A")
        vacancy1 = MockVacancy(employer=employer1)
        result1 = _build_searchable_text(vacancy1)
        assert "company a" in result1
        
        # Employer как dict
        vacancy2 = MockVacancy(employer={"name": "Company B"})
        result2 = _build_searchable_text(vacancy2)
        assert "company b" in result2
        
        # Employer как строка
        vacancy3 = MockVacancy(employer="Company C")
        result3 = _build_searchable_text(vacancy3)
        assert "company c" in result3

    def test_build_searchable_text_employment_with_name(self):
        """Покрытие: employment с атрибутом name"""
        employment = MagicMock()
        # Мокируем hasattr чтобы __str__ не нашелся, а name нашелся
        employment.name = "Part-time"
        
        vacancy = MockVacancy(employment=employment)
        
        with patch('builtins.hasattr', side_effect=lambda obj, attr: attr == 'name'):
            result = _build_searchable_text(vacancy)
            assert "part-time" in result

    def test_build_searchable_text_skills_variations(self):
        """Покрытие: различные форматы skills"""
        vacancy = MockVacancy(
            skills=[
                {"name": "Python"},  # dict с name
                "JavaScript",        # строка  
                123,                # другой тип
                {"other": "value"}  # dict без name
            ]
        )
        
        result = _build_searchable_text(vacancy)
        
        assert "python" in result
        assert "javascript" in result
        assert "123" in result
        assert "value" in result

    def test_build_searchable_text_no_skills_attribute(self):
        """Покрытие: вакансия без атрибута skills"""
        vacancy = MockVacancy()
        delattr(vacancy, 'skills')  # Удаляем атрибут
        
        result = _build_searchable_text(vacancy)
        
        # Не должно быть ошибок, просто пропускаем skills
        assert isinstance(result, str)


class TestVacancyFiltering:
    """100% покрытие фильтрации вакансий"""

    def test_filter_vacancies_by_keyword_empty_input(self):
        """Покрытие: пустые входные данные"""
        vacancies = [MockVacancy()]
        
        # Пустое ключевое слово
        assert filter_vacancies_by_keyword(vacancies, "") == []
        assert filter_vacancies_by_keyword(vacancies, None) == []
        
        # Пустой список вакансий
        assert filter_vacancies_by_keyword([], "Python") == []

    def test_filter_vacancies_by_keyword_single_word(self):
        """Покрытие: поиск по одному слову"""
        vacancy1 = MockVacancy(title="Python Developer")
        vacancy2 = MockVacancy(title="Java Developer") 
        vacancy3 = MockVacancy(description="Experience with Python required")
        
        vacancies = [vacancy1, vacancy2, vacancy3]
        result = filter_vacancies_by_keyword(vacancies, "Python")
        
        assert len(result) == 2
        assert vacancy1 in result
        assert vacancy3 in result
        assert vacancy2 not in result

    def test_filter_vacancies_by_keyword_and_operator(self):
        """Покрытие: поиск с оператором AND"""
        vacancy1 = MockVacancy(title="Python Django Developer")
        vacancy2 = MockVacancy(title="Python Flask Developer")
        vacancy3 = MockVacancy(title="Java Spring Developer")
        
        vacancies = [vacancy1, vacancy2, vacancy3]
        
        with patch('src.utils.ui_helpers._parse_search_query') as mock_parse:
            mock_parse.return_value = {"keywords": ["Python", "Django"], "operator": "AND"}
            
            with patch('src.utils.ui_helpers._build_searchable_text') as mock_build:
                mock_build.side_effect = [
                    "python django developer",
                    "python flask developer", 
                    "java spring developer"
                ]
                
                result = filter_vacancies_by_keyword(vacancies, "Python AND Django")
        
        assert len(result) == 1
        assert vacancy1 in result

    def test_filter_vacancies_by_keyword_or_operator(self):
        """Покрытие: поиск с оператором OR"""
        vacancy1 = MockVacancy(title="Python Developer")
        vacancy2 = MockVacancy(title="Java Developer")
        vacancy3 = MockVacancy(title="Go Developer")
        
        vacancies = [vacancy1, vacancy2, vacancy3]
        
        with patch('src.utils.ui_helpers._parse_search_query') as mock_parse:
            mock_parse.return_value = {"keywords": ["Python", "Java"], "operator": "OR"}
            
            with patch('src.utils.ui_helpers._build_searchable_text') as mock_build:
                mock_build.side_effect = [
                    "python developer",
                    "java developer",
                    "go developer"
                ]
                
                result = filter_vacancies_by_keyword(vacancies, "Python OR Java")
        
        assert len(result) == 2
        assert vacancy1 in result
        assert vacancy2 in result
        assert vacancy3 not in result

    def test_filter_vacancies_by_keyword_invalid_parse(self):
        """Покрытие: некорректный парсинг запроса"""
        vacancies = [MockVacancy()]
        
        with patch('src.utils.ui_helpers._parse_search_query', return_value=None):
            result = filter_vacancies_by_keyword(vacancies, "invalid query")
        
        assert result == []


class TestWrapperFunctions:
    """100% покрытие устаревших wrapper функций"""

    @patch('src.utils.ui_helpers.VacancyOperations.filter_vacancies_by_min_salary')
    def test_filter_vacancies_by_min_salary_wrapper(self, mock_filter):
        """Покрытие: wrapper для filter_vacancies_by_min_salary"""
        vacancies = [MockVacancy()]
        expected_result = [MockVacancy()]
        mock_filter.return_value = expected_result
        
        result = filter_vacancies_by_min_salary(vacancies, 100000)
        
        mock_filter.assert_called_once_with(vacancies, 100000)
        assert result == expected_result

    @patch('src.utils.ui_helpers.VacancyOperations.filter_vacancies_by_max_salary')
    def test_filter_vacancies_by_max_salary_wrapper(self, mock_filter):
        """Покрытие: wrapper для filter_vacancies_by_max_salary"""
        vacancies = [MockVacancy()]
        expected_result = [MockVacancy()]
        mock_filter.return_value = expected_result
        
        result = filter_vacancies_by_max_salary(vacancies, 150000)
        
        mock_filter.assert_called_once_with(vacancies, 150000)
        assert result == expected_result

    @patch('src.utils.ui_helpers.VacancyOperations.filter_vacancies_by_salary_range')
    def test_filter_vacancies_by_salary_range_wrapper(self, mock_filter):
        """Покрытие: wrapper для filter_vacancies_by_salary_range"""
        vacancies = [MockVacancy()]
        expected_result = [MockVacancy()]
        mock_filter.return_value = expected_result
        
        result = filter_vacancies_by_salary_range(vacancies, 80000, 120000)
        
        mock_filter.assert_called_once_with(vacancies, 80000, 120000)
        assert result == expected_result

    @patch('src.utils.ui_helpers.VacancyOperations.get_vacancies_with_salary')
    def test_get_vacancies_with_salary_wrapper(self, mock_filter):
        """Покрытие: wrapper для get_vacancies_with_salary"""
        vacancies = [MockVacancy()]
        expected_result = [MockVacancy()]
        mock_filter.return_value = expected_result
        
        result = get_vacancies_with_salary(vacancies)
        
        mock_filter.assert_called_once_with(vacancies)
        assert result == expected_result

    @patch('src.utils.ui_helpers.VacancyOperations.sort_vacancies_by_salary')
    def test_sort_vacancies_by_salary_wrapper(self, mock_sort):
        """Покрытие: wrapper для sort_vacancies_by_salary"""
        vacancies = [MockVacancy()]
        expected_result = [MockVacancy()]
        mock_sort.return_value = expected_result
        
        # Тест с default параметром
        result1 = sort_vacancies_by_salary(vacancies)
        mock_sort.assert_called_with(vacancies, True)
        
        # Тест с явным параметром  
        result2 = sort_vacancies_by_salary(vacancies, reverse=False)
        mock_sort.assert_called_with(vacancies, False)

    @patch('src.utils.ui_helpers.VacancyOperations.filter_vacancies_by_multiple_keywords')
    def test_filter_vacancies_by_multiple_keywords_wrapper(self, mock_filter):
        """Покрытие: wrapper для filter_vacancies_by_multiple_keywords"""
        vacancies = [MockVacancy()]
        keywords = ["Python", "Django"]
        expected_result = [MockVacancy()]
        mock_filter.return_value = expected_result
        
        result = filter_vacancies_by_multiple_keywords(vacancies, keywords)
        
        mock_filter.assert_called_once_with(vacancies, keywords)
        assert result == expected_result

    @patch('src.utils.ui_helpers.VacancyOperations.search_vacancies_advanced')
    def test_search_vacancies_advanced_wrapper(self, mock_search):
        """Покрытие: wrapper для search_vacancies_advanced"""
        vacancies = [MockVacancy()]
        query = "Python AND Django"
        expected_result = [MockVacancy()]
        mock_search.return_value = expected_result
        
        result = search_vacancies_advanced(vacancies, query)
        
        mock_search.assert_called_once_with(vacancies, query)
        assert result == expected_result


class TestDebugFunctions:
    """100% покрытие отладочных функций"""

    @patch('builtins.print')
    def test_debug_vacancy_search_full_info(self, mock_print):
        """Покрытие: отладка поиска с полной информацией о вакансии"""
        vacancy = MockVacancy(
            id="test123",
            title="Senior Python Developer",
            description="Great opportunity to work with Python and Django",
            requirements="3+ years Python experience",
            responsibilities="Develop web applications",
            skills=["Python", "Django", "PostgreSQL"],
            employer="Tech Company",
            experience="3-6 лет",
            employment="Полная занятость", 
            schedule="Полный день",
            benefits="ДМС, обучение"
        )
        
        debug_vacancy_search(vacancy, "Python")
        
        # Проверяем количество print вызовов
        assert mock_print.call_count >= 10
        
        # Проверяем содержимое вывода
        printed_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        printed_text = " ".join(printed_calls)
        
        assert "Senior Python Developer" in printed_text
        assert "test123" in printed_text
        assert "Great opportunity" in printed_text
        assert "Python experience" in printed_text
        assert "заголовок" in printed_text  # Найдено в заголовке

    @patch('builtins.print')
    def test_debug_vacancy_search_minimal_info(self, mock_print):
        """Покрытие: отладка поиска с минимальной информацией"""
        vacancy = MockVacancy(
            title="Simple Job",
            description=None,
            requirements=None,
            responsibilities=None
        )
        
        debug_vacancy_search(vacancy, "test")
        
        # Должны быть вызовы print, но с "Нет" для пустых полей
        printed_text = " ".join([str(call[0][0]) for call in mock_print.call_args_list])
        assert "Simple Job" in printed_text
        assert "Нет" in printed_text

    @patch('builtins.print')
    def test_debug_vacancy_search_keyword_found_in_different_fields(self, mock_print):
        """Покрытие: ключевое слово в разных полях"""
        vacancy = MockVacancy(
            title="Python Developer",
            description="Work with Python frameworks",
            requirements="Python skills required",
            responsibilities="Python development tasks"
        )
        
        debug_vacancy_search(vacancy, "Python")
        
        printed_text = " ".join([str(call[0][0]) for call in mock_print.call_args_list])
        
        # Должно найти во всех полях
        assert "заголовок" in printed_text
        assert "описание" in printed_text  
        assert "требования" in printed_text
        assert "обязанности" in printed_text

    @patch('builtins.print')
    def test_debug_vacancy_search_keyword_not_found(self, mock_print):
        """Покрытие: ключевое слово не найдено"""
        vacancy = MockVacancy(
            title="Java Developer",
            description="Java and Spring experience"
        )
        
        debug_vacancy_search(vacancy, "Python")
        
        printed_text = " ".join([str(call[0][0]) for call in mock_print.call_args_list])
        assert "НИГДЕ" in printed_text

    @patch('builtins.print')
    @patch('src.utils.ui_helpers.debug_vacancy_search')
    def test_debug_search_vacancies_multiple(self, mock_debug_single, mock_print):
        """Покрытие: отладка поиска по множеству вакансий"""
        vacancies = [
            MockVacancy(title=f"Job {i}")
            for i in range(10)  # 10 вакансий
        ]
        
        debug_search_vacancies(vacancies, "test")
        
        # Должны быть общие print вызовы
        assert mock_print.call_count >= 2
        printed_text = " ".join([str(call[0][0]) for call in mock_print.call_args_list])
        assert "Всего вакансий: 10" in printed_text
        
        # Должен вызваться debug для первых 5 вакансий
        assert mock_debug_single.call_count == 5

    @patch('builtins.print') 
    @patch('src.utils.ui_helpers.debug_vacancy_search')
    def test_debug_search_vacancies_few(self, mock_debug_single, mock_print):
        """Покрытие: отладка поиска по малому количеству вакансий"""
        vacancies = [MockVacancy(title="Job 1"), MockVacancy(title="Job 2")]
        
        debug_search_vacancies(vacancies, "keyword")
        
        # Должен вызваться debug для всех вакансий (меньше 5)
        assert mock_debug_single.call_count == 2

    @patch('src.utils.ui_helpers.vacancy_formatter')
    def test_display_vacancy_info_with_number(self, mock_formatter):
        """Покрытие: отображение информации с номером"""
        vacancy = MockVacancy()
        
        display_vacancy_info(vacancy, 42)
        
        mock_formatter.display_vacancy_info.assert_called_once_with(vacancy, 42)

    @patch('src.utils.ui_helpers.vacancy_formatter')
    def test_display_vacancy_info_without_number(self, mock_formatter):
        """Покрытие: отображение информации без номера"""
        vacancy = MockVacancy()
        
        display_vacancy_info(vacancy)
        
        mock_formatter.display_vacancy_info.assert_called_once_with(vacancy, None)


class TestIntegration:
    """Интеграционные тесты для совместной работы функций"""

    @patch('builtins.input')
    @patch('builtins.print')
    def test_user_input_and_parsing_integration(self, mock_print, mock_input):
        """Покрытие: интеграция пользовательского ввода и парсинга"""
        # Пользователь вводит диапазон зарплат
        mock_input.return_value = "100000 - 150000"
        user_range = get_user_input("Enter salary range:")
        
        # Парсим введенный диапазон
        parsed_range = parse_salary_range(user_range)
        
        assert parsed_range == (100000, 150000)

    def test_search_query_parsing_and_filtering_integration(self):
        """Покрытие: интеграция парсинга запроса и фильтрации"""
        vacancies = [
            MockVacancy(title="Python Django Developer"),
            MockVacancy(title="Python Flask Developer"),
            MockVacancy(title="Java Spring Developer")
        ]
        
        # Парсим запрос
        query = "Python AND Django"
        parsed = _parse_search_query(query)
        
        assert parsed["operator"] == "AND"
        assert "Python" in parsed["keywords"]
        assert "Django" in parsed["keywords"]
        
        # Используем результат парсинга для фильтрации
        result = filter_vacancies_by_keyword(vacancies, query)
        
        # Должна найтись только Django вакансия
        assert len(result) == 1
        assert "Django" in result[0].title

    def test_edge_cases_combination(self):
        """Покрытие: граничные случаи в комбинации"""
        # Комбинация пустых входных данных
        assert filter_vacancies_by_keyword([], "") == []
        assert _parse_search_query("") is None
        
        # MockVacancy по умолчанию имеет title="Test Job"
        empty_vacancy = MockVacancy(
            title=None, description=None, requirements=None, 
            responsibilities=None, employer=None, employment=None, skills=[]
        )
        assert _build_searchable_text(empty_vacancy).strip() == ""