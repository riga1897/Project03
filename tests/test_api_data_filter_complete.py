
"""
Полные тесты для APIDataFilter
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.api_data_filter import APIDataFilter
    API_DATA_FILTER_AVAILABLE = True
except ImportError:
    API_DATA_FILTER_AVAILABLE = False
    APIDataFilter = object


@pytest.mark.skipif(not API_DATA_FILTER_AVAILABLE, reason="APIDataFilter not available")
class TestAPIDataFilterComplete:
    """Полное тестирование APIDataFilter"""
    
    @pytest.fixture
    def filter_instance(self):
        """Экземпляр фильтра API данных"""
        return APIDataFilter()
    
    @pytest.fixture
    def sample_hh_data(self):
        """Образцы данных HH для тестирования"""
        return [
            {
                "name": "Python Developer",
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "area": {"name": "Москва"},
                "experience": {"name": "От 3 до 6 лет"},
                "employment": {"name": "Полная занятость"},
                "employer": {"name": "Яндекс"},
                "snippet": {"requirement": "Python Django", "responsibility": "Разработка API"}
            },
            {
                "name": "Java Developer", 
                "salary": {"from": 80000, "to": None, "currency": "RUR"},
                "area": {"name": "СПб"},
                "experience": {"name": "От 1 до 3 лет"},
                "employment": {"name": "Частичная занятость"},
                "employer": {"name": "Mail.Ru"},
                "snippet": {"requirement": "Java Spring", "responsibility": "Backend разработка"}
            },
            {
                "name": "Frontend Developer",
                "salary": None,
                "area": {"name": "Новосибирск"},
                "experience": {"name": "Без опыта"},
                "employment": {"name": "Полная занятость"},
                "employer": {"name": "2ГИС"},
                "snippet": {"requirement": "React JavaScript", "responsibility": "UI/UX"}
            }
        ]
    
    @pytest.fixture
    def sample_sj_data(self):
        """Образцы данных SJ для тестирования"""
        return [
            {
                "profession": "Python разработчик",
                "payment_from": 120000,
                "payment_to": 180000,
                "currency": "rub",
                "town": {"title": "Москва"},
                "experience": {"title": "От 3 до 6 лет"},
                "type_of_work": {"title": "Полный день"},
                "firm_name": "Тинькофф",
                "candidat": "Знание Python, Django, PostgreSQL"
            },
            {
                "profession": "QA Engineer",
                "payment_from": 90000,
                "payment_to": None,
                "currency": "rub",
                "town": {"title": "Екатеринбург"},
                "experience": {"title": "От 1 до 3 лет"},
                "type_of_work": {"title": "Удаленная работа"},
                "firm_name": "Avito",
                "candidat": "Тестирование веб-приложений"
            }
        ]
    
    def test_filter_by_salary_range_hh(self, filter_instance, sample_hh_data):
        """Тест фильтрации по диапазону зарплаты для HH"""
        result = filter_instance.filter_by_salary_range(
            sample_hh_data, 
            min_salary=90000, 
            max_salary=130000, 
            source="hh"
        )
        assert len(result) == 1
        assert result[0]["name"] == "Python Developer"
    
    def test_filter_by_salary_range_sj(self, filter_instance, sample_sj_data):
        """Тест фильтрации по диапазону зарплаты для SJ"""
        result = filter_instance.filter_by_salary_range(
            sample_sj_data,
            min_salary=100000,
            max_salary=200000,
            source="sj"
        )
        assert len(result) == 1
        assert result[0]["profession"] == "Python разработчик"
    
    def test_filter_by_salary_range_empty_data(self, filter_instance):
        """Тест фильтрации пустых данных"""
        result = filter_instance.filter_by_salary_range([], 50000, 100000)
        assert result == []
    
    def test_filter_by_salary_range_no_limits(self, filter_instance, sample_hh_data):
        """Тест фильтрации без ограничений по зарплате"""
        result = filter_instance.filter_by_salary_range(sample_hh_data, source="hh")
        assert len(result) == 2  # только записи с зарплатой
    
    def test_filter_by_salary_invalid_data(self, filter_instance):
        """Тест фильтрации с невалидными данными"""
        invalid_data = ["not_a_dict", {"name": "test"}, None]
        result = filter_instance.filter_by_salary_range(invalid_data, 50000, 100000)
        assert result == []
    
    def test_filter_by_keywords(self, filter_instance, sample_hh_data):
        """Тест фильтрации по ключевым словам"""
        keywords = ["Python", "Django"]
        result = filter_instance.filter_by_keywords(sample_hh_data, keywords)
        assert len(result) == 1
        assert result[0]["name"] == "Python Developer"
    
    def test_filter_by_keywords_no_match(self, filter_instance, sample_hh_data):
        """Тест фильтрации когда ключевые слова не найдены"""
        keywords = ["PHP", "Laravel"]
        result = filter_instance.filter_by_keywords(sample_hh_data, keywords)
        assert result == []
    
    def test_filter_by_keywords_empty_keywords(self, filter_instance, sample_hh_data):
        """Тест фильтрации с пустым списком ключевых слов"""
        result = filter_instance.filter_by_keywords(sample_hh_data, [])
        assert result == sample_hh_data
    
    def test_filter_by_location_basic(self, filter_instance):
        """Тест фильтрации по местоположению"""
        with patch.object(filter_instance, '_extract_location') as mock_extract:
            mock_extract.side_effect = ["Москва", "СПб", "Новосибирск"]
            
            data = [{"id": 1}, {"id": 2}, {"id": 3}]
            result = filter_instance.filter_by_location(data, ["Москва"])
            assert len(result) == 1
    
    def test_filter_by_location_multiple(self, filter_instance):
        """Тест фильтрации по нескольким городам"""
        with patch.object(filter_instance, '_extract_location') as mock_extract:
            mock_extract.side_effect = ["Москва", "СПб", "Новосибирск"]
            
            data = [{"id": 1}, {"id": 2}, {"id": 3}]
            result = filter_instance.filter_by_location(data, ["Москва", "СПб"])
            assert len(result) == 2
    
    def test_filter_by_experience(self, filter_instance):
        """Тест фильтрации по опыту работы"""
        with patch.object(filter_instance, '_extract_experience') as mock_extract:
            mock_extract.side_effect = ["От 1 до 3 лет", "От 3 до 6 лет", "Без опыта"]
            
            data = [{"id": 1}, {"id": 2}, {"id": 3}]
            result = filter_instance.filter_by_experience(data, ["От 1 до 3 лет"])
            assert len(result) == 1
    
    def test_filter_by_employment_type(self, filter_instance):
        """Тест фильтрации по типу занятости"""
        with patch.object(filter_instance, '_extract_employment_type') as mock_extract:
            mock_extract.side_effect = ["Полная занятость", "Частичная занятость", "Удаленная работа"]
            
            data = [{"id": 1}, {"id": 2}, {"id": 3}]
            result = filter_instance.filter_by_employment_type(data, ["Полная занятость"])
            assert len(result) == 1
    
    def test_filter_by_company_hh(self, filter_instance):
        """Тест фильтрации по компании для HH формата"""
        with patch.object(filter_instance, '_extract_company_name') as mock_extract:
            mock_extract.side_effect = ["Яндекс", "Mail.Ru", "2ГИС"]
            
            data = [{"id": 1}, {"id": 2}, {"id": 3}]
            result = filter_instance.filter_by_company(data, ["Яндекс"])
            assert len(result) == 1
    
    def test_filter_by_company_sj(self, filter_instance):
        """Тест фильтрации по компании для SJ формата"""
        with patch.object(filter_instance, '_extract_company_name') as mock_extract:
            mock_extract.side_effect = ["Тинькофф", "Avito", "Ozon"]
            
            data = [{"id": 1}, {"id": 2}, {"id": 3}]
            result = filter_instance.filter_by_company(data, ["тинькофф"])  # регистронезависимый поиск
            assert len(result) == 1
    
    def test_extract_salary_info_hh(self, filter_instance):
        """Тест извлечения информации о зарплате для HH"""
        item = {"salary": {"from": 100000, "to": 150000, "currency": "RUR"}}
        result = filter_instance._extract_salary_info(item, "hh")
        assert result == {"from": 100000, "to": 150000, "currency": "RUR"}
    
    def test_extract_salary_info_sj(self, filter_instance):
        """Тест извлечения информации о зарплате для SJ"""
        item = {"payment_from": 120000, "payment_to": 180000, "currency": "rub"}
        result = filter_instance._extract_salary_info(item, "sj")
        expected = {"from": 120000, "to": 180000, "currency": "rub"}
        assert result == expected
    
    def test_extract_salary_info_no_salary(self, filter_instance):
        """Тест извлечения информации когда зарплата не указана"""
        item = {"name": "Test Job"}
        result = filter_instance._extract_salary_info(item, "hh")
        assert result is None
    
    def test_salary_in_range_both_values(self, filter_instance):
        """Тест проверки диапазона когда указаны обе границы зарплаты"""
        salary_info = {"from": 100000, "to": 150000}
        result = filter_instance._salary_in_range(salary_info, 90000, 160000)
        assert result is True
        
        result2 = filter_instance._salary_in_range(salary_info, 160000, 200000)
        assert result2 is False
    
    def test_salary_in_range_single_value(self, filter_instance):
        """Тест проверки диапазона когда указано только одно значение"""
        salary_info = {"from": 100000, "to": None}
        result = filter_instance._salary_in_range(salary_info, 90000, 120000)
        assert result is True
    
    def test_salary_in_range_no_values(self, filter_instance):
        """Тест проверки диапазона когда зарплата не указана"""
        salary_info = {"from": None, "to": None}
        result = filter_instance._salary_in_range(salary_info, 50000, 100000)
        assert result is False
    
    def test_get_searchable_text_hh(self, filter_instance):
        """Тест получения текста для поиска из данных HH"""
        item = {
            "name": "Python Developer",
            "snippet": {
                "requirement": "Python Django",
                "responsibility": "Backend development"
            }
        }
        result = filter_instance._get_searchable_text(item)
        expected = "python developer python django backend development"
        assert result == expected
    
    def test_get_searchable_text_sj(self, filter_instance):
        """Тест получения текста для поиска из данных SJ"""
        item = {
            "profession": "QA Engineer",
            "candidat": "Testing automation"
        }
        result = filter_instance._get_searchable_text(item)
        expected = "qa engineer testing automation"
        assert result == expected
    
    def test_contains_keywords_found(self, filter_instance):
        """Тест поиска ключевых слов в тексте - найдено"""
        text = "python developer with django experience"
        keywords = ["python", "django"]
        result = filter_instance._contains_keywords(text, keywords)
        assert result is True
    
    def test_contains_keywords_not_found(self, filter_instance):
        """Тест поиска ключевых слов в тексте - не найдено"""
        text = "java developer with spring experience"
        keywords = ["python", "django"]
        result = filter_instance._contains_keywords(text, keywords)
        assert result is False
    
    def test_extract_location_valid(self, filter_instance):
        """Тест извлечения местоположения"""
        with patch('src.utils.data_normalizers.normalize_area_data') as mock_normalize:
            mock_normalize.return_value = "Москва"
            
            item = {"area": {"name": "Москва"}}
            result = filter_instance._extract_location(item)
            assert result == "Москва"
            mock_normalize.assert_called_once_with({"name": "Москва"})
    
    def test_extract_location_invalid_item(self, filter_instance):
        """Тест извлечения местоположения с невалидным элементом"""
        result = filter_instance._extract_location("not_a_dict")
        assert result is None
    
    def test_extract_company_name_hh_format(self, filter_instance):
        """Тест извлечения названия компании в формате HH"""
        with patch('src.utils.data_normalizers.normalize_employer_data') as mock_normalize:
            mock_normalize.return_value = "Яндекс"
            
            item = {"employer": {"name": "Яндекс"}}
            result = filter_instance._extract_company_name(item)
            assert result == "Яндекс"
            mock_normalize.assert_called_once_with({"name": "Яндекс"})
    
    def test_extract_company_name_sj_format(self, filter_instance):
        """Тест извлечения названия компании в формате SJ"""
        with patch('src.utils.data_normalizers.normalize_employer_data') as mock_normalize:
            mock_normalize.return_value = "Тинькофф"
            
            item = {"firm_name": "Тинькофф"}
            result = filter_instance._extract_company_name(item)
            assert result == "Тинькофф"
            mock_normalize.assert_called_once_with({"name": "Тинькофф"})
    
    def test_extract_company_name_invalid_item(self, filter_instance):
        """Тест извлечения названия компании с невалидным элементом"""
        result = filter_instance._extract_company_name("not_a_dict")
        assert result is None
    
    def test_filter_by_salary_with_vacancy_objects(self, filter_instance):
        """Тест фильтрации по зарплате с объектами вакансий"""
        # Мокаем объекты вакансий
        vacancies = [Mock(), Mock(), Mock()]
        
        # Мокаем метод filter_by_salary_range
        with patch.object(filter_instance, 'filter_by_salary_range') as mock_filter:
            mock_filter.return_value = [vacancies[0]]
            
            result = filter_instance.filter_by_salary(vacancies, 50000, 100000)
            assert result == [vacancies[0]]
            mock_filter.assert_called_once_with(vacancies, 50000, 100000)
    
    def test_error_handling_in_filters(self, filter_instance):
        """Тест обработки ошибок в фильтрах"""
        # Данные, которые могут вызвать ошибки
        problematic_data = [
            {"name": "Valid Job", "salary": {"from": 100000}},
            None,  # Вызовет ошибку при обращении к .get()
            {"incomplete": "data"}  # Без необходимых полей
        ]
        
        # Фильтры должны обрабатывать ошибки и продолжать работу
        result = filter_instance.filter_by_salary_range(problematic_data, 50000, 150000, source="hh")
        assert len(result) <= len(problematic_data)  # Может быть меньше из-за ошибок
    
    def test_all_filter_methods_with_empty_data(self, filter_instance):
        """Тест всех методов фильтрации с пустыми данными"""
        empty_data = []
        
        # Все методы должны корректно обрабатывать пустые данные
        assert filter_instance.filter_by_salary_range(empty_data, 50000, 100000) == []
        assert filter_instance.filter_by_keywords(empty_data, ["python"]) == []
        assert filter_instance.filter_by_location(empty_data, ["Москва"]) == []
        assert filter_instance.filter_by_experience(empty_data, ["От 1 до 3 лет"]) == []
        assert filter_instance.filter_by_employment_type(empty_data, ["Полная занятость"]) == []
        assert filter_instance.filter_by_company(empty_data, ["Яндекс"]) == []
    
    def test_all_filter_methods_with_none_params(self, filter_instance, sample_hh_data):
        """Тест всех методов фильтрации с None параметрами"""
        # Методы должны возвращать исходные данные при None/пустых параметрах
        assert filter_instance.filter_by_keywords(sample_hh_data, None) == sample_hh_data
        assert filter_instance.filter_by_location(sample_hh_data, None) == sample_hh_data
        assert filter_instance.filter_by_experience(sample_hh_data, None) == sample_hh_data
        assert filter_instance.filter_by_employment_type(sample_hh_data, None) == sample_hh_data
        assert filter_instance.filter_by_company(sample_hh_data, None) == sample_hh_data


@pytest.mark.skipif(not API_DATA_FILTER_AVAILABLE, reason="APIDataFilter not available")
class TestAPIDataFilterIntegration:
    """Интеграционные тесты для APIDataFilter"""
    
    def test_complex_filtering_scenario(self):
        """Тест сложного сценария фильтрации"""
        filter_instance = APIDataFilter()
        
        # Комплексные тестовые данные
        data = [
            {
                "name": "Senior Python Developer",
                "salary": {"from": 150000, "to": 200000, "currency": "RUR"},
                "area": {"name": "Москва"},
                "employer": {"name": "Яндекс"},
                "snippet": {"requirement": "Python Django PostgreSQL"}
            },
            {
                "name": "Junior Java Developer", 
                "salary": {"from": 60000, "to": 80000, "currency": "RUR"},
                "area": {"name": "СПб"},
                "employer": {"name": "JetBrains"},
                "snippet": {"requirement": "Java Spring MySQL"}
            }
        ]
        
        # Тестируем цепочку фильтров
        with patch('src.utils.data_normalizers.normalize_area_data', side_effect=lambda x: x.get('name', '') if x else ''), \
             patch('src.utils.data_normalizers.normalize_employer_data', side_effect=lambda x: x.get('name', '') if x else ''):
            
            # Фильтрация по зарплате
            salary_filtered = filter_instance.filter_by_salary_range(data, 100000, 250000, source="hh")
            assert len(salary_filtered) == 1
            
            # Фильтрация по ключевым словам
            keyword_filtered = filter_instance.filter_by_keywords(salary_filtered, ["Python"])
            assert len(keyword_filtered) == 1
            
            # Фильтрация по местоположению
            location_filtered = filter_instance.filter_by_location(keyword_filtered, ["Москва"])
            assert len(location_filtered) == 1
