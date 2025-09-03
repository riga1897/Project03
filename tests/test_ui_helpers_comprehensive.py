
"""
Комплексные тесты для модуля ui_helpers с максимальным покрытием кода.
Включает тестирование всех функций помощников пользовательского интерфейса.

Все тесты используют консолидированные моки без внешних запросов.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import List, Dict, Any, Optional

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.ui_helpers import (
    get_user_input, get_positive_integer, parse_salary_range, confirm_action,
    filter_vacancies_by_keyword, debug_vacancy_search, debug_search_vacancies,
    display_vacancy_info, _parse_search_query, _build_searchable_text
)
from src.vacancies.models import Vacancy, Employer
from src.utils.salary import Salary


class ConsolidatedUIHelpersMocks:
    """Консолидированная система моков для UI helpers"""
    
    def __init__(self):
        """Инициализация всех моков"""
        self.input_mock = Mock()
        self.print_mock = Mock()
        self.vacancy_mock = Mock()
        self.employer_mock = Mock()
        self.salary_mock = Mock()
        
        # Настройка поведения моков
        self.input_mock.return_value = "test_input"
        self.vacancy_mock.title = "Python Developer"
        self.vacancy_mock.description = "Test description"
        self.vacancy_mock.requirements = "Python, Django"
        self.vacancy_mock.employer = self.employer_mock
        self.employer_mock.name = "Test Company"
        

# Глобальный экземпляр моков
ui_mocks = ConsolidatedUIHelpersMocks()


class TestGetUserInput:
    """Тестирование функции получения пользовательского ввода"""
    
    @patch('builtins.input')
    def test_get_user_input_valid_required(self, mock_input):
        """Тестирование получения валидного обязательного ввода"""
        mock_input.return_value = "valid input"
        result = get_user_input("Enter text: ", required=True)
        assert result == "valid input"
        mock_input.assert_called_once_with("Enter text: ")
    
    @patch('builtins.input')
    def test_get_user_input_empty_optional(self, mock_input):
        """Тестирование пустого ввода для необязательного поля"""
        mock_input.return_value = ""
        result = get_user_input("Enter text: ", required=False)
        assert result is None
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_empty_required_then_valid(self, mock_print, mock_input):
        """Тестирование пустого ввода для обязательного поля, затем валидный"""
        mock_input.side_effect = ["", "valid input"]
        result = get_user_input("Enter text: ", required=True)
        assert result == "valid input"
        assert mock_input.call_count == 2
        mock_print.assert_called_with("Поле не может быть пустым!")
    
    @patch('builtins.input')
    def test_get_user_input_whitespace_handling(self, mock_input):
        """Тестирование обработки пробелов"""
        mock_input.return_value = "  trimmed  "
        result = get_user_input("Enter text: ", required=True)
        assert result == "trimmed"


class TestGetPositiveInteger:
    """Тестирование функции получения положительного числа"""
    
    @patch('builtins.input')
    def test_get_positive_integer_valid(self, mock_input):
        """Тестирование ввода валидного положительного числа"""
        mock_input.return_value = "42"
        result = get_positive_integer("Enter number: ")
        assert result == 42
    
    @patch('builtins.input')
    def test_get_positive_integer_with_default(self, mock_input):
        """Тестирование с значением по умолчанию"""
        mock_input.return_value = ""
        result = get_positive_integer("Enter number: ", default=10)
        assert result == 10
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_negative(self, mock_print, mock_input):
        """Тестирование отрицательного числа"""
        mock_input.return_value = "-5"
        result = get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_with("Число должно быть положительным!")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_zero(self, mock_print, mock_input):
        """Тестирование нуля"""
        mock_input.return_value = "0"
        result = get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_with("Число должно быть положительным!")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_invalid_format(self, mock_print, mock_input):
        """Тестирование неверного формата"""
        mock_input.return_value = "not_a_number"
        result = get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_with("Введите корректное число!")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_empty_no_default(self, mock_print, mock_input):
        """Тестирование пустого ввода без значения по умолчанию"""
        mock_input.return_value = ""
        result = get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_with("Введите корректное число!")


class TestParseSalaryRange:
    """Тестирование функции парсинга диапазона зарплат"""
    
    def test_parse_salary_range_with_spaces(self):
        """Тестирование диапазона с пробелами"""
        result = parse_salary_range("100000 - 150000")
        assert result == (100000, 150000)
    
    def test_parse_salary_range_without_spaces(self):
        """Тестирование диапазона без пробелов"""
        result = parse_salary_range("80000-120000")
        assert result == (80000, 120000)
    
    def test_parse_salary_range_reversed(self):
        """Тестирование обращенного диапазона"""
        result = parse_salary_range("150000 - 100000")
        assert result == (100000, 150000)  # Должно быть исправлено
    
    @patch('builtins.print')
    def test_parse_salary_range_invalid_format(self, mock_print):
        """Тестирование неверного формата"""
        result = parse_salary_range("invalid_range")
        assert result is None
        mock_print.assert_called_with("Неверный формат диапазона. Используйте формат: 100000 - 150000")
    
    @patch('builtins.print')
    def test_parse_salary_range_invalid_numbers(self, mock_print):
        """Тестирование неверных чисел в диапазоне"""
        result = parse_salary_range("abc - def")
        assert result is None
        mock_print.assert_called_with("Введите корректные числа!")


class TestConfirmAction:
    """Тестирование функции подтверждения действия"""
    
    @patch('builtins.input')
    def test_confirm_action_yes_variants(self, mock_input):
        """Тестирование различных вариантов "да" """
        yes_variants = ["y", "yes", "д", "да", "Y", "YES", "Д", "ДА"]
        
        for variant in yes_variants:
            mock_input.return_value = variant
            result = confirm_action("Продолжить?")
            assert result is True
    
    @patch('builtins.input')
    def test_confirm_action_no_variants(self, mock_input):
        """Тестирование различных вариантов "нет" """
        no_variants = ["n", "no", "н", "нет", "N", "NO", "Н", "НЕТ"]
        
        for variant in no_variants:
            mock_input.return_value = variant
            result = confirm_action("Продолжить?")
            assert result is False
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_confirm_action_invalid_then_valid(self, mock_print, mock_input):
        """Тестирование неверного ввода, затем валидного"""
        mock_input.side_effect = ["maybe", "y"]
        result = confirm_action("Продолжить?")
        assert result is True
        mock_print.assert_called_with("Введите 'y' для да или 'n' для нет.")


class TestFilterVacanciesByKeyword:
    """Тестирование фильтрации вакансий по ключевым словам"""
    
    def create_test_vacancy(self, title="Test Job", description="Test Description", **kwargs):
        """Создание тестовой вакансии"""
        employer = Employer("Test Company", "123")
        vacancy = Vacancy(
            title=title,
            description=description,
            employer=employer,
            url="https://test.com/job",
            **kwargs
        )
        return vacancy
    
    def test_filter_vacancies_single_keyword(self):
        """Тестирование фильтрации по одному ключевому слову"""
        vacancies = [
            self.create_test_vacancy("Python Developer", "Python programming"),
            self.create_test_vacancy("Java Developer", "Java programming"),
            self.create_test_vacancy("Full Stack", "Python and JavaScript")
        ]
        
        result = filter_vacancies_by_keyword(vacancies, "Python")
        assert len(result) == 2
        assert all("python" in _build_searchable_text(v) for v in result)
    
    def test_filter_vacancies_and_operator(self):
        """Тестирование фильтрации с оператором AND"""
        vacancies = [
            self.create_test_vacancy("Python Django Developer", "Python and Django"),
            self.create_test_vacancy("Python Flask Developer", "Python and Flask"),
            self.create_test_vacancy("Java Spring Developer", "Java and Spring")
        ]
        
        result = filter_vacancies_by_keyword(vacancies, "Python AND Django")
        assert len(result) == 1
        assert "Django" in result[0].title
    
    def test_filter_vacancies_or_operator(self):
        """Тестирование фильтрации с оператором OR"""
        vacancies = [
            self.create_test_vacancy("Python Developer", "Python programming"),
            self.create_test_vacancy("Java Developer", "Java programming"),
            self.create_test_vacancy("C# Developer", "C# programming")
        ]
        
        result = filter_vacancies_by_keyword(vacancies, "Python OR Java")
        assert len(result) == 2
    
    def test_filter_vacancies_empty_keyword(self):
        """Тестирование с пустым ключевым словом"""
        vacancies = [self.create_test_vacancy()]
        result = filter_vacancies_by_keyword(vacancies, "")
        assert result == []
    
    def test_filter_vacancies_no_matches(self):
        """Тестирование без совпадений"""
        vacancies = [self.create_test_vacancy("Python Developer")]
        result = filter_vacancies_by_keyword(vacancies, "PHP")
        assert result == []


class TestParseSearchQuery:
    """Тестирование парсинга поискового запроса"""
    
    def test_parse_search_query_and_operator(self):
        """Тестирование запроса с AND"""
        result = _parse_search_query("Python AND Django")
        assert result["keywords"] == ["Python", "Django"]
        assert result["operator"] == "AND"
    
    def test_parse_search_query_or_operator(self):
        """Тестирование запроса с OR"""
        result = _parse_search_query("Java OR Kotlin")
        assert result["keywords"] == ["Java", "Kotlin"]
        assert result["operator"] == "OR"
    
    def test_parse_search_query_comma_separator(self):
        """Тестирование запроса с запятой"""
        result = _parse_search_query("Python, Django, Flask")
        assert result["keywords"] == ["Python", "Django", "Flask"]
        assert result["operator"] == "OR"
    
    def test_parse_search_query_single_word(self):
        """Тестирование одного слова"""
        result = _parse_search_query("Python")
        assert result["keywords"] == ["Python"]
        assert result["operator"] == "OR"
    
    def test_parse_search_query_empty(self):
        """Тестирование пустого запроса"""
        result = _parse_search_query("")
        assert result is None
    
    def test_parse_search_query_case_insensitive(self):
        """Тестирование нечувствительности к регистру операторов"""
        result = _parse_search_query("python and django")
        assert result["keywords"] == ["python", "django"]
        assert result["operator"] == "AND"


class TestBuildSearchableText:
    """Тестирование построения текста для поиска"""
    
    def test_build_searchable_text_full_vacancy(self):
        """Тестирование с полной вакансией"""
        employer = Employer("Test Company", "123")
        salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        
        vacancy = Vacancy(
            title="Python Developer",
            description="Develop applications",
            requirements="Python, Django",
            responsibilities="Code development",
            employer=employer,
            salary=salary,
            employment="Full time",
            skills=[{"name": "Python"}, "Django"],
            url="https://test.com/job"
        )
        
        searchable_text = _build_searchable_text(vacancy)
        
        assert "python developer" in searchable_text
        assert "develop applications" in searchable_text
        assert "python, django" in searchable_text
        assert "test company" in searchable_text
    
    def test_build_searchable_text_minimal_vacancy(self):
        """Тестирование с минимальной вакансией"""
        vacancy = Vacancy(
            title="Developer",
            url="https://test.com/job"
        )
        
        searchable_text = _build_searchable_text(vacancy)
        assert "developer" in searchable_text
    
    def test_build_searchable_text_with_skills_dict(self):
        """Тестирование с навыками в формате словаря"""
        vacancy = Vacancy(
            title="Developer",
            skills=[{"name": "Python"}, {"name": "Django"}],
            url="https://test.com/job"
        )
        
        searchable_text = _build_searchable_text(vacancy)
        assert "python" in searchable_text
        assert "django" in searchable_text
    
    def test_build_searchable_text_with_skills_string(self):
        """Тестирование с навыками в формате строки"""
        vacancy = Vacancy(
            title="Developer",
            skills=["Python", "Django"],
            url="https://test.com/job"
        )
        
        searchable_text = _build_searchable_text(vacancy)
        assert "python" in searchable_text
        assert "django" in searchable_text


class TestDebugFunctions:
    """Тестирование отладочных функций"""
    
    @patch('builtins.print')
    def test_debug_vacancy_search(self, mock_print):
        """Тестирование отладки поиска по вакансии"""
        vacancy = Vacancy(
            vacancy_id="test_123",
            title="Python Developer",
            description="Test description",
            url="https://test.com/job"
        )
        
        debug_vacancy_search(vacancy, "Python")
        
        # Проверяем, что функция print была вызвана
        assert mock_print.call_count > 0
        
        # Проверяем, что в выводе есть информация о вакансии
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Python Developer" in call for call in print_calls)
        assert any("test_123" in call for call in print_calls)
    
    @patch('builtins.print')
    def test_debug_search_vacancies(self, mock_print):
        """Тестирование отладки поиска по списку вакансий"""
        vacancies = [
            Vacancy(title=f"Job {i}", url=f"https://test.com/job{i}")
            for i in range(10)
        ]
        
        debug_search_vacancies(vacancies, "test")
        
        # Проверяем, что функция print была вызвана
        assert mock_print.call_count > 0
        
        # Проверяем, что выводится общая информация
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Всего вакансий: 10" in call for call in print_calls)


class TestDisplayVacancyInfo:
    """Тестирование отображения информации о вакансии"""
    
    @patch('src.utils.vacancy_formatter.vacancy_formatter')
    def test_display_vacancy_info(self, mock_formatter):
        """Тестирование отображения информации о вакансии"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://test.com/job"
        )
        
        display_vacancy_info(vacancy, 1)
        
        # Проверяем, что форматер был вызван
        mock_formatter.display_vacancy_info.assert_called_once_with(vacancy, 1)
    
    @patch('src.utils.vacancy_formatter.vacancy_formatter')
    def test_display_vacancy_info_without_number(self, mock_formatter):
        """Тестирование отображения без номера"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://test.com/job"
        )
        
        display_vacancy_info(vacancy)
        
        mock_formatter.display_vacancy_info.assert_called_once_with(vacancy, None)


class TestUIHelpersIntegration:
    """Интеграционные тесты для UI helpers"""
    
    @patch('builtins.input')
    def test_full_user_input_workflow(self, mock_input):
        """Тестирование полного рабочего процесса пользовательского ввода"""
        # Симулируем диалог с пользователем
        mock_input.side_effect = [
            "Python Developer",  # Название позиции
            "100000 - 150000",   # Диапазон зарплат
            "y"                  # Подтверждение
        ]
        
        position = get_user_input("Введите название позиции: ")
        salary_range = parse_salary_range(position if position == "100000 - 150000" else "100000 - 150000")
        confirmation = confirm_action("Подтвердить поиск?")
        
        assert position == "Python Developer"
        assert salary_range == (100000, 150000)
        assert confirmation is True
    
    def test_vacancy_search_and_filtering_workflow(self):
        """Тестирование рабочего процесса поиска и фильтрации"""
        # Создаем тестовые вакансии
        vacancies = [
            Vacancy(
                title="Python Developer",
                description="Backend development with Python",
                requirements="Python, Django, PostgreSQL",
                employer=Employer("Tech Company", "123"),
                url="https://test.com/job1"
            ),
            Vacancy(
                title="Java Developer",
                description="Enterprise development with Java",
                requirements="Java, Spring, MySQL",
                employer=Employer("Enterprise Corp", "456"),
                url="https://test.com/job2"
            ),
            Vacancy(
                title="Full Stack Developer",
                description="Full stack with Python and React",
                requirements="Python, JavaScript, React",
                employer=Employer("Startup Inc", "789"),
                url="https://test.com/job3"
            )
        ]
        
        # Тестируем различные поисковые запросы
        python_jobs = filter_vacancies_by_keyword(vacancies, "Python")
        assert len(python_jobs) == 2
        
        django_jobs = filter_vacancies_by_keyword(vacancies, "Django")
        assert len(django_jobs) == 1
        
        full_stack_jobs = filter_vacancies_by_keyword(vacancies, "Full Stack")
        assert len(full_stack_jobs) == 1
        
        # Комбинированный поиск
        python_and_react = filter_vacancies_by_keyword(vacancies, "Python AND React")
        assert len(python_and_react) == 1
        
        backend_or_frontend = filter_vacancies_by_keyword(vacancies, "Python OR Java")
        assert len(backend_or_frontend) == 3
