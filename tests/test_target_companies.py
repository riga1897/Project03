
import pytest
from src.config.target_companies import TargetCompanies, get_target_companies


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
