
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.vacancies.models import Vacancy, VacancySalary, VacancyEmployer


class TestVacancyDisplayHandler:
    """Тесты для VacancyDisplayHandler"""

    def test_vacancy_display_handler_initialization(self):
        """Тест инициализации VacancyDisplayHandler"""
        mock_storage = Mock()
        handler = VacancyDisplayHandler(mock_storage)
        
        assert handler.storage == mock_storage

    @patch('builtins.print')
    def test_display_vacancies_empty_list(self, mock_print):
        """Тест отображения пустого списка вакансий"""
        mock_storage = Mock()
        handler = VacancyDisplayHandler(mock_storage)
        
        handler.display_vacancies([])
        
        # Должно быть сообщение о том, что вакансий нет
        mock_print.assert_called()

    @patch('builtins.print')
    def test_display_vacancies_with_data(self, mock_print):
        """Тест отображения списка вакансий"""
        mock_storage = Mock()
        handler = VacancyDisplayHandler(mock_storage)
        
        vacancies = [
            Vacancy("123", "Python Developer", "https://test.com", "hh.ru"),
            Vacancy("124", "Java Developer", "https://test2.com", "hh.ru")
        ]
        
        handler.display_vacancies(vacancies)
        
        # Проверяем, что функция print была вызвана
        mock_print.assert_called()

    @patch('src.ui_interfaces.vacancy_display_handler.quick_paginate')
    def test_display_vacancies_with_pagination(self, mock_paginate):
        """Тест отображения вакансий с пагинацией"""
        mock_storage = Mock()
        handler = VacancyDisplayHandler(mock_storage)
        
        vacancies = [Vacancy("123", "Python Developer", "https://test.com", "hh.ru")]
        
        handler.display_vacancies_paginated(vacancies)
        
        # Проверяем, что пагинация была вызвана
        mock_paginate.assert_called()

    def test_format_vacancy_for_display(self):
        """Тест форматирования вакансии для отображения"""
        mock_storage = Mock()
        handler = VacancyDisplayHandler(mock_storage)
        
        salary = VacancySalary(from_amount=100000, to_amount=150000, currency="RUR")
        employer = VacancyEmployer(name="Test Company")
        
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="https://test.com/vacancy/123",
            source="hh.ru",
            salary=salary,
            employer=employer
        )
        
        result = handler.format_vacancy_for_display(vacancy)
        
        assert isinstance(result, str)
        assert "Python Developer" in result
        assert "Test Company" in result
