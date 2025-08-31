import pytest
from unittest.mock import MagicMock
from src.vacancies.parsers.base_parser import BaseParser


class ConcreteParser(BaseParser):
    """Конкретная реализация BaseParser для тестирования"""

    def parse_vacancy(self, vacancy_data):
        """Парсинг одной вакансии"""
        return {
            'id': vacancy_data.get('id'),
            'title': vacancy_data.get('name', 'Unknown'),
            'company': vacancy_data.get('company', 'Unknown Company')
        }

    def parse_vacancies(self, vacancies_data):
        """Парсинг списка вакансий"""
        return [self.parse_vacancy(v) for v in vacancies_data]


class TestBaseParser:
    def test_base_parser_initialization(self):
        """Тест инициализации базового парсера"""
        parser = ConcreteParser()
        assert parser is not None

    def test_base_parser_is_abstract(self):
        """Тест что BaseParser нельзя инстанцировать напрямую"""
        with pytest.raises(TypeError):
            BaseParser()

    def test_concrete_parser_parse_vacancy(self):
        """Тест парсинга одной вакансии"""
        parser = ConcreteParser()
        data = {'id': '123', 'name': 'Python Developer', 'company': 'Tech Corp'}
        result = parser.parse_vacancy(data)
        assert result['id'] == '123'
        assert result['title'] == 'Python Developer'
        assert result['company'] == 'Tech Corp'

    def test_concrete_parser_parse_vacancies_list(self):
        """Тест парсинга списка вакансий"""
        parser = ConcreteParser()
        data = {
            'items': [
                {'id': '123', 'name': 'Python Developer', 'company': 'Tech Corp'},
                {'id': '124', 'name': 'Java Developer', 'company': 'Code Inc'}
            ]
        }
        result = parser.parse_vacancies(data.get('items', []))
        assert len(result) == 2
        assert result[0]['id'] == '123'
        assert result[1]['id'] == '124'
        assert result[0]['company'] == 'Tech Corp'
        assert result[1]['company'] == 'Code Inc'

    def test_parser_empty_data(self):
        """Тест парсинга пустых данных"""
        parser = ConcreteParser()
        result = parser.parse_vacancies([])
        assert result == []

    def test_parser_invalid_data(self):
        """Тест парсинга невалидных данных"""
        parser = ConcreteParser()
        result = parser.parse_vacancy({})
        assert result['id'] is None
        assert result['title'] == 'Unknown'
        assert result['company'] == 'Unknown Company'