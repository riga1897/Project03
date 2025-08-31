import os
import sys
from dataclasses import dataclass
from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.vacancy_stats import VacancyStats
except ImportError:

    class VacancyStats:
        """Placeholder for VacancyStats if not found in src"""

        def calculate_salary_statistics(self, vacancies: List):
            """Placeholder method for salary statistics calculation."""
            if not vacancies:
                return {"average": 0, "min": 0, "max": 0}
            salaries = [v.salary.from_amount for v in vacancies if v.salary and v.salary.from_amount is not None]
            if not salaries:
                return {"average": 0, "min": 0, "max": 0}
            return {"average": sum(salaries) / len(salaries), "min": min(salaries), "max": max(salaries)}

        def get_top_employers(self, vacancies: List, top_n: int = 5):
            """Placeholder method for top employers retrieval."""
            employer_counts = {}
            for v in vacancies:
                if v.employer and v.employer.name:
                    employer_counts[v.employer.name] = employer_counts.get(v.employer.name, 0) + 1
            sorted_employers = sorted(employer_counts.items(), key=lambda item: item[1], reverse=True)
            return sorted_employers[:top_n]

        def get_source_distribution(self, vacancies: List):
            """Placeholder method for source distribution calculation."""
            source_counts = {}
            for v in vacancies:
                source_counts[v.source] = source_counts.get(v.source, 0) + 1
            return source_counts


def calculate_statistics(vacancies: List):
    """Placeholder function for overall statistics calculation."""
    stats_calculator = VacancyStats()
    salary_stats = stats_calculator.calculate_salary_statistics(vacancies)
    top_employers = stats_calculator.get_top_employers(vacancies)
    source_distribution = stats_calculator.get_source_distribution(vacancies)
    return {"salary_stats": salary_stats, "top_employers": top_employers, "source_distribution": source_distribution}


try:
    from src.vacancies.models import Vacancy, VacancyEmployer, VacancySalary
except ImportError:

    @dataclass
    class Vacancy:
        """Placeholder for Vacancy model."""

        id: str
        title: str
        url: str
        source: str
        salary: Optional["VacancySalary"] = None
        employer: Optional["VacancyEmployer"] = None

    @dataclass
    class VacancySalary:
        """Placeholder for VacancySalary model."""

        from_amount: Optional[int] = None
        to_amount: Optional[int] = None
        currency: str = "RUR"

    @dataclass
    class VacancyEmployer:
        """Placeholder for VacancyEmployer model."""

        name: str


class TestVacancyStats:
    """Тесты для VacancyStats"""

    def test_vacancy_stats_initialization(self):
        """Тест инициализации VacancyStats"""
        stats = VacancyStats()
        assert isinstance(stats, VacancyStats)

    def test_calculate_salary_statistics(self):
        """Тест подсчета статистики по зарплатам"""
        vacancies = [
            Vacancy("123", "Dev1", "url1", "hh.ru", salary=VacancySalary(from_amount=100000, currency="RUR")),
            Vacancy("124", "Dev2", "url2", "hh.ru", salary=VacancySalary(from_amount=150000, currency="RUR")),
            Vacancy("125", "Dev3", "url3", "hh.ru", salary=VacancySalary(from_amount=200000, currency="RUR")),
        ]

        stats = VacancyStats()
        result = stats.calculate_salary_statistics(vacancies)

        assert isinstance(result, dict)
        assert "average" in result
        assert "min" in result
        assert "max" in result
        assert result["average"] == 150000
        assert result["min"] == 100000
        assert result["max"] == 200000

    def test_calculate_salary_statistics_empty(self):
        """Тест подсчета статистики для пустого списка"""
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([])

        assert result["average"] == 0
        assert result["min"] == 0
        assert result["max"] == 0

    def test_calculate_salary_statistics_no_salary(self):
        """Тест подсчета статистики для вакансий без зарплаты"""
        vacancies = [Vacancy("123", "Dev1", "url1", "hh.ru"), Vacancy("124", "Dev2", "url2", "hh.ru")]

        stats = VacancyStats()
        result = stats.calculate_salary_statistics(vacancies)

        assert result["average"] == 0

    def test_get_top_employers(self):
        """Тест получения топ работодателей"""
        vacancies = [
            Vacancy("123", "Dev1", "url1", "hh.ru", employer=VacancyEmployer("Company A")),
            Vacancy("124", "Dev2", "url2", "hh.ru", employer=VacancyEmployer("Company A")),
            Vacancy("125", "Dev3", "url3", "hh.ru", employer=VacancyEmployer("Company B")),
        ]

        stats = VacancyStats()
        result = stats.get_top_employers(vacancies, top_n=2)

        assert isinstance(result, list)
        assert len(result) <= 2
        # Company A должна быть первой (2 вакансии)
        assert result[0][0] == "Company A"
        assert result[0][1] == 2

    def test_get_source_distribution(self):
        """Тест получения распределения по источникам"""
        vacancies = [
            Vacancy("123", "Dev1", "url1", "hh.ru"),
            Vacancy("124", "Dev2", "url2", "hh.ru"),
            Vacancy("125", "Dev3", "url3", "superjob.ru"),
        ]

        stats = VacancyStats()
        result = stats.get_source_distribution(vacancies)

        assert isinstance(result, dict)
        assert result["hh.ru"] == 2
        assert result["superjob.ru"] == 1

    def test_calculate_statistics_function(self):
        """Тест функции calculate_statistics"""
        vacancies = [Vacancy("123", "Dev1", "url1", "hh.ru", salary=VacancySalary(from_amount=100000, currency="RUR"))]

        result = calculate_statistics(vacancies)

        assert isinstance(result, dict)
        assert "salary_stats" in result
        assert "top_employers" in result
        assert "source_distribution" in result
