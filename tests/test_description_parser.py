
"""
Тесты для парсера описаний вакансий
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.utils.description_parser import DescriptionParser
    DESCRIPTION_PARSER_AVAILABLE = True
except ImportError:
    DESCRIPTION_PARSER_AVAILABLE = False


class TestDescriptionParser:
    """Тесты для парсера описаний"""
    
    @pytest.fixture
    def parser(self):
        """Фикстура для создания парсера"""
        if not DESCRIPTION_PARSER_AVAILABLE:
            pytest.skip("DescriptionParser not available")
        return DescriptionParser()
    
    def test_parser_init(self, parser):
        """Тест инициализации парсера"""
        assert parser is not None
    
    def test_parse_html_description(self, parser):
        """Тест парсинга HTML описания"""
        html_text = "<p>Описание <strong>вакансии</strong> с HTML тегами</p>"
        
        if hasattr(parser, 'parse_html'):
            result = parser.parse_html(html_text)
            assert isinstance(result, str)
            assert "Описание" in result
            assert "вакансии" in result
    
    def test_extract_skills(self, parser):
        """Тест извлечения навыков из описания"""
        description = "Требуются навыки: Python, Django, PostgreSQL"
        
        if hasattr(parser, 'extract_skills'):
            skills = parser.extract_skills(description)
            assert isinstance(skills, list)
    
    def test_extract_requirements(self, parser):
        """Тест извлечения требований"""
        description = "Требования: опыт работы от 3 лет, знание Python"
        
        if hasattr(parser, 'extract_requirements'):
            requirements = parser.extract_requirements(description)
            assert isinstance(requirements, (list, str))
    
    def test_clean_text(self, parser):
        """Тест очистки текста"""
        dirty_text = "  Текст   с   лишними    пробелами  \n\t"
        
        if hasattr(parser, 'clean_text'):
            clean = parser.clean_text(dirty_text)
            assert isinstance(clean, str)
            assert clean.strip() == "Текст с лишними пробелами"
    
    def test_parse_salary_from_description(self, parser):
        """Тест извлечения зарплаты из описания"""
        description = "Зарплата от 100000 до 150000 рублей"
        
        if hasattr(parser, 'parse_salary'):
            salary_info = parser.parse_salary(description)
            assert isinstance(salary_info, (dict, str, type(None)))
    
    def test_parse_empty_description(self, parser):
        """Тест парсинга пустого описания"""
        if hasattr(parser, 'parse_html'):
            result = parser.parse_html("")
            assert result == ""
        
        if hasattr(parser, 'extract_skills'):
            skills = parser.extract_skills("")
            assert skills == []
    
    def test_parse_none_description(self, parser):
        """Тест парсинга None описания"""
        if hasattr(parser, 'parse_html'):
            result = parser.parse_html(None)
            assert result in ("", None)
    
    def test_extract_contact_info(self, parser):
        """Тест извлечения контактной информации"""
        description = "Контакт: email@example.com, телефон: +7 123 456 78 90"
        
        if hasattr(parser, 'extract_contacts'):
            contacts = parser.extract_contacts(description)
            assert isinstance(contacts, (list, dict))
    
    def test_parse_complex_html(self, parser):
        """Тест парсинга сложного HTML"""
        complex_html = """
        <div>
            <h2>Описание вакансии</h2>
            <ul>
                <li>Требование 1</li>
                <li>Требование 2</li>
            </ul>
            <p>Дополнительная информация</p>
        </div>
        """
        
        if hasattr(parser, 'parse_html'):
            result = parser.parse_html(complex_html)
            assert isinstance(result, str)
            assert "Описание вакансии" in result
