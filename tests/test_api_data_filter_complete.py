
"""
Полные тесты для фильтра данных API
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


class TestAPIDataFilterComplete:
    """Полные тесты для фильтра данных API"""

    @pytest.fixture
    def filter_instance(self):
        """Фикстура для создания экземпляра фильтра"""
        if not API_DATA_FILTER_AVAILABLE:
            pytest.skip("APIDataFilter not available")
        return APIDataFilter()

    @pytest.fixture
    def sample_hh_data(self):
        """Пример данных HH.ru"""
        return [
            {
                'id': '1',
                'name': 'Python Developer',
                'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
                'area': {'name': 'Москва'},
                'experience': {'name': 'От 1 года до 3 лет'},
                'employment': {'name': 'Полная занятость'},
                'employer': {'name': 'Google'},
                'snippet': {'requirement': 'Python, Django', 'responsibility': 'Development'}
            },
            {
                'id': '2',
                'name': 'Java Developer',
                'salary': {'from': 80000, 'to': 120000, 'currency': 'RUR'},
                'area': {'name': 'Санкт-Петербург'},
                'experience': {'name': 'От 3 до 6 лет'},
                'employment': {'name': 'Частичная занятость'},
                'employer': {'name': 'Yandex'},
                'snippet': {'requirement': 'Java, Spring', 'responsibility': 'Backend development'}
            }
        ]

    @pytest.fixture
    def sample_sj_data(self):
        """Пример данных SuperJob"""
        return [
            {
                'id': '1',
                'profession': 'Python Developer',
                'payment_from': 100000,
                'payment_to': 150000,
                'currency': 'rub',
                'candidat': 'Python experience required',
                'firm_name': 'Tech Company'
            },
            {
                'id': '2',
                'profession': 'Frontend Developer',
                'payment_from': 80000,
                'payment_to': None,
                'currency': 'rub',
                'candidat': 'React, JavaScript',
                'firm_name': 'Web Studio'
            }
        ]

    def test_filter_by_salary_range_hh(self, filter_instance, sample_hh_data):
        """Тест фильтрации HH данных по зарплате"""
        result = filter_instance.filter_by_salary_range(
            sample_hh_data, min_salary=90000, max_salary=140000, source="hh"
        )
        assert len(result) == 1
        assert result[0]['id'] == '1'

    def test_filter_by_salary_range_sj(self, filter_instance, sample_sj_data):
        """Тест фильтрации SJ данных по зарплате"""
        result = filter_instance.filter_by_salary_range(
            sample_sj_data, min_salary=90000, max_salary=140000, source="sj"
        )
        assert len(result) == 1
        assert result[0]['id'] == '1'

    def test_filter_by_salary_empty_data(self, filter_instance):
        """Тест фильтрации пустых данных"""
        result = filter_instance.filter_by_salary_range([], min_salary=50000)
        assert result == []

    def test_filter_by_salary_invalid_data(self, filter_instance):
        """Тест фильтрации невалидных данных"""
        invalid_data = ["invalid", None, {"no_salary": True}]
        result = filter_instance.filter_by_salary_range(invalid_data, min_salary=50000)
        assert result == []

    def test_filter_by_keywords_basic(self, filter_instance, sample_hh_data):
        """Тест базовой фильтрации по ключевым словам"""
        result = filter_instance.filter_by_keywords(sample_hh_data, ["Python"])
        assert len(result) == 1
        assert result[0]['name'] == 'Python Developer'

    def test_filter_by_keywords_multiple(self, filter_instance, sample_hh_data):
        """Тест фильтрации по нескольким ключевым словам"""
        result = filter_instance.filter_by_keywords(sample_hh_data, ["Python", "Java"])
        assert len(result) == 2

    def test_filter_by_keywords_empty_keywords(self, filter_instance, sample_hh_data):
        """Тест фильтрации с пустыми ключевыми словами"""
        result = filter_instance.filter_by_keywords(sample_hh_data, [])
        assert len(result) == len(sample_hh_data)

    @patch('src.utils.api_data_filter.normalize_area_data')
    def test_filter_by_location_basic(self, mock_normalize, filter_instance, sample_hh_data):
        """Тест базовой фильтрации по местоположению"""
        mock_normalize.return_value = "Москва"
        
        result = filter_instance.filter_by_location(sample_hh_data, ["Москва"])
        assert len(result) == 2  # mock возвращает "Москва" для всех

    @patch('src.utils.api_data_filter.normalize_area_data')
    def test_filter_by_location_multiple(self, mock_normalize, filter_instance, sample_hh_data):
        """Тест фильтрации по нескольким местоположениям"""
        mock_normalize.side_effect = ["Москва", "Санкт-Петербург"]
        
        result = filter_instance.filter_by_location(sample_hh_data, ["Москва", "Санкт-Петербург"])
        assert len(result) == 2

    @patch('src.utils.api_data_filter.normalize_experience_data')
    def test_filter_by_experience(self, mock_normalize, filter_instance, sample_hh_data):
        """Тест фильтрации по опыту работы"""
        mock_normalize.return_value = "От 1 года до 3 лет"
        
        result = filter_instance.filter_by_experience(sample_hh_data, ["От 1 года до 3 лет"])
        assert len(result) == 2  # mock возвращает одинаковое значение

    @patch('src.utils.api_data_filter.normalize_employment_data')
    def test_filter_by_employment_type(self, mock_normalize, filter_instance, sample_hh_data):
        """Тест фильтрации по типу занятости"""
        mock_normalize.return_value = "Полная занятость"
        
        result = filter_instance.filter_by_employment_type(sample_hh_data, ["Полная занятость"])
        assert len(result) == 2

    @patch('src.utils.api_data_filter.normalize_employer_data')
    def test_filter_by_company_hh(self, mock_normalize, filter_instance, sample_hh_data):
        """Тест фильтрации по компании для HH данных"""
        mock_normalize.side_effect = ["Google", "Yandex"]
        
        result = filter_instance.filter_by_company(sample_hh_data, ["Google"])
        assert len(result) == 1
        assert result[0]['employer']['name'] == 'Google'

    @patch('src.utils.api_data_filter.normalize_employer_data')
    def test_filter_by_company_sj(self, mock_normalize, filter_instance, sample_sj_data):
        """Тест фильтрации по компании для SJ данных"""
        mock_normalize.side_effect = ["Tech Company", "Web Studio"]
        
        result = filter_instance.filter_by_company(sample_sj_data, ["Tech"])
        assert len(result) == 1

    def test_extract_salary_info_hh(self, filter_instance):
        """Тест извлечения информации о зарплате для HH"""
        item = {'salary': {'from': 100000, 'to': 150000}}
        result = filter_instance._extract_salary_info(item, "hh")
        assert result == {'from': 100000, 'to': 150000}

    def test_extract_salary_info_sj(self, filter_instance):
        """Тест извлечения информации о зарплате для SJ"""
        item = {'payment_from': 100000, 'payment_to': 150000, 'currency': 'rub'}
        result = filter_instance._extract_salary_info(item, "sj")
        assert result == {'from': 100000, 'to': 150000, 'currency': 'rub'}

    def test_salary_in_range_both_values(self, filter_instance):
        """Тест проверки зарплаты в диапазоне с обоими значениями"""
        salary_info = {'from': 100000, 'to': 150000}
        result = filter_instance._salary_in_range(salary_info, 90000, 160000)
        assert result == True

    def test_salary_in_range_only_from(self, filter_instance):
        """Тест проверки зарплаты только с минимумом"""
        salary_info = {'from': 100000, 'to': None}
        result = filter_instance._salary_in_range(salary_info, 90000, 160000)
        assert result == True

    def test_salary_in_range_out_of_bounds(self, filter_instance):
        """Тест зарплаты вне диапазона"""
        salary_info = {'from': 200000, 'to': 250000}
        result = filter_instance._salary_in_range(salary_info, 90000, 160000)
        assert result == False

    def test_get_searchable_text_hh(self, filter_instance):
        """Тест получения текста для поиска из HH данных"""
        item = {
            'name': 'Python Developer',
            'snippet': {
                'requirement': 'Python skills',
                'responsibility': 'Development tasks'
            }
        }
        result = filter_instance._get_searchable_text(item)
        assert 'python developer' in result
        assert 'python skills' in result
        assert 'development tasks' in result

    def test_get_searchable_text_sj(self, filter_instance):
        """Тест получения текста для поиска из SJ данных"""
        item = {
            'name': 'Developer',
            'candidat': 'Programming experience'
        }
        result = filter_instance._get_searchable_text(item)
        assert 'developer' in result
        assert 'programming experience' in result

    def test_contains_keywords_found(self, filter_instance):
        """Тест поиска найденных ключевых слов"""
        text = "python developer with django experience"
        result = filter_instance._contains_keywords(text, ["python", "django"])
        assert result == True

    def test_contains_keywords_not_found(self, filter_instance):
        """Тест поиска ненайденных ключевых слов"""
        text = "java developer with spring experience"
        result = filter_instance._contains_keywords(text, ["python", "django"])
        assert result == False

    @patch('src.utils.api_data_filter.normalize_area_data')
    def test_extract_location_valid(self, mock_normalize, filter_instance):
        """Тест извлечения валидного местоположения"""
        mock_normalize.return_value = "Москва"
        
        item = {'area': {'name': 'Москва'}}
        result = filter_instance._extract_location(item)
        assert result == "Москва"

    def test_extract_location_invalid_type(self, filter_instance):
        """Тест извлечения местоположения из невалидного типа"""
        result = filter_instance._extract_location("invalid")
        assert result is None

    @patch('src.utils.api_data_filter.normalize_employer_data')
    def test_extract_company_name_hh_format(self, mock_normalize, filter_instance):
        """Тест извлечения названия компании в формате HH"""
        mock_normalize.return_value = "Google"
        
        item = {'employer': {'name': 'Google'}}
        result = filter_instance._extract_company_name(item)
        assert result == "Google"

    @patch('src.utils.api_data_filter.normalize_employer_data')
    def test_extract_company_name_sj_format(self, mock_normalize, filter_instance):
        """Тест извлечения названия компании в формате SJ"""
        mock_normalize.return_value = "Tech Company"
        
        item = {'firm_name': 'Tech Company'}
        result = filter_instance._extract_company_name(item)
        assert result == "Tech Company"

    def test_filter_by_salary_abstract_method(self, filter_instance):
        """Тест абстрактного метода фильтрации по зарплате"""
        # Создаем мок-данные для теста абстрактного метода
        mock_vacancy = Mock()
        mock_vacancy.salary = {'from': 100000, 'to': 150000}
        
        # Поскольку это абстрактная реализация, мы тестируем что она вызывает filter_by_salary_range
        with patch.object(filter_instance, 'filter_by_salary_range') as mock_filter:
            mock_filter.return_value = [mock_vacancy]
            
            result = filter_instance.filter_by_salary([mock_vacancy], 50000, 200000)
            mock_filter.assert_called_once_with([mock_vacancy], 50000, 200000)
            assert result == [mock_vacancy]

    def test_error_handling_in_filters(self, filter_instance):
        """Тест обработки ошибок в фильтрах"""
        # Данные, которые могут вызвать ошибки
        problematic_data = [
            {"invalid": "data"},
            None,
            {"salary": "not_a_dict"},
        ]
        
        # Все фильтры должны обрабатывать ошибки gracefully
        result = filter_instance.filter_by_salary_range(problematic_data, 50000, 100000)
        assert result == []
        
        result = filter_instance.filter_by_keywords(problematic_data, ["test"])
        assert result == []
        
        result = filter_instance.filter_by_location(problematic_data, ["Moscow"])
        assert result == []
