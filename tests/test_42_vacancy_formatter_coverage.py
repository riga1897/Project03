#!/usr/bin/env python3
"""
Тесты модуля vacancy_formatter.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций 
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Тестирование класса VacancyFormatter и всех его методов

Модуль содержит:
- 1 класс VacancyFormatter с 20+ методами форматирования
- Методы извлечения данных из объектов вакансий
- Методы форматирования различных типов данных
- Статические методы для отображения
- Глобальный экземпляр vacancy_formatter
"""

import pytest
from unittest.mock import patch, MagicMock
import re

from src.utils.vacancy_formatter import VacancyFormatter, vacancy_formatter


class MockVacancy:
    """Мок-объект вакансии для тестирования"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockEmployer:
    """Мок-объект работодателя"""
    
    def __init__(self, name=None, has_get_name=False):
        self.name = name
        self._has_get_name = has_get_name
    
    def get_name(self):
        return self.name if self._has_get_name else None
    
    def __str__(self):
        return self.name or "Unknown"


class MockSalary:
    """Мок-объект зарплаты"""
    
    def __init__(self, salary_str="100000-150000 руб."):
        self._str = salary_str
    
    def __str__(self):
        return self._str


class MockExperience:
    """Мок-объект опыта работы"""
    
    def __init__(self, name=None, has_get_name=False):
        self.name = name
        self._has_get_name = has_get_name
    
    def get_name(self):
        return self.name if self._has_get_name else None
    
    def __str__(self):
        return self.name or "Unknown"


class TestVacancyFormatter:
    """100% покрытие класса VacancyFormatter"""

    def test_init(self):
        """Покрытие: инициализация форматировщика"""
        formatter = VacancyFormatter()
        assert isinstance(formatter, VacancyFormatter)

    def test_format_vacancy_info_basic(self):
        """Покрытие: базовое форматирование информации о вакансии"""
        formatter = VacancyFormatter()
        vacancy = MockVacancy(
            vacancy_id="123",
            title="Python Developer",
            area="Москва",
            source="HeadHunter"
        )
        
        result = formatter.format_vacancy_info(vacancy, 1)
        
        assert "1." in result
        assert "ID: 123" in result
        assert "Название: Python Developer" in result
        assert "Регион: Москва" in result
        assert "Источник: HeadHunter" in result

    def test_format_vacancy_info_no_number(self):
        """Покрытие: форматирование без номера"""
        formatter = VacancyFormatter()
        vacancy = MockVacancy(title="Developer")
        
        result = formatter.format_vacancy_info(vacancy)
        
        assert "1." not in result
        assert "Название: Developer" in result

    def test_build_vacancy_lines_id_alternatives(self):
        """Покрытие: различные варианты ID (vacancy_id vs id)"""
        formatter = VacancyFormatter()
        
        # Тест с vacancy_id
        vacancy1 = MockVacancy(vacancy_id="123")
        lines1 = formatter._build_vacancy_lines(vacancy1)
        assert "ID: 123" in lines1
        
        # Тест с id (fallback)
        vacancy2 = MockVacancy(id="456")
        lines2 = formatter._build_vacancy_lines(vacancy2)
        assert "ID: 456" in lines2
        
        # Тест без ID
        vacancy3 = MockVacancy()
        lines3 = formatter._build_vacancy_lines(vacancy3)
        assert not any("ID:" in line for line in lines3)

    def test_build_vacancy_lines_title_alternatives(self):
        """Покрытие: различные варианты названия (title vs name)"""
        formatter = VacancyFormatter()
        
        # Тест с title
        vacancy1 = MockVacancy(title="Senior Developer")
        lines1 = formatter._build_vacancy_lines(vacancy1)
        assert "Название: Senior Developer" in lines1
        
        # Тест с name (fallback)
        vacancy2 = MockVacancy(name="Junior Developer")
        lines2 = formatter._build_vacancy_lines(vacancy2)
        assert "Название: Junior Developer" in lines2

    def test_build_vacancy_lines_company_filtering(self):
        """Покрытие: фильтрация компании 'Не указана'"""
        formatter = VacancyFormatter()
        
        # Компания указана
        employer = MockEmployer("Яндекс")
        vacancy1 = MockVacancy(employer=employer)
        lines1 = formatter._build_vacancy_lines(vacancy1)
        assert "Компания: Яндекс" in lines1
        
        # Компания "Не указана" - не должна показываться
        with patch.object(formatter, '_extract_company_name', return_value="Не указана"):
            vacancy2 = MockVacancy()
            lines2 = formatter._build_vacancy_lines(vacancy2)
            assert not any("Компания:" in line for line in lines2)

    def test_build_vacancy_lines_experience_employment(self):
        """Покрытие: опыт и занятость"""
        formatter = VacancyFormatter()
        
        experience = MockExperience("от 3 лет")
        employment = MockExperience("полная занятость")
        vacancy = MockVacancy(
            experience=experience,
            employment=employment
        )
        
        with patch.object(formatter, 'format_experience', return_value="от 3 лет"):
            with patch.object(formatter, 'format_employment_type', return_value="полная занятость"):
                lines = formatter._build_vacancy_lines(vacancy)
        
        assert "Опыт: от 3 лет" in lines
        assert "Занятость: полная занятость" in lines

    def test_build_vacancy_lines_url_alternatives(self):
        """Покрытие: различные варианты URL (url vs alternate_url)"""
        formatter = VacancyFormatter()
        
        # Тест с url
        vacancy1 = MockVacancy(url="https://example.com/job1")
        lines1 = formatter._build_vacancy_lines(vacancy1)
        assert "Ссылка: https://example.com/job1" in lines1
        
        # Тест с alternate_url (fallback)
        vacancy2 = MockVacancy(alternate_url="https://example.com/job2")
        lines2 = formatter._build_vacancy_lines(vacancy2)
        assert "Ссылка: https://example.com/job2" in lines2

    @patch('src.utils.vacancy_formatter.logger')
    def test_build_vacancy_lines_debug_logging(self, mock_logger):
        """Покрытие: debug логирование для отсутствующих полей"""
        formatter = VacancyFormatter()
        vacancy = MockVacancy(vacancy_id="test123")
        
        # Мокируем методы извлечения чтобы они возвращали None
        with patch.object(formatter, '_extract_requirements', return_value=None):
            with patch.object(formatter, '_extract_responsibilities', return_value=None):
                with patch.object(formatter, '_extract_description', return_value=None):
                    lines = formatter._build_vacancy_lines(vacancy)
        
        # Проверяем что были вызовы debug логирования
        assert mock_logger.debug.call_count >= 2  # Минимум 2 вызова для requirements и responsibilities

    def test_build_vacancy_lines_text_formatting(self):
        """Покрытие: форматирование текстовых полей с ограничениями"""
        formatter = VacancyFormatter()
        
        long_req = "Python Django Flask " * 20  # Длинные требования
        long_resp = "Разработка поддержка " * 20  # Длинные обязанности
        long_desc = "Описание вакансии " * 30  # Длинное описание
        
        vacancy = MockVacancy()
        
        with patch.object(formatter, '_extract_requirements', return_value=long_req):
            with patch.object(formatter, '_extract_responsibilities', return_value=long_resp):
                with patch.object(formatter, '_extract_description', return_value=long_desc):
                    with patch.object(formatter, 'format_text') as mock_format:
                        mock_format.side_effect = lambda text, limit: f"formatted:{limit}"
                        lines = formatter._build_vacancy_lines(vacancy)
        
        # Проверяем что format_text вызывался с правильными лимитами
        calls = mock_format.call_args_list
        limits = [call[0][1] for call in calls if len(call[0]) > 1]
        assert 200 in limits  # requirements limit
        assert 200 in limits  # responsibilities limit  
        assert 250 in limits  # description limit

    def test_build_vacancy_lines_conditions(self):
        """Покрытие: извлечение и форматирование условий"""
        formatter = VacancyFormatter()
        vacancy = MockVacancy()
        
        with patch.object(formatter, '_extract_conditions', return_value="Удаленная работа, гибкий график"):
            with patch.object(formatter, 'format_text', return_value="formatted_conditions"):
                lines = formatter._build_vacancy_lines(vacancy)
        
        assert "Условия: formatted_conditions" in lines

    def test_extract_company_name_get_name_method(self):
        """Покрытие: извлечение названия компании с методом get_name()"""
        formatter = VacancyFormatter()
        
        # Тест с методом get_name()
        employer = MockEmployer("Яндекс", has_get_name=True)
        vacancy = MockVacancy(employer=employer)
        result = formatter._extract_company_name(vacancy)
        assert result == "Яндекс"

    def test_extract_company_name_name_attribute(self):
        """Покрытие: извлечение названия компании через атрибут name"""
        formatter = VacancyFormatter()
        
        # Тест с атрибутом name (но без get_name)
        employer = MockEmployer("Google")
        vacancy = MockVacancy(employer=employer)
        result = formatter._extract_company_name(vacancy)
        assert result == "Google"

    def test_extract_company_name_fallback(self):
        """Покрытие: fallback для извлечения названия компании"""
        formatter = VacancyFormatter()
        
        # Тест со строковым employer
        vacancy = MockVacancy(employer="Microsoft")
        result = formatter._extract_company_name(vacancy)
        assert result == "Microsoft"

    def test_extract_company_name_no_employer(self):
        """Покрытие: отсутствующий employer"""
        formatter = VacancyFormatter()
        
        vacancy = MockVacancy()  # Без employer
        result = formatter._extract_company_name(vacancy)
        assert result == "Не указана"

    def test_extract_salary_info(self):
        """Покрытие: извлечение информации о зарплате"""
        formatter = VacancyFormatter()
        
        # С зарплатой
        salary = MockSalary("100000-150000 руб.")
        vacancy = MockVacancy(salary=salary)
        
        with patch.object(formatter, 'format_salary', return_value="100000-150000 руб.") as mock_format:
            result = formatter._extract_salary_info(vacancy)
            assert result == "100000-150000 руб."
            mock_format.assert_called_once_with(salary)

    def test_extract_salary_info_no_salary(self):
        """Покрытие: отсутствующая зарплата"""
        formatter = VacancyFormatter()
        
        vacancy = MockVacancy()  # Без salary
        result = formatter._extract_salary_info(vacancy)
        assert result == "Не указана"

    def test_extract_description(self):
        """Покрытие: извлечение описания вакансии"""
        formatter = VacancyFormatter()
        
        vacancy = MockVacancy(description="Интересная работа в IT")
        result = formatter._extract_description(vacancy)
        assert result == "Интересная работа в IT"

    def test_extract_responsibilities_direct_field(self):
        """Покрытие: извлечение обязанностей из прямого поля"""
        formatter = VacancyFormatter()
        
        vacancy = MockVacancy(responsibilities="Разработка приложений")
        result = formatter._extract_responsibilities(vacancy)
        assert result == "Разработка приложений"

    def test_extract_responsibilities_empty_direct_field(self):
        """Покрытие: пустое прямое поле обязанностей, извлечение из snippet"""
        formatter = VacancyFormatter()
        
        # Тест с dict snippet
        snippet_dict = {"responsibility": "Работа с командой"}
        vacancy1 = MockVacancy(responsibilities="", snippet=snippet_dict)
        result1 = formatter._extract_responsibilities(vacancy1)
        assert result1 == "Работа с командой"
        
        # Тест с объектом snippet
        snippet_obj = MagicMock()
        snippet_obj.responsibility = "Code review"
        vacancy2 = MockVacancy(responsibilities=None, snippet=snippet_obj)
        result2 = formatter._extract_responsibilities(vacancy2)
        assert result2 == "Code review"

    def test_extract_responsibilities_whitespace_handling(self):
        """Покрытие: обработка пробелов в обязанностях"""
        formatter = VacancyFormatter()
        
        # Тест с пробелами по краям
        vacancy = MockVacancy(responsibilities="  Тестирование ПО  ")
        result = formatter._extract_responsibilities(vacancy)
        assert result == "Тестирование ПО"
        
        # Тест с пустой строкой после strip
        vacancy2 = MockVacancy(responsibilities="   ")
        result2 = formatter._extract_responsibilities(vacancy2)
        assert result2 is None

    def test_extract_requirements_direct_field(self):
        """Покрытие: извлечение требований из прямого поля"""
        formatter = VacancyFormatter()
        
        vacancy = MockVacancy(requirements="Python, Django, PostgreSQL")
        result = formatter._extract_requirements(vacancy)
        assert result == "Python, Django, PostgreSQL"

    def test_extract_requirements_from_snippet(self):
        """Покрытие: извлечение требований из snippet"""
        formatter = VacancyFormatter()
        
        # Тест с dict snippet
        snippet_dict = {"requirement": "JavaScript, React"}
        vacancy1 = MockVacancy(requirements="", snippet=snippet_dict)
        result1 = formatter._extract_requirements(vacancy1)
        assert result1 == "JavaScript, React"
        
        # Тест с объектом snippet
        snippet_obj = MagicMock()
        snippet_obj.requirement = "Go, Kubernetes"
        vacancy2 = MockVacancy(requirements=None, snippet=snippet_obj)
        result2 = formatter._extract_requirements(vacancy2)
        assert result2 == "Go, Kubernetes"

    def test_extract_requirements_whitespace_handling(self):
        """Покрытие: обработка пробелов в требованиях"""
        formatter = VacancyFormatter()
        
        # Пустая строка после обработки
        vacancy = MockVacancy(requirements="   ")
        result = formatter._extract_requirements(vacancy)
        assert result is None

    def test_extract_conditions(self):
        """Покрытие: извлечение условий работы"""
        formatter = VacancyFormatter()
        
        # Прямое поле conditions
        vacancy1 = MockVacancy(conditions="Удаленная работа")
        result1 = formatter._extract_conditions(vacancy1)
        assert result1 == "Удаленная работа"
        
        # Fallback на schedule
        schedule = MockExperience("полный день")
        vacancy2 = MockVacancy(schedule=schedule)
        
        with patch.object(formatter, 'format_schedule', return_value="полный день"):
            result2 = formatter._extract_conditions(vacancy2)
            assert result2 == "График: полный день"
        
        # Нет условий
        vacancy3 = MockVacancy()
        result3 = formatter._extract_conditions(vacancy3)
        assert result3 is None

    def test_format_salary_none(self):
        """Покрытие: форматирование None зарплаты"""
        formatter = VacancyFormatter()
        
        result = formatter.format_salary(None)
        assert result == "Не указана"

    @patch('src.utils.vacancy_formatter.Salary')
    def test_format_salary_dict_import_success(self, mock_salary_class):
        """Покрытие: форматирование словаря зарплаты с успешным импортом"""
        formatter = VacancyFormatter()
        
        # Мокируем класс Salary
        mock_salary_instance = MagicMock()
        mock_salary_instance.__str__ = MagicMock(return_value="50000-80000 руб.")
        mock_salary_class.return_value = mock_salary_instance
        
        salary_dict = {"from": 50000, "to": 80000, "currency": "RUR"}
        result = formatter.format_salary(salary_dict)
        
        mock_salary_class.assert_called_once_with(salary_dict)
        assert result == "50000-80000 руб."

    def test_format_salary_dict_import_error(self):
        """Покрытие: форматирование словаря зарплаты с ошибкой импорта"""
        formatter = VacancyFormatter()
        
        # Мокируем ImportError при первом импорте
        with patch('src.utils.vacancy_formatter.Salary', side_effect=ImportError):
            # Мокируем успешный второй импорт
            with patch('builtins.__import__') as mock_import:
                mock_salary_module = MagicMock()
                mock_salary_class = MagicMock()
                mock_salary_instance = MagicMock()
                mock_salary_instance.__str__ = MagicMock(return_value="60000 руб.")
                mock_salary_class.return_value = mock_salary_instance
                mock_salary_module.Salary = mock_salary_class
                mock_import.return_value = mock_salary_module
                
                salary_dict = {"from": 60000}
                result = formatter.format_salary(salary_dict)
                assert result == "60000 руб."

    def test_format_salary_object(self):
        """Покрытие: форматирование объекта зарплаты"""
        formatter = VacancyFormatter()
        
        salary_obj = MockSalary("70000-90000 руб.")
        result = formatter.format_salary(salary_obj)
        assert result == "70000-90000 руб."

    def test_format_currency(self):
        """Покрытие: форматирование валюты"""
        formatter = VacancyFormatter()
        
        assert formatter.format_currency("RUR") == "руб."
        assert formatter.format_currency("RUB") == "руб."
        assert formatter.format_currency("USD") == "долл."
        assert formatter.format_currency("EUR") == "евро"
        assert formatter.format_currency("GBP") == "GBP"  # Неизвестная валюта

    def test_format_text_empty(self):
        """Покрытие: форматирование пустого текста"""
        formatter = VacancyFormatter()
        
        assert formatter.format_text("") == "Не указано"
        assert formatter.format_text(None) == "Не указано"

    def test_format_text_with_html(self):
        """Покрытие: форматирование текста с HTML тегами"""
        formatter = VacancyFormatter()
        
        with patch.object(formatter, 'clean_html_tags', return_value="Чистый текст"):
            result = formatter.format_text("<p>HTML текст</p>", 50)
            assert result == "Чистый текст"

    def test_format_text_truncation(self):
        """Покрытие: усечение длинного текста"""
        formatter = VacancyFormatter()
        
        long_text = "Очень длинный текст который должен быть усечен" * 10
        with patch.object(formatter, 'clean_html_tags', return_value=long_text):
            result = formatter.format_text(long_text, 50)
            assert result.endswith("...")
            assert len(result) == 53  # 50 символов + "..."

    def test_format_text_no_truncation(self):
        """Покрытие: короткий текст без усечения"""
        formatter = VacancyFormatter()
        
        short_text = "Короткий текст"
        with patch.object(formatter, 'clean_html_tags', return_value=short_text):
            result = formatter.format_text(short_text, 50)
            assert result == short_text
            assert not result.endswith("...")

    def test_format_date_empty(self):
        """Покрытие: форматирование пустой даты"""
        formatter = VacancyFormatter()
        
        assert formatter.format_date("") == "Не указано"
        assert formatter.format_date(None) == "Не указано"

    def test_format_date_iso_format(self):
        """Покрытие: форматирование ISO даты"""
        formatter = VacancyFormatter()
        
        # Полная ISO дата с временем
        result1 = formatter.format_date("2023-12-25T10:30:00Z")
        assert result1 == "25.12.2023"
        
        # Дата без времени но с T
        result2 = formatter.format_date("2023-01-15T00:00:00")
        assert result2 == "15.01.2023"

    def test_format_date_invalid_format(self):
        """Покрытие: некорректный формат даты"""
        formatter = VacancyFormatter()
        
        # Не ISO формат - возвращается как есть
        result = formatter.format_date("25.12.2023")
        assert result == "25.12.2023"
        
        # Некорректная дата
        result2 = formatter.format_date("invalid-date")
        assert result2 == "invalid-date"

    def test_format_date_exception_handling(self):
        """Покрытие: обработка исключений при форматировании даты"""
        formatter = VacancyFormatter()
        
        # Тест на исключение в блоке try
        with patch('src.utils.vacancy_formatter.VacancyFormatter.format_date') as mock_method:
            # Сначала мокируем чтобы вызвать исключение, потом возвращаем исходное
            mock_method.side_effect = [Exception("Test error"), "fallback-date"]
            
            # Создаем новый экземпляр чтобы вызвать реальный метод
            real_formatter = VacancyFormatter()
            result = real_formatter.format_date("2023T13-45")  # Некорректная дата
            assert result == "2023T13-45"

    def test_format_experience_none(self):
        """Покрытие: форматирование None опыта"""
        formatter = VacancyFormatter()
        
        result = formatter.format_experience(None)
        assert result == "Не указан"

    def test_format_experience_with_get_name(self):
        """Покрытие: форматирование опыта с методом get_name()"""
        formatter = VacancyFormatter()
        
        experience = MockExperience("от 3 до 6 лет", has_get_name=True)
        result = formatter.format_experience(experience)
        assert result == "от 3 до 6 лет"

    def test_format_experience_fallback(self):
        """Покрытие: fallback для форматирования опыта"""
        formatter = VacancyFormatter()
        
        # Без метода get_name - используется str()
        experience = MockExperience("1-3 года")
        result = formatter.format_experience(experience)
        assert result == "1-3 года"

    def test_format_employment_type_none(self):
        """Покрытие: форматирование None занятости"""
        formatter = VacancyFormatter()
        
        result = formatter.format_employment_type(None)
        assert result == "Не указан"

    def test_format_employment_type_with_get_name(self):
        """Покрытие: форматирование занятости с методом get_name()"""
        formatter = VacancyFormatter()
        
        employment = MockExperience("полная занятость", has_get_name=True)
        result = formatter.format_employment_type(employment)
        assert result == "полная занятость"

    def test_format_employment_type_fallback(self):
        """Покрытие: fallback для форматирования занятости"""
        formatter = VacancyFormatter()
        
        employment = MockExperience("частичная занятость")
        result = formatter.format_employment_type(employment)
        assert result == "частичная занятость"

    def test_format_schedule_none(self):
        """Покрытие: форматирование None графика"""
        formatter = VacancyFormatter()
        
        result = formatter.format_schedule(None)
        assert result == "Не указан"

    def test_format_schedule_with_get_name(self):
        """Покрытие: форматирование графика с методом get_name()"""
        formatter = VacancyFormatter()
        
        schedule = MockExperience("полный день", has_get_name=True)
        result = formatter.format_schedule(schedule)
        assert result == "полный день"

    def test_format_schedule_with_name_attribute(self):
        """Покрытие: форматирование графика через атрибут name"""
        formatter = VacancyFormatter()
        
        schedule = MockExperience("гибкий график")
        result = formatter.format_schedule(schedule)
        assert result == "гибкий график"

    def test_format_schedule_fallback(self):
        """Покрытие: fallback для форматирования графика"""
        formatter = VacancyFormatter()
        
        result = formatter.format_schedule("удаленная работа")
        assert result == "удаленная работа"

    def test_format_company_name_none(self):
        """Покрытие: форматирование None компании"""
        formatter = VacancyFormatter()
        
        result = formatter.format_company_name(None)
        assert result == "Не указана"

    def test_format_company_name_dict(self):
        """Покрытие: форматирование компании из словаря"""
        formatter = VacancyFormatter()
        
        company_dict = {"name": "Тинькофф Банк"}
        result = formatter.format_company_name(company_dict)
        assert result == "Тинькофф Банк"
        
        # Словарь без name
        empty_dict = {}
        result2 = formatter.format_company_name(empty_dict)
        assert result2 == "Не указана"

    def test_format_company_name_string(self):
        """Покрытие: форматирование компании из строки"""
        formatter = VacancyFormatter()
        
        result = formatter.format_company_name("Сбербанк")
        assert result == "Сбербанк"

    def test_clean_html_tags_empty(self):
        """Покрытие: очистка HTML из пустого текста"""
        formatter = VacancyFormatter()
        
        assert formatter.clean_html_tags("") == ""
        assert formatter.clean_html_tags(None) == ""

    def test_clean_html_tags_with_html(self):
        """Покрытие: очистка HTML тегов"""
        formatter = VacancyFormatter()
        
        html_text = "<p>Текст с <strong>HTML</strong> тегами</p>"
        result = formatter.clean_html_tags(html_text)
        
        assert "<p>" not in result
        assert "<strong>" not in result
        assert "Текст с HTML тегами" in result

    def test_clean_html_tags_whitespace_cleanup(self):
        """Покрытие: очистка множественных пробелов"""
        formatter = VacancyFormatter()
        
        messy_text = "Текст   с    множественными     пробелами"
        result = formatter.clean_html_tags(messy_text)
        
        assert "   " not in result
        assert result == "Текст с множественными пробелами"

    def test_clean_html_tags_strip(self):
        """Покрытие: удаление пробелов по краям"""
        formatter = VacancyFormatter()
        
        text_with_spaces = "   Текст с пробелами по краям   "
        result = formatter.clean_html_tags(text_with_spaces)
        
        assert result == "Текст с пробелами по краям"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_format_number_valid_numbers(self):
        """Покрытие: форматирование валидных чисел"""
        formatter = VacancyFormatter()
        
        assert formatter.format_number(1000) == "1 000"
        assert formatter.format_number(1000000) == "1 000 000"
        assert formatter.format_number(1500.5) == "1 500.5"

    def test_format_number_invalid_input(self):
        """Покрытие: форматирование невалидного ввода"""
        formatter = VacancyFormatter()
        
        assert formatter.format_number("строка") == "строка"
        assert formatter.format_number(None) == "None"
        assert formatter.format_number([1, 2, 3]) == "[1, 2, 3]"

    @patch('builtins.print')
    def test_display_vacancy_info_static(self, mock_print):
        """Покрытие: статический метод отображения информации о вакансии"""
        vacancy = MockVacancy(title="Test Job")
        
        VacancyFormatter.display_vacancy_info(vacancy, 1)
        
        mock_print.assert_called_once()
        # Проверяем что print был вызван с отформатированной строкой
        printed_text = mock_print.call_args[0][0]
        assert "Название: Test Job" in printed_text

    def test_format_vacancy_brief_static(self):
        """Покрытие: статический метод краткого форматирования"""
        vacancy = MockVacancy(
            title="Brief Job",
            area="СПб",
            url="https://example.com"
        )
        
        result = VacancyFormatter.format_vacancy_brief(vacancy, 1)
        
        expected_parts = ["1.", "Brief Job", "Регион: СПб", "Ссылка: https://example.com"]
        for part in expected_parts:
            assert part in result
        
        # Проверяем что части разделены " | "
        assert " | " in result

    def test_format_vacancy_brief_no_number(self):
        """Покрытие: краткое форматирование без номера"""
        vacancy = MockVacancy(title="No Number Job")
        
        result = VacancyFormatter.format_vacancy_brief(vacancy)
        
        assert "1." not in result
        assert "No Number Job" in result

    def test_format_vacancy_brief_title_alternatives(self):
        """Покрытие: краткое форматирование с различными полями названия"""
        # С title
        vacancy1 = MockVacancy(title="Title Job")
        result1 = VacancyFormatter.format_vacancy_brief(vacancy1)
        assert "Title Job" in result1
        
        # С name (fallback)
        vacancy2 = MockVacancy(name="Name Job")
        result2 = VacancyFormatter.format_vacancy_brief(vacancy2)
        assert "Name Job" in result2

    def test_format_vacancy_brief_company_filtering(self):
        """Покрытие: фильтрация компании в кратком формате"""
        formatter = VacancyFormatter()
        vacancy = MockVacancy(title="Job")
        
        # Компания "Не указана" не должна показываться
        with patch.object(formatter, '_extract_company_name', return_value="Не указана"):
            result = VacancyFormatter.format_vacancy_brief(vacancy)
            assert "Компания:" not in result


class TestVacancyFormatterGlobalInstance:
    """Покрытие глобального экземпляра vacancy_formatter"""

    def test_global_instance_exists(self):
        """Покрытие: проверка существования глобального экземпляра"""
        assert vacancy_formatter is not None
        assert isinstance(vacancy_formatter, VacancyFormatter)

    def test_global_instance_functionality(self):
        """Покрытие: функциональность глобального экземпляра"""
        vacancy = MockVacancy(title="Global Test")
        
        result = vacancy_formatter.format_vacancy_info(vacancy)
        assert "Название: Global Test" in result


class TestVacancyFormatterIntegration:
    """Интеграционные тесты для проверки совместной работы методов"""

    def test_full_vacancy_formatting_workflow(self):
        """Покрытие: полный цикл форматирования сложной вакансии"""
        # Создаем комплексную вакансию
        employer = MockEmployer("Яндекс", has_get_name=True)
        salary = MockSalary("150000-250000 руб.")
        experience = MockExperience("от 3 до 6 лет", has_get_name=True)
        employment = MockExperience("полная занятость", has_get_name=True)
        
        vacancy = MockVacancy(
            vacancy_id="yandex_001",
            title="Senior Python Developer",
            employer=employer,
            salary=salary,
            area="Москва",
            experience=experience,
            employment=employment,
            source="HeadHunter",
            url="https://hh.ru/vacancy/yandex_001",
            requirements="Python 3.8+, Django, PostgreSQL, Redis, Docker",
            responsibilities="Разработка и поддержка высоконагруженных веб-сервисов",
            description="Мы ищем опытного Python разработчика для работы над интересными проектами",
            conditions="Удаленная работа, ДМС, корпоративное обучение"
        )
        
        formatter = VacancyFormatter()
        
        # Полное форматирование
        full_result = formatter.format_vacancy_info(vacancy, 1)
        
        # Проверяем что все ключевые элементы присутствуют
        expected_elements = [
            "1.",
            "ID: yandex_001",
            "Название: Senior Python Developer", 
            "Компания: Яндекс",
            "Зарплата: 150000-250000 руб.",
            "Регион: Москва",
            "Опыт: от 3 до 6 лет",
            "Занятость: полная занятость",
            "Источник: HeadHunter",
            "Ссылка: https://hh.ru/vacancy/yandex_001",
            "Требования: Python 3.8+",
            "Обязанности: Разработка",
            "Описание: Мы ищем",
            "Условия: Удаленная"
        ]
        
        for element in expected_elements:
            assert element in full_result
        
        # Краткое форматирование
        brief_result = VacancyFormatter.format_vacancy_brief(vacancy, 2)
        
        brief_expected = [
            "2.",
            "Senior Python Developer",
            "Компания: Яндекс", 
            "Зарплата: 150000-250000 руб.",
            "Регион: Москва",
            "Ссылка: https://hh.ru/vacancy/yandex_001"
        ]
        
        for element in brief_expected:
            assert element in brief_result

    def test_edge_case_minimal_vacancy(self):
        """Покрытие: минимальная вакансия с пустыми полями"""
        vacancy = MockVacancy()  # Пустая вакансия
        
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(vacancy)
        
        # Должна быть хотя бы зарплата "Не указана"
        assert "Зарплата: Не указана" in result
        
        # Остальные поля должны отсутствовать
        assert "ID:" not in result
        assert "Название:" not in result
        assert "Компания:" not in result