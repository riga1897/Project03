
import pytest
from unittest.mock import MagicMock
from src.vacancies.parsers.base_parser import BaseParser


class ConcreteParser(BaseParser):
    """Конкретная реализация для тестирования"""
    
    def parse_vacancy(self, data):
        return {'id': data.get('id'), 'title': data.get('name')}
    
    def parse_vacancies_list(self, data):
        return [self.parse_vacancy(item) for item in data.get('items', [])]


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
        data = {'id': '123', 'name': 'Python Developer'}
        result = parser.parse_vacancy(data)
        assert result['id'] == '123'
        assert result['title'] == 'Python Developer'

    def test_concrete_parser_parse_vacancies_list(self):
        """Тест парсинга списка вакансий"""
        parser = ConcreteParser()
        data = {
            'items': [
                {'id': '123', 'name': 'Python Developer'},
                {'id': '124', 'name': 'Java Developer'}
            ]
        }
        result = parser.parse_vacancies_list(data)
        assert len(result) == 2
        assert result[0]['id'] == '123'
        assert result[1]['id'] == '124'

    def test_parser_empty_data(self):
        """Тест парсинга пустых данных"""
        parser = ConcreteParser()
        result = parser.parse_vacancies_list({})
        assert result == []

    def test_parser_invalid_data(self):
        """Тест парсинга невалидных данных"""
        parser = ConcreteParser()
        result = parser.parse_vacancy({})
        assert result['id'] is None
        assert result['title'] is None
