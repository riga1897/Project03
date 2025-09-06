
"""Вспомогательные моки для тестов"""

from unittest.mock import Mock, MagicMock
from typing import Any, Dict, List, Optional


class MockTestCachedAPI:
    """Тестовая реализация CachedAPI"""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        self.cache = Mock()
        
    def get_vacancies(self, query: str, **kwargs):
        return {"items": []}
    
    def get_vacancies_page(self, page: int, **kwargs):
        return {"items": []}
    
    def _get_empty_response(self):
        return {"items": []}
    
    def _validate_vacancy(self, vacancy_data):
        return True


class ConcreteFilterService:
    """Конкретная реализация фильтр-сервиса для тестов"""
    
    def __init__(self, strategy=None):
        self.strategy = strategy or Mock()
    
    def filter_by_company_ids(self, vacancies: List[Dict], company_ids: List[int]) -> List[Dict]:
        return [v for v in vacancies if v.get('company_id') in company_ids]
    
    def get_target_company_stats(self, vacancies: List[Dict]) -> Dict[str, Any]:
        return {"total": len(vacancies), "filtered": 0}


def create_mock_vacancy(vacancy_id: str = "1", title: str = "Test Job") -> Mock:
    """Создать мок вакансии"""
    vacancy = Mock()
    vacancy.id = vacancy_id
    vacancy.title = title
    vacancy.employer = Mock()
    vacancy.employer.name = "Test Company"
    vacancy.url = f"https://test.com/vacancy/{vacancy_id}"
    vacancy.is_valid = Mock(return_value=True)
    return vacancy


def create_test_items(count: int) -> List[Dict[str, Any]]:
    """Создать тестовые элементы для пагинации"""
    return [{"id": i, "title": f"Item {i}"} for i in range(count)]
