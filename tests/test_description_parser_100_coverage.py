"""
100% покрытие utils/description_parser.py модуля
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest
from typing import Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.utils.description_parser import DescriptionParser


class TestDescriptionParser:
    """100% покрытие DescriptionParser"""

    def test_clean_html_empty_input(self):
        """Тест очистки пустого HTML"""
        result = DescriptionParser.clean_html("")
        assert result == ""
        
        result = DescriptionParser.clean_html(None)
        assert result == ""

    def test_clean_html_simple_tags(self):
        """Тест очистки простых HTML тегов"""
        html = "<p>Simple text</p>"
        result = DescriptionParser.clean_html(html)
        assert result == "Simple text"

    def test_clean_html_lists(self):
        """Тест очистки HTML списков"""
        html = """
        <ul>
            <li>First item</li>
            <li>Second item</li>
        </ul>
        """
        result = DescriptionParser.clean_html(html)
        assert "• First item" in result
        assert "• Second item" in result

    def test_clean_html_ordered_lists(self):
        """Тест очистки упорядоченных списков"""
        html = """
        <ol>
            <li>Item 1</li>
            <li>Item 2</li>
        </ol>
        """
        result = DescriptionParser.clean_html(html)
        assert "• Item 1" in result
        assert "• Item 2" in result

    def test_clean_html_paragraphs(self):
        """Тест очистки параграфов"""
        html = "<p>First paragraph</p><p>Second paragraph</p>"
        result = DescriptionParser.clean_html(html)
        assert "First paragraph" in result
        assert "Second paragraph" in result

    def test_clean_html_entities(self):
        """Тест декодирования HTML сущностей"""
        html = "&lt;div&gt;Text with &amp; symbols&lt;/div&gt;"
        result = DescriptionParser.clean_html(html)
        # clean_html удаляет теги, но декодирует HTML сущности
        assert "Text with & symbols" == result

    def test_clean_html_complex(self):
        """Тест очистки сложного HTML"""
        html = """
        <div class="container">
            <p><strong>Requirements:</strong></p>
            <ul>
                <li>Python 3.8+</li>
                <li>Django experience</li>
            </ul>
            <p>Additional info</p>
        </div>
        """
        result = DescriptionParser.clean_html(html)
        assert "Requirements:" in result
        assert "• Python 3.8+" in result
        assert "• Django experience" in result
        assert "Additional info" in result

    def test_extract_requirements_empty_description(self):
        """Тест извлечения из пустого описания"""
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities("")
        assert requirements is None
        assert responsibilities is None

    def test_extract_requirements_no_patterns_match(self):
        """Тест извлечения когда паттерны не совпадают"""
        description = "Just some random text without structured requirements or responsibilities"
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
        assert requirements is None
        assert responsibilities is None

    def test_extract_requirements_html_strong_tags(self):
        """Тест извлечения требований из HTML с strong тегами"""
        description = """
        <p><strong>Требования:</strong></p>
        <ul>
            <li>Python 3.8+</li>
            <li>Django 3.2+</li>
        </ul>
        <p><strong>Обязанности:</strong></p>
        <ul>
            <li>Разработка веб-приложений</li>
            <li>Участие в код-ревью</li>
        </ul>
        """
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
        
        assert requirements is not None
        assert "Python 3.8+" in requirements
        assert "Django 3.2+" in requirements
        
        assert responsibilities is not None
        assert "Разработка веб-приложений" in responsibilities
        assert "Участие в код-ревью" in responsibilities

    def test_extract_requirements_html_b_tags(self):
        """Тест извлечения требований из HTML с b тегами"""
        description = """
        <p><b>Требования:</b></p>
        <p>Python, FastAPI, PostgreSQL</p>
        <p><b>Обязанности:</b></p>
        <p>Разработка микросервисов</p>
        """
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
        
        assert requirements is not None
        assert "Python, FastAPI, PostgreSQL" in requirements
        
        assert responsibilities is not None  
        assert "Разработка микросервисов" in responsibilities

    def test_extract_requirements_plain_text_colon(self):
        """Тест извлечения требований из простого текста с двоеточием"""
        description = """
        Требования:
        - Python 3.8+
        - Опыт работы с Django
        
        Обязанности:
        - Разработка веб-приложений
        - Участие в планировании
        """
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
        
        assert requirements is not None
        assert "Python 3.8+" in requirements
        assert "Django" in requirements
        
        assert responsibilities is not None
        assert "Разработка веб-приложений" in responsibilities

    def test_extract_requirements_uppercase_headers(self):
        """Тест извлечения требований с заголовками в верхнем регистре"""
        description = """
        ТРЕБОВАНИЯ:
        Python, Django, PostgreSQL
        
        ОБЯЗАННОСТИ:
        Разработка и поддержка системы
        """
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
        
        assert requirements is not None
        assert "Python, Django, PostgreSQL" in requirements
        
        assert responsibilities is not None
        assert "Разработка и поддержка системы" in responsibilities

    def test_extract_requirements_tasks_section(self):
        """Тест извлечения с разделом 'Задачи'"""
        description = """
        Требования:
        Python, FastAPI
        
        Задачи:
        Разработка API для мобильного приложения
        """
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
        
        assert requirements is not None
        assert "Python, FastAPI" in requirements
        
        assert responsibilities is not None
        assert "Разработка API для мобильного приложения" in responsibilities

    def test_extract_requirements_uppercase_tasks(self):
        """Тест извлечения с разделом 'ЗАДАЧИ'"""
        description = """
        ТРЕБОВАНИЯ:
        Знание Python
        
        ЗАДАЧИ:
        Создание REST API
        """
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
        
        assert requirements is not None
        assert "Знание Python" in requirements
        
        assert responsibilities is not None
        assert "Создание REST API" in responsibilities

    def test_extract_requirements_only_requirements(self):
        """Тест извлечения только требований без обязанностей"""
        description = """
        <strong>Требования:</strong>
        Python, Django, REST API
        """
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
        
        assert requirements is not None
        assert "Python, Django, REST API" in requirements
        assert responsibilities is None

    def test_extract_requirements_only_responsibilities(self):
        """Тест извлечения только обязанностей без требований"""
        description = """
        <strong>Обязанности:</strong>
        Разработка веб-сервисов
        Написание технической документации
        """
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
        
        assert requirements is None
        assert responsibilities is not None
        assert "Разработка веб-сервисов" in responsibilities
        assert "Написание технической документации" in responsibilities

    def test_patterns_coverage_all_requirements_patterns(self):
        """Тест покрытия всех паттернов требований"""
        # Тестируем каждый паттерн из REQUIREMENTS_PATTERNS
        patterns_test_data = [
            ("<p><strong>Требования к кандидату</strong></p><p>Python experience</p>", "Python experience"),
            ("<p><b>Требования</b></p><p>Django skills</p>", "Django skills"),
            ("<strong>Требования:</strong>FastAPI knowledge", "FastAPI knowledge"),
            ("<b>Требования</b>PostgreSQL experience", "PostgreSQL experience"),
            ("Требования:\nPython 3.8+\nNext Section:", "Python 3.8+"),
            ("ТРЕБОВАНИЯ:\nDjango 3.2+\nОбязанности:", "Django 3.2+")
        ]
        
        for description, expected_content in patterns_test_data:
            requirements, _ = DescriptionParser.extract_requirements_and_responsibilities(description)
            assert requirements is not None, f"Failed to extract from: {description}"
            assert expected_content in requirements, f"Expected '{expected_content}' in '{requirements}'"

    def test_patterns_coverage_all_responsibilities_patterns(self):
        """Тест покрытия всех паттернов обязанностей"""
        # Тестируем каждый паттерн из RESPONSIBILITIES_PATTERNS  
        patterns_test_data = [
            ("<p><strong>Обязанности сотрудника</strong></p><p>Web development</p>", "Web development"),
            ("<p><b>Обязанности</b></p><p>API development</p>", "API development"),
            ("<strong>Обязанности:</strong>Code review", "Code review"),
            ("<b>Обязанности</b>Testing applications", "Testing applications"),
            ("Обязанности:\nDevelop features\nТребования:", "Develop features"),
            ("ОБЯЗАННОСТИ:\nCode maintenance\nДругой раздел:", "Code maintenance"),
            ("Задачи:\nCreate APIs\nТребования:", "Create APIs"),
            ("ЗАДАЧИ:\nDocument code\nОбязанности:", "Document code")
        ]
        
        for description, expected_content in patterns_test_data:
            _, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)
            assert responsibilities is not None, f"Failed to extract from: {description}"
            assert expected_content in responsibilities, f"Expected '{expected_content}' in '{responsibilities}'"

    def test_whitespace_and_formatting_cleanup(self):
        """Тест очистки лишних пробелов и форматирования"""
        html = """
        <p>   Text  with   multiple    spaces   </p>
        
        
        <p>Another    paragraph</p>
        """
        result = DescriptionParser.clean_html(html)
        # Проверяем что множественные пробелы схлопнулись
        assert "Text with multiple spaces" in result
        assert "Another paragraph" in result
        # Не должно быть лишних переносов строк
        assert result.count('\n') <= 2

    def test_real_world_hh_example(self):
        """Тест на реальном примере с HH.ru (покрывает строки 141-177)"""
        # Покрываем тестовые данные из исходного файла
        test_description_hh = """
        <p><strong>Обязанности:</strong></p>
        <ul>
        <li>Разработка и поддержка веб-приложений на Python/Django</li>
        <li>Участие в проектировании архитектуры системы</li>
        <li>Код-ревью и менторинг младших разработчиков</li>
        </ul>
        <p><strong>Требования:</strong></p>
        <ul>
        <li>Python 3.8+, Django 3.2+</li>
        <li>Опыт работы с PostgreSQL, Redis</li>
        <li>Знание Git, Docker</li>
        </ul>
        """
        
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(test_description_hh)
        
        assert requirements is not None
        assert "Python 3.8+, Django 3.2+" in requirements
        assert "PostgreSQL, Redis" in requirements
        assert "Git, Docker" in requirements
        
        assert responsibilities is not None
        assert "Разработка и поддержка веб-приложений" in responsibilities
        assert "архитектуры системы" in responsibilities
        assert "Код-ревью и менторинг" in responsibilities

    def test_real_world_text_example(self):
        """Тест на реальном примере текстового формата"""
        test_description_text = """
        Обязанности:
        - Разработка микросервисов на FastAPI
        - Интеграция с внешними API

        Требования:
        - Python, FastAPI, SQLAlchemy
        - Опыт работы от 3 лет
        """
        
        requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(test_description_text)
        
        assert requirements is not None
        assert "Python, FastAPI, SQLAlchemy" in requirements
        assert "Опыт работы от 3 лет" in requirements
        
        assert responsibilities is not None
        assert "Разработка микросервисов на FastAPI" in responsibilities
        assert "Интеграция с внешними API" in responsibilities