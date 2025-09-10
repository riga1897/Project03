#!/usr/bin/env python3
"""
Тесты утилит нормализации данных для 100% покрытия.

Покрывает все функции в src/utils/data_normalizers.py:
- normalize_area_data - нормализация данных области
- normalize_experience_data - нормализация данных опыта
- normalize_employment_data - нормализация данных занятости
- normalize_employer_data - нормализация данных работодателя (строковое представление)

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""


# Импорты из реального кода для покрытия
from src.utils.data_normalizers import (
    normalize_area_data,
    normalize_experience_data,
    normalize_employment_data,
    normalize_employer_data
)


class TestNormalizeAreaData:
    """100% покрытие normalize_area_data"""

    def test_normalize_area_none(self) -> None:
        """Покрытие None входных данных"""
        result = normalize_area_data(None)
        assert result is None

    def test_normalize_area_empty_string(self) -> None:
        """Покрытие пустой строки"""
        result = normalize_area_data("")
        assert result is None

    def test_normalize_area_whitespace_string(self) -> None:
        """Покрытие строки из пробелов"""
        result = normalize_area_data("   ")
        assert result is None

    def test_normalize_area_valid_string(self) -> None:
        """Покрытие валидной строки"""
        result = normalize_area_data("Москва")
        assert result == "Москва"

    def test_normalize_area_string_with_whitespace(self) -> None:
        """Покрытие строки с пробелами"""
        result = normalize_area_data("  Санкт-Петербург  ")
        assert result == "Санкт-Петербург"

    def test_normalize_area_dict_with_name(self) -> None:
        """Покрытие словаря с полем name"""
        data = {"name": "Екатеринбург", "id": "1"}
        result = normalize_area_data(data)
        assert result == "Екатеринбург"

    def test_normalize_area_dict_with_name_whitespace(self) -> None:
        """Покрытие словаря с name содержащим пробелы"""
        data = {"name": "  Новосибирск  "}
        result = normalize_area_data(data)
        assert result == "Новосибирск"

    def test_normalize_area_dict_with_title(self) -> None:
        """Покрытие словаря с полем title (fallback)"""
        data = {"title": "Казань", "id": "2"}
        result = normalize_area_data(data)
        assert result == "Казань"

    def test_normalize_area_dict_with_id_only(self) -> None:
        """Покрытие словаря только с id"""
        data = {"id": "123"}
        result = normalize_area_data(data)
        assert result == "123"

    def test_normalize_area_dict_empty(self) -> None:
        """Покрытие пустого словаря"""
        result = normalize_area_data({})
        assert result is None

    def test_normalize_area_dict_with_other_keys(self) -> None:
        """Покрытие словаря с другими ключами"""
        data = {"some_key": "value", "another": "data"}
        result = normalize_area_data(data)
        assert result == str(data)

    def test_normalize_area_other_type(self) -> None:
        """Покрытие других типов данных"""
        result = normalize_area_data(123)
        assert result == "123"

    def test_normalize_area_other_type_empty(self) -> None:
        """Покрытие других типов, приводящих к пустой строке"""
        result = normalize_area_data(0)
        assert result is None


class TestNormalizeExperienceData:
    """100% покрытие normalize_experience_data"""

    def test_normalize_experience_none(self) -> None:
        """Покрытие None входных данных"""
        result = normalize_experience_data(None)
        assert result is None

    def test_normalize_experience_empty_string(self) -> None:
        """Покрытие пустой строки"""
        result = normalize_experience_data("")
        assert result is None

    def test_normalize_experience_valid_string(self) -> None:
        """Покрытие валидной строки"""
        result = normalize_experience_data("3-6 лет")
        assert result == "3-6 лет"

    def test_normalize_experience_string_with_whitespace(self) -> None:
        """Покрытие строки с пробелами"""
        result = normalize_experience_data("  Без опыта  ")
        assert result == "Без опыта"

    def test_normalize_experience_dict_with_name(self) -> None:
        """Покрытие словаря с полем name"""
        data = {"name": "От 1 года до 3 лет", "id": "between1And3"}
        result = normalize_experience_data(data)
        assert result == "От 1 года до 3 лет"

    def test_normalize_experience_dict_with_title(self) -> None:
        """Покрытие словаря с полем title"""
        data = {"title": "Более 6 лет", "id": "moreThan6"}
        result = normalize_experience_data(data)
        assert result == "Более 6 лет"

    def test_normalize_experience_dict_with_id_only(self) -> None:
        """Покрытие словаря только с id"""
        data = {"id": "noExperience"}
        result = normalize_experience_data(data)
        assert result == "noExperience"

    def test_normalize_experience_dict_empty(self) -> None:
        """Покрытие пустого словаря"""
        result = normalize_experience_data({})
        assert result is None

    def test_normalize_experience_other_type(self) -> None:
        """Покрытие других типов данных"""
        result = normalize_experience_data(5)
        assert result == "5"


class TestNormalizeEmploymentData:
    """100% покрытие normalize_employment_data"""

    def test_normalize_employment_none(self) -> None:
        """Покрытие None входных данных"""
        result = normalize_employment_data(None)
        assert result is None

    def test_normalize_employment_valid_string(self) -> None:
        """Покрытие валидной строки"""
        result = normalize_employment_data("Полная занятость")
        assert result == "Полная занятость"

    def test_normalize_employment_dict_with_name(self) -> None:
        """Покрытие словаря с полем name"""
        data = {"name": "Частичная занятость", "id": "part"}
        result = normalize_employment_data(data)
        assert result == "Частичная занятость"

    def test_normalize_employment_dict_with_title(self) -> None:
        """Покрытие словаря с полем title"""
        data = {"title": "Проектная работа", "id": "project"}
        result = normalize_employment_data(data)
        assert result == "Проектная работа"

    def test_normalize_employment_dict_with_id_only(self) -> None:
        """Покрытие словаря только с id"""
        data = {"id": "full"}
        result = normalize_employment_data(data)
        assert result == "full"

    def test_normalize_employment_dict_empty(self) -> None:
        """Покрытие пустого словаря"""
        result = normalize_employment_data({})
        assert result is None

    def test_normalize_employment_dict_with_type(self) -> None:
        """Покрытие словаря с полем type"""
        data = {"type": "Стажировка", "id": "intern"}
        result = normalize_employment_data(data)
        assert result == "Стажировка"


class TestNormalizeEmployerData:
    """100% покрытие normalize_employer_data"""

    def test_normalize_employer_none(self) -> None:
        """Покрытие None входных данных"""
        result = normalize_employer_data(None)
        assert result is None

    def test_normalize_employer_empty_dict(self) -> None:
        """Покрытие пустого словаря"""
        result = normalize_employer_data({})
        assert result is None

    def test_normalize_employer_string(self) -> None:
        """Покрытие строкового входа"""
        result = normalize_employer_data("Яндекс")
        assert result == "Яндекс"

    def test_normalize_employer_empty_string(self) -> None:
        """Покрытие пустой строки"""
        result = normalize_employer_data("")
        assert result is None

    def test_normalize_employer_name_only(self) -> None:
        """Покрытие данных только с именем"""
        data = {"name": "Google"}
        result = normalize_employer_data(data)
        assert result == "Google"

    def test_normalize_employer_with_title(self) -> None:
        """Покрытие данных с полем title"""
        data = {"title": "Mail.ru Group"}
        result = normalize_employer_data(data)
        assert result == "Mail.ru Group"

    def test_normalize_employer_with_firm_name(self) -> None:
        """Покрытие данных с полем firm_name (SuperJob)"""
        data = {"firm_name": "Сбербанк"}
        result = normalize_employer_data(data)
        assert result == "Сбербанк"

    def test_normalize_employer_with_id_only(self) -> None:
        """Покрытие данных только с id"""
        data = {"id": "123"}
        result = normalize_employer_data(data)
        assert result == "123"

    def test_normalize_employer_priority_order(self) -> None:
        """Покрытие приоритета полей: name > title > firm_name > id"""
        data = {
            "name": "Primary Name",
            "title": "Secondary Title",
            "firm_name": "Tertiary Firm",
            "id": "Fourth ID"
        }
        result = normalize_employer_data(data)
        assert result == "Primary Name"

    def test_normalize_employer_fallback_to_title(self) -> None:
        """Покрытие fallback к title"""
        data = {"title": "Title Only", "id": "123"}
        result = normalize_employer_data(data)
        assert result == "Title Only"

    def test_normalize_employer_fallback_to_firm_name(self) -> None:
        """Покрытие fallback к firm_name"""
        data = {"firm_name": "Firm Name Only", "id": "456"}
        result = normalize_employer_data(data)
        assert result == "Firm Name Only"

    def test_normalize_employer_other_keys(self) -> None:
        """Покрытие других ключей в словаре"""
        data = {"some_key": "value", "other": "data"}
        result = normalize_employer_data(data)
        assert result == str(data)


class TestEdgeCasesAndIntegration:
    """Покрытие граничных случаев и интеграционных сценариев"""

    def test_all_normalizers_with_false_values(self) -> None:
        """Покрытие всех нормализаторов с ложными значениями"""
        false_values = [False, 0, "", [], {}]

        for value in false_values:
            # Большинство нормализаторов должны вернуть None для ложных значений
            assert normalize_area_data(value) is None or normalize_area_data(value) == "False"
            assert normalize_experience_data(value) is None or normalize_experience_data(value) == "False"
            assert normalize_employment_data(value) is None or normalize_employment_data(value) == "False"
            assert normalize_employer_data(value) is None or normalize_employer_data(value) == "False"

    def test_unicode_and_special_characters(self) -> None:
        """Покрытие Unicode и специальных символов"""
        unicode_text = "Москва 🏢 Center"

        # Тестируем обработку Unicode в строковых нормализаторах
        assert normalize_area_data(unicode_text) == unicode_text
        assert normalize_experience_data(unicode_text) == unicode_text
        assert normalize_employment_data(unicode_text) == unicode_text
        assert normalize_employer_data(unicode_text) == unicode_text

    def test_very_long_strings(self) -> None:
        """Покрытие очень длинных строк"""
        long_string = "A" * 1000

        # Все строковые нормализаторы должны обработать длинные строки
        assert normalize_area_data(long_string) == long_string
        assert normalize_experience_data(long_string) == long_string
        assert normalize_employment_data(long_string) == long_string
        assert normalize_employer_data(long_string) == long_string

    def test_nested_dict_structures(self) -> None:
        """Покрытие вложенных структур данных"""
        nested_data = {
            "name": "Valid Name",
            "nested": {
                "deep": {
                    "value": "should_be_ignored"
                }
            }
        }

        # Все словарные нормализаторы должны извлекать только нужные поля
        assert normalize_area_data(nested_data) == "Valid Name"
        assert normalize_experience_data(nested_data) == "Valid Name"
        assert normalize_employment_data(nested_data) == "Valid Name"
        assert normalize_employer_data(nested_data) == "Valid Name"

    def test_other_types_coverage(self) -> None:
        """Покрытие других типов данных для полного покрытия"""
        # Тестируем числовые значения
        assert normalize_area_data(123) == "123"
        assert normalize_experience_data(456) == "456"
        assert normalize_employment_data(789) == "789"
        assert normalize_employer_data(999) == "999"

        # Тестируем булевы значения
        assert normalize_area_data(True) == "True"
        assert normalize_experience_data(True) == "True"
        assert normalize_employment_data(True) == "True"
        assert normalize_employer_data(True) == "True"