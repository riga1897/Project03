"""
Комплексные тесты для модуля data_normalizers
"""

import os
import sys
from unittest.mock import MagicMock

# Мокаем psycopg2 перед импортом
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.sql'] = MagicMock()

# Добавляем путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import data_normalizers


class TestDataNormalizers:
    """Тесты для нормализации данных"""
    
    def test_normalize_area_data_none(self):
        """Тест нормализации None области"""
        result = data_normalizers.normalize_area_data(None)
        assert result is None
    
    def test_normalize_area_data_empty_string(self):
        """Тест нормализации пустой строки"""
        result = data_normalizers.normalize_area_data("")
        assert result is None
    
    def test_normalize_area_data_whitespace_string(self):
        """Тест нормализации строки с пробелами"""
        result = data_normalizers.normalize_area_data("   ")
        assert result is None
    
    def test_normalize_area_data_valid_string(self):
        """Тест нормализации валидной строки"""
        result = data_normalizers.normalize_area_data("  Москва  ")
        assert result == "Москва"
    
    def test_normalize_area_data_dict_with_name(self):
        """Тест нормализации словаря с полем name"""
        area_dict = {"name": "Санкт-Петербург", "id": 2}
        result = data_normalizers.normalize_area_data(area_dict)
        assert result == "Санкт-Петербург"
    
    def test_normalize_area_data_dict_with_title(self):
        """Тест нормализации словаря с полем title"""
        area_dict = {"title": "Екатеринбург", "id": 3}
        result = data_normalizers.normalize_area_data(area_dict)
        assert result == "Екатеринбург"
    
    def test_normalize_area_data_dict_with_id_only(self):
        """Тест нормализации словаря только с id"""
        area_dict = {"id": 123}
        result = data_normalizers.normalize_area_data(area_dict)
        assert result == "123"
    
    def test_normalize_area_data_dict_empty(self):
        """Тест нормализации пустого словаря"""
        result = data_normalizers.normalize_area_data({})
        assert result is None
    
    def test_normalize_area_data_dict_other_fields(self):
        """Тест нормализации словаря с другими полями"""
        area_dict = {"region": "Московская область", "country": "Россия"}
        result = data_normalizers.normalize_area_data(area_dict)
        assert "Московская область" in result or "Россия" in result
    
    def test_normalize_area_data_dict_name_whitespace(self):
        """Тест нормализации словаря с name содержащим пробелы"""
        area_dict = {"name": "  Новосибирск  "}
        result = data_normalizers.normalize_area_data(area_dict)
        assert result == "Новосибирск"
    
    def test_normalize_area_data_other_type(self):
        """Тест нормализации других типов данных"""
        result = data_normalizers.normalize_area_data(123)
        assert result == "123"
    
    def test_normalize_experience_data_none(self):
        """Тест нормализации None опыта"""
        result = data_normalizers.normalize_experience_data(None)
        assert result is None
    
    def test_normalize_experience_data_empty_string(self):
        """Тест нормализации пустой строки опыта"""
        result = data_normalizers.normalize_experience_data("")
        assert result is None
    
    def test_normalize_experience_data_valid_string(self):
        """Тест нормализации валидной строки опыта"""
        result = data_normalizers.normalize_experience_data("  От 1 года до 3 лет  ")
        assert result == "От 1 года до 3 лет"
    
    def test_normalize_experience_data_dict_with_name(self):
        """Тест нормализации словаря опыта с полем name"""
        exp_dict = {"name": "От 3 до 6 лет", "id": "between3And6"}
        result = data_normalizers.normalize_experience_data(exp_dict)
        assert result == "От 3 до 6 лет"
    
    def test_normalize_experience_data_dict_with_title(self):
        """Тест нормализации словаря опыта с полем title"""
        exp_dict = {"title": "Более 6 лет", "id": "moreThan6"}
        result = data_normalizers.normalize_experience_data(exp_dict)
        assert result == "Более 6 лет"
    
    def test_normalize_experience_data_dict_with_id_only(self):
        """Тест нормализации словаря опыта только с id"""
        exp_dict = {"id": "noExperience"}
        result = data_normalizers.normalize_experience_data(exp_dict)
        assert result == "noExperience"
    
    def test_normalize_experience_data_dict_empty(self):
        """Тест нормализации пустого словаря опыта"""
        result = data_normalizers.normalize_experience_data({})
        assert result is None
    
    def test_normalize_employer_data_none(self):
        """Тест нормализации None работодателя"""
        result = data_normalizers.normalize_employer_data(None)
        assert result is None
    
    def test_normalize_employer_data_string(self):
        """Тест нормализации строки работодателя"""
        result = data_normalizers.normalize_employer_data("  Google  ")
        assert result == "Google"
    
    def test_normalize_employer_data_dict_with_name(self):
        """Тест нормализации словаря работодателя с name"""
        employer_dict = {"name": "Яндекс", "id": 1740}
        result = data_normalizers.normalize_employer_data(employer_dict)
        assert result == "Яндекс"
    
    def test_normalize_employer_data_dict_with_title(self):
        """Тест нормализации словаря работодателя с title"""
        employer_dict = {"title": "Mail.ru Group", "id": 15478}
        result = data_normalizers.normalize_employer_data(employer_dict)
        assert result == "Mail.ru Group"
    
    def test_normalize_employment_data_none(self):
        """Тест нормализации None типа занятости"""
        result = data_normalizers.normalize_employment_data(None)
        assert result is None
    
    def test_normalize_employment_data_string(self):
        """Тест нормализации строки типа занятости"""
        result = data_normalizers.normalize_employment_data("  Полная занятость  ")
        assert result == "Полная занятость"
    
    def test_normalize_employment_data_dict_with_name(self):
        """Тест нормализации словаря типа занятости с name"""
        employment_dict = {"name": "Частичная занятость", "id": "part"}
        result = data_normalizers.normalize_employment_data(employment_dict)
        assert result == "Частичная занятость"
    
    def test_normalize_employment_data_dict_with_type(self):
        """Тест нормализации словаря типа занятости с type"""
        employment_dict = {"type": "Стажировка", "id": "probation"}
        result = data_normalizers.normalize_employment_data(employment_dict)
        assert result == "Стажировка"
    
    def test_normalize_employer_data_dict_with_firm_name(self):
        """Тест нормализации словаря работодателя с firm_name (для SuperJob)"""
        employer_dict = {"firm_name": "ВКонтакте", "id": 12345}
        result = data_normalizers.normalize_employer_data(employer_dict)
        assert result == "ВКонтакте"
    
    def test_normalize_all_data_comprehensive(self):
        """Комплексный тест нормализации всех типов данных"""
        raw_data = {
            "area": {"name": "  Москва  "},
            "experience": {"name": "От 1 года до 3 лет"},
            "employer": {"name": "  Яндекс  "},
            "employment": {"name": "Полная занятость"}
        }
        
        # Нормализуем каждое поле
        normalized = {}
        normalized["area"] = data_normalizers.normalize_area_data(raw_data["area"])
        normalized["experience"] = data_normalizers.normalize_experience_data(raw_data["experience"])
        normalized["employer"] = data_normalizers.normalize_employer_data(raw_data["employer"])
        normalized["employment"] = data_normalizers.normalize_employment_data(raw_data["employment"])
        
        # Проверяем результаты
        assert normalized["area"] == "Москва"
        assert normalized["experience"] == "От 1 года до 3 лет"
        assert normalized["employer"] == "Яндекс"
        assert normalized["employment"] == "Полная занятость"