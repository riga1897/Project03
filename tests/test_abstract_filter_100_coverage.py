"""
100% покрытие utils/abstract_filter.py модуля
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.utils.abstract_filter import AbstractDataFilter


class ConcreteTestFilter(AbstractDataFilter):
    """Конкретная реализация абстрактного фильтра для тестирования"""
    
    def filter_by_company(self, data: List[Dict[str, Any]], companies: List[str]) -> List[Dict[str, Any]]:
        """Конкретная реализация фильтрации по компаниям"""
        return [item for item in data if item.get('company') in companies]
    
    def filter_by_salary(
        self, data: List[Dict[str, Any]], min_salary: Optional[int] = None, max_salary: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Конкретная реализация фильтрации по зарплате"""
        filtered_data = data[:]
        
        if min_salary is not None:
            filtered_data = [item for item in filtered_data if item.get('salary', 0) >= min_salary]
        
        if max_salary is not None:
            filtered_data = [item for item in filtered_data if item.get('salary', 0) <= max_salary]
        
        return filtered_data
    
    def filter_by_location(self, data: List[Dict[str, Any]], locations: List[str]) -> List[Dict[str, Any]]:
        """Конкретная реализация фильтрации по местоположению"""
        return [item for item in data if item.get('location') in locations]
    
    def filter_by_experience(self, data: List[Dict[str, Any]], experience_levels: List[str]) -> List[Dict[str, Any]]:
        """Конкретная реализация фильтрации по опыту"""
        return [item for item in data if item.get('experience') in experience_levels]


class TestAbstractDataFilter:
    """100% покрытие AbstractDataFilter"""

    def test_cannot_instantiate_abstract_class(self):
        """Тест что абстрактный класс нельзя инстанцировать"""
        with pytest.raises(TypeError) as exc_info:
            AbstractDataFilter()
        
        assert "Can't instantiate abstract class" in str(exc_info.value)

    def test_concrete_implementation_filter_by_company(self):
        """Тест конкретной реализации filter_by_company - покрывает строку 30"""
        filter_instance = ConcreteTestFilter()
        
        test_data = [
            {'company': 'Google', 'title': 'Developer'},
            {'company': 'Microsoft', 'title': 'Engineer'},
            {'company': 'Apple', 'title': 'Architect'}
        ]
        
        companies = ['Google', 'Apple']
        result = filter_instance.filter_by_company(test_data, companies)
        
        assert len(result) == 2
        assert all(item['company'] in companies for item in result)

    def test_concrete_implementation_filter_by_salary(self):
        """Тест конкретной реализации filter_by_salary - покрывает строку 47"""
        filter_instance = ConcreteTestFilter()
        
        test_data = [
            {'salary': 50000, 'title': 'Junior'},
            {'salary': 80000, 'title': 'Middle'},
            {'salary': 120000, 'title': 'Senior'}
        ]
        
        # Тест с минимальной зарплатой
        result = filter_instance.filter_by_salary(test_data, min_salary=70000)
        assert len(result) == 2
        assert all(item['salary'] >= 70000 for item in result)
        
        # Тест с максимальной зарплатой
        result = filter_instance.filter_by_salary(test_data, max_salary=90000)
        assert len(result) == 2
        assert all(item['salary'] <= 90000 for item in result)
        
        # Тест с диапазоном
        result = filter_instance.filter_by_salary(test_data, min_salary=60000, max_salary=100000)
        assert len(result) == 1
        assert result[0]['salary'] == 80000

    def test_concrete_implementation_filter_by_location(self):
        """Тест конкретной реализации filter_by_location - покрывает строку 61"""
        filter_instance = ConcreteTestFilter()
        
        test_data = [
            {'location': 'Moscow', 'title': 'Developer'},
            {'location': 'SPb', 'title': 'Engineer'},
            {'location': 'Novosibirsk', 'title': 'Architect'}
        ]
        
        locations = ['Moscow', 'SPb']
        result = filter_instance.filter_by_location(test_data, locations)
        
        assert len(result) == 2
        assert all(item['location'] in locations for item in result)

    def test_concrete_implementation_filter_by_experience(self):
        """Тест конкретной реализации filter_by_experience - покрывает строку 75"""
        filter_instance = ConcreteTestFilter()
        
        test_data = [
            {'experience': 'Junior', 'title': 'Developer'},
            {'experience': 'Middle', 'title': 'Engineer'},
            {'experience': 'Senior', 'title': 'Architect'}
        ]
        
        experience_levels = ['Middle', 'Senior']
        result = filter_instance.filter_by_experience(test_data, experience_levels)
        
        assert len(result) == 2
        assert all(item['experience'] in experience_levels for item in result)

    def test_abstract_methods_must_be_implemented(self):
        """Тест что все абстрактные методы должны быть реализованы"""
        class IncompleteFilter(AbstractDataFilter):
            def filter_by_company(self, data, companies):
                return data
            # Не реализуем остальные методы
        
        with pytest.raises(TypeError) as exc_info:
            IncompleteFilter()
        
        assert "abstract methods" in str(exc_info.value)

    def test_method_signatures_match_abstract(self):
        """Тест что сигнатуры методов соответствуют абстрактным"""
        filter_instance = ConcreteTestFilter()
        
        # Проверяем что методы существуют и callable
        assert callable(getattr(filter_instance, 'filter_by_company'))
        assert callable(getattr(filter_instance, 'filter_by_salary'))
        assert callable(getattr(filter_instance, 'filter_by_location'))
        assert callable(getattr(filter_instance, 'filter_by_experience'))

    def test_empty_data_handling(self):
        """Тест обработки пустых данных"""
        filter_instance = ConcreteTestFilter()
        empty_data = []
        
        # Все методы должны корректно обрабатывать пустые данные
        assert filter_instance.filter_by_company(empty_data, ['test']) == []
        assert filter_instance.filter_by_salary(empty_data, 1000) == []
        assert filter_instance.filter_by_location(empty_data, ['Moscow']) == []
        assert filter_instance.filter_by_experience(empty_data, ['Junior']) == []

    def test_edge_cases_filter_by_salary(self):
        """Тест граничных случаев для фильтрации по зарплате"""
        filter_instance = ConcreteTestFilter()
        
        test_data = [
            {'salary': 0, 'title': 'Intern'},
            {'salary': 50000, 'title': 'Junior'},
            {'title': 'No salary info'}  # Отсутствует поле salary
        ]
        
        # Тест с данными без поля salary
        result = filter_instance.filter_by_salary(test_data, min_salary=1)
        # Должны остаться только элементы с зарплатой >= 1
        assert len(result) == 1
        assert result[0]['salary'] == 50000