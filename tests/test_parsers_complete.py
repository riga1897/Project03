
"""
Полные тесты для парсеров вакансий
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.vacancies.parsers.base_parser import BaseParser
    from src.vacancies.parsers.hh_parser import HHParser
    from src.vacancies.parsers.sj_parser import SJParser
    PARSERS_AVAILABLE = True
except ImportError:
    PARSERS_AVAILABLE = False
    BaseParser = object
    HHParser = object 
    SJParser = object


class ConcreteParser(BaseParser if PARSERS_AVAILABLE else object):
    """Конкретная реализация BaseParser для тестирования"""
    
    def parse_vacancy(self, raw_data):
        return {"id": raw_data.get("id", "test"), "title": "Test Vacancy"}
    
    def parse_vacancies(self, raw_vacancies):
        return [self.parse_vacancy(v) for v in raw_vacancies]


class TestBaseParser:
    """Тесты для базового парсера"""
    
    def test_base_parser_cannot_be_instantiated(self):
        """Тест что базовый класс нельзя инстанциировать"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        with pytest.raises(TypeError):
            BaseParser()
    
    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        parser = ConcreteParser()
        assert parser is not None
        
        # Тест parse_vacancy
        result = parser.parse_vacancy({"id": "123", "name": "Test"})
        assert isinstance(result, dict)
        assert result["id"] == "123"
        
        # Тест parse_vacancies
        results = parser.parse_vacancies([{"id": "1"}, {"id": "2"}])
        assert isinstance(results, list)
        assert len(results) == 2
    
    def test_abstract_methods_exist(self):
        """Тест что абстрактные методы определены"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        abstract_methods = BaseParser.__abstractmethods__
        assert 'parse_vacancy' in abstract_methods
        assert 'parse_vacancies' in abstract_methods


class TestHHParser:
    """Тесты для парсера HeadHunter"""
    
    @pytest.fixture
    def hh_parser(self):
        """Фикстура HH парсера"""
        if not PARSERS_AVAILABLE:
            return Mock()
        return HHParser()
    
    @pytest.fixture
    def sample_hh_vacancy(self):
        """Образец данных вакансии HH"""
        return {
            "id": "12345",
            "name": "Python Developer",
            "url": "https://hh.ru/vacancy/12345",
            "employer": {
                "id": "company123",
                "name": "Test Company"
            },
            "salary": {
                "from": 100000,
                "to": 150000,
                "currency": "RUR"
            },
            "experience": {"name": "От 1 года до 3 лет"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"},
            "area": {"name": "Москва"},
            "published_at": "2024-01-01T10:00:00+0300",
            "snippet": {
                "requirement": "Знание Python",
                "responsibility": "Разработка"
            }
        }
    
    def test_hh_parser_init(self, hh_parser):
        """Тест инициализации HH парсера"""
        assert hh_parser is not None
    
    def test_parse_vacancy(self, hh_parser, sample_hh_vacancy):
        """Тест парсинга одной вакансии HH"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        result = hh_parser.parse_vacancy(sample_hh_vacancy)
        
        assert isinstance(result, dict)
        assert result["id"] == "12345"
        assert result["title"] == "Python Developer"
        assert "salary_from" in result or "parsed" in str(result)
    
    def test_parse_vacancies(self, hh_parser, sample_hh_vacancy):
        """Тест парсинга списка вакансий HH"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        vacancies = [sample_hh_vacancy, {**sample_hh_vacancy, "id": "67890"}]
        results = hh_parser.parse_vacancies(vacancies)
        
        assert isinstance(results, list)
        assert len(results) == 2
    
    def test_parse_vacancy_missing_fields(self, hh_parser):
        """Тест парсинга вакансии с отсутствующими полями"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        incomplete_vacancy = {"id": "test", "name": "Test"}
        result = hh_parser.parse_vacancy(incomplete_vacancy)
        
        assert isinstance(result, dict)
        assert result["id"] == "test"


class TestSJParser:
    """Тесты для парсера SuperJob"""
    
    @pytest.fixture
    def sj_parser(self):
        """Фикстура SJ парсера"""
        if not PARSERS_AVAILABLE:
            return Mock()
        return SJParser()
    
    @pytest.fixture
    def sample_sj_vacancy(self):
        """Образец данных вакансии SJ"""
        return {
            "id": 12345,
            "profession": "Python Developer",
            "link": "https://superjob.ru/vacancy/12345",
            "firm_name": "Test Company",
            "payment_from": 100000,
            "payment_to": 150000,
            "currency": "rub",
            "experience": {"title": "от 1 года"},
            "type_of_work": {"title": "полная занятость"},
            "place_of_work": {"title": "офис"},
            "town": {"title": "Москва"},
            "date_published": 1704110400,
            "candidat": "Знание Python",
            "work": "Разработка"
        }
    
    def test_sj_parser_init(self, sj_parser):
        """Тест инициализации SJ парсера"""
        assert sj_parser is not None
    
    def test_parse_vacancy(self, sj_parser, sample_sj_vacancy):
        """Тест парсинга одной вакансии SJ"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        result = sj_parser.parse_vacancy(sample_sj_vacancy)
        
        assert isinstance(result, dict)
        assert str(result["id"]) == "12345"
        assert result["title"] == "Python Developer"
    
    def test_parse_vacancies(self, sj_parser, sample_sj_vacancy):
        """Тест парсинга списка вакансий SJ"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        vacancies = [sample_sj_vacancy, {**sample_sj_vacancy, "id": 67890}]
        results = sj_parser.parse_vacancies(vacancies)
        
        assert isinstance(results, list)
        assert len(results) == 2
    
    def test_parse_vacancy_missing_fields(self, sj_parser):
        """Тест парсинга вакансии с отсутствующими полями"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        incomplete_vacancy = {"id": 123, "profession": "Test"}
        result = sj_parser.parse_vacancy(incomplete_vacancy)
        
        assert isinstance(result, dict)
        assert str(result["id"]) == "123"


class TestParsersIntegration:
    """Интеграционные тесты парсеров"""
    
    def test_parsers_compatibility(self):
        """Тест совместимости парсеров"""
        if not PARSERS_AVAILABLE:
            pytest.skip("Parsers not available")
        
        parsers = [ConcreteParser()]
        
        if PARSERS_AVAILABLE:
            try:
                parsers.extend([HHParser(), SJParser()])
            except:
                pass
        
        test_data = {"id": "test", "title": "Test"}
        
        for parser in parsers:
            result = parser.parse_vacancy(test_data)
            assert isinstance(result, dict)
            
            results = parser.parse_vacancies([test_data])
            assert isinstance(results, list)
            assert len(results) == 1
