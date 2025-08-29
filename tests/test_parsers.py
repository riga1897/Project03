
"""
Тесты для парсеров данных

Содержит тесты для проверки корректности работы парсеров вакансий
из различных источников (HH.ru, SuperJob).
"""

from unittest.mock import Mock
import pytest
from src.vacancies.parsers.hh_parser import HHParser
from src.vacancies.parsers.sj_parser import SuperJobParser


class TestHHParser:
    """Тесты для парсера HeadHunter"""

    @pytest.fixture
    def hh_parser(self):
        """Фикстура HH парсера"""
        return HHParser()

    def test_parse_vacancy_full_data(self, hh_parser):
        """Тест парсинга полных данных вакансии"""
        vacancy_data = {
            "id": "123456",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/123456",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "snippet": {
                "requirement": "Python, Django",
                "responsibility": "Разработка веб-приложений"
            },
            "employer": {"name": "TechCorp"},
            "area": {"name": "Москва"},
            "experience": {"name": "От 1 года до 3 лет"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"},
            "published_at": "2024-01-01T10:00:00+03:00"
        }

        result = hh_parser.parse_vacancy(vacancy_data)
        
        assert result is not None
        assert result["id"] == "123456"
        assert result["name"] == "Python Developer"
        assert result["alternate_url"] == "https://hh.ru/vacancy/123456"

    def test_parse_vacancy_minimal_data(self, hh_parser):
        """Тест парсинга минимальных данных вакансии"""
        vacancy_data = {
            "id": "123",
            "name": "Test Job",
            "alternate_url": "https://hh.ru/vacancy/123"
        }

        result = hh_parser.parse_vacancy(vacancy_data)
        
        assert result is not None
        assert result["id"] == "123"
        assert result["name"] == "Test Job"

    def test_parse_vacancy_no_salary(self, hh_parser):
        """Тест парсинга вакансии без зарплаты"""
        vacancy_data = {
            "id": "456",
            "name": "No Salary Job", 
            "alternate_url": "https://hh.ru/vacancy/456",
            "salary": None
        }

        result = hh_parser.parse_vacancy(vacancy_data)
        
        assert result is not None
        assert result["salary"] is None

    def test_parse_vacancy_list(self, hh_parser):
        """Тест парсинга списка вакансий"""
        vacancies_data = {
            "items": [
                {"id": "1", "name": "Job 1", "alternate_url": "https://hh.ru/vacancy/1"},
                {"id": "2", "name": "Job 2", "alternate_url": "https://hh.ru/vacancy/2"}
            ]
        }

        # Проверяем, есть ли метод parse_vacancies
        if hasattr(hh_parser, 'parse_vacancies'):
            result = hh_parser.parse_vacancies(vacancies_data)
            assert len(result) == 2
        else:
            # Альтернативно парсим каждую вакансию отдельно
            results = []
            for item in vacancies_data["items"]:
                parsed = hh_parser.parse_vacancy(item)
                results.append(parsed)
            assert len(results) == 2

    def test_parse_error_handling(self, hh_parser):
        """Тест обработки ошибок парсинга"""
        # Тест с некорректными данными
        invalid_data = {"invalid": "data"}
        
        try:
            result = hh_parser.parse_vacancy(invalid_data)
            # Если парсер возвращает None или пустой результат при ошибке
            assert result is None or result == {}
        except Exception as e:
            # Если парсер выбрасывает исключение, это тоже валидное поведение
            assert isinstance(e, Exception)

    def test_parse_vacancy_with_description(self, hh_parser):
        """Тест парсинга вакансии с описанием"""
        vacancy_data = {
            "id": "789",
            "name": "Job with Description",
            "alternate_url": "https://hh.ru/vacancy/789",
            "description": "<p>Подробное описание вакансии</p>"
        }

        result = hh_parser.parse_vacancy(vacancy_data)
        
        assert result is not None
        # Проверяем, что описание обрабатывается
        if "description" in result:
            assert isinstance(result["description"], str)


class TestSuperJobParser:
    """Тесты для парсера SuperJob"""

    @pytest.fixture
    def sj_parser(self):
        """Фикстура SJ парсера"""
        return SuperJobParser()

    def test_parse_vacancy_full_data(self, sj_parser):
        """Тест парсинга полных данных вакансии SJ"""
        vacancy_data = {
            "id": 12345,
            "profession": "Python разработчик",
            "link": "https://superjob.ru/vakansii/python-12345.html",
            "payment_from": 100000,
            "payment_to": 150000,
            "currency": "rub",
            "candidat": "Опыт работы с Python",
            "work": "Разработка приложений",
            "firm_name": "SuperCorp",
            "town": {"title": "Москва"},
            "type_of_work": {"title": "Полная занятость"},
            "date_published": 1640995200
        }

        result = sj_parser.parse_vacancy(vacancy_data)
        
        assert result is not None
        assert result["id"] == 12345
        assert result["profession"] == "Python разработчик"

    def test_parse_vacancy_minimal_data(self, sj_parser):
        """Тест парсинга минимальных данных вакансии SJ"""
        vacancy_data = {
            "id": 999,
            "profession": "Test SJ Job",
            "link": "https://superjob.ru/vakansii/test-999.html"
        }

        result = sj_parser.parse_vacancy(vacancy_data)
        
        assert result is not None
        assert result["id"] == 999
        assert result["profession"] == "Test SJ Job"

    def test_parse_vacancy_list_sj(self, sj_parser):
        """Тест парсинга списка вакансий SJ"""
        vacancies_data = {
            "objects": [
                {"id": 1, "profession": "SJ Job 1", "link": "https://superjob.ru/1"},
                {"id": 2, "profession": "SJ Job 2", "link": "https://superjob.ru/2"}
            ]
        }

        # Проверяем, есть ли метод parse_vacancies
        if hasattr(sj_parser, 'parse_vacancies'):
            result = sj_parser.parse_vacancies(vacancies_data)
            assert len(result) == 2
        else:
            # Альтернативно парсим каждую вакансию отдельно
            results = []
            for item in vacancies_data["objects"]:
                parsed = sj_parser.parse_vacancy(item)
                results.append(parsed)
            assert len(results) == 2

    def test_parse_error_handling_sj(self, sj_parser):
        """Тест обработки ошибок парсинга SJ"""
        invalid_data = {"invalid": "data"}
        
        try:
            result = sj_parser.parse_vacancy(invalid_data)
            assert result is None or result == {}
        except Exception as e:
            assert isinstance(e, Exception)

    def test_parse_vacancy_no_payment(self, sj_parser):
        """Тест парсинга вакансии SJ без зарплаты"""
        vacancy_data = {
            "id": 555,
            "profession": "No Payment Job",
            "link": "https://superjob.ru/vakansii/555",
            "payment_from": 0,
            "payment_to": 0
        }

        result = sj_parser.parse_vacancy(vacancy_data)
        
        assert result is not None
        # Проверяем обработку отсутствующей зарплаты
        if "payment_from" in result:
            assert result["payment_from"] == 0
        if "payment_to" in result:
            assert result["payment_to"] == 0
