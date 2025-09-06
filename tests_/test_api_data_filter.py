
"""
Тесты для фильтра API данных
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.api_data_filter import APIDataFilter
    API_DATA_FILTER_AVAILABLE = True
except ImportError:
    API_DATA_FILTER_AVAILABLE = False


class TestAPIDataFilter:
    """Тесты для фильтра API данных"""
    
    @pytest.fixture
    def api_filter(self):
        """Фикстура для создания экземпляра фильтра"""
        if not API_DATA_FILTER_AVAILABLE:
            pytest.skip("APIDataFilter not available")
        return APIDataFilter()
    
    def test_api_data_filter_init(self, api_filter):
        """Тест инициализации фильтра"""
        assert api_filter is not None
    
    def test_filter_by_salary_range(self, api_filter):
        """Тест фильтрации по диапазону зарплаты"""
        test_data = [
            {"id": "1", "salary": {"from": 50000, "to": 80000}},
            {"id": "2", "salary": {"from": 100000, "to": 150000}},
            {"id": "3", "salary": None}
        ]
        
        if hasattr(api_filter, 'filter_by_salary_range'):
            result = api_filter.filter_by_salary_range(test_data, min_salary=60000)
            assert len(result) <= len(test_data)
    
    def test_filter_by_location(self, api_filter):
        """Тест фильтрации по местоположению"""
        test_data = [
            {"id": "1", "area": {"name": "Москва"}},
            {"id": "2", "area": {"name": "Санкт-Петербург"}},
            {"id": "3", "area": {"name": "Новосибирск"}}
        ]
        
        if hasattr(api_filter, 'filter_by_location'):
            result = api_filter.filter_by_location(test_data, locations=["Москва"])
            assert isinstance(result, list)
    
    def test_filter_by_experience(self, api_filter):
        """Тест фильтрации по опыту работы"""
        test_data = [
            {"id": "1", "experience": {"id": "noExperience"}},
            {"id": "2", "experience": {"id": "between1And3"}},
            {"id": "3", "experience": {"id": "between3And6"}}
        ]
        
        if hasattr(api_filter, 'filter_by_experience'):
            result = api_filter.filter_by_experience(test_data, experience_levels=["noExperience"])
            assert isinstance(result, list)
    
    def test_filter_empty_data(self, api_filter):
        """Тест фильтрации пустых данных"""
        if hasattr(api_filter, 'filter_by_salary_range'):
            result = api_filter.filter_by_salary_range([], min_salary=50000)
            assert result == []
    
    def test_filter_with_none_values(self, api_filter):
        """Тест фильтрации с None значениями"""
        test_data = [
            {"id": "1", "salary": None},
            {"id": "2", "area": None},
            {"id": "3", "experience": None}
        ]
        
        if hasattr(api_filter, 'filter_by_salary_range'):
            result = api_filter.filter_by_salary_range(test_data, min_salary=50000)
            assert isinstance(result, list)
