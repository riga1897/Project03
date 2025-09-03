#!/usr/bin/env python3
"""
Тесты для модуля vacancy_display_handler
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.vacancies.models import Vacancy


class TestVacancyDisplayHandler:
    """Класс для тестирования VacancyDisplayHandler"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        mock_storage = Mock()
        self.display_handler = VacancyDisplayHandler(mock_storage)

        self.sample_vacancies = [
            Vacancy(
                vacancy_id="1",
                title="Python Developer",
                description="Разработка веб-приложений на Python",
                url="https://example.com/vacancy/1"
            ),
            Vacancy(
                vacancy_id="2",
                title="Java Developer",
                description="Разработка корпоративных приложений",
                url="https://example.com/vacancy/2"
            )
        ]

    def test_vacancy_display_handler_init(self):
        """Тест инициализации обработчика отображения вакансий"""
        handler = VacancyDisplayHandler()
        assert handler is not None

    @patch('builtins.print')
    def test_display_vacancies_list(self, mock_print):
        """Тест отображения списка вакансий"""
        if hasattr(self.display_handler, 'display_vacancies'):
            self.display_handler.display_vacancies(self.sample_vacancies)
            mock_print.assert_called()

    @patch('builtins.print')
    def test_display_vacancy_details(self, mock_print):
        """Тест отображения детальной информации о вакансии"""
        if hasattr(self.display_handler, 'display_details'):
            self.display_handler.display_details(self.sample_vacancies[0])
            mock_print.assert_called()

    @patch('builtins.print')
    def test_display_empty_list(self, mock_print):
        """Тест отображения пустого списка вакансий"""
        if hasattr(self.display_handler, 'display_vacancies'):
            self.display_handler.display_vacancies([])
            mock_print.assert_called()

    @patch('builtins.print')
    def test_display_vacancy_summary(self, mock_print):
        """Тест отображения краткой информации о вакансии"""
        if hasattr(self.display_handler, 'display_summary'):
            self.display_handler.display_summary(self.sample_vacancies[0])
            mock_print.assert_called()

    @patch('builtins.print')
    def test_display_formatted_salary(self, mock_print):
        """Тест отображения отформатированной зарплаты"""
        if hasattr(self.display_handler, 'format_salary'):
            formatted = self.display_handler.format_salary(100000, 150000, "RUR")
            assert isinstance(formatted, str)

    @patch('builtins.print')
    def test_display_pagination(self, mock_print):
        """Тест постраничного отображения вакансий"""
        if hasattr(self.display_handler, 'display_paginated'):
            self.display_handler.display_paginated(self.sample_vacancies, page=1, per_page=1)
            mock_print.assert_called()

    def test_format_vacancy_title(self):
        """Тест форматирования заголовка вакансии"""
        if hasattr(self.display_handler, 'format_title'):
            formatted = self.display_handler.format_title(self.sample_vacancies[0])
            assert isinstance(formatted, str)
            assert "Python Developer" in formatted

    def test_format_company_info(self):
        """Тест форматирования информации о компании"""
        if hasattr(self.display_handler, 'format_company'):
            formatted = self.display_handler.format_company(self.sample_vacancies[0])
            assert isinstance(formatted, str)
            assert "Tech Company" in formatted

    @patch('builtins.print')
    def test_display_vacancy_statistics(self, mock_print):
        """Тест отображения статистики по вакансиям"""
        stats = {
            'total': len(self.sample_vacancies),
            'avg_salary': 135000,
            'max_salary': 180000,
            'min_salary': 100000
        }

        if hasattr(self.display_handler, 'display_statistics'):
            self.display_handler.display_statistics(stats)
            mock_print.assert_called()

    @patch('builtins.print')
    def test_display_search_results_header(self, mock_print):
        """Тест отображения заголовка результатов поиска"""
        if hasattr(self.display_handler, 'display_search_header'):
            self.display_handler.display_search_header("python", len(self.sample_vacancies))
            mock_print.assert_called()

    def test_truncate_description(self):
        """Тест сокращения описания вакансии"""
        long_description = "Очень длинное описание вакансии " * 10

        if hasattr(self.display_handler, 'truncate_description'):
            truncated = self.display_handler.truncate_description(long_description, 100)
            assert len(truncated) <= 103  # 100 символов + "..."

    @patch('builtins.print')
    def test_display_vacancy_table(self, mock_print):
        """Тест отображения вакансий в виде таблицы"""
        if hasattr(self.display_handler, 'display_table'):
            self.display_handler.display_table(self.sample_vacancies)
            mock_print.assert_called()

    @patch('builtins.input', return_value='1')
    def test_select_vacancy_from_list(self, mock_input):
        """Тест выбора вакансии из списка"""
        if hasattr(self.display_handler, 'select_vacancy'):
            selected = self.display_handler.select_vacancy(self.sample_vacancies)
            assert selected is not None

    @patch('builtins.print')
    def test_display_no_results_message(self, mock_print):
        """Тест отображения сообщения об отсутствии результатов"""
        if hasattr(self.display_handler, 'display_no_results'):
            self.display_handler.display_no_results("python")
            mock_print.assert_called()

    def test_sort_vacancies_by_salary(self):
        """Тест сортировки вакансий по зарплате"""
        if hasattr(self.display_handler, 'sort_by_salary'):
            sorted_vacancies = self.display_handler.sort_by_salary(self.sample_vacancies)
            assert isinstance(sorted_vacancies, list)
            assert len(sorted_vacancies) == len(self.sample_vacancies)

    @patch('builtins.print')
    def test_display_filter_options(self, mock_print):
        """Тест отображения опций фильтрации"""
        if hasattr(self.display_handler, 'display_filter_options'):
            self.display_handler.display_filter_options()
            mock_print.assert_called()

    def test_highlight_keywords(self):
        """Тест выделения ключевых слов в тексте"""
        text = "Python разработчик в компании Tech"
        keywords = ["Python"]

        if hasattr(self.display_handler, 'highlight_keywords'):
            highlighted = self.display_handler.highlight_keywords(text, keywords)
            assert isinstance(highlighted, str)

    @patch('builtins.print')
    def test_display_export_options(self, mock_print):
        """Тест отображения опций экспорта"""
        if hasattr(self.display_handler, 'display_export_options'):
            self.display_handler.display_export_options(self.sample_vacancies)
            mock_print.assert_called()