
"""
Полные тесты для абстрактного фильтра
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.abstract_filter import AbstractDataFilter
    ABSTRACT_FILTER_AVAILABLE = True
except ImportError:
    ABSTRACT_FILTER_AVAILABLE = False
    AbstractDataFilter = object


class ConcreteDataFilter(AbstractDataFilter if ABSTRACT_FILTER_AVAILABLE else object):
    """Конкретная реализация AbstractDataFilter для тестирования"""
    
    def filter_by_salary(self, data, min_salary=None, max_salary=None):
        """Конкретная реализация фильтрации по зарплате"""
        if not data:
            return []
        
        filtered = []
        for item in data:
            salary = item.get('salary', 0)
            if min_salary and salary < min_salary:
                continue
            if max_salary and salary > max_salary:
                continue
            filtered.append(item)
        return filtered


class TestAbstractDataFilter:
    """Тесты для абстрактного фильтра данных"""

    def test_abstract_filter_cannot_be_instantiated(self):
        """Тест что абстрактный класс нельзя инстанциировать"""
        if not ABSTRACT_FILTER_AVAILABLE:
            pytest.skip("AbstractDataFilter not available")

        with pytest.raises(TypeError):
            AbstractDataFilter()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not ABSTRACT_FILTER_AVAILABLE:
            pytest.skip("AbstractDataFilter not available")

        filter_instance = ConcreteDataFilter()
        assert filter_instance is not None

        # Тест фильтрации по зарплате
        test_data = [
            {'id': 1, 'salary': 50000},
            {'id': 2, 'salary': 75000},
            {'id': 3, 'salary': 100000}
        ]

        # Фильтр по минимальной зарплате
        result = filter_instance.filter_by_salary(test_data, min_salary=60000)
        assert len(result) == 2
        assert all(item['salary'] >= 60000 for item in result)

        # Фильтр по максимальной зарплате
        result = filter_instance.filter_by_salary(test_data, max_salary=80000)
        assert len(result) == 2
        assert all(item['salary'] <= 80000 for item in result)

        # Фильтр по диапазону
        result = filter_instance.filter_by_salary(test_data, min_salary=60000, max_salary=80000)
        assert len(result) == 1
        assert result[0]['salary'] == 75000

    def test_filter_empty_data(self):
        """Тест фильтрации пустых данных"""
        if not ABSTRACT_FILTER_AVAILABLE:
            pytest.skip("AbstractDataFilter not available")

        filter_instance = ConcreteDataFilter()
        result = filter_instance.filter_by_salary([], min_salary=50000)
        assert result == []

    def test_filter_none_data(self):
        """Тест фильтрации None данных"""
        if not ABSTRACT_FILTER_AVAILABLE:
            pytest.skip("AbstractDataFilter not available")

        filter_instance = ConcreteDataFilter()
        result = filter_instance.filter_by_salary(None, min_salary=50000)
        assert result == []

    def test_filter_no_salary_constraints(self):
        """Тест фильтрации без ограничений по зарплате"""
        if not ABSTRACT_FILTER_AVAILABLE:
            pytest.skip("AbstractDataFilter not available")

        filter_instance = ConcreteDataFilter()
        test_data = [
            {'id': 1, 'salary': 50000},
            {'id': 2, 'salary': 75000}
        ]

        result = filter_instance.filter_by_salary(test_data)
        assert len(result) == 2
        assert result == test_data

    def test_filter_items_without_salary(self):
        """Тест фильтрации элементов без поля salary"""
        if not ABSTRACT_FILTER_AVAILABLE:
            pytest.skip("AbstractDataFilter not available")

        filter_instance = ConcreteDataFilter()
        test_data = [
            {'id': 1},  # нет salary
            {'id': 2, 'salary': 75000}
        ]

        result = filter_instance.filter_by_salary(test_data, min_salary=50000)
        assert len(result) == 1
        assert result[0]['id'] == 2


class TestAbstractFilterIntegration:
    """Интеграционные тесты абстрактного фильтра"""

    def test_multiple_filters_chaining(self):
        """Тест цепочки фильтров"""
        if not ABSTRACT_FILTER_AVAILABLE:
            pytest.skip("AbstractDataFilter not available")

        filter_instance = ConcreteDataFilter()
        test_data = [
            {'id': 1, 'salary': 30000},
            {'id': 2, 'salary': 60000},
            {'id': 3, 'salary': 90000},
            {'id': 4, 'salary': 120000}
        ]

        # Сначала фильтр по минимальной зарплате
        step1 = filter_instance.filter_by_salary(test_data, min_salary=50000)
        assert len(step1) == 3

        # Затем по максимальной
        step2 = filter_instance.filter_by_salary(step1, max_salary=100000)
        assert len(step2) == 2

    def test_edge_cases(self):
        """Тест граничных случаев"""
        if not ABSTRACT_FILTER_AVAILABLE:
            pytest.skip("AbstractDataFilter not available")

        filter_instance = ConcreteDataFilter()
        
        # Тест с нулевой зарплатой
        test_data = [{'id': 1, 'salary': 0}]
        result = filter_instance.filter_by_salary(test_data, min_salary=0)
        assert len(result) == 1

        # Тест с отрицательными значениями
        test_data = [{'id': 1, 'salary': -1000}]
        result = filter_instance.filter_by_salary(test_data, min_salary=0)
        assert len(result) == 0

        # Тест с очень большими значениями
        test_data = [{'id': 1, 'salary': 999999999}]
        result = filter_instance.filter_by_salary(test_data, max_salary=1000000000)
        assert len(result) == 1
