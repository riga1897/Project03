
"""
Полные тесты для APIDataFilter с 100% покрытием
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.api_data_filter import APIDataFilter


class TestAPIDataFilterComplete:
    """Полные тесты для APIDataFilter"""

    @pytest.fixture
    def filter_instance(self):
        """Фикстура с экземпляром фильтра"""
        return APIDataFilter()

    @pytest.fixture
    def hh_vacancies(self):
        """Фикстура с вакансиями HH"""
        return [
            {
                "id": "1",
                "name": "Python Developer",
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "snippet": {"requirement": "Python, Django", "responsibility": "Разработка"},
                "area": {"name": "Москва"},
                "experience": {"name": "От 1 года до 3 лет"},
                "employment": {"name": "Полная занятость"},
                "employer": {"name": "Tech Company"}
            },
            {
                "id": "2", 
                "name": "Java Developer",
                "salary": {"from": 120000, "currency": "RUR"},
                "area": {"name": "СПб"},
                "employer": {"name": "Java Corp"}
            }
        ]

    @pytest.fixture 
    def sj_vacancies(self):
        """Фикстура с вакансиями SuperJob"""
        return [
            {
                "id": "10",
                "profession": "Python Developer",
                "payment_from": 80000,
                "payment_to": 120000,
                "currency": "rub",
                "candidat": "Опыт с Python",
                "firm_name": "SJ Company"
            },
            {
                "id": "11",
                "profession": "JS Developer", 
                "payment_from": 90000,
                "firm_name": "JS Corp"
            }
        ]

    def test_filter_by_salary_hh_source(self, filter_instance, hh_vacancies):
        """Тест фильтрации по зарплате для HH"""
        result = filter_instance.filter_by_salary_range(
            hh_vacancies, min_salary=110000, max_salary=140000, source="hh"
        )
        assert len(result) == 2  # Обе вакансии подходят под критерии

    def test_filter_by_salary_sj_source(self, filter_instance, sj_vacancies):
        """Тест фильтрации по зарплате для SJ"""
        result = filter_instance.filter_by_salary_range(
            sj_vacancies, min_salary=85000, max_salary=110000, source="sj"
        )
        assert len(result) == 2

    def test_filter_by_salary_empty_data(self, filter_instance):
        """Тест фильтрации пустых данных"""
        result = filter_instance.filter_by_salary_range([], 100000, 200000)
        assert result == []

    def test_filter_by_salary_no_limits(self, filter_instance, hh_vacancies):
        """Тест фильтрации без ограничений"""
        result = filter_instance.filter_by_salary_range(hh_vacancies)
        assert len(result) == 2

    def test_filter_by_salary_invalid_data(self, filter_instance):
        """Тест фильтрации с невалидными данными"""
        invalid_data = [
            {"id": "1", "name": "Test"},  # Нет зарплаты
            "invalid_string",
            None,
            {"salary": "invalid"}
        ]
        result = filter_instance.filter_by_salary_range(invalid_data, source="hh")
        assert result == []

    def test_filter_by_keywords_basic(self, filter_instance, hh_vacancies):
        """Тест фильтрации по ключевым словам"""
        result = filter_instance.filter_by_keywords(hh_vacancies, ["Python"])
        assert len(result) == 1
        assert result[0]["name"] == "Python Developer"

    def test_filter_by_keywords_empty(self, filter_instance, hh_vacancies):
        """Тест фильтрации без ключевых слов"""
        result = filter_instance.filter_by_keywords(hh_vacancies, [])
        assert len(result) == 2

    def test_filter_by_keywords_multiple(self, filter_instance, hh_vacancies):
        """Тест фильтрации по нескольким ключевым словам"""
        result = filter_instance.filter_by_keywords(hh_vacancies, ["Developer"])
        assert len(result) == 2

    def test_filter_by_keywords_sj_format(self, filter_instance, sj_vacancies):
        """Тест фильтрации для формата SJ"""
        result = filter_instance.filter_by_keywords(sj_vacancies, ["Python"])
        assert len(result) == 1

    def test_filter_by_keywords_invalid_data(self, filter_instance):
        """Тест фильтрации с невалидными данными"""
        invalid_data = ["string", None, 123]
        result = filter_instance.filter_by_keywords(invalid_data, ["test"])
        assert result == []

    @patch('src.utils.api_data_filter.normalize_area_data')
    def test_filter_by_location_basic(self, mock_normalize, filter_instance, hh_vacancies):
        """Тест фильтрации по местоположению"""
        mock_normalize.side_effect = lambda x: x.get("name") if x else None
        
        result = filter_instance.filter_by_location(hh_vacancies, ["Москва"])
        assert len(result) == 1
        assert result[0]["area"]["name"] == "Москва"

    @patch('src.utils.api_data_filter.normalize_area_data')
    def test_filter_by_location_multiple(self, mock_normalize, filter_instance, hh_vacancies):
        """Тест фильтрации по нескольким локациям"""
        mock_normalize.side_effect = lambda x: x.get("name") if x else None
        
        result = filter_instance.filter_by_location(hh_vacancies, ["Москва", "СПб"])
        assert len(result) == 2

    def test_filter_by_location_empty(self, filter_instance, hh_vacancies):
        """Тест фильтрации без локаций"""
        result = filter_instance.filter_by_location(hh_vacancies, [])
        assert len(result) == 2

    @patch('src.utils.api_data_filter.normalize_experience_data')
    def test_filter_by_experience(self, mock_normalize, filter_instance, hh_vacancies):
        """Тест фильтрации по опыту"""
        mock_normalize.side_effect = lambda x: x.get("name") if x else None
        
        result = filter_instance.filter_by_experience(hh_vacancies, ["От 1 года до 3 лет"])
        assert len(result) == 1

    @patch('src.utils.api_data_filter.normalize_employment_data')
    def test_filter_by_employment_type(self, mock_normalize, filter_instance, hh_vacancies):
        """Тест фильтрации по типу занятости"""
        mock_normalize.side_effect = lambda x: x.get("name") if x else None
        
        result = filter_instance.filter_by_employment_type(hh_vacancies, ["Полная занятость"])
        assert len(result) == 1

    @patch('src.utils.api_data_filter.normalize_employer_data')
    def test_filter_by_company_hh(self, mock_normalize, filter_instance, hh_vacancies):
        """Тест фильтрации по компании HH"""
        mock_normalize.side_effect = lambda x: x.get("name") if x else None
        
        result = filter_instance.filter_by_company(hh_vacancies, ["Tech"])
        assert len(result) == 1

    @patch('src.utils.api_data_filter.normalize_employer_data')
    def test_filter_by_company_sj(self, mock_normalize, filter_instance, sj_vacancies):
        """Тест фильтрации по компании SJ"""
        mock_normalize.side_effect = lambda x: x.get("name") if x else None
        
        result = filter_instance.filter_by_company(sj_vacancies, ["SJ Company"])
        assert len(result) == 1

    def test_extract_salary_info_hh(self, filter_instance):
        """Тест извлечения зарплаты HH"""
        item = {"salary": {"from": 100000, "to": 150000}}
        result = filter_instance._extract_salary_info(item, "hh")
        assert result == {"from": 100000, "to": 150000}

    def test_extract_salary_info_sj(self, filter_instance):
        """Тест извлечения зарплаты SJ"""
        item = {"payment_from": 100000, "payment_to": 150000, "currency": "rub"}
        result = filter_instance._extract_salary_info(item, "sj")
        assert result == {"from": 100000, "to": 150000, "currency": "rub"}

    def test_extract_salary_info_sj_partial(self, filter_instance):
        """Тест извлечения частичной зарплаты SJ"""
        item = {"payment_from": 100000}
        result = filter_instance._extract_salary_info(item, "sj")
        assert result == {"from": 100000, "to": None, "currency": "rub"}

    def test_extract_salary_info_none(self, filter_instance):
        """Тест извлечения отсутствующей зарплаты"""
        item = {"name": "Test"}
        result = filter_instance._extract_salary_info(item, "hh")
        assert result is None

    def test_salary_in_range_both_bounds(self, filter_instance):
        """Тест проверки зарплаты в диапазоне"""
        salary_info = {"from": 100000, "to": 150000}
        assert filter_instance._salary_in_range(salary_info, 120000, 140000) is True
        assert filter_instance._salary_in_range(salary_info, 160000, 200000) is False

    def test_salary_in_range_single_value(self, filter_instance):
        """Тест проверки зарплаты с одним значением"""
        salary_info = {"from": 100000, "to": None}
        assert filter_instance._salary_in_range(salary_info, 50000, 150000) is True
        assert filter_instance._salary_in_range(salary_info, 120000, 150000) is False

    def test_salary_in_range_no_salary(self, filter_instance):
        """Тест проверки отсутствующей зарплаты"""
        salary_info = {"from": None, "to": None}
        assert filter_instance._salary_in_range(salary_info, 100000, 200000) is False

    def test_get_searchable_text_hh(self, filter_instance):
        """Тест получения текста для поиска HH"""
        item = {
            "name": "Python Developer",
            "snippet": {
                "requirement": "Python знание",
                "responsibility": "Разработка"
            }
        }
        result = filter_instance._get_searchable_text(item)
        assert "python developer" in result
        assert "python знание" in result
        assert "разработка" in result

    def test_get_searchable_text_sj(self, filter_instance):
        """Тест получения текста для поиска SJ"""
        item = {
            "name": "Java Developer",
            "candidat": "Опыт с Java"
        }
        result = filter_instance._get_searchable_text(item)
        assert "java developer" in result
        assert "опыт с java" in result

    def test_get_searchable_text_snippet_string(self, filter_instance):
        """Тест получения текста со строковым snippet"""
        item = {
            "name": "Developer",
            "snippet": "Simple text description"
        }
        result = filter_instance._get_searchable_text(item)
        assert "developer" in result
        assert "simple text description" in result

    def test_contains_keywords_true(self, filter_instance):
        """Тест проверки наличия ключевых слов"""
        text = "python developer with django experience"
        assert filter_instance._contains_keywords(text, ["python"]) is True
        assert filter_instance._contains_keywords(text, ["django"]) is True

    def test_contains_keywords_false(self, filter_instance):
        """Тест отсутствия ключевых слов"""
        text = "python developer with django experience"
        assert filter_instance._contains_keywords(text, ["java"]) is False

    def test_contains_keywords_case_insensitive(self, filter_instance):
        """Тест поиска без учета регистра"""
        text = "python developer"
        assert filter_instance._contains_keywords(text, ["Python"]) is True
        assert filter_instance._contains_keywords(text, ["DEVELOPER"]) is True

    @patch('src.utils.api_data_filter.normalize_area_data')
    def test_extract_location_valid(self, mock_normalize, filter_instance):
        """Тест извлечения местоположения"""
        mock_normalize.return_value = "Москва"
        item = {"area": {"name": "Москва"}}
        result = filter_instance._extract_location(item)
        assert result == "Москва"

    def test_extract_location_invalid_item(self, filter_instance):
        """Тест извлечения местоположения с невалидным объектом"""
        result = filter_instance._extract_location("invalid")
        assert result is None

    @patch('src.utils.api_data_filter.normalize_employer_data')
    def test_extract_company_name_hh_format(self, mock_normalize, filter_instance):
        """Тест извлечения названия компании HH"""
        mock_normalize.return_value = "Tech Company"
        item = {"employer": {"name": "Tech Company"}}
        result = filter_instance._extract_company_name(item)
        assert result == "Tech Company"

    @patch('src.utils.api_data_filter.normalize_employer_data')
    def test_extract_company_name_sj_format(self, mock_normalize, filter_instance):
        """Тест извлечения названия компании SJ"""
        mock_normalize.return_value = "SJ Company"
        item = {"firm_name": "SJ Company"}
        result = filter_instance._extract_company_name(item)
        assert result == "SJ Company"

    def test_extract_company_name_invalid_item(self, filter_instance):
        """Тест извлечения названия компании с невалидным объектом"""
        result = filter_instance._extract_company_name("invalid")
        assert result is None

    def test_filter_by_salary_inheritance_method(self, filter_instance):
        """Тест наследованного метода filter_by_salary"""
        # Создаем мок-вакансии
        mock_vacancy1 = Mock()
        mock_vacancy2 = Mock()
        vacancies = [mock_vacancy1, mock_vacancy2]
        
        # Мокаем метод filter_by_salary_range
        with patch.object(filter_instance, 'filter_by_salary_range') as mock_filter:
            mock_filter.return_value = [mock_vacancy1]
            
            result = filter_instance.filter_by_salary(vacancies, 100000, 200000)
            
            assert result == [mock_vacancy1]
            mock_filter.assert_called_once_with(vacancies, 100000, 200000)

    def test_error_handling_in_filters(self, filter_instance):
        """Тест обработки ошибок в фильтрах"""
        # Данные, которые могут вызвать исключения
        problematic_data = [
            {"name": "Test", "salary": "invalid_salary"},
            {"snippet": None},
            {"area": "string_instead_of_dict"}
        ]
        
        # Все методы должны обрабатывать ошибки gracefully
        assert filter_instance.filter_by_salary_range(problematic_data, 100000) == []
        assert filter_instance.filter_by_keywords(problematic_data, ["test"]) == []
        assert filter_instance.filter_by_location(problematic_data, ["test"]) == []
        assert filter_instance.filter_by_experience(problematic_data, ["test"]) == []
        assert filter_instance.filter_by_employment_type(problematic_data, ["test"]) == []
        assert filter_instance.filter_by_company(problematic_data, ["test"]) == []
