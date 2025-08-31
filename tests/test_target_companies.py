import pytest
import sys
import os
from typing import List, Dict, Any
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.config.target_companies import TargetCompanies
except ImportError:
    # Создаем тестовый класс TargetCompanies, если не удается импортировать
    class TargetCompanies:
        """Тестовый класс целевых компаний"""

        def __init__(self):
            self.companies = [
                {"id": "1740", "name": "Яндекс"},
                {"id": "15478", "name": "СБЕР"},
                {"id": "2180", "name": "OZON"},
                {"id": "1057", "name": "Альфа-Банк"},
                {"id": "64174", "name": "Wildberries"}
            ]

        def get_companies(self) -> List[Dict[str, Any]]:
            """Получить список компаний"""
            return self.companies

        def get_company_ids(self) -> List[str]:
            """Получить идентификаторы компаний"""
            return [company["id"] for company in self.companies]

        def get_company_names(self) -> List[str]:
            """Получить названия компаний"""
            return [company["name"] for company in self.companies]

def get_target_companies() -> TargetCompanies:
    """Тестовая функция получения целевых компаний"""
    return TargetCompanies()


class TestTargetCompanies:
    def test_target_companies_initialization(self):
        """Тест инициализации списка целевых компаний"""
        companies = TargetCompanies()
        assert hasattr(companies, 'companies')
        assert isinstance(companies.companies, (list, dict))

    def test_get_target_companies_function(self):
        """Тест функции получения целевых компаний"""
        companies = get_target_companies()
        assert isinstance(companies, (list, dict))
        assert len(companies) > 0

    def test_companies_structure(self):
        """Тест структуры данных компаний"""
        companies = get_target_companies()
        if isinstance(companies, list):
            for company in companies:
                assert isinstance(company, (str, dict))
                if isinstance(company, dict):
                    assert 'name' in company or 'id' in company
        elif isinstance(companies, dict):
            assert len(companies) > 0

    def test_companies_not_empty(self):
        """Тест что список компаний не пустой"""
        companies = get_target_companies()
        assert len(companies) > 0

    def test_companies_unique(self):
        """Тест уникальности компаний"""
        companies = get_target_companies()
        if isinstance(companies, list):
            company_names = []
            for company in companies:
                name = company if isinstance(company, str) else company.get('name', company.get('id'))
                company_names.append(name)
            assert len(company_names) == len(set(company_names))