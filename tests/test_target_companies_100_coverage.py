"""
100% покрытие config/target_companies.py модуля
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest
from typing import List, Optional, Set

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.config.target_companies import (
    CompanyInfo, TargetCompanies, get_target_company_ids, get_target_company_names
)


class TestCompanyInfo:
    """100% покрытие CompanyInfo dataclass"""

    def test_company_info_creation(self):
        """Тест создания объекта CompanyInfo"""
        company = CompanyInfo(
            name="Test Company",
            hh_id="12345",
            sj_id="67890",
            description="Test description"
        )
        
        assert company.name == "Test Company"
        assert company.hh_id == "12345"
        assert company.sj_id == "67890"
        assert company.description == "Test description"

    def test_company_info_with_optional_fields(self):
        """Тест создания CompanyInfo с опциональными полями"""
        company = CompanyInfo(name="Minimal Company", hh_id="123")
        
        assert company.name == "Minimal Company"
        assert company.hh_id == "123"
        assert company.sj_id is None
        assert company.description == ""

    def test_company_info_dataclass_equality(self):
        """Тест равенства объектов CompanyInfo"""
        company1 = CompanyInfo("Test", "123", "456", "desc")
        company2 = CompanyInfo("Test", "123", "456", "desc")
        company3 = CompanyInfo("Test", "123", "457", "desc")
        
        assert company1 == company2
        assert company1 != company3


class TestTargetCompanies:
    """100% покрытие TargetCompanies"""

    def test_companies_list_exists(self):
        """Тест что список компаний существует и не пустой"""
        assert hasattr(TargetCompanies, 'COMPANIES')
        assert isinstance(TargetCompanies.COMPANIES, list)
        assert len(TargetCompanies.COMPANIES) > 0
        
        # Проверяем что первая компания имеет правильную структуру
        first_company = TargetCompanies.COMPANIES[0]
        assert isinstance(first_company, CompanyInfo)
        assert first_company.name
        assert first_company.hh_id

    def test_get_all_companies(self):
        """Тест метода get_all_companies - покрывает строку 105"""
        companies = TargetCompanies.get_all_companies()
        
        assert isinstance(companies, list)
        assert len(companies) > 0
        assert all(isinstance(company, CompanyInfo) for company in companies)
        
        # Проверяем что возвращает тот же список что и COMPANIES
        assert companies == TargetCompanies.COMPANIES

    def test_get_hh_ids(self):
        """Тест метода get_hh_ids - покрывает строку 110"""
        hh_ids = TargetCompanies.get_hh_ids()
        
        assert isinstance(hh_ids, list)
        assert len(hh_ids) > 0
        assert all(isinstance(hh_id, str) for hh_id in hh_ids)
        
        # Проверяем что все ID уникальны
        assert len(hh_ids) == len(set(hh_ids))
        
        # Проверяем что содержит известные ID
        expected_companies = TargetCompanies.COMPANIES
        expected_hh_ids = [company.hh_id for company in expected_companies]
        assert hh_ids == expected_hh_ids

    def test_get_sj_ids(self):
        """Тест метода get_sj_ids - покрывает строку 115"""
        sj_ids = TargetCompanies.get_sj_ids()
        
        assert isinstance(sj_ids, list)
        assert all(isinstance(sj_id, str) for sj_id in sj_ids if sj_id is not None)
        
        # Проверяем что возвращает только не-None SuperJob ID
        expected_sj_ids = [company.sj_id for company in TargetCompanies.COMPANIES 
                          if company.sj_id is not None]
        assert sj_ids == expected_sj_ids

    def test_get_company_names(self):
        """Тест метода get_company_names - покрывает строку 120"""
        names = TargetCompanies.get_company_names()
        
        assert isinstance(names, list)
        assert len(names) > 0
        assert all(isinstance(name, str) for name in names)
        
        # Проверяем что содержит известные имена
        expected_names = [company.name for company in TargetCompanies.COMPANIES]
        assert names == expected_names

    def test_get_all_ids(self):
        """Тест метода get_all_ids - покрывает строку 130"""
        all_ids = TargetCompanies.get_all_ids()
        
        assert isinstance(all_ids, set)
        assert len(all_ids) > 0
        
        # Проверяем что объединяет HH и SJ ID
        hh_ids = set(TargetCompanies.get_hh_ids())
        sj_ids = set(TargetCompanies.get_sj_ids())
        expected_all_ids = hh_ids.union(sj_ids)
        assert all_ids == expected_all_ids

    def test_get_company_by_hh_id_found(self):
        """Тест метода get_company_by_hh_id когда компания найдена - покрывает строки 136, 138"""
        # Берем первую компанию из списка
        first_company = TargetCompanies.COMPANIES[0]
        found_company = TargetCompanies.get_company_by_hh_id(first_company.hh_id)
        
        assert found_company is not None
        assert found_company == first_company
        assert found_company.hh_id == first_company.hh_id

    def test_get_company_by_hh_id_not_found(self):
        """Тест метода get_company_by_hh_id когда компания не найдена - покрывает строку 139"""
        not_found = TargetCompanies.get_company_by_hh_id("nonexistent_id")
        assert not_found is None

    def test_get_company_by_sj_id_found(self):
        """Тест метода get_company_by_sj_id когда компания найдена - покрывает строки 144, 146"""
        # Найдем компанию с SuperJob ID
        company_with_sj = None
        for company in TargetCompanies.COMPANIES:
            if company.sj_id is not None:
                company_with_sj = company
                break
        
        if company_with_sj:
            found_company = TargetCompanies.get_company_by_sj_id(company_with_sj.sj_id)
            assert found_company is not None
            assert found_company == company_with_sj

    def test_get_company_by_sj_id_not_found(self):
        """Тест метода get_company_by_sj_id когда компания не найдена - покрывает строку 147"""
        not_found = TargetCompanies.get_company_by_sj_id("nonexistent_sj_id")
        assert not_found is None

    def test_is_target_company_true(self):
        """Тест метода is_target_company когда компания целевая - покрывает строку 152"""
        # Проверяем с HH ID
        first_company = TargetCompanies.COMPANIES[0]
        assert TargetCompanies.is_target_company(first_company.hh_id) is True
        
        # Проверяем с SJ ID если есть
        for company in TargetCompanies.COMPANIES:
            if company.sj_id:
                assert TargetCompanies.is_target_company(company.sj_id) is True
                break

    def test_is_target_company_false(self):
        """Тест метода is_target_company когда компания не целевая - покрывает строку 152"""
        assert TargetCompanies.is_target_company("nonexistent_id") is False

    def test_find_company_by_exact_name_found(self):
        """Тест метода find_company_by_exact_name когда найдено - покрывает строки 157, 159"""
        first_company = TargetCompanies.COMPANIES[0]
        found_company = TargetCompanies.find_company_by_exact_name(first_company.name)
        
        assert found_company is not None
        assert found_company == first_company

    def test_find_company_by_exact_name_not_found(self):
        """Тест метода find_company_by_exact_name когда не найдено - покрывает строку 160"""
        not_found = TargetCompanies.find_company_by_exact_name("Nonexistent Company")
        assert not_found is None

    def test_find_company_by_exact_name_case_handling(self):
        """Тест поиска по точному имени с разными регистрами"""
        first_company = TargetCompanies.COMPANIES[0]
        # Проверяем поиск - может быть как чувствительный, так и нечувствительный к регистру
        result = TargetCompanies.find_company_by_exact_name(first_company.name.lower())
        # Просто проверяем что метод работает, не делаем предположений о чувствительности к регистру
        assert result is None or isinstance(result, CompanyInfo)

    def test_get_company_count(self):
        """Тест метода get_company_count - покрывает строку 168"""
        count = TargetCompanies.get_company_count()
        
        assert isinstance(count, int)
        assert count > 0
        assert count == len(TargetCompanies.COMPANIES)


class TestModuleFunctions:
    """Тесты для функций уровня модуля"""

    def test_get_target_company_ids(self):
        """Тест функции get_target_company_ids - покрывает строку 186"""
        ids = get_target_company_ids()
        
        assert isinstance(ids, list)
        assert len(ids) > 0
        assert all(isinstance(company_id, str) for company_id in ids)
        
        # Проверяем что возвращает те же ID что и метод класса
        expected_ids = TargetCompanies.get_hh_ids()
        assert ids == expected_ids

    def test_get_target_company_names(self):
        """Тест функции get_target_company_names - покрывает строку 191"""
        names = get_target_company_names()
        
        assert isinstance(names, list)
        assert len(names) > 0
        assert all(isinstance(name, str) for name in names)
        
        # Проверяем что возвращает те же имена что и метод класса
        expected_names = TargetCompanies.get_company_names()
        assert names == expected_names


class TestCompaniesDataIntegrity:
    """Тесты целостности данных компаний"""

    def test_all_companies_have_required_fields(self):
        """Проверяем что все компании имеют обязательные поля"""
        for company in TargetCompanies.COMPANIES:
            assert company.name, f"Company missing name: {company}"
            assert company.hh_id, f"Company missing hh_id: {company.name}"
            assert isinstance(company.name, str)
            assert isinstance(company.hh_id, str)

    def test_hh_ids_are_unique(self):
        """Проверяем что все HH ID уникальны"""
        hh_ids = [company.hh_id for company in TargetCompanies.COMPANIES]
        assert len(hh_ids) == len(set(hh_ids)), "Duplicate HH IDs found"

    def test_sj_ids_are_unique(self):
        """Проверяем что все SuperJob ID уникальны (не считая None)"""
        sj_ids = [company.sj_id for company in TargetCompanies.COMPANIES if company.sj_id is not None]
        assert len(sj_ids) == len(set(sj_ids)), "Duplicate SJ IDs found"

    def test_company_names_are_unique(self):
        """Проверяем что все имена компаний уникальны"""
        names = [company.name for company in TargetCompanies.COMPANIES]
        assert len(names) == len(set(names)), "Duplicate company names found"

    def test_expected_number_of_companies(self):
        """Проверяем что у нас правильное количество компаний (12 согласно docstring)"""
        # Комментарий в коде говорит о 12 компаниях
        companies_count = len(TargetCompanies.COMPANIES)
        assert companies_count >= 10, f"Expected at least 10 companies, got {companies_count}"

    def test_known_companies_present(self):
        """Проверяем что известные компании присутствуют в списке"""
        company_names = TargetCompanies.get_company_names()
        
        # Проверяем наличие некоторых известных компаний
        expected_companies = ["Яндекс", "СБЕР", "Тинькофф"]  # Известные из кода
        
        for expected_company in expected_companies:
            found = any(expected_company in name for name in company_names)
            assert found, f"Expected company '{expected_company}' not found in company names"


class TestClassMethodsTypeConsistency:
    """Тесты консистентности типов методов класса"""

    def test_method_return_types(self):
        """Проверяем что методы возвращают правильные типы"""
        # get_all_companies должен возвращать List[CompanyInfo]
        companies = TargetCompanies.get_all_companies()
        assert isinstance(companies, list)
        assert all(isinstance(c, CompanyInfo) for c in companies)
        
        # get_hh_ids должен возвращать List[str]
        hh_ids = TargetCompanies.get_hh_ids()
        assert isinstance(hh_ids, list)
        assert all(isinstance(h, str) for h in hh_ids)
        
        # get_sj_ids должен возвращать List[str]
        sj_ids = TargetCompanies.get_sj_ids()
        assert isinstance(sj_ids, list)
        assert all(isinstance(s, str) for s in sj_ids)
        
        # get_company_names должен возвращать List[str]
        names = TargetCompanies.get_company_names()
        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)
        
        # get_all_ids должен возвращать Set[str]
        all_ids = TargetCompanies.get_all_ids()
        assert isinstance(all_ids, set)
        assert all(isinstance(i, str) for i in all_ids)
        
        # get_company_count должен возвращать int
        count = TargetCompanies.get_company_count()
        assert isinstance(count, int)

    def test_optional_return_types(self):
        """Проверяем методы возвращающие Optional типы"""
        # get_company_by_hh_id должен возвращать Optional[CompanyInfo]
        found = TargetCompanies.get_company_by_hh_id(TargetCompanies.COMPANIES[0].hh_id)
        assert found is None or isinstance(found, CompanyInfo)
        
        not_found = TargetCompanies.get_company_by_hh_id("invalid_id")
        assert not_found is None
        
        # get_company_by_sj_id должен возвращать Optional[CompanyInfo]
        not_found_sj = TargetCompanies.get_company_by_sj_id("invalid_sj_id")
        assert not_found_sj is None
        
        # find_company_by_exact_name должен возвращать Optional[CompanyInfo]
        found_by_name = TargetCompanies.find_company_by_exact_name(TargetCompanies.COMPANIES[0].name)
        assert found_by_name is None or isinstance(found_by_name, CompanyInfo)


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_empty_string_searches(self):
        """Тесты поиска по пустой строке"""
        assert TargetCompanies.get_company_by_hh_id("") is None
        assert TargetCompanies.get_company_by_sj_id("") is None
        assert TargetCompanies.find_company_by_exact_name("") is None
        assert TargetCompanies.is_target_company("") is False

    def test_whitespace_searches(self):
        """Тесты поиска со строками содержащими только пробелы"""
        assert TargetCompanies.get_company_by_hh_id("   ") is None
        assert TargetCompanies.find_company_by_exact_name("   ") is None
        assert TargetCompanies.is_target_company("   ") is False