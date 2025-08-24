
"""
Тесты для форматирования вакансий
"""

import pytest
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestVacancyFormatter:
    """Тесты для класса VacancyFormatter"""

    def test_format_vacancy_info_basic(self, sample_vacancy):
        """Тест базового форматирования информации о вакансии"""
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(sample_vacancy, number=1)
        
        assert "1." in result
        assert "ID: 12345" in result
        assert "Python Developer" in result
        assert "Test Company" in result
        assert "до 150,000" in result

    def test_format_vacancy_info_no_number(self, sample_vacancy):
        """Тест форматирования без номера"""
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(sample_vacancy)
        
        assert "1." not in result
        assert "ID: 12345" in result
        assert "Python Developer" in result

    def test_format_salary_with_range(self):
        """Тест форматирования зарплаты с диапазоном"""
        salary_info = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }
        
        result = VacancyFormatter.format_salary(salary_info)
        
        assert "от 100000" in result
        assert "до 150000" in result
        assert "RUR" in result

    def test_format_salary_only_from(self):
        """Тест форматирования зарплаты только с минимумом"""
        salary_info = {
            "from": 80000,
            "currency": "RUR"
        }
        
        result = VacancyFormatter.format_salary(salary_info)
        
        assert "от 80000" in result
        assert "до" not in result

    def test_format_salary_none(self):
        """Тест форматирования пустой зарплаты"""
        result = VacancyFormatter.format_salary(None)
        
        assert result == "Зарплата не указана"

    def test_format_company_info_dict(self):
        """Тест форматирования информации о компании из словаря"""
        employer_info = {"name": "Test Company Ltd"}
        
        result = VacancyFormatter.format_company_info(employer_info)
        
        assert result == "Test Company Ltd"

    def test_format_company_info_string(self):
        """Тест форматирования информации о компании из строки"""
        employer_info = "Simple Company Name"
        
        result = VacancyFormatter.format_company_info(employer_info)
        
        assert result == "Simple Company Name"

    def test_format_company_info_none(self):
        """Тест форматирования пустой информации о компании"""
        result = VacancyFormatter.format_company_info(None)
        
        assert result == "Не указана"

    def test_extract_responsibilities(self, sample_vacancy):
        """Тест извлечения обязанностей"""
        result = VacancyFormatter._extract_responsibilities(sample_vacancy)
        
        assert result == "Development"

    def test_extract_requirements(self, sample_vacancy):
        """Тест извлечения требований"""
        result = VacancyFormatter._extract_requirements(sample_vacancy)
        
        assert result == "Python, Django"

    def test_extract_conditions_with_schedule(self, sample_vacancy):
        """Тест извлечения условий с графиком работы"""
        result = VacancyFormatter._extract_conditions(sample_vacancy)
        
        assert "График: Полный день" in result

    def test_build_vacancy_lines_complete(self, sample_vacancy):
        """Тест построения полного списка строк вакансии"""
        lines = VacancyFormatter._build_vacancy_lines(sample_vacancy, number=1)
        
        # Проверяем наличие основных разделов
        line_text = "\n".join(lines)
        assert "1." in line_text
        assert "ID: 12345" in line_text
        assert "Название: Python Developer" in line_text
        assert "Компания: Test Company" in line_text
        assert "Зарплата:" in line_text
        assert "Опыт: От 1 года до 3 лет" in line_text
        assert "Занятость: Полная занятость" in line_text
        assert "Ссылка: https://hh.ru/vacancy/12345" in line_text
        assert "Описание вакансии:" in line_text

    def test_convert_hh_api_url_to_web_url(self):
        """Тест преобразования API-ссылки HH в веб-ссылку"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://api.hh.ru/vacancies/12345",
            vacancy_id="12345"
        )
        
        lines = VacancyFormatter._build_vacancy_lines(vacancy)
        line_text = "\n".join(lines)
        
        assert "https://hh.ru/vacancy/12345" in line_text
        assert "api.hh.ru" not in line_text
