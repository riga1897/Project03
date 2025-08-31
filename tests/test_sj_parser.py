
import pytest
from unittest.mock import MagicMock
from src.vacancies.parsers.sj_parser import SJParser


class TestSJParser:
    def setup_method(self):
        """Настройка для каждого теста"""
        self.parser = SJParser()
        self.sample_sj_vacancy = {
            'id': 654321,
            'profession': 'Python Developer',
            'firm_name': 'Test Company',
            'payment_from': 100000,
            'payment_to': 150000,
            'currency': 'rub',
            'town': {'title': 'Москва'},
            'experience': {'title': '3-6 лет'},
            'type_of_work': {'title': 'Полная занятость'},
            'link': 'https://superjob.ru/vakansii/654321',
            'candidat': 'Требования к кандидату',
            'work': 'Обязанности'
        }

    def test_sj_parser_initialization(self):
        """Тест инициализации SJ парсера"""
        parser = SJParser()
        assert parser is not None

    def test_parse_sj_vacancy(self):
        """Тест парсинга вакансии SuperJob"""
        result = self.parser.parse_vacancy(self.sample_sj_vacancy)
        assert result['id'] == '654321'
        assert result['title'] == 'Python Developer'
        assert result['company'] == 'Test Company'
        assert result['source'] == 'superjob.ru'

    def test_parse_sj_salary(self):
        """Тест парсинга зарплаты SuperJob"""
        result = self.parser.parse_vacancy(self.sample_sj_vacancy)
        assert 'salary_from' in result
        assert 'salary_to' in result
        assert result['salary_from'] == 100000
        assert result['salary_to'] == 150000

    def test_parse_sj_vacancy_no_salary(self):
        """Тест парсинга вакансии без зарплаты"""
        vacancy_data = self.sample_sj_vacancy.copy()
        vacancy_data['payment_from'] = 0
        vacancy_data['payment_to'] = 0
        result = self.parser.parse_vacancy(vacancy_data)
        assert result['salary_from'] == 0 or result['salary_from'] is None
        assert result['salary_to'] == 0 or result['salary_to'] is None

    def test_parse_sj_vacancies_list(self):
        """Тест парсинга списка вакансий SuperJob"""
        data = {'objects': [self.sample_sj_vacancy]}
        result = self.parser.parse_vacancies_list(data)
        assert len(result) == 1
        assert result[0]['id'] == '654321'

    def test_parse_sj_vacancy_minimal_data(self):
        """Тест парсинга вакансии с минимальными данными"""
        minimal_data = {'id': 123, 'profession': 'Test Job'}
        result = self.parser.parse_vacancy(minimal_data)
        assert result['id'] == '123'
        assert result['title'] == 'Test Job'
        assert result['source'] == 'superjob.ru'

    def test_parse_sj_firm_name(self):
        """Тест парсинга названия компании"""
        result = self.parser.parse_vacancy(self.sample_sj_vacancy)
        assert result['company'] == 'Test Company'

    def test_parse_sj_location_data(self):
        """Тест парсинга данных о местоположении"""
        result = self.parser.parse_vacancy(self.sample_sj_vacancy)
        assert 'location' in result or 'town' in result
