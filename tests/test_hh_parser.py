import pytest
from unittest.mock import MagicMock
from src.vacancies.parsers.hh_parser import HHParser


class TestHHParser:
    def setup_method(self):
        """Настройка для каждого теста"""
        self.parser = HHParser()
        self.sample_hh_vacancy = {
            'id': '123456',
            'name': 'Python Developer',
            'employer': {'name': 'Test Company'},
            'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
            'area': {'name': 'Москва'},
            'experience': {'name': 'От 3 до 6 лет'},
            'employment': {'name': 'Полная занятость'},
            'alternate_url': 'https://hh.ru/vacancy/123456',
            'snippet': {'requirement': 'Python, Django', 'responsibility': 'Разработка'}
        }

    def test_hh_parser_initialization(self):
        """Тест инициализации HH парсера"""
        parser = HHParser()
        assert parser is not None

    def test_parse_hh_vacancy(self):
        """Тест парсинга вакансии HH"""
        result = self.parser.parse_vacancy(self.sample_hh_vacancy)
        # Проверяем что парсер возвращает валидный результат
        assert result is not None
        # Проверяем тип результата - может быть объект Vacancy или dict
        assert hasattr(result, 'vacancy_id') or isinstance(result, dict)

    def test_parse_hh_salary(self):
        """Тест парсинга зарплаты HH"""
        result = self.parser.parse_vacancy(self.sample_hh_vacancy)
        assert 'salary_from' in result
        assert 'salary_to' in result
        assert result['salary_from'] == 100000
        assert result['salary_to'] == 150000

    def test_parse_hh_vacancy_no_salary(self):
        """Тест парсинга вакансии без зарплаты"""
        vacancy_data = self.sample_hh_vacancy.copy()
        vacancy_data['salary'] = None
        result = self.parser.parse_vacancy(vacancy_data)
        assert result['salary_from'] is None
        assert result['salary_to'] is None

    def test_parse_hh_vacancies_list(self):
        """Тест парсинга списка вакансий HH"""
        data = {'items': [self.sample_hh_vacancy]}
        result = self.parser.parse_vacancies_list(data)
        assert len(result) == 1
        assert result[0]['id'] == '123456'

    def test_parse_hh_vacancy_minimal_data(self):
        """Тест парсинга вакансии с минимальными данными"""
        minimal_data = {'id': '123', 'name': 'Test Job'}
        result = self.parser.parse_vacancy(minimal_data)
        assert result['id'] == '123'
        assert result['title'] == 'Test Job'
        assert result['source'] == 'hh.ru'

    def test_parse_hh_employer_data(self):
        """Тест парсинга данных работодателя"""
        result = self.parser.parse_vacancy(self.sample_hh_vacancy)
        assert result['employer']['name'] == 'Test Company'
        assert result['employer']['id'] == '1'

    def test_parse_hh_location_data(self):
        """Тест парсинга данных о местоположении"""
        result = self.parser.parse_vacancy(self.sample_hh_vacancy)
        assert 'location' in result or 'area' in result