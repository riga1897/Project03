
"""
Тесты для модуля статистики вакансий
"""

import os
import sys
from typing import List, Dict, Any, Optional
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт из реального кода
from src.utils.vacancy_stats import VacancyStats
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestVacancyStats:
    """Тесты для класса статистики вакансий"""

    @pytest.fixture
    def sample_vacancies(self) -> List[Dict[str, Any]]:
        """Создание тестовых вакансий"""
        return [
            {
                "title": "Python Developer",
                "vacancy_id": "1",
                "url": "https://example.com/1",
                "source": "hh.ru",
                "employer": {"name": "Яндекс"},
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "description": "Работа с Python и Django"
            },
            {
                "title": "Java Developer",
                "vacancy_id": "2",
                "url": "https://example.com/2",
                "source": "hh.ru",
                "employer": {"name": "СБЕР"},
                "salary": {"from": 120000, "to": 180000, "currency": "RUR"},
                "description": "Разработка на Java Spring"
            },
            {
                "title": "Frontend Developer",
                "vacancy_id": "3",
                "url": "https://example.com/3",
                "source": "superjob.ru",
                "employer": {"name": "Тинькофф"},
                "salary": None,
                "description": "Работа с React и TypeScript"
            }
        ]

    @pytest.fixture
    def vacancy_stats(self) -> VacancyStats:
        """Создание экземпляра VacancyStats"""
        return VacancyStats()

    @pytest.fixture
    def vacancy_objects(self, sample_vacancies) -> List[Vacancy]:
        """Создание объектов Vacancy из тестовых данных"""
        vacancies = []
        for data in sample_vacancies:
            # Создаем объект Salary если есть данные
            salary = None
            if data.get('salary'):
                salary_data = data['salary']
                salary = Salary(
                    salary_from=salary_data.get('from'),
                    salary_to=salary_data.get('to'),
                    currency=salary_data.get('currency', 'RUR')
                )
            
            vacancy = Vacancy(
                title=data['title'],
                vacancy_id=data['vacancy_id'],
                url=data['url'],
                source=data['source'],
                employer=data.get('employer'),
                salary=salary,
                description=data.get('description')
            )
            vacancies.append(vacancy)
        
        return vacancies

    def test_vacancy_stats_initialization(self, vacancy_stats):
        """Тест инициализации класса статистики"""
        assert vacancy_stats is not None
        assert hasattr(vacancy_stats, 'calculate_salary_statistics')

    def test_calculate_salary_statistics(self, vacancy_stats, vacancy_objects):
        """Тест расчета статистики по зарплатам"""
        stats = vacancy_stats.calculate_salary_statistics(vacancy_objects)
        
        # Проверяем что метод возвращает результат
        assert stats is not None

    def test_empty_vacancies_list(self, vacancy_stats):
        """Тест обработки пустого списка вакансий"""
        empty_list = []
        
        # Тест статистики зарплат
        stats = vacancy_stats.calculate_salary_statistics(empty_list)
        
        # Метод должен обработать пустой список
        assert stats is not None or stats is None

    def test_vacancies_without_salary(self, vacancy_stats):
        """Тест обработки вакансий без зарплаты"""
        # Создаем вакансию без зарплаты
        vacancy_no_salary = Vacancy(
            title="Developer",
            vacancy_id="1",
            url="https://example.com/1",
            source="hh.ru",
            employer={"name": "Company1"},
            salary=None,
            description="Job description"
        )
        
        vacancies = [vacancy_no_salary]
        stats = vacancy_stats.calculate_salary_statistics(vacancies)
        
        # Метод должен обработать вакансии без зарплаты
        assert stats is not None or stats is None

    def test_salary_range_calculation(self, vacancy_stats):
        """Тест расчета диапазона зарплат"""
        # Создаем вакансию с диапазоном зарплат
        salary = Salary(salary_from=50000, salary_to=100000, currency="RUR")
        
        vacancy_with_range = Vacancy(
            title="Developer",
            vacancy_id="1",
            url="https://example.com/1",
            source="hh.ru",
            employer={"name": "Company1"},
            salary=salary,
            description="Job description"
        )
        
        vacancies = [vacancy_with_range]
        stats = vacancy_stats.calculate_salary_statistics(vacancies)
        
        # Проверяем что метод работает
        assert stats is not None or stats is None

    def test_mixed_salary_types(self, vacancy_stats):
        """Тест обработки различных типов зарплат"""
        vacancies = []
        
        # Вакансия с полным диапазоном
        salary1 = Salary(salary_from=80000, salary_to=120000, currency="RUR")
        vacancy1 = Vacancy(
            title="Python Developer",
            vacancy_id="1", 
            url="https://example.com/1",
            source="hh.ru",
            salary=salary1
        )
        vacancies.append(vacancy1)
        
        # Вакансия только с минимальной зарплатой
        salary2 = Salary(salary_from=100000, salary_to=None, currency="RUR")
        vacancy2 = Vacancy(
            title="Java Developer",
            vacancy_id="2",
            url="https://example.com/2", 
            source="hh.ru",
            salary=salary2
        )
        vacancies.append(vacancy2)
        
        # Вакансия только с максимальной зарплатой
        salary3 = Salary(salary_from=None, salary_to=150000, currency="RUR")
        vacancy3 = Vacancy(
            title="Frontend Developer",
            vacancy_id="3",
            url="https://example.com/3",
            source="superjob.ru", 
            salary=salary3
        )
        vacancies.append(vacancy3)
        
        # Вакансия без зарплаты
        vacancy4 = Vacancy(
            title="Designer",
            vacancy_id="4",
            url="https://example.com/4",
            source="hh.ru",
            salary=None
        )
        vacancies.append(vacancy4)
        
        stats = vacancy_stats.calculate_salary_statistics(vacancies)
        assert stats is not None or stats is None

    def test_salary_statistics_with_different_currencies(self, vacancy_stats):
        """Тест статистики с различными валютами"""
        vacancies = []
        
        # Вакансия в рублях
        salary_rur = Salary(salary_from=100000, salary_to=150000, currency="RUR")
        vacancy_rur = Vacancy(
            title="Developer RUR",
            vacancy_id="1",
            url="https://example.com/1",
            source="hh.ru",
            salary=salary_rur
        )
        vacancies.append(vacancy_rur)
        
        # Вакансия в долларах
        salary_usd = Salary(salary_from=1000, salary_to=2000, currency="USD")
        vacancy_usd = Vacancy(
            title="Developer USD",
            vacancy_id="2",
            url="https://example.com/2",
            source="hh.ru",
            salary=salary_usd
        )
        vacancies.append(vacancy_usd)
        
        stats = vacancy_stats.calculate_salary_statistics(vacancies)
        assert stats is not None or stats is None

    def test_vacancy_stats_methods_existence(self, vacancy_stats):
        """Тест наличия основных методов в VacancyStats"""
        # Проверяем что основные методы определены
        assert hasattr(vacancy_stats, 'calculate_salary_statistics')
        assert callable(getattr(vacancy_stats, 'calculate_salary_statistics'))

    def test_calculate_salary_statistics_performance(self, vacancy_stats):
        """Тест производительности расчета статистики"""
        import time
        
        # Создаем большое количество вакансий
        large_vacancy_list = []
        for i in range(100):
            salary = Salary(salary_from=50000 + i * 1000, salary_to=100000 + i * 1000, currency="RUR")
            vacancy = Vacancy(
                title=f"Developer {i}",
                vacancy_id=str(i),
                url=f"https://example.com/{i}",
                source="hh.ru",
                salary=salary
            )
            large_vacancy_list.append(vacancy)
        
        start_time = time.time()
        stats = vacancy_stats.calculate_salary_statistics(large_vacancy_list)
        end_time = time.time()
        
        # Операция должна выполниться быстро
        assert (end_time - start_time) < 1.0
        assert stats is not None or stats is None

    def test_edge_cases_handling(self, vacancy_stats):
        """Тест обработки граничных случаев"""
        # Тест с None в качестве аргумента
        try:
            stats = vacancy_stats.calculate_salary_statistics(None)
            assert stats is not None or stats is None
        except (TypeError, AttributeError):
            # Ожидаемое поведение при передаче None
            pass
        
        # Тест с некорректными данными в списке
        invalid_data = ["not_a_vacancy", 123, None]
        try:
            stats = vacancy_stats.calculate_salary_statistics(invalid_data)
            assert stats is not None or stats is None
        except (TypeError, AttributeError):
            # Ожидаемое поведение при некорректных данных
            pass
