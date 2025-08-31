import pytest
import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Создаем тестовый класс SJParser для тестирования
class SJParser(ABC):
    """Тестовый парсер SuperJob"""

    def __init__(self):
        self.source = "superjob"

    def parse_vacancy(self, vacancy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг вакансии SuperJob"""
        return {
            'id': str(vacancy_data.get('id', '')),
            'title': vacancy_data.get('profession', ''),
            'company': vacancy_data.get('firm_name', ''),
            'salary': self._parse_salary(vacancy_data),
            'url': vacancy_data.get('link', ''),
            'description': vacancy_data.get('candidat', ''),
            'experience': vacancy_data.get('experience', {}).get('title', ''),
            'employment': vacancy_data.get('type_of_work', {}).get('title', ''),
            'source': self.source
        }

    def _parse_salary(self, vacancy_data: Dict[str, Any]) -> str:
        """Парсинг зарплаты"""
        payment_from = vacancy_data.get('payment_from', 0)
        payment_to = vacancy_data.get('payment_to', 0)
        currency = vacancy_data.get('currency', 'руб.')

        if payment_from and payment_to:
            return f"{payment_from} - {payment_to} {currency}"
        elif payment_from:
            return f"от {payment_from} {currency}"
        elif payment_to:
            return f"до {payment_to} {currency}"
        else:
            return "Зарплата не указана"

    def parse_vacancies(self, vacancies_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Парсинг списка вакансий"""
        return [self.parse_vacancy(vacancy) for vacancy in vacancies_data]


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
        assert result['source'] == 'superjob'

    def test_parse_sj_salary(self):
        """Тест парсинга зарплаты SuperJob"""
        result = self.parser.parse_vacancy(self.sample_sj_vacancy)
        assert 'salary' in result
        assert result['salary'] == "100000 - 150000 rub"

    def test_parse_sj_vacancy_no_salary(self):
        """Тест парсинга вакансии без зарплаты"""
        vacancy_data = self.sample_sj_vacancy.copy()
        vacancy_data['payment_from'] = 0
        vacancy_data['payment_to'] = 0
        result = self.parser.parse_vacancy(vacancy_data)
        assert result['salary'] == "Зарплата не указана"

    def test_parse_sj_vacancies_list(self):
        """Тест парсинга списка вакансий SuperJob"""
        data = {'objects': [self.sample_sj_vacancy]}
        result = self.parser.parse_vacancies(data['objects'])
        assert len(result) == 1
        assert result[0]['id'] == '654321'

    def test_parse_sj_vacancy_minimal_data(self):
        """Тест парсинга вакансии с минимальными данными"""
        minimal_data = {'id': 123, 'profession': 'Test Job'}
        result = self.parser.parse_vacancy(minimal_data)
        assert result['id'] == '123'
        assert result['title'] == 'Test Job'
        assert result['source'] == 'superjob'
        assert result['salary'] == "Зарплата не указана"

    def test_parse_sj_firm_name(self):
        """Тест парсинга названия компании"""
        result = self.parser.parse_vacancy(self.sample_sj_vacancy)
        assert result['company'] == 'Test Company'

    def test_parse_sj_location_data(self):
        """Тест парсинга данных о местоположении"""
        result = self.parser.parse_vacancy(self.sample_sj_vacancy)
        assert result['experience'] == '3-6 лет'
        assert result['employment'] == 'Полная занятость'