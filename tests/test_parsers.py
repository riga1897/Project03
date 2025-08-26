
"""
Тесты для парсеров вакансий
"""

import pytest
from unittest.mock import Mock, patch
from src.vacancies.parsers.hh_parser import HHParser
from src.vacancies.parsers.sj_parser import SJParser


class TestHHParser:
    """Тесты для парсера HeadHunter"""

    @pytest.fixture
    def hh_parser(self):
        """Фикстура парсера HH"""
        return HHParser()

    def test_parse_vacancy_full_data(self, hh_parser):
        """Тест парсинга полных данных вакансии"""
        vacancy_data = {
            'id': '12345',
            'name': 'Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/12345',
            'salary': {
                'from': 100000,
                'to': 150000,
                'currency': 'RUR'
            },
            'snippet': {
                'requirement': 'Python, Django',
                'responsibility': 'Разработка веб-приложений'
            },
            'employer': {
                'id': '1',
                'name': 'TechCorp'
            },
            'area': {
                'name': 'Москва'
            },
            'experience': {
                'name': '1–3 года'
            },
            'employment': {
                'name': 'Полная занятость'
            },
            'schedule': {
                'name': 'Полный день'
            },
            'published_at': '2024-01-15T10:30:00+0300'
        }

        result = hh_parser.parse_vacancy(vacancy_data)

        assert result['vacancy_id'] == '12345'
        assert result['title'] == 'Python Developer'
        assert result['url'] == 'https://hh.ru/vacancy/12345'
        assert result['salary_from'] == 100000
        assert result['salary_to'] == 150000
        assert result['salary_currency'] == 'RUR'
        assert result['requirements'] == 'Python, Django'
        assert result['responsibilities'] == 'Разработка веб-приложений'
        assert result['employer'] == 'TechCorp'
        assert result['area'] == 'Москва'

    def test_parse_vacancy_minimal_data(self, hh_parser):
        """Тест парсинга минимальных данных"""
        vacancy_data = {
            'id': '67890',
            'name': 'Java Developer'
        }

        result = hh_parser.parse_vacancy(vacancy_data)

        assert result['vacancy_id'] == '67890'
        assert result['title'] == 'Java Developer'
        assert result['salary_from'] is None
        assert result['salary_to'] is None
        assert result['employer'] == ''

    def test_parse_vacancy_no_salary(self, hh_parser):
        """Тест парсинга вакансии без зарплаты"""
        vacancy_data = {
            'id': '111',
            'name': 'Frontend Developer',
            'salary': None
        }

        result = hh_parser.parse_vacancy(vacancy_data)

        assert result['salary_from'] is None
        assert result['salary_to'] is None
        assert result['salary_currency'] is None

    def test_parse_company_data(self, hh_parser):
        """Тест парсинга данных компании"""
        company_data = {
            'id': '123',
            'name': 'TestCompany',
            'description': 'Test Description',
            'alternate_url': 'https://hh.ru/employer/123'
        }

        result = hh_parser.parse_company(company_data)

        assert result['company_id'] == '123'
        assert result['name'] == 'TestCompany'
        assert result['description'] == 'Test Description'

    def test_parse_companies_list(self, hh_parser):
        """Тест парсинга списка компаний"""
        companies_data = {
            'items': [
                {'id': '1', 'name': 'Company1'},
                {'id': '2', 'name': 'Company2'}
            ]
        }

        result = hh_parser.parse_companies(companies_data)

        assert len(result) == 2
        assert result[0]['company_id'] == '1'
        assert result[1]['name'] == 'Company2'


class TestSJParser:
    """Тесты для парсера SuperJob"""

    @pytest.fixture
    def sj_parser(self):
        """Фикстура парсера SJ"""
        return SJParser()

    def test_parse_vacancy_full_data(self, sj_parser):
        """Тест парсинга полных данных вакансии SJ"""
        vacancy_data = {
            'id': 54321,
            'profession': 'Python Developer',
            'link': 'https://superjob.ru/vakansii/python-54321.html',
            'payment_from': 80000,
            'payment_to': 120000,
            'currency': 'rub',
            'candidat': 'Требования к кандидату',
            'work': 'Обязанности',
            'firm_name': 'SuperTech',
            'town': {'title': 'Санкт-Петербург'},
            'experience': {'title': '1–3 года'},
            'type_of_work': {'title': 'Полная занятость'},
            'place_of_work': {'title': 'Офис'},
            'date_pub_timestamp': 1642248000
        }

        result = sj_parser.parse_vacancy(vacancy_data)

        assert result['vacancy_id'] == '54321'
        assert result['title'] == 'Python Developer'
        assert result['url'] == 'https://superjob.ru/vakansii/python-54321.html'
        assert result['salary_from'] == 80000
        assert result['salary_to'] == 120000
        assert result['salary_currency'] == 'rub'
        assert result['requirements'] == 'Требования к кандидату'
        assert result['responsibilities'] == 'Обязанности'
        assert result['employer'] == 'SuperTech'
        assert result['area'] == 'Санкт-Петербург'

    def test_parse_vacancy_minimal_data(self, sj_parser):
        """Тест парсинга минимальных данных SJ"""
        vacancy_data = {
            'id': 99999,
            'profession': 'React Developer'
        }

        result = sj_parser.parse_vacancy(vacancy_data)

        assert result['vacancy_id'] == '99999'
        assert result['title'] == 'React Developer'
        assert result['salary_from'] is None
        assert result['salary_to'] is None
        assert result['employer'] == ''

    def test_parse_companies_list(self, sj_parser):
        """Тест парсинга списка компаний SJ"""
        companies_data = {
            'objects': [
                {'id': 101, 'title': 'SJ Company1'},
                {'id': 102, 'title': 'SJ Company2'}
            ]
        }

        result = sj_parser.parse_companies(companies_data)

        assert len(result) == 2
        assert result[0]['company_id'] == '101'
        assert result[1]['name'] == 'SJ Company2'
