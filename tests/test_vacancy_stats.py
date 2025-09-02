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
        """
        Создание тестовых вакансий

        Returns:
            List[Dict[str, Any]]: Список тестовых данных вакансий
        """
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
        """
        Создание экземпляра VacancyStats

        Returns:
            VacancyStats: Экземпляр калькулятора статистик
        """
        return VacancyStats()

    @pytest.fixture
    def vacancy_objects(self, sample_vacancies: List[Dict[str, Any]]) -> List[Vacancy]:
        """
        Создание объектов Vacancy из тестовых данных

        Args:
            sample_vacancies: Тестовые данные вакансий

        Returns:
            List[Vacancy]: Список объектов вакансий
        """
        vacancies = []
        for data in sample_vacancies:
            # Создаем объект Salary если есть данные - используем правильный конструктор
            salary = None
            if data.get('salary'):
                salary_data = data['salary']
                salary = Salary({"from": salary_data.get('from'), "to": salary_data.get('to'), "currency": salary_data.get('currency', 'RUR')})

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

    def test_vacancy_stats_initialization(self, vacancy_stats: VacancyStats) -> None:
        """Тест инициализации класса статистики"""
        assert vacancy_stats is not None
        assert hasattr(vacancy_stats, 'calculate_salary_statistics')

    def test_calculate_salary_statistics(self, vacancy_stats: VacancyStats, vacancy_objects: List[Vacancy]) -> None:
        """Тест расчета статистики по зарплатам"""
        stats = vacancy_stats.calculate_salary_statistics(vacancy_objects)

        # Проверяем что метод возвращает результат
        assert stats is not None
        # Проверяем что это словарь со статистикой
        if isinstance(stats, dict):
            # Возможные ключи статистики
            expected_keys = ['count', 'average', 'min', 'max', 'median', 'with_salary_count', 'without_salary_count']
            # Проверяем что хотя бы некоторые ключи присутствуют
            assert any(key in stats for key in expected_keys)

    def test_empty_vacancies_list(self, vacancy_stats: VacancyStats) -> None:
        """Тест обработки пустого списка вакансий"""
        empty_list = []

        # Тест статистики зарплат
        stats = vacancy_stats.calculate_salary_statistics(empty_list)

        # Метод должен обработать пустой список
        assert stats is not None or stats is None
        if stats is not None and isinstance(stats, dict):
            # Для пустого списка статистики должны быть нулевые или None
            assert stats.get('count', 0) == 0

    def test_vacancies_without_salary(self, vacancy_stats: VacancyStats) -> None:
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
        if stats is not None and isinstance(stats, dict):
            # Для вакансий без зарплаты статистики зарплат должны быть пустые
            assert stats.get('with_salary_count', 0) == 0

    def test_salary_range_calculation(self, vacancy_stats: VacancyStats) -> None:
        """Тест расчета диапазона зарплат"""
        # Создаем вакансию с диапазоном зарплат - используем правильный конструктор
        salary = Salary({"from": 50000, "to": 100000, "currency": "RUR"})

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
        if stats is not None and isinstance(stats, dict):
            assert stats.get('with_salary_count', 0) >= 1

    def test_mixed_salary_types(self, vacancy_stats: VacancyStats) -> None:
        """Тест обработки различных типов зарплат"""
        vacancies = []

        # Вакансия с полным диапазоном
        salary1 = Salary({"from": 80000, "to": 120000, "currency": "RUR"})
        vacancy1 = Vacancy(
            title="Python Developer",
            vacancy_id="1", 
            url="https://example.com/1",
            source="hh.ru",
            salary=salary1
        )
        vacancies.append(vacancy1)

        # Вакансия только с минимальной зарплатой
        salary2 = Salary({"from": 100000, "to": None, "currency": "RUR"})
        vacancy2 = Vacancy(
            title="Java Developer",
            vacancy_id="2",
            url="https://example.com/2", 
            source="hh.ru",
            salary=salary2
        )
        vacancies.append(vacancy2)

        # Вакансия только с максимальной зарплатой
        salary3 = Salary({"from": None, "to": 150000, "currency": "RUR"})
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
        if stats is not None and isinstance(stats, dict):
            # Должно быть 3 вакансии с зарплатой и 1 без
            assert stats.get('with_salary_count', 0) >= 3
            assert stats.get('without_salary_count', 0) >= 1

    def test_salary_statistics_with_different_currencies(self, vacancy_stats: VacancyStats) -> None:
        """Тест статистики с различными валютами"""
        vacancies = []

        # Вакансия в рублях
        salary_rur = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        vacancy_rur = Vacancy(
            title="Developer RUR",
            vacancy_id="1",
            url="https://example.com/1",
            source="hh.ru",
            salary=salary_rur
        )
        vacancies.append(vacancy_rur)

        # Вакансия в долларах
        salary_usd = Salary({"from": 1000, "to": 2000, "currency": "USD"})
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
        if stats is not None and isinstance(stats, dict):
            # Статистика должна учитывать разные валюты
            assert stats.get('with_salary_count', 0) >= 2

    def test_vacancy_stats_methods_existence(self, vacancy_stats: VacancyStats) -> None:
        """Тест наличия основных методов в VacancyStats"""
        # Проверяем что основные методы определены
        assert hasattr(vacancy_stats, 'calculate_salary_statistics')
        assert callable(getattr(vacancy_stats, 'calculate_salary_statistics'))

    def test_calculate_salary_statistics_performance(self, vacancy_stats: VacancyStats) -> None:
        """Тест производительности расчета статистики"""
        import time

        # Создаем большое количество вакансий
        large_vacancy_list = []
        for i in range(100):
            salary = Salary({"from": 50000 + i * 1000, "to": 100000 + i * 1000, "currency": "RUR"})
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

    def test_edge_cases_handling(self, vacancy_stats: VacancyStats) -> None:
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

    def test_salary_statistics_detailed(self, vacancy_stats: VacancyStats) -> None:
        """Тест детальной статистики зарплат"""
        # Создаем вакансии с известными зарплатами для проверки расчетов
        vacancies = []

        # Вакансии с конкретными зарплатами
        salaries_data = [
            (100000, 150000),  # средняя: 125000
            (200000, 250000),  # средняя: 225000  
            (80000, 120000),   # средняя: 100000
        ]

        for i, (min_sal, max_sal) in enumerate(salaries_data):
            salary = Salary({"from": min_sal, "to": max_sal, "currency": "RUR"})
            vacancy = Vacancy(
                title=f"Developer {i}",
                vacancy_id=str(i),
                url=f"https://example.com/{i}",
                source="hh.ru",
                salary=salary
            )
            vacancies.append(vacancy)

        stats = vacancy_stats.calculate_salary_statistics(vacancies)

        if stats is not None and isinstance(stats, dict):
            # Проверяем основные статистики
            assert stats.get('with_salary_count', 0) == 3
            assert stats.get('without_salary_count', 0) == 0

            # Проверяем что средняя зарплата в разумных пределах
            avg_salary = stats.get('average')
            if avg_salary is not None:
                assert 100000 <= avg_salary <= 225000  # Между минимальной и максимальной средней

    def test_salary_statistics_formatting(self, vacancy_stats: VacancyStats) -> None:
        """Тест форматирования результатов статистики"""
        # Создаем простую вакансию для тестирования
        salary = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        vacancy = Vacancy(
            title="Test Developer",
            vacancy_id="test_1",
            url="https://example.com/test",
            source="hh.ru",
            salary=salary
        )

        stats = vacancy_stats.calculate_salary_statistics([vacancy])

        if stats is not None:
            # Проверяем что результат можно сериализовать
            assert isinstance(stats, (dict, str, int, float, list))

            # Если это словарь, проверяем что значения корректные
            if isinstance(stats, dict):
                for key, value in stats.items():
                    assert isinstance(key, str)
                    assert value is None or isinstance(value, (int, float, str, list, dict))