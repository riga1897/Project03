#!/usr/bin/env python3
"""
Тесты модуля target_companies для 100% покрытия.

Покрывает все классы и функции в src/config/target_companies.py:
- CompanyInfo - dataclass с информацией о компании
- TargetCompanies - класс для работы с целевыми компаниями
- Все классовые методы и функции обратной совместимости
- TARGET_COMPANIES - константа для обратной совместимости
- get_target_company_ids, get_target_company_names - устаревшие функции

Модуль содержит статические данные и не требует I/O операций.
"""

import pytest
from typing import List, Optional, Set

# Импорты из реального кода для покрытия
from src.config.target_companies import (
    CompanyInfo,
    TargetCompanies,
    TARGET_COMPANIES,
    get_target_company_ids,
    get_target_company_names
)


class TestCompanyInfo:
    """100% покрытие CompanyInfo dataclass"""

    def test_company_info_all_fields(self):
        """Покрытие создания CompanyInfo со всеми полями"""
        company = CompanyInfo(
            name="Test Company",
            hh_id="123",
            sj_id="456",
            description="Test description"
        )
        
        assert company.name == "Test Company"
        assert company.hh_id == "123"
        assert company.sj_id == "456"
        assert company.description == "Test description"

    def test_company_info_minimal_fields(self):
        """Покрытие создания CompanyInfo с минимальными полями"""
        company = CompanyInfo(
            name="Minimal Company",
            hh_id="789"
        )
        
        assert company.name == "Minimal Company"
        assert company.hh_id == "789"
        assert company.sj_id is None  # Значение по умолчанию
        assert company.description == ""  # Значение по умолчанию

    def test_company_info_optional_sj_id(self):
        """Покрытие CompanyInfo с опциональным sj_id"""
        company = CompanyInfo(
            name="No SJ Company",
            hh_id="101112",
            sj_id=None,
            description="Company without SuperJob ID"
        )
        
        assert company.name == "No SJ Company"
        assert company.hh_id == "101112"
        assert company.sj_id is None
        assert company.description == "Company without SuperJob ID"

    def test_company_info_empty_description(self):
        """Покрытие CompanyInfo с пустым описанием"""
        company = CompanyInfo(
            name="Empty Desc Company",
            hh_id="131415",
            description=""
        )
        
        assert company.name == "Empty Desc Company"
        assert company.hh_id == "131415"
        assert company.description == ""

    def test_company_info_dataclass_behavior(self):
        """Покрытие поведения dataclass CompanyInfo"""
        company1 = CompanyInfo("Same", "1", "2", "desc")
        company2 = CompanyInfo("Same", "1", "2", "desc")
        company3 = CompanyInfo("Different", "1", "2", "desc")
        
        # Dataclass обеспечивает равенство по значениям
        assert company1 == company2
        assert company1 != company3
        
        # Проверяем строковое представление
        company_str = str(company1)
        assert "Same" in company_str
        assert "1" in company_str


class TestTargetCompanies:
    """100% покрытие TargetCompanies класса"""

    def test_companies_list_exists(self):
        """Покрытие существования списка COMPANIES"""
        companies = TargetCompanies.COMPANIES
        
        assert isinstance(companies, list)
        assert len(companies) > 0
        assert all(isinstance(company, CompanyInfo) for company in companies)

    def test_companies_count_expected(self):
        """Покрытие ожидаемого количества компаний (12)"""
        companies = TargetCompanies.COMPANIES
        
        # По документации должно быть 12 компаний
        assert len(companies) == 12

    def test_companies_required_fields(self):
        """Покрытие обязательных полей у всех компаний"""
        companies = TargetCompanies.COMPANIES
        
        for company in companies:
            assert company.name  # Не пустое название
            assert company.hh_id  # Не пустое HH ID
            # sj_id может быть None, это нормально

    def test_get_all_companies_returns_copy(self):
        """Покрытие того, что get_all_companies возвращает копию"""
        companies1 = TargetCompanies.get_all_companies()
        companies2 = TargetCompanies.get_all_companies()
        
        # Должны быть разными объектами (копии)
        assert companies1 is not companies2
        assert companies1 == companies2
        
        # Изменение возвращенной копии не должно влиять на оригинал
        companies1.pop()
        assert len(TargetCompanies.get_all_companies()) == 12

    def test_get_hh_ids_all_present(self):
        """Покрытие получения всех HH ID"""
        hh_ids = TargetCompanies.get_hh_ids()
        
        assert isinstance(hh_ids, list)
        assert len(hh_ids) == 12  # Все компании должны иметь HH ID
        assert all(isinstance(hh_id, str) for hh_id in hh_ids)
        assert all(hh_id for hh_id in hh_ids)  # Все ID не пустые

    def test_get_hh_ids_specific_values(self):
        """Покрытие конкретных значений HH ID"""
        hh_ids = TargetCompanies.get_hh_ids()
        
        # Проверяем некоторые известные HH ID
        assert "1740" in hh_ids  # Яндекс
        assert "78638" in hh_ids  # Тинькофф
        assert "3529" in hh_ids  # СБЕР

    def test_get_sj_ids_filtering(self):
        """Покрытие получения SJ ID с фильтрацией"""
        sj_ids = TargetCompanies.get_sj_ids()
        
        assert isinstance(sj_ids, list)
        assert all(isinstance(sj_id, str) for sj_id in sj_ids)
        assert all(sj_id for sj_id in sj_ids)  # Все ID не пустые
        
        # Количество может быть меньше 12, если не все компании есть в SuperJob
        assert len(sj_ids) <= 12

    def test_get_sj_ids_specific_values(self):
        """Покрытие конкретных значений SJ ID"""
        sj_ids = TargetCompanies.get_sj_ids()
        
        # Проверяем некоторые известные SJ ID
        assert "19421" in sj_ids  # Яндекс
        assert "2324" in sj_ids   # Тинькофф

    def test_get_company_names_all_present(self):
        """Покрытие получения всех названий компаний"""
        names = TargetCompanies.get_company_names()
        
        assert isinstance(names, list)
        assert len(names) == 12
        assert all(isinstance(name, str) for name in names)
        assert all(name for name in names)  # Все названия не пустые

    def test_get_company_names_specific_values(self):
        """Покрытие конкретных названий компаний"""
        names = TargetCompanies.get_company_names()
        
        # Проверяем некоторые известные названия
        assert "Яндекс" in names
        assert "Тинькофф" in names
        assert "СБЕР" in names
        assert "VK" in names

    def test_get_all_ids_union(self):
        """Покрытие получения объединения всех ID"""
        all_ids = TargetCompanies.get_all_ids()
        
        assert isinstance(all_ids, set)
        
        # Проверяем что включены HH ID
        hh_ids = TargetCompanies.get_hh_ids()
        for hh_id in hh_ids:
            assert hh_id in all_ids
        
        # Проверяем что включены SJ ID
        sj_ids = TargetCompanies.get_sj_ids()
        for sj_id in sj_ids:
            assert sj_id in all_ids

    def test_get_all_ids_no_duplicates(self):
        """Покрытие отсутствия дубликатов в get_all_ids"""
        all_ids = TargetCompanies.get_all_ids()
        all_ids_list = list(all_ids)
        
        # Set автоматически убирает дубликаты
        assert len(all_ids) == len(set(all_ids_list))

    def test_get_company_by_hh_id_found(self):
        """Покрытие поиска компании по HH ID - найдена"""
        # Берем первую компанию для тестирования
        first_company = TargetCompanies.COMPANIES[0]
        
        found_company = TargetCompanies.get_company_by_hh_id(first_company.hh_id)
        
        assert found_company is not None
        assert found_company == first_company
        assert found_company.name == first_company.name

    def test_get_company_by_hh_id_not_found(self):
        """Покрытие поиска компании по HH ID - не найдена"""
        result = TargetCompanies.get_company_by_hh_id("nonexistent_id")
        
        assert result is None

    def test_get_company_by_hh_id_specific_companies(self):
        """Покрытие поиска конкретных компаний по HH ID"""
        # Яндекс
        yandex = TargetCompanies.get_company_by_hh_id("1740")
        assert yandex is not None
        assert yandex.name == "Яндекс"
        
        # Тинькофф
        tinkoff = TargetCompanies.get_company_by_hh_id("78638")
        assert tinkoff is not None
        assert tinkoff.name == "Тинькофф"

    def test_get_company_by_sj_id_found(self):
        """Покрытие поиска компании по SJ ID - найдена"""
        # Найдем компанию с SJ ID
        company_with_sj = None
        for company in TargetCompanies.COMPANIES:
            if company.sj_id:
                company_with_sj = company
                break
        
        assert company_with_sj is not None  # Убеждаемся что есть компания с SJ ID
        
        found_company = TargetCompanies.get_company_by_sj_id(company_with_sj.sj_id)
        assert found_company is not None
        assert found_company == company_with_sj

    def test_get_company_by_sj_id_not_found(self):
        """Покрытие поиска компании по SJ ID - не найдена"""
        result = TargetCompanies.get_company_by_sj_id("nonexistent_sj_id")
        
        assert result is None

    def test_get_company_by_sj_id_specific_companies(self):
        """Покрытие поиска конкретных компаний по SJ ID"""
        # Яндекс
        yandex = TargetCompanies.get_company_by_sj_id("19421")
        assert yandex is not None
        assert yandex.name == "Яндекс"

    def test_is_target_company_hh_id(self):
        """Покрытие проверки целевой компании по HH ID"""
        # Известные HH ID
        assert TargetCompanies.is_target_company("1740")  # Яндекс
        assert TargetCompanies.is_target_company("78638")  # Тинькофф
        
        # Неизвестный ID
        assert not TargetCompanies.is_target_company("unknown_id")

    def test_is_target_company_sj_id(self):
        """Покрытие проверки целевой компании по SJ ID"""
        # Известные SJ ID
        assert TargetCompanies.is_target_company("19421")  # Яндекс SJ
        assert TargetCompanies.is_target_company("2324")   # Тинькофф SJ
        
        # Неизвестный SJ ID
        assert not TargetCompanies.is_target_company("unknown_sj_id")

    def test_find_company_by_exact_name_found(self):
        """Покрытие поиска компании по точному названию - найдена"""
        yandex = TargetCompanies.find_company_by_exact_name("Яндекс")
        assert yandex is not None
        assert yandex.name == "Яндекс"
        assert yandex.hh_id == "1740"

    def test_find_company_by_exact_name_case_insensitive(self):
        """Покрытие поиска компании по названию без учета регистра"""
        # Различные варианты регистра
        yandex1 = TargetCompanies.find_company_by_exact_name("яндекс")
        yandex2 = TargetCompanies.find_company_by_exact_name("ЯНДЕКС")
        yandex3 = TargetCompanies.find_company_by_exact_name("ЯнДеКс")
        
        assert yandex1 is not None
        assert yandex2 is not None
        assert yandex3 is not None
        assert yandex1.name == "Яндекс"
        assert yandex2.name == "Яндекс"
        assert yandex3.name == "Яндекс"

    def test_find_company_by_exact_name_not_found(self):
        """Покрытие поиска компании по названию - не найдена"""
        result = TargetCompanies.find_company_by_exact_name("Несуществующая Компания")
        assert result is None

    def test_find_company_by_exact_name_partial_match(self):
        """Покрытие что частичные совпадения не находятся"""
        # Частичные совпадения не должны работать
        result = TargetCompanies.find_company_by_exact_name("Янд")
        assert result is None
        
        result = TargetCompanies.find_company_by_exact_name("Яндекс Плюс")
        assert result is None

    def test_find_company_by_exact_name_all_companies(self):
        """Покрытие поиска всех компаний по точному названию"""
        all_companies = TargetCompanies.get_all_companies()
        
        for company in all_companies:
            found = TargetCompanies.find_company_by_exact_name(company.name)
            assert found is not None
            assert found.name == company.name
            assert found.hh_id == company.hh_id

    def test_get_company_count(self):
        """Покрытие получения количества компаний"""
        count = TargetCompanies.get_company_count()
        
        assert isinstance(count, int)
        assert count == 12
        assert count == len(TargetCompanies.COMPANIES)


class TestTargetCompaniesLegacyConstants:
    """Покрытие константы TARGET_COMPANIES для обратной совместимости"""

    def test_target_companies_constant_exists(self):
        """Покрытие существования константы TARGET_COMPANIES"""
        assert TARGET_COMPANIES is not None
        assert isinstance(TARGET_COMPANIES, list)

    def test_target_companies_constant_structure(self):
        """Покрытие структуры константы TARGET_COMPANIES"""
        assert len(TARGET_COMPANIES) == 12
        
        for company_dict in TARGET_COMPANIES:
            assert isinstance(company_dict, dict)
            assert "name" in company_dict
            assert "hh_id" in company_dict
            assert "sj_id" in company_dict
            assert "description" in company_dict

    def test_target_companies_constant_values(self):
        """Покрытие значений в константе TARGET_COMPANIES"""
        # Проверяем первую компанию (Яндекс)
        yandex_dict = TARGET_COMPANIES[0]
        assert yandex_dict["name"] == "Яндекс"
        assert yandex_dict["hh_id"] == "1740"
        assert yandex_dict["sj_id"] == "19421"
        assert "поисковой системы" in yandex_dict["description"]

    def test_target_companies_constant_consistency(self):
        """Покрытие соответствия константы и класса"""
        class_companies = TargetCompanies.get_all_companies()
        
        assert len(TARGET_COMPANIES) == len(class_companies)
        
        for i, company_dict in enumerate(TARGET_COMPANIES):
            class_company = class_companies[i]
            assert company_dict["name"] == class_company.name
            assert company_dict["hh_id"] == class_company.hh_id
            assert company_dict["sj_id"] == class_company.sj_id
            assert company_dict["description"] == class_company.description


class TestLegacyFunctions:
    """Покрытие устаревших функций для обратной совместимости"""

    def test_get_target_company_ids_function(self):
        """Покрытие устаревшей функции get_target_company_ids"""
        legacy_ids = get_target_company_ids()
        modern_ids = TargetCompanies.get_hh_ids()
        
        assert legacy_ids == modern_ids
        assert isinstance(legacy_ids, list)
        assert len(legacy_ids) == 12

    def test_get_target_company_names_function(self):
        """Покрытие устаревшей функции get_target_company_names"""
        legacy_names = get_target_company_names()
        modern_names = TargetCompanies.get_company_names()
        
        assert legacy_names == modern_names
        assert isinstance(legacy_names, list)
        assert len(legacy_names) == 12

    def test_legacy_functions_specific_values(self):
        """Покрытие конкретных значений в устаревших функциях"""
        ids = get_target_company_ids()
        names = get_target_company_names()
        
        # Проверяем известные значения
        assert "1740" in ids  # Яндекс HH ID
        assert "Яндекс" in names  # Яндекс название


class TestTargetCompaniesEdgeCases:
    """Покрытие граничных случаев и особых сценариев"""

    def test_companies_with_missing_sj_id(self):
        """Покрытие компаний без SJ ID"""
        companies_without_sj = [
            company for company in TargetCompanies.COMPANIES 
            if company.sj_id is None
        ]
        
        # Проверяем что такие компании корректно обрабатываются
        sj_ids = TargetCompanies.get_sj_ids()
        for company in companies_without_sj:
            assert company.hh_id not in sj_ids  # HH ID не должно попасть в SJ IDs

    def test_empty_string_searches(self):
        """Покрытие поиска с пустыми строками"""
        # Поиск по пустой строке
        result = TargetCompanies.find_company_by_exact_name("")
        assert result is None
        
        result = TargetCompanies.get_company_by_hh_id("")
        assert result is None
        
        result = TargetCompanies.get_company_by_sj_id("")
        assert result is None
        
        assert not TargetCompanies.is_target_company("")

    def test_whitespace_in_names(self):
        """Покрытие поиска с пробелами в названиях"""
        # Названия с пробелами в начале/конце не должны находиться
        result = TargetCompanies.find_company_by_exact_name(" Яндекс ")
        assert result is None
        
        result = TargetCompanies.find_company_by_exact_name("Яндекс ")
        assert result is None
        
        result = TargetCompanies.find_company_by_exact_name(" Яндекс")
        assert result is None

    def test_unique_company_ids(self):
        """Покрытие уникальности ID компаний"""
        hh_ids = TargetCompanies.get_hh_ids()
        sj_ids = TargetCompanies.get_sj_ids()
        
        # HH ID должны быть уникальными
        assert len(hh_ids) == len(set(hh_ids))
        
        # SJ ID должны быть уникальными
        assert len(sj_ids) == len(set(sj_ids))

    def test_company_names_uniqueness(self):
        """Покрытие уникальности названий компаний"""
        names = TargetCompanies.get_company_names()
        
        # Названия должны быть уникальными
        assert len(names) == len(set(names))


class TestTargetCompaniesIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    def test_full_company_lookup_workflow(self):
        """Покрытие полного процесса поиска компании"""
        # Получаем все компании
        all_companies = TargetCompanies.get_all_companies()
        
        for company in all_companies:
            # Поиск по HH ID
            found_by_hh = TargetCompanies.get_company_by_hh_id(company.hh_id)
            assert found_by_hh == company
            
            # Поиск по названию
            found_by_name = TargetCompanies.find_company_by_exact_name(company.name)
            assert found_by_name == company
            
            # Проверка что это целевая компания
            assert TargetCompanies.is_target_company(company.hh_id)
            
            # Поиск по SJ ID (если есть)
            if company.sj_id:
                found_by_sj = TargetCompanies.get_company_by_sj_id(company.sj_id)
                assert found_by_sj == company
                assert TargetCompanies.is_target_company(company.sj_id)

    def test_cross_method_consistency(self):
        """Покрытие согласованности между различными методами"""
        # Количество должно быть согласованным
        count = TargetCompanies.get_company_count()
        companies = TargetCompanies.get_all_companies()
        names = TargetCompanies.get_company_names()
        hh_ids = TargetCompanies.get_hh_ids()
        
        assert count == len(companies)
        assert count == len(names)
        assert count == len(hh_ids)
        
        # Все HH ID должны быть в get_all_ids
        all_ids = TargetCompanies.get_all_ids()
        for hh_id in hh_ids:
            assert hh_id in all_ids

    def test_data_integrity(self):
        """Покрытие целостности данных"""
        companies = TargetCompanies.get_all_companies()
        
        for company in companies:
            # Обязательные поля не должны быть пустыми
            assert company.name.strip()
            assert company.hh_id.strip()
            
            # Если есть SJ ID, оно не должно быть пустым
            if company.sj_id:
                assert company.sj_id.strip()
            
            # Description может быть пустым, но не None
            assert company.description is not None