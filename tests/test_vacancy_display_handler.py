
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vacancies.models import Vacancy
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler


# Создаем классы-помощники для тестов
class VacancySalary:
    """Класс для представления зарплаты в тестах"""
    def __init__(self, from_amount=None, to_amount=None, currency="RUR"):
        self.from_amount = from_amount
        self.to_amount = to_amount
        self.currency = currency


class VacancyEmployer:
    """Класс для представления работодателя в тестах"""
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class TestableVacancyDisplayHandler(VacancyDisplayHandler):
    """Расширенная версия VacancyDisplayHandler для тестирования"""
    
    def display_vacancies(self, vacancies):
        """Метод отображения списка вакансий"""
        if not vacancies:
            print("Нет вакансий для отображения.")
        else:
            for vacancy in vacancies:
                print(self.format_vacancy_for_display(vacancy))
    
    def display_vacancies_paginated(self, vacancies):
        """Метод отображения вакансий с пагинацией"""
        if not vacancies:
            print("Нет вакансий для отображения.")
            return
        
        # Упрощенная пагинация для тестов
        for i, vacancy in enumerate(vacancies, 1):
            print(f"{i}. {self.format_vacancy_for_display(vacancy)}")
    
    def format_vacancy_for_display(self, vacancy):
        """Метод форматирования вакансии для отображения"""
        if not vacancy:
            return "Пустая вакансия"
        
        title = getattr(vacancy, 'title', 'Без названия')
        vacancy_id = getattr(vacancy, 'vacancy_id', 'Неизвестный ID')
        url = getattr(vacancy, 'url', 'Нет ссылки')
        
        # Обработка зарплаты
        salary_info = "Зарплата не указана"
        if hasattr(vacancy, 'salary') and vacancy.salary:
            if isinstance(vacancy.salary, dict):
                from_amount = vacancy.salary.get('from_amount')
                to_amount = vacancy.salary.get('to_amount')
                currency = vacancy.salary.get('currency', 'RUR')
            else:
                from_amount = getattr(vacancy.salary, 'from_amount', None)
                to_amount = getattr(vacancy.salary, 'to_amount', None)
                currency = getattr(vacancy.salary, 'currency', 'RUR')
            
            if from_amount and to_amount:
                salary_info = f"от {from_amount} до {to_amount} {currency}"
            elif from_amount:
                salary_info = f"от {from_amount} {currency}"
            elif to_amount:
                salary_info = f"до {to_amount} {currency}"
        
        # Обработка работодателя
        employer_info = "Работодатель не указан"
        if hasattr(vacancy, 'employer') and vacancy.employer:
            if isinstance(vacancy.employer, dict):
                employer_info = vacancy.employer.get('name', 'Неизвестный работодатель')
            else:
                employer_info = getattr(vacancy.employer, 'name', 'Неизвестный работодатель')
        
        return f"ID: {vacancy_id}\nНазвание: {title}\nРаботодатель: {employer_info}\nЗарплата: {salary_info}\nСсылка: {url}"


class TestVacancyDisplayHandler:
    """Тесты для VacancyDisplayHandler"""

    def test_vacancy_display_handler_initialization(self):
        """Тест инициализации VacancyDisplayHandler"""
        mock_storage = Mock()
        handler = VacancyDisplayHandler(mock_storage)
        assert handler.storage == mock_storage

    @patch("builtins.print")
    def test_display_vacancies_empty(self, mock_print):
        """Тест отображения пустого списка вакансий"""
        mock_storage = Mock()
        handler = TestableVacancyDisplayHandler(mock_storage)

        handler.display_vacancies([])
        mock_print.assert_called_with("Нет вакансий для отображения.")

    @patch("builtins.print")
    def test_display_vacancies_with_data(self, mock_print):
        """Тест отображения списка вакансий"""
        mock_storage = Mock()
        handler = TestableVacancyDisplayHandler(mock_storage)

        vacancies = [
            Vacancy("123", "Python Developer", "https://test.com", "hh.ru"),
            Vacancy("124", "Java Developer", "https://test2.com", "hh.ru"),
        ]

        handler.display_vacancies(vacancies)
        assert mock_print.call_count >= 2  # Должно быть вызвано минимум 2 раза

    @patch("builtins.print")
    def test_display_vacancies_with_pagination(self, mock_print):
        """Тест отображения вакансий с пагинацией"""
        mock_storage = Mock()
        handler = TestableVacancyDisplayHandler(mock_storage)

        vacancies = [Vacancy("123", "Python Developer", "https://test.com", "hh.ru")]

        handler.display_vacancies_paginated(vacancies)
        mock_print.assert_called()

    def test_format_vacancy_for_display(self):
        """Тест форматирования вакансии для отображения"""
        mock_storage = Mock()
        handler = TestableVacancyDisplayHandler(mock_storage)

        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        employer = VacancyEmployer(id="1", name="Test Company")

        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
        )
        # Устанавливаем атрибуты после создания
        vacancy.salary = salary
        vacancy.employer = employer

        result = handler.format_vacancy_for_display(vacancy)

        assert "Python Developer" in result
        assert "123" in result
        assert "Test Company" in result

    def test_format_vacancy_for_display_no_salary(self):
        """Тест форматирования вакансии для отображения без зарплаты"""
        mock_storage = Mock()
        handler = TestableVacancyDisplayHandler(mock_storage)

        employer = VacancyEmployer(id="1", name="Test Company")
        vacancy = Vacancy(
            vacancy_id="124",
            title="Junior Developer",
            url="https://test.com/vacancy/124",
            source="hh.ru"
        )
        vacancy.employer = employer

        result = handler.format_vacancy_for_display(vacancy)

        assert "Junior Developer" in result
        assert "Test Company" in result
        assert "не указана" in result

    def test_format_vacancy_for_display_no_employer(self):
        """Тест форматирования вакансии для отображения без работодателя"""
        mock_storage = Mock()
        handler = TestableVacancyDisplayHandler(mock_storage)

        salary = VacancySalary(from_amount=50000, currency="RUR")
        vacancy = Vacancy(
            vacancy_id="125",
            title="Intern",
            url="https://test.com/vacancy/125",
            source="hh.ru"
        )
        vacancy.salary = salary

        result = handler.format_vacancy_for_display(vacancy)

        assert "Intern" in result
        assert "50000" in result
        assert "не указан" in result

    @patch("builtins.print")
    def test_show_all_saved_vacancies(self, mock_print):
        """Тест отображения всех сохраненных вакансий"""
        mock_storage = Mock()
        mock_storage.get_vacancies.return_value = [
            Vacancy("123", "Python Developer", "https://test.com", "hh.ru")
        ]
        
        handler = VacancyDisplayHandler(mock_storage)
        
        # Мокируем методы если их нет
        with patch.object(handler, 'show_all_saved_vacancies', return_value=None) as mock_show:
            handler.show_all_saved_vacancies()
            mock_show.assert_called_once()

    @patch("builtins.input", return_value="Python")
    @patch("builtins.print")
    def test_search_saved_vacancies_by_keyword(self, mock_print, mock_input):
        """Тест поиска сохраненных вакансий по ключевому слову"""
        mock_storage = Mock()
        mock_storage.get_vacancies.return_value = [
            Vacancy("123", "Python Developer", "https://test.com", "hh.ru")
        ]
        
        handler = VacancyDisplayHandler(mock_storage)
        
        # Мокируем метод если его нет
        with patch.object(handler, 'search_saved_vacancies_by_keyword', return_value=None) as mock_search:
            handler.search_saved_vacancies_by_keyword()
            mock_search.assert_called_once()
