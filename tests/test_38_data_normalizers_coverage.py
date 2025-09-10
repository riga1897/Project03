#!/usr/bin/env python3
"""
Тесты модуля data_normalizers.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Тестирование всех возможных входных типов данных

Модуль содержит 4 чистые функции для нормализации данных:
- normalize_area_data: области/местоположения
- normalize_experience_data: опыт работы
- normalize_employment_data: тип занятости
- normalize_employer_data: данные работодателя
"""

import pytest
from typing import Dict, Any, Optional, Union

from src.utils.data_normalizers import (
    normalize_area_data,
    normalize_experience_data,
    normalize_employment_data,
    normalize_employer_data
)


class TestNormalizeAreaData:
    """100% покрытие функции normalize_area_data"""

    def test_normalize_area_data_with_none(self) -> None:
        """Покрытие: None input"""
        result = normalize_area_data(None)
        assert result is None

    def test_normalize_area_data_with_empty_string(self) -> None:
        """Покрытие: пустая строка"""
        result = normalize_area_data("")
        assert result is None

    def test_normalize_area_data_with_whitespace_string(self) -> None:
        """Покрытие: строка из пробелов"""
        result = normalize_area_data("   ")
        assert result is None

    def test_normalize_area_data_with_valid_string(self) -> None:
        """Покрытие: валидная строка"""
        result = normalize_area_data("Москва")
        assert result == "Москва"

    def test_normalize_area_data_with_padded_string(self) -> None:
        """Покрытие: строка с пробелами по краям"""
        result = normalize_area_data("  Санкт-Петербург  ")
        assert result == "Санкт-Петербург"

    def test_normalize_area_data_with_dict_name_key(self) -> None:
        """Покрытие: словарь с ключом 'name'"""
        area_dict = {"name": "Новосибирск"}
        result = normalize_area_data(area_dict)
        assert result == "Новосибирск"

    def test_normalize_area_data_with_dict_name_padded(self) -> None:
        """Покрытие: словарь с 'name' и пробелами"""
        area_dict = {"name": "  Екатеринбург  "}
        result = normalize_area_data(area_dict)
        assert result == "Екатеринбург"

    def test_normalize_area_data_with_dict_title_key(self) -> None:
        """Покрытие: словарь с ключом 'title' (fallback)"""
        area_dict = {"title": "Казань"}
        result = normalize_area_data(area_dict)
        assert result == "Казань"

    def test_normalize_area_data_with_dict_id_key(self) -> None:
        """Покрытие: словарь с ключом 'id' (второй fallback)"""
        area_dict = {"id": 123}
        result = normalize_area_data(area_dict)
        assert result == "123"

    def test_normalize_area_data_with_dict_priority_name_over_title(self) -> None:
        """Покрытие: приоритет 'name' над 'title'"""
        area_dict = {"name": "Москва", "title": "Столица"}
        result = normalize_area_data(area_dict)
        assert result == "Москва"  # name имеет приоритет

    def test_normalize_area_data_with_dict_priority_title_over_id(self) -> None:
        """Покрытие: приоритет 'title' над 'id'"""
        area_dict = {"title": "Владивосток", "id": 456}
        result = normalize_area_data(area_dict)
        assert result == "Владивосток"  # title имеет приоритет

    def test_normalize_area_data_with_dict_other_keys(self) -> None:
        """Покрытие: словарь с другими ключами -> str(dict)"""
        area_dict = {"region": "Far East", "code": "FE"}
        result = normalize_area_data(area_dict)
        expected = str(area_dict).strip()
        assert result == expected

    def test_normalize_area_data_with_empty_dict(self) -> None:
        """Покрытие: пустой словарь -> None"""
        result = normalize_area_data({})
        assert result is None

    def test_normalize_area_data_with_empty_name_fallback_title(self) -> None:
        """Покрытие: пустой name, переход к title"""
        area_dict = {"name": "", "title": "Ростов-на-Дону"}
        result = normalize_area_data(area_dict)
        assert result == "Ростов-на-Дону"

    def test_normalize_area_data_with_empty_title_fallback_id(self) -> None:
        """Покрытие: пустые name и title, переход к id"""
        area_dict = {"name": "", "title": "", "id": 789}
        result = normalize_area_data(area_dict)
        assert result == "789"

    def test_normalize_area_data_with_integer_input(self) -> None:
        """Покрытие: числовой input -> str()"""
        result = normalize_area_data(12345)  # type: ignore
        assert result == "12345"

    def test_normalize_area_data_with_list_input(self) -> None:
        """Покрытие: список -> str()"""
        result = normalize_area_data([1, 2, 3])  # type: ignore
        assert result == "[1, 2, 3]"

    def test_normalize_area_data_with_boolean_input(self) -> None:
        """Покрытие: bool -> str()"""
        result = normalize_area_data(True)  # type: ignore
        assert result == "True"

    def test_normalize_area_data_with_float_input(self) -> None:
        """Покрытие: float -> str()"""
        result = normalize_area_data(3.14)  # type: ignore
        assert result == "3.14"


class TestNormalizeExperienceData:
    """100% покрытие функции normalize_experience_data"""

    def test_normalize_experience_data_with_none(self) -> None:
        """Покрытие: None input"""
        result = normalize_experience_data(None)
        assert result is None

    def test_normalize_experience_data_with_empty_string(self) -> None:
        """Покрытие: пустая строка"""
        result = normalize_experience_data("")
        assert result is None

    def test_normalize_experience_data_with_valid_string(self) -> None:
        """Покрытие: валидная строка"""
        result = normalize_experience_data("От 1 года до 3 лет")
        assert result == "От 1 года до 3 лет"

    def test_normalize_experience_data_with_dict_name_key(self) -> None:
        """Покрытие: словарь с ключом 'name'"""
        exp_dict = {"name": "От 3 до 6 лет"}
        result = normalize_experience_data(exp_dict)
        assert result == "От 3 до 6 лет"

    def test_normalize_experience_data_with_dict_title_key(self) -> None:
        """Покрытие: словарь с ключом 'title'"""
        exp_dict = {"title": "Более 6 лет"}
        result = normalize_experience_data(exp_dict)
        assert result == "Более 6 лет"

    def test_normalize_experience_data_with_dict_id_key(self) -> None:
        """Покрытие: словарь с ключом 'id'"""
        exp_dict = {"id": "noExperience"}
        result = normalize_experience_data(exp_dict)
        assert result == "noExperience"

    def test_normalize_experience_data_with_dict_priority(self) -> None:
        """Покрытие: приоритет name > title > id"""
        exp_dict = {"name": "Junior", "title": "Начинающий", "id": "entry"}
        result = normalize_experience_data(exp_dict)
        assert result == "Junior"  # name имеет приоритет

    def test_normalize_experience_data_with_dict_other_keys(self) -> None:
        """Покрытие: словарь с другими ключами"""
        exp_dict = {"level": "senior", "years": 5}
        result = normalize_experience_data(exp_dict)
        expected = str(exp_dict).strip()
        assert result == expected

    def test_normalize_experience_data_with_empty_dict(self) -> None:
        """Покрытие: пустой словарь"""
        result = normalize_experience_data({})
        assert result is None

    def test_normalize_experience_data_with_integer_input(self) -> None:
        """Покрытие: числовой input"""
        result = normalize_experience_data(5)  # type: ignore
        assert result == "5"

    def test_normalize_experience_data_with_whitespace_string(self) -> None:
        """Покрытие: строка из пробелов"""
        result = normalize_experience_data("   ")
        assert result is None

    def test_normalize_experience_data_with_padded_string(self) -> None:
        """Покрытие: строка с пробелами по краям"""
        result = normalize_experience_data("  Нет опыта  ")
        assert result == "Нет опыта"


class TestNormalizeEmploymentData:
    """100% покрытие функции normalize_employment_data"""

    def test_normalize_employment_data_with_none(self) -> None:
        """Покрытие: None input"""
        result = normalize_employment_data(None)
        assert result is None

    def test_normalize_employment_data_with_empty_string(self) -> None:
        """Покрытие: пустая строка"""
        result = normalize_employment_data("")
        assert result is None

    def test_normalize_employment_data_with_valid_string(self) -> None:
        """Покрытие: валидная строка"""
        result = normalize_employment_data("Полная занятость")
        assert result == "Полная занятость"

    def test_normalize_employment_data_with_dict_name_key(self) -> None:
        """Покрытие: словарь с ключом 'name'"""
        emp_dict = {"name": "Частичная занятость"}
        result = normalize_employment_data(emp_dict)
        assert result == "Частичная занятость"

    def test_normalize_employment_data_with_dict_title_key(self) -> None:
        """Покрытие: словарь с ключом 'title'"""
        emp_dict = {"title": "Проектная работа"}
        result = normalize_employment_data(emp_dict)
        assert result == "Проектная работа"

    def test_normalize_employment_data_with_dict_type_key(self) -> None:
        """Покрытие: словарь с ключом 'type'"""
        emp_dict = {"type": "full"}
        result = normalize_employment_data(emp_dict)
        assert result == "full"

    def test_normalize_employment_data_with_dict_id_key(self) -> None:
        """Покрытие: словарь с ключом 'id'"""
        emp_dict = {"id": "part_time"}
        result = normalize_employment_data(emp_dict)
        assert result == "part_time"

    def test_normalize_employment_data_with_dict_priority(self) -> None:
        """Покрытие: приоритет name > title > type > id"""
        emp_dict = {
            "name": "Полная",
            "title": "Full-time",
            "type": "full",
            "id": "ft"
        }
        result = normalize_employment_data(emp_dict)
        assert result == "Полная"  # name имеет приоритет

    def test_normalize_employment_data_with_dict_title_over_type(self) -> None:
        """Покрытие: приоритет title над type"""
        emp_dict = {"title": "Удаленная", "type": "remote", "id": "rm"}
        result = normalize_employment_data(emp_dict)
        assert result == "Удаленная"  # title имеет приоритет

    def test_normalize_employment_data_with_dict_type_over_id(self) -> None:
        """Покрытие: приоритет type над id"""
        emp_dict = {"type": "contract", "id": "cnt"}
        result = normalize_employment_data(emp_dict)
        assert result == "contract"  # type имеет приоритет

    def test_normalize_employment_data_with_dict_other_keys(self) -> None:
        """Покрытие: словарь с другими ключами"""
        emp_dict = {"hours": 40, "schedule": "flexible"}
        result = normalize_employment_data(emp_dict)
        expected = str(emp_dict).strip()
        assert result == expected

    def test_normalize_employment_data_with_empty_dict(self) -> None:
        """Покрытие: пустой словарь"""
        result = normalize_employment_data({})
        assert result is None

    def test_normalize_employment_data_with_whitespace_string(self) -> None:
        """Покрытие: строка из пробелов"""
        result = normalize_employment_data("   ")
        assert result is None

    def test_normalize_employment_data_with_padded_string(self) -> None:
        """Покрытие: строка с пробелами по краям"""
        result = normalize_employment_data("  Стажировка  ")
        assert result == "Стажировка"

    def test_normalize_employment_data_with_integer_input(self) -> None:
        """Покрытие: числовой input"""
        result = normalize_employment_data(1)  # type: ignore
        assert result == "1"


class TestNormalizeEmployerData:
    """100% покрытие функции normalize_employer_data"""

    def test_normalize_employer_data_with_none(self) -> None:
        """Покрытие: None input"""
        result = normalize_employer_data(None)
        assert result is None

    def test_normalize_employer_data_with_empty_string(self) -> None:
        """Покрытие: пустая строка"""
        result = normalize_employer_data("")
        assert result is None

    def test_normalize_employer_data_with_valid_string(self) -> None:
        """Покрытие: валидная строка"""
        result = normalize_employer_data("Яндекс")
        assert result == "Яндекс"

    def test_normalize_employer_data_with_dict_name_key(self) -> None:
        """Покрытие: словарь с ключом 'name'"""
        emp_dict = {"name": "Mail.ru Group"}
        result = normalize_employer_data(emp_dict)
        assert result == "Mail.ru Group"

    def test_normalize_employer_data_with_dict_title_key(self) -> None:
        """Покрытие: словарь с ключом 'title'"""
        emp_dict = {"title": "OZON"}
        result = normalize_employer_data(emp_dict)
        assert result == "OZON"

    def test_normalize_employer_data_with_dict_firm_name_key(self) -> None:
        """Покрытие: словарь с ключом 'firm_name' (SuperJob)"""
        emp_dict = {"firm_name": "СберТех"}
        result = normalize_employer_data(emp_dict)
        assert result == "СберТех"

    def test_normalize_employer_data_with_dict_id_key(self) -> None:
        """Покрытие: словарь с ключом 'id'"""
        emp_dict = {"id": "company_123"}
        result = normalize_employer_data(emp_dict)
        assert result == "company_123"

    def test_normalize_employer_data_with_dict_priority(self) -> None:
        """Покрытие: приоритет name > title > firm_name > id"""
        emp_dict = {
            "name": "Тинькофф",
            "title": "Tinkoff Bank",
            "firm_name": "Тинькофф Банк",
            "id": "tinkoff"
        }
        result = normalize_employer_data(emp_dict)
        assert result == "Тинькофф"  # name имеет приоритет

    def test_normalize_employer_data_with_dict_title_over_firm_name(self) -> None:
        """Покрытие: приоритет title над firm_name"""
        emp_dict = {
            "title": "Авито",
            "firm_name": "Avito Group",
            "id": "avito"
        }
        result = normalize_employer_data(emp_dict)
        assert result == "Авито"  # title имеет приоритет

    def test_normalize_employer_data_with_dict_firm_name_over_id(self) -> None:
        """Покрытие: приоритет firm_name над id"""
        emp_dict = {"firm_name": "ВТБ", "id": "vtb"}
        result = normalize_employer_data(emp_dict)
        assert result == "ВТБ"  # firm_name имеет приоритет

    def test_normalize_employer_data_with_dict_other_keys(self) -> None:
        """Покрытие: словарь с другими ключами"""
        emp_dict = {"industry": "IT", "size": "1000+"}
        result = normalize_employer_data(emp_dict)
        expected = str(emp_dict).strip()
        assert result == expected

    def test_normalize_employer_data_with_empty_dict(self) -> None:
        """Покрытие: пустой словарь"""
        result = normalize_employer_data({})
        assert result is None

    def test_normalize_employer_data_with_whitespace_string(self) -> None:
        """Покрытие: строка из пробелов"""
        result = normalize_employer_data("   ")
        assert result is None

    def test_normalize_employer_data_with_padded_string(self) -> None:
        """Покрытие: строка с пробелами по краям"""
        result = normalize_employer_data("  JetBrains  ")
        assert result == "JetBrains"

    def test_normalize_employer_data_with_integer_input(self) -> None:
        """Покрытие: числовой input"""
        result = normalize_employer_data(999)  # type: ignore
        assert result == "999"

    def test_normalize_employer_data_with_empty_name_fallback_title(self) -> None:
        """Покрытие: пустой name, переход к title"""
        emp_dict = {"name": "", "title": "Альфа-Банк"}
        result = normalize_employer_data(emp_dict)
        assert result == "Альфа-Банк"

    def test_normalize_employer_data_with_empty_title_fallback_firm_name(self) -> None:
        """Покрытие: пустые name и title, переход к firm_name"""
        emp_dict = {"name": "", "title": "", "firm_name": "Сбербанк"}
        result = normalize_employer_data(emp_dict)
        assert result == "Сбербанк"

    def test_normalize_employer_data_with_empty_firm_name_fallback_id(self) -> None:
        """Покрытие: пустые name, title и firm_name, переход к id"""
        emp_dict = {"name": "", "title": "", "firm_name": "", "id": "sberbank"}
        result = normalize_employer_data(emp_dict)
        assert result == "sberbank"


class TestDataNormalizersEdgeCases:
    """Тестирование граничных случаев и комплексных сценариев"""

    def test_all_functions_with_complex_nested_dict(self) -> None:
        """Покрытие: сложные вложенные структуры данных"""
        complex_dict = {
            "nested": {"deep": {"value": "test"}},
            "list": [1, 2, 3]
        }

        # Все функции должны обрабатывать сложные объекты
        area_result = normalize_area_data(complex_dict)
        exp_result = normalize_experience_data(complex_dict)
        emp_result = normalize_employment_data(complex_dict)
        employer_result = normalize_employer_data(complex_dict)

        expected = str(complex_dict).strip()
        assert area_result == expected
        assert exp_result == expected
        assert emp_result == expected
        assert employer_result == expected

    def test_all_functions_with_zero_value(self) -> None:
        """Покрытие: число 0 - falsy значение возвращает None"""
        for func in [
            normalize_area_data,
            normalize_experience_data,
            normalize_employment_data,
            normalize_employer_data
        ]:
            result = func(0)  # type: ignore
            # 0 является falsy, поэтому `if not area_data:` возвращает None
            assert result is None

    def test_all_functions_with_false_boolean(self) -> None:
        """Покрытие: False - falsy значение возвращает None"""
        for func in [
            normalize_area_data,
            normalize_experience_data,
            normalize_employment_data,
            normalize_employer_data
        ]:
            result = func(False)  # type: ignore
            # False является falsy, поэтому `if not area_data:` возвращает None
            assert result is None

    def test_all_functions_with_empty_list(self) -> None:
        """Покрытие: пустой список - falsy значение возвращает None"""
        for func in [
            normalize_area_data,
            normalize_experience_data,
            normalize_employment_data,
            normalize_employer_data
        ]:
            result = func([])  # type: ignore
            # [] является falsy, поэтому `if not area_data:` возвращает None
            assert result is None

    def test_dict_with_none_values_in_priority_keys(self) -> None:
        """Покрытие: None значения в приоритетных ключах"""
        # area_data: name -> title -> id -> str(dict)
        area_dict = {"name": None, "title": None, "id": "fallback_id"}
        result = normalize_area_data(area_dict)
        assert result == "fallback_id"

        # experience_data: name -> title -> id -> str(dict)
        exp_dict = {"name": None, "title": "fallback_title", "id": "fallback_id"}
        result = normalize_experience_data(exp_dict)
        assert result == "fallback_title"

        # employment_data: name -> title -> type -> id -> str(dict)
        emp_dict = {"name": None, "title": None, "type": "fallback_type", "id": "fallback_id"}
        result = normalize_employment_data(emp_dict)
        assert result == "fallback_type"

        # employer_data: name -> title -> firm_name -> id -> str(dict)
        employer_dict = {"name": None, "title": None, "firm_name": "fallback_firm", "id": "fallback_id"}
        result = normalize_employer_data(employer_dict)
        assert result == "fallback_firm"


# Дополнительные интеграционные тесты
class TestIntegrationScenarios:
    """Тестирование реальных сценариев использования"""

    def test_hh_ru_area_format(self) -> None:
        """Тест формата данных HeadHunter для области"""
        hh_area = {"id": "1", "name": "Москва", "url": "https://api.hh.ru/areas/1"}
        result = normalize_area_data(hh_area)
        assert result == "Москва"

    def test_superjob_employer_format(self) -> None:
        """Тест формата данных SuperJob для работодателя"""
        sj_employer = {"id": 123, "firm_name": "Яндекс", "town": "Москва"}
        result = normalize_employer_data(sj_employer)
        assert result == "Яндекс"

    def test_mixed_api_experience_formats(self) -> None:
        """Тест различных форматов опыта из разных API"""
        # HH.ru формат
        hh_exp = {"id": "between1And3", "name": "От 1 года до 3 лет"}
        result = normalize_experience_data(hh_exp)
        assert result == "От 1 года до 3 лет"

        # SuperJob формат (строка)
        sj_exp = "Опыт работы от 3 лет"
        result = normalize_experience_data(sj_exp)
        assert result == "Опыт работы от 3 лет"

        # Кастомный формат
        custom_exp = {"title": "Senior level", "years": "5+"}
        result = normalize_experience_data(custom_exp)
        assert result == "Senior level"

    def test_employment_type_variations(self) -> None:
        """Тест различных вариантов типов занятости"""
        # Полные данные
        full_emp = {"id": "full", "name": "Полная занятость", "type": "fullTime"}
        result = normalize_employment_data(full_emp)
        assert result == "Полная занятость"

        # Только тип
        type_only = {"type": "partTime"}
        result = normalize_employment_data(type_only)
        assert result == "partTime"

        # Только ID
        id_only = {"id": "remote"}
        result = normalize_employment_data(id_only)
        assert result == "remote"