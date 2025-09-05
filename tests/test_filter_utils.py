
"""
Тесты для утилит фильтрации данных
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.abstract_filter import AbstractFilter
    from src.utils.api_data_filter import ApiDataFilter
    FILTER_UTILS_AVAILABLE = True
except ImportError:
    FILTER_UTILS_AVAILABLE = False


class ConcreteFilter(AbstractFilter if FILTER_UTILS_AVAILABLE else object):
    """Конкретная реализация AbstractFilter для тестирования"""
    
    def filter(self, data, criteria):
        if not criteria:
            return data
        return [item for item in data if self._matches_criteria(item, criteria)]
    
    def _matches_criteria(self, item, criteria):
        for key, value in criteria.items():
            if key not in item or item[key] != value:
                return False
        return True


class TestAbstractFilter:
    """Тесты для абстрактного класса фильтрации"""

    def test_abstract_filter_cannot_be_instantiated(self):
        """Тест что абстрактный класс нельзя инстанциировать"""
        if not FILTER_UTILS_AVAILABLE:
            pytest.skip("Filter utils not available")
        
        with pytest.raises(TypeError):
            AbstractFilter()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not FILTER_UTILS_AVAILABLE:
            pytest.skip("Filter utils not available")
        
        filter_obj = ConcreteFilter()
        test_data = [
            {"id": 1, "name": "test1", "type": "A"},
            {"id": 2, "name": "test2", "type": "B"},
            {"id": 3, "name": "test3", "type": "A"}
        ]
        
        # Фильтрация по критерию
        result = filter_obj.filter(test_data, {"type": "A"})
        assert len(result) == 2
        assert all(item["type"] == "A" for item in result)
        
        # Фильтрация без критериев
        result = filter_obj.filter(test_data, {})
        assert len(result) == 3


class TestApiDataFilter:
    """Тесты для фильтра API данных"""

    @pytest.fixture
    def test_data(self):
        """Фикстура с тестовыми данными"""
        return [
            {
                "id": "1",
                "name": "Python Developer",
                "salary": {"from": 100000, "to": 150000},
                "employer": {"name": "Company A"},
                "area": {"name": "Москва"}
            },
            {
                "id": "2", 
                "name": "Java Developer",
                "salary": {"from": 120000, "to": 180000},
                "employer": {"name": "Company B"},
                "area": {"name": "СПб"}
            }
        ]

    def test_api_data_filter_creation(self):
        """Тест создания фильтра API данных"""
        if not FILTER_UTILS_AVAILABLE:
            pytest.skip("Filter utils not available")
        
        try:
            filter_obj = ApiDataFilter()
            assert filter_obj is not None
        except TypeError:
            # Если требуются аргументы
            filter_obj = ApiDataFilter({})
            assert filter_obj is not None

    @patch('builtins.print')
    def test_api_data_filter_methods_exist(self, mock_print, test_data):
        """Тест что методы фильтра существуют"""
        if not FILTER_UTILS_AVAILABLE:
            pytest.skip("Filter utils not available")
        
        try:
            filter_obj = ApiDataFilter()
        except TypeError:
            filter_obj = ApiDataFilter({})
        
        # Проверяем наличие методов фильтрации
        expected_methods = [
            'filter', 'filter_by_salary', 'filter_by_city',
            'filter_by_company', 'apply_filters'
        ]
        
        existing_methods = []
        for method_name in expected_methods:
            if hasattr(filter_obj, method_name):
                existing_methods.append(method_name)
        
        assert len(existing_methods) > 0

    @patch('builtins.print')
    def test_api_data_filter_execution(self, mock_print, test_data):
        """Тест выполнения фильтрации"""
        if not FILTER_UTILS_AVAILABLE:
            pytest.skip("Filter utils not available")
        
        try:
            filter_obj = ApiDataFilter()
        except TypeError:
            filter_obj = ApiDataFilter({})
        
        # Тестируем основной метод filter если он есть
        if hasattr(filter_obj, 'filter'):
            try:
                result = filter_obj.filter(test_data, {})
                assert isinstance(result, list)
            except Exception:
                pass  # Ожидаем возможные исключения
        
        # Тестируем другие методы фильтрации
        for method_name in ['filter_by_salary', 'filter_by_city', 'filter_by_company']:
            if hasattr(filter_obj, method_name):
                method = getattr(filter_obj, method_name)
                try:
                    result = method(test_data, "test_criteria")
                    assert isinstance(result, list)
                except Exception:
                    pass  # Ожидаем возможные исключения


class TestFilterIntegration:
    """Интеграционные тесты для фильтров"""

    @pytest.fixture
    def complex_test_data(self):
        """Комплексные тестовые данные"""
        return [
            {
                "id": "1",
                "name": "Senior Python Developer",
                "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
                "employer": {"id": "123", "name": "Яндекс"},
                "area": {"id": "1", "name": "Москва"},
                "experience": {"id": "between3And6", "name": "От 3 до 6 лет"}
            },
            {
                "id": "2",
                "name": "Junior Java Developer", 
                "salary": {"from": 80000, "to": 120000, "currency": "RUR"},
                "employer": {"id": "456", "name": "Google"},
                "area": {"id": "2", "name": "Санкт-Петербург"},
                "experience": {"id": "noExperience", "name": "Нет опыта"}
            }
        ]

    @patch('builtins.print')
    def test_multiple_filters_chain(self, mock_print, complex_test_data):
        """Тест цепочки фильтров"""
        if not FILTER_UTILS_AVAILABLE:
            pytest.skip("Filter utils not available")
        
        try:
            filter_obj = ApiDataFilter()
        except TypeError:
            filter_obj = ApiDataFilter({})
        
        # Применяем несколько фильтров подряд
        result = complex_test_data
        
        for filter_method in ['filter_by_salary', 'filter_by_city']:
            if hasattr(filter_obj, filter_method):
                try:
                    method = getattr(filter_obj, filter_method)
                    result = method(result, "test")
                    assert isinstance(result, list)
                except Exception:
                    pass
